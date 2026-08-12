---
name: minecraft-nbt-path
description: |
  NBT路径（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是在命令中检索特定NBT标签的方法。关于NBT网络传输和文件格式，请见“NBT格式”；关于用文本表示的NBT结构，请见“SNBT格式”。
  
  【涵盖内容】
  - 带引号的节点
  - 混合路径
  - 示例1
  - 示例2
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 NBT路径 的完整规范时
---

本条目介绍的是在命令中检索特定NBT标签的方法。关于NBT网络传输和文件格式，请见“NBT格式”；关于用文本表示的NBT结构，请见“SNBT格式”。

本条目所述内容仅适用于Java版。
NBT路径（NBT path）是用来从NBT数据树中指定其中的一个或多个特定元素的描述性字符串。

# 用法

NBT路径的基本格式为
```
节点.节点.….节点
```

，即一个或多个节点由
```
.
```

分隔开来，某些节点前的
```
.
```

可以省略（见下文表格）。其中每个
```
节点
```

声明了可以从当前哪种类型的标签中选择哪种类型的子标签，一个节点应用到一个标签上时，可以从其中选择一个或多个子标签。

不带有标签名的标签汇聚成集，称为标签集（tags collection）。初始标签集仅有一个元素（根标签），NBT路径中的节点会应用于标签集中的元素，得到新标签集。随着路径中节点的逐个应用，标签集不断更迭。直到路径中最后一个节点应用后，所得到的标签集里的所有标签即为该NBT路径所选择的标签。

如果当前标签集中有多个元素，节点会应用于标签集中的每一个元素，分别选择子标签，所选择的所有子标签都放入新的标签集。例如：对于
```
{tag1:1b, tag2:[{foo:0},{foo:[]},{foo:{}}]}
```

，路径
```
tag2
```

所确定标签集中只有一个元素：列表标签
```
[{foo:0},{foo:[]},{foo:{}}]
```

；路径
```
tag2.[]
```

所确定的标签集中有三个元素：三个复合标签
```
{foo:0}
```

、​
```
{foo:[]}
```

和​
```
{foo:{}}
```

；如果在此路径之后再增加节点，则新节点会在这三个元素上分别应用，例如路径
```
tag2.[].foo
```

所确定的标签集中有三个元素：一个整型标签
```
0
```

、一个列表标签
```
[]
```

、一个复合标签
```
{} 
```

。

如
```
/
data
 get ...
```

等命令要求NBT路径所得到的标签集大小为1，即只能选择一个标签。

而如
```
/
data
 modify ...
```

等命令允许NBT路径所得标签集大小大于1，即一次性选择多个标签。

# 节点

节点（node）共有6种。根复合标签节点必须为路径之首，其他所有节点按需随意排列使用。

以下为全部节点的格式：

# 示例

## 带引号的节点

在下列情况下匹配标签名时，节点最外层必须被一对引号包裹：

- 要匹配的标签名本身含有点号 ``` . ``` 时。对于{a.b: 0}中的标签，可使用 ``` 'a.b' ``` 来匹配。
- 要匹配的标签名本身含有空字符（比如空格）时。例如，对于{"a b": 6}中的标签，可使用 ``` 'a b' ``` 来匹配。
- 要匹配的标签名本身含有单引号或双引号时。例如，对于{'"测试"': 1, "'测试'": 2, "\"tes't": 3}中的各标签，所对应的NBT路径为： ``` '"测试"' ``` 、 ``` "'测试'" ``` 、 ``` "\"tes't" ``` 。

## 混合路径

