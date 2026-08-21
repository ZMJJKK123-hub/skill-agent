---

name: forge-concept-resources
description: "Forge 资源系统：assets 目录（客户端视觉资源：模型、纹理、本地化）、data 目录（服务端游戏逻辑：配方、战利品表）、资源包（Resource Packs）控制 assets、数据包（Datapacks）控制 data、ResourceLocation 命名空间与路径（namespace:path）、默认命名空间 minecraft、modid 命名空间使用、资源合并规则（覆盖与合并）、snake_case 路径规范、src/main/resources 目录结构、资源包禁用/覆盖机制、数据包 /datapack 命令、资源唯一标识、注册表使用。"
whenToUse: "Use when understanding Minecraft resource systems, ResourceLocation naming, or where to place mod assets/data."

---

# Resources

A resource is extra data used by the game, stored in a data file instead of in code. Minecraft has two primary resource systems: `assets` (logical client; visuals such as models, textures, localization) and `data` (logical server; gameplay such as recipes and loot tables). Resource packs control the former; datapacks control the latter.

In the default mod development kit, assets and data directories are under `src/main/resources`.

When multiple resource/data packs are enabled they are merged: files from packs at the top of the stack override those below, except for certain files (localization, tags) which merge contentwise. Mods define their packs in `resources`; mod resource packs cannot be disabled but can be overridden; mod datapacks can be disabled with `/datapack`. All resources should use snake_case paths (enforced since 1.11).

## ResourceLocation

Minecraft identifies resources via `ResourceLocation`, which has a namespace and a path, generally pointing to `assets/<namespace>/<ctx>/<path>`. As a string it reads `<namespace>:<path>`; without a namespace the default is `minecraft`. A mod should use its mod id as the namespace (e.g. `examplemod:<path>`), though other namespaces are allowed. `ResourceLocation`s are also used outside the resource system to uniquely identify objects (e.g. registries).
