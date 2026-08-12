---
name: minecraft-atlas
description: |
  纹理图集（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是Java版现行的动态生成的纹理图集机制。关于其他用法，请见“纹理图集（消歧义）”。
  
  【涵盖内容】
  - armor_trims
  - banner_patterns
  - blocks
  - celestials
  - chests
  - decorated_pot
  - gui
  - items
  - map_decorations
  - paintings
  - particles
  - shield_patterns
  
  【关键定义】
  - 数据包路径：data/assets/minecraft/atlases、data/textures/s/foo/abc.png、data/map/decorations
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 纹理图集 的完整规范时
---

本条目介绍的是Java版现行的动态生成的纹理图集机制。关于其他用法，请见“纹理图集（消歧义）”。

本条目所述内容仅适用于Java版。

纹理图集（Texture Atlas）是游戏对纹理渲染使用的一种优化手段，也是一种动态生成纹理的方案。对多个纹理进行合并，合并而成的大纹理就被称为纹理图集，而组成纹理图集的各个小纹理被称为精灵图（Sprite）。

# 使用

 参见：纹理 
由于纹理图集自身就是一张大纹理，故游戏生成的纹理图集也可以通过命名空间ID的方式引用。对于纹理图集
```
minecraft:<
标识符
>
```

而言，生成的纹理位于
```
assets/minecraft/textures/atlas/<
标识符
>
```

，即
```
minecraft:atlas/<
标识符
>
```

。

在游戏中按下“转储动态纹理”（默认为F3 + S）可以导出所有纹理图集，并同时导出所有精灵图命名空间ID和纹理图集位置的映射文件。

纹理图集的长和宽永远是2的整数次幂，且为正方形或长是宽两倍的长方形，最大尺寸为16384×16384。使用这种尺寸的纹理可以使纹理精确渲染，而不会因为精度损失造成渲染问题。

如果纹理图集内有一个纹理本身加载失败，那么它仍然会被纹理图集记录，但会随机映射到一个精灵图位置。如果纹理的元数据加载失败，则纹理图集不会记录这个纹理，在引用此纹理时会被替换引用为无效纹理。

# 定义格式

游戏不支持定义新的纹理图集，但是支持对原版定义的纹理图集的内容进行增删。

纹理图集定义文件都在资源包的
```
assets/minecraft/atlases
```

目录下，且均为JSON文件。在资源包实际的加载过程中，游戏只会读取原版定义的纹理图集对应的JSON文件以合并纹理图集。纹理图集内的精灵图在解析时会根据精灵图的命名空间ID自动转换为
```
assets/<
命名空间
>/textures/<
ID
>.png
```

的对应路径。

如果不同的纹理图集出现了相同的精灵图，则游戏会在日志中警告
```
Duplicate sprite <
精灵图ID
> from atlas <
纹理图集ID
>, already defined in atlas <
另一个纹理图集ID
>. This will be rejected in a future version
```

。精灵图引用的纹理的内容可以不同，游戏将精灵图的ID作为判定依据。

纹理图集内只包含纹理图集源数据，按照资源包的顺序和每个资源包内对应纹理图集数据列表的顺序依次执行。

