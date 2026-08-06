# Tool: generate_mods_toml (Forge版)

## 用途
生成 `META-INF/mods.toml` 文件。

## 输入
```json
{
  "mod_id": "my_mod",
  "mod_name": "My Mod",
  "mod_version": "1.0.0",
  "description": "A forge mod",
  "authors": "Author",
  "license": "MIT",
  "dependencies": [
    {"mod_id": "forge", "mandatory": true, "version_range": "[65,)"},
    {"mod_id": "minecraft", "mandatory": true, "version_range": "[26.2,27)"}
  ]
}
```

## 输出
完整的 mods.toml 内容
