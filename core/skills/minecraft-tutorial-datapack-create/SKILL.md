---
name: minecraft-tutorial-datapack-create
description: |
  Tutorial:制作数据包（Minecraft Wiki 中文版全量正文）。
  
  【概述】本教程介绍的是Java版制作数据包的方法。关于基岩版上与之功能类似的行为包，请见“Tutorial:制作行为包”。
  
  【涵盖内容】
  - 相关问题
  - pack.mcmeta
  - 命名空间
  - 命名空间ID和注册表
  - 函数概要
  - .json文件
  - JSON和SNBT结构补全
  - .nbt结构文件
  - 参考原版数据包
  - 与资源包共同作用
  - 实例
  
  【关键定义】
  - 数据包路径：data/.minecraft/saves/temp/generated/test/structures、data/.minecraft/saves/temp/generated/test/structures/test/bar.nbt
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Tutorial:制作数据包 的完整规范时
---

本教程介绍的是Java版制作数据包的方法。关于基岩版上与之功能类似的行为包，请见“Tutorial:制作行为包”。

本教程所述内容仅适用于Java版。
本教程介绍如何制作数据包。数据包允许玩家添加或修改函数、战利品表、世界结构、进度、配方、谓词、标签、维度和自定义世界生成等Minecraft游戏内容。

本教程建议学习者事先具备命令方块和JSON、SNBT基础。

# 概述

数据包是什么？

数据包可以是一个文件夹或压缩包，你可以通过数据包在原版自定义一些游戏内容。

数据包是Mod吗？它们的区别是什么？

数据包不是传统意义上的Mod。Mod目前仅由第三方的Mod端支持，并且Mod涉及对游戏Java源码的直接拆解。数据包受到原版支持，但其只能在原版代码的框架上为固定的接口提供有限的数据定义。如果将Minecraft比作一个大型工厂，那Mod则可以为这个工厂添加新的产线机器，而数据包和资源包只能为固定产线提供符合规定的原料。

数据包的用途

与Mod一样，数据包也可以为游戏添加新的游戏内容，只是这些内容的类型都是由游戏源码预先定义好的。数据包也通常被用于制作原版地图——通过数据包触发命令，实现地图中的各种机关，配合资源包，实现更加独特的艺术表现力。

# 准备工作

本节主要内容为安装Visual Studio Code（下文称VS Code）软件及配置相应扩展。VS Code是如今很多数据包制作者都常用的编辑软件，可以很方便地安装扩展，有些扩展可极大提升编辑体验。

- VS Code官网

点击以上链接进入官网后，点击左下角的“Download for”按钮以安装官网所推荐的VS Code版本。右上角的“Download”按钮可以手动选择要安装的VS Code平台版本。更详细的安装细节在此不过多阐述。

安装完成后，打开VS Code。如果你的界面语言为英文，可以在侧边栏找到“Extension”图标，点击后在展开区域上方的输入框中输入“Chinese”，找到“Chinese (Simplified) ”（简体中文）或“Chinese (Traditional) ”（繁体中文）并点击“Install”按钮以安装中文语言套件。

点击侧边栏的“Extension”（扩展）图标，在搜索框中输入“mcfunction”，找到“syntax-mcfunction”扩展，点击“Install”（安装）按钮安装。

点击侧边栏的“Extension”（扩展）图标，在搜索框中输入“spyglass”，找到“Datapack Helper Plus by Spyglass”扩展，点击“Install”（安装）按钮安装。

请确保你已经安装了“syntax-mcfunction”扩展，否则“Datapack Helper Plus by Spyglass”可能无法运行。

## 相关问题

此段内容过长，请通过显示按钮阅读

该章节主要讲述了扩展安装失败的一种解决方法，你可以先跳过该章节。

如果在初始化Spyglass时弹出连接错误提示，则可参考如下解决方法：

进入网址
```
https://tool.chinaz.com/dns
```

