# 配方类型规范 (Recipe Types)

> **通用**: Minecraft原版数据包规范。  
> **路径**: `data/<modid>/recipes/<name>.json`  
> **注意**: MC 26.x 使用 `{ "id": "mod:item", "count": N }` 格式替代旧的 `"result": "mod:item"`

---

## 有序合成 (crafting_shaped)

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": ["XXX", "XYX", "XXX"],
  "key": {
    "X": { "item": "minecraft:diamond" },
    "Y": { "item": "minecraft:nether_star" }
  },
  "result": { "id": "mymod:my_item", "count": 1 }
}
```

## 无序合成 (crafting_shapeless)

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    { "item": "minecraft:iron_ingot" },
    { "tag": "minecraft:planks" }
  ],
  "result": { "id": "mymod:my_item", "count": 2 }
}
```

## 熔炼 (smelting)

```json
{
  "type": "minecraft:smelting",
  "ingredient": { "item": "mymod:raw_material" },
  "result": { "id": "mymod:smelted_material" },
  "experience": 0.7,
  "cookingtime": 200
}
```

## 高炉 (blasting)

```json
{
  "type": "minecraft:blasting",
  "ingredient": { "item": "mymod:raw_material" },
  "result": { "id": "mymod:smelted_material" },
  "experience": 1.0,
  "cookingtime": 100
}
```

## 烟熏 (smoking)

```json
{
  "type": "minecraft:smoking",
  "ingredient": { "item": "minecraft:beef" },
  "result": { "id": "minecraft:cooked_beef" },
  "experience": 0.35,
  "cookingtime": 100
}
```

## 锻造台 (smithing_transform) - MC 1.20+/26.x

```json
{
  "type": "minecraft:smithing_transform",
  "template": { "item": "minecraft:netherite_upgrade_smithing_template" },
  "base": { "item": "minecraft:diamond_sword" },
  "addition": { "item": "minecraft:netherite_ingot" },
  "result": { "id": "minecraft:netherite_sword" }
}
```

## 石材切割 (stonecutting)

```json
{
  "type": "minecraft:stonecutting",
  "ingredient": { "item": "mymod:my_block" },
  "result": { "id": "mymod:my_stairs", "count": 1 }
}
```

---

## ingredient 类型

| 类型 | JSON |
|------|------|
| 物品 | `{ "item": "minecraft:diamond" }` |
| 标签 | `{ "tag": "minecraft:planks" }` |
| 多选 | `[{ "item": "A" }, { "item": "B" }]` |

---

## MC 26.x 关键变更
- result格式: `{ "id": "modid:item", "count": N }` (非旧 `"result": "modid:item"`)
- 锻造台: 需要 `template` 字段
