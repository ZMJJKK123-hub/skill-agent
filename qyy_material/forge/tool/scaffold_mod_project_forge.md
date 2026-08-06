# Tool: scaffold_mod_project (Forge版)

## 用途
一键生成完整Forge mod项目目录结构 + 所有基础模板文件。

## 输入 JSON Schema
```json
{
  "mod_id": "my_mod",
  "mod_name": "My Mod",
  "mc_version": "26.2",
  "forge_version": "65.1.0",
  "package_path": "com.example.my_mod",
  "author": "AI_Agent"
}
```

## 输出
完整的项目目录结构，包含:
- build.gradle, settings.gradle, gradle.properties
- gradle wrapper
- Mod主类 (@Mod)
- META-INF/mods.toml
- pack.mcmeta
- assets/{mod_id}/ 基础目录
- data/{mod_id}/ 基础目录
