# -*- coding: utf-8 -*-
"""ask_user_question tool implementation (moved from core/tools.py)."""
import json
import time
from pathlib import Path

from . import config
from .config import logger

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
    options = options or []
    # 归一化为标准 questions 列表
    if isinstance(questions, list) and questions:
        qs = []
        for q in questions:
            if isinstance(q, dict):
                qs.append({"question": str(q.get("question", "")), "options": list(q.get("options") or [])})
            else:
                qs.append({"question": str(q), "options": []})
    else:
        qs = [{"question": str(questions or ""), "options": options}]
    if not qs or not qs[0]["question"].strip():
        return "Error: 问题为空"

    if config.AUTO_MODE:
        logger.info("ask_user_question | 全自动模式开启，跳过用户提问")
        return (
            "AUTO_MODE is enabled: cannot block for user input. "
            "Use your best judgment / reasonable defaults, and clearly state assumptions "
            "in your final summary."
        )

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
        while time.time() < deadline:
            if apath.exists():
                try:
                    data = json.loads(apath.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    time.sleep(1)
                    continue
                try:
                    apath.unlink()
                except OSError:
                    pass
                if qpath.exists():
                    try:
                        qpath.unlink()
                    except OSError:
                        pass
                # 结构化多答案：{answers: [{question, answer}, ...]}
                raw_answers = data.get("answers")
                if isinstance(raw_answers, list):
                    # 归一化：与 qs 对齐（可能缺题/多余，按 question 文本匹配或按序）
                    out = []
                    for idx, q in enumerate(qs):
                        ans = ""
                        if idx < len(raw_answers):
                            candidate = raw_answers[idx]
                            if isinstance(candidate, dict):
                                ans = str(candidate.get("answer", ""))
                            else:
                                ans = str(candidate)
                        out.append({"question": q["question"], "answer": ans})
                    return json.dumps(out, ensure_ascii=False)
                # 兼容旧单答格式：{"answer": "..."}
                legacy = str(data.get("answer", ""))
                return json.dumps([{"question": qs[0]["question"], "answer": legacy}], ensure_ascii=False)
            time.sleep(1)
    except Exception as e:
        return f"Error: {e}"
    # 超时：清掉问题，避免前端一直显示
    if qpath.exists():
        try:
            qpath.unlink()
        except OSError:
            pass
    return "(用户未回答，已超时)"

