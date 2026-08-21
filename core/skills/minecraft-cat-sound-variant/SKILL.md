---

name: minecraft-cat-sound-variant
description: "Minecraft Cat Sound Variant 猫声音变体定义：CAT_SOUND_VARIANT 注册表、data/<namespace>/cat_sound_variant/ 数据包路径、JSON 格式（adult_sounds 成年猫声音、baby_sounds 幼猫声音）、Adult Sounds 成年猫声音事件（ambient_sound 空闲、beg_for_food_sound 乞食、death_sound 死亡、eat_sound 进食、hiss_sound 对幻翼嘶叫、hurt_sound 受伤、purr_sound 呼噜、purreow_sound 驯服空闲、stray_ambient_sound 流浪空闲）、Baby Sounds 幼猫声音事件（同上格式）、Sound Types 声音类型（Immediate 即时：hurt/death/eat；Random 随机：hiss/beg_for_food/purr/purreow/stray_ambient/ambient）、服务器启动加载（/reload 不重新加载）、CAT_SOUND_VARIANT 注册表至少一个元素、声音变体独立于猫变体。"
whenToUse: "Use when writing datapack cat_sound_variant definitions or custom cat sounds."

---

# Cat Sound Variants

This content applies only to Java Edition.

Cat sound variant definition files are the data-driven definitions of cat sound variants in datapacks.

## Definition format

Cat sound variants use the `CAT_SOUND_VARIANT` registry; the datapack path is `cat_sound_variant` (definitions in `data/<namespace>/cat_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult cats. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `beg_for_food_sound` (begging), `death_sound`, `eat_sound`, `hiss_sound` (hissing at phantoms), `hurt_sound`, `purr_sound` (purring), `purreow_sound` (tamed idle), `stray_ambient_sound` (untamed idle).
  - `baby_sounds` (compound, required): same format, for baby cats.

## Definition behavior

Cat sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CAT_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Cat sound variants are independent of cat variants; each spawned cat randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `eat_sound`. Random sounds: `hiss_sound` (hissing at phantoms), `beg_for_food_sound`, `purr_sound`, `purreow_sound` (idle when tamed), `stray_ambient_sound` (untamed), `ambient_sound` (idle, alternating randomly with `purreow_sound`).
