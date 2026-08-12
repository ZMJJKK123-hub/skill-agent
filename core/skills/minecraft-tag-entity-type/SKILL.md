---
name: minecraft-tag-entity-type
description: |
  Java版标签/实体类型（Minecraft Wiki 中文版全量正文）。
  
  【概述】实体类型标签（Entity Type Tags）是实体类型的组合。
  
  【涵盖内容】
  - accepts_iron_golem_gift
  - aquatic
  - arrows
  - arthropod
  - axolotl_always_hostiles
  - axolotl_hunt_targets
  - beehive_inhabitors
  - boat
  - burn_in_daylight
  - can_breathe_under_water
  - can_equip_harness
  - can_equip_saddle
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/实体类型 的完整规范时
---

本条目所述内容仅适用于Java版。
实体类型标签（Entity Type Tags）是实体类型的组合。

# 使用

实体类型标签可以被实体谓词和目标选择器等调用以测试实体类型。只要实体类型在此标签内，测试就会成功。实体类型标签也控制了一些与特定实体相关的游戏行为，参考以下每个标签的介绍。

# 标签列表

## accepts_iron_golem_gift

- 会将铁傀儡的赠礼戴到头上的实体。

- #accepts_iron_golem_gift（1项） - ``` copper_golem ``` （铜傀儡）

## aquatic

- 被视为水生生物的实体。

- #aquatic（14项） - ``` turtle ``` （海龟） - ``` axolotl ``` （美西螈） - ``` guardian ``` （守卫者） - ``` elder_guardian ``` （远古守卫者） - ``` cod ``` （鳕鱼） - ``` pufferfish ``` （河豚） - ``` salmon ``` （鲑鱼） - ``` tropical_fish ``` （热带鱼） - ``` dolphin ``` （海豚） - ``` squid ``` （鱿鱼） - ``` glow_squid ``` （发光鱿鱼） - ``` tadpole ``` （蝌蚪） - ``` nautilus ``` （鹦鹉螺） - ``` zombie_nautilus ``` （僵尸鹦鹉螺）

## arrows

- 用于瞄准目标进度。

- #arrows（2项） - ``` arrow ``` （箭） - ``` spectral_arrow ``` （光灵箭）

## arthropod

- 被视为节肢生物的实体。

- #arthropod（5项） - ``` bee ``` （蜜蜂） - ``` endermite ``` （末影螨） - ``` silverfish ``` （蠹虫） - ``` spider ``` （蜘蛛） - ``` cave_spider ``` （洞穴蜘蛛）

## axolotl_always_hostiles

- 美西螈总是对这些实体保持敌对。

- #axolotl_always_hostiles（3项） - ``` drowned ``` （溺尸） - ``` guardian ``` （守卫者） - ``` elder_guardian ``` （远古守卫者）

## axolotl_hunt_targets

- 美西螈会在有冷却时间的情况下“猎杀”这些实体。

- #axolotl_hunt_targets（7项） - ``` tropical_fish ``` （热带鱼） - ``` pufferfish ``` （河豚） - ``` salmon ``` （鲑鱼） - ``` cod ``` （鳕鱼） - ``` squid ``` （鱿鱼） - ``` glow_squid ``` （发光鱿鱼） - ``` tadpole ``` （蝌蚪）

## beehive_inhabitors

- 这些实体可以进入蜂箱。

- #beehive_inhabitors（1项） - ``` bee ``` （蜜蜂）

## boat

- 用于羊帆起航！进度。

- #boat（11项） - ``` oak_boat ``` （橡木船） - ``` spruce_boat ``` （云杉木船） - ``` birch_boat ``` （白桦木船） - ``` jungle_boat ``` （丛林木船） - ``` acacia_boat ``` （金合欢木船） - ``` cherry_boat ``` （樱花木船） - ``` dark_oak_boat ``` （深色橡木船） - ``` pale_oak_boat ``` （苍白橡木船） - ``` mangrove_boat ``` （红树木船） - ``` bamboo_raft ``` （竹筏） - ``` poplar_boat ``` （杨木船）

