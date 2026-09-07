# -*- coding: utf-8 -*-
"""OpenAI SDK 适配器：ModelClient 的正式实现（infrastructure 层）。

全引擎唯一允许出现 OpenAI SDK dict 的地方（适配器模式，Rule 2）：
类型化消息 → SDK dict 的转换、图片多模态展开、Zen 会话头、
上下文超限识别都在本模块内闭环。
"""
from __future__ import annotations

import base64
import uuid
from pathlib import Path
from typing import Iterator

import httpx  # HTTP 底座：预构连接池，跳过证书库加载（冷启动 15s→秒级）
from openai import OpenAI  # OpenAI 兼容 SDK：chat.completions 协议

from ..domain.errors import ContextOverflowError, EngineError
from ..domain.events import StreamDelta
from ..domain.messages import Message, UserMessage, transport_messages
from ..interfaces.model_client import ToolSchema
from .config import ModelSettings
from .logging_.logger import get_logger

#: 超限错误特征（API 报错文本匹配；命中即抛 ContextOverflowError 让上层压缩重试）。
_OVERFLOW_MARKERS = (
    "context length", "maximum context", "context window exceeded",
    "context_window_exceeded", "token limit", "too many tokens",
    "maximum context length",
)

logger = get_logger("openai_client")


def _is_context_overflow(exc: Exception) -> bool:
    """输入：任意异常。返回：文本是否命中上下文超限特征。"""
    text = str(exc).lower()
    return any(marker in text for marker in _OVERFLOW_MARKERS)


