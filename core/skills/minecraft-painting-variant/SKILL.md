---
name: minecraft-painting-variant
description: |
  画变种定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】画变种（Painting Variant）决定了画的内容和尺寸等数据。画变种定义文件是画变种在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - 提示框
  
  【关键定义】
  - 注册表：PAINTING_VARIANT
  - 数据包路径：data/painting/variant
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 画变种定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
画变种（Painting Variant）决定了画的内容和尺寸等数据。画变种定义文件是画变种在数据包中的数据驱动定义文件。

# 定义格式

画变种在游戏内使用
```
PAINTING_VARIANT
```

注册表，数据包路径为
```
painting_variant
```

，即所有画变种定义文件都需要在
```
data/<
命名空间
>/painting_variant
```

目录中定义，画变种标签则需要在
```
data/<
命名空间
>/tags/painting_variant
```

目录中定义。

画变种定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*width：（1≤值≤16）画的宽度，以方块为单位。 - [图:整型]*height：（1≤值≤16）画的高度，以方块为单位。 - [图:字符串]*asset_id：（命名空间ID）画使用的纹理，游戏在渲染时将此值解析为 ``` assets/< 命名空间 >/textures/painting/< 路径 >.png ``` 。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]title：（文本组件）画的标题。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]author：（文本组件）画的作者。

# 定义行为

画变种定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使画变种定义被重新加载，而必须重启服务端。

```
PAINTING_VARIANT
```

注册表中必须至少有一个元素，否则游戏会在同步时报错并阻止世界加载。

画在游戏中有大小、纹理不一的不同变种。根据定义数据，相应变种的画宽为[图:整型]width格、高为[图:整型]height格。

## 提示框

画物品会根据其
```
painting/variant
```

组件指定的画变种在提示框中显示画尺寸。如果指定了画的作者或标题则也会一并显示。

# 历史

# 导航
