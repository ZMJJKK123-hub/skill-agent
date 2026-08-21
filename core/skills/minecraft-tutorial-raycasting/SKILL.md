---

name: minecraft-tutorial-raycasting
description: "Minecraft Tutorial: Datapack Raycasting 数据包射线投射教程（Java 1.21+）：Basic Method 基本方法（从玩家眼睛位置开始 沿视线方向步进 当前方块可通行则前进 在第一个固体方块停止 最大步数限制避免无限递归）、Datapack Implementation 数据包实现（generic/function/raycast/start.mcfunction 初始化计数器 return run generic:raycast/shoot、generic/function/raycast/shoot.mcfunction 步进循环 粒子可视化 #raycast_check_times 检查次数 块标签 #test:raycan_pass 可通行方块 递归 位置前移0.1方块）、generic/function/raycast/end.mcfunction 射线击中方块 执行上下文在击中方块位置 挂接效果、generic/function/raycast/dispatcher.mcfunction 接口 检查标志标签 转发上下文 扩展命名空间插件）、Using Third-Party Package 使用第三方包（Bookshelf Raycast模块 #bs.raycast:run）、Example: Counting Bees 示例：计数蜜蜂（蜂巢/蜂箱方块实体 bees列表 entity_data.Age Age≥0=成年 Age<0=幼年、实现：移除标志 检查方块 复制bees列表 初始化计数器 循环处理 Age≤-1幼年+1 否则成年+1 tellraw输出）、Polish and Improvements 完善改进（Filter players 过滤玩家 谓词门控 execute as @a[predicate=...]、Localization 本地化 translate组件 with参数 %s/%n$s 占位符 语言文件 assets/<ns>/lang/）。"
whenToUse: "Use when implementing raycasts (aim-point detection) in datapacks, Java 1.21+."

---

# Tutorial: Datapack Example — Raycasting

Java Edition only; covers 1.21.5 through the latest snapshot. Requires datapack basics (functions, relative/local coordinates, scoreboards, `/execute`, `/data`, text components).

## Basic Method

Simulate the player's line of sight: start at the player's **eye position** and step forward along the view direction, advancing if the current block is passable (air, grass, ...), stopping at the first solid block, and stopping after a max step count to avoid runaway recursion.

## Datapack Implementation

Files under `data/`:

**`generic/function/raycast/start.mcfunction`** — call this after `/execute anchored eyes run ...`:

```mcfunction
scoreboard players set #raycast_check_times var 0
return run function generic:raycast/shoot
```

`#raycast_check_times` counts the steps and must be 0 before starting. `return run` lets the caller inspect the return value (e.g. `run return 0`/`fail` handling).

**`generic/function/raycast/shoot.mcfunction`** — the stepping loop:

```mcfunction
particle minecraft:end_rod ^ ^ ^ 0 0 0 0 0          # visualize the ray
execute if score #raycast_check_times var matches 100.. run return run function generic:raycast/end
execute unless block ~ ~ ~ #test:raycast/can_pass run return run function generic:raycast/end
scoreboard players add #raycast_check_times var 1
execute positioned ^ ^ ^0.1 run function generic:raycast/shoot   # step 0.1 blocks forward, recurse
```

- `#test:raycast/can_pass` is a block tag listing passable blocks (`data/test/tags/block/raycast/can_pass.json`).
- The recursion naturally terminates because the context moves forward each call.

**`generic/function/raycast/end.mcfunction`** — the ray hit a block; the execution context (position, rotation, `@s`) is now at the hit block. This is where you hook your effect.

**`generic/function/raycast/dispatcher.mcfunction`** — an interface: checks a flag tag and forwards the context, e.g.:

```mcfunction
execute if entity @s[tag=used_bee_finder] run function test:bee_finder/extender/raycast_end
```

The `generic:raycast/end` function calls this dispatcher, letting add-on namespaces plug in without touching the core.

Load via `#minecraft:function/load` → `test:load` (or the `#minecraft:load` tag in newer versions).

## Using a Third-Party Package

The Bookshelf datapack's Raycast module provides a robust implementation:

```mcfunction
execute anchored eyes positioned ^ ^ ^ run function #bs.raycast:run {with:{}}
data get storage bs:out raycast.hit_point   # last hit coordinates
```

## Example: Counting Bees in a Beehive

Beehive/bee nest block entity data stores bees in a `bees` list; each entry has `entity_data` (partial bee entity data; `#beehive_inhabitors` only) plus `min_ticks_in_hive`, `ticks_in_hive`, `flower_pos`. Bee entity data uses `Age` from the breedable tags: **Age ≥ 0 = adult, Age < 0 = baby**.

Implementation outline:

- `test/function/bee_finder/extender/raycast_end.mcfunction` — remove `used_bee_finder` flag, then:
  - `execute unless block ~ ~ ~ #minecraft:beehives run return fail` (with a "invalid block" message).
  - `data modify storage generic:data queue.value set from block ~ ~ ~ bees` — if the list is empty, say "no bees" and stop.
  - Initialize `#bee_finder_adult`/`#bee_finder_baby` counters to 0, then loop: take the first element (`data modify storage generic:data queue.output set from storage generic:data queue.value[0]`), reset `#bee_finder_bee_age`, `data get storage generic:data queue.output.entity_data.Age` → `#bee_finder_bee_age`; `Age ≤ -1` → baby count +1, else adult count +1; remove the consumed element and recurse until the list is empty.
  - `tellraw @s` the result: "Adult bees: X, Baby bees: Y".

## Polish and Improvements

- **Filter players**: instead of ticking everyone, gate with a predicate, e.g. `data/beeutility/predicates/hold_glass_bottle.json`:

```json
{
  "condition": "minecraft:entity_properties",
  "entity": "this",
  "predicate": { "equipment": { "offhand": { "item": "minecraft:glass_bottle" } } }
}
```

then `execute as @a[predicate=beeutility:hold_glass_bottle] at @s anchored eyes run function ...`.

- **Localization**: use `{"translate": "beeutility.msg.bee_count", "with": [{"score": {"name": "#bee_finder_adult", "objective": "var"}}, ...]}` with language files in a resource pack at `assets/beeutility/lang/en_us.json` / `zh_cn.json`. Translation lookup: current language → `en_us` → the key itself. `with` fills `%s` / `%n$s` placeholders in order.
