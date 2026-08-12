---
name: minecraft-entity-data-format
description: |
  实体数据格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于基岩版中的实体格式，请见“基岩版存档格式/实体格式”。
  
  【涵盖内容】
  - 生物
  - 基因
  - 弹射物
  - 交通工具
  - 其他
  
  【关键定义】
  - 数据包路径：data/width/2
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 实体数据格式 的完整规范时
---

关于基岩版中的实体格式，请见“基岩版存档格式/实体格式”。

本条目所述内容仅适用于Java版。
各种实体都有它们各自的数据，对应了不同的数据格式。

# 数据格式

所有实体都有一部分相同的数据格式，以保存实体的最基础的信息：

- [图:NBT复合标签/JSON对象] 实体数据根标签

- - [图:字符串]* *id：（命名空间ID）实体类型。此数据仅在持久化保存（存储入区块文件、结构模板、蜂巢、蜂箱数据或作为乘客实体保存）时存在。 ``` / data ``` 无法获取此数据，也无法修改。 - [图:短整型]*Air：（-20≤值≤实体最大空气值）当前实体所剩的空气值。在指定环境中每刻增加4直至实体最大空气值；在可窒息环境中逐渐减少直至-20，达到-20后如果实体仍然在可窒息环境中则会受到伤害，并将此值重置为0，继续减少进行循环。此值不存在时游戏默认为实体最大空气值。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前实体的自定义名称。会出现在玩家的死亡消息与村民的交易界面，以及玩家的光标指向的实体的上方。此项实体数据会被视为数据组件custom_name。 - [图:布尔型]CustomNameVisible：表示实体是否一直渲染名称。如果为true，那么名称会一直在它们的上方渲染，而不受光标指向的影响。如果实体没有自定义名称，则渲染默认名称。此项不存在时游戏默认为false。 - [图:字符串][图:NBT复合标签/JSON对象]data：任意NBT数据。字符串形式只用于加载，游戏在保存时只使用复合标签形式。此项实体数据会被视为数据组件custom_data。 - [图:双精度浮点数]*fall_distance：当前实体已经摔落的距离。值越大，实体落地时受到的摔落伤害越大。此项不存在时游戏默认为0。 - [图:短整型]*Fire：正值代表距离火熄灭剩余的时间，负值表示当前实体能够在火中站立而不着火的时间，单位为游戏刻。未着火且未接触火时，玩家为-20游戏刻（1秒），其他实体为-1游戏刻（0.05秒）。此项不存在时游戏默认为0。 - [图:布尔型]Glowing：实体是否有发光的轮廓线。此项不存在时游戏默认为false。 - [图:布尔型]HasVisualFire：表示实体是否视觉上正在着火。如果为true，实体会渲染为正在着火，但实际上可能没有着火。此项不存在时游戏默认为false。 - [图:布尔型]*Invulnerable：实体是否永久抵抗绝大多数伤害。如果为true，实体只会受到来自创造模式玩家的伤害和属于 ``` #bypasses_invulnerability ``` 标签的伤害。此项不存在时游戏默认为false。 - [图:整型]invulnerable_time：实体能够抵抗绝大多数伤害的剩余刻数。此项不存在时游戏默认为0。此项小于等于0时不会被存储。 - [图:NBT列表/JSON数组]* *Motion：当前实体的速度，代表了下一游戏刻实体的移动距离和方向。 - [图:双精度浮点数]：（-10≤值≤10）X轴速度分量。如果此值超过值域，则加载时会被重置为0。如果为非数（NaN），游戏不做处理正常加载。 - [图:双精度浮点数]：（-10≤值≤10）Y轴速度分量。如果此值超过值域，则加载时会被重置为0。如果为非数（NaN），游戏不做处理正常加载。 - [图:双精度浮点数]：（-10≤值≤10）Z轴速度分量。如果此值超过值域，则加载时会被重置为0。如果为非数（NaN），游戏不做处理正常加载。 - [图:布尔型]NoGravity：实体是否不会受到重力的影响。此项不存在时游戏默认为false。 - [图:布尔型]*OnGround：实体是否正在接触地面。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Passengers：正在骑乘当前实体的实体的数据，递归标签。此值仅在使用 ``` / summon ``` 指定标签生成实体、刷怪笼和试炼刷怪笼指定生成数据生成实体时此标签才可以有效设置，其他任何方式均无法有效设置。 - [图:NBT复合标签/JSON对象]：一个乘客。 - 详见实体数据格式。 - [图:整型]*PortalCooldown：距离当前实体下一次可以穿过下界传送门传送的时间，以游戏刻计。在使用下界传送门传送后，此项根据玩家游戏模式和当前游戏规则设置冷却。当实体不接触下界传送门方块时，此值每游戏刻减1直至0，此时才可以再次使用下界传送门传送。此项不存在时游戏默认为0。 - [图:NBT列表/JSON数组]* *Pos：当前实体的坐标。 - [图:双精度浮点数]：（-30000512≤值≤30000512）X轴坐标。如果此值超过值域，则被强制修改坐标以回到值域。如果为非数（NaN），则加载此实体时会产生错误。 - [图:双精度浮点数]：（-20000000≤值≤20000000）Y轴坐标。如果此值超过值域，则被强制修改坐标以回到值域。如果为非数（NaN），则加载此实体时会产生错误。 - [图:双精度浮点数]：（-30000512≤值≤30000512）Z轴坐标。如果此值超过值域，则被强制修改坐标以回到值域。如果为非数（NaN），则加载此实体时会产生错误。 - [图:NBT列表/JSON数组]* *Rotation：实体的旋转角度，使用角度制。如果角度值为无限或非数（NaN），则对应角度会被修改为0度。 - [图:单精度浮点数]：当前实体以Y轴为中心，与正南方以顺时针方向旋转的视角角度（即偏转角）。如果角度值超出对应值域，则在按照相同朝向重新限制到值域内。 - [图:单精度浮点数]：（-90≤值≤90）当前实体与视角与水平面之间的倾斜角（即俯仰角）。水平面为0，正值表示面朝下方，相反则为上方。如果此值超过值域，则被强制修改以回到值域。 - [图:布尔型]Silent：实体是否不会发出任何声音。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Tags：实体的自定义记分板标签。不超过1024个。 - [图:字符串]：一项记分板标签。 - [图:整型]TicksFrozen：实体的冷冻时间。当实体在细雪中时每刻增加1，离开细雪则每刻减少2。此项不存在时游戏默认为0。 - [图:整型数组]* *UUID：（UUID）实体的UUID。此值无法使用 ``` / data ``` 修改。

各种不同的实体在这个数据格式的基础上，附加了自身额外的信息。下列是Java版中所有实体的数据格式：

## 生物

每个生物都有额外的标签来储存它们的血量、状态、效果。

玩家数据格式见玩家数据格式。

悦灵

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:长整型]* *DuplicationCooldown：悦灵复制的冷却时间。悦灵被复制时此值设为6000游戏刻（5分），每游戏刻减少1直到0。 - [图:NBT列表/JSON数组]*Inventory：已被悦灵拾起的物品列表，此列表最多包含一组物品。当读取时，如果列表数量超过1，则超出范围的物品尝试与范围内的物品合并，如果无法合并则被删除。此处并非玩家给予悦灵的物品，被给予的物品被记录在[图:NBT复合标签/JSON对象]equipment.mainhand中。 - [图:NBT复合标签/JSON对象]：一项物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:NBT复合标签/JSON对象]*listener：悦灵的振动事件监听器。 - - 振动监听器，见Template:Nbt inherit/vibration listener/source

犰狳

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:整型]*scute_time：犰狳掉落犰狳鳞甲的倒计时，每游戏刻减少1。当此值小于1时犰狳掉落犰狳鳞甲，并重置此值到6000游戏刻（5分）-12000游戏刻（10分）之间。 - [图:字符串]* *state：犰狳当前的状态。可以为 ``` idle ``` （未蜷缩）、 ``` rolling ``` （正在蜷缩）和 ``` scared ``` （蜷缩）。

盔甲架

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - [图:整型]* *DisabledSlots：用于禁用某个部位的放置、替换和移除。此值使用按位或进行数据的保存，不同二进制位的含义在下方列出。比如，把值设为16191（0x3F3F）或4144896（0x3F3F00）会禁用所有盔甲的放置、移除和替换。 - [图:布尔型]* *Invisible：表示盔甲架是否隐形。隐形不会影响盔甲架身上物品的显示。 - [图:布尔型]Marker：（默认为 ``` false ``` ）盔甲架是否被当作“标记”。如果为true，盔甲架的碰撞箱会消失，且无法与之进行任何交互。 - [图:布尔型]* *NoBasePlate：表示盔甲架是否不会显示下面的基座。 - [图:NBT复合标签/JSON对象]* *Pose：盔甲架的不同部位的旋转角度，每个身体部分都有三个[图:单精度浮点数]单精度浮点数组成的列表按顺序保存XYZ轴的旋转角度。 - [图:NBT列表/JSON数组]Body：（默认为 ``` [0f, 0f, 0f] ``` ）躯干的角度。 - [图:NBT列表/JSON数组]Head：（默认为 ``` [0f, 0f, 0f] ``` ）头部的角度。 - [图:NBT列表/JSON数组]LeftArm：（默认为 ``` [-10f, 0f, -10f] ``` ）左臂的角度。 - [图:NBT列表/JSON数组]LeftLeg：（默认为 ``` [-1f, 0f, -1f] ``` ）左腿的角度。 - [图:NBT列表/JSON数组]RightArm：（默认为 ``` [-15f, 0f, 10f] ``` ）右臂的角度。 - [图:NBT列表/JSON数组]RightLeg：（默认为 ``` [1f, 0f, 1f] ``` ）右腿的角度。 - [图:布尔型]* *ShowArms：表示盔甲架是否会显示其手臂。如果其手臂不存在，玩家不能对其手持的物品互动。 - [图:布尔型]* *Small：表示盔甲架是否是小型盔甲架。

