---

name: minecraft-zombie-nautilus
description: "Minecraft Zombie Nautilus 僵尸鹦鹉螺：Spawning 生成（Java 溺尸生成时50%概率骑乘僵尸鹦鹉螺 自然生成唯一方式、Bedrock 海洋生物群系稀有生成2-4额外溺尸 一个成年骑僵尸鹦鹉螺 温暖海洋珊瑚变体）、Drops 掉落（1-3 XP 装备鞍和鹦鹉螺盔甲 Bedrock）、Behavior 行为（有鞍漫游16方块 无鞍32方块、免疫中毒、友好但计入怪物生物上限、Bedrock 溺尸骑乘附近未驯服 铁傀儡/雪傀儡攻击 兔子逃跑）、Attacks 攻击（未驯服攻击伤害者 后退然后冲刺 伤害+强击退 ~20秒后自动结束、偶尔攻击河豚、持鱼或鱼桶停止攻击敌对玩家、驯服后永不敌对、陆地不能攻击）、Dehydration 脱水（完全离开水不能自主移动 仍可骑乘/控制 不受脱水伤害）、Taming 驯服（喂河豚或河豚桶 1/3概率 桶→水桶 驯服死亡显示死亡消息）、Equipment 装备（两个物品槽：鹦鹉螺盔甲 僵尸鹦鹉螺专用 和鞍 可剪刀移除 先盔甲）、Riding 骑乘（方向+跳跃键控制 下马像马 骑乘时使用物品/交互 无缓慢下沉 水速7.15m/s 快10% 速度条=冲刺充能条 跳跃键充能 释放冲刺 最大充能10刻26.40m/s ~11方块 冲刺后55刻冷却 骑乘时显示鹦鹉螺生命条 骑乘获得鹦鹉螺呼吸效果冻结氧气条 Java每40刻60刻 Bedrock持续40刻效果 仅鞍时）、Feeding 喂养（任何鱼或鱼桶治愈受伤驯服成年 桶→水桶 Java满血驯服成年进入爱心模式 不能繁殖）、Creature Family 生物家族（Undead 亡灵：额外伤害 灵魂伤害 治疗伤害 生命恢复免疫 中毒免疫 无溺水 无脱水 不被凋灵攻击、Unlike most undead they can swim 与大多数亡灵不同可游泳、Burn in sunlight 除非穿鹦鹉螺盔甲 日光燃烧、Aquatic 水生 Java：额外穿刺伤害）、Data Values 数据（variant 无效/缺失→temperate）。"
whenToUse: "Use when working with zombie nautiluses (taming, riding, nautilus armor)."

---

# Zombie Nautilus

Zombie nautiluses are friendly mobs spawning with drowned — the undead variant of nautiluses.

## Spawning

Java: when a drowned spawns naturally or via structures (ocean ruins) in a non-river/frozen-river biome, is not a baby, and holds a trident in the main hand, there is a 50% chance a zombie nautilus spawns as its mount. That's the only natural spawning. Bedrock: ocean biomes rarely spawn 2–4 extra drowned, one adult riding a zombie nautilus. In warm oceans the coral zombie nautilus variant replaces it (Java: `/summon zombie_nautilus ~ ~ ~ {variant:warm}`).

## Drops

1–3 XP (player/tamed-wolf kill), the equipped saddle and nautilus armor (Bedrock).

## Behavior

Saddled zombie nautiluses wander within 16 blocks, unsaddled within 32. Immune to poison. Friendly but counts toward the monster mob cap. Bedrock: drowned mount nearby untamed ones; iron golems/snow golems attack them; rabbits flee them.

### Attacks

Untamed zombie nautiluses attack anything that hurt them: back off, then dash, dealing damage + strong knockback (hitting others along the way), hostility auto-ending after ~20 s. They occasionally attack nearby pufferfish. Holding fish or fish buckets stops them attacking a hostile player. Tamed ones never become hostile. They cannot attack on land.

### Dehydration

Fully out of water they can't move on their own (still rideable/controllable); unlike nautiluses they take no dehydration damage.

### Taming

Feed pufferfish or pufferfish buckets (1/3 chance per feed; bucket → water bucket). Tamed zombie nautilus deaths show a death message.

### Equipment

Two inventory slots: **nautilus armor** (zombie-nautilus-only armor) and **saddle**. Both removable with shears (armor first).

### Riding

With a saddle: direction + jump keys control it; dismount like a horse; use items/interact while riding; no slow sinking. Water speed 7.15 m/s (10% faster than nautilus, faster than Depth Strider III sprint-swimming). The XP bar becomes the **dash charge bar**: hold jump to charge; release to dash. Max charge at 10 ticks (0.5 s; bar reaches the orange zone) → 26.40 m/s for ~11 blocks; charging longer shrinks the bar and weakens the dash. Speed affected by Speed/Slowness. After dashing: 55-tick (2.75 s) cooldown. A nautilus-style health bar shows while riding. Riding grants the **Nautilus' Breath** effect freezing the oxygen bar (Java: every 40 ticks for 60 ticks; Bedrock: constant 40-tick effect, saddled only). Control on land is possible but much slower.

### Feeding

Feed any fish or fish bucket to heal a damaged tamed adult (bucket → water bucket). Java: full-health tamed adults enter love mode (but they can't breed).

## Creature Family

**Undead**: extra damage from Smite melee, healed by Instant Damage, hurt by Instant Health, immune to Regeneration and Poison, no drowning, no dehydration, not attacked by Withers. Unlike most undead they can swim (don't sink). Burn in sunlight unless wearing nautilus armor. **Aquatic** (Java): extra damage from Impaling melee attacks and Impaling trident projectiles.

## Data Values

- ID: `minecraft:zombie_nautilus`.
- NBT: entity/living/mob/animal/tameable common tags plus `variant` (invalid/absent → `temperate`).

## Trivia

The design was inspired by French escargot (per Sarah Boeving).
