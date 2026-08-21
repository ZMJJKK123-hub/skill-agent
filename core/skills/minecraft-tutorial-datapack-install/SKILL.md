---

name: minecraft-tutorial-datapack-install
description: "Minecraft Tutorial: Installing Data Packs 安装数据包教程：Getting a Data Pack 获取数据包（下载或创建、识别包 文件夹或zip 第一级有pack.mcmeta 可选pack.png+data/<namespace>/...、游戏不识别可能多余目录层）、Single-Player 单人游戏（At World Creation 创建世界时：创建新世界→更多→数据包 拖入文件/打开包文件夹添加 箭头重排优先级、Incompatible警告不一定破坏加载；Into an Existing World 现有世界：不推荐维度/世界生成包、选择世界→编辑→打开世界文件夹→datapacks/ 放入包 重新进入世界 /datapack list enabled 检查 成功加载仅表示pack.mcmeta被读取）、Multiplayer 多人游戏（服务器文件夹 world/datapacks/ 放入包 下次服务器启动加载、运行服务器 /reload 控制台或≥3权限级别 /datapack list enabled 控制台或≥2）。"
whenToUse: "Use when installing data packs in single-player or multiplayer."

---

# Tutorial: Installing Data Packs

Java Edition only.

## Getting a Data Pack

Download one or make your own. A recognized pack (folder or zip) has `pack.mcmeta` at its first level (the only required file), plus optional `pack.png` (icon) and `data/<namespace>/...`. If the game doesn't recognize it, the pack is probably wrapped in an extra directory layer.

## Single-Player

### At World Creation

1. "Create New World" → "More" → "Data Packs".
2. Drag the pack file into the window ("Yes"); or use "Open Pack Folder" to add/remove several. Arrows reorder selection/priority; arrows on selected packs unselect them.
3. If the pack doesn't appear, check the file layer and `pack.mcmeta` validity. "Incompatible" warnings don't necessarily break the pack — actual loading depends on content/structure vs the current version.
4. "Done".

Troubleshooting: "unable to verify" usually means missing key content (often tags) — keep the vanilla pack loaded or ensure the pack includes the required content; don't remove the vanilla pack to strip vanilla advancements/recipes (use dedicated packs). World-creation errors often come from custom-dimension/worldgen packs — remove and report to the author; check mods in modded environments.

### Into an Existing World

Not recommended for dimension/worldgen packs (they may not work). Steps: select the world → "Edit" → "Open World Folder" → open `datapacks/` → drop the pack in. Re-enter the world. Verify with `/datapack list enabled` (cheats on; listed in priority order). Note: successful loading only means pack.mcmeta was read, not that all registrations loaded.

## Multiplayer

1. Open the server folder → `world/` → `datapacks/`, drop the pack in.
2. It loads at the next server start (highest priority).
3. On a running server: `/reload` (console or ≥3 permission level); confirm with `/datapack list enabled` (console or ≥2).
