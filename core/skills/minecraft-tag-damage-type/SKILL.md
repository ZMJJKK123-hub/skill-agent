---
name: minecraft-tag-damage-type
description: |
  Java版标签/伤害类型（Minecraft Wiki 中文版全量正文）。
  
  【概述】伤害类型标签（Damage Type Tags）是伤害类型的组合。
  
  【涵盖内容】
  - always_hurts_ender_dragons
  - always_kills_armor_stands
  - always_most_significant_fall
  - always_triggers_silverfish
  - avoids_guardian_thorns
  - burn_from_stepping
  - burns_armor_stands
  - bypasses_armor
  - bypasses_cooldown
  - bypasses_effects
  - bypasses_enchantments
  - bypasses_invulnerability
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/伤害类型 的完整规范时
---

本条目所述内容仅适用于Java版。
伤害类型标签（Damage Type Tags）是伤害类型的组合。

# 使用

伤害类型标签用于将伤害类型分组，例如所有火焰伤害被归类为标签
```
#is_fire
```

。当游戏使用标签测试伤害类型时，只要伤害类型在此标签内即测试成功。

# 标签列表

## always_hurts_ender_dragons

- 持有该标签的伤害类型的伤害总是能对末影龙造成伤害。

- #always_hurts_ender_dragons（1项） - ``` #is_explosion ```

## always_kills_armor_stands

- 持有该标签的伤害类型的伤害总是会完全杀死盔甲架。

- #always_kills_armor_stands（5项） - ``` arrow ``` - ``` trident ``` - ``` fireball ``` - ``` wither_skull ``` - ``` wind_charge ```

## always_most_significant_fall

- 生物死于持有此标签的伤害类型的伤害时，在计算死亡消息时总是会认为生物下落了超过15格。

- #always_most_significant_fall（1项） - ``` out_of_world ```

## always_triggers_silverfish

- 持有该标签的伤害类型的伤害总是触发蠹虫破坏周围虫蚀方块的效果，即使伤害没有来源。

- #always_triggers_silverfish（1项） - ``` magic ```

## avoids_guardian_thorns

- 持有该标签的伤害类型的伤害不触发守卫者或远古守卫者的尖刺效果。

- #avoids_guardian_thorns（3项） - ``` magic ``` - ``` thorns ``` - ``` #is_explosion ```

## burn_from_stepping

- 持有该标签的伤害类型的伤害会被穿着附有冰霜行者靴子的玩家免疫。

- #burn_from_stepping（3项） - ``` campfire ``` - ``` hot_floor ``` - ``` sulfur_cube_hot ```

## burns_armor_stands

- 持有该标签的伤害类型的伤害使盔甲架生命值减少4（[图:♥][图:♥]）。

- #burns_armor_stands（1项） - ``` on_fire ```

## bypasses_armor

- 持有该标签的伤害类型的伤害无视护甲值的伤害减免效果。

- #bypasses_armor（19项） - ``` on_fire ``` - ``` in_wall ``` - ``` cramming ``` - ``` drown ``` - ``` fly_into_wall ``` - ``` generic ``` - ``` wither ``` - ``` dragon_breath ``` - ``` starve ``` - ``` fall ``` - ``` ender_pearl ``` - ``` freeze ``` - ``` stalagmite ``` - ``` magic ``` - ``` indirect_magic ``` - ``` out_of_world ``` - ``` generic_kill ``` - ``` sonic_boom ``` - ``` outside_border ```

## bypasses_cooldown

- 持有该标签的伤害类型的伤害无视受击后伤害免疫。
- 原版游戏未包含此文件。

## bypasses_effects

- 持有该标签的伤害类型的伤害无视抗性提升，魔咒提供的伤害减免效果。

- #bypasses_effects（1项） - ``` starve ```

## bypasses_enchantments

- 持有该标签的伤害类型的伤害无视保护的伤害减免效果。

- #bypasses_enchantments（1项） - ``` sonic_boom ```

## bypasses_invulnerability

- 持有该标签的伤害类型的伤害无视伤害免疫效果，包括持有实体数据 ``` Invulnerable ``` 的生物、处于创造模式或旁观模式的玩家、准备状态的凋灵、正在钻地的监守者的伤害免疫效果。
- 生物死于持有此标签的伤害类型的伤害时，不会触发不死图腾。

- #bypasses_invulnerability（2项） - ``` out_of_world ``` - ``` generic_kill ```

## bypasses_resistance

