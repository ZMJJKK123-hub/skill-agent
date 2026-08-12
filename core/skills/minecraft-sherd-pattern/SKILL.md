---
name: minecraft-sherd-pattern
description: |
  饰纹陶罐图案定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】本页面包含会在下一次更新中出现的内容。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：DECORATED_POT_PATTERN
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 饰纹陶罐图案定义格式 的完整规范时
---

本页面包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

饰纹陶罐图案（Decorated Pot Pattern）定义了饰纹陶罐可用使用的图案类型。饰纹陶罐图案定义文件是饰纹陶罐图案在数据包中的数据驱动定义文件。

# 定义格式

饰纹陶罐图案在游戏内使用
```
DECORATED_POT_PATTERN
```

注册表，数据包路径为
```
decorated_pot_pattern
```

，即所有饰纹陶罐图案定义文件都需要在
```
data/<
命名空间
>/decorated_pot_pattern
```

目录内定义，饰纹陶罐图案标签则需要在
```
data/<
命名空间
>/tags/decorated_pot_pattern
```

目录内定义。

饰纹陶罐图案定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]* *asset_id：（命名空间ID）饰纹陶罐图案使用的纹理，游戏在渲染时会将此值解析为 ``` assets/< 命名空间 >/textures/entity/decorated_pot/< 路径 >.png ``` 。

# 定义行为

饰纹陶罐图案定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使饰纹陶罐图案定义被重新加载，而必须重启服务端。

游戏在渲染饰纹陶罐的侧面时，会先获取饰纹陶罐的图案数据，然后根据每个面的物品进行渲染。如果对应面的物品不存在，或物品没有provides_pottery_pattern组件，则这一面渲染为无图案（
```
minecraft:decorated_pot_side
```

）；否则，根据物品
```
provides_pottery_pattern
```

组件指定的饰纹陶罐样式所对应的精灵图进行渲染。

# 历史

# 导航