- ``` {} ``` ——指定根标签
- ``` {foo:4.0f} ``` ——指定根标签，如果其foo子标签的值为 ``` 4.0f ``` 。
- ``` foo ``` ——指定根标签下命名为foo的子标签。
- ``` foo.bar ``` 或 ``` foo{}.bar ``` ——指定foo中名为bar的子标签。
- ``` foo.bar[0] ``` ——指定bar（应为列表或数组）中的第一个元素。
- ``` foo.bar[-1] ``` ——指定bar（应为列表或数组）中的最后一个元素。
- ``` foo.bar[0]."A [crazy name]!" ``` ——指定bar（应为列表）中第一个元素（应为复合标签）下命名为"A [crazy name]!"的子标签。
- ``` foo.bar[0]."A [crazy name]!".baz ``` ——指定上述子标签（应为复合标签）中命名为baz的子标签。
- ``` foo.bar[] ``` ——指定bar（应为列表或数组）中的所有元素。
- ``` foo.bar[].baz ``` ——指定bar（应为列表）的所有复合标签元素中命名为baz的子标签。
- ``` foo.bar[{baz:5b}] ``` ——指定bar（应为列表）中所有拥有值为 ``` 5b ``` 的baz子标签的复合标签元素。
- ``` foo{bar:"baz"} ``` ——指定foo子标签，如果其为复合标签且其子标签bar的值为 ``` "baz" ``` 。
- ``` foo{bar:"baz"}.bar ``` ——指定foo子标签（应为复合标签）中的bar子标签，如果其值为 ``` "baz" ``` 。

## 示例1

```
/data get entity @p foo.bar[0]."A [crazy name]!".baz
```

这些标签名称并非真实存在的，仅用于演示。

- ``` foo ``` ——指定根标签下名为foo的子标签。
- ``` foo.bar ``` ——指定上述子标签下名为bar的子标签。
- ``` foo.bar[0] ``` ——指定上述子标签bar（应为数组或列表）中的第一个元素。
- ``` foo.bar[0]."A [crazy name]!" ``` ——指定上述元素（应为复合标签）中的名为"A [crazy name]!"的子标签。
- ``` foo.bar[0]."A [crazy name]!".baz ``` ——指定上述子标签（应为复合标签）中命名为baz的子标签。

树状图

- [图:NBT复合标签/JSON对象] 实体的根标签 - [图:NBT复合标签/JSON对象]foo：foo标签 - [图:NBT列表/JSON数组]bar：bar标签 - [图:NBT复合标签/JSON对象] 列表bar的第一个元素 - [图:NBT复合标签/JSON对象]A [crazy name]!："A [crazy name]!"标签 - [图:字节型]baz：baz标签；本示例的目标标签 - [图:NBT复合标签/JSON对象] 列表bar中的另一个无关元素

## 示例2

```
/data get block ~ ~ ~ Items[1].components.minecraft:written_book_content.pages[3].raw
```

某玩家写了一本书，将其放在了一个箱子里。Alex要一步步尝试拆解这条命令，最终运行上述命令。

聊天栏记录