- 持有该标签的伤害类型的伤害无视一切伤害减免效果和伤害免疫效果。

- #bypasses_resistance（2项） - ``` out_of_world ``` - ``` generic_kill ```

## bypasses_shield

- 持有该标签的伤害类型的伤害无视盾牌的阻挡。

- #bypasses_shield（12项） - ``` #bypasses_armor ``` - ``` cactus ``` - ``` campfire ``` - ``` dry_out ``` - ``` falling_anvil ``` - ``` falling_stalactite ``` - ``` hot_floor ``` - ``` sulfur_cube_hot ``` - ``` in_fire ``` - ``` lava ``` - ``` lightning_bolt ``` - ``` sweet_berry_bush ```

## bypasses_wolf_armor

- 持有该标签的伤害类型的伤害无视狼铠的抵消效果。

- #bypasses_wolf_armor（12项） - ``` #bypasses_invulnerability ``` - ``` cramming ``` - ``` drown ``` - ``` dry_out ``` - ``` freeze ``` - ``` in_wall ``` - ``` indirect_magic ``` - ``` magic ``` - ``` outside_border ``` - ``` starve ``` - ``` thorns ``` - ``` wither ```

## can_break_armor_stand

- 持有该标签的伤害类型能一击破坏盔甲架。

- #can_break_armor_stand（2项） - ``` player_explosion ``` - ``` #is_player_attack ```

## damages_helmet

- 持有该标签的伤害类型的伤害对头盔造成大量耐久度消耗。

- #damages_helmet（3项） - ``` falling_anvil ``` - ``` falling_block ``` - ``` falling_stalactite ```

## ignites_armor_stands

- 持有该标签的伤害类型的伤害设置盔甲架的剩余着火时间为100游戏刻（5秒）。

- #ignites_armor_stands（2项） - ``` in_fire ``` - ``` campfire ```

## is_drowning

- 持有该标签的伤害类型的伤害被游戏规则“溺水伤害”（ ``` drowning_damage ``` ）为 ``` false ``` 时的玩家免疫。

- #is_drowning（1项） - ``` drown ```

## is_explosion

- 持有该标签的伤害类型的伤害受到爆炸保护的伤害减免效果。

- #is_explosion（4项） - ``` fireworks ``` - ``` explosion ``` - ``` player_explosion ``` - ``` bad_respawn_point ```

## is_fall

- 持有该标签的伤害类型的伤害受到摔落缓冲的伤害减免效果。
- 持有该标签的伤害类型的伤害被猫、豹猫、雪傀儡、铁傀儡、岩浆怪、蝙蝠、烈焰人、末影龙、恶魂、鹦鹉、恼鬼、凋灵、鸡、潜影贝、游戏规则“摔落伤害”（ ``` fall_damage ``` ）为 ``` false ``` 时的玩家免疫。

- #is_fall（3项） - ``` fall ``` - ``` ender_pearl ``` - ``` stalagmite ```

## is_fire

- 持有该标签的伤害类型的伤害受到火焰保护的伤害减免效果。
- 持有该标签的伤害类型的伤害被僵尸猪灵、恶魂、凋灵骷髅、烈焰人、炽足兽、岩浆怪、僵尸疣猪兽、监守者、末影龙、凋灵、具有抗火效果的生物、游戏规则“火焰伤害”（ ``` fire_damage ``` ）为 ``` false ``` 时的玩家免疫。

- #is_fire（8项） - ``` in_fire ``` - ``` campfire ``` - ``` on_fire ``` - ``` lava ``` - ``` hot_floor ``` - ``` sulfur_cube_hot ``` - ``` unattributed_fireball ``` - ``` fireball ```

## is_freezing

- 持有该标签的伤害类型的伤害被游戏规则“冰冻伤害”（ ``` freeze_damage ``` ）为 ``` false ``` 时的玩家免疫。

- #is_freezing（1项） - ``` freeze ```

## is_lightning

- 持有该标签的伤害类型的伤害击杀海龟后会掉落碗。

- #is_lightning（1项） - ``` lightning_bolt ```

## is_player_attack

- 由玩家造成的攻击伤害类型。

- #is_player_attack（3项） - ``` player_attack ``` - ``` spear ``` - ``` mace_smash ```

## is_projectile

- 持有该标签的伤害类型的伤害受到弹射物保护的伤害减免效果。