## burn_in_daylight

- 会在阳光下着火的实体。

- #burn_in_daylight（10项） - ``` skeleton ``` （骷髅） - ``` stray ``` （流浪者） - ``` wither_skeleton ``` （凋灵骷髅） - ``` bogged ``` （沼骸） - ``` zombie ``` （僵尸） - ``` zombie_horse ``` （僵尸马） - ``` zombie_villager ``` （僵尸村民） - ``` drowned ``` （溺尸） - ``` zombie_nautilus ``` （僵尸鹦鹉螺） - ``` phantom ``` （幻翼）

## can_breathe_under_water

- 拥有该标签的生物不会溺水。

- #can_breathe_under_water（16项） - ``` #undead ``` - ``` axolotl ``` （美西螈） - ``` frog ``` （青蛙） - ``` guardian ``` （守卫者） - ``` elder_guardian ``` （远古守卫者） - ``` turtle ``` （海龟） - ``` glow_squid ``` （发光鱿鱼） - ``` cod ``` （鳕鱼） - ``` pufferfish ``` （河豚） - ``` salmon ``` （鲑鱼） - ``` squid ``` （鱿鱼） - ``` tropical_fish ``` （热带鱼） - ``` tadpole ``` （蝌蚪） - ``` armor_stand ``` （盔甲架） - ``` copper_golem ``` （铜傀儡） - ``` nautilus ``` （鹦鹉螺）

## can_equip_harness

- 可装备挽具的实体。

- #can_equip_harness（1项） - ``` happy_ghast ``` （快乐恶魂）

## can_equip_saddle

- 可装备鞍的实体。

- #can_equip_saddle（11项） - ``` horse ``` （马） - ``` skeleton_horse ``` （骷髅马） - ``` zombie_horse ``` （僵尸马） - ``` donkey ``` （驴） - ``` mule ``` （骡） - ``` pig ``` （猪） - ``` strider ``` （炽足兽） - ``` camel ``` （骆驼） - ``` camel_husk ``` （骆驼尸壳） - ``` nautilus ``` （鹦鹉螺） - ``` zombie_nautilus ``` （僵尸鹦鹉螺）

## can_float_while_ridden

- 控制生物被骑乘时是否可在水上漂浮游泳而非下沉。

- #can_float_while_ridden（6项） - ``` horse ``` （马） - ``` zombie_horse ``` （僵尸马） - ``` mule ``` （骡） - ``` donkey ``` （驴） - ``` camel ``` （骆驼） - ``` camel_husk ``` （骆驼尸壳）

## can_turn_in_boats

- 拥有该标签的生物能在船中改变方向。

- #can_turn_in_boats（1项） - ``` breeze ``` （旋风人）

## can_wear_horse_armor

- 拥有该标签的生物会在其马类实体物品栏中显示马铠槽位。

- #can_wear_horse_armor（2项） - ``` horse ``` （马） - ``` zombie_horse ``` （僵尸马）

## can_wear_nautilus_armor

- 可装备鹦鹉螺铠的实体。

- #can_wear_nautilus_armor（2项） - ``` nautilus ``` （鹦鹉螺） - ``` zombie_nautilus ``` （僵尸鹦鹉螺）

## candidate_for_iron_golem_gift

- 会被铁傀儡赠予虞美人的实体。

- #candidate_for_iron_golem_gift（2项） - ``` villager ``` （村民） - ``` #accepts_iron_golem_gift ```

## cannot_be_age_locked

- 不可以被金蒲公英停止生长的可成长生物。

- #cannot_be_age_locked（3项） - ``` zombie_horse ``` （僵尸马） - ``` skeleton_horse ``` （骷髅马） - ``` villager ``` （村民）

## cannot_be_dismounted_by_item_usage

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 生物对这些实体使用物品后，不会脱离骑乘状态。

