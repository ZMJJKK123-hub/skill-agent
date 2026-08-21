---

name: minecraft-chicken-sound-variant
description: "Minecraft Chicken Sound Variant 鸡声音变体定义：CHICKEN_SOUND_VARIANT 注册表、data/<namespace>/chicken_sound_variant/ 数据包路径、JSON 格式（adult_sounds 成年鸡声音、baby_sounds 幼鸡声音）、Adult Sounds 成年鸡声音事件（ambient_sound 空闲、death_sound 死亡、hurt_sound 受伤、step_sound 脚步）、Baby Sounds 幼鸡声音事件（同上格式）、Sound Types 声音类型（Immediate 即时：hurt/death/step；Random 随机：ambient）、服务器启动加载（/reload 不重新加载）、CHICKEN_SOUND_VARIANT 注册表至少一个元素、声音变体独立于鸡变体。"
whenToUse: "Use when writing datapack chicken_sound_variant definitions or custom chicken sounds."

---

# Chicken Sound Variants

This content applies only to Java Edition.

Chicken sound variant definition files are the data-driven definitions of chicken sound variants in datapacks.

## Definition format

Chicken sound variants use the `CHICKEN_SOUND_VARIANT` registry; the datapack path is `chicken_sound_variant` (definitions in `data/<namespace>/chicken_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult chickens. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `death_sound`, `hurt_sound`, `step_sound`.
  - `baby_sounds` (compound, required): same format, for baby chickens.

## Definition behavior

Chicken sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CHICKEN_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Chicken sound variants are independent of chicken variants; each spawned chicken randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `step_sound`. Random sounds: `ambient_sound` (idle).
