# -*- coding: utf-8 -*-
"""技能目录 digest 动态注入（由 skills.py 拆出，M2 对齐 DSH tool-skill catalog）。

类职责：digest 计算 / 历史比对 / 目录消息渲染 / 变化才追加注入。
生命周期：loop 的 skill_catalog 注入器每轮调用。
"""
import hashlib

from ...config import logger
from .skills import skill_loader  # 单例在 skills 中部已定义（尾部才导入本模块）

# ---------- M2：技能目录 digest 动态注入（对齐 DSH tool-skill catalog）----------
# 目录作为 user 角色消息注入会话历史：digest 变化才追加新目录（整表替换语义），
# 不变则零开销；auto_compact 把目录消息压进摘要区后，下一轮自然重新注入。
CATALOG_MARKER = "<available-skills>"

# 目录消息中的路由指引（与旧 system prompt skill:catalog section 文案一致）
CATALOG_ROUTING = (
    "For Minecraft MOD development, load the most relevant skill FIRST with load_skill before writing any "
    "Java/resource file. For a COMPLEX mod (dimensions/entities/worldgen/armor/structures/GameTest), batch-load "
    "this skill bundle in ONE turn before writing code: forge-simple-min-mod, forge-items, forge-blocks, "
    "forge-concept-registries, forge-concept-events, forge-gettingstarted, forge-networking, minecraft-entity-type, "
    "minecraft-dimension-type, minecraft-dimension, minecraft-structure, minecraft-structure-set, "
    "minecraft-equipment-asset, minecraft-data-component, minecraft-test-instance. Skills are the PRIMARY reference. "
    "Do NOT read mc_java_sources or starter/docs before writing; source is backup only after a compile/test error.\n"
    "本目录仅含技能摘要（name + 首行描述），须先加载对应技能全文再写 MOD 代码。"
)


def _catalog_digest(entries: list) -> str:
    """对 entries（name, desc）序列化取 sha256——对齐 DSH 基于 entries 而非渲染文本。"""
    return _hashlib.sha256(
        json.dumps(entries, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _last_catalog_digest(messages: list) -> str | None:
    """从消息历史找最近的目录消息，返回其 digest；无则 None。"""
    for m in reversed(messages):
        if m.get("role") != "user":
            continue
        content = m.get("content")
        if not isinstance(content, str) or not content.lstrip().startswith(CATALOG_MARKER):
            continue
        m2 = re.search(r"digest:\s*([0-9a-f]{64})", content)
        if m2:
            return m2.group(1)
    return None


def render_catalog_message(entries: list, digest: str) -> str:
    """渲染目录消息（marker + digest + 条目 + 路由指引）。"""
    lines = [CATALOG_MARKER, f"digest: {digest}"]
    lines.append("Available skills (use load_skill to access):")
    if entries:
        for name, desc in entries:
            lines.append(f"  - {name}: {desc}")
    else:
        lines.append("  (no skills available)")
    lines.append("</available-skills>")
    lines.append("")
    lines.append(CATALOG_ROUTING)
    return "\n".join(lines)


def maybe_inject_skill_catalog(messages: list) -> bool:
    """digest 变化（或无目录消息）时注入最新目录；返回是否注入。"""
    entries = skill_loader.catalog_entries()
    digest = _catalog_digest(entries)
    if _last_catalog_digest(messages) == digest:
        return False
    messages.append({"role": "user", "content": render_catalog_message(entries, digest)})
    logger.info(f"maybe_inject_skill_catalog | 注入 {len(entries)} 个技能目录条目")
    return True


# 重构：不再传 "skills"——缺省时自动解析为 core/skills（包相对），
# 保证从任意启动目录都能找到技能，与 cwd 无关。
