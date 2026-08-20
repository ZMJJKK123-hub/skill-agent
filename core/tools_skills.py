# -*- coding: utf-8 -*-
"""SkillLoader + skill catalog implementations (moved from core/tools.py)."""
import hashlib as _hashlib
import json
import os
import re
from pathlib import Path

import yaml

from .config import logger
from .skillcheck import record_load

# ---------- SkillLoader（第 5 课：两层知识注入；M2：多源分层 + 正文现读）----------
# M2 对齐 DSH skill 注册表设计：
# - 多源分层（rank 小的赢）：会话技能（<session_root>/skills，rank 100）
#   > 自定义目录（DSH_CUSTOM_SKILL_DIRS，rank 300）> 内置 core/skills（rank 600）
# - 形态：目录包 <name>/SKILL.md 或平铺 <name>.md
# - frontmatter 调用策略：disable-model-invocation（模型不可调）、user-invocable
# - 目录（name+首行描述）由 digest 驱动注入会话消息（maybe_inject_skill_catalog）；
#   正文每次 get_content() 现读磁盘——会话中编辑 SKILL.md 即时生效。

# 技能来源优先级（rank 越小越优先；同名低 rank 胜出）
RANK_SESSION = 100
RANK_CUSTOM = 300
RANK_BUILTIN = 600