，点击“DNS查询”，输入
```
raw.githubusercontent.com
```

，在查询出的“解析内容”中选择一个地址复制。

然后在你的操作系统中找到
```
hosts
```

文件。在Windows 11系统中，该文件位于
```
C:\Windows\System32\drivers\etc
```

。你可以右键hosts文件，选择“通过 Code 打开”。在hosts文件中添加你刚才复制的地址，并随后加上
```
raw.githubusercontent.com
```

。例如：

```
185.199.111.133 raw.githubusercontent.com	
```

同样方法，继续添加
```
github.com
```

的DNS解析地址：

```
185.199.111.133 raw.githubusercontent.com	
20.205.243.166 github.com
```

然后按Ctrl+S保存。此时如果弹出无法保存的提示，请选择“Retry as Admin”（以管理员权限重试），之后便成功保存。

为了确保扩展初始化正常，之后应点击“Datapack Helper Plus by Spyglass”的齿轮图标，选择“Uninstall”（卸载）以卸载扩展，然后再次安装。

现在，在你的命名空间新建一个函数文件：

- [图:File directory.png：Minecraft中directory的精灵图] ``` Test ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` test ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` - [图:File file.png：Minecraft中file的精灵图] ``` test.mcfunction ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ```

在函数中键入命令，看看是否会有自动补全提示框出现。如果没有任何影响，或依然出现扩展错误提示，可以在你的工作区根目录中添加一个
```
spyglass.json
```

文件：

- [图:File directory.png：Minecraft中directory的精灵图] ``` TEST ``` - [图:File file.png：Minecraft中file的精灵图] ``` spyglass.json ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` test ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` - [图:File file.png：Minecraft中file的精灵图] ``` test.mcfunction ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ```

[图:File file.png：Minecraft中file的精灵图] 
```
spyglass.json
```

json

```
{

    
"env"
:
 
{

        
"dataSource"
:
 
"jsDelivr"

    
}

}
```

该解决方案来自：Spyglass Issue#1445 -  Server initialization failed。

然后再关闭VS Code，重新进入。若等待一段时间后扩展依然报错后无法正常使用，你可再尝试卸载“Datapack Helper Plus by Spyglass”扩展，重复该章节的步骤。

# 创建数据包

 参见：命令/datapack、​Java版存档格式以及.minecraft 
在1.21.6以上的正式版，你可以按照如下步骤创建数据包：

（1）在聊天栏执行命令：

```
/
datapack
 
create
 
my_example
 
"这是一条介绍"
```

（2）进入单人游戏的“选择世界”界面，选中一个世界，点击左下角的“编辑”按钮。

（3）在“编辑世界”界面中，点击“打开世界文件夹”按钮。

（4）在弹出的系统界面中，找到
```
datapacks
```

文件夹。进入
```
datapacks
```

文件夹，你可以看到使用
```
/
datapack
 create
```

命令所创建的
```
my_example
```

数据包。

（5）在1.21.5及以下的版本，除了第（1）步执行的命令不可用外，其余步骤大致相同。总之，你应确保在存档
```
datapacks
```

目录中包含以下结构的文件夹：

- [图:File directory.png：Minecraft中directory的精灵图] ``` my_example ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ```

## pack.mcmeta

 参见：pack.mcmeta 
```
pack.mcmeta
```

是数据包所必须的文件，因为Minecraft通过该文件识别数据包。

生成的数据包中已经包含该文件。你还可以尝试修改
```
pack.mcmeta
```

的内容：