美西螈

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]* *FromBucket：表示此美西螈是否曾被从桶中放出。如果为true，美西螈不会自然消失。 - [图:整型]* *Variant：美西螈变种的ID。此项实体数据会被视为数据组件axolotl/variant。

蝙蝠

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]* *BatFlags：表示蝙蝠是否正在倒挂在方块下面。

蜜蜂

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source - [图:整型]* *CannotEnterHiveTicks：离蜜蜂能再次进入蜂箱的刻数。 - [图:整型]* *CropsGrownSincePollination：蜜蜂一共促进了多少作物的生长。此值用来限制蜜蜂促进生长作物的次数，当此值大于10时蜜蜂不会再促进生长作物。 - [图:整型数组]flower_pos：储存其盘旋的花的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:布尔型]* *HasNectar：表示蜜蜂是否携带花粉。 - [图:布尔型]* *HasStung：表示蜜蜂是否蜇过玩家或生物。 - [图:整型数组]hive_pos：其蜂箱的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:整型]* *TicksSincePollination：蜜蜂离开蜂箱后未携带花粉的时间。如果[图:NBT复合标签/JSON对象]FlowerPos存在，当此值超过2400游戏刻（2分）时，蜜蜂会尝试飞向对应坐标。

烈焰人

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

旋风人

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

骆驼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:长整型]* *LastPoseTick：骆驼最后一次起身的时间。当此值为负值时骆驼坐下，且其相反数代表开始坐下的时间。

猫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 可驯服动物共通标签，见Template:Nbt inherit/tameable/source - [图:字节型]*CollarColor：（0≤值≤15，默认为14（红色））猫的项圈颜色，颜色取对应染料序号的颜色。未驯服的流浪猫也有此字段，但是不进行渲染。如果设置值超出值域则设置为0（白色）。此项实体数据会被视为数据组件cat/collar。 - [图:字符串]* *sound_variant：（命名空间ID）猫的音效变种。如果设置值无效则设置为 ``` classic ``` 。此项实体数据会被视为数据组件cat/sound_variant。 - [图:字符串]* *variant：（命名空间ID）猫的皮肤。如果设置值无效则设置为 ``` black ``` （西服猫）。此项实体数据会被视为数据组件cat/variant。

洞穴蜘蛛

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

鸡

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:整型]*EggLayTime：距离鸡下一次下蛋的时间。鸡会在此值为0的时候下蛋，然后该值会被随机重置到6000游戏刻（5分）到12000游戏刻（10分）之间。此值不存在时游戏读取时立刻重置此值。 - [图:布尔型]* *IsChickenJockey：表示这只鸡是否为幼年僵尸、幼年尸壳、幼年僵尸村民、幼年溺尸或幼年僵尸猪灵的载具。如果为true，这只鸡可以被自然清除且不再下蛋，在被玩家击杀时会掉落10经验，而不是平时的1-3经验。无论此值为何，骑乘鸡的幼年僵尸依然可以控制这只鸡。 - [图:字符串]* *sound_variant：（命名空间ID）鸡的音效变种。如果设置值无效则设置为 ``` classic ``` 。此项实体数据会被视为数据组件chicken/sound_variant。 - [图:字符串]* *variant：（命名空间ID）鸡的变种。如果设置值无效则设置为 ``` temperate ``` 。此项实体数据会被视为数据组件chicken/variant。

鳕鱼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]* *FromBucket：表示此鳕鱼是否曾被从桶中放出。如果为true，鳕鱼不会自然删除。

铜傀儡

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:长整型]*next_weather_age：（默认为 ``` -1L ``` ）铜傀儡进入下一氧化阶段或转变为铜傀儡像的期限，单位为刻。涂蜡后，此值变为 ``` -2L ``` ，使铜傀儡不再继续氧化或转化。此值为 ``` -1L ``` 、进入下一氧化阶段或除蜡后，此值重置为504000 – 552000间的随机数+所在存档的昼夜更替时间。 - [图:字符串]*weather_state：（默认为 ``` unaffected ``` ）铜傀儡的氧化阶段。可选值为 ``` unaffected ``` 、​ ``` exposed ``` 、​ ``` weathered ``` 和​ ``` oxidized ``` 。

牛

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:字符串]* *sound_variant：（命名空间ID）牛的音效变种。如果设置值无效则设置为 ``` classic ``` 。此项实体数据会被视为数据组件cow/sound_variant。 - [图:字符串]* *variant：（命名空间ID）牛的变种。如果设置值无效则设置为 ``` temperate ``` 。此项实体数据会被视为数据组件cow/variant。

嘎枝

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

苦力怕

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:字节型]*ExplosionRadius：苦力怕爆炸的威力或闪电苦力怕爆炸的威力的一半。不存在此值时游戏默认为3。 - [图:短整型]*Fuse：此苦力怕从引燃到爆炸的时间。当苦力怕的内部爆炸计时器达到此值时苦力怕爆炸。不存在此值时游戏默认为30游戏刻（1.5秒）。 - [图:布尔型]*ignited：表示此苦力怕是否被玩家用物品点燃。 - [图:布尔型]*powered：表示此苦力怕是否为闪电苦力怕。

海豚

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - [图:布尔型]* *GotFish：表示海豚是否从玩家处得到了鱼。 - [图:整型]* *Moistness：（默认为2400）海豚所剩的湿润时间。在水中为2400游戏刻（120秒），不在水中则每游戏刻减少1。如果此项小于等于0时海豚不在水中，那么其每游戏刻会受到1点伤害。

驴

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:布尔型]*ChestedHorse：表示驴身上是否带箱子。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Items：（当[图:布尔型]*ChestedHorse为true时存在并有效）物品栏列表。驴共有15个槽位，超过槽位范围的物品无效。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source

溺尸

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 僵尸共通标签，见Template:Nbt inherit/zombie/source

远古守卫者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

末影龙

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]DragonDeathTime：（默认为0）末影龙死亡计时，用于控制渲染和掉落经验。当此值大于200游戏刻（10秒）时，末影龙被删除。 - [图:整型]DragonPhase：（不小于0且不大于10）控制当前末影龙行动的枚举。从0到10，各个数字分别代表：绕圈（徘徊）、扫射（准备发射火球）、飞至传送门并降落（降落行动的一部分）、停在传送门上（降落行动的一部分）、从传送门起飞（起飞行动的一部分）、降落时吐出龙息、降落时面向玩家并进行龙息攻击、降落时在进行龙息攻击前咆啸、冲向玩家（俯冲攻击）、飞至传送门并死亡、停止末影龙的行动并保持悬停。 - [图:单精度浮点数]*sitting_damage_received：（默认为0）末影龙栖息在末地祭坛上时受到的总伤害量。

末影人

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source - [图:字符串][图:NBT复合标签/JSON对象]carriedBlockState：末影人拿着的方块。 - - 方块状态，见Template:Nbt inherit/block state/source

末影螨

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Lifetime：末影螨已存在的时间。如果[图:布尔型]PersistenceRequired为true，则此值不增加。当此值达到或超过2400游戏刻（120秒）时末影螨会自动删除。

唤魔者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source - [图:整型]* *SpellTicks：下一个法术可以释放的倒计时。当法术释放时设为某个正值，每游戏刻减少1直到0。

青蛙

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:字符串]* *variant：（命名空间ID）青蛙肤色。如果设置值无效则设置为 ``` temperate ``` 。可以为 ``` temperate ``` （温带）、 ``` warm ``` （热带）和 ``` cold ``` （寒带）。此项实体数据会被视为数据组件frog/variant。

狐狸

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]* *Crouching：表示狐狸是否在潜行。 - [图:布尔型]* *Sleeping：表示狐狸是否在睡觉。 - [图:布尔型]* *Sitting：表示狐狸是否坐着。 - [图:NBT列表/JSON数组]* *Trusted：（默认为空列表 ``` [] ``` ）狐狸信任的玩家。此列表最多有两个元素，从列表第三项开始都不会生效。 - [图:整型数组]：信任玩家的UUID。 - [图:字符串]* *Type：狐狸的种类。可设置为 ``` red ``` （红色）或 ``` snow ``` （白色）。此项实体数据会被视为数据组件fox/variant。

恶魂

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:字节型]*ExplosionPower：（默认为1）恶魂发出的火球的爆炸威力。

巨人

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

发光鱿鱼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - [图:整型]* *DarkTicksRemaining：距离发光鱿鱼发光的时间。发光时为0，不发光时为正值。

山羊

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]* *HasLeftHorn：（默认为true）表示此山羊是否有左侧的角。 - [图:布尔型]* *HasRightHorn：（默认为true）表示此山羊是否有右侧的角。 - [图:布尔型]* *IsScreamingGoat：表示此山羊是否为尖叫山羊。

