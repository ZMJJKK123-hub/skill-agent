---
name: forge-mods-toml
description: Forge mods.toml 元数据文件规范
---

# Forge mods.toml 元数据规范

> **用途**: Agent 生成 `META-INF/mods.toml` 时参考。  
> **加载器**: Forge 65.x (MC 26.2)

---

## 完整模板

```toml
modLoader = "javafml"
loaderVersion = "[65,)"

license = "${mod_license}"

[[mods]]
modId = "${mod_id}"
version = "${mod_version}"
displayName = "${mod_name}"
displayURL = ""
logoFile = ""
credits = ""
authors = "${mod_authors}"
description = '''${mod_description}'''

[[dependencies.${mod_id}]]
    modId = "forge"
    mandatory = true
    versionRange = "${forge_version_range}"
    ordering = "NONE"
    side = "BOTH"

[[dependencies.${mod_id}]]
    modId = "minecraft"
    mandatory = true
    versionRange = "${minecraft_version_range}"
    ordering = "NONE"
    side = "BOTH"
```

---

## 字段说明

### [[mods]] 条目

| 字段 | 必需 | 说明 |
|------|-----|------|
| `modId` | ✅ | 唯一ID，小写+下划线 |
| `version` | ✅ | 版本号，支持 `${file.jarVersion}` |
| `displayName` | ✅ | 显示名称 |
| `description` | ✅ | 描述，支持多行 `'''...'''` |
| `authors` | ❌ | 作者 |
| `logoFile` | ❌ | logo路径 |

### [[dependencies.xxx]] 条目

| 字段 | 必需 | 说明 |
|------|-----|------|
| `modId` | ✅ | 依赖的mod ID |
| `mandatory` | ✅ | `true`=必须, `false`=可选 |
| `versionRange` | ✅ | Maven版本范围 |
| `ordering` | ✅ | `NONE`, `BEFORE`, `AFTER` |
| `side` | ✅ | `BOTH`, `CLIENT`, `SERVER` |

---

## Forge vs NeoForge mods.toml 差异

| 差异 | Forge | NeoForge |
|------|-------|----------|
| 文件名 | `mods.toml` | `neoforge.mods.toml` |
| 依赖嵌套 | `[[dependencies.xxx]]` | `[[mods.dependencies.xxx]]` |
| 必需标记 | `mandatory = true` | `type = "required"` |

---

## 版本范围表达式

| 表达式 | 含义 |
|--------|------|
| `[65,66)` | >=65 且 <66 |
| `[65,)` | >=65 |
| `[26.2,27)` | >=26.2 且 <27 |
