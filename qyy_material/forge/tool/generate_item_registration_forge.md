# Tool: generate_item_registration (Forge版)

## 用途
生成Forge物品注册代码。

## 输入
```json
{
  "mod_id": "my_mod",
  "items": [
    {
      "name": "my_item",
      "stack_size": 64,
      "rarity": "common",
      "fire_resistant": false,
      "creative_tab": "my_tab"
    }
  ]
}
```

## 输出
- ModItems.java片段
- 物品模型JSON
- 语言文件条目
- 配方JSON (如果提供recipe)
- 创造标签页追加代码
