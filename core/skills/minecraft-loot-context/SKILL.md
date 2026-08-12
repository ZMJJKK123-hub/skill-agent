---
name: minecraft-loot-context
description: |
  战利品上下文（Minecraft Wiki 中文版全量正文）。
  
  【概述】战利品上下文（Loot Context）是一些用于战利品表、谓词、物品修饰器以及数值提供器等的参数构成的集合。尽管名为战利品上下文，但游戏也会在战利品表以外的系统使用战利品上下文，例如进度、魔咒和命令等。
  
  【涵盖内容】
  - 用于战利品表
  - empty
  - generic
  - advancement_reward
  - archaeology
  - barter
  - block
  - block_interact
  - chest
  - entity
  - entity_interact
  - equipment
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 战利品上下文 的完整规范时
---

本条目所述内容仅适用于Java版。
战利品上下文（Loot Context）是一些用于战利品表、谓词、物品修饰器以及数值提供器等的参数构成的集合。尽管名为战利品上下文，但游戏也会在战利品表以外的系统使用战利品上下文，例如进度、魔咒和命令等。

# 参数

战利品上下文中总共含有15/16种参数，这些参数根据战利品上下文类型的不同可能不存在：

- ``` this_entity ``` ：引起战利品生成的实体
- ``` interacting_entity ``` ：交互行为中的执行实体
- ``` target_entity ``` ：交互行为中的目标实体
- ``` last_damage_player ``` ：伤害实体的最后玩家
- ``` attacking_entity ``` ：导致实体受伤或死亡的源发实体
- ``` direct_attacking_entity ``` ：导致实体受伤或死亡的直接实体
- ``` damage_source ``` ：导致实体受伤或死亡的伤害来源
- ``` origin ``` ：引起战利品生成的来源位置
- ``` block_state ``` ：交互的方块状态
- ``` block_entity ``` ：交互的方块实体
- ``` tool ``` ：交互使用的物品堆叠
- ``` explosion_radius ``` ：距离爆炸中心的距离
- ``` enchantment_active ``` ：魔咒是否生效
- ``` enchantment_level ``` ：魔咒的等级
- ``` additional_cost_component_allowed ```
- ``` container ``` ：方块实体或实体等槽位提供者

游戏在谓词和物品修饰器等场合也需要从战利品上下文引用参数，但这些参数的名称可能和战利品上下文的参数名称不同：

- 实体目标 - ``` this ``` ：引用战利品上下文参数 ``` this_entity ``` 。 - ``` target_entity ``` ：引用战利品上下文参数 ``` target_entity ``` 。 - ``` interacting_entity ``` ：引用战利品上下文参数 ``` interacting_entity ``` 。 - ``` attacking_player ``` ：引用战利品上下文参数 ``` last_damage_player ``` 。 - ``` attacker ``` ：引用战利品上下文参数 ``` attacking_entity ``` 。 - ``` direct_attacker ``` ：引用战利品上下文参数 ``` direct_attacking_entity ``` 。
- 物品堆叠目标 - ``` tool ``` ：引用战利品上下文参数 ``` tool ``` 。
- 方块实体目标 - ``` block_entity ``` ：引用战利品上下文参数 ``` block_entity ``` 。

除上述参数外，战利品上下文也控制了战利品表中幸运值的来源和计算，详见战利品表 § 随机池。

# 参数集

游戏会在不同的场合使用不同的战利品上下文参数集。由于不同的战利品上下文可能具有不同的参数，故战利品上下文可以用于判定是否使用了此战利品上下文不提供的战利品上下文参数。这使得数据包在加载阶段就可以检查完相关参数，而非在运行时。

对于数据包中的战利品表，游戏将使用其[图:字符串]type字段来检查此战利品表使用的上下文参数。如果战利品表用于特定上下文，则指定类型字段允许游戏检查战利品表文件是否使用了该上下文中不会提供的参数，而无需在游戏中实际应用它们。

对于非战利品表系统，其验证使用的战利品上下文参数集是硬编码的。

下列是游戏内所有的战利品上下文参数集，以及他们提供的参数和使用情况：

## 用于战利品表

### empty

空参数集。
提供的上下文参数：

- 无。

