# mc_java_sources 迁移计划：26.2 → 1.21.11（方案 A + 方案 B）

> 执行人：pro 模型（或任何后续会话）。本文件是唯一任务书，读完按步骤执行。
> 前置事实（已在本会话验证）：
> - `mc_java_sources/` 是 **MC 26.2 / Forge 26.2-65.1.0** 时代的数据。
>   证据：`mc_java_sources/net/minecraftforge/gametest/ForgeGameTestHooks.java`
>   的哈希与会话 `data/sessions/1948349514a0/mod/.gradle/mavenizer/repo/
>   net/minecraftforge/forge/26.2-65.1.0/...ForgeGameTestHooks.java` 完全一致。
> - 26.2 已废弃（缺少数据）；现行目标 = **MC 1.21.11 / Forge 1.21.11-61.2.0**
>   （config.py 硬性事实、前端版本列表、forge-1.21.11 模板三方一致）。

---

## 目标

1. 把现有 `mc_java_sources/` 重命名为 `mc_java_sources_26.2/`（保留 26.2 数据备用，不再误用）。
2. 生成 1.21.11 源码树 `mc_java_sources_1.21.11/`（方案 A：解包 + 反编译）。
3. 接线：`server.py` 按会话版本复制对应源码树（方案 B），会话内目录名保持 `mc_java_sources` 不变。

---

## 步骤 0：前置确认（原料是否齐全）

1.21.11 的全部原料应该在模板的 mavenizer 缓存里（如果之前跑过 1.21.11 构建）：

```
mod_templates/minecraft/forge-1.21.11/.gradle/mavenizer/repo/
├── net/minecraftforge/forge/1.21.11-61.2.0/
│   └── forge-1.21.11-61.2.0-sources.jar        ← Forge 源码（直接解包）
├── net/minecraft/client-extra/1.21.11-20251223.124241/
│   └── client-extra-1.21.11-20251223.124241.jar ← MC 客户端 jar（需反编译）
└── net/minecraft/mappings_official/1.21.11-20251223.124241/
    ├── mappings_official-1.21.11-...-map2obf.tsrg.gz  ← 官方映射 official→obf
    └── mappings_official-1.21.11-...-map2srg.tsrg.gz  ← 官方映射 official→srg
```

缺失时：在 `mod_templates/minecraft/forge-1.21.11/` 跑一次 `gradlew.bat build`（或
`gradlew.bat runData`）让 ForgeGradle/mavenizer 自动下载齐全，然后再回来。

---

## 步骤 1：重命名旧目录

```powershell
# 在项目根（C:\Users\59639\Desktop\skill-agent）
git mv mc_java_sources mc_java_sources_26.2
```

改名后确认：`mc_java_sources/`（无后缀）不存在。

---

## 步骤 2：准备反编译工具

优先用 gradle 缓存里现成的（避免网络下载）：

```powershell
# Fernflower（ForgeGradle 自带依赖）
Get-ChildItem "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\org.jetbrains.java.decompiler" -Recurse -Filter "*.jar"
# Vineflower（社区增强版）
Get-ChildItem "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\org.vineflower" -Recurse -Filter "*.jar"
# SpecialSource（映射转换/反转）
Get-ChildItem "$env:USERPROFILE\.gradle\caches\modules-2\files-2.1\net.md-5.specialsource" -Recurse -Filter "*.jar"
```

都没有再从 Maven Central 下载（gradle 网络可达即可）：
- `org.vineflower:vineflower:1.10.1`
  → https://repo1.maven.org/maven2/org/vineflower/vineflower/1.10.1/vineflower-1.10.1.jar
- `net.md-5.specialsource:specialsource:1.11.6`（如需要反转映射）

---

## 步骤 3：生成 1.21.11 源码树（方案 A）

建议在临时目录工作：`_work/mc12111_src/`（生成完删掉）。

### A1. Forge 源码（直接解包）

```powershell
# 在临时目录
jar xf <cache>/net/minecraftforge/forge/1.21.11-61.2.0/forge-1.21.11-61.2.0-sources.jar
# 产物：net/minecraftforge/...（以及可能包含的 cpw/org 等）
```

### A2. MC 本体反编译（两条路线，先试路线一）

**路线一：Vineflower 直接吃 tsrg 映射（最快）**