守卫者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

快乐恶魂

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:整型]*still_timeout：快乐恶魂剩余滞空时间。此值小于5且快乐恶魂头顶可以找到有效玩家时，此值被设为10，随后每游戏刻减少1，直至0时恢复控制和移动。

疣猪兽

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]CannotBeHunted：（当此值为true时存在）表示猪灵是否不会攻击这只疣猪兽。 - [图:布尔型]IsImmuneToZombification：（当此值为true时存在）表示疣猪兽是否不会在下界以外的维度中变成僵尸疣猪兽。当此项为true时，[图:整型]TimeInOverworld会被重置为0。 - [图:整型]* *TimeInOverworld：疣猪兽在对其不安全的维度（默认为下界以外的维度）停留的总时间。如果此值大于300游戏刻（15秒），疣猪兽会转化成僵尸疣猪兽。当回到对其安全的维度时此值重置为0。

马

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:整型]* *Variant：马的外观数据。设置为最后8位代表马的类型，在之前的8位为马的花纹。未使用的值会生成白色的马。此项实体数据负责马的类型的部分会被视为数据组件horse/variant。

尸壳

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 僵尸共通标签，见Template:Nbt inherit/zombie/source

幻术师

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source - [图:整型]* *SpellTicks：下一个法术可以释放的倒计时。当法术释放时设为某个正值，每游戏刻减少1直到0。

铁傀儡

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source - [图:布尔型]* *PlayerCreated：表示此铁傀儡是否是被建造产生的。

羊驼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:布尔型]*ChestedHorse：表示羊驼身上是否带箱子。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Items：（当[图:布尔型]*ChestedHorse为true时存在并有效）物品栏列表。羊驼共有3×s（s是[图:整型]* *Strength的值）个槽位，超过槽位范围的物品无效。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:整型]* *Strength：（1≤值≤5）羊驼的“强度”，决定羊驼可以携带的物品数量以及使狼逃离的能力。 - [图:整型]* *Variant：（0≤值≤3）羊驼的类型。从0到3分别对应 ``` creamy ``` 、​ ``` white ``` 、​ ``` brown ``` 和​ ``` gray ``` 。如果此值小于0则被重置为0（ ``` creamy ``` ），如果此值大于3则重置为3（ ``` gray ``` ）。此项实体数据会被视为数据组件llama/variant。

岩浆怪

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Size：（0≤值≤126）岩浆怪的大小，同时影响岩浆怪的最大生命值、移动速度和攻击力。如果设置小于0则重置为0，大于126则重置为126。 - [图:布尔型]* *wasOnGround：表示岩浆怪在上一游戏刻是否接触地面。

玩家模型

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]description：（文本组件，默认为 ``` {"translate": "entity.minecraft.mannequin.label"} ``` ）在玩家模型的 ``` below_name ``` 记分板显示位置处显示的文本。 - [图:布尔型]hide_description：（默认为 ``` false ``` ）玩家模型是否不显示 ``` below_name ``` 记分板显示位置处的文本。 - [图:NBT列表/JSON数组]* *hidden_layers：不渲染的外层皮肤列表。 - [图:字符串]：要隐藏的一个外层皮肤。取值可以为 ``` cape ``` （披风）、 ``` jacket ``` （外套）、 ``` left_sleeve ``` （左袖）、 ``` right_sleeve ``` （右袖）、 ``` left_pants_leg ``` （左裤腿）、 ``` right_pants_leg ``` （右裤腿）和 ``` hat ``` （帽子）。 - [图:布尔型]* *immovable：（默认为 ``` false ``` ）玩家模型是否不能被移动。 - [图:字符串]* *main_hand：玩家模型的主手，可以为 ``` left ``` 或 ``` right ``` 。 - [图:字符串]* *pose：（默认为 ``` standing ``` ）玩家模型的姿势。取值可以为 ``` standing ``` （站立）、 ``` crouching ``` （潜行）、 ``` swimming ``` （游泳）、 ``` fall_flying ``` （滑翔）和 ``` sleeping ``` （睡觉）。 - [图:字符串][图:NBT复合标签/JSON对象]* *profile：玩家模型的档案数据，影响其皮肤渲染。此项实体数据会被视为数据组件profile。 - - 游戏档案，见Template:Nbt inherit/resolvable profile/source

哞菇

- [图:NBT复合标签/JSON对象] 实体数据值 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:NBT列表/JSON数组]stew_effects：棕色哞菇产生的谜之炖菜的状态效果列表。如果棕色哞菇没有保存状态效果则不存在此标签。 - [图:NBT复合标签/JSON对象]：一项状态效果。 - [图:整型]duration：（默认为160游戏刻（8秒））状态效果的持续时间。 - [图:字符串]* *id：状态效果的命名空间ID。 - [图:字符串]* *Type：哞菇的种类。可以为 ``` red ``` （红色）或 ``` brown ``` （棕色）。如果设置值无效则重置为 ``` red ``` （红色）。此项实体数据会被视为数据组件mooshroom/variant。

骡

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:布尔型]*ChestedHorse：表示骡身上是否带箱子。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Items：（当[图:布尔型]*ChestedHorse为true时存在并有效）物品栏列表。骡共有15个槽位，超过槽位范围的物品无效。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source

鹦鹉螺

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 可驯服动物共通标签，见Template:Nbt inherit/tameable/source

豹猫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]* *Trusting：表示豹猫是否信任玩家。

熊猫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:字符串]* *HiddenGene：熊猫拥有的隐藏基因，可以转移到其子代。 - [图:字符串]* *MainGene：熊猫拥有的主要基因，可以转移到其子代。

### 基因

主条目：熊猫/DV

鹦鹉

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 可驯服动物共通标签，见Template:Nbt inherit/tameable/source - [图:整型]* *Variant：（0≤值≤4）鹦鹉的颜色。从0到4分别为红色、蓝色、绿色、青色和灰色。如果设置值小于0则重置为0（红色），大于4则重置为4（灰色）。此项实体数据会被视为数据组件parrot/variant。

幻翼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型数组]*anchor_pos：幻翼在非攻击状态下会尝试围绕着此坐标盘旋飞行，在每次俯冲结束后，此值都会重置到目标玩家正上方的某个高度。内部的三分个整数依次对应X、Y、Z坐标，其中Y坐标永远不会低于此维度的海平面高度。 - [图:整型]* *size：（0≤值≤64）幻翼的大小。影响幻翼的攻击伤害，每增加1攻击伤害也加1。自然生成的幻翼大小值为0。

猪

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:字符串]* *sound_variant：（命名空间ID）猪的音效变种。如果设置值无效则设置为 ``` classic ``` 。此项实体数据会被视为数据组件pig/sound_variant。 - [图:字符串]* *variant：（命名空间ID）猪的变种。如果设置值无效则设置为 ``` temperate ``` 。此项实体数据会被视为数据组件pig/variant。

猪灵

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]CannotHunt：（此值为true时存在）表示猪灵是否不会攻击疣猪兽。 - [图:NBT列表/JSON数组]* *Inventory：猪灵存储的物品栏，此标签最多容纳8组物品。当读取时，如果列表数量超过8，则超出范围的物品尝试与范围内的物品合并，如果无法合并则被删除。 - [图:NBT复合标签/JSON对象]：物品栏中的一个物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:布尔型]IsBaby：（此值为true时存在）表示此猪灵是否为幼年个体。 - [图:布尔型]IsImmuneToZombification：（此值为true时存在）表示猪灵是否不会在下界以外的维度中变成僵尸猪灵。当此项为true时，[图:整型]TimeInOverworld会被重置为0且不会增加。 - [图:整型]* *TimeInOverworld：猪灵在对其不安全的维度（默认为下界以外的维度）停留的总时间。如果此值大于300游戏刻（15秒），猪灵会转化成僵尸猪灵。当回到对其安全的维度时此值重置为0。

猪灵蛮兵

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]IsImmuneToZombification：（此值为true时存在）表示猪灵蛮兵在主世界是否不会变成僵尸猪灵。当此项为true时，[图:整型]TimeInOverworld会被重置为0且不会增加。 - [图:整型]* *TimeInOverworld：猪灵蛮兵在对猪灵不安全的维度（默认为下界以外的维度）停留的总时间。如果此值大于300游戏刻（15秒），猪灵蛮兵会转化成僵尸猪灵。当回到对猪灵安全的维度时此值重置为0。

掠夺者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source - [图:NBT列表/JSON数组]* *Inventory：掠夺者存储的物品栏，此标签最多容纳5组物品。当读取时，如果列表数量超过5，则超出范围的物品尝试与范围内的物品合并，如果无法合并则被删除。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source

北极熊

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source

河豚

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]* *FromBucket：表示此河豚是否曾被从桶中放出。如果为true，河豚不会自然删除。 - [图:整型]* *PuffState：（0≤值≤2）河豚的膨胀状态。0表示河豚未膨胀，1表示半膨胀，2表示完全膨胀，超出值域的值效果等同于完全膨胀。

