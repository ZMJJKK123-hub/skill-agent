---
name: minecraft-tag-enchantment
description: |
  Java版标签/魔咒（Minecraft Wiki 中文版全量正文）。
  
  【概述】魔咒标签（Enchantment Tags）是魔咒的组合。
  
  【涵盖内容】
  - curse
  - double_trade_price
  - exclusive_set/armor
  - exclusive_set/boots
  - exclusive_set/bow
  - exclusive_set/crossbow
  - exclusive_set/damage
  - exclusive_set/mining
  - exclusive_set/riptide
  - in_enchanting_table
  - non_treasure
  - on_mob_spawn_equipment
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/魔咒 的完整规范时
---

本条目所述内容仅适用于Java版。
魔咒标签（Enchantment Tags）是魔咒的组合。

# 使用

魔咒标签用于控制魔咒的出现条件和一些基本功能。

# 标签列表

## curse

- 在提示框中以红色文本显示且不可被祛魔的魔咒。

- #curse（2项） - ``` binding_curse ``` （绑定诅咒） - ``` vanishing_curse ``` （消失诅咒）

## double_trade_price

- 需要花费双倍绿宝石交易的魔咒。

- #double_trade_price（1项） - ``` #treasure ```

## exclusive_set/armor

- 不能在盔甲上共存的魔咒。

- #exclusive_set/armor（4项） - ``` protection ``` （保护） - ``` blast_protection ``` （爆炸保护） - ``` fire_protection ``` （火焰保护） - ``` projectile_protection ``` （弹射物保护）

## exclusive_set/boots

- 不能在靴子上共存的魔咒。

- #exclusive_set/boots（2项） - ``` frost_walker ``` （冰霜行者） - ``` depth_strider ``` （深海探索者）

## exclusive_set/bow

- 不能在弓上共存的魔咒。

- #exclusive_set/bow（2项） - ``` infinity ``` （无限） - ``` mending ``` （经验修补）

## exclusive_set/crossbow

- 不能在弩上共存的魔咒。

- #exclusive_set/crossbow（2项） - ``` multishot ``` （多重射击） - ``` piercing ``` （穿透）

## exclusive_set/damage

- 不能共存的伤害增幅类魔咒。

- #exclusive_set/damage（6项） - ``` sharpness ``` （锋利） - ``` smite ``` （亡灵杀手） - ``` bane_of_arthropods ``` （节肢杀手） - ``` impaling ``` （穿刺） - ``` density ``` （致密） - ``` breach ``` （破甲）

## exclusive_set/mining

- 不能共存的挖掘类魔咒。

- #exclusive_set/mining（2项） - ``` fortune ``` （时运） - ``` silk_touch ``` （精准采集）

## exclusive_set/riptide

- 不能与激流共存的魔咒。

- #exclusive_set/riptide（2项） - ``` loyalty ``` （忠诚） - ``` channeling ``` （引雷）

## in_enchanting_table

- 会出现在附魔台里的魔咒。

- #in_enchanting_table（1项） - ``` #non_treasure ```

## non_treasure

- 非宝藏类魔咒。

- #non_treasure（36项） - ``` protection ``` （保护） - ``` fire_protection ``` （火焰保护） - ``` feather_falling ``` （摔落缓冲） - ``` blast_protection ``` （爆炸保护） - ``` projectile_protection ``` （弹射物保护） - ``` respiration ``` （水下呼吸） - ``` aqua_affinity ``` （水下速掘） - ``` thorns ``` （荆棘） - ``` depth_strider ``` （深海探索者） - ``` sharpness ``` （锋利） - ``` smite ``` （亡灵杀手） - ``` bane_of_arthropods ``` （节肢杀手） - ``` knockback ``` （击退） - ``` fire_aspect ``` （火焰附加） - ``` looting ``` （抢夺） - ``` sweeping_edge ``` （横扫之刃） - ``` efficiency ``` （效率） - ``` silk_touch ``` （精准采集） - ``` unbreaking ``` （耐久） - ``` fortune ``` （时运） - ``` power ``` （力量） - ``` punch ``` （冲击） - ``` flame ``` （火矢） - ``` infinity ``` （无限） - ``` luck_of_the_sea ``` （海之眷顾） - ``` lure ``` （饵钓） - ``` loyalty ``` （忠诚） - ``` impaling ``` （穿刺） - ``` riptide ``` （激流） - ``` channeling ``` （引雷） - ``` multishot ``` （多重射击） - ``` quick_charge ``` （快速装填） - ``` piercing ``` （穿透） - ``` density ``` （致密） - ``` breach ``` （破甲） - ``` lunge ``` （突进）

## on_mob_spawn_equipment

- 会出现在随机生成生物所穿装备上的魔咒。

- #on_mob_spawn_equipment（1项） - ``` #non_treasure ```

## on_random_loot

- 会出现在战利品箱子内的战利品上的魔咒。

- #on_random_loot（5项） - ``` #non_treasure ``` - ``` binding_curse ``` （绑定诅咒） - ``` vanishing_curse ``` （消失诅咒） - ``` frost_walker ``` （冰霜行者） - ``` mending ``` （经验修补）