1. 解压 `mappings_official-1.21.11-...-map2obf.tsrg.gz` → `map2obf.tsrg`（official→obf 方向）。
2. 反编译时应用映射。Vineflower 的 `-mappings` 参数把目标名映射到源 jar 的混淆名，
   所以需要的是 **obf→official** 方向——若 map2obf 方向不对，用 SpecialSource 反转：
   ```powershell
   java -cp specialsource.jar net.md-5.specialsource.SpecialSource `
     --in-jar client-extra-1.21.11-....jar `
     --out-jar client-named.jar `
     --mappings map2obf.tsrg --reverse
   ```
   或者直接试：
   ```powershell
   java -jar vineflower.jar -mappings map2obf.tsrg client-extra-1.21.11-....jar out/
   ```
3. 验证产物：`out/net/minecraft/resources/Identifier.java` 必须存在
   （1.21.11 模板的 Config.java 就 import `net.minecraft.resources.Identifier`）。
   同时抽查 `net/minecraft/gametest/framework/GameTestHelper.java`。

**路线二：ForgeGradle 同款流程（更稳，慢）**

1. SpecialSource：client jar obf→srg（用 map2srg 反转）→ `client-srg.jar`
2. Fernflower/Vineflower 反编译 `client-srg.jar` → srg 名源码
3. srg→official 名替换（tsrg 映射 + 文本替换），最终 agent 看到 official 名

> 如果两条路线都卡在工具/网络上：**备用方案**——反编译只做 MC 本体，
> Forge 部分（net/minecraftforge）永远直接来自 sources.jar，两者是独立的。

### A3. 组装目录

```
mc_java_sources_1.21.11/
├── module-info.java        （参考 26.2 版结构；不需要就删）
├── com/   （mojang/authlib、brigadier、datafixers…，随 A2 一并产出）
├── cpw/   （如 sources.jar 里有）
├── net/   （minecraft/ + minecraftforge/）
└── org/   （如需要）
```

> 对照 26.2 版目录结构（`mc_java_sources_26.2/`）保证顶层一致：
> com / cpw / net / org / module-info.java。

---

## 步骤 4：接线（方案 B）— server_app/server.py

定位 `_copy_template`（约第 153-193 行），把第 185 行的：

```python
mc_sources = PROJECT_ROOT / "mc_java_sources"
```

改为按版本选择：

```python
if version.startswith("1.21"):
    mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
elif version.startswith("26.2"):
    mc_sources = PROJECT_ROOT / "mc_java_sources_26.2"
else:
    # 默认（未传版本 / 恢复的旧会话）：现行目标 1.21.11
    mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
```

要点：
- 会话内的目标目录名**保持 `mc_java_sources` 不变**（`dest / "mc_java_sources"`），
  因此 `core/config.py` 提示词、`core/tools.py` 的 `_build_source_zip` skip 列表
  全部不用改。
- 26.2 遗留会话（如 1948349514a0）若按版本记录为 26.2，仍能拿到 26.2 源码。

---

## 步骤 5：验证

1. 手动建一个 1.21.11 会话（或直接调用 `_copy_template("minecraft", tmp, "forge", "1.21.11")`），
   检查会话内 `mod/mc_java_sources/net/minecraftforge/gametest/ForgeGameTestHooks.java`：
   - 存在 ✓
   - 哈希 ≠ 26.2 版（用 `mc_java_sources_26.2/` 里同名文件对比）
2. 抽查 `net/minecraft/resources/Identifier.java` 存在。
3. 抽查 1-2 个 1.21.11 特有 API 与 `mod_templates/minecraft/forge-1.21.11/` 模板代码吻合
   （如 `net/minecraftforge/event/BuildCreativeModeTabContentsEvent`）。
4. 跑一遍 1.21.11 会话的生成任务做端到端冒烟（可选）。

---

## 步骤 6：收尾

- 删除临时目录 `_work/mc12111_src/`
- `git add -A && git commit`（rename + 新树 + server.py 改动分开提交更清晰）
- 在 `mod_templates/minecraft/forge-1.21.11/KNOWN_ISSUES.md`（或根 KNOWN_ISSUES.md）
  追加一条本次迁移记录，方便后续会话。

---

## 风险与对策

| 风险 | 对策 |
|---|---|
| 反编译工具下载被网络/SSL 拦截（KNOWN_ISSUES 有先例） | 先扫 gradle 缓存；不行再下载；再不行用路线二或备用方案 |
| Vineflower 映射方向错误（产出 obf 名/报错） | 先用 1 个小包验证；方向不对就 SpecialSource `--reverse` |
| 1.21.11 结构与 26.2 差异（新类/改名） | 以实际产物为准，对照模板代码验证，不强行对齐 26.2 |
| 反编译耗时/体积大 | 分两步：先 MC 本体，再 Forge（直接解包），各自独立可验证 |
| server.py 改动影响旧会话 | 默认分支指向 1.21.11；26.2 会话显式匹配 26.2 |

---

## 参考事实速查（本会话已验证）

- 26.2 树标志文件哈希：`ForgeGameTestHooks.java = AA89305A717A3CBB4811AD3FC350253265CF57F3F4837C252BECBB454087E858`
- 1.21.11 模板：Forge `1.21.11-61.2.0`，Java toolchain 21，ForgeGradle `[7.0.3,8)`，
  mappings `official 1.21.11`，loader `[61,)`，minecraft `[1.21.11,1.22)`
- 前端版本列表：`["1.21.11","1.21.10","1.21.9"]`（1.21.9/1.21.10 复用 1.21.11 模板）
- 会话内 mc_java_sources 由 server.py `_copy_template` 复制，`_build_source_zip` 的
  skip 列表含 `mc_java_sources`
