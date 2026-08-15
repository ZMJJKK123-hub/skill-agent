---
name: minecraft-command-context
description: Command context — parameters, static vs dynamic, per-scenario contexts.
whenToUse: Use when reasoning about how commands/functions/text components resolve (executor, coordinates, permissions) in different contexts.
---

# Command Context

The command context (execution context, command source, command source stack) is the set of caller and environment parameters used for command execution and text component parsing.

## Parameters

Eight parameters: **permission level**, **executor** (executor name + executor entity), **environment** (execution dimension, position, rotation, anchor), and **output feedback**.

### Behavior

- `/function` runs inherit the executor parameters, environment parameters, and permission level — but NOT the output feedback. In Java single-player/LAN, function commands are capped at permission level 2 (even when the `/function` call ran at a higher level); servers can raise the cap via config.
- Bedrock: `/schedule`-planned functions also inherit executor/environment/permission.

### Static vs Dynamic Parameters (Java)

In Java, the executor name and all environment parameters are **static** once set: modifying the executor entity mid-function (e.g. `/tp` on the sheep used by `execute at @n[type=sheep] run function test`) does not change later commands' position/rotation/dimension.

- `/execute` freezes the dimension and rotation; `align`, `in`, `positioned <coords>`, `facing`, `rotated <angles>` freeze position/rotation; `anchored` freezes a dynamic position to the entity's feet/eyes (no effect on a static position).
- Example: chat-typed `/execute at @s run ...` has dynamic position+rotation but static dimension; `/execute positioned ~ ~ ~ run ...` has everything static.

In Bedrock, several parameters stay **dynamic** (fetched live from an entity): chat/WebSocket commands (position, rotation, dimension from the player), command block minecarts (position/rotation), entity-event/script/animation-controller/NPC commands (name, position, rotation, dimension), `/execute` itself (name), `at ...`/`positioned as ...` (position), `at ...`/`rotated as ...` (rotation). Dynamic positions use the mount's Y when the entity rides (e.g. player on minecart → player X/Z, minecart Y). If the depended-on entity is gone, defaults apply: name = "", dimension = empty, position = (0,0,0), rotation = (0,0) (e.g. `execute run say hi` in a command block says nothing; a `/schedule` whose executor died before running fails because the dimension is empty).

## Parameters in Detail

- **Permission level** — not modifiable by `/execute`. Function commands run at most at level 2 (configurable on servers).
- **Executor** — may be empty (command blocks). Used by `/msg`, `/say` (sender name), `@s`, default targets of `/tp`/`/kill`, player-requiring commands (`/clear`, `/gamemode`, `/playsound`), Java-only `/trigger`/`/teammsg`, and Java eye-height anchoring. Modified by `as`, `on`, and `summon` subcommands (Java sets name+entity together; Bedrock only the entity).
- **Execution dimension** — used for all coordinates, distance/box-restricted selectors (also `x`/`y`/`z` in Java), `/locate`. Modified by `at` and `in`.
- **Execution position** — origin of relative coordinates; base for local coordinates (Java: plus the anchor's eye offset), `/facing` starts, `/locate`, and default positions of `/summon`/`/spawnpoint`/`/playsound`. Modified by `align`, `at`, `positioned`, `in`.
- **Execution rotation** — coordinate system for local coordinates and `~` rotations in `/tp`/`/spawnpoint`. Modified by `at`, `facing`, `rotated`.
- **Execution anchor** (Java only) — feet or eyes (feet = execution position; eyes = position + eye height of the executor entity). Used for local coordinate origin, `/execute facing` start, `/tp ... facing ...` start, `/rotate ... facing ...` start. Modified by `anchored`. (Bedrock has no anchor parameter; `anchored` directly sets the position, freezing it if dynamic.)
- **Output feedback** — receives command success counts (command blocks, minecarts, scripts). `/execute store` adds feedback while keeping existing feedback (existing cannot be cleared). Functions don't inherit feedback.

## Contexts per Scenario

- **Server console** — level 4; name "Server"; no entity; dimension of world spawn (or Overworld); position = world-spawn block's NW-lower corner / (0,0,0); rotation (0,0); anchor feet; no feedback.
- **Server-executed functions** (`load`/`tick` tags, `tick.json`, `/schedule`) — same as console but level 2/1.
- **Player (chat / WebSocket / dev console)** — player's level; name = player name ("External"/"DevConsole" for WebSocket/dev console); entity = the player; dimension/position/rotation dynamic; anchor feet; no feedback.
- **Command block** — level 2/1; name = custom name or `@`/`!`; no entity; command block's dimension/center; its rotation / (0,0); receives success count.
- **Command block minecart** — like command block, but entity = the minecart, position/rotation dynamic.
- **Sign (Java, clicking a sign command)** — level 2; executor = the player; position = sign block center; rotation (0,0).
- **Advancement reward function (Java)** — level 2; executor = the rewarded player at their position/rotation.
- **Enchantment `run_function` effect (Java)** — level 2; executor = the effect entity at the effect position/rotation.
- **Bedrock entity-command contexts (entity events, scripts, animation controllers, NPCs)** — level 1; name/position/rotation/dimension dynamic from the entity; scripts return success count.
- **Bedrock dimension-command (scripts)** — level 1; name "script engine"; position (0,0,0); rotation (0,0); returns success count.
- **Test environment (Java)** — level 2; name "Server"; world-spawn dimension/position; rotation (0,0).

## Text Component Parsing

Text components resolve relative/local coordinates and selectors using the command context (output feedback is unused). `score` components with `name: "*"` show the reader's own score.

- **Command-invoked components** inherit the command's context: `/bossbar`, `/scoreboard`, `/team` (reader: executor `@s`); `/tellraw`, `/title` (readers: each receiving player).
- **Written book opened by a player (Java)** — player's context; reader = the player.
- **Written book placed on a lectern (Java)** — level 2; name "Lectern"; no entity; lectern dimension/center; rotation (0,0); no reader.
- **Sign text via NBT (Java)** — level 2; name "Sign"; sign center; rotation (0,0).
- **Text display entity (Java)** — level 2; executor = the text display entity itself.
- **Item modifiers `set_name`/`set_lore` (Java)** — when the `entity` field's entity exists, it is the executor (level 2) and reader.
