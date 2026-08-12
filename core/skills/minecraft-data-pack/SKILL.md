---
name: minecraft-data-pack
description: |
  数据包（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于控制数据包的加载和卸载的命令，请见“命令/datapack”。
  
  【涵盖内容】
  - 添加数据包
  - 加载数据包
  - 实验性设置
  - 数据包元数据
  - 示例
  - 数据包图标
  
  【关键定义】
  - 数据包路径：data//reload、data/assets/minecraft/textures/misc/unknown_pack.png
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 数据包 的完整规范时
---

关于控制数据包的加载和卸载的命令，请见“命令/datapack”。

本条目所述内容仅适用于Java版。
 Wiki上有与该主题相关的教程！
见教程:制作数据包与教程:安装数据包。

 Wiki上有与该主题相关的教程！
见教程:制作数据包与教程:安装数据包。

 
数据包（Data Pack）为玩家自定义Minecraft的游戏内容提供了更多新方法，包括但不限于配置进度、配方、战利品表、魔咒、伤害类型、生物变种和世界生成等。对数据包的修改并不等于修改了包含相同逻辑部分的游戏代码。

# 使用数据包

数据包是可被添加到
```
<
存档根目录
>/datapacks/
```

目录下的文件夹或.zip 压缩包或文件夹。

在“创建新世界”页面中选择数据包将会缓存至
```
Java临时文件目录
/mcworld-[19~20位数字]
```

目录下。

## 添加数据包

在创建世界前，玩家可以在创建新的世界屏幕的“更多”选项卡中配置数据包。与配置资源包的界面类似，玩家可以自由选择数据包的加载顺序和启用情况，并可以搜索数据包。

## 加载数据包

玩家每次加载存档时游戏都会尝试加载一次数据包。

在正在运行的游戏存档中，可以使用命令
```
/
reload
```

来重新加载数据包。

- 数据包中的进度、配方、函数、战利品表、谓词和物品修饰器目录的文件会被重新加载。
- 对于剩余数据包目录的文件，例如世界生成、魔咒、盔甲纹饰和唱片机曲目等，游戏仅会在服务端启动时加载一次，也即必须重新进入存档时游戏才会重新加载这些文件，命令 ``` /reload ``` 无法重新加载。 - 这些目录的文件若出现语法错误或无注册元素等情况，可能导致进入存档时出现“安全错误”提醒，在禁用这些数据包前游戏拒绝加载存档。

不论是哪种加载方式，只有有效的数据包才会被加载。这要求数据包：

- 数据包元数据被游戏正确加载。
- 数据包中的任何文件均无语法错误且能被成功解析，若文件无法被正常解析则对应文件不会生效或在进入存档时出现“安全错误”提醒。

加载顺序

在创建存档之前，配置数据包的界面中的数据包顺序就是游戏加载存档时使用的顺序。

在存档被创建后，玩家可以使用命令
```
/
datapack
 list
```

来获取数据包加载顺序。数据包加载顺序存储在存档的
```
level.dat
```

的[图:NBT复合标签/JSON对象]DataPacks标签内。

禁用数据包

- 在已经载入的世界中，玩家可以使用命令 ``` / datapack disable ``` 来手动禁用一个数据包。执行成功后，游戏会自动重新加载一次数据包。

启用数据包

- 在已经载入的世界中，玩家可以使用命令 ``` / datapack enable ``` 来手动启用一个已经被禁用了的数据包。执行成功后，游戏会自动重新加载一次数据包。

## 实验性设置

 提示：本章节的主题不是实验性内容。

一些数据包内容被游戏标记为实验性，如果存档启用了这些数据包，则玩家在尝试加载存档时会弹出实验性设置警告屏幕。

目前会触发实验性设置的数据包内容都是不可热重载的内容，即必须通过重新加载存档来加载的内容。只要客户端接收到的数据包内容和原版数据包内容不同，就会触发实验性设置屏幕。

# 目录结构

