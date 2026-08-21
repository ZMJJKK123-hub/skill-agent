---

name: minecraft-item-format
description: "Minecraft Item Format 物品格式：Data Format 数据格式（两种存储方式：带 Slot 字节标签 容器内、无槽位 属性数据 如物品实体、根标签 id 物品类型/组件补丁/count 堆叠数量）、Item stacks 物品堆栈（添加物品类型特定数据：堆叠数量+组件补丁、有效组件=默认组件+补丁 F3+H高级工具提示显示）、Encoding Formats 编码格式（Basic format 基本格式：物品ID必需 count和patch可选 最常用、Optional format 可选格式：可为空 仅用于快捷栏槽位）、Strict Validation 严格验证（定义物品堆栈和补丁组件时运行：组件检查 max_damage 暗示最大堆叠≤1、container/bundle_contents/charged_projectiles 要求每个包含物品通过计数验证；计数检查 count不能超过最大堆叠大小；验证失败使物品无效 命令失败 文件加载失败）、Default Components 默认组件（无外部修改获得的物品有默认组件、不序列化、无法通过/data获取、组件等于默认时不存储、与物品类型强关联 不继承、物品替换时只有序列化补丁组件携带、创造模式物品可能携带额外组件 匹配时显示蓝色类别+可堆叠、至少12个默认组件）。"
whenToUse: "Use when understanding item stack data in saves, commands, or datapack item components."

---

# Item Format

This content applies only to Java Edition. (For storage before Java 1.20.5, see the legacy article; for Bedrock, see the Bedrock item format.)

Item stacks are the game's unified way to store items across files: mob inventories, villager trades, item entities, container inventories, etc.

## Data format

Items are stored in two ways: with a `Slot` byte tag (in containers) or without a slot (as property data, e.g. item entities).

Storage format (root tag):

- `id` (string, required): (namespace ID) item type; absent → becomes air when chunks load or items generate.
- `components` (compound): the item's component patch.
  - `<component ID>` (any): one component and its data; the namespace may be omitted when setting, added as `minecraft:` on export.
  - `!<component ID>` (compound): invalidates a component; content has no effect.
- `count` (int): (0<v≤max stack size) stack count; defaults to 1 when absent/invalid.

## Item stacks

Item stacks add item-type-specific data: stack count and component patch. Effective components = default components + patch (the count shown in the F3+H advanced tooltip).

### Encoding formats

- Basic format: item ID required; count and patch optional. The most common format.
- Optional format: can be empty; used only for hotbar slots.

### Strict validation

Validation runs when defining item stacks and patching components (e.g. `/give`, `/item`):

- Component checks: `max_damage` implies max stack size ≤1; `container`, `bundle_contents` (total ≤1 stack), and `charged_projectiles` require every contained item to pass count validation.
- Count check: count must not exceed the max stack size.

In short, an item cannot be both damageable and stackable, and counts cannot exceed the max. Failed validation makes the item invalid — the command fails and the file fails to load.

### Default components

Items obtained without external modification have default components (the components of an item from `/give` without a patch). Default components are not serialized, cannot be fetched via `/data`, and are not stored when a component equals its default. They are strongly tied to the item type and not inherited by other items; on item replacement, only serialized patch components carry over.

In the creative inventory, items may carry extra components. When the item's components exactly match the creative entry, the item shows its category in blue in the tooltip and can stack with the creative item (if stackable). Items have at least 12 default components, varying by type.
