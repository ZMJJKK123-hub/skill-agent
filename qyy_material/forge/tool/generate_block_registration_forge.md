# Tool: generate_block_registration (Forge版)

## 用途
生成Forge方块注册代码(ModBlocks.java + 对应BlockItem的ModItems.java片段)。

## 输入
```json
{
  "mod_id": "my_mod",
  "blocks": [
    {
      "name": "my_block",
      "base_class": "Block",
      "hardness": 3.0,
      "resistance": 3.0,
      "sound_type": "STONE",
      "requires_tool": true,
      "tool_type": "pickaxe",
      "tool_level": "diamond",
      "luminance": 0
    }
  ]
}
```

## 输出
- ModBlocks.java (含DeferredRegister + 所有方块注册)
- ModItems.java片段 (含BlockItem注册)
- Blockstate JSON
- 方块模型JSON
- 方块物品模型JSON
- 掉落表JSON
- 标签JSON (mineable + needs_tool)