- #cannot_be_dismounted_by_item_usage（1项） - ``` interaction ``` （交互实体）

## cannot_be_pushed_onto_boats

- 不会被推进船的实体。

- #cannot_be_pushed_onto_boats（14项） - ``` player ``` （玩家） - ``` elder_guardian ``` （远古守卫者） - ``` cod ``` （鳕鱼） - ``` pufferfish ``` （河豚） - ``` salmon ``` （鲑鱼） - ``` tropical_fish ``` （热带鱼） - ``` dolphin ``` （海豚） - ``` squid ``` （鱿鱼） - ``` glow_squid ``` （发光鱿鱼） - ``` tadpole ``` （蝌蚪） - ``` creaking ``` （嘎枝） - ``` nautilus ``` （鹦鹉螺） - ``` zombie_nautilus ``` （僵尸鹦鹉螺） - ``` sulfur_cube ``` （硫方怪）

## deflects_projectiles

- 拥有该标签的生物能反射弹射物。

- #deflects_projectiles（1项） - ``` breeze ``` （旋风人）

## dismounts_underwater

- 这些实体会在进入水中时强制其乘客离开。

- #dismounts_underwater（13项） - ``` camel ``` （骆驼） - ``` chicken ``` （鸡） - ``` donkey ``` （驴） - ``` happy_ghast ``` （快乐恶魂） - ``` horse ``` （马） - ``` llama ``` （羊驼） - ``` mule ``` （骡） - ``` pig ``` （猪） - ``` ravager ``` （劫掠兽） - ``` spider ``` （蜘蛛） - ``` strider ``` （炽足兽） - ``` trader_llama ``` （行商羊驼） - ``` zombie_horse ``` （僵尸马）

## fall_damage_immune

- 这些实体不会受到摔落伤害。

- #fall_damage_immune（18项） - ``` copper_golem ``` （铜傀儡） - ``` iron_golem ``` （铁傀儡） - ``` snow_golem ``` （雪傀儡） - ``` shulker ``` （潜影贝） - ``` allay ``` （悦灵） - ``` bat ``` （蝙蝠） - ``` bee ``` （蜜蜂） - ``` blaze ``` （烈焰人） - ``` cat ``` （猫） - ``` chicken ``` （鸡） - ``` ghast ``` （恶魂） - ``` happy_ghast ``` （快乐恶魂） - ``` phantom ``` （幻翼） - ``` magma_cube ``` （岩浆怪） - ``` ocelot ``` （豹猫） - ``` parrot ``` （鹦鹉） - ``` wither ``` （凋灵） - ``` breeze ``` （旋风人）

## followable_friendly_mobs

- 会被小恶魂跟随的非幼年实体。

- #followable_friendly_mobs（25项） - ``` armadillo ``` （犰狳） - ``` bee ``` （蜜蜂） - ``` camel ``` （骆驼） - ``` cat ``` （猫） - ``` chicken ``` （鸡） - ``` cow ``` （牛） - ``` donkey ``` （驴） - ``` fox ``` （狐狸） - ``` goat ``` （山羊） - ``` happy_ghast ``` （快乐恶魂） - ``` horse ``` （马） - ``` skeleton_horse ``` （骷髅马） - ``` llama ``` （羊驼） - ``` mule ``` （骡） - ``` ocelot ``` （豹猫） - ``` panda ``` （熊猫） - ``` parrot ``` （鹦鹉） - ``` pig ``` （猪） - ``` polar_bear ``` （北极熊） - ``` rabbit ``` （兔子） - ``` sheep ``` （绵羊） - ``` sniffer ``` （嗅探兽） - ``` strider ``` （炽足兽） - ``` villager ``` （村民） - ``` wolf ``` （狼）

## freeze_hurts_extra_types

- 拥有这个标签的实体在细雪中会受到额外伤害。

- #freeze_hurts_extra_types（3项） - ``` strider ``` （炽足兽） - ``` blaze ``` （烈焰人） - ``` magma_cube ``` （岩浆怪）

