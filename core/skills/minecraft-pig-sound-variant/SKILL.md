---

name: minecraft-pig-sound-variant
description: "Minecraft Pig Sound Variant 猪声音变体定义：PIG_SOUND_VARIANT 注册表、data/<namespace>/pig_sound_variant/ 数据包路径、JSON 格式（adult_sounds 成年猪声音、baby_sounds 幼猪声音）、Adult Sounds 成年猪声音事件（ambient_sound 空闲、death_sound 死亡、hurt_sound 受伤、step_sound 脚步、eat_sound 进食）、Baby Sounds 幼猪声音事件（同上格式）、Sound Types 声音类型（Immediate 即时：hurt/death/step/eat；Random 随机：ambient）、服务器启动加载（/reload 不重新加载）、PIG_SOUND_VARIANT 注册表至少一个元素、声音变体独立于猪变体。"
whenToUse: "Use when writing datapack pig_sound_variant definitions or custom pig sounds."

---

# Pig Sound Variants

This content applies only to Java Edition.

Pig sound variant definition files are the data-driven definitions of pig sound variants in datapacks.

## Definition format

Pig sound variants use the `PIG_SOUND_VARIANT` registry; the datapack path is `pig_sound_variant` (definitions in `data/<namespace>/pig_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult pigs.
    - `ambient_sound` (string/compound): idle sound event (registry name or inline; same format for all below).
    - `death_sound` (string/compound): death sound event.
    - `hurt_sound` (string/compound): hurt sound event.
    - `step_sound` (string/compound): step sound event.
    - `eat_sound` (string/compound): eating sound event.
  - `baby_sounds` (compound, required): sounds used by baby pigs; same format as `adult_sounds`.

## Definition behavior

Pig sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `PIG_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Pig sound variants are independent of pig variants; each spawned pig randomly picks one registered sound variant. Immediate sounds: `hurt_sound` (hurt), `death_sound` (death), `step_sound` (walking), `eat_sound` (eating). Random sounds: `ambient_sound` (idle).
