"""toolkit: 工具注册表与执行管线（移植 DSH packages/core/tools 设计到 Python 裁剪版）。

DSH 参照：
- ToolDefinition：模型侧只发 {name, description, parameters} 白名单，宿主侧持有
  handler + 执行元数据（timeoutMs / isConcurrencySafe / readonly 等）。
- 执行管线：pre 钩子（allow/deny/ask 决策）→ 单调 guard（仅拒绝，监听顺序无法
  撤销拒绝）→ around 分发（超时/重试/指标）→ handler → post 钩子（接受/替换/block）。

本项目裁剪版（行为保持与旧 TOOL_HANDLERS 直调一致）：
- ToolDef 由现有 TOOLS（OpenAI dict）+ TOOL_HANDLERS + 元数据构建；
- schemas(include/exclude) 声明式过滤，替代 leader/subagent/supervisor 的手工列表拷贝；
- execute() 是 total 函数：任何钩子/handler 异常都转成温和错误文本，绝不抛出；
- 超时钩子 opt-in（timeout_ms 声明才生效），默认不声明——旧行为不变。
"""

import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set


@dataclass
class ToolDef:
    """一个已注册工具：模型可见 schema + handler + 执行元数据。"""

    name: str
    description: str
    parameters: dict                        # OpenAI function calling 参数 schema
    handler: Callable                       # 接收 **kwargs，返回文本结果
    timeout_ms: Optional[int] = None        # 超时（around 包装：线程 + join）
    concurrency_safe: bool = False          # 并行声明（对齐 executionMode，暂未调度用）
    readonly: bool = False                  # 只读声明（supervisor 过滤用）
    needs_approval: Optional[str] = None    # 预留：审批模式 ask/allow/deny（M5+）

    def to_openai_dict(self) -> dict:
        """模型可见投影：只含 {type, function:{name, description, parameters}}。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """工具注册表：声明式过滤 + 可扩展执行管线。

    兼容层：tools.py 里现有的 TOOLS / TOOL_HANDLERS 仍保留，由本注册表派生——
    迁移期任何直接使用旧结构的代码不受影响。
    """

    def __init__(self):
        self._tools: Dict[str, ToolDef] = {}
        self._pre_hooks: List[Callable] = []
        self._guards: List[Callable] = []
        self._post_hooks: List[Callable] = []

    # ---------- 注册 ----------

    def register(self, tool: ToolDef) -> None:
        """注册一个工具；重名抛 ValueError（fail loud）。"""
        if tool.name in self._tools:
            raise ValueError(f'tool "{tool.name}" is already registered')
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDef]:
        return self._tools.get(name)

    def names(self) -> list:
        return sorted(self._tools)

    # ---------- 声明式过滤（对齐 DSH schemas(scope) + restrict allow/deny）----------

    def schemas(
        self,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
    ) -> list:
        """返回 OpenAI 格式工具列表（保持注册顺序——与旧 TOOLS 列表顺序一致）。

        include 缺省 = 全部；exclude 从 include 结果中剔除。
        """
        names = list(self._tools.keys())
        if include is not None:
            names = [n for n in names if n in include]
        if exclude:
            names = [n for n in names if n not in exclude]
        return [self._tools[n].to_openai_dict() for n in names]

    def readonly_names(self) -> list:
        """所有声明 readonly 的工具名（supervisor 可用 include= 自动纳入）。"""
        return sorted(n for n, t in self._tools.items() if t.readonly)

    # ---------- 管线钩子 ----------

    def add_pre_hook(self, fn: Callable) -> None:
        """pre 钩子：fn(name, args) → None(放行) | (拒绝理由字符串)。

        对齐 tools/pre-execute 的 deny 语义（allow 即无返回）。
        """
        self._pre_hooks.append(fn)

    def add_guard(self, fn: Callable) -> None:
        """单调守卫：fn(name, args) → None(放行) | 拒绝理由。仅拒绝，无 allow。"""
        self._guards.append(fn)

    def add_post_hook(self, fn: Callable) -> None:
        """post 钩子：fn(name, args, output) → None(保留) | 替换文本。

        对齐 tools/post-execute 的 accept/block 语义（可改写模型可见结果）。
        """
        self._post_hooks.append(fn)

    # ---------- 执行 ----------

    def execute(self, name: str, args: dict) -> str:
        """执行一个工具调用（total：任何异常都转温和错误文本，不向调用方抛出）。

        管线：pre 钩子 → guard → handler（around 超时）→ post 钩子。
        未知工具 / 钩子拒绝 / handler 异常 / 超时 均返回 Error 文本。
        """
        tool = self._tools.get(name)
        if tool is None:
            return f"Unknown tool: {name}"

        # pre 钩子（deny 语义）
        for hook in self._pre_hooks:
            try:
                reason = hook(name, args)
            except Exception as e:
                reason = f"pre-hook error: {e}"
            if reason:
                return f"Error: {reason}"

        # 单调 guard（仅拒绝）
        for guard in self._guards:
            try:
                reason = guard(name, args)
            except Exception as e:
                reason = f"guard error: {e}"
            if reason:
                return f"Error: {reason}"

        # around 分发 + handler
        if tool.timeout_ms:
            output = self._execute_with_timeout(tool, args)
        else:
            try:
                output = tool.handler(**args)
            except Exception as e:
                output = f"Error executing {name}: {e}"
        if not isinstance(output, str):
            output = str(output)

        # post 钩子（可改写结果）
        for hook in self._post_hooks:
            try:
                replaced = hook(name, args, output)
            except Exception as e:
                replaced = f"Error: post-hook error: {e}"
            if replaced is not None:
                output = replaced
        return output

    def _execute_with_timeout(self, tool: ToolDef, args: dict) -> str:
        """超时包装：daemon 线程 + join(timeout)；超时返回温和错误。

        注意：不能硬杀线程内已启动的子进程（与 DSH 同约束）；超时工具的
        handler 自身应把耗时操作放进可取消的子进程（如 bash 的进程树强杀）。
        """
        box: Dict[str, str] = {}
        err: Dict[str, Exception] = {}

        def _run():
            try:
                box["out"] = tool.handler(**args)
            except Exception as e:  # noqa: BLE001
                err["e"] = e

        t = threading.Thread(target=_run, daemon=True, name=f"tool-{tool.name}")
        t.start()
        t.join(timeout=tool.timeout_ms / 1000.0)
        if t.is_alive():
            return (f"Error: Tool '{tool.name}' timed out after "
                    f"{tool.timeout_ms}ms. 请拆小任务或改用 run_in_background。")
        if "e" in err:
            return f"Error executing {tool.name}: {err['e']}"
        out = box.get("out")
        return out if isinstance(out, str) else str(out)


# 单例：由 tools.py 在模块底部构建并填充（避免循环导入）
tool_registry = ToolRegistry()
