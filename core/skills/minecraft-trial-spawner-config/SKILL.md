---
name: minecraft-trial-spawner-config
description: |
  试炼刷怪笼配置定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】试炼刷怪笼配置（Trial Spawner configurations）是试炼刷怪笼试炼行为的配置数据。试炼刷怪笼配置定义文件是试炼刷怪笼配置在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - 抽取物品
  
  【关键定义】
  - 注册表：TRIAL_SPAWNER_CONFIG
  - 数据包路径：data/spawners/trial_chamber/items_to_drop_when_ominous、data/spawners/trial_chamber/consumables、data/spawners/trial_chamber/key
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 试炼刷怪笼配置定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
试炼刷怪笼配置（Trial Spawner configurations）是试炼刷怪笼试炼行为的配置数据。试炼刷怪笼配置定义文件是试炼刷怪笼配置在数据包中的数据驱动定义文件。

# 定义格式

试炼刷怪笼配置数据在游戏内使用
```
TRIAL_SPAWNER_CONFIG
```

注册表，数据包路径为
```
trial_spawner
```

，即所有试炼刷怪笼配置定义文件都需要在
```
data/<
命名空间
>/trial_spawner
```

目录内定义，试炼刷怪笼标签则需要在
```
data/<
命名空间
>/tags/trial_spawner
```

目录内定义。

试炼刷怪笼配置定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]items_to_drop_when_ominous：（命名空间ID）战利品表，控制不祥状态的试炼刷怪笼激活状态时生成的不祥之物生成器实体内的物品。此项不存在时游戏默认为 ``` spawners/trial_chamber/items_to_drop_when_ominous ``` 。 - [图:NBT列表/JSON数组]loot_tables_to_eject：加权列表，决定试炼刷怪笼喷出的奖励物品。决定奖励时，游戏会从此列表中先抽出一项战利品表，然后根据参与试炼的玩家决定抽取次数。此项不存在时游戏默认为 ``` spawners/trial_chamber/consumables ``` 和 ``` spawners/trial_chamber/key ``` ，权重均为1。 - [图:NBT复合标签/JSON对象]：一项战利品项。 - [图:字符串]*data：（命名空间ID）战利品表。 - [图:整型]*weight：（值>0）此项的权重。 - [图:单精度浮点数]simultaneous_mobs：（值≥0，默认为2）同时存活的生成生物的最少数量，即仅一个玩家加入试炼时同时存活的生物数量。 - [图:单精度浮点数]simultaneous_mobs_added_per_player：（值≥0，默认为1）每增加一个加入试炼玩家，同时存活生物数量的增加值。设 ``` simultaneous_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的最大同时存活数量为⌊t+p(n−1)⌋。 - [图:NBT列表/JSON数组]spawn_potentials：（默认为空）加权列表，包含了可能生成的实体。在试炼刷怪笼进行一次尝试生成后，游戏将会随机从中选择一项用于下次生成。 - [图:NBT复合标签/JSON对象]：一次可能的生成。 - [图:NBT复合标签/JSON对象]*data：一项生成数据。 - - 生成数据，见Template:Nbt inherit/spawn data/source - [图:整型]*weight：（值>0）此项的权重。 - [图:整型]spawn_range：（1≤值≤128，默认为4）生成生物的范围，采用切比雪夫距离，越靠近试炼刷怪笼生成在此位置的概率越大。 - [图:单精度浮点数]total_mobs：（值≥0，默认为6）生成生物的最少总数量，即仅一个玩家加入试炼时生成的总生物数量。 - [图:单精度浮点数]total_mobs_added_per_player：（值≥0，默认为2）每增加一个加入试炼玩家，生成生物总数量的增加值。设 ``` total_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的生物总数量为⌊t+p(n−1)⌋。 - [图:整型]ticks_between_spawn：（值≥0，默认为40游戏刻（2秒））两次尝试生成生物的最小间隔时间。

# 定义行为

 参见：试炼刷怪笼 § 用途和不祥试炼刷怪笼 § 用途 
试炼刷怪笼配置定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使试炼刷怪笼配置定义被重新加载，而必须重启服务端。

试炼刷怪笼配置数据控制了实体生成数据，也控制了试炼结束后产生的战利品。

配置数据需要在试炼刷怪笼的下述方块实体数据中使用。试炼开启后会使用与方块状态
```
ominous
```

对应的配置数据，任何未填写的字段均被视为默认值。

- [图:NBT复合标签/JSON对象] 根标签 - [图:字符串][图:NBT复合标签/JSON对象]normal_config：正常变种（方块状态 ``` ominous ``` 为false）使用的配置数据。 - [图:字符串][图:NBT复合标签/JSON对象]ominous_config：不祥变种（方块状态 ``` ominous ``` 为true）使用的配置数据。 - ...

## 抽取物品

试炼刷怪笼有两种抽取行为：不祥试炼刷怪笼生成的不祥之物生成器和试炼结束后的奖励。

[图:字符串]items_to_drop_when_ominous决定了随机生成的不祥之物生成器内存储的物品。游戏会使用战利品上下文参数集
```
empty
```

从战利品表内生成一项物品，并将获得的物品的数量设为1作为结果。因此生成不祥之物的战利品表不能使用任何战利品上下文参数。

[图:NBT列表/JSON数组]loot_tables_to_eject决定了试炼结束后喷出的奖励。游戏会从中选取一项战利品表，并使用战利品上下文参数集
```
empty
```

从其中生成并一次性弹出奖励物品，每有一个玩家参与试炼就会弹出一次奖励。因此生成试炼刷怪笼奖励的战利品表不能使用任何战利品上下文参数。

# 历史

# 导航
