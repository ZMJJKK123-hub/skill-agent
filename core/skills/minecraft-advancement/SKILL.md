---
name: minecraft-advancement
description: |
  进度定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】提示：本条目的主题不是进度存储格式。
  
  【涵盖内容】
  - 显示信息
  - 进度选项卡
  - 定位
  - 缺省显示
  - allay_drop_item_on_block
  - any_block_use
  - avoid_vibration
  - bee_nest_destroyed
  - bred_animals
  - brewed_potion
  - changed_dimension
  - channeled_lightning
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 进度定义格式 的完整规范时
---

提示：本条目的主题不是进度存储格式。

本条目所述内容仅适用于Java版。

进度（Advancement）是位于数据包中用于定义进度的技术性JSON文件。

# 文件夹结构

在数据包中，每个进度都由一个进度文件定义。以下的文件结构图展示了进度文件在数据包中的位置：

- [图:File archive.png：Minecraft中archive的精灵图]/[图:File directory.png：Minecraft中directory的精灵图] ``` < 数据包名称 > ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` advancement ``` - [图:File file.png：Minecraft中file的精灵图] ``` < 进度文件名 >.json ``` - 查看更多目录…

# 主格式

- [图:NBT复合标签/JSON对象]根标签 - [图:NBT复合标签/JSON对象]*criteria：此进度的一系列准则。 - 一项准则。见下文。 - [图:NBT复合标签/JSON对象]display：进度的显示信息。 - [图:字符串]parent：此进度的上游进度的命名空间ID。若此项不存在，则此进度为根进度。循环引用上游进度将导致加载失败。 - [图:NBT列表/JSON数组]requirements：定义了以上准则将如何达成。其中包含许多子列表，每一个子列表中都允许包含此进度中的若干准则（在所有的 ``` <准则名称> ``` 中）。完成或废除一个准则时，如果所有子列表中至少有一个准则达成，则进度达成。默认情况下（即此项不存在），进度达成需要保证每个准则都要达成。 - [图:NBT列表/JSON数组]：在[图:NBT列表/JSON数组]requirements中的一个子列表，可包含若干 ``` <准则名称> ``` 。如果有任何一项子列表为空，则此进度不可达成，除非通过作弊。 - [图:字符串]：一项准则名称。 - [图:NBT复合标签/JSON对象]rewards：进度达成后的奖励。 - [图:整型]experience：（默认为0）完成进度后玩家将获得的经验值。 - [图:字符串]function：完成进度后执行的函数，不支持函数标签。函数将以该玩家为执行者，在其位置执行。详见命令上下文#进度奖励。 - [图:NBT列表/JSON数组]loot：完成进度后给予玩家的战利品表。 - [图:字符串]：战利品表的命名空间ID。 - [图:NBT列表/JSON数组]recipes：完成进度后玩家将解锁的配方。 - [图:字符串]：配方的命名空间ID。 - [图:布尔型]sends_telemetry_event：（默认为 ``` false ``` ）玩家达成此进度时是否收集遥测数据。只对命名空间为 ``` minecraft ``` 的进度才有效，其他进度永远不会收集遥测数据。

示例

```
{

  
"criteria"
:
 
{

    
"crafting_table"
:
 
{

      
"conditions"
:
 
{

        
"items"
:
 
[

          
{

            
"items"
:
 
"minecraft:crafting_table"

          
}

        
]

      
},

      
"trigger"
:
 
"minecraft:inventory_changed"

    
}

  
},

  
"display"
:
 
{

    
"announce_to_chat"
:
 
false
,

    
"background"
:
 
"minecraft:gui/advancements/backgrounds/stone"
,

    
"description"
:
 
{

      
"translate"
:
 
"advancements.story.root.description"

    
},

    
"icon"
:
 
{

      
"count"
:
 
1
,

      
"id"
:
 
"minecraft:grass_block"

    
},

    
"show_toast"
:
 
false
,

    
"title"
:
 
{

      
"translate"
:
 
"advancements.story.root.title"

    
}

  
},

  
"requirements"
:
 
[

    
[

      
"crafting_table"

    
]

  
],

  
"sends_telemetry_event"
:
 
true

}
```

# 显示

## 显示信息

显示信息的数据格式如下：

- [图:NBT复合标签/JSON对象]display：进度的显示信息。 - [图:布尔型]announce_to_chat：（默认为 ``` true ``` ）是否在完成此进度时在聊天窗口提示。 - [图:字符串]background：（仅根进度可用，命名空间ID）作为进度背景平铺图片的纹理。背景纹理文件需存放在资源包 ``` <命名空间>/textures/<路径>.png ``` ，在数据包内引用时应省略 ``` textures/ ``` 和 ``` .png ``` ，变为 ``` <命名空间>:<路径> ``` 。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*description：文本组件，表示该进度在进度界面中显示的描述信息。 - [图:字符串]frame：（默认为 ``` task ``` ）图标边框的可选种类。 ``` challenge ``` 为； ``` goal ``` 为； ``` task ``` 为。 - [图:布尔型]hidden：（默认为 ``` false ``` ）是否在进度屏幕隐藏此进度以及其所有子进度，直到完成此进度。此项对根进度自身无效，但依然能影响其子进度。 - [图:字符串][图:NBT复合标签/JSON对象]*icon：表示一个物品堆叠，用于显示进度的图标。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:布尔型]show_toast：（默认为 ``` true ``` ）是否在完成此进度后显示右上角的提示信息。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*title：文本组件，表示该进度在进度界面中显示的标题。

一个进度只有满足以下情况之一才会显示在进度菜单中：

- 此进度为根进度。
- 此进度的上游进度已处于显示状态，此进度的[图:NBT复合标签/JSON对象]display被有效定义且[图:布尔型]hidden为 ``` false ``` 。

## 进度选项卡

创建带有显示数据[图:NBT复合标签/JSON对象]display的根进度（不含[图:字符串]parent的进度）后将自动在进度菜单边缘创建一个选项卡。当游戏加载数据包后，若根进度所在的进度树中有任意进度被某玩家获取，则该根进度以及其选项卡都会显示给该玩家，且根进度和选项卡的图标一致。

根进度的背景图像不会影响选项卡的创建。若根进度未正确从[图:字符串]background加载图片，则背景默认显示为丢失纹理。

如果一个根进度成功创建了一个选项卡，它的子进度将会展示在该选项卡中（前提是该子进度拥有显示数据 [图:字符串]display）。

## 定位

在从数据包加载进度时，游戏会自动对进度进行排列，确定其位置，并将排列信息发送到客户端。每个进度都有从最近的可见上游进度指向它的箭头（即，如果其相邻的上游进度没有显示数据，则有从上游进度的上游进度指向它的箭头）。根进度出现在最左一列，每个箭头指向下一列中的进度。每一列中的进度基于其文件名排序。

## 缺省显示

有些进度（如原版中由配方解锁的进度）可能会省去显示数据，以便它们利用触发器和奖励来替代过多的命令和函数并实现更多功能和更灵活的控制。通过省去[图:NBT复合标签/JSON对象]display数据，这些用于逻辑控制的进度不仅能被一般玩家忽略，还有助于获得更好的加载性能。

# 准则

- [图:NBT复合标签/JSON对象]<准则名称>：一项准则，此名称必须唯一。 - [图:字符串]*trigger：该准则的触发器的命名空间ID。每种触发器都有其对应的触发情形和可检查条件。 - [图:NBT复合标签/JSON对象]conditions：触发器被触发时，达成此准则需要满足的条件。与具体的触发器有关。 - [图:NBT复合标签/JSON对象]player：一个实体谓词，玩家与谓词匹配后才能达成此准则，此项对于除 ``` minecraft:impossible ``` 外的触发器均可使用。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]player：[图:NBT复合标签/JSON对象]player的另一种格式，为一个谓词列表。玩家与该列表中的谓词全部匹配后才能达成此准则。此项对于除 ``` minecraft:impossible ``` 外的触发器均可使用。 - [图:NBT复合标签/JSON对象]：一个谓词。 - 其余的附加条件，取决于[图:字符串]trigger的值。详见下文。

# 可用准则触发器

在游戏中总共定义了下列准则触发器：

# 准则触发器

 “触发器”重定向至此。关于记分板的准则，请见“记分板 § 准则”。关于命令，请见“命令/trigger”。

所有触发器均要求玩家在线，如果不在线，即使其之后重新加入服务器也不会再获得进度。

## allay_drop_item_on_block

当悦灵确定待投掷的目标方块后，将物品投掷的瞬间触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]location：一个谓词列表，该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## any_block_use

玩家与方块进行任何交互（包括默认交互，以及玩家不空手使用物品等方式）时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]location：一个谓词列表，该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## avoid_vibration

当玩家产生振动时，若幽匿感测体、校频幽匿感测体或监守者因玩家正在潜行而无法检测振动时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## bee_nest_destroyed

玩家破坏蜂巢或蜂箱时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]block：被破坏的方块ID，当为 ``` minecraft:beehive ``` 和 ``` minecraft:bee_nest ``` 之外的值时不可能通过。 - [图:NBT复合标签/JSON对象]item：用于破坏该方块的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:整型][图:NBT复合标签/JSON对象]num_bees_inside：该蜂箱/蜂巢被破坏变为物品状态后其中含有的蜜蜂数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## bred_animals

两个动物繁殖时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]child：繁殖出的动物。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]child：“child”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]parent：双亲之一。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]parent：“parent”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]partner：配偶，即双亲中的另一位实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]partner：“partner”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## brewed_potion

玩家从酿造台中拿出一瓶药水时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]potion：检查拿出的药水ID是否匹配。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## changed_dimension

玩家在传送到另一个维度或死亡后在另一维度重生时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]from：实体原所在维度的命名空间ID，原版维度包含 ``` minecraft:overworld ``` （主世界）、 ``` minecraft:the_nether ``` （下界）或 ``` minecraft:the_end ``` （末地）。也可以使用数据包添加的其他维度。 - [图:字符串]to：实体到达的维度，同上。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家，玩家位置按照其在目标维度的位置计算。详见上文。

## channeled_lightning

闪电束由引雷魔咒生成时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]victims：检查所有被闪电束击中的实体，为一个谓词或谓词列表的列表，列表中所有项都对其中至少一个实体测试通过时才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个实体谓词，检查一个被击中的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]：描述被击中的实体的另一种格式。为一个谓词列表，该列表中的谓词全部测试通过后此项才能通过。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## construct_beacon

信标检测到基座结构更改时，如果更改后信标处于激活状态，且这个信标上方从第11格起没有任何方块，则对信标中心位置水平切比雪夫距离10格内，垂直距离向上5格，向下9格内的所有玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:整型][图:NBT复合标签/JSON对象]level：新的信标基座层数。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## consume_item

玩家消耗了带有
```
consumable
```

组件的物品后触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查被消耗的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## crafter_recipe_crafted

合成器将物品以实体形式掷出时，对中心位置切比雪夫距离8.5格内的所有玩家触发。当一次性掷出多个物品时（如合成蛋糕的同时掷出3个铁桶），每1个物品均会触发一次。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]*recipe_id：检查合成配方的命名空间ID。 - [图:NBT列表/JSON数组]ingredients：一个物品谓词列表，检查合成使用的原材料，该列表中的谓词全部测试通过后才能达成此准则。 每个物品谓词仅需对一个物品测试通过即可，且通过的物品之后不再参与测试，因此一个物品只能满足其中一个谓词。 此触发器触发时，合成使用的原材料尚未被扣除，但相应的物品实体已经被投掷。 - [图:NBT复合标签/JSON对象]：一个物品谓词。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## cured_zombie_villager

僵尸村民被治愈时，对喂食其金苹果的玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]villager：一个实体谓词，检查转化后的村民。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]villager：“villager”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]zombie：一个实体谓词，检查转换前的僵尸村民。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]zombie：“zombie”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## default_block_use

玩家在非潜行状态下与方块进行交互时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]location：一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## effects_changed

玩家获得/消除状态效果时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]effects：要检查的状态效果列表。 - - 状态效果谓词，见Template:Nbt inherit/mob effects predicate/source - [图:NBT复合标签/JSON对象]source：实体谓词，检查状态效果的来源实体。如果不存在该实体，则只有未指定时才会通过。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]source：“source”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## enchanted_item

玩家通过附魔台附魔物品时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查附魔后的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:整型][图:NBT复合标签/JSON对象]levels：附魔花费的经验等级。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家，附魔花费的经验值已经被扣除。详见上文。

## enter_block

每游戏刻，玩家对与其碰撞箱相交的各个方块分别触发，或者玩家掷出的末影珍珠进入末地折跃门时对其触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]block：检查方块的ID。 - [图:NBT复合标签/JSON对象]state：检查方块的方块状态。 - [图:字符串][图:NBT复合标签/JSON对象]<方块属性>：检查指定方块属性。如果方块不满足条件，那么测试会失败。可以为字符串或以两个数字字符串表示的数值区间。 - [图:字符串]min：数值的最小允许值。 - [图:字符串]max：数值的最大允许值。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## entity_hurt_player

当玩家受到伤害，或阻挡所受到的伤害时触发。伤害并不一定来源于某个实体（比如被熔岩伤害）。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]damage：检查对玩家造成伤害的类型。 - - 伤害谓词，见Template:Nbt inherit/damage predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## entity_killed_player

实体杀死玩家时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查伤害的来源实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。游戏会以将要获得进度的玩家的位置为来源，检查杀死玩家的实体。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]killing_blow：检查杀死玩家的伤害来源。 - - 伤害来源谓词，见Template:Nbt inherit/damage source predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## fall_after_explosion

在玩家被爆炸或风爆击飞后开始摔落时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]start_position：位置信息谓词，检查玩家被击飞时所在位置。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source - [图:NBT复合标签/JSON对象]distance：距离谓词，检查玩家从 ``` start_position ``` 起的摔落高度。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source - [图:NBT复合标签/JSON对象]cause：实体谓词，检查造成爆炸或风爆的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## fall_from_height

玩家摔落至地面时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]start_position：位置信息谓词，检查开始摔落时的位置。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source - [图:NBT复合标签/JSON对象]distance：距离谓词，检查玩家到其摔落起始位置的距离。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## filled_bucket

玩家填充桶时触发，从炼药锅填充时不触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查铁桶被填充后的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## fishing_rod_hooked

玩家成功通过钓鱼获取物品或者使用钓鱼竿拉实体时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被拉的实体。如果没有被拉的实体，则检查钓鱼竿的浮漂。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的谓词全部测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]item：物品谓词，检查钓鱼获取的物品或拉动的物品实体，如果不存在则总是不通过。每个物品谓词仅需对至少一个物品测试通过即可。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]rod：物品谓词，检查使用的钓鱼竿物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## hero_of_the_village

一场袭击胜利后对所有在该场袭击中击杀过至少一名袭击者的玩家触发，如果玩家当前为旁观模式（通常这发生在极限模式的世界中，例如玩家在袭击中死亡）则不会触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## impossible

无法触发，仅能通过命令
```
/
advancement
 grant
