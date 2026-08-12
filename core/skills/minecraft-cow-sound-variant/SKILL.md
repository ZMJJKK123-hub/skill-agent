---
name: minecraft-cow-sound-variant
description: |
  牛音效变种定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】牛音效变种定义文件是牛音效变种（Cow Sound Variant）在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：COW_SOUND_VARIANT
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 牛音效变种定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
牛音效变种定义文件是牛音效变种（Cow Sound Variant）在数据包中的数据驱动定义文件。

# 定义格式

牛音效变种在游戏内使用
```
COW_SOUND_VARIANT
```

注册表，数据包路径为
```
cow_sound_variant
```

，即所有牛音效变种自定义文件都需要在
```
data/<
命名空间
>/cow_sound_variant
```

目录中定义。

牛音效变种定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*adult_sounds：成年牛使用的音效。 - [图:字符串][图:NBT复合标签/JSON对象]*ambient_sound：牛空闲音效使用的声音事件。可以为一个声音事件的命名空间ID，也可以直接定义一个新的声音事件。下方字段格式与此相同。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*death_sound：牛死亡音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*hurt_sound：牛受伤音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*step_sound：牛行走音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:NBT复合标签/JSON对象]*baby_sounds：幼年牛使用的音效。 - 格式同[图:NBT复合标签/JSON对象]adult_sounds。

# 定义行为

牛音效变种定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使牛音效变种定义被重新加载，而必须重启服务端。

```
COW_SOUND_VARIANT
```

注册表中必须至少有一个元素，否则游戏会在同步时报错并阻止世界加载。

牛音效变种与牛变种相互独立，牛生成后会从世界内已注册的所有牛音效变种数据内随机选择一项作为自己的音效。这些音效会在牛的不同状态下播放。

满足条件时立刻播放的音效：

- ``` hurt_sound ``` ：牛受伤时播放。
- ``` death_sound ``` ：牛死亡时播放。
- ``` step_sound ``` ：牛行走时播放。

满足条件时随机播放的音效：

- ``` ambient_sound ``` ：牛空闲时播放。

# 历史

# 导航