```
{

    
"pack"
:
 
{

        
"description"
:
 
{
"text"
:
"教程数据包"
,
 
"color"
:
"gold"
},

		
"min_format"
:
 
88
,

        
"max_format"
:
 
88

    
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
 
{
"text"
:
"教程数据包"
,
 
"color"
:
"gold"
},

		
"pack_format"
:
 
81
,

        
"supported_formats"
:
 
[
0
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
 
{
"text"
:
"教程数据包"
,
 
"color"
:
"gold"
},

		
"pack_format"
:
 
88
,

        
"supported_formats"
:
 
[
48
,
 
88
],

		
"min_format"
:
 
48
,

        
"max_format"
:
 
88

    
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
 
{
"text"
:
"教程数据包"
,
 
"color"
:
"gold"
},

		
"pack_format"
:
 
9999
,

        
"supported_formats"
:
 
[
0
,
 
9999
],

		
"min_format"
:
 
0
,

        
"max_format"
:
 
9999

    
}

}
```

```
pack_format
```

是数据包的版本编号。在游戏内按下F3+V后将显示当前游戏的版本信息，其中
```
pack_data
```

即当前游戏对应的数据包版本编号。历史版本编号参见数据包 § 数据包版本。如果你认为你的数据包不止支持这一个版本，则还可以通过
```
supported_formats
```

设置数据包的版本编号范围。

更多字段建议对照数据包 § pack.mcmeta，并在VS Code中自动补全相关字段（自动补全由之前所安装的DHP扩展提供）。默认情况下，按Tab ↹即可自动补全提示框中的所选字段。

虽然
```
pack_format
```

等版本编号字段与对应版本不匹配时，会在数据包选择界面中将该数据包渲染为“不兼容的数据包”，但这并不代表该数据包在该版本下一定无法运作。实际上，版本编号一般用于提醒用户尽量选择更合适的版本而非“唯一可用的版本”。数据包的目录结构和文件内容才是决定数据包加载是否成功的核心因素。

执行
```
/
datapack
 list
```

，看看你的数据包是否已经启用：

已启用2个数据包：[vanilla（内置）]，[file/my_example（世界）]

如果
```
/
datapack
 list
```

命令执行后没有看到你的数据包，请检查：

- 如果你没有使用 ``` / datapack create ``` 命令而是手动创建数据包目录结构，是否保存了 ``` pack.mcmeta ``` 文件。若未保存，则该文件可能为一个不包含任何内容的空文件，游戏将不会读取到任何关于数据包的内容。
- ``` pack.mcmeta ``` 文件是否符合JSON语法。一般情况下，语法错误会直接在配置了前述扩展的VS Code中以红色标示出来。你应检查是否缺漏大括号 ``` {} ``` 、逗号 ``` , ``` 、冒号 ``` : ``` ，双引号 ``` "" ``` ，方括号 ``` [] ``` ；是否存在多余逗号 ``` , ``` 。请记住，对于每个左大括号、双引号或方括号，必须有一个右大括号、双引号或方括号与之配对；JSON中的每一个字段名都必须被英文双引号包裹（这可不是SNBT！）。
- 数据包目录结构是否正确。请确保 ``` pack.mcmeta ``` 文件在数据包文件夹或压缩包的根路径中，否则游戏将无法识别数据包。

# 添加内容

## 命名空间

主条目：命名空间
[图:File directory.png：Minecraft中directory的精灵图] 
```
data
```

目录中允许包含多个命名空间，比如：

- [图:File directory.png：Minecraft中directory的精灵图] ``` my_example ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` ：原版命名空间。 - [图:File directory.png：Minecraft中directory的精灵图] ``` test ``` ：test命名空间。

注意，数据包中的命名空间、路径、文件夹名和文件名应仅包含以下符号：

- ``` 0123456789 ``` 数字
- ``` abcdefghijklmnopqrstuvwxyz ``` 小写字母
- ``` _ ``` 下划线
- ``` - ``` 连字符（减号）
- ``` / ``` 正斜杠（不能用于命名空间）
- ``` . ``` 英文句号

首选命名格式为以下划线隔开的小写字母单词（
```
lower_case_with_underscores
```

），称为蛇形命名法（Snake Case）。

本教程使用
```
test
```

作为
```
data
```