兔子

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:整型]* *MoreCarrotTicks：兔子吃胡萝卜植株的冷却时间。当兔子吃下一个胡萝卜植株时，此值被设置为40。此值每游戏刻减少0-2，直到此值降为0，此时兔子才可以继续吃胡萝卜植株。 - [图:整型]* *RabbitType：决定兔子的皮肤，同时也影响兔子的行为。可以为 ``` 0 ``` （棕色）、 ``` 1 ``` （白色）、 ``` 2 ``` （黑色）、 ``` 3 ``` （黑白斑点）、 ``` 4 ``` （金黄色）、 ``` 5 ``` （棕白色）和 ``` 99 ``` （杀手兔）。如果设置为其他值，则自动设置为 ``` 0 ``` （棕色）。此项实体数据会被视为数据组件rabbit/variant。

劫掠兽

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source - [图:整型]* *AttackTick：当前劫掠兽攻击冷却时间。 - [图:整型]* *RoarTick：当前劫掠兽咆哮冷却时间。 - [图:整型]* *StunTick：当前劫掠兽眩晕冷却时间。

鲑鱼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]* *FromBucket：表示此鲑鱼是否曾被从桶中放出。如果为true，鲑鱼不会自然删除。 - [图:字符串]* *type：鲑鱼的类型。可以为 ``` small ``` （小型）、 ``` medium ``` （中型）或 ``` large ``` （大型）。此项实体数据会被视为数据组件salmon/size。

绵羊

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:字节型]* *Color：（0≤值≤15）绵羊的颜色，取对应染料序号的颜色。如果设置此值时不在值域内，则修改为0（白色）。 - [图:布尔型]* *Sheared：表示绵羊是否被剪毛。此项实体数据会被视为数据组件sheep/color。

潜影贝

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:字节型]* *AttachFace：（0≤值≤5）潜影贝所附着方块的方向。从0到5分别对应下上北南西东，如果超过值域则对6取余并取绝对值后对应方向。 - [图:字节型]* *Color：（0≤值≤16，默认为16）潜影贝的颜色。当值不小于0且不大于15时，颜色取对应染料序号的颜色；如果大于15则设置为16（默认颜色）；其他情况为0（白色）。此项实体数据在非默认颜色时会被视为数据组件shulker/variant，在默认颜色时不存在该组件。 - [图:字节型]* *Peek：潜影贝壳打开的高度，此值与0.01相乘可以得出潜影贝开壳的具体高度。没有开壳时为0，完全开壳时为100。

蠹虫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

骷髅

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]StrayConversionTime：骷髅转化为流浪者前要经历的时间。骷髅在细雪中140游戏刻（7秒）后，此值被设置为300游戏刻（15秒），并每游戏刻减少1，如果脱离细雪则此值无效。当此值被减少到不大于0时，骷髅被转化为流浪者。如果不处于细雪中也没有在转化过程中，此值为-1。

骷髅马

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:布尔型]* *SkeletonTrap：表示这匹骷髅马是否是一匹骷髅陷阱马。 - [图:整型]* *SkeletonTrapTime：骷髅陷阱存在的时间。当[图:布尔型]SkeletonTrap值为true时，此值每游戏刻增加1。当值达到18000游戏刻（15分）时如果[图:布尔型]SkeletonTrap值为true则骷髅马自动删除。

史莱姆

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Size：（0≤值≤126）史莱姆的大小，同时影响史莱姆的最大生命值、移动速度和攻击力。如果设置小于0则重置为0，大于126则重置为126。 - [图:布尔型]* *wasOnGround：表示史莱姆在上一游戏刻是否接触地面。

雪傀儡

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]*Pumpkin：（默认为true）表示雪傀儡是否戴有南瓜头盔。

嗅探兽

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source

蜘蛛

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

鱿鱼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source

流浪者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

炽足兽

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source

硫方怪

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - [图:整型]* *Size：（0≤值≤126）硫方怪的大小，同时影响硫方怪的最大生命值、移动速度和攻击力。如果设置小于0则重置为0，大于126则重置为126。 - [图:布尔型]* *wasOnGround：表示硫方怪在上一游戏刻是否接触地面。 - [图:整型]*pickup_timer：（默认为0）硫方怪可以捡起物品实体的倒计时。此值不小于0时每刻减少1，且硫方怪也不会搜寻并捡起物品实体。 - [图:布尔型]* *FromBucket：表示此硫方怪是否曾被从桶中放出。如果为true，硫方怪不会自然删除。 - [图:整型]fuse：（默认为-1）硫方怪在爆炸之前要经过的时间，小于0的值会禁用爆炸。

蝌蚪

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Age：该蝌蚪的年龄，每游戏刻增加1。当大于等于24000游戏刻（20分）时，蝌蚪会长大成青蛙。 - [图:布尔型]* *AgeLocked：表示蝌蚪的年龄是否不会随时间自然增长。 - [图:布尔型]* *FromBucket：表示此蝌蚪是否曾被从桶中放出。如果为true，蝌蚪不会自然删除。

行商羊驼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source - [图:布尔型]*ChestedHorse：表示行商羊驼身上是否带箱子。此项不存在时游戏默认为false。 - [图:NBT列表/JSON数组]Items：（当[图:布尔型]*ChestedHorse为true时存在并有效）物品栏列表。行商羊驼共有3×s（s是[图:整型]* *Strength的值）个槽位，超过槽位范围的物品无效。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:整型]* *Strength：（1≤值≤5）行商羊驼的“强度”，决定行商羊驼可以携带的物品数量以及使狼逃离的能力。 - [图:整型]* *Variant：（0≤值≤3）行商羊驼的类型。从0到3分别对应 ``` creamy ``` 、​ ``` white ``` 、​ ``` brown ``` 和​ ``` gray ``` 。如果此值小于0则被重置为0（ ``` creamy ``` ），如果此值大于3则重置为3（ ``` gray ``` ）。此项实体数据会被视为数据组件llama/variant。 - [图:整型]*DespawnDelay：（默认为47999）距离行商羊驼被删除的时间。

热带鱼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]* *FromBucket：表示此热带鱼是否曾被从桶中放出。如果为true，热带鱼不会自然删除。 - [图:整型]* *Variant：决定热带鱼的外观。此值分为4部分：从低到高字节分别代表热带鱼的体型、花纹、颜色和花纹颜色。体型只有两种，0代表大型，1代表小型。花纹共有6种，与体型结合共有12种。如果体型和花纹有一个是无效的，就会使用石首类变种。颜色和花纹颜色与对应染料序号的颜色一致。此项实体数据对应颜色、体型和花纹、花纹颜色的三部分会被分别视为数据组件tropical_fish/base_color、tropical_fish/pattern和tropical_fish/pattern_color。

海龟

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - [图:布尔型]* *has_egg：表示这只海龟是否将会产卵。

恼鬼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]bound_pos：恼鬼的游走中心，内部的三个整数依次对应X、Y、Z坐标。恼鬼在空闲时会在以此坐标为中心大小为15×11×15的空间四处飘浮。如果此恼鬼是由唤魔者召唤的则此值为召唤时的位置，否则为第一次开始游走的位置。 - [图:整型]life_ticks：伤害倒计时，每游戏刻减少1。当此值达到0时，恼鬼会受到1点饥饿伤害，并将此值重置为20游戏刻（1秒）。如果恼鬼可以长期存在则此项不存在。 - [图:整型数组]owner：生成该恼鬼的AI生物的UUID，此项存在时恼鬼会与该生物有共同的敌对目标。

村民

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - [图:布尔型]AssignProfessionWhenSpawned：（为false时不存在）表示村民是否在生成时就已经赋予职业。 - [图:字节型]*FoodLevel：（默认为0）当前村民的食物等级。只有当食物等级与村民物品栏内食物点数之和大于12时村民才会有意愿繁殖。 - [图:NBT列表/JSON数组]* *Inventory：村民存储的物品栏，此标签最多容纳8组物品。当读取时，如果列表数量超过8，则超出范围的物品尝试与范围内的物品合并，如果无法合并则被删除。 - [图:NBT复合标签/JSON对象]：物品栏中的一个物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:NBT列表/JSON数组]Gossips：村民存储的言论信息。 - [图:NBT复合标签/JSON对象]：一条言论。 - [图:整型数组]* *Target：引发言论的玩家的UUID。 - [图:字符串]* *Type：言论的类型。可以是 ``` major_negative ``` 、​ ``` minor_negative ``` 、​ ``` major_positive ``` 、​ ``` minor_positive ``` 和​ ``` trading ``` 。 - [图:整型]* *Value：（值>0）此言论的强度。 - [图:长整型]* *LastGossipDecay: （默认为0）此村民最后一次衰减言论值的时间。两次衰减时间不会小于24000游戏刻（20分）。 - [图:长整型]* *LastRestock: （默认为0）此村民最后一次前往工作站点补货的时间。两次补货时间不会小于2400游戏刻（120秒）。 - [图:NBT复合标签/JSON对象]Offers：交易数据。在玩家第一次打开交易菜单时产生。 - [图:NBT列表/JSON数组]Recipes：交易列表。 - [图:NBT复合标签/JSON对象]：单个交易选项。 - [图:NBT复合标签/JSON对象]* *buy：第一个收购物品。如果物品基础数量为n，则收购数量为n+max(0,⌊ndm⌋)+s，其中d为[图:整型]demand，m为[图:单精度浮点数]priceMultiplier，s为[图:整型]specialPrice。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:NBT复合标签/JSON对象]buyB：（默认为空）第二个收购物品。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:整型]demand：（默认为0）此项交易的需求，影响第一个收购物品的数量。当生物补货时更新此字段。如果原值为d，则更新之后的值d′=d+2u−m，其中u是[图:整型]uses，m是[图:整型]maxUses。 - [图:整型]maxUses：（默认为4）表示在交易选项失效前能进行的最大交易次数。 - [图:单精度浮点数]priceMultiplier：（默认为0）表示影响收购数量的乘数。 - [图:布尔型]rewardExp：（默认为true）表示交易是否会提供经验球。 - [图:NBT复合标签/JSON对象]* *sell：出售的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型]specialPrice：（默认为0）调节第一个收购物品的数量。对于村民，此项受到村庄英雄和言论机制的共同降价影响。 - [图:整型]uses：（默认为0）已经交易的次数。如果此值大于[图:整型]maxUses，此交易失效。 - [图:整型]xp：（默认为1）生物从此交易选项中能获得的经验值。 - [图:整型]* *RestocksToday：（默认为0）村民今天补货的次数。村民每天最多补货两次。 - [图:NBT复合标签/JSON对象]*VillagerData：关于村民职业的信息。 - [图:整型]level：（默认为1）村民当前交易选项等级，该值影响村民交易选项和徽章的纹理渲染。如果该值大于5，村民将无法升级也无法解锁新的交易。 - [图:字符串]*profession：村民的职业，是一个命名空间ID。如果不存在或无效则设置为 ``` minecraft:none ``` 。 - [图:字符串]*type：村民的种类，是一个命名空间ID。如果不存在或无效则设置为 ``` minecraft:plains ``` 。此项实体数据会被视为数据组件villager/variant。 - [图:布尔型]VillagerDataFinalized：（默认为 ``` false ``` ）村民数据是否初始化完毕。此值为 ``` false ``` 时游戏会重置村民生物群系着装数据，并设置为 ``` true ``` 。 - [图:整型]*Xp：（默认为0）此村民当前的经验值。

