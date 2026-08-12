---
name: minecraft-template-pool
description: |
  模板池（Minecraft Wiki 中文版全量正文）。
  
  【概述】基岩版模板池请参见官方文档
  
  【涵盖内容】
  - 模板池元素类型
  - empty_pool_element
  - feature_pool_element
  - list_pool_element
  - single_pool_element
  - legacy_single_pool_element
  
  【关键定义】
  - 注册表：TEMPLATE_POOL
  - 数据包路径：data/worldgen/template_pool
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 模板池 的完整规范时
---

本条目所述内容仅适用于Java版。
基岩版模板池请参见官方文档

模板池（Template Pool），也被称为结构池（Structure Pool）或拼图池（Jigsaw Pool），是拼图结构生成抽取子结构的基本单元。模板池定义文件是模板池在数据包中的数据驱动定义文件。

# 定义格式

模板池在游戏中使用
```
TEMPLATE_POOL
```

注册表，数据包路径为
```
worldgen/template_pool
```

，即所有的模板池定义文件都需要在
```
data/<
命名空间
>/worldgen/template_pool
```

目录下定义，模板池标签则需要在
```
data/<
命名空间
>/tags/worldgen/template_pool
```

目录下定义。

模板池定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*fallback：回落池。在结构生成结束后会从此模板池中选取一项作为终止拼图结构。 - [图:NBT列表/JSON数组]*elements：模板池可供选择的结构元素列表。 - [图:NBT复合标签/JSON对象] - [图:NBT复合标签/JSON对象]*element：此结构元素的属性。 - [图:字符串]*element_type：模板池元素类型。 - 依模板池元素类型的附加字段，见下文。 - [图:整型]*weight：（1≤值≤150）此结构元素的权重。

## 模板池元素类型

模板池元素类型决定了游戏如何处理模板池中的元素。

### empty_pool_element

空元素，什么也不生成。

- [图:NBT复合标签/JSON对象]*element 模板池元素 - [图:字符串]*element_type： ``` empty_pool_element ```

### feature_pool_element

生成一个地物。

- [图:NBT复合标签/JSON对象]*element 模板池元素 - [图:字符串]*element_type： ``` feature_pool_element ``` - [图:字符串]*projection：决定生成的结构元素是否匹配地形高度。取值可以为 ``` rigid ``` （不调整）或 ``` terrain_matching ``` （根据地形高度对进行偏移）。 - [图:字符串][图:NBT复合标签/JSON对象]*feature：一个已放置的地物，决定要生成的地物。

游戏放置地物时会假定地物具有拼图方块，此拼图方块的名称是
```
minecraft:bottom
```

，连接类型为允许旋转，[图:字符串]final_state为空气，方块状态为
```
orientation=down_south
```

。

### list_pool_element

按照列表顺序依次放置结构元素，使其重叠生成。

- [图:NBT复合标签/JSON对象]*element 模板池元素 - [图:字符串]*element_type： ``` list_pool_element ``` - [图:字符串]*projection：决定生成的结构元素是否匹配地形高度。取值可以为 ``` rigid ``` （不调整）或 ``` terrain_matching ``` （根据地形高度对进行偏移）。 - [图:NBT列表/JSON数组]*elements：一个结构元素列表。 - [图:NBT复合标签/JSON对象]：一个模板池元素。 - 与此结构相同，递归定义。

### single_pool_element

使用结构模板生成结构。

- [图:NBT复合标签/JSON对象]*element 模板池元素 - [图:字符串]*element_type： ``` single_pool_element ``` - [图:字符串]*projection：决定生成的结构元素是否匹配地形高度。取值可以为 ``` rigid ``` （不调整）或 ``` terrain_matching ``` （根据地形高度对进行偏移）。 - [图:字符串]*location：（命名空间ID）要放置的结构模板。 - [图:字符串]override_liquid_settings：（默认为 ``` apply_waterlogging ``` ）用于覆盖父模板池的液体设置。可以为 ``` apply_waterlogging ``` （将可含水方块转换为含水方块）和 ``` ignore_waterlogging ``` （直接替代液体方块）。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*processors：结构模板放置前要应用的处理器列表，命名空间ID或内联定义均可。

游戏准备放置结构模板时，会先转化拼图方块并移除所有结构空位，然后处理结构片段内的液体并使用处理器列表对结构模板进行后处理，处理完毕后才会真正放置结构片段。被移除的结构空位和空气的位置会保留结构生成前的方块。

### legacy_single_pool_element

使用结构模板生成结构。与
```
single_pool_element
```

类似，但会额外移除空气。

- [图:NBT复合标签/JSON对象]*element 模板池元素 - [图:字符串]*element_type： ``` legacy_single_pool_element ``` - [图:字符串]*projection：决定生成的结构元素是否匹配地形高度。取值可以为 ``` rigid ``` （不调整）或 ``` terrain_matching ``` （根据地形高度对进行偏移）。 - [图:字符串]*location：（命名空间ID）要放置的结构模板。 - [图:字符串]override_liquid_settings：（默认为 ``` apply_waterlogging ``` ）用于覆盖父模板池的液体设置。可以为 ``` apply_waterlogging ``` （将可含水方块转换为含水方块）和 ``` ignore_waterlogging ``` （直接替代液体方块）。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*processors：结构模板放置前要应用的处理器列表。

# 定义行为

模板池定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以重新加载模板池定义，而必须重启服务端。

模板池用于
```
jigsaw
```

结构类型的结构生成。每个拼图方块都指定了目标池，游戏在生成结构时会从目标池的结构元素中选取一项生成。由于拼图方块需要拼接，因此拼接时只会生成带有对应拼图方块的结构。模板池也可以被
```
/
place
 jigsaw
```

直接调用。

游戏将从模板池中随机选取一个元素。在起始模板池中，若指定了起始拼图方块名称，但该元素没有找到对应名称的拼图方块，则结构地物生成失败；在非起始模板池中，满足以下条件才能成功生成：

1. 存在对应名称、对应方向（水平的拼图方块相互对应、朝上和朝下的拼图方块相互对应）的拼图方块。
1. 将生成的该元素方块与结构起始点的三维切比雪夫距离不会超过该已配置结构地物中指定的最大距离，或使用命令或拼图方块GUI生成时不超过128。
1. 将生成的该元素不会与生成的其他拼图发生重叠，除非拼图方块指向的方块位于当前拼图内部。
1. 拼图方块指向的方块位于当前拼图内部，则该元素与之后生成的所有拼图都必须完全位于该拼图方块所在拼图的内部。

若无法成功生成，将会再去尝试该列表中的其他元素，如果全部都无法成功生成，将尝试使用回落池。

回落池中定义的模板会在以下两种情况下生成：

1. 当拼图方块生成达到预定层数时，回落池会生成在最后一层的末尾。
1. 当拼图方块试图加载的模板池中所有元素都无法成功生成。

以上两种情况下，游戏会试图从回落池加载一个模板来替代原先的模板进行生成。当回落池中的模板尝试生成时，如果该回落池中任意一个元素也都无法成功生成，则不会生成任何东西。

# 历史

# 导航
