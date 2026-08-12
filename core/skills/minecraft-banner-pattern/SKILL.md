---
name: minecraft-banner-pattern
description: |
  旗帜图案定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】提示：本条目的主题不是旗帜图案。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：BANNER_PATTERN
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 旗帜图案定义格式 的完整规范时
---

提示：本条目的主题不是旗帜图案。

本条目所述内容仅适用于Java版。
旗帜图案（Banner Pattern）定义了旗帜和盾牌可用的图案类型。旗帜图案定义文件是旗帜图案在数据包中的数据驱动定义文件。

# 定义格式

旗帜图案在游戏内使用
```
BANNER_PATTERN
```

注册表，数据包路径为
```
banner_pattern
```

，即所有旗帜图案定义文件都需要在
```
data/<
命名空间
>/banner_pattern
```

目录内定义，旗帜图案标签则需要在
```
data/<
命名空间
>/tags/banner_pattern
```

目录内定义。

旗帜图案定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]* *asset_id：（命名空间ID）旗帜图案使用的纹理，游戏在渲染时会将此值解析为 ``` assets/< 命名空间 >/textures/entity/banner/< 路径 >.png ``` （旗帜）和 ``` assets/< 命名空间 >/textures/entity/shield/< 路径 >.png ``` （盾牌）。 - [图:字符串]* *translation_key：旗帜图案在提示框中显示名称的翻译键的前缀，游戏会根据这一层图案的颜色使用 ``` < 此值 >.< 颜色名称 > ``` 作为完整的翻译键。

# 定义行为

旗帜图案定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使旗帜图案定义被重新加载，而必须重启服务端。

旗帜图案定义了单层图案所使用的图案样式，而每一层图案都包括图案样式和图案颜色，游戏会按照旗帜图案列表顺序依次渲染，后层图案会覆盖前层图案。

单层旗帜图案的名称由图案样式[图:字符串]translation_key和图案颜色决定。例如，单层图案的翻译键为
```
block.minecraft.banner.custom.pattern
```

、颜色为红色时，游戏解析的完整的翻译键名为
```
block.minecraft.banner.custom.pattern.red
```

。

# 历史

# 参考

1. ↑ MC-271587 — 漏洞状态为“无效”。

# 导航
