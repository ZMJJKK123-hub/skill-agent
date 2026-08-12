---
name: minecraft-json
description: |
  JSON（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是一种轻量级数据交换格式。关于NBT以及JSON的语法和用法，请见“Tutorial:NBT与JSON”。
  
  【涵盖内容】
  - JSON文本
  - JSON数据值
  - 对象
  - 数组
  - 字符串
  - 数字
  - 布尔
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 JSON 的完整规范时
---

本条目介绍的是一种轻量级数据交换格式。关于NBT以及JSON的语法和用法，请见“Tutorial:NBT与JSON”。

JavaScript对象表示法（JSON，JavaScript Object Notation）是一种轻量级数据交换格式。

Minecraft使用JSON来储存以下数据：

- 在基岩版中，在成书、告示牌、自定义名称以及 ``` / tellraw ``` 和 ``` / titleraw ``` 命令里的文本。
- 描述Java版中资源包和数据包的 ``` pack.mcmeta ``` 文件。
- 描述基岩版附加包的 ``` manifest.json ``` 。
- 在资源包里定义模型、声音事件和UI的文件。
- 在行为包中定义实体行为的文件。
- 进度和统计（例如 ``` .minecraft/saves/*/data/stats/*.json ``` ）。
- 用于启动器的档案数据（例如 ``` .minecraft/ launcher profiles.json ``` ）。
- 关于已下载的版本的信息（例如 ``` .minecraft/versions/<版本>/ <游戏版本>.json ``` ）。
- 在Java版中，在数据包中定义进度、战利品表、标签、配方、维度、维度类型、谓词等内容的文件。

# JSON语句规范

本条目主要描述Minecraft中的JSON语句规范，可能与JSON的原始标准定义有所区别。虽然JSON可以写在一行内，但是一般为了可读性会加入缩进和换行。

对于具体细节，参考ECMA的JSON标准。

## JSON文本

JSON文本是一组符合JSON数据值语法的，由万国码（Unicode）代码点组成的符号序列。这些符号包括六类结构化符号、字符串、数字值以及三类字面量符号。

六类结构化符号：

- ``` [ ``` ：左方括号。
- ``` { ``` ：左花括号。
- ``` ] ``` ：右方括号。
- ``` } ``` ：右花括号。
- ``` : ``` ：冒号。
- ``` , ``` ：逗号。

三类字面量符号：

- ``` true ``` 。
- ``` false ``` 。
- ``` null ``` 。

其中，
```
null
```

未在Minecraft的数据包标准文件中使用。

## JSON数据值

JSON数据值类型可以为：[图:NBT复合标签/JSON对象]对象（object）、[图:NBT列表/JSON数组]数组（array）、[图:字符串]字符串（string）、[图:字节型][图:短整型][图:整型][图:长整型][图:单精度浮点数][图:双精度浮点数]数值（number）、[图:布尔型]布尔（boolean）或[图:空]空（
```
null
```

）。

### 对象

一个对象，以左右花括号作为首尾，包含0个或若干个键值对。每个键都为一个字符串，其后都使用一个冒号与值相连接。多个不同的键值对间以逗号分隔。对象中所有键值对都由一个键名唯一确定，不能出现同名键。键值对中的值也可以是任意的JSON数据值类型。

```
{

    
"Bob"
:
 
{

        
"ID"
:
 
1234
,

        
"lastName"
:
 
"Ramsay"

    
},

    
"Alice"
:
 
{

        
"ID"
:
 
2345
,

        
"lastName"
:
 
"Berg"

    
}

}
```

### 数组

一个数组，以左右方括号作为首尾，包含0个或若干个以逗号隔开的数据值。与NBT中的[图:NBT列表/JSON数组]列表不同，JSON数组中的数据值可以为不同的数据类型。

```
[
"Bob"
,
 
"Alice"
,
 
"Carlos"
,
 
"Eve"
]
```

### 字符串

每个字符串都被一对双引号
```
"
```

所括，其中包含任意字符的组合。某些特殊字符需要通过反斜杠
```
\
```

进行转义。

- ``` "foo" ```
- ``` "Hello, world" ```
- ``` "An escaped \" quote within a string" ```

### 数字

连续输入键盘上的任意数字即可得到一个数值。数值可以加入小数点以表示小数，也可以使用
```
e
```

表示指数。

- ``` 2 ```
- ``` -0.5 ```
- ``` 3e6 ``` (=3×10)

### 布尔

布尔值只能为
```
true
```

或
```
false
```

。

```
{

    
"Steve"
:
 
{

        
"isAlive"
:
 
true

    
},

    
"Alex"
:
 
{

        
"isAlive"
:
 
false

    
}

}
```

# 序列化

序列化（Serialization）也即串行化，是一种将内存程序转换为方便网络传输和数据存储的方法。在Minecraft中，许多与数据包有关的内容都可以被序列化为JSON格式。所以JSON也是一种用来表示游戏内程序对象的一种文本格式。

在数据包被加载时，游戏会尝试将数据包内的JSON文件反序列化（Deserialization）以尝试在内存中还原出一个相应的程序对象。对于JSON所描述的各种JSON数据，基本都要再经过游戏程序本身进行验证——多余的JSON对象可能会被直接丢弃，且会对原JSON数值的范围进行重新计算。在一些严格的验证条件下，这可能导致一些非法的JSON值在数据包加载期间使游戏抛出异常，从而阻断数据包的正常加载。另外，由于要还原出一个完整的程序对象，必须使用JSON给出所有“必要”的对象属性值，否则也会导致加载异常。

# 参考

1. ↑ https://www.json.org/json-zh.html
1. ↑ https://ecma-international.org/wp-content/uploads/ECMA-404_2nd_edition_december_2017.pdf

# 导航