## freeze_immune_entity_types

- 拥有这个标签的实体免疫冰冻伤害。

- #freeze_immune_entity_types（4项） - ``` stray ``` （流浪者） - ``` polar_bear ``` （北极熊） - ``` snow_golem ``` （雪傀儡） - ``` wither ``` （凋灵）

## frog_food

- 青蛙会捕食这些实体，只有是生物的实体才有效。

- #frog_food（2项） - ``` slime ``` （史莱姆） - ``` magma_cube ``` （岩浆怪）

## ignores_poison_and_regen

- 免疫中毒和生命恢复效果的实体。

- #ignores_poison_and_regen（1项） - ``` #undead ```

## illager

- 被视为灾厄村民的实体。

- #illager（4项） - ``` evoker ``` （唤魔者） - ``` illusioner ``` （幻术师） - ``` pillager ``` （掠夺者） - ``` vindicator ``` （卫道士）

## illager_friends

- 被灾厄村民视为盟友的实体（不包括在其他队伍中的）。

- #illager_friends（1项） - ``` #illager ```

## immune_to_infested

- 免疫寄生状态效果的实体。

- #immune_to_infested（1项） - ``` silverfish ``` （蠹虫）

## immune_to_oozing

- 免疫渗浆状态效果的实体。

- #immune_to_oozing（1项） - ``` slime ``` （史莱姆）

## impact_projectiles

- 用来决定哪些实体可以破坏紫颂花和饰纹陶罐。
- 实体可以从这个标签中移除，若添加其他实体，则只有标靶可以响应的实体才有效。

- #impact_projectiles（11项） - ``` #arrows ``` - ``` firework_rocket ``` （烟花火箭） - ``` snowball ``` （雪球） - ``` fireball ``` （火球） - ``` small_fireball ``` （小火球） - ``` egg ``` （掷出的鸡蛋） - ``` trident ``` （三叉戟） - ``` dragon_fireball ``` （末影龙火球） - ``` wither_skull ``` （凋灵之首） - ``` wind_charge ``` （风弹） - ``` breeze_wind_charge ``` （风弹）

## inverted_healing_and_harm

- 瞬间治疗和瞬间伤害会对其产生相反效果的实体。

- #inverted_healing_and_harm（1项） - ``` #undead ```

## nautilus_hostiles

- 未驯服的鹦鹉螺和僵尸鹦鹉螺默认敌对的实体。

- #nautilus_hostiles（1项） - ``` pufferfish ``` （河豚）

## no_anger_from_wind_charge

- 不会被风弹激怒的实体。

- #no_anger_from_wind_charge（9项） - ``` breeze ``` （旋风人） - ``` skeleton ``` （骷髅） - ``` bogged ``` （沼骸） - ``` stray ``` （流浪者） - ``` zombie ``` （僵尸） - ``` husk ``` （尸壳） - ``` spider ``` （蜘蛛） - ``` cave_spider ``` （洞穴蜘蛛） - ``` slime ``` （史莱姆）

## non_controlling_rider

- 不能控制载具移动的实体。

- #non_controlling_rider（3项） - ``` slime ``` （史莱姆） - ``` magma_cube ``` （岩浆怪） - ``` sulfur_cube ``` （硫方怪）

## not_affected_by_geysers

- 不会受到间歇泉喷发提供的向上冲量影响的实体。

- #not_affected_by_geysers（1项） - ``` ender_dragon ``` （末影龙）

## not_scary_for_pufferfish

- 不会使河豚膨胀的实体。

- #not_scary_for_pufferfish（14项） - ``` turtle ``` （海龟） - ``` guardian ``` （守卫者） - ``` elder_guardian ``` （远古守卫者） - ``` cod ``` （鳕鱼） - ``` pufferfish ``` （河豚） - ``` salmon ``` （鲑鱼） - ``` tropical_fish ``` （热带鱼） - ``` dolphin ``` （海豚） - ``` squid ``` （鱿鱼） - ``` glow_squid ``` （发光鱿鱼） - ``` tadpole ``` （蝌蚪） - ``` nautilus ``` （鹦鹉螺） - ``` zombie_nautilus ``` （僵尸鹦鹉螺） - ``` sulfur_cube ``` （硫方怪）

