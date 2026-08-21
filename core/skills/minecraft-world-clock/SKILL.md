---

name: minecraft-world-clock
description: "Minecraft World Clock 世界时钟：WORLD_CLOCK 注册表、data/<namespace>/world_clock/ 数据包路径、tags/world_clock/ 标签、JSON格式 空对象 {}、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载）、World clock behavior 时钟行为（时钟本身无数据、游戏通过ID区分时钟、每个时钟持有内部时间 每刻递增 可暂停 由/time管理、advance_time游戏规则 false时即使未暂停也不前进、每个维度从维度类型获取世界时钟 默认/time 以及使用时间线的时间标记、每个时间线从其时钟计算环境属性轨迹、保存运行时间GameTime不由时钟管理）、Time markers 时间标记（命名特定时钟时间 在时间线time_markers中定义 启动时注册到时间线时钟 可在/time使用、游戏定义标记：wake_up_from_sleep 睡眠后时间 缺失=醒来无时间变化、roll_village_siege 僵尸围城检查时间 缺失=无围城）、Built-in clocks 内置时钟（overworld 主世界使用 所有内置时间线使用它 标记：day 1000/noon 6000/night 13000/midnight 18000/wake_up_from_sleep 0 隐藏/roll_village_siege 18000 隐藏 也用于区域难度 无时钟时0 和固定调试世界 服务器崩溃 无noon标记=无时间变化；the_end 末地用于末地天空闪光计时）。"
whenToUse: "Use when understanding world clocks, time markers, or /time command behavior."

---

# World Clocks

This content applies only to Java Edition.

World clocks (clocks) manage different world clock instances. Definition files are their data-driven definitions in datapacks.

## Definition format

World clocks use the `WORLD_CLOCK` registry; the datapack path is `world_clock` (definitions in `data/<namespace>/world_clock`, tags in `data/<namespace>/tags/world_clock`). Definition files are empty JSON objects `{}`.

## Definition behavior

World clock data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

### World clock behavior

A world clock itself carries no data; the game distinguishes clocks by ID. Each clock holds an internal time that increments every tick and can be paused; it is managed by `/time`. With the `advance_time` game rule `false`, clocks do not advance even when unpaused. Each dimension gets its world clock from its dimension type (default for `/time`, and time markers per the used timelines). Each timeline computes environment attribute tracks from its clock. Save run time (GameTime) is not managed by clocks.

### Time markers

Time markers name specific clock times. They are defined in timelines' `time_markers` and registered to the timeline's clock at startup. Usable in `/time`. Game-defined markers: `wake_up_from_sleep` (time after sleeping; absent = no time change on waking) and `roll_village_siege` (zombie siege check time; absent = no sieges).

## Built-in clocks

- `overworld`: used by the Overworld; all built-in timelines use it. Markers (from the `day` timeline): `day` 1000, `noon` 6000, `night` 13000, `midnight` 18000, `wake_up_from_sleep` 0 (hidden in `/time`), `roll_village_siege` 18000 (hidden). Also used for regional difficulty (0 without the clock) and fixed debug worlds (server crashes without it; no `noon` marker = no time changes).
- `the_end`: used by the End for end sky flash timing.