class OpenAIModelClient:
    """主模型客户端（ModelClient 实现）。

    类职责：流式/非流式对话；图片附件在发送边界展开为 image_url 片段
    （历史保持纯文本，token 估算/压缩/落盘不受影响）。
    类变量/实例属性：
        _client: OpenAI — SDK 单例（httpx 预置：trust_env=False、verify=False）。
        _session_root: str — 图片附件目录（.chat/uploads）的会话根。
    生命周期：bootstrap 每进程构建一个。
    """

    def __init__(self, model: ModelSettings, session_root: str = "") -> None:
        """输入：模型配置 + 会话根。返回：无。职责：构建 SDK 客户端单例。"""
        self._session_root = session_root
        seed = model.session_header_id or uuid.uuid4().hex
        http_client = httpx.Client(
            trust_env=False,   # 跳过系统代理探测（省 4-7s）
            verify=False,      # 跳过 CA 证书库加载（省 3-4s）
            timeout=model.timeout_s,
        )
        self._client = OpenAI(
            api_key=model.api_key,
            base_url=model.base_url,
            http_client=http_client,
            # Zen 端点要求稳定会话头（同会话同 ID 命中提示词缓存）；其余端点忽略。
            default_headers={
                "x-opencode-session": uuid.uuid5(uuid.NAMESPACE_URL, seed).hex,
            },
        )
        self._model = model.model

    # ---------- 多模态展开 ----------

    def _image_parts(self, msg: UserMessage) -> list[dict]:
        """输入：带附件的 user 消息。返回：image_url 片段列表（读取失败跳过）。"""
        parts: list[dict] = []
        uploads = Path(self._session_root) / ".chat" / "uploads"
        for name in list(msg.images or [])[:4]:
            path = uploads / str(name)
            try:
                b64 = base64.b64encode(path.read_bytes()).decode("ascii")
                mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
                parts.append({"type": "image_url",
                              "image_url": {"url": f"data:{mime};base64,{b64}"}})
            except OSError as e:
                logger.warning("图片附件读取失败（跳过） | path=%s | err=%s", path, e)
        return parts

    def _expand_for_sdk(self, messages: list[Message]) -> list[dict]:
        """输入：类型化消息。返回：SDK 消息列表（含多模态展开）。"""
        has_images = any(isinstance(m, UserMessage) and m.images
                         for m in messages)
        if not has_images:
            return transport_messages(messages)
        out: list[dict] = []
        for m in messages:
            if isinstance(m, UserMessage) and m.images:
                parts: list[dict] = [{"type": "text",
                                      "text": m.content or "（用户发送了图片）"}]
                parts.extend(self._image_parts(m))
                out.append({"role": "user", "content": parts})
            else:
                out.append(m.to_dict())
        logger.info("image parts: 已展开带附件的 user 消息（多模态输入）")
        return out

    # ---------- 出站清洗 ----------

    @staticmethod
    def _sanitize_tool_args(sdk_messages: list[dict]) -> list[dict]:
        """输入：SDK 消息列表。返回：同列表（原地清洗）。

        职责：把 assistant.tool_calls[].function.arguments 里的非法 JSON
        替换为 "{}"。流式截断可能留下残缺参数（真实案例：Zen 端点 400
        "Assistant tool call function.arguments must be valid JSON"——
        上游严格校验历史消息，智谱端宽松故旧版未暴露）。只清洗出站副本，
        不改动会话存储；工具执行侧的容错会向模型说明参数无效。
        Globals Used: 无（纯函数）。
        """
        import json as _json
        for m in sdk_messages:
            if m.get("role") != "assistant":
                continue
            for tc in m.get("tool_calls") or []:
                fn = tc.get("function") or {}
                args = fn.get("arguments")
                if args is None:
                    continue
                try:
                    _json.loads(args)
                except (ValueError, TypeError):
                    logger.warning("清洗非法 tool_call 参数（流式截断残片） | tool=%s",
                                   fn.get("name"))
                    fn["arguments"] = "{}"
        return sdk_messages

    # ---------- 流式 ----------

    def stream_chat(self, system: str, messages: list[Message],
                    tools: list[ToolSchema], max_tokens: int) -> Iterator[StreamDelta]:
        """流式对话（契约见 interfaces.model_client.ModelClient）。

        Raises:
            ContextOverflowError: 上下文超限（上层压缩后重试）。
            EngineError: 其余 API 故障。
        Yields:
            StreamDelta 序列；finish_reason 在最后一片。
        """
        request = {
            "model": self._model,
            "messages": self._sanitize_tool_args(
                [{"role": "system", "content": system}]
                + self._expand_for_sdk(messages)),
            "tools": tools,
            "max_tokens": max_tokens,
            "stream": True,
        }
        try:
            stream = self._client.chat.completions.create(**request)
            yield from self._iter_deltas(stream)
        except ContextOverflowError:
            raise
        except Exception as exc:
            if _is_context_overflow(exc):
                raise ContextOverflowError("模型上下文超限",
                                           model=self._model) from exc
            raise EngineError(f"模型流式请求失败: {exc}",
                              model=self._model) from exc

    def _iter_deltas(self, stream) -> Iterator[StreamDelta]:
        """输入：SDK 流对象。返回：归一化增量迭代器。职责：chunk→StreamDelta。

        单个 chunk 可能同时携带 content/reasoning/多个 tool_call 片段，
        逐类展开为多个 StreamDelta（与旧实现的累积语义一致）。
        """
        for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            finish = choice.finish_reason
            if delta is None:
                if finish:
                    yield StreamDelta(finish_reason=finish)
                continue
            content = getattr(delta, "content", None) or ""
            reasoning = getattr(delta, "reasoning_content", None) or ""
            if content or reasoning:
                yield StreamDelta(content=content, reasoning=reasoning)
            for tc in getattr(delta, "tool_calls", None) or []:
                name = args = ""
                if tc.function:
                    name = tc.function.name or ""
                    args = tc.function.arguments or ""
                yield StreamDelta(tool_index=tc.index, tool_call_id=tc.id or "",
                                  tool_name=name, tool_args=args)
            if finish:
                yield StreamDelta(finish_reason=finish)

    # ---------- 非流式 ----------

    def complete_chat(self, system: str, messages: list[Message],
                      max_tokens: int) -> str:
        """非流式对话（完成闸总结等一次性调用；异常转 EngineError）。"""
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=self._sanitize_tool_args(
                    [{"role": "system", "content": system}]
                    + self._expand_for_sdk(messages)),
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            raise EngineError(f"模型非流式请求失败: {exc}",
                              model=self._model) from exc
