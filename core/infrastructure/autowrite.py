# -*- coding: utf-8 -*-
"""写前预算兜底：starter 自动复制与最小骨架生成（infrastructure 层）。

背景（旧 agent.py 实测 bug 驱动）：新 modid 任务没有可匹配 starter
时，写前软提醒会无限循环——二振直接写最小可编译主类骨架，把
agent 推进到写/改/编译阶段（c43424752e7d）。
"""
from __future__ import annotations

import glob
import re
from pathlib import Path
from typing import Optional

from ..domain.messages import Message, UserMessage
from .logging_.logger import get_logger

logger = get_logger("autowrite")


def has_custom_java() -> bool:
    """输入：无。返回：cwd 下是否存在非模板自写 Java（模板 com/example 不算）。"""
    def is_template(p: Path) -> bool:
        parts = [x.lower() for x in p.parts]
        return "com" in parts and "example" in parts and "examplemod" in parts
    for root in (Path.cwd() / "src" / "main" / "java",
                 Path.cwd() / "src" / "test" / "java"):
        if not root.exists():
            continue
        for p in root.rglob("*.java"):
            if not is_template(p):
                return True
    return False


def infer_modid(messages: list[Message]) -> Optional[str]:
    """输入：消息列表。返回：推断的 modid（显式 modid= 优先，括号英文名兜底）。"""
    for m in messages:
        if not isinstance(m, UserMessage):
            continue
        hit = re.search(r"modid[ =:]+([a-z0-9_\-]{2,32})", m.content, re.I)
        if hit:
            return hit.group(1).lower()
    for m in messages:
        if not isinstance(m, UserMessage):
            continue
        hit = re.search(r"[（(]([A-Za-z][A-Za-z0-9 ]{2,31})[）)]", m.content)
        if hit:
            modid = re.sub(r"[^a-z0-9_]", "", hit.group(1).lower())
            if 3 <= len(modid) <= 32:
                return modid
    return None


def write_starter(messages: list[Message]) -> bool:
    """按 modid + 任务关键词自动复制最匹配的 starter Java 文件。

    Args:
        messages: 消息列表（只读 user 消息推断 modid/关键词）。
    Returns:
        是否写入了文件（modid 无匹配 starter 时 False）。
    """
    modid = None
    for m in messages:
        if isinstance(m, UserMessage):
            hit = re.search(r"modid[ =:]+([a-zA-Z0-9_\-]+)", m.content)
            if hit:
                modid = hit.group(1).lower()
                break
    if not modid:
        return False
    candidates = glob.glob(str(Path.cwd() / "starter" / "**" / "*.java"),
                           recursive=True)
    task_text = "\n".join(m.content.lower() for m in messages
                          if isinstance(m, UserMessage))
    best = _score_starter(candidates, modid, task_text)
    if best is None:
        return False
    path, content = best
    pkg = re.search(r"package\s+([\w\.]+)\s*;", content)
    if not pkg:
        return False
    dest = (Path.cwd() / "src" / "main" / "java"
            / pkg.group(1).replace(".", "/") / Path(path).name)
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(content, encoding="utf-8")
            logger.warning("auto-wrote starter Java file: %s", dest)
            return True
    except OSError as e:
        logger.warning("starter 写入失败: %s", e)
    return False


def _score_starter(candidates: list[str], modid: str,
                   task_text: str) -> Optional[tuple[str, str]]:
    """输入：候选文件 + modid + 任务文本。返回：(最佳文件, 内容) 或 None。"""
    block_kw = ("block", "方块")
    item_kw = ("item", "food", "apple", "ingot", "gem", "物品", "食物")
    tool_kw = ("tool", "sword", "pickaxe", "axe", "工具", "剑", "镐")
    game_kw = ("game", "minigame", "swap", "大逃杀", "游戏", "交换", "玩家")
    best_score, best = 0, None
    for path in candidates:
        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError:
            continue
        low_path = path.lower().replace("\\", "/")
        pkg = re.search(r"package\s+([\w\.]+)\s*;", content)
        # modid 必须出现在包名或路径里，否则视为无关 starter（coppertools 误配教训）
        if not ((pkg and modid in pkg.group(1).lower()) or modid in low_path):
            continue
        score = 1
        if any(k in task_text for k in block_kw) and "/block/" in low_path:
            score += 6
        if any(k in task_text for k in tool_kw) and ("/tools/" in low_path or "tool" in low_path):
            score += 7
        if any(k in task_text for k in item_kw) and ("/item/" in low_path or "rubymod" in low_path):
            score += 5
        if any(k in task_text for k in game_kw) and ("/swapgame/" in low_path or "swapgame" in low_path):
            score += 9
        if score > best_score and score >= 2:
            best_score, best = score, (path, content)
    return best


def write_skeleton(messages: list[Message]) -> Optional[str]:
    """写入最小可编译主类骨架（1.21.11 注册写法硬事实内嵌）。

    Args:
        messages: 消息列表（推断 modid）。
    Returns:
        写入的 modid；无法推断或已存在自写 Java 时 None。
    """
    modid = infer_modid(messages)
    if not modid:
        return None
    cls = modid.title().replace("_", "").replace("-", "") + "Mod"
    dest = Path.cwd() / "src" / "main" / "java" / "com" / modid / f"{cls}.java"
    if has_custom_java():
        return None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(_skeleton_source(modid, cls), encoding="utf-8")
        logger.warning("auto-wrote minimal mod skeleton: %s (modid=%s)", dest, modid)
        return modid
    except OSError as e:
        logger.warning("auto_write_skeleton 失败: %s", e)
        return None


def _skeleton_source(modid: str, cls: str) -> str:
    """输入：modid + 类名。返回：最小主类 Java 源码文本。"""
    return (
        f"package com.{modid};\n\n"
        f"import net.minecraftforge.fml.common.Mod;\n"
        f"import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;\n"
        f"import net.minecraftforge.registries.DeferredRegister;\n"
        f"import net.minecraftforge.registries.ForgeRegistries;\n\n"
        f"@Mod({cls}.MODID)\n"
        f"public class {cls} {{\n"
        f"    public static final String MODID = \"{modid}\";\n\n"
        f"    // 可在此扩展各注册表（物品/方块/BlockEntity 等），需要再加\n"
        f"    public static final DeferredRegister<net.minecraft.world.item.Item> ITEMS =\n"
        f"            DeferredRegister.create(ForgeRegistries.ITEMS, MODID);\n\n"
        f"    public {cls}() {{\n"
        f"        // 1.21.11 硬事实：注册挂 getModBusGroup()，不要写 IEventBus/getModEventBus\n"
        f"        ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());\n"
        f"    }}\n"
        f"}}\n"
    )
