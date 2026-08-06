# 掉落表规范 (Loot Table Spec)

> **通用**: Minecraft原版数据包规范。  
> **路径**: `data/<modid>/loot_tables/blocks/<block_name>.json`

---

## 方块自身掉落
```json
{
  "type": "minecraft:block",
  "pools": [{
    "rolls": 1,
    "entries": [{ "type": "minecraft:item", "name": "mymod:my_block" }],
    "conditions": [{ "condition": "minecraft:survives_explosion" }]
  }]
}
```

## 精准采集条件掉落
```json
{
  "type": "minecraft:block",
  "pools": [
    {
      "rolls": 1,
      "entries": [{ "type": "minecraft:item", "name": "mymod:my_block" }],
      "conditions": [
        { "condition": "minecraft:match_tool", "predicate": { "enchantments": [{ "enchantment": "minecraft:silk_touch", "levels": { "min": 1 } }] } }
      ]
    },
    {
      "rolls": 1,
      "entries": [{ "type": "minecraft:item", "name": "mymod:my_item", "functions": [{ "function": "minecraft:set_count", "count": { "min": 2, "max": 4 } }] }],
      "conditions": [{ "condition": "minecraft:survives_explosion" }]
    }
  ]
}
```

## 实体掉落
```json
{
  "type": "minecraft:entity",
  "pools": [{
    "rolls": 1,
    "entries": [
      { "type": "minecraft:item", "name": "mymod:my_item", "weight": 1,
        "functions": [{ "function": "minecraft:set_count", "count": { "min": 1, "max": 3 } },
                      { "function": "minecraft:looting_enchant", "count": { "min": 0, "max": 1 } }] }
    ]
  }]
}
```

---

## 常用条件 (conditions)

| 条件 | 说明 |
|------|------|
| `survives_explosion` | 不被爆炸摧毁 |
| `match_tool` + silk_touch | 精准采集 |
| `random_chance` | 概率掉落 float 0.0-1.0 |
| `killed_by_player` | 玩家击杀 |
| `entity_properties` | 实体属性匹配 |

## 常用函数 (functions)

| 函数 | 说明 |
|------|------|
| `set_count` | 设置数量 `{ "min": N, "max": M }` |
| `looting_enchant` | 掠夺加成 |
| `smelt` | 自动熔炼掉落 |
| `set_nbt` | 设置NBT标签 |
| `copy_name` | 复制方块名称 |
| `explosion_decay` | 爆炸递减 |