可能提供的上下文参数：

- 无。

在战利品表中指定为
```
"type":"empty"
```

表示在此战利品表中无法使用任何战利品上下文参数。
使用情境：

- 试炼刷怪笼生成奖励物品时。
- 不祥试炼刷怪笼生成不祥之物生成器内的物品时。

### generic

通用参数集。
提供的上下文参数：

- ``` this_entity ``` 、 ``` last_damage_player ``` 、 ``` attacking_entity ``` 、 ``` direct_attacking_entity ``` 、 ``` block_entity ``` 、 ``` block_state ``` 、 ``` damage_source ``` 、 ``` explosion_radius ``` 、 ``` origin ``` 、 ``` tool ``` 、 ``` additional_cost_component_allowed ``` 和 ``` container ``` 。
- ``` origin ``` 和​ ``` container ``` 。

可能提供的上下文参数：

- 无。

在战利品表中指定为
```
"type":"generic"
```

表示在此战利品表中可以使用除
```
additional_cost_component_allowed
```

外战利品表系统使用的所有上下文参数（不包括
```
target_entity
```

和
```
interacting_entity
```

）。
使用情境：

- 游戏验证未指定战利品上下文参数集的战利品表时。

### advancement_reward

进度奖励参数集。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 玩家获得进度奖励时。 - ``` this_entity ``` ：完成进度的玩家。 - ``` origin ``` ：玩家获得进度的位置。

### archaeology

考古战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` origin ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 刷扫已设置战利品表的可疑的方块时。 - ``` this_entity ``` ：刷扫方块的实体。 - ``` origin ``` ：可疑的方块的中心位置。 - ``` tool ``` ：扫刷可疑的方块的刷子工具。

### barter

以物易物战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 与猪灵以物易物时。 - ``` this_entity ``` ：与玩家交易的猪灵。

### block

方块战利品参数集。
提供的上下文参数：

- ``` block_state ``` 、​ ``` origin ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 、​ ``` block_entity ``` 和​ ``` explosion_radius ``` 。

使用情境：

- 方块被破坏时。 - ``` this_entity ``` ：破坏方块的玩家。若方块被爆炸破坏，则为引起爆炸的实体。 - ``` block_entity ``` ：若为方块实体，则为此方块实体。 - ``` block_state ``` ：被破坏方块的方块状态。 - ``` explosion_radius ``` ：若方块被爆炸破坏，且导致方块爆炸的爆炸对应的游戏规则允许此爆炸概率不掉落掉落物，则为爆炸半径。 - ``` origin ``` ：被破坏的方块的中心。 - ``` tool ``` ：破坏时使用的工具。
- 使用 ``` / loot … mine <pos> ``` 命令时。 - ``` this_entity ``` ：命令执行者实体。 - ``` block_entity ``` ：若为方块实体，则为此方块实体。 - ``` block_state ``` ：方块的方块状态。 - ``` origin ``` ：方块的中心。 - ``` tool ``` ：命令指定的工具。
- 搬起方块的末影人死亡时。 - ``` this_entity ``` ：此末影人。 - ``` block_state ``` ：末影人搬起的方块。 - ``` origin ``` ：末影人死亡时的位置。 - ``` tool ``` ：附魔钻石斧。由魔咒提供器 ``` enderman_loot_drop ``` 附魔，默认精准采集I。

### block_interact

方块交互战利品参数集。
提供的上下文参数：

- ``` block_state ``` 。

可能提供的上下文参数：

- ``` interacting_entity ``` 、​ ``` block_entity ``` 和​ ``` tool ``` 。

使用情境：

