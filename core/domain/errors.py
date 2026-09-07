# -*- coding: utf-8 -*-
"""引擎级自定义异常（domain 层，零依赖）。

按 agent.md Rule 2.4（显式错误隔离）：核心业务边界必须抛带语义
和上下文的异常，禁止裸 Exception / 静默吞掉。本模块是全部异常的
唯一定义点，各层只 import 不再自定义。
"""
from __future__ import annotations

from typing import Any


class EngineError(Exception):
    """引擎错误基类：所有 core 内异常的公共父类。

    类变量/属性：
        context: dict[str, Any] — 结构化上下文（session/round/tool 名等），
        供日志按 key-value 输出（Rule 2.5 结构化日志）。

    生命周期：由各层 raise，统一在 bootstrap/入口层捕获转成用户可见文本；
    服务层内部只捕自己认识的子类。
    """

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.context: dict[str, Any] = dict(context)

    def __str__(self) -> str:
        """带上下文的字符串表示（日志与用户提示共用）。"""
        base = super().__str__()
        if not self.context:
            return base
        pairs = " ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{base} | {pairs}"


class ConfigError(EngineError):
    """配置缺失/非法（如 API Key 为空、模式名不识别）。"""


class ContextOverflowError(EngineError):
    """模型 API 报上下文超限。

    上下文：approx_tokens — 触发时的粗略 token 估算（若可得）。
    语义：调用方应压缩上下文后重试，而不是终止任务。
    """


class LoopAbortError(EngineError):
    """主循环硬上限触发（工具轮数/总轮数等最后防线）。

    上下文：reason — 人可读的中止原因；round_idx — 触发轮号。
    语义：不可重试，调用方收集部分进度后收尾。
    """


class ToolExecutionError(EngineError):
    """工具执行失败（handler 抛出的非预期异常包装）。

    上下文：tool — 工具名；args_summary — 参数摘要（截断，防泄漏大负载）。
    """


class SandboxViolationError(EngineError):
    """沙箱违规（路径越界、禁写模式下的写操作等）。

    上下文：path — 违规路径；mode — 当前沙箱模式。
    """


class SessionStoreError(EngineError):
    """会话存储读写失败（.chat/ 文件协议损坏、磁盘错误）。

    上下文：path — 出错文件；operation — read/write。
    """
