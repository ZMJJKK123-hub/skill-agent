---
name: forge-concept-resources
description: |
  Forge 资源系统（assets / data）指南。
  
  【涵盖内容】
  - 两种资源系统：assets（逻辑客户端 / 视觉：模型、贴图、语言、着色器） vs data（逻辑服务端 / 玩法：配方、战利品、标签、进度）
  - 目录结构：src/main/resources/assets/<modid>/ 与 src/main/resources/data/<modid>/
  - pack.mcmeta 与资源包/数据包工作机理、多包叠加合并覆盖规则
  - ResourceLocation 概念：namespace:path、默认 namespace 为 minecraft、modid 通常等于命名空间
  - 资源命名规范：snake_case（小写+下划线）
  - 常见资源文件放置路径：模型（models/block, models/item）、贴图（textures/block, textures/item）、语言（lang）、配方（recipes）、战利品（loot_tables）、标签（tags）、进度（advancements）
  
  【关键 API】
  ResourceLocation, pack.mcmeta, assets, data, src/main/resources
  
  【适用场景】需要生成、放置或理解 mod 的 JSON 资源文件时
  【不涵盖】模型 JSON 细节（forge-resources-client）、数据包玩法 JSON 细节（forge-resources-server）
---

Resources
=========

A resource is extra data used by the game, and is stored in a data file, instead of being in the code. 
Minecraft has two primary resource systems active: one on the logical client used for visuals such as models, textures, and localization called `assets`, and one on the logical server used for gameplay such as recipes and loot tables called `data`.
[Resource packs][respack] control the former, while [Datapacks][datapack] control the latter.

In the default mod development kit, assets and data directories are located under the `src/main/resources` directory of the project. 

When multiple resource packs or data packs are enabled, they are merged. Generally, files from packs at the top of the stack override those below; however, for certain files, such as localization files and tags, data is actually merged contentwise. Mods define resource and data packs in their `resources` directories, but they are seen as subsets of the "Mod Resources" pack. Mod resource packs cannot be disabled, but they can be overridden by other resource packs. Mod datapacks can be disabled with the vanilla `/datapack` command.

All resources should have snake case paths and filenames (lowercase, using "_" for word boundaries), which is enforced in 1.11 and above.

`ResourceLocation`
------------------

Minecraft identifies resources using `ResourceLocation`s. A `ResourceLocation` contains two parts: a namespace and a path. It generally points to the resource at `assets/<namespace>/<ctx>/<path>`, where `ctx` is a context-specific path fragment that depends on how the `ResourceLocation` is being used. When a `ResourceLocation` is written/read as from a string, it is seen as `<namespace>:<path>`. If the namespace and the colon are left out, then when the string is read into an `ResourceLocation` the namespace will always default to `"minecraft"`. A mod should put its resources into a namespace with the same name as its mod id (e.g. a mod with the id `examplemod` should place its resources in `assets/examplemod` and `data/examplemod` respectively, and `ResourceLocation`s pointing to those files would look like `examplemod:<path>`.). This is not a requirement, and in some cases it can be desirable to use a different (or even more than one) namespace. `ResourceLocation`s are used outside the resource system, too, as they happen to be a great way to uniquely identify objects (e.g. [registries][]).

[respack]: ../resources/client/index.md
[datapack]: ../resources/server/index.md
[registries]: ./registries.md
