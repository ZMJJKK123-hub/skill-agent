---
name: forge-version-matrix
description: Forge 版本兼容性矩阵：Minecraft↔Forge 版本对应与 Gradle/JDK 要求（MC 26.x 最新）
---

# Forge 版本兼容性矩阵

> **用途**: Agent 生成 build.gradle / gradle.properties 时查询正确的版本号组合。  
> **更新日期**: 2026-08-04

---

## 当前推荐版本

| 组件 | 推荐版本 | 发布日期 |
|------|---------|----------|
| Minecraft | **26.2** | 2026-06-16 |
| Forge | **65.1.0** (recommended) | — |
| Forge (latest) | **65.1.0** | — |
| JDK | **25** | — |
| Gradle | **8.x** | — |

---

## 完整版本映射表

### MC 26.x 系列（新版本号体系）

| Minecraft | Forge (recommended) | Forge (latest) | JDK | Gradle |
|-----------|-------------------|----------------|-----|--------|
| 26.2 | 65.1.0 | 65.1.0 | 25 | 8.9+ |
| 26.1.2 | 64.1.0 | 64.1.0 | 25 | 8.9+ |
| 26.1.1 | — | 63.0.2 | 25 | 8.9+ |
| 26.1 | — | 62.0.9 | 25 | 8.9+ |

### MC 1.21.x 系列（经典版本号）

| Minecraft | Forge (recommended) | Forge (latest) | JDK |
|-----------|-------------------|----------------|-----|
| 1.21.11 | 61.1.0 | 61.1.14 | 21 |
| 1.21.10 | 60.1.0 | 60.1.13 | 21 |
| 1.21.9 | — | 59.0.5 | 21 |
| 1.21.8 | 58.1.0 | 58.1.20 | 21 |
| 1.21.7 | — | 57.0.3 | 21 |
| 1.21.6 | — | 56.0.9 | 21 |
| 1.21.5 | 55.1.0 | 55.1.11 | 21 |
| 1.21.4 | 54.1.14 | 54.1.17 | 21 |
| 1.21.3 | 53.1.0 | 53.1.11 | 21 |
| 1.21.1 | 52.1.0 | 52.1.16 | 21 |
| 1.21 | — | 51.0.33 | 21 |
| 1.20.6 | 50.2.0 | 50.2.10 | 21 |
| 1.20.4 | 49.2.0 | 49.2.8 | 17 |
| 1.20.2 | 48.1.0 | 48.1.0 | 17 |
| 1.20.1 | 47.4.10 | 47.4.22 | 17 |
| 1.20 | — | 46.0.14 | 17 |
| 1.19.4 | 45.4.0 | 45.4.3 | 17 |
| 1.19.2 | 43.5.0 | 43.5.2 | 17 |
| 1.18.2 | 40.3.0 | 40.3.12 | 17 |
| 1.16.5 | 36.2.34 | 36.2.42 | 8 |

---

## Forge Gradle 插件版本映射

| Forge版本范围 | ForgeGradle 插件版本 | Gradle 最低版本 |
|-------------|-------------------|----------------|
| 65.x (MC 26.2) | `net.minecraftforge.gradle` 7.0.17+ | 8.9 |
| 62-64.x (MC 26.1.x) | `net.minecraftforge.gradle` 7.0.17+ | 8.9 |
| 52-61.x (MC 1.21.x) | `net.minecraftforge.gradle` 6.0+ | 8.5 |
| 47-51.x (MC 1.20.x) | `net.minecraftforge.gradle` 5.1+ | 7.5 |

---

## ForgeGradle 插件仓库

```
maven {
    name = "MinecraftForge"
    url = "https://maven.minecraftforge.net/"
}
```

插件ID: `net.minecraftforge.gradle`

---

## Mappings 选择

| Mappings 类型 | 说明 |
|-------------|---------|
| **官方（内置）** | ForgeGradle 7 已内置 Mojang Official 反混淆，**无需在 build.gradle 显式配置 mappings 块** |
| Parchment | 带参数名、人类可读（如需，需额外配置 parchment 仓库） |
| MCP `stable` | 旧版，不推荐 |

---

## 版本号验证规则

Agent 在生成配置前必须检查：
1. `minecraft_version` 是否在 Forge 支持列表中
2. `forge_version` 的前两位数字 = `minecraft_version` 的主版本号 + 39（约等于）
   - 例如 MC 26.2 → Forge 65.x (26 + 39 = 65)
3. Java toolchain 版本 ≥ 25（MC 26.x）或 ≥ 17（MC 1.20.x-1.21.x）
4. Gradle 版本 ≥ 8.9（ForgeGradle 7.0.17+）

---

## 实时查询 API

- **Minecraft 版本列表**: `https://launchermeta.mojang.com/mc/game/version_manifest.json`
- **Forge 版本列表**: `https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json`
- **Forge Maven**: `https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml`