- 修剪南瓜时。 - ``` interacting_entity ``` ：修剪南瓜的实体。 - ``` block_state ``` ：南瓜。 - ``` block_entity ``` ：南瓜所在位置的方块实体。 - ``` tool ``` ：修剪南瓜使用的剪刀工具。
- 修剪蜂巢或蜂箱时。 - ``` interacting_entity ``` ：修剪蜂巢或蜂箱的实体。 - ``` block_state ``` ：蜂巢或蜂箱。 - ``` block_entity ``` ：蜂巢或蜂箱。 - ``` tool ``` ：修剪蜂巢或蜂箱使用的剪刀工具。
- 玩家采摘发光浆果时。 - ``` interacting_entity ``` ：采摘发光浆果的玩家。 - ``` block_state ``` ：洞穴藤蔓或洞穴藤蔓植株。 - ``` block_entity ``` ：洞穴藤蔓或洞穴藤蔓植株所在位置的方块实体。
- 玩家采摘甜浆果时。 - ``` interacting_entity ``` ：采摘甜浆果丛的玩家。 - ``` block_state ``` ：甜浆果丛。 - ``` block_entity ``` ：甜浆果丛所在位置的方块实体。
- Java版26.3起，填充堆肥桶时。 - ``` interacting_entity ``` ：向堆肥桶填充物品的实体。 - ``` block_state ``` ：堆肥桶。

### chest

容器战利品参数集。
提供的上下文参数：

- ``` origin ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 。

使用情境：

- 打开带有战利品表的容器时。容器可以是木桶、箱子、陷阱箱、漏斗、运输船、运输矿车、漏斗矿车、发射器、投掷器、合成器、潜影盒和饰纹陶罐。 - ``` this_entity ``` ：打开容器的实体。 - ``` origin ``` ：容器的中心位置。
- 使用 ``` / loot … loot <loot_table> ``` 命令时。 - ``` this_entity ``` ：命令执行者实体。 - ``` origin ``` ：命令执行坐标。

### entity

生物死亡战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` damage_source ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- ``` direct_attacking_entity ``` 、​ ``` last_damage_player ``` 和​ ``` attacking_entity ``` 。

使用情境：

- 生物死亡时。 - ``` this_entity ``` ：死亡的实体。 - ``` direct_attacking_entity ``` ：直接导致实体死亡的实体。 - ``` last_damage_player ``` ：伤害死亡实体的最后玩家。 - ``` attacking_entity ``` ：给实体造成最后伤害的来源实体。 - ``` damage_source ``` ：导致实体死亡的伤害来源。 - ``` origin ``` ：死亡位置。
- 使用 ``` / loot … kill <target> ``` 命令时。 - ``` this_entity ``` ：命令指定的实体。 - ``` direct_attacking_entity ``` ：命令执行者实体。 - ``` last_damage_player ``` ：如果命令执行者实体是玩家，则为此玩家。 - ``` attacking_entity ``` ：命令执行者实体。 - ``` damage_source ``` ： ``` magic ``` 伤害类型。 - ``` origin ``` ：死亡位置。

### entity_interact

生物交互战利品参数集。
提供的上下文参数：

- ``` target_entity ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- ``` interacting_entity ``` 。

使用情境：

- 扫刷犰狳时。 - ``` target_entity ``` ：犰狳。 - ``` interacting_entity ``` ：扫刷犰狳的实体。 - ``` tool ``` ：扫刷使用的刷子工具。

### equipment

装备战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 当任何种类的刷怪笼生成实体，且使用战利品表为生物穿上装备时。 - ``` this_entity ``` ：生成的生物。 - ``` origin ``` ：生成的生物位置。

### fishing

钓鱼战利品参数集。
提供的上下文参数：

- ``` origin ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 。

使用情境：

- 钓鱼时。 - ``` this_entity ``` ：浮漂实体。 - ``` origin ``` ：浮漂的位置。 - ``` tool ``` ：玩家使用的钓鱼竿工具。
- 使用 ``` / loot … fish <loot_table> ``` 命令时。 - ``` this_entity ``` ：命令执行者实体。 - ``` origin ``` ：命令指定的位置的方块中心。 - ``` tool ``` ：命令指定的工具。

### gift

礼物战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 猫给予玩家礼物时。
- 村民给予玩家礼物时。
- 嗅探兽刨挖时。
- 鸡下蛋时。
- 犰狳随机掉落犰狳鳞甲时。
- 熊猫打喷嚏时。
- 幼年海龟成年时。 - ``` this_entity ``` ：猫、村民等上述实体。 - ``` origin ``` ：猫、村民等上述实体的位置。

### shearing

