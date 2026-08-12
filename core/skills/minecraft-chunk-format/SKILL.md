---
name: minecraft-chunk-format
description: |
  Java版存档格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于基岩版的存档格式，请见“基岩版存档格式”。
  
  【涵盖内容】
  - 存档历史
  - 区块数据历史
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版存档格式 的完整规范时
---

关于基岩版的存档格式，请见“基岩版存档格式”。

本条目所述内容仅适用于Java版。
存档（Level）是游戏保存世界的持久化形式。

# 存档位置

游戏客户端内的所有存档均在
```
.minecraft
/saves
```

（存档存储目录）下，每一个目录代表一个存档。

游戏不会将所有目录都视为存档，而是会检查每个目录内的
```
level.dat
```

或
```
level.dat_old
```

以确认这是一个有效的游戏存档，确认后的目录才会在选择世界菜单中出现。

对于客户端，名称为w的存档，其存档根目录就是
```
.minecraft/saves/
w
```

。

对于服务端，存档位置由两个参数决定：

- 服务端启动参数 ``` --universe ``` （默认为 ``` . ``` ，即当前运行目录）：指定存档存储目录，下文简化为u。
- 服务端启动参数 ``` --world ``` 、 ``` server.properties ``` 中 ``` level-name ``` 项（按顺序尝试获取）：指定存档名称，下文简化为w。

根据这两个参数，服务端的存档根目录路径是
```
u
/
w
```

。

# 存档结构

 关于Java版26.1前的存档结构，请见“Java版存档格式/1.21.11”。

每个存档都有相应的文件保存数据，这些文件按照一定的存储格式，在特定的路径上起到作用。下文中粗体代表文件一定存在，未标注粗体则代表文件不一定存在，备份文件不以显示。假定存档已经初始化完成、且至少有一名玩家进入过存档。

所有和维度无关的数据其存储文件都直接和存档根目录相对应，下列是所有维度无关的数据存储文件：

- [图:File directory.png：Minecraft中directory的精灵图] ``` 存档根目录 ``` - [图:File file.png：Minecraft中file的精灵图] ``` icon.png ``` ：存档的图标。 - [图:File file.png：Minecraft中file的精灵图] ``` level.dat ``` ：存档基础数据存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` resourcepacks ``` ：世界指定资源包目录。 - [图:File archive.png：Minecraft中archive的精灵图] ``` resources.zip ``` ：世界指定资源包，见资源包 § 世界指定资源包。 - [图:File file.png：Minecraft中file的精灵图] ``` session.lock ``` ：存档会话锁文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` players ``` ：所有与玩家相关的数据存储目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` advancements ``` ：进度存储目录。 - [图:File file.png：Minecraft中file的精灵图] ``` < 玩家UUID >.json ``` ：进度存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` ：玩家存储目录。 - [图:File file.png：Minecraft中file的精灵图] ``` < 玩家UUID >.dat ``` ：玩家存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` stats ``` ：统计存储目录。 - [图:File file.png：Minecraft中file的精灵图] ``` < 玩家UUID >.json ``` ：统计存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` ：存档数据目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` ： ``` minecraft ``` 命名空间下的存储数据。 - [图:File directory.png：Minecraft中directory的精灵图] ``` maps ``` ：地图数据目录。 - [图:File file.png：Minecraft中file的精灵图] ``` last_id.dat ``` ：地图计数存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` < 地图ID >.dat ``` ：地图数据存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` command_storage.dat ``` ：命令存储存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` custom_boss_events.dat ``` ：自定义Boss栏存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` game_rules.dat ``` ：游戏规则存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` random_sequences.dat ``` ：随机序列存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` scheduled_events.dat ``` ：计划事件存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` scoreboard.dat ``` ：记分板存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` stopwatches.dat ``` ：秒表存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` wandering_trader.dat ``` ：流浪商人数据存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` weather.dat ``` ：天气数据存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` world_clocks.dat ``` ：世界时钟存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` world_gen_settings.dat ``` ：世界生成设置存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` < 命名空间 > ``` ：其他命名空间下的存储数据。 - 其他的存储文件，目前只有命令存储会使用 ``` minecraft ``` 以外的命名空间。 - [图:File directory.png：Minecraft中directory的精灵图] ``` datapacks ``` ：世界指定数据包。 - [图:File archive.png：Minecraft中archive的精灵图][图:File directory.png：Minecraft中directory的精灵图] ``` < 数据包名称 > ``` ：一个世界指定数据包。 - [图:File directory.png：Minecraft中directory的精灵图] ``` generated ``` ：生成数据存储目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` < 命名空间 > ``` ：对于指定命名空间的数据。 - [图:File directory.png：Minecraft中directory的精灵图] ``` structure ``` ：生成结构文件目录。 - [图:File file.png：Minecraft中file的精灵图] ``` < 标识符 >.nbt ``` ：结构存储文件。

对于所有维度数据，所有维度都有对应的根目录，下列列出了各个维度和对应维度目录相对于存档根目录的相对路径：

所有维度数据存储按照下列结构：

- [图:File directory.png：Minecraft中directory的精灵图] ``` 维度根目录 ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` ：维度数据目录。 - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` ：minecraft命名空间下的维度数据。 - [图:File file.png：Minecraft中file的精灵图] ``` chunk_tickets.dat ``` ：区块标签存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` raids.dat ``` ：袭击存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` ender_dragon_fight.dat ``` ：末影龙战斗存储文件。（仅限末地或其他可启动末影龙战斗的维度，否则不会自动生成此文件） - [图:File file.png：Minecraft中file的精灵图] ``` world_border.dat ``` ：世界边界存储文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` entities ``` ：实体数据目录。 - [图:File file.png：Minecraft中file的精灵图] ``` r.< 区域X坐标 >.< 区域Z坐标 >.mca ``` ：区域实体存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` c.< 区块X坐标 >.< 区块Z坐标 >.mcc ``` ：区域实体存储文件的区域额外文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` poi ``` ：兴趣点数据目录。 - [图:File file.png：Minecraft中file的精灵图] ``` r.< 区域X坐标 >.< 区域Z坐标 >.mca ``` ：区域兴趣点存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` c.< 区块X坐标 >.< 区块Z坐标 >.mcc ``` ：区域兴趣点存储文件的区域额外文件。 - [图:File directory.png：Minecraft中directory的精灵图] ``` region ``` ：区块基础数据目录。 - [图:File file.png：Minecraft中file的精灵图] ``` r.< 区域X坐标 >.< 区域Z坐标 >.mca ``` ：区域区块存储文件。 - [图:File file.png：Minecraft中file的精灵图] ``` c.< 区块X坐标 >.< 区块Z坐标 >.mcc ``` ：区域区块存储文件的区域额外文件。

对于从旧版本升级而来的存档，还可能存在下列文件：

- [图:File directory.png：Minecraft中directory的精灵图] ``` 存档根目录 ``` - [图:File file.png：Minecraft中file的精灵图] ``` level.dat_mcr ``` - [图:File file.png：Minecraft中file的精灵图] ``` worldgen_settings_export.json ``` ：世界生成导出设置，见自定义。

# 历史

## 存档历史

 参见：Java版存档格式/1.21.11 

## 区块数据历史

区块数据从Alpha阶段开始采用“区域”的概念存储，此时每个区块都存储于独立的文件夹中；自Beta 1.3起，区块数据使用MCRegion格式存储，随后在12w07a中改为Anvil文件格式，并使用至今。

# 参考

1. ↑ MC-304023 — 漏洞状态为“已修复”。

# 导航
