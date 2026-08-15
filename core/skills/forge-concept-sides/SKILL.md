---

name: forge-concept-sides
description: "Forge logical/physical sides: isClientSide, DistExecutor, thread groups, FMLEnvironment.dist."
whenToUse: "Use when writing side-aware Forge code or avoiding common client/server crashes."

---

# Sides in Minecraft

Two sides: **client** and **server**, each with two meanings:

- **Physical client**: the whole launcher program (graphical). **Physical server**: the dedicated `minecraft_server.jar` without GUI.
- **Logical server**: runs game logic (spawning, weather, inventories, AI); always on the `Server Thread`; present in both the physical server and single-player (inside the physical client).
- **Logical client**: accepts input and renders; runs on the `Render Thread`.

In Forge: `Dist` = physical side, `LogicalSide` = logical side.

## Side-specific operations

### `Level#isClientSide`

The default check: `true` = logical client, `false` = logical server (note: single-player's logical server also reports `false`). Run game logic only when `false`; applying logic on the client causes desync or crashes.

### `DistExecutor`

For code present on only one physical side (e.g. anything referencing `net.minecraft.client`). It prevents classloading via `invokedynamic`; executed methods should be static in a different class (use method references when no parameters).

- `#runWhenOn(Dist, ...)` / `#callWhenOn(Dist, ...)`, subdivided into `#safe*` (validates in dev) and `#unsafe*` variants. Note: checks the **physical** side — single-player always counts as `Dist.CLIENT`. Java 9+ wraps safe-variant exceptions in `BootstrapMethodError` in dev; prefer `#unsafe*` or `FMLEnvironment#dist`.

### Thread groups

`Thread.currentThread().getThreadGroup() == SidedThreadGroups.SERVER` guesses the logical side without a `Level`; use only as a last resort.

### `FMLEnvironment#dist` and `@OnlyIn`

`FMLEnvironment#dist` holds the physical side, determined at startup. Do **not** use `@OnlyIn` directly (it's only for stripped vanilla code); use `DistExecutor` or the `FMLEnvironment#dist` check.

## Common mistakes

- **Reaching across logical sides**: always use network packets, never direct references or static fields (race conditions in single-player's shared JVM).
- Accessing client-only classes (`Minecraft.getInstance()`) from common code crashes physical servers.

## One-sided mods

Mods must load on both physical sides. One-sided mods should register event handlers inside `DistExecutor#runWhenOn` (doing nothing on the wrong side) and should not register blocks/items. Set `displayTest` in `mods.toml`: `MATCH_VERSION` (default), `IGNORE_SERVER_VERSION` (server-only), `IGNORE_ALL_VERSION` (no server component), or `NONE` + an `IExtensionPoint.DisplayTest` extension:

```java
ModLoadingContext.get().registerExtensionPoint(IExtensionPoint.DisplayTest.class, () -> new IExtensionPoint.DisplayTest(() -> NetworkConstants.IGNORESERVERONLY, (a, b) -> true));
```
