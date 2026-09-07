# -*- coding: utf-8 -*-
"""skillcheck：技能加载登记与技能全文滚动（死代码清扫后的存活面）。

历史：本模块原含 <skill-source> 引用三重校验（check_skill_source 等
约 120 行）——该功能已按用户要求关闭且全库零引用，随死代码清扫删除。
存活职责仅两项：
  1. threading.local 在线登记"当前线程已加载的技能"
     （record_load / any_loaded）——load_skill 成功后登记，
     run_write/run_edit 据此强制"MOD 文件必须先 load_skill 才能写"。
  2. move_skills_to_end：已加载技能全文滚动到消息末尾
     （旧副本转占位符），token 不随轮数增长。
"""
import re
import threading

_SKILL_BLOCK_RE = re.compile(r"<skill\s+name=[\"']?([^\"'\s>]+)[\"']?>(.*?)</skill>", re.S)

# ---------- 线程级已加载技能注册中心 ----------
# main / subagent / teammate 各自在独立线程跑 Agent Loop，
# threading.local 保证三者的"已加载技能"互不污染。
_local = threading.local()


def record_load(skill_name: str) -> None:
    """登记当前线程已成功加载的技能名（load_skill 成功后调用）。"""
    if not hasattr(_local, "loaded"):
        _local.loaded = set()
    _local.loaded.add(skill_name)


def any_loaded() -> list:
    """返回当前线程已加载的技能名列表（空 = 尚未 load 任何技能）。"""
    return sorted(getattr(_local, "loaded", set()) or set())


def move_skills_to_end(messages: list) -> None:
    """把已加载技能全文滚动到消息末尾，旧副本转为占位符（原地变更）。

    OpenAI 协议约束：assistant(tool_calls) 后必须紧跟匹配的 role=tool
    消息，因此旧技能 tool 消息不能删除——保留骨架、仅把内容替换为
    占位符；技能全文以 role=user 形式追加到末尾（序列合法）。
    同名技能取最后一次 load 的内容（后出现的覆盖旧版）。
    """
    skills = {}
    for msg in messages:
        if msg.get("role") != "tool":
            continue
        c = msg.get("content")
        if not isinstance(c, str):
            continue
        blocks = list(_SKILL_BLOCK_RE.findall(c))
        if not blocks:
            continue
        for name, body in blocks:
            name = name.strip()
            if name:
                skills[name] = body.strip()
        msg["content"] = "<skill-content-rolled-to-latest/>"
    if not skills:
        return
    active = "".join(
        f'<skill name="{name}">\n{body}\n</skill>' for name, body in skills.items()
    )
    messages.append(
        {
            "role": "user",
            "content": (
                f"<active-skills>\n{active}\n</active-skills>\n"
                "以上为当前已加载的技能全文（主要参考）。写 MOD 代码前应先加载并依据技能；"
                "编译/测试报错需要查 API 时再从 ERROR_LIST / search_api / 技能查，mc_java_sources 仅作后备。"
            ),
        }
    )


# ---------- 每"循环"占位校验（功能已关闭，保留接口供 subagent 调用） ----------

def run_loop_check(tag: str, content: str, messages: list) -> bool:
    """每轮统一校验：已按用户要求关闭强制 <skill-source> 引用校验，恒 True。

    保留签名供 subagent 循环调用（让 agent 先写代码，报错后再查技能）。
    """
    return True