卫道士

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source - [图:布尔型]Johnny：（此值为true时存在）表示卫道士是否表现出Johnny的行为。如果此值为false，即使卫道士名称是“Johnny”也不会有Johnny的行为。

流浪商人

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Age：此项对流浪商人没有用处。 - [图:整型]*DespawnDelay：（默认为0）流浪商人强制消失前剩余的时间。如果此数值小于等于0则流浪商人不会强制消失。如果流浪商人正在与玩家交易则此值不减少。 - [图:整型]* *ForcedAge：此项对流浪商人没有用处。 - [图:NBT列表/JSON数组]* *Inventory：流浪商人的物品栏，此标签最多容纳8组物品。当读取时，如果列表数量超过8，则超出范围的物品尝试与范围内的物品合并，如果无法合并则被删除。 - [图:NBT复合标签/JSON对象]：物品栏中的一个物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:NBT复合标签/JSON对象]Offers：交易数据。在玩家第一次打开交易菜单时产生。 - [图:NBT列表/JSON数组]Recipes：交易列表。 - [图:NBT复合标签/JSON对象]：单个交易选项。 - [图:NBT复合标签/JSON对象]* *buy：第一个收购物品。如果物品基础数量为n，则收购数量为n+max(0,⌊ndm⌋)+s，其中d为[图:整型]demand，m为[图:单精度浮点数]priceMultiplier，s为[图:整型]specialPrice。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:NBT复合标签/JSON对象]buyB：（默认为空）第二个收购物品。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:整型]demand：（默认为0）此项交易的需求，影响第一个收购物品的数量。当生物补货时更新此字段。如果原值为d，则更新之后的值d′=d+2u−m，其中u是[图:整型]uses，m是[图:整型]maxUses。 - [图:整型]maxUses：（默认为4）表示在交易选项失效前能进行的最大交易次数。 - [图:单精度浮点数]priceMultiplier：（默认为0）表示影响收购数量的乘数。 - [图:布尔型]rewardExp：（默认为true）表示交易是否会提供经验球。 - [图:NBT复合标签/JSON对象]* *sell：出售的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型]specialPrice：（默认为0）调节第一个收购物品的数量。对于村民，此项受到村庄英雄和言论机制的共同降价影响。 - [图:整型]uses：（默认为0）已经交易的次数。如果此值大于[图:整型]maxUses，此交易失效。 - [图:整型]xp：（默认为1）生物从此交易选项中能获得的经验值。 - [图:整型数组]wander_target：流浪商人的目的地。内部的三个整数分别代表了位置的XYZ坐标值。

监守者

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:NBT复合标签/JSON对象]*anger：监守者的愤怒数据。 - [图:NBT列表/JSON数组]suspects：激怒监守者的可疑实体的列表。 - [图:NBT复合标签/JSON对象]：一个可疑实体及对应的愤怒值。 - [图:整型]* *anger：（值≥0）愤怒值。监守者对一个实体的最大愤怒值为150，每20游戏刻（1秒）减少1。 - [图:整型数组]* *uuid：与此愤怒值对应的实体的UUID。 - [图:NBT复合标签/JSON对象]*listener：与监守者绑定的振动监听器。 - - 振动监听器，见Template:Nbt inherit/vibration listener/source

女巫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 袭击者共通标签，见Template:Nbt inherit/raidable/source

凋灵

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:整型]* *Invul：在凋灵初次生成后无敌状态的剩余时间。不大于0时代表凋灵不处于无敌状态。

凋灵骷髅

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source

狼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 可驯服动物共通标签，见Template:Nbt inherit/tameable/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source - [图:字节型]*CollarColor：（0≤值≤15，默认为14（红色））狼项圈的颜色，颜色取对应染料序号的颜色。即使是野生的狼也仍然存在此标签，但项圈不会渲染。如果设置值超出值域则设置为0（白色）。此项实体数据会被视为数据组件wolf/collar。 - [图:字符串]* *sound_variant：（命名空间ID）狼的音效变种。如果设置值无效则设置为 ``` classic ``` 。此项实体数据会被视为数据组件wolf/sound_variant。 - [图:字符串]* *variant：（命名空间ID）狼的变种。如果设置值无效则设置为 ``` pale ``` 。此项实体数据会被视为数据组件wolf/variant。

僵尸

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 僵尸共通标签，见Template:Nbt inherit/zombie/source

僵尸马

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 马类共通标签，见Template:Nbt inherit/horse/source

僵尸鹦鹉螺

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 可驯服动物共通标签，见Template:Nbt inherit/tameable/source - [图:字符串]* *variant：僵尸鹦鹉螺的变种，不存在或无效时默认为 ``` temperate ``` 。

僵尸猪灵

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 僵尸共通标签，见Template:Nbt inherit/zombie/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source

僵尸村民

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 僵尸共通标签，见Template:Nbt inherit/zombie/source - [图:整型数组]ConversionPlayer：治疗僵尸村民的玩家的UUID。 - [图:整型]ConversionTime：僵尸村民转化为村民的倒计时。如果没有开始转化为村民，此值为-1。 - [图:NBT复合标签/JSON对象]Offers：交易数据。在玩家第一次打开交易菜单时产生。 - [图:NBT列表/JSON数组]Recipes：交易列表。 - [图:NBT复合标签/JSON对象]：单个交易选项。 - [图:NBT复合标签/JSON对象]* *buy：第一个收购物品。如果物品基础数量为n，则收购数量为n+max(0,⌊ndm⌋)+s，其中d为[图:整型]demand，m为[图:单精度浮点数]priceMultiplier，s为[图:整型]specialPrice。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:NBT复合标签/JSON对象]buyB：（默认为空）第二个收购物品。 - [图:字符串]* *id：物品的命名空间ID，不允许为空气（ ``` air ``` ）。 - [图:NBT复合标签/JSON对象]components：（默认为空）检查收购物品的额外信息。 - [图:任意类型]<物品堆叠组件>：检查指定的物品堆叠组件。当物品与指定的物品堆叠组件限制相同时检查才能成功。 - 见物品堆叠组件。 - [图:整型]count：（值>0，默认为1）收购物品的基础数量。 - [图:整型]demand：（默认为0）此项交易的需求，影响第一个收购物品的数量。当生物补货时更新此字段。如果原值为d，则更新之后的值d′=d+2u−m，其中u是[图:整型]uses，m是[图:整型]maxUses。 - [图:整型]maxUses：（默认为4）表示在交易选项失效前能进行的最大交易次数。 - [图:单精度浮点数]priceMultiplier：（默认为0）表示影响收购数量的乘数。 - [图:布尔型]rewardExp：（默认为true）表示交易是否会提供经验球。 - [图:NBT复合标签/JSON对象]* *sell：出售的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型]specialPrice：（默认为0）调节第一个收购物品的数量。对于村民，此项受到村庄英雄和言论机制的共同降价影响。 - [图:整型]uses：（默认为0）已经交易的次数。如果此值大于[图:整型]maxUses，此交易失效。 - [图:整型]xp：（默认为1）生物从此交易选项中能获得的经验值。 - [图:NBT列表/JSON数组]Gossips：僵尸村民存储的言论信息。 - [图:NBT复合标签/JSON对象]：一条言论。 - [图:整型数组]* *Target：引发言论的玩家的UUID。 - [图:字符串]* *Type：言论的类型。可以是 ``` major_negative ``` 、​ ``` minor_negative ``` 、​ ``` major_positive ``` 、​ ``` minor_positive ``` 和​ ``` trading ``` 。 - [图:整型]* *Value：（值>0）此言论的强度。 - [图:NBT复合标签/JSON对象]*VillagerData：关于村民职业的信息。 - [图:整型]level：（默认为1）村民当前交易选项等级，该值影响村民交易选项和徽章的纹理渲染。如果该值大于5，村民将无法升级也无法解锁新的交易。 - [图:字符串]*profession：村民的职业，是一个命名空间ID。如果不存在或无效则设置为 ``` minecraft:none ``` 。 - [图:字符串]*type：村民的种类，是一个命名空间ID。如果不存在或无效则设置为 ``` minecraft:plains ``` 。此项实体数据会被视为数据组件villager/variant。 - [图:布尔型]VillagerDataFinalized：（默认为 ``` false ``` ）村民数据是否初始化完毕。此值为 ``` false ``` 时游戏会重置僵尸村民的生物群系着装数据和职业数据，并设置为 ``` true ``` 。 - [图:整型]*Xp：（默认为0）此僵尸村民当前的经验值。