- #is_projectile（8项） - ``` arrow ``` - ``` trident ``` - ``` mob_projectile ``` - ``` unattributed_fireball ``` - ``` fireball ``` - ``` wither_skull ``` - ``` thrown ``` - ``` wind_charge ```

## mace_smash

- 用于相关进度文件。

- #mace_smash（1项） - ``` mace_smash ```

## no_anger

- 持有该标签的伤害类型的伤害不引发受到伤害的实体对造成伤害的实体的反击。

- #no_anger（1项） - ``` mob_attack_no_aggro ```

## no_impact

- 持有该标签的伤害类型的伤害不会使实体受伤后服务端发送数据包以同步位置和速度。

- #no_impact（1项） - ``` drown ```

## no_knockback

- 持有该标签的伤害类型的伤害不造成击退。

- #no_knockback（30项） - ``` explosion ``` - ``` player_explosion ``` - ``` bad_respawn_point ``` - ``` in_fire ``` - ``` lightning_bolt ``` - ``` on_fire ``` - ``` lava ``` - ``` hot_floor ``` - ``` sulfur_cube_hot ``` - ``` in_wall ``` - ``` cramming ``` - ``` drown ``` - ``` starve ``` - ``` cactus ``` - ``` fall ``` - ``` ender_pearl ``` - ``` fly_into_wall ``` - ``` out_of_world ``` - ``` generic ``` - ``` magic ``` - ``` wither ``` - ``` dragon_breath ``` - ``` dry_out ``` - ``` sweet_berry_bush ``` - ``` freeze ``` - ``` stalagmite ``` - ``` outside_border ``` - ``` generic_kill ``` - ``` campfire ``` - ``` spear ```

## no_wolf_retaliation

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 驯服狼的主人受到持有此标签的伤害类型后，狼不会尝试对伤害来源进行反击。

- #no_wolf_retaliation（1项） - ``` sulfur_cube_hot ```

## panic_causes

- 持有该标签的伤害类型会使被动型动物惊慌（尝试逃走）。

- #panic_causes（20项） - ``` #panic_environmental_causes ``` - ``` arrow ``` - ``` dragon_breath ``` - ``` explosion ``` - ``` fireball ``` - ``` fireworks ``` - ``` indirect_magic ``` - ``` magic ``` - ``` mob_attack ``` - ``` mob_projectile ``` - ``` player_explosion ``` - ``` sonic_boom ``` - ``` sting ``` - ``` thrown ``` - ``` trident ``` - ``` unattributed_fireball ``` - ``` wind_charge ``` - ``` wither ``` - ``` wither_skull ``` - ``` #is_player_attack ```

## panic_environmental_causes

- 持有该标签的伤害类型会使条件敌对动物惊慌（进行反击）。

- #panic_environmental_causes（8项） - ``` cactus ``` - ``` freeze ``` - ``` hot_floor ``` - ``` sulfur_cube_hot ``` - ``` in_fire ``` - ``` lava ``` - ``` lightning_bolt ``` - ``` on_fire ```

## sulfur_cube_with_block_immune_to

- 持有该标签的伤害类型的伤害被吸收方块的硫方怪免疫。

- #sulfur_cube_with_block_immune_to（24项） - ``` arrow ``` - ``` cactus ``` - ``` dry_out ``` - ``` fall ``` - ``` falling_anvil ``` - ``` falling_block ``` - ``` falling_stalactite ``` - ``` freeze ``` - ``` mace_smash ``` - ``` hot_floor ``` - ``` mob_attack ``` - ``` mob_attack_no_aggro ``` - ``` mob_projectile ``` - ``` player_attack ``` - ``` spear ``` - ``` spit ``` - ``` stalagmite ``` - ``` sting ``` - ``` sulfur_cube_hot ``` - ``` sweet_berry_bush ``` - ``` thrown ``` - ``` trident ``` - ``` wind_charge ``` - ``` #is_explosion ```

## witch_resistant_to

- 持有该标签的伤害类型的伤害受到女巫的85%伤害减免效果影响。

- #witch_resistant_to（4项） - ``` magic ``` - ``` indirect_magic ``` - ``` sonic_boom ``` - ``` thorns ```

## wither_immune_to

- 持有该标签的伤害类型的伤害被凋灵免疫。

- #wither_immune_to（1项） - ``` drown ```

# 已移除的标签

## breeze_immune_to

添加于：23w45a。移除于：24w21a。

- #breeze_immune_to（2项） - ``` arrow ``` - ``` trident ```

# 历史

# 导航
