# -*- coding: utf-8 -*-
"""人格系统：提示词表 / 会话人格持久化 / 切换命令解析（由 main.py 迁出）。"""
import os
from pathlib import Path
import logging  # 统一日志：降级路径记录

logger = logging.getLogger("tsinghua.personas")

PERSONA_PROMPTS = {
    "default": "你是默认的普通 AI 助手，语气自然、专业、温和，不刻意扮演任何特定角色。",
    "meow": "你现在是一只可爱的喵娘，说话要时不时带“喵”，语气亲昵俏皮，称呼用户为主人。",
    "cool": "你是一个高冷高效的技术助理，回答简洁直接，少说废话，不卖萌。",
    "cheer": "你是一个元气满满的少女，说话有活力，喜欢用感叹号和 emoji，语气开朗。",
    "elegant": "你是一位优雅温柔的姐姐，说话正式、体贴、有礼貌，语气从容。",
    "mystic": "你是一位神秘占卜师，说话带神秘色彩，喜欢用塔罗/星象的比喻，语气悠远有韵味。",
    "senpai": "你是一位热心靠谱的学长/前辈，说话亲切轻松，偶尔会吐槽，但总能把事情讲清楚。",
}

PERSONA_DISPLAY = {
    "meow": "喵娘",
    "cool": "高冷技术助理",
    "cheer": "元气少女",
    "elegant": "优雅姐姐",
    "mystic": "神秘占卜师",
    "senpai": "学长前辈",
    "default": "通用",
}

#: 人格切换命令别名（用户话术 → persona key）
PERSONA_ALIAS = {
    "喵娘": "meow", "喵娘模式": "meow", "猫娘": "meow",
    "高冷": "cool", "高冷技术助理": "cool",
    "元气": "cheer", "元气少女": "cheer",
    "优雅": "elegant", "优雅姐姐": "elegant",
    "神秘": "mystic", "神秘占卜师": "mystic", "占卜师": "mystic",
    "学长": "senpai", "前辈": "senpai", "学长前辈": "senpai",
    "默认": "default", "通用": "default",
}


def persona_file(session_root: Path) -> Path:
    """输入：会话根。返回：人格记忆文件路径。"""
    return session_root / "persona.txt"


def resolve_persona_key(session_id: str, workdir) -> str:
    """返回会话应使用的人格 key：先取会话文件，再取 DSH_PERSONA 环境变量。"""
    pfile = persona_file(workdir(session_id))
    if pfile.exists():
        try:
            key = pfile.read_text(encoding="utf-8").strip().lower()
            if key in PERSONA_PROMPTS:
                return key
        except OSError as e:
            logger.debug("resolve_persona_key 降级忽略 | %s", e)
    return os.environ.get("DSH_PERSONA", "").strip().lower()


def set_persona(session_id: str, persona_key: str, workdir) -> bool:
    """写入会话人格（持久化到 persona.txt）；未知 key 返回 False。"""
    if persona_key not in PERSONA_PROMPTS:
        return False
    try:
        persona_file(workdir(session_id)).write_text(persona_key, encoding="utf-8")
        return True
    except OSError:
        return False


def session_persona_command(messages: list) -> "tuple[str, str] | None":
    """检测用户是否想切换人格，返回 (persona_key, 显示名)；无则 None。"""
    from normalize import last_user_content
    c = last_user_content(messages)
    if not c:
        return None
    for label, key in PERSONA_ALIAS.items():
        if f"切换{label}" in c or f"切换成{label}" in c or f"人格{label}" in c:
            return key, label
    return None
