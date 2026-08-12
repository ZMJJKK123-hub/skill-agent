---
name: minecraft-tag-function
description: |
  Java版标签/函数（Minecraft Wiki 中文版全量正文）。
  
  【概述】函数标签（Function Tags）是函数的组合。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 数据包路径：data/minecraft/tags/function/load.json
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/函数 的完整规范时
---

本条目所述内容仅适用于Java版。
函数标签（Function Tags）是函数的组合。

# 使用

 参见：Java版函数 § 通过函数标签 
函数标签可以在
```
/
function
```

命令中使用，该命令会按标签中首次出现的顺序运行标签中指定的所有函数。如果一个函数在标签及其子标签中被多次引用，它只会运行一次。

游戏内部提供了两个特殊标签：

- 在 ``` #load ``` 标签中列出的函数将在世界加载时或者服务器被启动时执行。每当数据包重载时，这些函数也将被执行。

- 在 ``` #tick ``` 标签中列出的函数将在每一刻开始时执行。随着游戏刻递增，这些函数持续反复执行。

原版数据包中没有使用这些函数标签。

# 示例

以下示例在
```
minecraft
```

命名空间下定义了
```
#load
```

标签，并加入
```
example:test
```

函数。

[图:File file.png：Minecraft中file的精灵图] 
```
data/minecraft/tags/function/load.json
```

json

```
{

  
"values"
:
 
[

    
"example:test"

  
]

}
```

游戏将会在数据包加载时运行一次
```
example:test
```

函数。

# 历史

# 参考

1. ↑ MC-187539 — 漏洞状态为“已修复”。

# 导航
