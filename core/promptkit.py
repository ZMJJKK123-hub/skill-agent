"""promptkit: 系统提示词 section 化组装（移植 DSH system-prompt 设计）。

DSH 参照：packages/core/system-prompt —— PromptSection{name, order, text, complete?}
按 order 升序拼接，{{variable}} 严格插值（未注册变量直接报错，不静默留空）。

本项目裁剪版（单 agent 单 prompt，无 scope 链/瀑布）：
- section(name, order, text | callable, complete=False)
- variable(name, provider) 注册变量
- assemble() 排序拼接；join 分隔符为 "\\n\\n"（与历史导入期拼接行为逐字一致）
- complete: True 的段独占整个提示词（供将来 preset persona 自持）

兼容性保证：M1 阶段 assemble() 的渲染结果与旧 `config.SYSTEM`（原始 persona 字符串
+ tools.py 导入期追加块）逐字一致，由 golden 对照脚本验证。
"""

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Union

# {{name}} —— name 限定小写字母开头 [a-z][a-z0-9_]*，与 DSH 一致
_VAR_RE = re.compile(r"\{\{\s*([a-z][a-z0-9_]*)\s*\}\}")


class PromptError(ValueError):
    """提示词组装错误：重复注册 / 未知变量 / 多个 complete 段。"""


@dataclass
class PromptSection:
    """一段有序提示词。text 可以是静态字符串或按当前环境求值的函数。"""

    name: str
    order: int
    text: Union[str, Callable[[Dict[str, str]], str]]
    complete: bool = False


class PromptAssembler:
    """注册有序 section 与变量，assemble() 渲染最终系统提示词。

    顺序约定（对齐 DSH）：-100 身份 / 0 persona / 100-199 工具指引 /
    200+ 规则。同 order 按注册顺序稳定输出。
    """

    def __init__(self, variables: Optional[Dict[str, Callable[[], str]]] = None):
        self._sections: List[PromptSection] = []
        self._names: set = set()
        self._variables: Dict[str, Callable[[], str]] = dict(variables or {})

    # ---------- 注册 ----------

    def section(self, section: PromptSection) -> "PromptAssembler":
        """注册一个 section；重名抛 PromptError。"""
        if not section.name:
            raise PromptError("prompt section name must not be empty")
        if section.name in self._names:
            raise PromptError(f'prompt section "{section.name}" is already registered')
        self._names.add(section.name)
        self._sections.append(section)
        return self

    def variable(self, name: str, provider: Callable[[], str]) -> "PromptAssembler":
        """注册一个 {{name}} 变量；非法名抛 PromptError。"""
        if not _VAR_RE.fullmatch("{{" + name + "}}"):
            raise PromptError(f'invalid prompt variable name "{name}"')
        self._variables[name] = provider
        return self

    # ---------- 渲染 ----------

    def render(self, text: str) -> str:
        """对单段文本做严格变量插值：未知变量抛 PromptError。"""

        def _repl(m: "re.Match[str]") -> str:
            name = m.group(1)
            provider = self._variables.get(name)
            if provider is None:
                raise PromptError(
                    f'unknown prompt variable "{{{{{name}}}}}" in section text'
                )
            return provider()

        return _VAR_RE.sub(_repl, text)

    def _section_text(self, s: PromptSection, env: Dict[str, str]) -> str:
        if callable(s.text):
            return s.text(env)
        return s.text

    def assemble(self) -> str:
        """排序拼接所有 section；effective complete 段独占；空段跳过。"""
        ordered = sorted(self._sections, key=lambda s: (s.order,))
        complete = [s for s in ordered if s.complete]
        if len(complete) > 1:
            raise PromptError("more than one complete section")
        env: Dict[str, str] = {}
        if complete:
            return self.render(self._section_text(complete[0], env))
        parts = []
        for s in ordered:
            text = self._section_text(s, env)
            if not text:
                continue
            parts.append(self.render(text))
        return "\n\n".join(parts)

    # ---------- 只读视图（供调试/测试） ----------

    def names(self) -> list:
        """当前已注册 section 名（按 order 排序）。"""
        return [s.name for s in sorted(self._sections, key=lambda s: (s.order,))]