- [图:NBT复合标签/JSON对象] JSON文件根元素 - [图:NBT列表/JSON数组]*sources：纹理图集内包含精灵图的源。 - [图:NBT复合标签/JSON对象]：纹理图集源。 - [图:字符串]*type：纹理图集源的类型。 - - 如果[图:字符串]type为 ``` directory ``` ，则引入所有资源包所有命名空间中某路径下的所有纹理： - [图:字符串]*source：指定一个来源路径。该路径为从 ``` textures ``` 目录开始的一个子目录。游戏将通过该路径索引到相应的目录下，并匹配其中的所有 ``` .png ``` 纹理文件。 - [图:字符串]*prefix：指定所引入纹理文件的命名空间ID路径前缀。例如，若[图:字符串]source为 ``` s ``` ，[图:字符串]prefix为 ``` p ``` ，则对于命名空间x下的纹理文件 ``` textures/s/foo/abc.png ``` ，游戏会先得到其命名空间ID为 ``` x:foo/abc ``` ，最后为其添加前缀，变为 ``` x:p/foo/abc ``` 。 - - 如果[图:字符串]type为 ``` filter ``` ，则筛选已经添加到纹理图集的纹理资源： - [图:NBT复合标签/JSON对象]*pattern：对每个纹理资源映射后的命名空间ID进行正则筛选。 - [图:字符串]namespace：对命名空间进行正则匹配，必须为正则表达式。游戏会删除匹配成功的命名空间的精灵图。 - [图:字符串]path：对ID进行正则匹配，必须为正则表达式。游戏会删除匹配成功的ID的精灵图。 - - 如果[图:字符串]type为 ``` paletted_permutations ``` ，则利用调色板置换颜色在内存中动态生成纹理： - [图:NBT列表/JSON数组]*textures：定义原始纹理。原始纹理即被置换的纹理。原始纹理只能包含原始调色板所定义的RGB三通道颜色，A通道不做要求，在置换时，保留其A通道，使用置换调色板置换RGB通道。 - [图:字符串]：（命名空间ID）一个原始纹理。对于使用置换调色板P的原始纹理T，所生成的精灵图命名空间ID是 ``` < T >< 分隔符 >< P > ``` 。 - [图:字符串]*palette_key：（命名空间ID）原始调色板，表示一组用于置换原始纹理的颜色。同时也定义了原始纹理内的RGB三通道颜色。Java版26.3起，游戏会将此值解析为 ``` assets/< 命名空间 >/textures/palettes/< 路径 >.png ``` 。 - [图:NBT复合标签/JSON对象]*permutations：定义置换调色板。置换调色板纹理必须和原始调色板纹理尺寸一致——置换调色板纹理的每个像素与原始调色板的每个像素一一对应。这种对应关系用于将原始纹理中的符合原始调色板的颜色换为置换调色板所对应的颜色。 - [图:字符串]<置换调色板名称>：（命名空间ID）定义一个置换调色板命名空间ID，表示置换调色板纹理文件的位置。Java版26.3起，游戏会将此值解析为 ``` assets/< 命名空间 >/textures/palettes/< 路径 >.png ``` 。 - [图:字符串]separator：（默认为 ``` _ ``` ）精灵图ID中，在原始纹理与置换调色板之间的分隔符。 - - 如果[图:字符串]type为 ``` single ``` ，则直接引入单个纹理： - [图:字符串]*resource：（命名空间ID）纹理资源所在的位置。 - [图:字符串]sprite：（默认为[图:字符串]resource，命名空间ID）此纹理资源映射到的命名空间ID。 - - 如果[图:字符串]type为 ``` unstitch ``` ，则从一个纹理中截取一系列区域作为精灵图： - [图:双精度浮点数]divisor_x：（默认为1）将整个图像按照X轴，拆分为每个长度为[图:双精度浮点数]divisor_x的块，影响每个区域中[图:双精度浮点数]x和[图:双精度浮点数]width的计算方式。 - [图:双精度浮点数]divisor_y：（默认为1）将整个图像按照Y轴，拆分为每个长度为[图:双精度浮点数]divisor_y的块，影响每个区域中[图:双精度浮点数]y和[图:双精度浮点数]height的计算方式。 - [图:NBT列表/JSON数组]*regions：（至少包含一个元素）截取区域的列表。 - [图:NBT复合标签/JSON对象]：一个区域。 - [图:字符串]*sprite：（命名空间ID）此区域生成的精灵图映射到的命名空间ID。 - [图:双精度浮点数]*x：截取区域的左上角X坐标，对应像素X坐标是⌊xwt/dx⌋，其中x为此值，wt是原始纹理宽度，dx为[图:双精度浮点数]divisor_x的值。 - [图:双精度浮点数]*y：截取区域的左上角Y坐标，对应像素Y坐标是⌊yht/dy⌋，其中y为此值，ht是原始纹理高度，dy为[图:双精度浮点数]divisor_y的值。 - [图:双精度浮点数]*width：截取区域的宽度，对应像素宽度是⌊wwt/dx⌋，其中w为此值，wt是原始纹理宽度，dx为[图:双精度浮点数]divisor_x的值。 - [图:双精度浮点数]*height：截取区域的高度，对应像素高度是⌊hht/dy⌋，其中h为此值，ht是原始纹理高度，dy为[图:双精度浮点数]divisor_y的值。 - [图:字符串]*resource：（命名空间ID）截取纹理源的位置。