中的自定义命名空间（你可以使用自己喜欢的名称，但是请注意不要违反上述命名规则）。另外，请让命名空间保持独特性，这样可以最大限度地防止数据包冲突。如果实在想不出好的命名空间，不妨使用你的游戏ID。

以上便完成了数据包基本目录结构的创建。

## 命名空间ID和注册表

主条目：命名空间ID和注册表

## 函数概要

主条目：Tutorial:制作数据包/函数
前往该章节对应子页面以了解详情。在该页面中，你将创建你的第一个函数，你将学会函数的相关基本概念以及一些使用、调试技巧。

## .json文件

主条目：Tutorial:制作数据包/JSON文件
在本节中，你将学会一些基本的JSON文件编写技巧，同时了解如何通过解压jar获取JSON文件以及如何通过源码确定JSON格式。

## JSON和SNBT结构补全

Spyglass的DHP扩展提供了非常强大的自动补全功能。善加利用，你可以非常方便地编写大量字段。

查看字段描述信息：

查看字段类型。这里带有方括号，表示它之后是一个元素为MyQuest的列表：

## .nbt结构文件

 参见：教程:结构方块和教程:拼图方块 
结构可以用于结构方块或拼图方块，也可以覆盖Minecraft中原版结构的外观。结构以NBT格式存储，你可以使用结构方块创建NBT文件。MCEdit之类的第三方软件也可以导出NBT文件。

当你使用结构方块成功保存一个结构后，在
```
.minecraft/saves/temp/generated/test/structures/
```

目录及其子目录下，可以看到你保存的.nbt文件。例如，我在结构方块所输入的结构名为
```
test:bar
```

，那么保存后的结构文件路径为：
```
.minecraft/saves/temp/generated/test/structures/test/bar.nbt
```

。

在你的命名空间文件夹中，你可以创建
```
structure
```

文件夹，然后放入刚才通过结构方块保存的结构文件。

## 参考原版数据包

 参见：客户端核心文件 
将位于
```
版本根目录/%版本名%.jar
```

的客户端核心
```
.jar
```

文件解压后，得到的data目录与需要在正在制作的数据包下的data目录结构相同，其内置了大量原版数据包的文件，若在自己的开发中遇到困难，可参考原版数据包进行开发。若要实现的功能仅为原版数据包基础上的微调，可直接复制原版数据包中对应的文件进行微调，这将大大增加开发效率。

## 与资源包共同作用

在很多地图或服务器玩法中，往往需要数据包和资源包共同搭配。在社区中，很多优秀作品也由于其独特的美术风格而脱颖而出。对于这种在非Mod环境下通过资源包或数据包制作“新方块”或“新生物”的游戏包，一些社区玩家将其称为“原版模组”。

相关教程：

- 教程:Java版自定义物品
- 教程:自定义盔甲纹饰

在开发服务器级或模块式的数据包时，你可能需要使用外部工具进行代码生成——包中有大量重复且需要进一步抽象的逻辑层。为了提高互操作性，提高开发效率，你可以考虑使用类似Beet的工具。在设计上，你可将Beet当做“中间处理工厂”——你可以利用Python编写Beet Plugin，并对已有的包文件施加影响。在已有的社区项目中，Gamemode4项目是典型的使用Beet开发的中大型数据包族。

# 开发工具和实用程序

该段落的内容不代表Mojang Studios或Minecraft Wiki的官方意见。
现在有很多的工具可以帮助你更容易地编写数据包。以下列表包含了一些转换器以及语法高亮扩展相关的软件工具。对于这些第三方的程序，要谨慎安装——这些程序并没有受到严格监控，可能包含恶意软件。

# 视频

# 参见

- 数据包
- 资源包
- Tutorial:安装数据包
- Tutorial:制作数据包/函数
- Tutorial:制作数据包/JSON文件
- Tutorial:制作数据包/输入检测

## 实例

- 射线投射
- 视线魔法

# 导航