僵尸疣猪兽

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - [图:布尔型]IsBaby：（此值为true时存在）表示此僵尸疣猪兽是否为幼年个体。

## 弹射物

箭

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 箭类弹射物共通标签，见Template:Nbt inherit/arrow/source

末影龙火球

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 火球类弹射物共通标签，见Template:Nbt inherit/fireball/source

鸡蛋

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

末影珍珠

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

附魔之瓶

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

火球

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 火球类弹射物共通标签，见Template:Nbt inherit/fireball/source - [图:字节型]*ExplosionPower：火球的爆炸威力大小。此项不存在时游戏默认为1。 - [图:NBT复合标签/JSON对象]*Item：实体渲染时使用的物品。此项不存在时使用火焰弹物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source

钓鱼竿浮漂

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source

滞留药水

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

羊驼唾沫

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source

喷溅药水

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

潜影弹

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - [图:整型]Dir：（0≤值≤5）潜影弹正在移动的方向。从0到5分别对应下上北南西东，如果超过值域则对6取余并取绝对值后对应方向。 - [图:整型]* *Steps：下次强制改变移动方向的倒计时，即潜影弹在一个方向上能移动的最大“步数”。 - [图:整型数组]Target：潜影弹目标的UUID。 - [图:双精度浮点数]* *TXD：潜影弹直线飞行的向量X轴上的分量。 - [图:双精度浮点数]* *TYD：潜影弹直线飞行的向量Y轴上的分量。 - [图:双精度浮点数]* *TZD：潜影弹直线飞行的向量Z轴上的分量。

小火球

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 火球类弹射物共通标签，见Template:Nbt inherit/fireball/source - [图:NBT复合标签/JSON对象]*Item：实体渲染时使用的物品。此项不存在时使用火焰弹物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source

雪球

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 投掷物弹射物共通标签，见Template:Nbt inherit/item projectile/source

光灵箭

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 箭类弹射物共通标签，见Template:Nbt inherit/arrow/source - [图:整型]*Duration：发光效果的持续时间，以刻为单位。此值不存在时默认为200游戏刻（10秒）。

三叉戟

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 箭类弹射物共通标签，见Template:Nbt inherit/arrow/source - [图:布尔型]* *DealtDamage：表示此三叉戟是否已经攻击过实体或落地超过4游戏刻（0.2秒）。如果此值为true，则此三叉戟不会与其他实体进行碰撞检测，三叉戟忠诚魔咒在这时才会生效。

风弹

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 火球类弹射物共通标签，见Template:Nbt inherit/fireball/source

凋灵之首

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - - 火球类弹射物共通标签，见Template:Nbt inherit/fireball/source - [图:布尔型]* *dangerous：表示此凋灵之首是否为蓝色凋灵之首。

## 交通工具

船

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:整型数组][图:NBT复合标签/JSON对象]leash：二选一，代表船目前是否被拴绳拴住与被拴住时的信息。如果没有被拴住则不存在此标签。 - - 当船被拴绳拴在一个栅栏上时，此标签为[图:整型数组]整型数组，内部的三个整数分别代表了位置的XYZ坐标值。 - - 当船被另一个实体用拴绳拴住时，此标签为[图:NBT复合标签/JSON对象]复合标签，附加的标签如下： - [图:整型数组]* *UUID：拴绳连接到的实体的UUID。

运输船

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 容器运输实体共通标签，见Template:Nbt inherit/container entity/source - [图:整型数组][图:NBT复合标签/JSON对象]leash：二选一，代表运输船目前是否被拴绳拴住与被拴住时的信息。如果没有被拴住则不存在此标签。 - - 当运输船被拴绳拴在一个栅栏上时，此标签为[图:整型数组]整型数组，内部的三个整数分别代表了位置的XYZ坐标值。 - - 当运输船被另一个实体用拴绳拴住时，此标签为[图:NBT复合标签/JSON对象]复合标签，附加的标签如下： - [图:整型数组]* *UUID：拴绳连接到的实体的UUID。

矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source

运输矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - - 容器运输实体共通标签，见Template:Nbt inherit/container entity/source

命令方块矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - [图:字符串]* *Command：命令方块矿车中的命令。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件，默认为“@”）命令方块矿车的自定义名称。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]LastOutput：（文本组件，当[图:布尔型]*TrackOutput为true时存在并有效）上一条命令的输出。游戏规则“广播命令方块输出”（ ``` command_block_output ``` ）为false时依旧会储存。 - [图:长整型]LastExecution：（当[图:布尔型]*UpdateLastExecution为true时存在并有效）上一条命令执行的时间戳。 - [图:整型]* *SuccessCount：命令执行的成功次数，影响用红石比较器输出的模拟信号强度。只在命令方块矿车用激活铁轨激活后更新。 - [图:布尔型]*TrackOutput：表示是否储存上一条命令的输出，在GUI中点击"上一个输出"文本框旁的按钮进行开关。按钮上的标志指示出目前的状态：O为true，X为false。当此项不存在时游戏默认为 ``` true ``` 。 - [图:布尔型]*UpdateLastExecution：表示是否储存上一条命令执行的时间戳。当此项不存在时游戏默认为 ``` true ``` 。

动力矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - [图:短整型]* *Fuel：直到矿车燃料耗尽所用的时间。 - [图:双精度浮点数]* *PushX：沿X轴的动力，用于流畅地加速/减速。 - [图:双精度浮点数]* *PushZ：沿Z轴的动力，用于流畅地加速/减速。

漏斗矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - - 容器运输实体共通标签，见Template:Nbt inherit/container entity/source - [图:布尔型]*Enabled：表示漏斗矿车是否能将物品吸取至自己的物品栏里。此项不存在时游戏默认为 ``` true ``` 。

刷怪笼矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - - 刷怪笼共通标签，见Template:Nbt inherit/spawner/source

TNT矿车

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 矿车共通标签，见Template:Nbt inherit/minecart/source - [图:单精度浮点数]explosion_power：（默认为4）TNT矿车的基础爆炸威力b。 - [图:单精度浮点数]explosion_speed_factor：（默认为1）TNT矿车的附加爆炸威力s。设基础威力增加量为a，那么最终的爆炸威力为[b,b+1.5sa)区间内的随机浮点数。 - [图:整型]*fuse：（点燃时默认为80，单位为刻，即4秒）距离爆炸的倒计时，未点燃时为-1。设置此值为负数等于未点燃，设置为正数则被认为点燃，为0时爆炸。如果此值不存在则游戏默认为-1。

## 其他

区域效果云

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:整型]* *Age：区域效果云当前已存在的时间。 - [图:NBT复合标签/JSON对象]custom_particle：区域效果云的所使用的自定义粒子。指定带颜色粒子选项粒子时会忽略药水效果定义的颜色。 - 见粒子数据格式。 - [图:整型]* *Duration：（默认为-1）区域效果云的持续时间。如果[图:整型]Age大于[图:整型]WaitTime与此值之和，或此值小于等于0且不为-1，则无论半径为何，区域效果云都会立刻删除。此值为-1时区域效果云永不自然删除。 - [图:整型]* *DurationOnUse：对生物施加状态效果后，区域效果云持续时间的变化量。正常情况下为负值。 - [图:整型数组]Owner：区域效果云创建者的UUID。 - [图:字符串][图:NBT复合标签/JSON对象]potion_contents：药水效果信息。可以为一个药水效果的命名空间ID，也可以指定详细的药水效果数据。此项实体数据会被视为数据组件potion_contents。 - [图:整型]custom_color：区域效果云默认的粒子颜色。只使用后24位，每个颜色通道占用8位，按RGB依次存储。 - [图:NBT列表/JSON数组]custom_effects：区域效果云的自定义状态效果。 - [图:NBT复合标签/JSON对象]：一项状态效果。 - - 状态效果，见Template:Nbt inherit/effect/source - [图:字符串]custom_name：对区域效果云没有任何用处。代表生成此区域效果云的滞留药水的自定义名称后缀。 - [图:字符串]potion：药水效果的命名空间ID，影响区域效果云的药水效果和粒子颜色。 - [图:单精度浮点数]potion_duration_scale：药水效果时长缩放系数。不存在此项时默认为1.0。此项实体数据会被视为数据组件potion_duration_scale。 - [图:单精度浮点数]* *Radius：（不大于32且不小于0）区域效果云的半径。 - [图:单精度浮点数]* *RadiusOnUse：每次对一个生物施加状态效果后区域效果云半径的变化量。正常情况下为负值。 - [图:单精度浮点数]* *RadiusPerTick：区域效果云半径每游戏刻的变化量。正常情况下为负值。 - [图:整型]* *ReapplicationDelay：对同一个生物再次施加状态效果的冷却时间。 - [图:整型]* *WaitTime：区域效果云生效前的等待时间。如果[图:整型]Age不大于此值，则区域效果云产生黑色的粒子效果，且不会对在其中的生物施加状态效果。