修剪战利品参数集。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` origin ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 剪去沼骸的蘑菇时。
- 剪去绵羊的羊毛时。
- 剪去哞菇的蘑菇时。
- 剪去雪傀儡的南瓜头时。 - ``` this_entity ``` ：被修剪的生物。 - ``` origin ``` ：被修剪的生物位置。 - ``` tool ``` ：修剪使用的剪刀工具。

### vault

宝库战利品参数集。
提供的上下文参数：

- ``` origin ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 和​ ``` tool ``` 。

使用情境：

- 宝库展示物品时。 - ``` origin ``` ：宝库方块的中心位置。
- 宝库产生战利品时。 - ``` this_entity ``` ：打开宝库的玩家。 - ``` origin ``` ：宝库方块的中心位置。 - ``` tool ``` ：解锁宝库的物品。

## 仅用于谓词

### advancement_entity

进度实体谓词参数集。
不用于战利品表，写为
```
"type":"advancement_entity"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 进度判定实体条件时。

- ``` this_entity ``` ：被检查的实体。
- ``` origin ``` ：将获得进度的玩家位置。

### advancement_location

进度位置谓词参数集。
不用于战利品表，写为
```
"type":"advancement_location"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` block_state ``` 、​ ``` origin ``` 和​ ``` tool ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 进度触发器 ``` allay_drop_item_on_block ``` 判定位置条件时。

- ``` this_entity ``` ：给予悦灵物品的玩家。
- ``` block_state ``` ：悦灵将物品投掷到的方块。
- ``` origin ``` ：物品被投掷到的方块的中心位置。
- ``` tool ``` ：悦灵持有的物品。

- 进度触发器 ``` any_block_use ``` 和 ``` item_used_on_block ``` 判定位置条件时。

- ``` this_entity ``` ：与方块交互的玩家。
- ``` block_state ``` ：被交互的方块。
- ``` origin ``` ：被交互的方块的中心位置。
- ``` tool ``` ：与方块交互使用的物品。

- 进度触发器 ``` placed_block ``` 判定位置条件时。

- ``` this_entity ``` ：放置方块的玩家。
- ``` block_state ``` ：被放置的方块。
- ``` origin ``` ：被放置的方块的中心位置。
- ``` tool ``` ：放置方块时使用的物品。

### block_use

方块默认交互信息谓词参数集。

- 不用于战利品表，写为 ``` "type":"block_use" ``` 是无效的。

提供的上下文参数：

- ``` this_entity ``` 、​ ``` block_state ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

- 使用情境：

- 进度触发器 ``` default_block_use ``` 判定位置条件时。

- ``` this_entity ``` ：与方块交互的玩家。
- ``` block_state ``` ：被交互的方块。
- ``` origin ``` ：被交互的方块的中心。

### command

命令参数集。

- 不用于战利品表，写为 ``` "type":"command" ``` 是无效的。

提供的上下文参数：

- ``` origin ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 。

- 使用情境：

- 使用 ``` / execute (if|unless) predicate ``` 命令进行谓词判断时。

- ``` this_entity ``` ：命令的执行实体。
- ``` origin ``` ：命令的执行位置。

- 使用 ``` / item ``` 命令修饰物品时。

- ``` this_entity ``` ：命令的执行实体。
- ``` origin ``` ：命令的执行位置。

### command_slot_source

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

命令槽位源参数集。

- 不用于战利品表，写为 ``` "type":"command_slot_source" ``` 是无效的。

提供的上下文参数：

- ``` origin ``` 和​ ``` container ``` 。

可能提供的上下文参数：

- ``` this_entity ``` 。

- 使用情境：

- 命令获取槽位源时。

- ``` origin ``` ：命令的执行位置。
- ``` container ``` ：命令的目标槽位。
- ``` this_entity ``` ：命令执行者实体。

### enchanted_damage

魔咒伤害效果参数集。
不用于战利品表，写为
```
"type":"enchanted_damage"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` damage_source ``` 、​ ``` origin ``` 和​ ``` enchantment_level ``` 。

可能提供的上下文参数：

- ``` attacking_entity ``` 和​ ``` direct_attacking_entity ``` 。

- 使用情境：

- 魔咒效果组件 ``` armor_effectiveness ``` 、​ ``` damage ``` 、​ ``` damage_immunity ``` 、​ ``` damage_protection ``` 、​ ``` equipment_drops ``` 、​ ``` knockback ``` 、​ ``` post_attack ``` 和​ ``` smash_damage_per_fallen_block ``` 计算生效条件时。

