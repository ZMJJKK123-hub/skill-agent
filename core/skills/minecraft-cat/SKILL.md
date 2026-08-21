---

name: minecraft-cat
description: "Minecraft Cat 猫：Spawning 生成（沼泽小屋黑猫生成、村庄猫生成 60秒/随机玩家/8-31方块/5 beds/48方块/10-11外观、基岩版村庄猫配额 1:4村民/17x13x17区域）、Sound Variants 声音变体（Classic 和 Royal 各50%）、Drops 掉落（1-3 XP 成年猫）、Behavior 行为（免疫摔落伤害、看穿隐身玩家、对幻翼嘶叫、苦力怕保持6方块距离、幻翼16方块、水中漂浮）、Stray Cats 流浪猫（野生物群系消失规则、15方块内猎杀兔子和幼龟、16方块内避免玩家、快速移动逃跑、生鱼/生鲑鱼乞讨）、Breeding 繁殖（生鱼喂养、爱心模式、1只幼崽、1-7 XP、5分钟冷却、幼崽继承父母毛色、项圈颜色混合、金蒲公英控制生长）、Healing 治疗（主人生鱼2HP）、Appearance 外观（22种皮肤 11种年龄、黑色/英国短毛/三花/Jellie/波斯/布偶/红色虎斑/暹罗/虎斑/燕尾服/白色、可染色项圈）、Taming 驯服（生鱼1/3概率、平均3条鱼、坐下/站立交互、喜欢坐在箱子/床/熔炉上）、Teleporting 传送（12方块外传送、各种不传送情况）、Gifts 礼物（70%概率晨礼 gamepplay/cat_morning_gift 战利品表）、NBT 数据（CollarColor/sound_variant/variant）。"
whenToUse: "Use when working with cats (taming, breeding, variants, gifts)."

---

# Cat

Cats are tameable friendly mobs (untameable ocelots are separate). "cat" also names a music disc.

## Spawning

- A witch and an untamed **black cat** always generate at swamp huts (in front of the red mushroom pot) and never despawn. Java: spawn eggs/unspecified `/summon` inside the hut's 7×7×9 area also yield black cats.
- **Villages (Java)**: every 60 seconds per dimension, a random non-dead player (incl. spectator) is picked; a position 8–31 blocks off (X/Z) from them is chosen. If valid, with ≥5 claimed beds within 48 blocks and <5 cats within 48×48×8 (Chebyshev), a random-look cat spawns (10 looks off full moon, all 11 during full moon).
- **Swamp hut (Java)**: if the spot is valid but fails village conditions and lies in a swamp hut, a black cat spawns.
- **Bedrock**: villages spawn untamed cats to meet a quota of 1 per 4 villagers (max 5; all cats in the village count); spawn area matches iron golems (17×13×17 around the village center). 25% spawn as babies; 50% black during full moon.

### Sound Variants

2 sound variants: **Classic** and **Royal**, assigned independently (50% each); used for idle, death, and hurt sounds.

## Drops

1–3 XP when killed by a player or tamed wolf (adults only; babies drop nothing).

## Behavior

- Immune to fall damage (still avoids big falls). Sees invisible players. Babies are just faster.
- Java: hisses at Phantoms pursuing the player. Creepers keep 6 blocks away (not if already primed and the player is out of blast range); Phantoms keep 16 blocks away.
- Cats float in water; babies may drown before being rescued.

### Stray Cats (untamed)

Strays despawn like other wild mobs (only after >120 s when too far). They hunt rabbits and baby turtles within 15 blocks (sneaking approach first; Bedrock: see through blocks). They wander, avoid non-creative/spectator players within 16 blocks, and flee faster (1.33×) when the player moves significantly (≥0.1 blocks/tick, not sneaking) or shakes the camera (≥5°/tick). They slowly approach players holding raw cod/salmon within 6 blocks and beg; any fast movement, camera shake, or item change breaks it.

### Breeding

Feed two full-health tamed adults raw cod/salmon → love mode (at least one standing) → 1 baby (1–7 XP; 5-min/1-min cooldown; full-health parents can't be fed again). Baby takes a random parent's coat; collar = valid mix of parents' colors (else random parent's); owner per the same rules as wolves (same owner; different owners → the later-loaded cat's owner unless one was ordered to sit → the other's). Feed babies raw cod/salmon to grow ~10% faster per fish. Golden dandelions halt/restart baby growth (halted babies accept only golden dandelions).

### Healing

Only the owner's raw cod/salmon heals a tamed cat (2 HP). Cat tails do not reflect health.

## Appearance

22 skins (11 per age): black (all-black, orange eyes), British shorthair (light gray, black eyes), calico (orange/white/black, heterochromia), Jellie (gray/white, gray-green — community-voted from GoodTimesWithScar's cat), Persian (tan, blue eyes, distinct face), Ragdoll (white/soft amber, blue eyes), red tabby (orange/white, green), Siamese (light brown/white, blue), tabby (brown/white, yellow), tuxedo (black/white, green), white (all-white, light blue/yellow eyes). Tamed cats have a dyeable collar.

## Taming

Feed strays raw cod/salmon (1/3 chance per feed, average 3 fish). Unlike wolves, stray cats can be tamed even mid-fight. Tamed cats don't despawn, follow their owner, and purr/meow. Interacting (without fish/lead) makes them sit/stand. They love sitting on chests, bed halves, and lit furnaces (the 8 candidate offsets around them, requiring air above); sitting on a chest locks it. Cats sleep on empty beds (Java). Java: after hostile damage, standing tamed cats can't be ordered to sit for a while.

### Teleporting

Tamed cats teleport when >12 blocks from the owner (possible bad teleports: suffocation/drowning). No teleport when: ordered to sit (exception: sitting cats attacked may teleport, e.g. lightning-struck); attempting to sit on chest/bed/furnace; sleeping on a bed; in a minecart/boat; leashed; chunk unloaded; no valid 5×5×1 rim spot; owner in another dimension; owner in water (teleports right after). Silent.

### Gifts

A tamed, standing cat walks onto the owner's bed while the owner sleeps (one cat only). 70% chance to give a morning gift after a **night** sleep (not daytime thunderstorms); loot from `gameplay/cat_morning_gift` loot table.

## Data Values

- ID: `minecraft:cat`.
- NBT: entity/living/mob/breedable/animal/tameable common tags plus:
  - `CollarColor` (0–15, default 14 red; strays have it but don't render; out of range → 0 white; → component `cat/collar`).
  - `sound_variant` (namespace ID; invalid → `classic`; → component `cat/sound_variant`).
  - `variant` (namespace ID; invalid → `black`; → component `cat/variant`).

## Trivia

- Pre-1.14/1.10.0, cats came from taming ocelots. Tuxedo is based on Jeb's cat Newton; white on the Khao Manee; black on Bombay cats. Calico cats are almost always female in real life. Jellie's cat died Jan 5, 2024. Cat sounds were recorded from Samuel Åberg's pet Odi.
