# skill-agent —— Minecraft Forge MOD 制作 Agent

一个能**全自动开发 Minecraft Forge 模组**的 AI Agent 引擎：给它一句需求，它会自主加载领域知识（技能库）、编写 Java 代码与资源文件、运行 Gradle 构建、跑 GameTest 自动化测试、修复编译错误，最终交付一个可直接放进 `.minecraft/mods/` 的 **mod jar**。

- **核心引擎**（`core/`）：Agent 主循环 + 85 个工具 + 200+ 技能文档（Forge 概念 / MC 数据包格式），带上下文压缩、多 Agent 团队协作、监管者、Git Worktree 隔离等完整机制
- **网页版**（`server_app/`）：FastAPI 网站，建会话、实时看 agent 干活、下载产物
- **外部接入**（`tsinghua agent server/`）：把 agent 以 OpenAI 兼容 API 暴露给第三方平台

目标版本硬约束：**Minecraft 1.21.11 + Forge 1.21.11-61.2.0 + Java 21**（模板已写死，agent 会自动遵守）。

> 适用系统：**Windows 10/11 x64**。Agent 的提示词、工具与安全规则均按 Windows cmd 定制；Linux/macOS 需自行改造。

---

## 目录

1. [环境要求](#1-环境要求)
2. [安装基础工具（裸机必看）](#2-安装基础工具裸机必看)
3. [克隆项目并安装依赖](#3-克隆项目并安装依赖)
4. [配置 .env（最关键的一步）](#4-配置-env最关键的一步)
5. [连通性自检](#5-连通性自检)
6. [跑第一个 MOD 任务](#6-跑第一个-mod-任务)
7. [监控与验收](#7-监控与验收)
8. [可选：启动网页版](#8-可选启动网页版)
9. [故障排查（实测踩坑）](#9-故障排查实测踩坑)
10. [目录结构速览](#10-目录结构速览)

---

## 1. 环境要求

| 项目 | 要求 | 说明 |
|---|---|---|
| 操作系统 | Windows 10/11 x64 | 提示词/工具链为 cmd 定制 |
| 磁盘 | ≥ 10 GB 空闲 | JDK + Gradle/MC 依赖缓存（约 2-3 GB）+ 会话工作区 |
| 内存 | ≥ 8 GB | GameTest 服务器需 2-3 GB 堆 |
| 网络 | 可访问 pypi、`maven.minecraftforge.net`、`open.bigmodel.cn` | 首次构建要下载约 0.5-1 GB Forge/MC 依赖 |
| API Key | 智谱开放平台 Key（或其他 OpenAI 兼容服务） | 见 [第 4 步](#4-配置-env最关键的一步) |

---

## 2. 安装基础工具（裸机必看）

> 全新 Windows 机器通常**没有** Python/Git/JDK。以下每一步都给出 winget 安装命令（推荐）和验证命令。若没有 winget，去官网下载安装包手动装，效果相同。

### 2.1 Python 3.10+（推荐 3.13）

```bat
winget install --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
```

**新开一个终端**验证（必须新开，旧终端不会刷新 PATH）：

```bat
python --version
pip --version
```

> ⚠️ **坑 1：Microsoft Store 假 python**。如果 `python --version` 没输出或弹出 Microsoft Store，说明你运行的是系统自带的占位程序（`WindowsApps\python.exe`），不是真 Python。按上面 winget 安装后**重开终端**即可；若还不行，检查"设置 → 应用 → 应用执行别名"，把 `python.exe` / `python3.exe` 的别名关掉。

> ⚠️ **坑 2：winget 说"已安装"但命令不存在**。可能是之前装 Python 时自定义过安装路径（比如装到了 D 盘），注册表里还有记录。先 `winget list --name Python` 查看，再 `winget uninstall --id Python.Python.3.13` 卸干净，重新安装到默认位置。

### 2.2 Git

```bat
winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
git --version
```

### 2.3 JDK 21（Forge 1.21.11 硬性要求，必须 21）

```bat
winget install --id EclipseAdoptium.Temurin.21.JDK --silent --accept-package-agreements --accept-source-agreements
```

装完**手动设置** `JAVA_HOME`（两种方式任选）：

- 图形界面：`Win+R` 输入 `sysdm.cpl` → 高级 → 环境变量 → 用户变量新建 `JAVA_HOME`，值为 `C:\Program Files\Eclipse Adoptium\jdk-21.0.x-hotspot`（以实际目录为准，`dir "C:\Program Files\Eclipse Adoptium"` 可查）
- 或 PowerShell（一次性，推荐）：

```powershell
$jdk = (Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory | Where-Object Name -like "jdk-21*").FullName
[Environment]::SetEnvironmentVariable('JAVA_HOME', $jdk, 'User')
```

**新开终端**验证：

```bat
java -version
echo %JAVA_HOME%
```

> ⚠️ **坑 3：GitHub 下载失败**。winget 下载 JDK 走 GitHub Releases，国内网络可能报 `InternetOpenUrl() failed (0x80072efd)`。解决办法：① 开代理后重试；② 去 Adoptium 官网（adoptium.net）手动下载 JDK 21 MSI 安装；③ 从别的机器把同版本 JDK 目录拷贝过来（如拷到 `C:\Java\jdk-21`），再把 `JAVA_HOME` 指过去即可——JDK 对安装位置没有要求，**只要 `JAVA_HOME\bin\java.exe` 真实存在**。

> ⚠️ **坑 4：JAVA_HOME 值带了尾随空格（本项目实测踩过）**。在 cmd 里写 `set JAVA_HOME=C:\Java\jdk-21 && ...` 时，**&& 之前的空格会被并入变量值**，变成 `JAVA_HOME="C:\Java\jdk-21 "`，Gradle 启动即报：
> ```
> ERROR: JAVA_HOME is set to an invalid directory: C:\Java\jdk-21
> ```
> 看起来"目录明明存在"，实际是值末尾多了个空格。cmd 里必须写带引号的形式：`set "JAVA_HOME=C:\Java\jdk-21"`，或干脆用上面的系统属性面板/PowerShell 方式设置。**注意：agent 是独立子进程，会继承启动它的终端里的环境变量——改完环境变量后必须重启 agent 会话才能生效，正在跑的会话改不回来。**

### 2.4 Node.js（可选，仅网页版需要）

```bat
winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
node --version
```

只用命令行跑 MOD 任务的话，可以不装。

---

## 3. 克隆项目并安装依赖

```bat
git clone <本仓库地址> skill-agent
cd skill-agent
pip install -r requirements.txt
```

国内网络建议用清华镜像加速（ usually 快 10 倍以上）：

```bat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

验证引擎可正常导入（应输出 `IMPORT_OK tools= 85` 左右的数字）：

```bat
set "DSH_MODE=mod"
set "DEEPSEEK_API_KEY=dummy"
python -c "import core.agent as a; print('IMPORT_OK tools=', len(a.tool_registry.names()))"
```

> 说明：项目自带 Forge 模板（`mod_templates/minecraft/forge-1.21.11`）与 MC/Forge 反编译参考源码（`mc_java_sources_1.21.11/`），clone 后即全部就位，会话创建时以目录联结（junction）挂进工作区，无需额外下载。

---

## 4. 配置 .env（最关键的一步）

`.env` 被 gitignore，**clone 后不存在**，需在**项目根目录**手工创建。最小可用配置（智谱为例）：

```ini
# 智谱开放平台 API Key
DEEPSEEK_API_KEY=你的Key

# 模型名
DSH_MODEL=GLM-5.3-Flash

# API 端点（见下方说明，二选一！）
DSH_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4

# 上下文窗口（token），决定自动压缩触发阈值 = 80% × 此值
DSH_CONTEXT_WINDOW=128000
```

### 4.1 DSH_BASE_URL 怎么填（填错直接 401）

| 你的 Key 类型 | DSH_BASE_URL 填 |
|---|---|
| 智谱 **Coding Plan 订阅**包月 Key | `https://open.bigmodel.cn/api/coding/paas/v4` |
| 智谱开放平台**按量计费** Key | `https://open.bigmodel.cn/api/paas/v4` |
| 其他 OpenAI 兼容服务 | 该服务的 OpenAI 兼容端点（DeepSeek 为 `https://api.deepseek.com`） |

> Coding Plan 的 Key 走直连地址会报错，反之亦然——**订阅 Key 配订阅端点**。

### 4.2 reasoning 模型（GLM 系列必设）的两个参数

不设时代码默认按 **100 万 token** 窗口计算压缩阈值（80% = 80 万），而 GLM 系列实际窗口是 128K/200K——结果是自动压缩永远不主动触发，直到撞上 API 的上下文超限错误才被动压缩，浪费轮次。**GLM 建议填 `128000`**；用 200K 窗口模型可填 `200000`。

同时，GLM-5.3 系列是 **reasoning（思考）模型**，思考与可见回复**共享**单次补全预算；agent 默认预算 8000 token，复杂任务下思考就会把预算烧光，API 侧表现为**每轮挂约 3 分钟后返回空响应**、agent 卡死在重试。设：

```ini
DSH_MAX_COMPLETION_TOKENS=32768
```

### 4.3 其他可用环境变量（按需）

| 变量 | 默认 | 说明 |
|---|---|---|
| `DSH_MAX_COMPLETION_TOKENS` | `8000` | 单次补全上限（含 reasoning 思考预算）；GLM-5.3 系列 reasoning 模型建议 `32768+`，DeepSeek 等非思考模型保持默认 |
| `DSH_MAX_TOOL_ROUNDS` | `200` | 单任务工具轮上限；模型临耗尽时可调 `extend_round_limit` 工具自行扩展 |
| `DSH_MAX_TOTAL_ROUNDS` | `300` | 总轮数上限（同样可被 extend_round_limit 扩展） |
| `DSH_ABSOLUTE_MAX_ROUNDS` | `1000` | 轮次预算绝对硬顶（extend 也不能突破，防无限续命烧钱） |
| `DSH_AUTO_MODE` | `0` | `1` = 全自动模式，`ask_user_question` 不阻塞等待用户 |
| `DSH_MAX_TOOL_ROUNDS` | `100` | 单任务工具轮上限（防死循环） |
| `DSH_MAX_TOTAL_ROUNDS` | `150` | 总轮数硬上限 |
| `DSH_DISABLE_CLIENT_TOOLS` | 未设 | `1` = 低内存服务器模式，移除所有游戏 GUI 工具，只保留 build+GameTest+资源校验 |
| `DSH_SANDBOX_MODE` | `full-access` | 会话沙箱：`full-access` / `workspace-write` / `read-only` |

**超时与轮次预算的运行时策略**（引擎不会写死卡死 agent）：bash 默认 30s（上限 600s）、后台任务默认 600s（上限 3600s）、构建/GameTest 默认 900s/180s（上限 3600s）——**这些超时由模型按任务自估传入**（冷缓存首建会自动传 1800-2700s）；轮次预算每轮通过 runtime-context 向模型播报"已用/上限（剩余）"，剩余 <20 时预警，模型可调 `extend_round_limit(extra_rounds=N)` 申请更多轮数（绝对硬顶 1000）。

---

## 5. 连通性自检

跑 MOD 任务前，先用 20 行脚本确认 Key/URL/模型三者匹配。把下面内容存为项目根目录 `test_connectivity.py`：

```python
# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["DSH_NO_ENV_FILE"] = "1"
from dotenv import load_dotenv
load_dotenv(".env")
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DSH_BASE_URL"],
    http_client=httpx.Client(trust_env=False, verify=False, timeout=120.0),
)
r = client.chat.completions.create(
    model=os.environ["DSH_MODEL"],
    messages=[{"role": "user", "content": "回复两个字：连通"}],
    max_tokens=512,
)
print("REPLY:", (r.choices[0].message.content or "").strip())
print("CONNECTIVITY_OK")
```

运行：

```bat
python test_connectivity.py
```

输出 `REPLY: 连通` + `CONNECTIVITY_OK` 即成功；报 401/认证错误回到第 4 步核对 Key 与端点组合。

---

## 6. 跑第一个 MOD 任务

### 6.1 写需求提示词

新建 `prompt.txt`，用自然语言描述 MOD。例如（可直接使用，覆盖方块/物品/合成/资源/GameTest 全链路）：

```text
制作一个名为 "gemcraft"（modid 就用 gemcraft）的魔法宝石 MOD，要求以下全部功能：
1. 自定义矿物方块：Gem Ore，开采掉落 1-2 个宝石
2. 自定义物品（放在自定义创造模式标签页 GemCraft 下）：
   - Gem 宝石（材料）、Gem Sword（伤害 9，耐久 1200）、
     Gem Pickaxe（挖掘速度高于铁镐）、Gem Apple（食物，食用后 30 秒速度 I）
3. 有序合成配方：宝石+木棍→剑；3宝石+2木棍→镐；8宝石环绕苹果→宝石苹果
4. 资源（1.21.11 格式）：items 模型定义、models、blockstate、
   en_us/zh_cn 双语 lang、loot table；贴图可用纯色 PNG
5. GameTest（src/test/java）：测试注册、合成输出、矿物掉落
6. 完成标准：dist/ 出 jar、run_test_gametest 全通过、validate_resources 无 ERROR
```

### 6.2 一条命令启动完整会话

```bat
python server_app\run_full_mod_task.py <会话ID> auto prompt.txt
```

- `<会话ID>`：自定义字符串（如 `my_first_mod`），同一 ID 重跑会**删除旧会话重来**
- `auto`：从 `.env` 读 Key；也可直接把 Key 写在这个参数位置
- `prompt.txt`：需求文件路径

启动器会自动：创建 `data/sessions/<会话ID>/mod` 工作区 → 复制 Forge 1.21.11 模板 → 挂载 MC 反编译源码和 agent 文档 → 后台启动 agent 循环，日志写入 `data/sessions/<会话ID>/run.log`。

> ⚠️ **用对 JAVA_HOME 的终端启动**。agent 子进程继承当前终端的全部环境变量，第 2.3 步的坑 4 在这里生效。

### 6.3 中断 / 重跑

```bat
:: 查 agent 进程 pid（run_full_mod_task 启动时会打印 started pid=xxx）
tasklist | findstr python

:: 终止整个会话进程树
taskkill /f /t /pid <pid>
```

**禁止** `taskkill /f /im python.exe`（会误杀机器上所有 Python 进程）。

---

## 7. 监控与验收

### 7.1 看 run.log

```bat
powershell -NoProfile -Command "Get-Content data\sessions\<会话ID>\run.log -Tail 50 -Encoding UTF8"
```

日志里的关键行：

| 标记 | 含义 |
|---|---|
| `[round] #N messages=… tokens≈…` | 每轮状态（轮次/上下文大小），看这个判断是否还在推进 |
| `[tool] …` / `[tool-result] success\|failed` | 每次工具调用与结果 |
| `[reply] …` | 模型回复（流式） |
| `[build] 构建成功 ✓` / `[build] Gradle 构建失败` | jar 构建 |
| `[gametest] …` | GameTest 运行 |
| `All required tests passed` | **测试全部通过（完成前提）** |
| `<write-first-stop>` / `<build-now-stop>` / `<gametest-check>` | 系统防跑偏提醒（正常现象，不必干预） |
| `[supervisor 思考]` | 监管 agent 的分析（只提建议，不改代码） |

### 7.2 一次完整任务的时间预期

| 阶段 | 耗时 | 说明 |
|---|---|---|
| 读技能 + 写代码 | 10-25 分钟 | 视 MOD 复杂度和模型速度 |
| **首次 Gradle 构建** | **10-30 分钟** | 要下载约 0.5-1 GB Forge/MC 依赖并缓存 |
| GameTest 运行 + 修复循环 | 10-40 分钟 | 每次改代码后重新构建+测试 |
| 收尾 | 2-5 分钟 | 自动出 jar + 源码 zip |

> 单次构建工具有 900 秒超时保护，首次构建若超过会被杀掉——**agent 会自动重试，Gradle 缓存让重试续传**，日志里出现一两次构建超时属正常现象，不用管。

### 7.3 验收标准（三者齐备才算成功）

```bat
:: 1) 产物 jar 存在
dir data\sessions\<会话ID>\mod\dist

:: 2) GameTest 通过标记
powershell -NoProfile -Command "Select-String -Path data\sessions\<会话ID>\run.log -Pattern 'All required tests passed' | Select-Object -Last 3"

:: 3) 资源校验无 ERROR（日志中 validate_resources 输出 RESULT: OK / PASS）
```

jar 直接复制到 `.minecraft/mods/` 即可进游戏（需 Forge 1.21.11-61.2.0）。会话目录下还有 `mod.zip`（源码包）可供下载留存。

### 7.4 任务结束信号

日志末尾出现最终中文总结（功能清单 + 文件结构），且之后 `[round]` 不再增长，即任务完成。若出现：

- `Max total rounds reached (150)` —— 触发总轮数保护，查看 run.log 分析卡点
- `GameTest 校验连续 N 次未通过判定，但 dist/xxx.jar 已生成，已强制收尾，请人工复核` —— 系统防无限循环的兜底，jar 可用但测试未闭环，需人工确认

---

## 8. 可选：启动网页版

不想用命令行的话，网页版提供会话管理、实时过程展示、一键下载：

```bat
:: 8000 网页版（MOD 制作器网站）
cd server_app
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

浏览器打开 `http://127.0.0.1:8000`。详见 [`server_app/README.md`](server_app/README.md)。

前端开发与验证见 [`server_app/frontend/README.md`](server_app/frontend/README.md)，架构与逐文件流程见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 和 [`Frontend.md`](Frontend.md)。

还有 [`tsinghua agent server/README.md`](tsinghua%20agent%20server/README.md)：把 agent 以 OpenAI 兼容 API（8001 端口）暴露给第三方平台接入。

---

## 9. 故障排查（实测踩坑）

| 症状 | 原因 | 解决 |
|---|---|---|
| `python` 弹出 Microsoft Store | Store 占位 stub，非真 Python | 见 2.1 坑 1：关闭应用执行别名，winget 重装后重开终端 |
| winget 说 Python 已安装但命令不存在 | 历史安装注册残留（常因自定义过安装路径） | `winget list --name Python` → `winget uninstall` → 重装到默认位置 |
| `ERROR: JAVA_HOME is set to an invalid directory: <路径>`（路径明明存在） | JAVA_HOME 值带尾随空格/引号 | cmd 用 `set "JAVA_HOME=..."` 带引号形式；或用系统属性面板设置；**改完必须重启 agent 会话** |
| winget 装 JDK 报 `InternetOpenUrl() failed 0x80072efd` | GitHub 直连不通 | 开代理重试 / Adoptium 官网手动下载 / 拷贝同版本 JDK 目录后指 JAVA_HOME |
| LLM 调用 401 / 认证失败 | Key 与端点不匹配 | Coding Plan 订阅 Key 配 `…/api/coding/paas/v4`；按量 Key 配 `…/paas/v4`，见 4.1 |
| 每轮挂 2-3 分钟后返回**空响应**，`run.log` 连续出现 `<empty-response>`，agent 反复重试 | reasoning 模型思考耗尽默认 8000 补全预算 | `.env` 设 `DSH_MAX_COMPLETION_TOKENS=32768` 后重启会话，见 4.2 |
| 日志频繁出现"上下文超限，自动压缩后重试" | `DSH_CONTEXT_WINDOW` 未设，压缩阈值虚高 | 设为实际窗口（GLM 建议 128000），见 4.2 |
| `Model returned empty responses 8 times in a row` | 上下文过大导致模型空响应 | 同上；系统会自动强制收尾，减少一次性加载的技能数 |
| 构建报 `SSLHandshakeException` / `PKIX path building failed` | 代理/加速器对本机流量做 TLS MITM（如 SteamTools、clash TUN 模式、公司网关），Java 不认其自签证书 | 关闭该软件的 TUN/MITM 后重试；或导出其根证书用 `keytool -importcert -alias <名字> -file <根证书> -keystore "%JAVA_HOME%\lib\security\cacerts" -storepass changeit` 导入 JDK 信任库（agent 遇到此问题时通常能自行完成） |
| 构建工具报 `cannot access local variable 'out'` | 首次构建超过 900 秒触发超时分支（旧版本工具 bug） | 已在最新代码修复；老版本请更新 `core/tools_mod.py`，或手动跑 `gradlew build`（Gradle 缓存让重试续传） |
| `taskkill /f /im python.exe` 后任务诡异退出 | 这条命令会杀掉 agent 自身 | 永远用 `taskkill /f /t /pid <pid>` 按进程树杀 |
| 控制台中文乱码 | Windows 终端默认 GBK | `chcp 65001` 或用 Windows Terminal（agent 落盘日志均为 UTF-8） |
| pip 安装很慢 | 默认源在国外 | 加 `-i https://pypi.tuna.tsinghua.edu.cn/simple` |

---

## 10. 目录结构速览

```
skill-agent/
├── core/                     # ★ Agent 核心引擎（主循环/工具/技能/团队协议/压缩）
│   ├── agent.py              #   Agent 主循环（上下文注入/出口闸/防死循环守卫）
│   ├── tools.py              #   工具 schema 与注册中心（实现拆分在 tools_*.py）
│   ├── skills/               #   200+ 技能文档（Forge 概念 + MC 数据包格式）
│   ├── protocol.py           #   团队协议（关机握手/计划审批状态机）
│   ├── compact.py            #   三层上下文压缩
│   └── ...
├── mc_java_sources_1.21.11/  # MC+Forge 反编译源码（agent 报错后查 API 用，只读）
├── mod_templates/            # Forge 工程模板（会话创建时复制）
├── docs/
│   ├── ARCHITECTURE.md       # 前端分区、依赖方向与现有 API 边界
│   ├── agent/                # 给 agent 读的运行期文档（ERROR_LIST/TOOL_GUIDE）
│   └── dev/                  # 给人看的开发/交接文档
├── server_app/               # 网页版（FastAPI，8000）
│   ├── frontend/             # React + 严格 TypeScript 前端
│   │   ├── site/             # 分区源码：index/user_auth/conversation/settings/session_history/generation/games
│   │   │   └── assets/       # 跨分区共享的基础设施和样式
│   │   ├── tests/            # 前端契约、状态机、结构门禁与隔离回归夹具
│   │   └── hooks/            # 前端推送前类型与架构检查
│   └── web/                  # Vite 生成的生产静态资源
├── tsinghua agent server/    # 外部平台接入服务（OpenAI 兼容 API，8001）
├── data/sessions/            # 运行时生成：每个会话一个目录（mod 工作区 + run.log + 产物）
├── Frontend.md               # 前端逐文件参数、分支、请求与界面状态
└── requirements.txt
```

---

## 求助

遇到 README 覆盖不了的问题：

1. 先看 `data/sessions/<会话ID>/run.log` 末尾 100 行——90% 的答案都在日志里
2. `agent.log`（项目根目录）记录了引擎级调试信息
3. `docs/agent/ERROR_LIST.md` 是构建/GameTest 已知错误清单，agent 遇错会自动先查这里，人工排查也可参考
