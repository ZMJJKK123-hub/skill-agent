---

name: minecraft-registry
description: "Registry mechanism: built-in vs writable, ID keys, tags, datapack paths."
whenToUse: "Use when understanding how datapack registries (enchantment, jukebox_song, tags, etc.) work."

---

# Registries

This content applies only to Java Edition.

Registries are a widely used game mechanism organizing values of the same type.

## Categories

- **Built-in registries**: hardcoded; contents cannot be modified; shared across worlds.
- **Writable registries**: loaded from datapacks; world-bound and data-dependent.
- **Network-synchronized registries**: writable registries synced to clients via the `registry_data` packet during configuration.

## Indexing

- Namespace IDs map to values (e.g. `grass_block` in the `BLOCK` registry).
- Numeric IDs are used only on the network to shorten data.
- Tags map to multiple values (e.g. `#air` = `air` + `cave_air` + `void_air`); tags are never hardcoded and can be defined by datapacks for any registry. Synced registries (all built-in + network-synchronized writable ones) sync tags via the `update_tags` packet.

## Structure

Every writable registry has a deserializer (e.g. `ENCHANTMENT` ↔ enchantment format) and a datapack path P: files `data/<N>/<P>/<I>.json` register value `N:I`. Example: `data/minecraft/jukebox_song/5.json` registers `minecraft:5`. Tags: files `data/<N>/tags/<P>/<I>.json` (including subdirectories) create tag `#N:I`, e.g. `data/minecraft/tags/block/mineable/axe.json` → `#minecraft:mineable/axe`.

Registries themselves are registered in a special registry; they cannot be added or removed.
