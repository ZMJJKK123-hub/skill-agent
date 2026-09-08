# -*- coding: utf-8 -*-
"""ask_user_question tool implementation (moved from core/tools.py)."""
import json
import time
from pathlib import Path

from ... import config
from ...config import logger
from ...config import logger  # 统一日志：降级路径记录

def _normalize_questions(questions, options: list) -> list[dict]:
    """输入：多问题列表或 legacy 单问题。返回：标准 questions 列表（空=无效）。

    职责：兼容 dict/str 两种多问题元素与 legacy (questions, options) 入参。
    """
    options = options or []
    if isinstance(questions, list) and questions:
        qs = []
        for q in questions:
            if isinstance(q, dict):
                qs.append({"question": str(q.get("question", "")), "options": list(q.get("options") or [])})
            else:
                qs.append({"question": str(q), "options": []})
        return qs
    return [{"question": str(questions or ""), "options": options}]


def _format_answers(data: dict, qs: list[dict]) -> str:
    """输入：answer.json 内容 + 问题列表。返回：结构化多答案 JSON 串。

    职责：多答案按序与 qs 对齐；兼容旧单答 {"answer": "..."}。
    """
    raw_answers = data.get("answers")
    if isinstance(raw_answers, list):
        out = []
        for idx, q in enumerate(qs):
            ans = ""
            if idx < len(raw_answers):
                candidate = raw_answers[idx]
                ans = str(candidate.get("answer", "")) if isinstance(candidate, dict) else str(candidate)
            out.append({"question": q["question"], "answer": ans})
        return json.dumps(out, ensure_ascii=False)
    legacy = str(data.get("answer", ""))
    return json.dumps([{"question": qs[0]["question"], "answer": legacy}], ensure_ascii=False)


def _auto_mode_reply() -> str | None:
    """全自动模式的替代回复（开启时返回说明；关闭返回 None）。"""
    if not config.AUTO_MODE:
        return None
    logger.info("ask_user_question | 全自动模式开启，跳过用户提问")
    return (
        "AUTO_MODE is enabled: cannot block for user input. "
        "Use your best judgment / reasonable defaults, and clearly state assumptions "
        "in your final summary."
    )


def _wait_answer_files(apath: Path, qpath: Path, deadline: float,
                       qs: list) -> str | None:
    """轮询 answer.json；读到即清理问答文件并返回结构化答案。

    Args:
        apath/qpath: 答案与问题文件。deadline: 截止时间戳。
        qs: 问题列表（答案对齐用）。
    Returns:
        结构化答案 JSON 串；超时返回 None（清理交调用方）。
    """
    while time.time() < deadline:
        if apath.exists():
            try:
                data = json.loads(apath.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                time.sleep(1)
                continue
            try:
                apath.unlink()
            except OSError as e:
                logger.warning("_wait_answer_files 降级忽略 | %s", e)
            _cleanup_question_file(qpath)
            return _format_answers(data, qs)
        time.sleep(1)
    return None


def _cleanup_question_file(qpath: Path) -> None:
    """清理问题文件（超时/答后通用，避免前端一直显示）。"""
    if qpath.exists():
        try:
            qpath.unlink()
        except OSError as e:
            logger.warning("_cleanup_question_file 降级忽略 | %s", e)


def run_ask_user(questions, options: list = None) -> str:
    """向用户提出一个或多个问题并阻塞等待回答（文件 IPC：写 question.json，轮询 answer.json）。

    支持两种入参：
      - 多问题：questions=[{"question": "...", "options": [...]}, ...]
      - 单问题（legacy）：questions="...", options=[...]
    前端轮询 /api/question 发现待答问题 → 展示所有问题（可选项/自由填写，
    确认前可随意切换修改）→ 用户点确认 → POST /api/answer 写 answer.json
    （{"answers": [{"question": "...", "answer": "..."}, ...]}）→ 这里读到后
    返回结构化多答案 JSON、agent 继续。
    超时：从用户确认提交后开始计时 5 分钟（等待 agent 读取），
    用户填写阶段不设超时（避免慢慢填被强杀）。
    """
    qs = _normalize_questions(questions, options)
    if not qs:
        return "Error: 问题为空"

    auto = _auto_mode_reply()
    if auto:
        return auto

    base = Path.cwd()  # agent 子进程 cwd = 会话目录（run_task.py os.chdir）
    qpath = base / "question.json"
    apath = base / "answer.json"
    try:
        qpath.write_text(
            json.dumps({"questions": qs}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        return f"Error: 无法写入问题文件: {e}"
    logger.info(f"ask_user_question | 提出 {len(qs)} 个问题")

    # 等 answer.json：用户确认提交后这里才读到；读到后 5 分钟超时兜底
    # （防止前端已确认但消息丢失导致 agent 永久卡死）。
    deadline = time.time() + 300
    try:
        answer = _wait_answer_files(apath, qpath, deadline, qs)
    except Exception as e:
        return f"Error: {e}"
    if answer is None:
        _cleanup_question_file(qpath)
        return "(用户未回答，已超时)"
    return answer