# 原版纹理图集

原版的纹理图集定义文件如下所示：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` atlases ``` - [图:File file.png：Minecraft中file的精灵图] ``` armor_trims.json ``` ：包含所有与实体模型有关的盔甲纹饰。 - [图:File file.png：Minecraft中file的精灵图] ``` banner_patterns.json ``` ：包含所有旗帜图案。 - [图:File file.png：Minecraft中file的精灵图] ``` blocks.json ``` ：包含所有方块使用的纹理。此纹理图集可以拥有MipMap版本。 - [图:File file.png：Minecraft中file的精灵图] ``` celestials.json ``` ：包含所有天体纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` chests.json ``` ：包含所有箱子纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` decorated_pot.json ``` ：包含所有饰纹陶罐相关的陶片图案纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` gui.json ``` ：包含所有GUI相关的纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` items.json ``` ：包含所有物品使用的纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` map_decorations.json ``` ：包含所有地图图标纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` paintings.json ``` ：包含所有画的纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` particles.json ``` ：包含所有粒子纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` shield_patterns.json ``` ：包含所有盾牌图案的纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` shulker_boxes.json ``` ：包含所有潜影盒、潜影贝纹理。

## armor_trims

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

此纹理图集控制了所有盔甲纹饰纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` trims ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` color_palettes ``` - [图:File file.png：Minecraft中file的精灵图] ``` trim_palette.png ``` ：盔甲纹饰的原始调色板。 - [图:File file.png：Minecraft中file的精灵图] ``` < 盔甲纹饰材料字符串 >.png ``` ：各种盔甲纹饰材料对应的调色板。 - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` humanoid ``` - [图:File file.png：Minecraft中file的精灵图] ``` < 盔甲纹饰图案ID >.png ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` humanoid_leggings ``` - [图:File file.png：Minecraft中file的精灵图] ``` < 盔甲纹饰图案ID >.png ```

所生成图集中，每张精灵图的命名空间ID格式为
```
trims/entity/<
装备模型
预设模型类型
>/<
盔甲纹饰图案ID
>_<
盔甲纹饰材料字符串
>
```

。

## banner_patterns

此纹理图集控制了所有旗帜相关的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File file.png：Minecraft中file的精灵图] ``` banner_base.png ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` banner ``` - 该目录下的所有png文件。

## blocks

此纹理图集控制了大多数方块的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` block ``` ：所有方块纹理。 - 该目录下的所有png文件。所对应的精灵图命名空间ID为 ``` < 命名空间 >:block/< 方块纹理文件名称 > ``` 。 - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` conduit ``` ：所有潮涌核心相关纹理。 - 该目录下的所有png文件。所对应的精灵图命名空间ID为 ``` < 命名空间 >:entity/conduit/< 潮涌核心 纹理文件名称 > ``` 。 - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` bell ``` - [图:File file.png：Minecraft中file的精灵图] ``` bell_body.png ``` ：钟纹理。 - [图:File directory.png：Minecraft中directory的精灵图] ``` decorated_pot ``` - [图:File file.png：Minecraft中file的精灵图] ``` decorated_pot_side.png ``` ：饰纹陶罐侧面纹理。 - [图:File directory.png：Minecraft中directory的精灵图] ``` enchantment ``` - [图:File file.png：Minecraft中file的精灵图] ``` enchanting_table_book.png ``` ：附魔台书纹理。

## celestials

此纹理图集控制天体相关的纹理，星星由于硬编码生成不由纹理图集控制。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` environment ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` celestial ``` - 该目录下的所有png文件。