class SkillLoader:
    """多源技能加载器：目录描述 + 按需加载（正文现读）。

    第一层：get_descriptions()/catalog_entries() 返回技能目录（名称+首行描述），
    由 agent 循环按 digest 变化注入会话消息（M2 起不再拼进 system prompt）。
    第二层：get_content(name) 每次重新读盘解析 SKILL.md，通过 load_skill 按需注入。

    skills 目录默认相对本包（core/skills/），不依赖运行时的 cwd——
    这样无论从项目根、server_app 还是任意目录启动，技能都能被找到。
    """

    def __init__(self, skills_dir: str | None = None):
        # roots: [(rank, path)]，rank 小者优先
        self.skills_dir = skills_dir or str(Path(__file__).resolve().parent / "skills")
        self.roots: list = [(RANK_BUILTIN, self.skills_dir)]
        session_root = os.environ.get("DSH_SESSION_ROOT", "")
        if session_root:
            self.roots.append((RANK_SESSION, os.path.join(session_root, "skills")))
        custom = os.environ.get("DSH_CUSTOM_SKILL_DIRS", "")
        if custom:
            for d in custom.split(os.pathsep):
                if d.strip():
                    self.roots.append((RANK_CUSTOM, d.strip()))
        self.roots.sort(key=lambda r: r[0])
        self.skills = {}  # name → {description, path, model_invocable, user_invocable, rank}
        self._scan()
        logger.info(
            f"SkillLoader 初始化 | 源={[p for _, p in self.roots]} | "
            f"扫描到 {len(self.skills)} 个技能: {list(self.skills.keys())}"
        )

    def _scan(self):
        """按 rank 扫描全部源；同名低 rank 胜出（高 rank 同名被跳过）。"""
        self.skills = {}
        for rank, root in self.roots:
            if not os.path.isdir(root):
                continue
            for entry in sorted(os.listdir(root)):
                skill_path = None
                dir_path = os.path.join(root, entry)
                if os.path.isdir(dir_path):
                    # 目录包：<name>/SKILL.md
                    candidate = os.path.join(dir_path, "SKILL.md")
                    if os.path.isfile(candidate):
                        skill_path = candidate
                elif entry.endswith(".md"):
                    # 平铺文件：<name>.md
                    skill_path = os.path.join(root, entry)
                if not skill_path:
                    continue
                try:
                    raw = self._read_head(skill_path)
                except OSError as e:
                    logger.warning(f"SkillLoader 读取失败 {skill_path}: {e}")
                    continue
                meta, _body = self._parse_frontmatter(raw)
                name = meta.get("name", "") or (
                    entry[:-3] if entry.endswith(".md") else entry
                )
                description = meta.get("description", "") or ""
                policy = self._parse_invocation_policy(meta, name, skill_path)
                if policy is None:
                    continue  # 策略字段非法 → fail-closed 丢弃整文件
                if name in self.skills:
                    logger.info(f"SkillLoader 跳过低优先级同名技能: {name} @ {skill_path}")
                    continue
                self.skills[name] = {
                    "description": description,
                    "path": skill_path,
                    "model_invocable": policy[0],
                    "user_invocable": policy[1],
                    "rank": rank,
                }
                logger.debug(f"SkillLoader 扫描技能: {name} @ {skill_path}")

    @staticmethod
    def _read_head(path: str, max_bytes: int = 8192) -> str:
        """只读取文件头部（frontmatter 部分），避免扫描时全量读大文件。

        frontmatter 必须位于文件开头（--- 包裹）；8KB 足够覆盖全部技能的
        元数据字段（name/description/whenToUse/调用策略）。正文由
        get_content 在需要时现读全文，扫描阶段不需要。
        尾部可能截断多字节 UTF-8 字符 → errors="replace" 兜底（不影响
        frontmatter 解析，因为分隔符在头部内）。
        """
        with open(path, "rb") as f:
            head = f.read(max_bytes)
        return head.decode("utf-8", errors="replace")

    @staticmethod
    def _parse_frontmatter(raw: str) -> tuple[dict, str]:
        """分离 YAML frontmatter 和 markdown 正文。"""
        if not raw.startswith("---"):
            return {}, raw
        parts = raw.split("---", 2)
        if len(parts) < 3:
            return {}, raw
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2]
        return meta, body

    @staticmethod
    def _parse_invocation_policy(meta: dict, name: str, path: str):
        """解析调用策略 (model_invocable, user_invocable)；非法 → None（丢弃技能）。

        对齐 DSH SkillInvocationPolicy：disable-model-invocation / user-invocable
        布尔字段；值非法时 fail-closed 丢弃整文件并告警，不静默降级。
        """
        for key, val in (
            ("disable-model-invocation", meta.get("disable-model-invocation", False)),
            ("user-invocable", meta.get("user-invocable", True)),
        ):
            if not isinstance(val, bool):
                logger.warning(
                    f"SkillLoader 丢弃技能 {name} @ {path}: 字段 {key} 必须为布尔，"
                    f"实际 {val!r}（fail-closed）"
                )
                return None
        return (not meta.get("disable-model-invocation", False),
                meta.get("user-invocable", True))

    @staticmethod
    def _shorten_description(desc: str, max_len: int = 100) -> str:
        """压缩技能描述用于目录：只保留首行标题。

        desc 原始格式为「标题 + 【概述】 + 【涵盖内容】长列表 + 【适用场景】」，
        完整版可达数百字符。目录只需让模型识别技能主题，
        首行标题已足够（如 'Forge BlockEntity（方块实体）完整指南'）。
        """
        if not desc:
            return ""
        first = next((l.strip() for l in desc.splitlines() if l.strip()), "")
        if len(first) > max_len:
            first = first[:max_len].rstrip() + "…"
        return first

    def catalog_entries(self) -> list:
        """目录条目 [(name, 首行描述)]，按 name 排序，仅模型可调用技能。"""
        entries = []
        for name in sorted(self.skills):
            info = self.skills[name]
            if not info["model_invocable"]:
                continue
            entries.append((name, self._shorten_description(info["description"])))
        return entries

    def get_descriptions(self) -> str:
        """生成技能目录文本（兼容旧调用方；M2 起主要由目录消息替代）。"""
        entries = self.catalog_entries()
        if not entries:
            return ""
        lines = ["Available skills (use load_skill to access):"]
        for name, desc in entries:
            lines.append(f"  - {name}: {desc}")
        result = "\n".join(lines)
        logger.info(f"SkillLoader.get_descriptions 生成技能目录 | {len(result)} 字符")
        return result

    def get_content(self, skill_name: str) -> str:
        """返回完整技能内容（第二层注入，每次现读磁盘），用 XML 标签包裹。

        会话运行中编辑 SKILL.md，下次加载即读到新内容（对齐 DSH body-only
        edits change later tool calls，无缓存协议）。
        调用策略：disable-model-invocation 的技能拒绝模型加载。
        """
        info = self.skills.get(skill_name)
        if info is None:
            available = ", ".join(self.skills.keys())
            logger.info(
                f"SkillLoader.get_content: 技能 '{skill_name}' 未找到 | 可用: {available}"
            )
            return f"Error: Skill '{skill_name}' not found. Available: {available}"
        if not info["model_invocable"]:
            return (f"Error: Skill '{skill_name}' is not invocable by the model "
                    f"(disable-model-invocation). Ask the user to invoke it directly.")
        try:
            with open(info["path"], "r", encoding="utf-8") as f:
                raw = f.read()
            _meta, body = self._parse_frontmatter(raw)
        except OSError as e:
            logger.warning(f"SkillLoader.get_content 读取失败 {info['path']}: {e}")
            return f"Error: Failed to read skill '{skill_name}': {e}"
        content = body.strip()
        result = f'<skill name="{skill_name}">\n{content}\n</skill>'
        logger.info(
            f"SkillLoader.get_content: 加载技能 '{skill_name}'（现读） | {len(content)} 字符"
        )
        return result

    def reload(self) -> None:
        """重新扫描全部源（新增/删除技能文件后调用）。"""
        self._scan()
        logger.info(f"SkillLoader.reload | 扫描到 {len(self.skills)} 个技能")


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
skill_loader = SkillLoader()

def _load_skill_and_record(kw: dict) -> str:
    name = kw.get("skill_name", "")
    out = skill_loader.get_content(name)
    if not out.startswith("Error:"):
        record_load(name)
    return out