```

等直接授予。

## inventory_changed

玩家物品栏变化时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]items：一个物品谓词列表，用于检查进度触发时新增到玩家物品栏的所有物品。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个物品谓词，检查一项物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]slots： - [图:整型][图:NBT复合标签/JSON对象]empty：检查物品栏中空槽位数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:整型][图:NBT复合标签/JSON对象]full：检查物品栏中已被填满（物品数量大于等于最大堆叠数量）的槽位数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:整型][图:NBT复合标签/JSON对象]occupied：检查物品栏中已被填充至少一个物品的槽位数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## item_durability_changed

物品栏中任何物品以任何形式损害时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:整型][图:NBT复合标签/JSON对象]delta：检查耐久度的变化量，负数代表损耗了耐久值。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:整型][图:NBT复合标签/JSON对象]durability：检查物品的剩余耐久度。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]item：物品谓词，检查损害前的物品，可用来检查物品损害前的耐久度。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## item_used_on_block

玩家对方块空手或手持物品时进行某些使用操作时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]location：一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

关于所有可触发此触发器的操作详见MC-259075。

## kill_mob_near_sculk_catalyst

幽匿催发体蔓延时对死亡生物的伤害来源玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被杀死的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]killing_blow：检查杀死该实体的伤害来源。 - - 伤害来源谓词，见Template:Nbt inherit/damage source predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## killed_by_arrow

箭杀死实体后对发射箭的玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:整型][图:NBT复合标签/JSON对象]unique_entity_types：检查杀死的不同实体种类的数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]fired_from_weapon：物品谓词，检查发射箭的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]victims：一个实体谓词或谓词列表的列表，检查所有被杀死的实体，列表中每项仅需对一个实体测试通过即可，且通过的实体之后不再参与测试，因此一个实体只能满足其中一个谓词。 - [图:NBT复合标签/JSON对象]：一个实体谓词，检查一个被杀死的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]：描述被杀死的实体的另一种格式。为一个谓词列表，该列表中的谓词全部测试通过后此项才能通过。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## levitation

玩家带有飘浮状态效果时每游戏刻触发一次。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]distance：检查玩家到其飘浮起始点的距离。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source - [图:整型][图:NBT复合标签/JSON对象]duration：检查飘浮时间，单位为游戏刻。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## lightning_strike

闪电束消失时对半径256格内的玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]lightning：实体谓词，检查消失的闪电束。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]lightning：“lightning”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]bystander：检查所有没有被闪电束击中，且在其位置水平切比雪夫距离15格内，垂直距离向上21格，向下15格范围内的实体，对其中任意一个实体测试通过即可。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]bystander：“bystander”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才视为通过。对其中任意一个实体测试通过即可。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## location

所有玩家每20游戏刻（1秒）触发一次。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## nether_travel

玩家进入下界，然后返回主世界时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]start_position：检查玩家被传送至下界前位于主世界的最后位置。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source - [图:NBT复合标签/JSON对象]distance：检查玩家传送到下界前的主世界位置和返回时到达的主世界位置之间的距离。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## placed_block

玩家放置方块物品、水或熔岩，以及使用打火石点火时触发，但使用火焰弹点火时不会触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT列表/JSON数组]location：一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## player_generates_container_loot

玩家与方块、容器或生物交互并使之按照战利品表生成战利品时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]*loot_table：检查生成战利品的战利品表的命名空间ID。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## player_hurt_entity

玩家伤害实体（包括自己）时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]damage：检查造成的伤害。 - - 伤害谓词，见Template:Nbt inherit/damage predicate/source - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被伤害的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## player_interacted_with_entity

玩家与实体交互时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查玩家与实体互动时手中的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]entity：实体谓词，检查交互的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## player_killed_entity

玩家杀死实体时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被杀死的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象]killing_blow：检查杀死实体的伤害来源。 - - 伤害来源谓词，见Template:Nbt inherit/damage source predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## player_sheared_equipment

玩家对生物使用剪刀修剪下装备时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查被修剪下的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]entity：实体谓词，检查交互的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## recipe_crafted

玩家使用工作台，熔炉，高炉，烟熏炉，切石机，物品栏，或锻造台合成配方时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]*recipe_id：检查合成配方的命名空间ID。 - [图:NBT列表/JSON数组]ingredients：一个物品谓词列表，检查合成使用的原材料，该列表中的谓词全部测试通过后才能达成此准则。 每个物品谓词仅需对一个物品测试通过即可，且通过的物品之后不再参与测试，因此一个物品只能满足其中一个谓词。 - [图:NBT复合标签/JSON对象]：一个物品谓词。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## recipe_unlocked

玩家解锁配方时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]*recipe：检查被解锁的配方的命名空间ID。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## ride_entity_in_lava

玩家骑乘位于熔岩上的实体时，每游戏刻触发一次。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]start_position：检查玩家开始骑乘实体时所在的位置。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source - [图:NBT复合标签/JSON对象]distance：检查玩家开始骑乘的位置到当前位置的距离。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## shot_crossbow

玩家使用弩发射弹射物时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查发射所使用的弩。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## slept_in_bed

玩家上床睡觉时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## slide_down_block

玩家从蜂蜜块上滑下时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:字符串]block：检查玩家所滑下的方块，为 ``` honey_block ``` 之外的值时不可能通过。 - [图:NBT复合标签/JSON对象]state：检查玩家所滑下的方块的方块状态。蜂蜜块并没有任何方块属性，故此项实际上并不能检查任何条件。 - [图:字符串][图:NBT复合标签/JSON对象]<方块属性>：检查指定方块属性。如果方块不满足条件，那么测试会失败。 - [图:字符串]min：数值的最小允许值。 - [图:字符串]max：数值的最大允许值。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## started_riding

实体被骑乘时对所有玩家乘客触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## summoned_entity

- 铁傀儡和雪傀儡被通过搭建结构召唤时，对自身位置切比雪夫距离5格范围内的所有玩家触发。
- 凋灵被通过搭建结构召唤时，对自身位置切比雪夫距离50格范围内的所有玩家触发。
- 末影龙被复活时，对在末地中距离 ``` 0,0,0 ``` 不超过192格的所有玩家触发。

可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被召唤的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## spear_mobs

玩家使用任意物品进行冲锋攻击时触发。

- [图:NBT复合标签/JSON对象]conditions - [图:整型]count: 单次攻击的最少受击生物数量。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player: 将要获得进度的玩家，详见上文。

## tame_animal

玩家驯服动物时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]entity：实体谓词，检查被驯服的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## target_hit

玩家射中标靶时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:整型][图:NBT复合标签/JSON对象]signal_strength：检查标靶将产生的红石信号强度。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]projectile：实体谓词，检查被用来射击标靶的弹射物。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]projectile：“projectile”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## thrown_item_picked_up_by_entity

实体捡起玩家扔出的物品时对扔出物品的玩家触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查被捡起的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]entity：实体谓词，检查捡起物品的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## thrown_item_picked_up_by_player

玩家捡起实体扔出的物品时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查被捡起的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]entity：实体谓词，检查扔出物品的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]entity：“entity”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## tick

每游戏刻对所有玩家触发一次。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## used_ender_eye

玩家使用末影之眼定位要塞时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:双精度浮点数][图:NBT复合标签/JSON对象]distance：检查玩家与末影之眼指向的要塞的水平距离。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## used_totem

玩家使用不死图腾免于死亡时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查消耗的不死图腾。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## using_item

每个游戏刻玩家使用持续使用的物品时触发。可用于弓、弩、蜂蜜瓶、奶桶、药水、盾牌、望远镜、三叉戟、食物物品和末影之眼。大多数点击一次即可激活的物品，如钓鱼竿，不受此触发器影响。可用的条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查被使用的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## villager_trade

玩家成交一项交易时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]item：物品谓词，检查购买的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]villager：实体谓词，检查参与交易的村民或流浪商人。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]villager：“villager”的另一种格式，为一个谓词列表。该列表中的所有谓词均测试通过后才能达成此准则。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

## voluntary_exile

玩家触发一场新的袭击时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

# 历史

## 进度谓词

 关于进度实体谓词历史，请见“实体谓词 § 历史”。

## 已移除触发器

### arbitrary_player_tick

每游戏刻仅对一名玩家触发。无可用条件。

### item_delivered_to_player

当悦灵向玩家投掷物品时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

一个例子：

```
{

  
"criteria"
:
 
{

    
"example"
:
 
{

      
"trigger"
:
 
"minecraft:item_delivered_to_player"
,

      
"conditions"
:
 
{

        
"player"
:
 
[

          
{

            
"condition"
:
 
"minecraft:entity_properties"
,

            
"predicate"
:
 
{

              
"location"
:
 
{

                
"dimension"
:
 
"minecraft:the_nether"

              
}

            
},

            
"entity"
:
 
"this"

          
}

        
]

      
}

    
}

  
}

}
```

### player_damaged

玩家受到伤害时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]damage：用于匹配伤害来源的谓词。 - - 伤害谓词，见Template:Nbt inherit/damage predicate/source

### safely_harvest_honey

玩家从一个垫有营火的蜂巢或蜂箱中收获蜂蜜时触发。可用选项：

- [图:NBT复合标签/JSON对象]conditions - [图:NBT复合标签/JSON对象]block：玩家收获蜂蜜的方块。 - [图:字符串]block： 一个方块ID。 - [图:字符串]tag：一个方块标签。 - [图:NBT复合标签/JSON对象]item：玩家用于收获蜂蜜的物品。 - - 物品谓词

- - [图:字符串]item： 一个物品ID。 - [图:字符串]tag：一个物品标签。 - [图:整型][图:NBT复合标签/JSON对象]durability： 匹配物品的耐久度。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]enchantments： 检查该物品的魔咒。 - [图:NBT复合标签/JSON对象] - [图:字符串]enchantment：要检查的魔咒ID。 - [图:整型][图:NBT复合标签/JSON对象]level： 此魔咒的等级。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]stored_enchantments：检查附魔书中的魔咒，格式与[图:NBT列表/JSON数组]enchantments相同。 - [图:字符串]potion：检查该物品的药水类型。 - [图:字符串]nbt：检查物品的其他NBT数据。

- - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

### killed_by_crossbow

玩家使用弩远程杀死生物或玩家时触发。可用条件：

- [图:NBT复合标签/JSON对象]conditions - [图:整型][图:NBT复合标签/JSON对象]unique_entity_types：杀死的实体种类的数量。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]victims：被杀死的实体的列表。所有谓词都必须被匹配，且一个实体只可以匹配一个谓词。 - [图:NBT复合标签/JSON对象]：一个被杀死的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT列表/JSON数组]：描述被杀死的任意实体的另一种格式。实体被该列表匹配，是玩家完成进度的必要条件。游戏会以将要获得进度的玩家的位置为来源，检查被杀死的实体。 - [图:NBT复合标签/JSON对象]：一个谓词。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]player：将要获得进度的玩家。详见上文。

# 参考

1. ↑ MC-116922
1. ↑ MC-153385
1. ↑ MC-205424
1. ↑ MC-117653 — 漏洞状态为“已修复”。

# 外部链接

- Advancement Generator on misode.github.io，一个进度生成器。

# 导航