展示实体

- - [图:字符串]*billboard：（默认为 ``` fixed ``` ）展示实体面朝玩家渲染时的固定轴。可以为 ``` fixed ``` （固定垂直和水平轴）、 ``` vertical ``` （固定垂直轴）、 ``` horizontal ``` （固定水平轴）和 ``` center ``` （按照中心旋转跟随玩家视角）。 - [图:NBT复合标签/JSON对象]brightness：使用指定值覆盖原来的渲染亮度值。如果未指定此标签，则使用当前实体所在位置的亮度。 - [图:整型]block：渲染使用的方块光照等级，取值为0-15。 - [图:整型]sky：渲染使用的天空光照等级，取值为0-15。 - [图:整型]glow_color_override：（默认为-1）覆盖发光边框颜色，如果为-1则使用展示实体所在队伍的颜色。格式为( 红 << 16) + ( 绿 << 8) + 蓝。 - [图:单精度浮点数]*height：（默认为0）展示实体的剔除判定箱高度。坐标满足 ``` y ``` 到 ``` y+height ``` 的部分作为剔除判定箱范围，如果玩家的视锥内无法与剔除判定箱相交，则实体会被剔除而不可见。如果设置为0则永远不进行剔除。 - [图:单精度浮点数]*width：（默认为0）展示实体的剔除判定箱宽度。水平方向上距离实体中心 ``` width/2 ``` 部分作为剔除判定箱范围，如果玩家的视锥内无法与剔除判定箱相交，则实体会被剔除而不可见。如果设置为0则永远不进行剔除。 - [图:单精度浮点数]*shadow_radius：（可插值，默认为0）实体阴影半径。当值超过64时效果与64相同，小于等于0则不显示阴影。 - [图:单精度浮点数]*shadow_strength：（可插值，默认为1）控制实体阴影的不透明度。实体阴影透明度随玩家到方块表面的距离而变化。 - [图:整型]start_interpolation：（不能导出和保存，仅可以加载或使用 ``` / data ``` 修改）开始插值前的延时。在此标签被设置后才会开始插值。若为0，则立即开始插值。 - [图:整型]*interpolation_duration：（默认为0）展示实体渲染变换发生改变时的插值时间，单位为游戏刻。 - [图:整型]*teleport_duration：（默认为0）展示实体位置与视线旋转发生改变时的插值时间，单位为游戏刻。若为0，则位置和视线会立刻改变。 - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]*transformation：（可插值，默认为单位变换）展示实体模型的渲染变换，以实体所在位置为原点。游戏存档时只使用分解形式。在定义此标签时必须写入此标签内的所有标签，否则此标签无效。 - - 若为[图:NBT列表/JSON数组]：使用矩阵形式。其中包含16个浮点数元素，描述一个行主序（Row-major）矩阵： - [图:单精度浮点数]：矩阵中的一个值。其中第13、第14、第15个值对于变换没有任何效果；第16个值会将前12个值进行缩放，即将前12个数字除以此数字。 - - 若为[图:NBT复合标签/JSON对象]：使用分解形式。此标签必须包含下列所有标签，且各个标签按下方列出的顺序依次应用： - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]* *right_rotation：初始旋转。此标签对应矩阵形式中矩阵左上角的3x3矩阵奇异值分解后的右奇异向量矩阵。游戏存档时只使用四元数形式。 - - 若为[图:NBT列表/JSON数组]：使用四元数表示旋转（非单位四元数还会使模型缩放）。其中包含4个浮点数。 - [图:单精度浮点数]：四元数中的一个元素。 - - 若为[图:NBT复合标签/JSON对象]：使用轴-角度形式表示旋转。必须包含下列所有标签： - [图:单精度浮点数]* *angle：表示绕旋转轴的旋转角度（以弧度为单位）。 - [图:NBT列表/JSON数组]* *axis：（列表长度为3）一个3维向量，表示旋转轴。 - [图:单精度浮点数]：一个向量分量。 - [图:NBT列表/JSON数组]* *scale：以原点为中心缩放模型。此标签对应矩阵形式中的矩阵左上角的3x3矩阵奇异值分解后的奇异值。此标签为含有3个元素的浮点数列表： - [图:单精度浮点数]：向量的一个分量。 - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]* *left_rotation：再次旋转模型。此标签对应矩阵形式中矩阵左上角的3x3矩阵奇异值分解后的左奇异向量矩阵。游戏存档时只使用四元数形式。 - - 若为[图:NBT列表/JSON数组]：使用四元数表示旋转（非单位四元数还会使模型缩放）。其中包含4个浮点数。 - [图:单精度浮点数]：四元数中的一个元素。 - - 若为[图:NBT复合标签/JSON对象]：使用轴-角度形式表示旋转。必须包含下列所有标签： - [图:单精度浮点数]* *angle：表示绕旋转轴的旋转角度（以弧度为单位）。 - [图:NBT列表/JSON数组]* *axis：（列表长度为3）一个3维向量，表示旋转轴。 - [图:单精度浮点数]：一个向量分量。 - [图:NBT列表/JSON数组]* *translation：平移变换。此标签对应矩阵形式中的最后一列的前3个元素。此标签为含有3个元素的浮点数列表： - [图:单精度浮点数]：向量的一个分量。 - [图:单精度浮点数]*view_range：（默认为1）实体最大可视范围。当玩家距离展示实体超过 ``` < 最大可视范围 >×< entityDistanceScaling >×64 ``` 时此实体不会进行渲染。

物品展示实体：

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 展示实体共通标签 - [图:NBT复合标签/JSON对象]item：（默认为空气）要展示的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:字符串]*item_display：（默认为 ``` none ``` ）物品展示实体的模式，用于再次变换物品模型。可以为 ``` none ``` （不变换）、 ``` thirdperson_lefthand ``` （第三人称视角左手变换）、 ``` thirdperson_righthand ``` （第三人称视角右手变换）、 ``` firstperson_lefthand ``` （第一人称视角左手变换）、 ``` firstperson_righthand ``` （第一人称视角右手变换）、 ``` head ``` （放置在头部物品栏的变换）、 ``` gui ``` （在图形界面中的变换）、 ``` ground ``` （平铺在地面的变换）、 ``` fixed ``` （默认变换）和 ``` on_shelf ``` （在展示架中的变换）。

方块展示实体：

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 展示实体共通标签 - [图:字符串][图:NBT复合标签/JSON对象]* *block_state：要展示的方块状态。 - - 方块状态，见Template:Nbt inherit/block state/source

文本展示实体：

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 展示实体共通标签 - [图:字符串]*alignment：（默认为 ``` center ``` ）文本对齐方向。可以为 ``` center ``` （居中）、 ``` left ``` （左对齐）和 ``` right ``` （右对齐）。 - [图:整型]*background：（可插值，默认为0x40000000）文本展示实体的背景颜色，各颜色通道按ARGB排列。由于在渲染时会自动丢弃Alpha通道小于0.1的片段，所以当A小于26（0x1A）时背景会变为完全透明。 - [图:布尔型]*default_background：（默认为 ``` false ``` ）表示是否使用默认的文本背景，此项会覆盖[图:整型]background的更改。 - [图:整型]*line_width：（默认为200）一行文本的最大宽度。如果展示文本超过了这个宽度会进行换行。 - [图:布尔型]*see_through：（默认为 ``` false ``` ）表示此文本展示实体是否能穿过方块渲染。 - [图:布尔型]*shadow：（默认为 ``` false ``` ）表示文本是否显示阴影。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *text：（文本组件）要展示的文本，以当前展示实体的前后文解析。 - [图:字节型]*text_opacity：（无符号8位整数，可插值，默认为-1，即无符号整数255）文本的不透明度。由于Java中没有无符号整数，所以大于127的值需要用 ``` < opacity >-256 ``` 进行替代。当取值为4~25时渲染片段将直接丢弃，这时文本会完全透明而不可见。

末地水晶

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:整型数组]beam_target：治愈激光定位到的位置。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:布尔型]*ShowBottom：表示末地水晶是否显示基岩底座。使用末地水晶物品放置生成时此值为false，其他情况下都为true。

唤魔者尖牙

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:整型数组]Owner：召唤该尖牙的实体的UUID。尖牙不对具有此UUID的生物造成伤害。 - [图:整型]* *Warmup：尖牙出现前的剩余时间。尖牙在此值小于等于0时出现并开始闭合，设置为负值会导致其没有延迟立刻闭合。当此值为-8时尖牙会对周围实体进行伤害。无论此值为多少，尖牙都会在生成的22游戏刻（1.1秒）后被删除。