## on_traded_equipment

- 会出现在交易中的附魔装备上的魔咒。

- #on_traded_equipment（1项） - ``` #non_treasure ```

## prevents_bee_spawns_when_mining

- 使工具破坏蜂巢和蜂箱后不会释放激怒状态的蜜蜂的魔咒。

- #prevents_bee_spawns_when_mining（1项） - ``` silk_touch ``` （精准采集）

## prevents_decorated_pot_shattering

- 使工具不会打破饰纹陶罐的魔咒。

- #prevents_decorated_pot_shattering（1项） - ``` silk_touch ``` （精准采集）

## prevents_ice_melting

- 使工具不会将冰打破成水的魔咒。

- #prevents_ice_melting（1项） - ``` silk_touch ``` （精准采集）

## prevents_infested_spawns

- 允许工具破坏虫蚀方块而不生成其中生物的魔咒。

- #prevents_infested_spawns（1项） - ``` silk_touch ``` （精准采集）

## smelts_loot

- 使掉落的战利品经过烧炼的魔咒。

- #smelts_loot（1项） - ``` fire_aspect ``` （火焰附加）

## tooltip_order

- 影响在物品提示框中所显示魔咒的顺序。

- #tooltip_order（43项） - ``` binding_curse ``` （绑定诅咒） - ``` vanishing_curse ``` （消失诅咒） - ``` riptide ``` （激流） - ``` channeling ``` （引雷） - ``` wind_burst ``` （风爆） - ``` frost_walker ``` （冰霜行者） - ``` lunge ``` （突进） - ``` sharpness ``` （锋利） - ``` smite ``` （亡灵杀手） - ``` bane_of_arthropods ``` （节肢杀手） - ``` impaling ``` （穿刺） - ``` power ``` （力量） - ``` density ``` （致密） - ``` breach ``` （破甲） - ``` piercing ``` （穿透） - ``` sweeping_edge ``` （横扫之刃） - ``` multishot ``` （多重射击） - ``` fire_aspect ``` （火焰附加） - ``` flame ``` （火矢） - ``` knockback ``` （击退） - ``` punch ``` （冲击） - ``` protection ``` （保护） - ``` blast_protection ``` （爆炸保护） - ``` fire_protection ``` （火焰保护） - ``` projectile_protection ``` （弹射物保护） - ``` feather_falling ``` （摔落缓冲） - ``` fortune ``` （时运） - ``` looting ``` （抢夺） - ``` silk_touch ``` （精准采集） - ``` luck_of_the_sea ``` （海之眷顾） - ``` efficiency ``` （效率） - ``` quick_charge ``` （快速装填） - ``` lure ``` （饵钓） - ``` respiration ``` （水下呼吸） - ``` aqua_affinity ``` （水下速掘） - ``` soul_speed ``` （灵魂疾行） - ``` swift_sneak ``` （迅捷潜行） - ``` depth_strider ``` （深海探索者） - ``` thorns ``` （荆棘） - ``` loyalty ``` （忠诚） - ``` unbreaking ``` （耐久） - ``` infinity ``` （无限） - ``` mending ``` （经验修补）

## tradeable

- 会出现在交易中的附魔书上的魔咒。

- #tradeable（5项） - ``` #non_treasure ``` - ``` binding_curse ``` （绑定诅咒） - ``` vanishing_curse ``` （消失诅咒） - ``` frost_walker ``` （冰霜行者） - ``` mending ``` （经验修补）

## treasure

- 宝藏类魔咒。

- #treasure（7项） - ``` binding_curse ``` （绑定诅咒） - ``` vanishing_curse ``` （消失诅咒） - ``` swift_sneak ``` （迅捷潜行） - ``` soul_speed ``` （灵魂疾行） - ``` frost_walker ``` （冰霜行者） - ``` mending ``` （经验修补） - ``` wind_burst ``` （风爆）

# 村民交易的平衡性调整

本段落包含在Java版的实验性内容中出现的内容。
这些特性在当前版本中需要开启“村民交易的平衡性调整”选项才可使用。

## trades/desert_common

沙漠图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/desert_common（3项） - ``` fire_protection ``` - ``` thorns ``` - ``` infinity ```

## trades/jungle_common

丛林图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/jungle_common（3项） - ``` feather_falling ``` - ``` projectile_protection ``` - ``` power ```

## trades/plains_common

平原图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/plains_common（3项） - ``` punch ``` - ``` smite ``` - ``` bane_of_arthropods ```

## trades/savanna_common

热带草原图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/savanna_common（3项） - ``` knockback ``` - ``` binding_curse ``` - ``` sweeping_edge ```

## trades/snow_common

雪原图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/snow_common（3项） - ``` aqua_affinity ``` - ``` looting ``` - ``` frost_walker ```

## trades/swamp_common

沼泽图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/swamp_common（3项） - ``` depth_strider ``` - ``` respiration ``` - ``` vanishing_curse ```

## trades/taiga_common

针叶林图书管理员售卖的附魔书能附加的普通魔咒。

- #trades/taiga_common（3项） - ``` blast_protection ``` - ``` fire_aspect ``` - ``` flame ```

# 历史

# 导航
