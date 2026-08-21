---

name: minecraft-cow-sound-variant
description: "Minecraft Cow Sound Variant 牛声音变体定义：COW_SOUND_VARIANT 注册表、data/<namespace>/cow_sound_variant/ 数据包路径、JSON 格式（adult_sounds 成年牛声音、baby_sounds 幼牛声音）、Adult Sounds 成年牛声音事件（ambient_sound 空闲、death_sound 死亡、hurt_sound 受伤、step_sound 脚步）、Baby Sounds 幼牛声音事件（同上格式）、Sound Types 声音类型（Immediate 即时：hurt/death/step；Random 随机：ambient）、服务器启动加载（/reload 不重新加载）、COW_SOUND_VARIANT 注册表至少一个元素、声音变体独立于牛变体。"
whenToUse: "Use when writing datapack cow_sound_variant definitions or custom cow sounds."

---

# Cow Sound Variants

This content applies only to Java Edition.

Cow sound variant definition files are the data-driven definitions of cow sound variants in datapacks.

## Definition format

Cow sound variants use the `COW_SOUND_VARIANT` registry; the datapack path is `cow_sound_variant` (definitions in `data/<namespace>/cow_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult cows. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `death_sound`, `hurt_sound`, `step_sound`.
  - `baby_sounds` (compound, required): same format, for baby cows.

## Definition behavior

Cow sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `COW_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Cow sound variants are independent of cow variants; each spawned cow randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `step_sound`. Random sounds: `ambient_sound` (idle).