```
* Alex 跳上了箱子。

* Alex 运行命令：/data get block 
~ ~ ~

0, 55, 0拥有以下方块数据：
{
x
: 
0
, 
y
: 
55
, 
z
: 
0
, 
Items
: [{
Slot
: 
0
b
, 
id
: "
minecraft:clock
", 
count
: 
1
}, {
Slot
: 
9
b
, 
id
: "
minecraft:written_book
", 
count
: 
1
, 
components
: {"
minecraft:written_book_content
": {
pages
: [{
raw
: '
"twas brillig and the slithy toves"
'}, {
raw
: '
"Did gyre and gimble in the wabe."
'}, {
raw
: '
"All mimsy were the borogoves"
'}, {
raw
: '
"And the mome raths outgrabe."
'}], 
author
: "
LewisCarroll
", 
title
: {
raw
: "
Jabberwocky
"}, 
resoveled
: 
1
b
}}}], 
id
: "
minecraft:chest
"}

* Alex 只想看看这个箱子的物品栏。虽然他可以
搜一搜Minecraft Wiki
来获取
那个标签的名字
，但由于他知道如何阅读
SNBT
，他决定从上个命令的输出中把它弄明白。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: 
[{
Slot
: 
0
b
, 
id
: "
minecraft:clock
", 
count
: 
1
}, {
Slot
: 
9
b
, 
id
: "
minecraft:written_book
", 
count
: 
1
, 
components
: {"
minecraft:written_book_content
": {
pages
: [{
raw
: '
"twas brillig and the slithy toves"
'}, {
raw
: '
"Did gyre and gimble in the wabe."
'}, {
raw
: '
"All mimsy were the borogoves"
'}, {
raw
: '
"And the mome raths outgrabe."
'}], 
author
: "
LewisCarroll
", 
title
: {
raw
: "
Jabberwocky
"}, 
resoveled
: 
1
b
}}}]
, id: "minecraft:chest"}

* Alex 想把输出范围缩减到箱子内的第二个物品。他从0开始数，得出第二个物品是元素1。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items[1]

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: [{Slot: 0b, id: "minecraft:clock", count: 1}, 
{
Slot
: 
9
b
, 
id
: "
minecraft:written_book
", 
count
: 
1
, 
components
: {"
minecraft:written_book_content
": {
pages
: [{
raw
: '
"twas brillig and the slithy toves"
'}, {
raw
: '
"Did gyre and gimble in the wabe."
'}, {
raw
: '
"All mimsy were the borogoves"
'}, {
raw
: '
"And the mome raths outgrabe."
'}], 
author
: "
LewisCarroll
", 
title
: {
raw
: "
Jabberwocky
"}, 
resoveled
: 
1
b
}}}
], id: "minecraft:chest"}

* Alex 只想要标签“components”。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items[1].components

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: [{Slot: 0b, id: "minecraft:clock", count: 1}, {Slot: 9b, id: "minecraft:written_book", count: 1, components: 
{"
minecraft:written_book_content
": {
pages
: [{
raw
: '
"twas brillig and the slithy toves"
'}, {
raw
: '
"Did gyre and gimble in the wabe."
'}, {
raw
: '
"All mimsy were the borogoves"
'}, {
raw
: '
"And the mome raths outgrabe."
'}], 
author
: "
LewisCarroll
", 
title
: {
raw
: "
Jabberwocky
"}, 
resoveled
: 
1
b
}}
}], id: "minecraft:chest"}

* Alex 只想要标签“pages”。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.pages

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: [{Slot: 0b, id: "minecraft:clock", count: 1}, {Slot: 9b, id: "minecraft:written_book", count: 1, components: {"minecraft:written_book_content": {pages: 
[{
raw
: '
"twas brillig and the slithy toves"
'}, {
raw
: '
"Did gyre and gimble in the wabe."
'}, {
raw
: '
"All mimsy were the borogoves"
'}, {
raw
: '
"And the mome raths outgrabe."
'}]
, author: "LewisCarroll", title: {raw: "Jabberwocky"}, resoveled: 1b}}}], id: "minecraft:chest"}

* Alex 只想要这个列表的第四个元素。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.pages[3]

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: [{Slot: 0b, id: "minecraft:clock", count: 1}, {Slot: 9b, id: "minecraft:written_book", count: 1, components: {"minecraft:written_book_content": {pages: [{raw: '"twas brillig and the slithy toves"'}, {raw: '"Did gyre and gimble in the wabe."'}, {raw: '"All mimsy were the borogoves"'}, 
{
raw
: '
"And the mome raths outgrabe."
'}
], author: "LewisCarroll", title: {raw: "Jabberwocky"}, resoveled: 1b}}}], id: "minecraft:chest"}

* Alex 只想要这个元素中的文本。

* Alex 运行命令：/data get block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.pages[3].raw

0, 55, 0拥有以下方块数据：
{x: 0, y: 55, z: 0, Items: [{Slot: 0b, id: "minecraft:clock", count: 1}, {Slot: 9b, id: "minecraft:written_book", count: 1, components: {"minecraft:written_book_content": {pages: [{raw: '"twas brillig and the slithy toves"'}, {raw: '"Did gyre and gimble in the wabe."'}, {raw: '"All mimsy were the borogoves"'}, {raw: 
'
"And the mome raths outgrabe."
'
}], author: "LewisCarroll", title: {raw: "Jabberwocky"}, resoveled: 1b}}}], id: "minecraft:chest"}

* Alex 达到了他的目的。他想使用NBT路径来编辑这本书。

* Alex 运行命令：/data modify block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.pages[3].raw
 set value 
'"And this pig here\'s named Babe."'

已修改位于0, 55, 0的方块数据

* Alex 运行命令：/data modify block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.pages
 prepend value 
{raw: '"Call me Ishmael."'}

已修改位于0, 55, 0的方块数据

* Alex 运行命令：/data modify block 
~ ~ ~
 
Items[1].components.minecraft:written_book_content.author
 set value 
"Cthulhu the Sleeper"
```

# 历史

此段落仍需完善。
你可以帮助我们加入更多信息。

# 参考

1. ↑ MC-175504 — 漏洞状态为“已修复”。

# 导航
