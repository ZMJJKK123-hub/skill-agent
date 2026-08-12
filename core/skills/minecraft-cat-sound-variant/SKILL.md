---
name: minecraft-cat-sound-variant
description: |
  猫音效变种定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】猫音效变种定义文件是猫音效变种（Cat Sound Variant）在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：CAT_SOUND_VARIANT
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 猫音效变种定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
猫音效变种定义文件是猫音效变种（Cat Sound Variant）在数据包中的数据驱动定义文件。

# 定义格式

猫音效变种在游戏内使用
```
CAT_SOUND_VARIANT
```

注册表，数据包路径为
```
cat_sound_variant
```

，即所有猫音效变种自定义文件都需要在
```
data/<
命名空间
>/cat_sound_variant
```

目录中定义。

猫音效变种定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*adult_sounds：成年猫使用的音效。 - [图:字符串][图:NBT复合标签/JSON对象]*ambient_sound：猫空闲音效使用的声音事件。可以为一个声音事件的命名空间ID，也可以直接定义一个新的声音事件。下方字段格式与此相同。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*beg_for_food_sound：猫求食音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*death_sound：猫死亡音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*eat_sound：猫进食音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*hiss_sound：猫威慑幻翼音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*hurt_sound：猫受伤音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*purr_sound：猫呼噜声音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*purreow_sound：猫驯服后空闲音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]*stray_ambient_sound：猫驯服前空闲音效使用的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:NBT复合标签/JSON对象]*baby_sounds：幼年猫使用的音效。 - 格式同[图:NBT复合标签/JSON对象]adult_sounds。

# 定义行为

猫音效变种定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使猫音效变种定义被重新加载，而必须重启服务端。

```
CAT_SOUND_VARIANT
```

注册表中必须至少有一个元素，否则游戏会在同步时报错并阻止世界加载。

猫音效变种与猫变种相互独立，猫生成后会从世界内已注册的所有猫音效变种数据内随机选择一项作为自己的音效。这些音效会在猫的不同状态下播放。

满足条件时立刻播放的音效：

- ``` hurt_sound ``` ：猫受伤时播放。
- ``` death_sound ``` ：猫死亡时播放。
- ``` eat_sound ``` ：猫进食时播放。

满足条件时随机播放的音效：

- ``` hiss_sound ``` ：猫威慑幻翼时播放。
- ``` beg_for_food_sound ``` ：猫求食时播放。
- ``` purr_sound ``` ：猫发出呼噜声时播放。
- ``` purreow_sound ``` ：猫被驯服后空闲时播放。
- ``` stray_ambient_sound ``` ：猫未被驯服时播放。
- ``` ambient_sound ``` ：猫空闲时播放（与 ``` purreow_sound ``` 或 ``` purreow_sound ``` 交替随机播放）。

# 历史

# 导航
