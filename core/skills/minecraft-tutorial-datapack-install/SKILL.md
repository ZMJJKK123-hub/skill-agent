---

name: minecraft-tutorial-datapack-install
description: "Tutorial — installing data packs: at world creation, into existing worlds, on servers."
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
