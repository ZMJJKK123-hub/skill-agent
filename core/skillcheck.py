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


def extract_loaded_skills(messages: list) -> dict:
    """从消息历史提取本循环所有 load_skill 加载过的技能原文 {name: 全文}。"""
    loaded = {}
    for msg in messages:
        if msg.get("role") != "tool":
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
    """每轮统一校验：PASS→注入 PASSED（去重）；FAIL→注入 FAILED 并返回 False（调用方 continue）。
    content 为空（工具轮）自动跳过视为通过。连续 FAIL ≥ FAIL_STREAK_LIMIT 时附加重读指引。"""
    st = _loop_state.setdefault(tag, {"last": None, "streak": 0})
    if not content or not content.strip():
        st["streak"] = 0
        return True
    loaded = extract_loaded_skills(messages)
    ok, reason = check_skill_source(content, loaded)
    if ok:
        st["streak"] = 0
        if st["last"] != "passed":
            messages.append({"role": "user", "content":
                "<skill-source-check> PASSED: 引用原文与已加载技能一致。"})
            st["last"] = "passed"
        return True
    st["last"] = "failed"
    st["streak"] += 1
    extra = ""
    if st["streak"] >= FAIL_STREAK_LIMIT:
        extra = ("\n你已连续多轮未通过引用校验，请停止写作，先调用 load_skill "
                 "仔细阅读相关技能原文，再基于其真实内容继续。")
    messages.append({"role": "user", "content":
        f"<skill-source-check> FAILED: {reason}{extra}\n"
        "请重新 load_skill 加载正确技能并按其原文补充 <skill-source>，通过前不得结束。"})
    return False
