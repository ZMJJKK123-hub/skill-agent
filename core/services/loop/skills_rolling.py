# -*- coding: utf-8 -*-
"""已加载技能的滚动保留（services/loop 层；旧 core/skillcheck 移植）。

设计：技能全文全程只保留一份且总在模型最近可见位置——旧 load_skill
的 tool 消息内容替换为占位符（OpenAI 协议要求 tool 消息骨架保留），
全文以 user 消息形式滚动追加到末尾；token 不随轮数增长。
"""
from __future__ import annotations

import re

from ...domain.messages import Message, ToolResultMessage, UserMessage

#: tool 消息内容里的 <skill name="...">全文</skill> 块。
_SKILL_BLOCK_RE = re.compile(r"<skill\s+name=[\"']?([^\"'\s>]+)[\"']?>(.*?)</skill>", re.S)

#: 旧副本被替换后的占位符（保持 role/tool_call_id 骨架合法）。
ROLLED_PLACEHOLDER = "<skill-content-rolled-to-latest/>"

#: 滚动块尾部的使用指引（与旧实现逐字一致）。
_ACTIVE_SKILLS_TAIL = (
    "以上为当前已加载的技能全文（主要参考）。写 MOD 代码前应先加载并依据技能；"
    "编译/测试报错需要查 API 时再从 ERROR_LIST / search_api / 技能查，mc_java_sources 仅作后备。"
)


def move_skills_to_end(messages: list[Message]) -> None:
    """把已加载技能全文滚动到消息末尾（同名取最后一次加载的内容）。

    Args:
        messages: 当前消息列表（原地修改：旧块置占位符，末尾追加全文）。
    """
    skills: dict[str, str] = {}
    for m in messages:
        if not isinstance(m, ToolResultMessage) or not isinstance(m.content, str):
            continue
        blocks = list(_SKILL_BLOCK_RE.findall(m.content))
        if not blocks:
            continue
        for name, body in blocks:
            name = name.strip()
            if name:
                skills[name] = body.strip()
        m.content = ROLLED_PLACEHOLDER
    if not skills:
        return
    active = "".join(
        f'<skill name="{name}">\n{body}\n</skill>' for name, body in skills.items())
    messages.append(UserMessage(content=(
        f"<active-skills>\n{active}\n</active-skills>\n{_ACTIVE_SKILLS_TAIL}")))