经验球

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:短整型]* *Age：此经验球已存在的时间。当多个经验球合并时，此值会变成它们相应值中的最小值。在6000游戏刻（5分）后，此经验球会自然删除。 - [图:整型]* *Count：此经验球可被捡起的剩余次数，当经验球接触到玩家并给予经验时此值减1。当多个经验球合并时，此值会成为它们相应值之和。当此值到0时，此经验球被耗尽而被删除。当此值小于1时，游戏读取默认为1。 - [图:短整型]* *Health：经验球的“生命值”。经验球会受到火、熔岩、下落的铁砧和爆炸的伤害。当此值降至0及以下时经验球会被破坏而删除。 - [图:短整型]* *Value：此经验球被捡起时单次给予的经验值。

末影之眼

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:NBT复合标签/JSON对象]*Item：实体渲染时使用的物品，同时也控制掉落时产生的物品。此项不存在或无效时游戏使用末影之眼物品作为默认值。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source

下落的方块

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:字符串][图:NBT复合标签/JSON对象]* *BlockState：此下落的方块实体存储的方块。如果设置为空气，则游戏立刻清除此实体。未指定或数据无效时默认为沙子。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:布尔型]* *CancelDrop：表示下落的方块是否在落地时立刻被破坏且不放置方块或掉落任何物品。 - [图:布尔型]* *DropItem：（默认为true）表示下落的方块落地无法放置方块而被破坏时是否要掉落物品。如果存储的方块没有对应的方块物品，即使此值设置为true也不会掉落物品。 - [图:单精度浮点数]FallHurtAmount：（默认为0，[图:布尔型]* *HurtEntities为true时存在并有效）下落的方块每下落一格增加的伤害。 - [图:整型]FallHurtMax：（默认为40，[图:布尔型]* *HurtEntities为true时存在并有效）被这个下落的方块砸中的实体所承受的最大伤害。 - [图:布尔型]* *HurtEntities：（默认为false，但[图:NBT复合标签/JSON对象]* *BlockState指定的方块属于方块标签 ``` #anvil ``` 时，默认为true）表示是否要对它碰到的实体造成伤害。如果此项为false，但方块本身带有 ``` #anvil ``` 标签，那么游戏会尝试对碰到它的实体进行伤害，但伤害初始值为0。 - [图:NBT复合标签/JSON对象]TileEntityData：存储方块的方块实体数据。 - 见方块实体数据格式。不包含[图:字符串]id、[图:整型]x、[图:整型]y、[图:整型]z。 - [图:整型]* *Time：下落的方块已存在的时间，生成时设为0，每游戏刻增加1。当此值超过600游戏刻（30秒），或者处于世界建造高度之外且此值超过100游戏刻（5秒）时，下落的方块就会被删除。

烟花火箭

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 弹射物共通标签，见Template:Nbt inherit/projectile/source - [图:NBT复合标签/JSON对象]*FireworksItem：发射此烟花火箭的物品，决定烟火样式和伤害。此项不存在时游戏默认使用烟花火箭物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型]* *Life：这个烟花火箭已经飞行的时间。当此值大于[图:整型]LifeTime时，烟花火箭爆裂。 - [图:整型]* *LifeTime：这个烟花火箭从开始飞行到爆裂的时间。其值会在烟花火箭发射时随机决定，计算公式为：10(f+1)+rand(6)+rand(7)，其中，f表示[图:字节型]flight_duration的值，rand(x)返回[0,x−1]的随机整数。 - [图:布尔型]*ShotAtAngle：（默认为false）表示此烟花火箭是否由弩或发射器射出。如果此值为true，则烟花火箭在水平方向上会逐渐加速。

交互实体

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:NBT复合标签/JSON对象]attack：交互实体最后一次受到的攻击数据。 - [图:整型数组]* *player：攻击交互实体的玩家。 - [图:长整型]* *timestamp：被攻击的时间。 - [图:NBT复合标签/JSON对象]interaction：交互实体最后一次受到的交互数据。 - [图:整型数组]* *player：与交互实体交互的玩家。 - [图:长整型]* *timestamp：交互的时间。 - [图:单精度浮点数]height：（默认为1）交互实体的高度。 - [图:单精度浮点数]width：（默认为1）交互实体的宽度。 - [图:布尔型]response：（默认为 ``` false ``` ）表示玩家与交互实体交互时是否会挥动手臂。

物品

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:短整型]* *Age：（默认为0）未被捡起的持续时间，当物品在6000游戏刻（5分）内没有被捡起时就会被删除。如果被设置为-32768，那么此值将不会增加，物品也不会自然删除或被合并。 - [图:短整型]* *Health：（默认为5）物品实体的“生命值”，初始值为5。物品可以被火、熔岩、爆炸等伤害。当此值不大于0时物品实体被销毁而删除。 - [图:NBT复合标签/JSON对象]Item：物品实体中包含的物品。如果此项不存在，或包含的物品是空气，那么物品实体会被立刻删除。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型数组]Owner：只有对应UUID的玩家才能够捡起这个物品，用于防止 ``` / give ``` 产生的物品实体被其他玩家吸取。 - [图:短整型]*PickupDelay：剩余的不能够被捡起的时间，初始值为40游戏刻（2秒），每游戏刻减少1直到为0，此时生物才能将此物品捡起。如果被设置为32767或负数，那么此值将不会减少，物品也永远不能被捡起。如果被设置为32767，则物品实体也不能被合并。如果此值不存在，游戏读取时默认为0。 - [图:整型数组]Thrower：如果是玩家掉落的物品，则此值为掉落此物品的玩家的UUID。

物品展示框

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 方块附着物实体共通标签，见Template:Nbt inherit/hangable/source - [图:字节型]* *Facing：（0≤值≤5）当前物品展示框面对的方向。从0到5分别对应下上北南西东，如果超过值域则对6取余并取绝对值后对应方向。 - [图:布尔型]* *Fixed：表示物品展示框是否被固定。如果为true，物品展示框将不再因失去支撑方块、被移动（如被活塞推动）、受到伤害而掉落，但也不能在物品展示框内放置、移除或旋转物品。 - [图:布尔型]* *Invisible：表示物品展示框是否处于隐形状态。在隐形状态下，物品展示框内包含的物品和地图依然可见。 - [图:NBT复合标签/JSON对象]Item：物品展示框内的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:单精度浮点数]ItemDropChance：（默认为1）物品展示框被破坏时内部物品掉落的概率。当物品展示框内有物品时此标签才有效。 - [图:字节型]ItemRotation：（0≤值≤7，[图:NBT复合标签/JSON对象]Item存在时此项存在并有效）展示物品的方向，从0到7分别代表了物品展示框中物品的8个方向，如果超过值域则对8取余后对应方向。当物品展示框内有物品时此标签才有效。

拴绳结

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source

闪电束

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source

标记

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source

不祥之物生成器

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:NBT复合标签/JSON对象]item：不祥之物生成器内存储的物品。如果物品是任何弹射物物品，则在倒计时结束生成时变为对应的弹射物实体并向下发射；如果不是，则直接生成对应物品实体。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:长整型]* *spawn_item_after_ticks：从不祥之物生成器实体生成或加载开始计时，到不祥之物生成器生成内部物品而自身被删除作为计时结束，其中经过的总时间。

画

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 方块附着物实体共通标签，见Template:Nbt inherit/hangable/source - [图:字节型]* *facing：（0≤值≤3）当前画面对的方向，从0到3分别对应南西北东，如果超过值域则对4取余并取绝对值后对应方向。 - [图:字符串]* *variant：（命名空间ID）画的内容。如果设置值无效则为 ``` alban ``` 。此项实体数据会被视为数据组件painting/variant。 -

被激活的TNT

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - [图:字符串][图:NBT复合标签/JSON对象]*block_state：用于显示的方块状态。此项不存在时游戏默认为TNT。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:单精度浮点数]explosion_power：TNT的爆炸威力，取值为0到128之间的浮点数，小于0时会被设为0，大于128时会被设为128。不存在时默认为4。 - [图:短整型]* *fuse：（默认为80，单位为刻，即4秒）在爆炸之前要经过的时间，负值则在游戏刻计算时立刻爆炸。 - [图:整型数组]owner：点燃该TNT的生物的UUID，用于计算爆炸伤害来源实体。

# 存储格式

实体数据存储文件是一种区块数据，以区域文件格式为载体，存储于
```
<
维度根目录
>/entities
```

内。例如，主世界的实体数据存储文件全部位于
```
<
存档根目录
>/dimensions/minecraft/overworld/entities
```

，下界的全部位于
```
<
存档根目录
>/dimensions/minecraft/the_nether/entities
```

。

在每个区块数据内，实体数据都有下列存储格式：

- [图:NBT复合标签/JSON对象] 区域文件区块根标签 - [图:整型]*DataVersion：保存此实体数据存储文件的游戏的数据版本。如果此项不存在则游戏认为此项是-1。 - [图:整型数组]* *Position：数组的两个元素分别代表区块的X和Z坐标。如果区块位置和此值不对应，则游戏报错 ``` Chunk file at < 区块位置 > is in the wrong location. (Expected < 区块位置 >, got < Position数据位置 >) ``` 。 - [图:NBT列表/JSON数组]* *Entities：区块内保存的实体。 - [图:NBT复合标签/JSON对象]：一个实体对应的实体数据。如果实体是一个乘客（即正在骑乘另一个实体），则其本身数据由根实体（递归找到不骑乘其他实体的实体）负责记录，自身不再单独创建一个实体数据项。 - 见上文§ 数据格式。

# 历史

# 导航
