---

name: minecraft-command
description: "Minecraft Command 命令系统：Usage 使用方式（聊天 T/、命令方块、服务器控制台、functions 数据包、run_command 文本组件点击）、Syntax Notation 语法符号（Java [] 可选参数 (grant|revoke) 选择字面量 <targets> 必需参数、Bedrock <size: int> 必需参数）、Restrictions 限制（权限等级、单人作弊启用、多人操作员、命令方块无限制）、Parameter Types 参数类型（坐标、目标选择器 SNBT、文本组件）、Parsing and Execution 解析执行（客户端解析提供补全和早期错误、函数加载时全部解析、宏行运行时解析）、Output 输出（Success count 成功计数 比较器读取、Stored values 存储值 /execute store success/result）、Results 结果（Unparseable 不可解析、Error 错误、Void 空函数、Interrupted 中断 /execute、Success/failure 成功/失败）、Debug Commands 调试命令（MC_DEBUG_DEV_COMMANDS/MC_DEBUG_CHASE_COMMAND）、Removed Commands 已移除命令、April Fools Commands 愚人节命令。"
whenToUse: "Use when writing or debugging commands, command blocks, or functions."

---

# Command

Commands are advanced features invoked by typing text strings (chat, command blocks, server console, functions, clickable text components). Java Edition unless noted.

## Usage

- Chat: press T or `/` (default) — `/` also types the leading slash. ↑/↓ browse history; Tab cycles suggestions/arguments (also fills block coordinates under the crosshair, or an entity's UUID when pointing at it); a value list shows above the input for the current argument.
- Command blocks and minecarts: the leading `/` is optional.
- Dedicated server console: no leading `/`.
- Execution sources: player chat, command block / command block minecart, server console, functions (data packs), script/animation controllers/block & entity events (Bedrock), `run_command` text component clicks (Java), WebSocket server (Bedrock), NPC dialogs (Bedrock).

## Syntax Notation

- Java: `[<size>]` = optional argument; `[size]` = optional literal; `(grant|revoke)` = choose one literal; `<targets>` = required argument.
- Bedrock: `<size: int>` = required argument; bare words = required literals.
- Both: `[b]`/`[c]` optional parts only at the end; `a [b] [c]` allows `a`, `a b`, `a b c`.

## Restrictions

Most commands need sufficient permission level (in single-player: cheats enabled; multiplayer: operator). Command blocks always execute regardless of cheats. Additional restrictions: none; "cheats enabled" (Bedrock: command blocks/console/scripts ignore the setting, others need it); dedicated-server-only; not-on-dedicated-server.

### Cheats

- Java: "Allow Commands" at world creation only affects offline single-player and LAN owners; opening to LAN can temporarily enable commands; permanent enabling requires editing `level.dat`.
- Bedrock: toggled in settings (except hardcore-like cases); enabling cheats permanently disables achievements for that world.

## Parameter Types

Arguments use formats like coordinates, target selectors, SNBT, and text components — see the parameter-types skill.

## Parsing and Execution

Commands are parsed (identify command, validate completeness/arguments) then executed. Client-side parsing (chat/command blocks) provides suggestions and early errors — client-parseable does not guarantee server-parseable.

- Java: an unparseable argument turns it and everything after it red with a syntax message above the chat bar; multiple spaces between arguments get collapsed to one on execution/history.
- Bedrock: next suggestion turns white; command block input only autocompletes; closing a command block GUI parses immediately server-side and writes errors to the output box.
- Unparseable commands show an error (`<--[here]` marker in Java; "Unknown command" / "Syntax error" in Bedrock).
- Function commands are all parsed when the function loads — one bad line blocks the whole function. Java macro lines parse at run time with their arguments.
- Bedrock scripts throw when executing unparseable commands.

### Output

Commands produce output values:

- **Success count** — the value passed to command blocks (readable by a comparator behind the block; retained until the next execution). Java: usually 0 or 1 (exception: `/execute`); commands not executable in command blocks have no success count. Bedrock: 0..2147483647 depending on the command.
- **Stored values** — Java: `/execute store` can store `success` (0 or 1) and `result` (integer, floored) from the executed command. Every command has both except `/execute` itself (without `if`/`unless`) and `/function` in certain cases.

### Results

After attempting a command, the result is one of:

- **Unparseable** — restrictions not met, incomplete input, or unparseable arguments.
- **Error** — the command threw a non-`CommandSyntaxException` exception: "An unexpected error occurred trying to execute that command", possible side effects (crashes), `/execute` branches may stop midway.
- **Void** — only `/function` (without `if`/`unless`): no `result`/`success` values to store.
- **Interrupted** — only `/execute`: the number of execution branches became 0 before the trailing subcommand (e.g. `/execute as @s run ...` in a command block, which is not an entity).
- **Success / failure** — otherwise: success count 0 = failure, > 0 = success. (Unparseable/error/void/interrupted are NOT "failure" even though their success count is 0; a "successful" command need not change the world, and a "failed" one may still have done something.)

## Command List

The complete list of Java commands (including upcoming ones) with per-command syntax: see the Minecraft Wiki "Commands" page. Java-specific notes: the wiki marks commands by game state (Java only, Bedrock only, Education only, etc.).

### Debug Commands (Java)

Debug tooling should not be enabled during normal play (may crash or irreversibly damage saves). Some commands only exist with the `MC_DEBUG_DEV_COMMANDS` debug tool enabled; others with `MC_DEBUG_CHASE_COMMAND`.

### Hidden Commands (Bedrock/Education)

Usually executable only via a WebSocket server, not in-game.

## Removed Commands

- **Bedrock developer commands** — for development/testing; normally invisible to players.
- **Agent commands (Education)** — `/attack`, `/collect`, `/createagent`, `/destroy`, `/detectredstone`, `/detect`, `/dropall`, `/drop`, `/getitemcount`, `/getitemdetail`, `/getitemspace`, `/inspectdata`, `/inspect`, `/move`, `/place`, `/till`, `/tpagent`, `/transfer`, `/turn` — replaced by `/agent`.

## April Fools Commands (Java)

Exist only in some April Fools versions: `/debugdim`, `/transform`, `/vote`, `/warp`. (26w14a's living block entity commands: see "Block entity commands".)
