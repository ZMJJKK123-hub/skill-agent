---
name: forge-tag-guide
description: Forge Tag 标签系统（data tags）指南
---

# 标签系统规范 (Tag Guide)

> **通用**: Minecraft原版数据包规范。  
> **路径**: `data/<modid>/tags/<registry>/<tag_name>.json`

---

## 方块标签

### 挖掘工具标签
```json
{ "values": ["mymod:my_block", "mymod:my_ore"] }
```
路径: `data/<modid>/tags/blocks/mineable/pickaxe.json`  
对应的: `mineable/axe.json`, `mineable/shovel.json`, `mineable/hoe.json`

### 挖掘等级标签
```json
{ "values": ["mymod:my_block"] }
```
路径: `needs_diamond_tool.json`, `needs_iron_tool.json`, `needs_stone_tool.json`

### 结构标签
`walls.json`, `fences.json`, `fence_gates.json`, `logs.json`, `planks.json` 等

### 错误工具标签 (MC 26.x新)
`incorrect_for_diamond_tool.json`, `incorrect_for_iron_tool.json` 等

---

## 物品标签

```json
{
  "replace": false,
  "values": ["mymod:my_item", "minecraft:diamond"]
}
```

## 实体标签

```json
{ "replace": false, "values": ["mymod:my_entity"] }
```

## 流体标签

```json
{ "values": ["mymod:my_fluid", "mymod:my_fluid_flowing"] }
```

---

## 常用原版标签速查

| 功能 | 标签路径 |
|------|---------|
| 矿镐可挖 | `minecraft:mineable/pickaxe` |
| 斧可挖 | `minecraft:mineable/axe` |
| 需要钻石工具 | `minecraft:needs_diamond_tool` |
| 需要铁工具 | `minecraft:needs_iron_tool` |
| 墙 | `minecraft:walls` |
| 栅栏 | `minecraft:fences` |
| 原木 | `minecraft:logs` |
| 木板 | `minecraft:planks` |

---

## Agent 生成规则

| 方块属性 | 自动添加的标签 |
|---------|-------------|
| requiresCorrectTool + 硬度>=3 | `mineable/pickaxe` + `needs_iron_tool` |
| requiresCorrectTool + 硬度>=5 | `mineable/pickaxe` + `needs_diamond_tool` |
| 木质方块 | `mineable/axe` |
| 土质方块 | `mineable/shovel` |
| 栅栏 | `walls` 或 `fences` |
