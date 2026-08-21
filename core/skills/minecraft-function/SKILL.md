---

name: minecraft-function
description: "Minecraft Function 函数：Definition 定义（.mcfunction 文本文件、data/<namespace>/function/、每行一个命令 无/前导、尾部\行续、#行首注释、允许子文件夹）、Macros 宏函数（$开头宏行 $(key) 替换段 key允许 a-z/A-Z/0-9/_、调用 /function with entity @p SelectedItem 复合标签、值转换 数字→纯文本 字符串→原始值 列表/复合/整数数组→SNBT、宏行在调用时解析 缓存已解析结果）、Invocation 调用（/function <id>、/execute if|unless function <id>、function tags #example:example_tag 顺序运行去重、Advancement rewards function 执行者为进度玩家、Special tags #minecraft:load 世界加载/服务器启动/每次重载运行、#minecraft:tick 每刻开始运行、/schedule 延迟执行、Enchantment run_function 执行者为效果实体）、Behavior 行为（/reload 重载函数、加载时所有非宏行解析 一行坏整个函数失败 宏行每次调用解析、单人/LAN 权限上限2 服务器 function-permission-level 配置、每刻总命令数上限 max_command_sequence_length 65536、执行者上下文存储 /execute 内部更改不泄露）、Recursion 递归（函数调用自身运行直到 maxCommandChainLength 限制）、Return 返回（return [run ...] 强制结束函数 后续命令跳过、execute if|unless ... run return 条件退出、返回值 成功标志+整数返回值、无return→Void、/function 输出返回值、/execute (if|unless) function 检查返回值存在且非零）。"
whenToUse: "Use when writing or calling .mcfunction files in datapacks."

---

# Java Edition Function

Functions are `.mcfunction` text files with multiple commands, stored in `data/<namespace>/function/`. Java Edition only (Bedrock has its own functions).

## Definition

- One command per line, no leading `/`; leading/trailing whitespace is stripped; commands are not limited by the command block's 32,500-char limit.
- Line continuation: a trailing `\` joins the next line (whitespace stripped).
- Comments: single-line only, `#` at line start.
- Subfolders are allowed: `data/custom/function/example/test.mcfunction` → ID `custom:example/test`.

### Macros

A line whose first non-whitespace char is `$` is a macro line; the function becomes a macro function. Macro lines contain `$(<key>)` replacement segments; keys allow only `a-z`, `A-Z`, `0-9`, `_`. Example:

```mcfunction
$give @s $(id) $(count)
```

Called with `/function test:macro_func with entity @p SelectedItem` — every `$(key)` must be found in the passed compound, or the whole macro function won't run (extra keys are fine). Missing/extra args per line: each substituted line is parsed as a normal command; an invalid result fails that parse (the function doesn't run if any needed key is absent; invalid substituted commands fail the call). Calling a non-macro function with a compound is ignored silently.

Value conversion: numbers → plain text (no type suffixes, ≤15 decimals, exponent form expanded e.g. `1.2E1` → `12`); strings → raw value (no quotes); lists/compounds/int arrays → SNBT. Macro lines parse at call time (some cost; the game caches parsed results per used argument set).

## Invocation

- `/function <id>` and `/execute if|unless function <id>`.
- Function tags: `function #example:example_tag` runs all listed functions in order; duplicates run once.
- **Advancement rewards**: `"rewards": { "function": "<id>" }` — executor is the advancing player.
- **Special tags**: `#minecraft:load` runs on world load/server start and every pack reload (before players join — `@a` finds nobody, tellraw/title show nothing); `#minecraft:tick` runs at the start of every tick.
- `/schedule` — delayed server-side execution.
- Enchantment entity effect `run_function` — executor is the effect's entity (see the enchantment skill).

## Behavior

- `/reload` reloads functions; they also load on world/server start. At load, all non-macro lines are parsed — one bad line fails the whole function; macro lines parse per call.
- Single-player/LAN: functions run commands up to permission level 2 (like command blocks). Servers: the `function-permission-level` in server.properties caps it.
- All commands of a function (including called sub-functions) run within one game tick; the total per tick is capped by the `max_command_sequence_length` game rule (default 65536; excess is ignored).
- The caller's context (executor, position, rotation, dimension, anchor) is stored in the execution context for every command; `/execute` changes inside a function don't leak into later commands. Server-executed functions run at the world spawn position.

Example (foo:bar): `teleport @s ~ ~5 ~` moves every player up 5; the second line `execute at @s run setblock ~ ~-1 ~ minecraft:diamond_block` places diamond at the NEW position (its `at` changed the context), while the following plain `setblock ~ ~-1 ~ minecraft:emerald_block` uses the stored context (the pre-teleport position).

- **Recursion**: a function calling itself runs within the tick until the `maxCommandChainLength`-style limit stops it.
- **Return**: `return [run ...]` forcibly ends the function (later commands skipped); combined with `execute if|unless ... run return`, functions can exit early under conditions. Return values: a success flag (true/false) + an integer return value ("function test:test returned 42"). No `return` → Void (no return value). `/function` outputs the return value; `/execute (if|unless) function` checks that the return value exists and is non-zero.
