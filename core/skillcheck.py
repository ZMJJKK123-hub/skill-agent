"""skillcheck: 每轮校验 <skill-source> 引用是否真实来自已加载技能。

唯一可信原文源 = 本循环消息历史中 load_skill 实际输出的技能全文。
三重校验：1) 必须存在 <skill-source> 块；2) source 行技能名已加载；
3) '->' 后关键词真实出现在技能原文。返回 (ok, reason)。
主 agent / subagent / teammate 三循环共用，各自以自己消息列表为准。

另：threading.local 在线注册"当前线程已加载的技能"（record_load/any_loaded），
供 run_write/run_edit 前置强制"MOD 文件必须先 load_skill 才能写"（A 方案，
从源头掐断模型凭记忆乱写 MOD 文件的烧钱路径）。
"""
import re
import threading

_SKILL_BLOCK_RE = re.compile(r"<skill\s+name=[\"']?([^\"'\s>]+)[\"']?>(.*?)</skill>", re.S)
_SKILL_SOURCE_RE = re.compile(r"<skill-source>(.*?)</skill-source>", re.S)
_SOURCE_LINE_RE = re.compile(r"^\s*[-*]?\s*source\s*:\s*([\w\-\.]+?)\s*(?:->|=>)\s*(.+?)\s*$", re.I | re.M)

FAIL_STREAK_LIMIT = 5

# ---------- 线程级已加载技能注册中心（A 方案：写 MOD 文件前的强skill前置） ----------
# main / subagent / teammate 各自在独立线程跑 Agent Loop，
# threading.local 保证三者的"已加载技能"互不污染。
# record_load 由 load_skill handler 在成功加载后调用；
# any_loaded 由 run_write/run_edit 判断当前线程是否已 load 过技能。
_local = threading.local()


def record_load(skill_name: str) -> None:
    """登记当前线程已成功加载的技能名（load_skill 成功后调用）。"""
    if not hasattr(_local, "loaded"):
        _local.loaded = set()
    _local.loaded.add(skill_name)


def reset_loaded() -> None:
    """清空当前线程的已加载记录（循环开始/结束时可选调用）。"""
    _local.loaded = set()


def any_loaded() -> list:
    """返回当前线程已加载的技能名列表（空 = 尚未 load 任何技能）。"""
    return sorted(getattr(_local, "loaded", set()) or set())


def move_skills_to_end(messages: list) -> None:
    """把已加载技能全文滚动到消息末尾，旧副本转为占位符（每轮调用前执行）。

    设计目标：技能内容全程只保留一份、且总在模型最近可见位置，
    随轮数滚动而不是累积，token 不随轮数增长。

    OpenAI 协议约束：assistant(tool_calls) 后必须紧跟匹配的 role=tool
    消息，因此旧技能 tool 消息不能删除——保留 role/tool_call_id 骨架、
    仅把内容替换为占位符；技能全文以 role=user 形式追加到末尾（序列合法）。
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


def extract_loaded_skills(messages: list) -> dict:
    """从消息历史提取本循环所有 load_skill 加载过的技能原文 {name: 全文}。

    同时扫描 role=tool 的 load_skill 输出与 role=user 的 <active-skills>
    （move_skills_to_end 会把技能全文滚动到末尾的 user 消息里）。
    """
    loaded = {}
    for msg in messages:
        if msg.get("role") not in ("tool", "user"):
            continue
        c = msg.get("content", "")
        if not isinstance(c, str):
            continue
        for m in _SKILL_BLOCK_RE.finditer(c):
            name, body = m.group(1).strip(), m.group(2).strip()
            if name:
                loaded[name] = body
    return loaded


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().lower()


def _hits(cited: str, skill_text: str) -> list:
    ns, nk = _norm(cited.rstrip("。.;;，,")), _norm(skill_text)
    if ns and ns in nk:
        return [ns]
    hits = []
    for tok in re.split(r"[,;，；\s()\[\]<>]+", ns):
        tok = tok.strip(".:#")
        if len(tok) >= 3 and tok in nk:
            hits.append(tok)
    return hits


def check_skill_source(content: str, loaded: dict) -> tuple:
    """校验 content 中的 <skill-source> 引用。返回 (ok, reason)。"""
    if not content or not content.strip():
        return True, "empty content, skipped"
    blocks = list(_SKILL_SOURCE_RE.findall(content))
    if not blocks:
        return False, ("回复中没有任何 <skill-source> 块；涉及 MOD 代码/资源必须附引用，"
                       "否则判定为无依据创作。")
    for block in blocks:
        src_lines = _SOURCE_LINE_RE.findall(block)
        if not src_lines:
            return False, "<skill-source> 块内缺少 'source: 技能名 -> 原文条目' 行。"
        for skill_name, cited in src_lines:
            skill_name = skill_name.strip().rstrip(":")
            if skill_name not in loaded:
                return False, (f"引用的技能 '{skill_name}' 尚未通过 load_skill 加载"
                               f"（已加载: {', '.join(loaded.keys()) or '无'}）。请先加载再引用。")
            if not _hits(cited, loaded[skill_name]):
                return False, (f"技能 '{skill_name}' 的引文 \"{cited[:120]}\" 在技能原文中"
                               "找不到匹配；请复制真实原文片段，不要凭记忆概括。")
    return True, "all <skill-source> references verified against loaded skills"


# ---------- 三循环共用的「每轮校验注入」 ----------
# 每个 agent 循环（主/sub/teammate）各自用独立 tag，状态互不干扰。
_loop_state: dict = {}

def init_per_loop(tag: str) -> None:
    """循环开头调用：重置该循环的校验状态（last 结果、连续失败计数）。"""
    _loop_state[tag] = {"last": None, "streak": 0}

def run_loop_check(tag: str, content: str, messages: list) -> bool:
    """每轮统一校验：已按用户要求关闭强制 <skill-source> 引用校验。

    现在总是返回 True，不再阻断 agent；让 agent 先写代码/资源，
    跑 build/GameTest 报错后再回头查技能/源码。
    """
    st = _loop_state.setdefault(tag, {"last": None, "streak": 0})
    st["streak"] = 0
    st["last"] = "passed"
    return True