## powder_snow_walkable_mobs

- 拥有这个标签的实体可以在细雪顶部行走。

- #powder_snow_walkable_mobs（4项） - ``` rabbit ``` （兔子） - ``` endermite ``` （末影螨） - ``` silverfish ``` （蠹虫） - ``` fox ``` （狐狸）

## raiders

- 决定敲钟时哪些实体获得发光效果。
- 此标签中的实体在骑乘劫掠兽时不会覆盖劫掠兽的AI。
- 用于自我放逐进度。

- #raiders（6项） - ``` evoker ``` （唤魔者） - ``` pillager ``` （掠夺者） - ``` ravager ``` （劫掠兽） - ``` vindicator ``` （卫道士） - ``` illusioner ``` （幻术师） - ``` witch ``` （女巫）

## redirectable_projectile

- 能被玩家攻击和弹射物击中且会随玩家视角或弹射物方向偏转的弹射物实体。

- #redirectable_projectile（3项） - ``` fireball ``` （火球） - ``` wind_charge ``` （风弹） - ``` breeze_wind_charge ``` （风弹）

## sensitive_to_bane_of_arthropods

- 节肢杀手魔咒会对其产生额外伤害的实体。

- #sensitive_to_bane_of_arthropods（1项） - ``` #arthropod ```

## sensitive_to_impaling

- 穿刺魔咒会对其产生额外伤害的实体。

- #sensitive_to_impaling（1项） - ``` #aquatic ```

## sensitive_to_smite

- 亡灵杀手魔咒会对其产生额外伤害的实体。

- #sensitive_to_smite（1项） - ``` #undead ```

## skeletons

- 苦力怕在被这些实体杀死时掉落音乐唱片。

- #skeletons（6项） - ``` skeleton ``` （骷髅） - ``` stray ``` （流浪者） - ``` wither_skeleton ``` （凋灵骷髅） - ``` skeleton_horse ``` （骷髅马） - ``` bogged ``` （沼骸） - ``` parched ``` （焦骸）

## undead

- 拥有这个标签的实体属于亡灵生物。

- #undead（4项） - ``` #skeletons ``` - ``` #zombies ``` - ``` wither ``` （凋灵） - ``` phantom ``` （幻翼）

## wither_friends

- 不被凋灵视为目标，也不会对凋灵造成伤害的实体。

- #wither_friends（1项） - ``` #undead ```

## zombies

- 拥有这个标签的实体属于僵尸类生物。

- #zombies（9项） - ``` zombie_horse ``` （僵尸马） - ``` camel_husk ``` （骆驼尸壳） - ``` zombie ``` （僵尸） - ``` zombie_villager ``` （僵尸村民） - ``` zombified_piglin ``` （僵尸猪灵） - ``` zoglin ``` （僵尸疣猪兽） - ``` drowned ``` （溺尸） - ``` husk ``` （尸壳） - ``` zombie_nautilus ``` （僵尸鹦鹉螺）

# 已移除的标签

## axolotl_tempted_hostiles

- 已被 ``` #axolotl_always_hostiles ``` 标签取代。

添加于：20w51a。移除于：21w13a。

- #axolotl_tempted_hostiles（2项） - ``` drowned ``` - ``` guardian ```

## deflects_arrows

- 已被 ``` #deflects_projectiles ``` 标签取代。

添加于：23w45a。移除于：24w03a。

- #deflects_arrows（1项） - ``` breeze ```

## deflects_tridents

- 已被 ``` #deflects_projectiles ``` 标签取代。

添加于：23w45a。移除于：24w03a。

- #deflects_tridents（1项） - ``` breeze ```

# 历史

# 导航