所生成图集中，每张精灵图的命名空间ID格式为
```
<
命名空间
>:<
天体名称
>
```

。

## chests

此纹理图集控制所有箱子的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` chest ``` - 该目录下的所有png文件。

## decorated_pot

此纹理图集控制所有饰纹陶罐的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` decorated_pot ``` - 该目录下的所有png文件。

## gui

此纹理图集控制所有用户界面图片的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` gui ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` sprites ``` - 该目录下的所有png文件。所生成图集中，每张精灵图的命名空间ID格式为 ``` < 命名空间 >:< GUI精灵图名称 > ``` 。 - [图:File directory.png：Minecraft中directory的精灵图] ``` mob_effect ``` - 该目录下的所有png文件。

## items

此纹理图集控制所有物品的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` item ``` ：所有物品纹理。 - 该目录下的所有png文件。所对应的精灵图命名空间ID为 ``` < 命名空间 >:item/< 物品纹理文件名称 > ``` 。 - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` trims ``` ：在所生成的图集中，所对应的每张精灵图的命名空间ID为 ``` minecraft:trims/items/< 盔甲类型 >_trim_< 盔甲纹饰材料 > ``` 。 - [图:File directory.png：Minecraft中directory的精灵图] ``` color_palettes ``` ：用于盔甲纹饰颜色的像素色盘。 - [图:File file.png：Minecraft中file的精灵图] ``` trim_palette.png ``` ：原始纹饰色盘。 - [图:File file.png：Minecraft中file的精灵图] ``` < 盔甲纹饰材料字符串 >.png ``` ：相应盔甲纹饰材料对应的色盘。 - [图:File directory.png：Minecraft中directory的精灵图] ``` items ``` ：所有物品纹饰纹理。 - [图:File file.png：Minecraft中file的精灵图] ``` helmet_trim.png ``` ：头盔纹饰。 - [图:File file.png：Minecraft中file的精灵图] ``` chestplate_trim.png ``` ：胸甲纹饰。 - [图:File file.png：Minecraft中file的精灵图] ``` leggings_trim.png ``` ：护腿纹饰。 - [图:File file.png：Minecraft中file的精灵图] ``` boots_trim.png ``` ：靴子纹饰。

## map_decorations

此纹理图集控制所有地图图标纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` map ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` map/decorations ``` - 该目录下的所有png文件。

所生成图集中，每张精灵图的命名空间ID格式为
```
<
命名空间
>:<
地图图标纹理文件名称
>
```

。

## paintings

此纹理图集控制所有画的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` painting ``` - 该目录下的所有png文件。

所生成图集中，每张精灵图的命名空间ID格式为
```
<
命名空间
>:<
画纹理文件名称
>
```

。

## particles

此纹理图集控制所有粒子的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` <资源包> ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` particle ``` - 该目录下的所有png文件。

所生成图集中，每张精灵图的命名空间ID格式为
```
<
命名空间
>:<
粒子纹理文件名称
>
```

。

## shield_patterns

此纹理图集控制所有盾牌的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` shield ``` - 该目录下的所有png文件。

## shulker_boxes

此纹理图集控制所有潜影盒的纹理。对于原版游戏而言，构成该图集的纹理来源于：

- [图:File directory.png：Minecraft中directory的精灵图] ``` assets ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 任意命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` textures ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` entity ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` shulker ``` - 该目录下的所有png文件。

# 历史

# 参考

1. ↑ MC-276568 — 漏洞状态为“已修复”。
1. ↑ MC-277447 — 漏洞状态为“已修复”。
1. ↑ MC-277450 — 漏洞状态为“已修复”。
1. ↑ MC-277470 — 漏洞状态为“已修复”。
1. ↑ MC-277471 — 漏洞状态为“已修复”。
1. ↑ MC-277473 — 漏洞状态为“已修复”。
1. ↑ MC-277481 — 漏洞状态为“已修复”。
1. ↑ MC-277483 — 漏洞状态为“已修复”。

# 导航