- ``` this_entity ``` ：受伤或死亡的实体。
- ``` attacking_entity ``` ：伤害的来源实体。
- ``` direct_attacking_entity ``` ：伤害的直接实体。
- ``` damage_source ``` ：造成这次伤害的伤害来源。
- ``` origin ``` ：对应实体的位置。
- ``` enchantment_level ``` ：魔咒等级。

### enchanted_entity

魔咒实体效果参数集。
不用于战利品表，写为
```
"type":"enchanted_entity"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` origin ``` 和​ ``` enchantment_level ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 魔咒效果组件 ``` fishing_luck_bonus ``` 、​ ``` fishing_time_reduction ``` 、​ ``` mob_experience ``` 、​ ``` post_piercing_attack ``` 、​ ``` projectile_count ``` 、​ ``` projectile_spawned ``` 、​ ``` projectile_spread ``` 、​ ``` tick ``` 和​ ``` trident_return_acceleration ``` 计算生效条件时。

- ``` this_entity ``` ：对应的实体。

- ``` fishing_luck_bonus ``` ：钓鱼的玩家
- ``` fishing_time_reduction ``` ：钓鱼的玩家
- ``` mob_experience ``` ：死亡的实体
- ``` post_piercing_attack ``` ：进行戳刺攻击的生物
- ``` projectile_count ``` ：装填弓弩的生物
- ``` projectile_spawned ``` ：发射的弹射物
- ``` projectile_spread ``` ：使用弓弩的生物
- ``` tick ``` ：使魔咒生效的实体
- ``` trident_return_acceleration ``` ：三叉戟

- ``` origin ``` ：对应的实体的位置。
- ``` enchantment_level ``` ：魔咒等级。

### enchanted_item

魔咒物品效果参数集。
不用于战利品表，写为
```
"type":"enchanted_item"
```

是无效的。
提供的上下文参数：

- ``` tool ``` 和​ ``` enchantment_level ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 魔咒效果组件 ``` ammo_use ``` 、​ ``` block_experience ``` 、​ ``` item_damage ``` 、​ ``` projectile_piercing ``` 和​ ``` repair_with_xp ``` 计算生效条件时。

- ``` tool ``` ：带有魔咒的物品。
- ``` enchantment_level ``` ：魔咒等级。

### enchanted_location

魔咒位置效果参数集。
不用于战利品表，写为
```
"type":"enchanted_location"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` origin ``` 、​ ``` enchantment_active ``` 和​ ``` enchantment_level ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 魔咒效果组件 ``` location_changed ``` 计算生效条件时。

- ``` this_entity ``` ：使魔咒生效的实体。
- ``` origin ``` ：使魔咒生效的实体的位置。
- ``` enchantment_active ``` ：魔咒是否已经生效。
- ``` enchantment_level ``` ：魔咒等级。

### hit_block

魔咒击中方块效果参数集。
不用于战利品表，写为
```
"type":"hit_block"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 、​ ``` block_state ``` 、​ ``` origin ``` 和​ ``` enchantment_level ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 魔咒效果组件 ``` hit_block ``` 计算生效条件时。

- ``` this_entity ``` ：击中方块的实体。
- ``` block_state ``` ：击中的方块。
- ``` origin ``` ：击中的方块的位置。
- ``` enchantment_level ``` ：魔咒等级。

### selector

目标选择器参数集。
不用于战利品表，写为
```
"type":"selector"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 目标选择器使用谓词筛选实体时。

- ``` this_entity ``` ：被检测的实体。
- ``` origin ``` ：被检测实体的位置。

### villager_trade

村民交易参数集。
不用于战利品表，写为
```
"type":"villager_trade"
```

是无效的。
提供的上下文参数：

- ``` this_entity ``` 和​ ``` origin ``` 。

可能提供的上下文参数：

- 无。

使用情境：

- 村民生成交易时。

- ``` this_entity ``` ：生成交易的村民。
- ``` origin ``` ：生成交易的村民的位置。
- ``` additional_cost_component_allowed ```

# 历史

# 导航
