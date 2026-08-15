---
name: minecraft-function
description: Java Edition function — .mcfunction format, macros, invocation, recursion, return.
whenToUse: Use when writing or calling .mcfunction files in datapacks.
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