- [图:File archive.png：Minecraft中archive的精灵图]/[图:File directory.png：Minecraft中directory的精灵图] ``` < 数据包名称 > ``` ：根目录。 - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ``` ：数据包元数据。 - [图:File file.png：Minecraft中file的精灵图] ``` pack.png ``` ：数据包图标。 - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` datapacks ``` ：实验性内容的内置数据包目录，仅限于游戏内部使用，无法由自定义数据包提供。 - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` ：函数文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` structure ``` ：结构模板文件目录。 - - 以下所有文件均为JSON文件： - [图:File directory.png：Minecraft中directory的精灵图] ``` advancement ``` ：进度文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` banner_pattern ``` ：旗帜图案文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` cat_variant ``` ：猫变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` chat_type ``` ：聊天类型文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` chicken_variant ``` ：鸡变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` cow_variant ``` ：牛变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` damage_type ``` ：伤害类型文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` decorated_pot_pattern ``` ：饰纹陶罐图案文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` dialog ``` ：对话框文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` dimension ``` ：维度文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` dimension_type ``` ：维度类型文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` enchantment ``` ：魔咒文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` enchantment_provider ``` ：魔咒提供器文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` frog_variant ``` ：青蛙变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` instrument ``` ：山羊角乐器文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` item_modifier ``` ：物品修饰器文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` jukebox_song ``` ：唱片机曲目文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` loot_table ``` ：战利品表文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` number_provider ``` ：数值提供器文件目录 - [图:File directory.png：Minecraft中directory的精灵图] ``` painting_variant ``` ：画变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` predicate ``` ：谓词文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` pig_variant ``` ：猪变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` recipe ``` ：配方文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` slot_source ``` ：槽位源文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` sulfur_cube_archetype ``` ：硫方怪原型文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` tags ``` ：数据包标签根目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` ：函数标签目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` < 注册名 > ``` ：此注册项的标签目录。绝大多数注册项都可以定义标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` timeline ``` ：时间线文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` test_environment ``` ：测试环境文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` test_instance ``` ：测试实例文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` trade_set ``` ：交易集文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` trial_spawner ``` ：试炼刷怪笼配置文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` trim_material ``` ：纹饰材料文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` trim_pattern ``` ：纹饰图案文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` villager_trade ``` ：村民交易文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` wolf_sound_variant ``` ：狼音效变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` wolf_variant ``` ：狼变种文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` world_clock ``` ：世界时钟文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` worldgen ``` ：世界生成根目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` biome ``` ：生物群系文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` carver ``` ：已配置的雕刻器文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` configured_carver ``` ：已配置的雕刻器文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` configured_feature ``` ：已配置的地物文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` density_function ``` ：密度函数文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` feature ``` ：已配置的地物文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` flat_level_generator_preset ``` ：超平坦世界生成预设文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` material_condition ``` ：材料规则文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` material_rule ``` ：材料条件文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` multi_noise_biome_source_parameter_list ``` ：多噪声生物群系源参数列表文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` noise ``` ：噪声文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` noise_settings ``` ：噪声设置文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` placed_feature ``` ：已放置的地物文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` processor_list ``` ：处理器列表文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` structure ``` ：结构文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` structure_set ``` ：结构集文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` template_pool ``` ：模板池文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` world_preset ``` ：世界预设文件目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` zombie_nautilus_variant ``` ：僵尸鹦鹉螺变种文件目录。

# 数据包基础结构

## 数据包元数据

主条目：pack.mcmeta
数据包需要指定元数据才能被游戏识别为一个数据包。数据包元数据位于数据包根目录，其名称为
```
pack.mcmeta
```

，使用JSON格式，内部元素如下：

- [图:NBT复合标签/JSON对象]：根对象。 - [图:NBT复合标签/JSON对象]*pack：存放数据包信息。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*description：（文本组件）数据包的描述信息。在创建世界的数据包页面，或光标在 ``` / datapack list ``` 命令列出的数据包名称上悬停时，会显示此描述。 - [图:整型][图:整型数组]*min_format：数据包兼容的最低版本号，为两个整数组成的数组，依次为主要版本号和次要版本号。单个整数被视为次要版本号 ``` 0 ``` ，如 ``` 94 ``` 、 ``` [94] ``` 等价于 ``` [94, 0] ``` 。 - [图:整型][图:整型数组]*max_format：数据包兼容的最高版本号，为两个整数组成的数组，依次为主要版本号和次要版本号。单个整数被视为次要版本号 ``` 0x7fffffff ``` 。 - [图:整型]pack_format：已弃用，为兼容性而保留。数据包的基础版本。 - [图:整型][图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]supported_formats：已弃用，为兼容性而保留。此数据包支持的数据包版本范围。 - - 整数范围，见Template:Nbt inherit/int inclusive range/source - [图:NBT复合标签/JSON对象]overlays：指定要覆盖的部分，即应用在“标准”包内容上的子包。其目录是其自己的资源和 ``` data ``` 目录（存放于包的根目录下）。 - [图:NBT列表/JSON数组]*entries：覆盖列表。其顺序很重要，列表中的第一个对象将被首先应用。 - [图:NBT复合标签/JSON对象] - [图:字符串]*directory：此子包所在的相对路径。允许的字符： ``` a-z ``` 、 ``` 0-9 ``` 、 ``` _ ``` 和 ``` - ``` 。 - [图:整型][图:整型数组]min_format：此叠加数据包生效的最低版本号。 - [图:整型][图:整型数组]max_format：此叠加数据包生效的最高版本号。 - [图:整型][图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]*formats：已弃用，为兼容性而保留。此叠加数据包生效的数据包版本范围。 - - 整数范围，见Template:Nbt inherit/int inclusive range/source - [图:NBT复合标签/JSON对象]filter：包过滤器，用于指定数据包要忽略的文件。在[图:NBT列表/JSON数组]block内被匹配到的任何模式都将形如其不在该数据包中存在。 - [图:NBT列表/JSON数组]block：模式列表。 - [图:NBT复合标签/JSON对象]： - [图:字符串]namespace：一个正则表达式，表示要滤除文件的命名空间。若省略则匹配所有命名空间。 - [图:字符串]path：一个正则表达式，表示要滤除文件的路径。若省略则匹配所有文件。 - [图:NBT复合标签/JSON对象]features：要启用的实验性内容。注意：如果添加了该字段，则该数据包需要在创建新世界的时候添加，否则在更改旧世界的level.dat前无法添加。 - [图:NBT列表/JSON数组]*enabled：启用的内容。 - [图:字符串]：（命名空间ID）一项实验性内容。可用值见实验性内容 § 数据值。

### 示例

以下为
```
pack.mcmeta
```

的编写示例：

```
{

    
"pack"
:
 
{

        
"description"
:
 
"示例数据包"
,

		
"pack_format"
:
 
81
,

        
"supported_formats"
:
 
[
48
,
 
81
]

    
}

}
```

```
{

    
"pack"
:
 
{

        
"description"
:
 
"示例数据包"
,

		
"min_format"
:
 
[
88
,
 
0
],

        
"max_format"
:
 
[
107
,
 
1
]

    
}

}
```

```
{

    
"pack"
:
 
{

        
"description"
:
 
"示例数据包，同时支持旧版与新版格式"
,

		
"pack_format"
:
 
107
,

        
"supported_formats"
:
 
[
48
,
 
107
],

		
"min_format"
:
 
48
,

        
"max_format"
:
 
[
107
,
 
1
]

    
}

}
```

## 数据包图标

数据包根目录下可以添加一个
```
pack.png
```

作为数据包的图标，这个图标会在创建新的世界屏幕中的数据包列表中渲染。

如果数据包没有图标，或图标加载错误，游戏会使用默认资源包纹理
```
assets/minecraft/textures/misc/unknown_pack.png
```

作为此数据包的图标。

# 数据包内容

数据包的具体内容详见§ 目录结构，以下介绍内容的加载。

数据包的
```
data
```

下包含了不同的命名空间目录，每个命名空间目录下的每个文件夹都对应了一个注册项，以存储不同的数据包内容。在加载数据包时：

- 每个位于数据包 ``` data/< 命名空间 >/< 注册名 >/< 路径 >.json ``` 的文件会在对应的注册项下注册ID为 ``` < 命名空间 >:< 路径 > ``` 的内容。 - 尽管函数和结构模板不属于注册项，但加载过程类似。
- 每个位于数据包 ``` data/< 命名空间 >/tags/< 注册名 >/< 路径 >.json ``` 的文件会在对应的注册项下注册ID为 ``` < 命名空间 >:< 路径 > ``` 的标签。引用标签时通常会带上 ``` # ``` 前缀，即 ``` #< 命名空间 >:< 路径 > ``` 。 - 结构模板、进度和配方不具有标签。

如果加载了多个数据包，且不同的数据包对同一个文件进行了定义，则上层数据包的文件优先级高于下层数据包的文件。

如果数据包具有叠加目录，则叠加目录的内容会覆盖数据包本体的对应内容。此覆盖是完全覆盖，即使对应文件的加载行为是默认合并，此数据包也只会加载最后一个叠加数据包的数据。

# 数据包版本

 提示：本章节的主题不是数据版本。

下表粗略描述了各正式版的数据包版本编号及其数据包内容的变化：

# 历史

 关于数据包版本历史，请见“数据包/版本”。

# 参见

- 附加包
- 资源包
- Tutorial:制作数据包
- Tutorial:优化数据包

# 外部链接

- misode.github.io，一个数据包生成器。
- Pack.mcmeta Generator on misode.github.io，pack.mcmeta生成器。

# 参考

1. ↑ MC-187938 — 漏洞状态为“无效”。
1. ↑ MC-260446 — 漏洞状态为“无效”。
1. ↑ MC-260452 — 漏洞状态为“无效”。
1. ↑ MC-272540 — 漏洞状态为“有意为之”。
1. ↑ MC-273807 — 漏洞状态为“无效”。

# 导航
