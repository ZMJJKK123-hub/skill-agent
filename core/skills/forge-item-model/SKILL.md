---
name: forge-item-model
description: Forge 物品模型 JSON 规范（assets）
---

# 物品模型JSON规范 (Item Model Spec)

> **通用**: 适用于所有加载器。  
> **路径**: `assets/<modid>/models/item/<item_name>.json`

---

## Parent 类型

| Parent | 用途 | 手持姿势 |
|--------|------|---------|
| `minecraft:item/generated` | 普通物品（扁平图标） | 平放手中 |
| `minecraft:item/handheld` | 工具/武器 | 斜45°手持 |
| `minecraft:item/handheld_rod` | 钓鱼竿类 | 钓鱼竿姿势 |
| `<modid>:block/<block>` | 方块物品 | 方块渲染 |
| `minecraft:item/template_spawn_egg` | 刷怪蛋 | — |

---

## 完整示例

### 普通物品
```json
{
  "parent": "minecraft:item/generated",
  "textures": { "layer0": "mymod:item/my_item" }
}
```

### 工具（剑/镐/斧/铲/锄）
```json
{
  "parent": "minecraft:item/handheld",
  "textures": { "layer0": "mymod:item/my_sword" }
}
```

### 多层纹理（叠加层，如染色工具）
```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "mymod:item/my_tool_base",
    "layer1": "mymod:item/my_tool_overlay"
  }
}
```

### 方块物品
```json
{ "parent": "mymod:block/my_block" }
```

### 刷怪蛋
```json
{ "parent": "minecraft:item/template_spawn_egg" }
```

---

## Agent 生成规则

| 物品类型 | parent | 纹理路径 |
|---------|--------|---------|
| 普通物品/材料 | `item/generated` | `<modid>:item/<name>` |
| 剑/镐/斧/铲/锄 | `item/handheld` | `<modid>:item/<name>` |
| 食物 | `item/generated` | `<modid>:item/<name>` |
| 盔甲 | `item/generated` | `<modid>:item/<name>` |
| 刷怪蛋 | `item/template_spawn_egg` | — |
| 方块物品 | `<modid>:block/<name>` | — |
| 钓鱼竿 | `item/handheld_rod` | `<modid>:item/<name>` |
