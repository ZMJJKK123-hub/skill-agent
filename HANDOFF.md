# HANDOFF — skill-agent 项目交接文档

> 用途：把本项目背景、已完成工作、以及当前进行中的任务（识图模式 = 截屏 + 图片识别工具）完整交接给新的任务会话。
> 创建时间：2026-08-16
> 读者：接手的 agent / 开发者本人

---

## 1. 项目概况

- **项目路径**：`C:\Users\59639\Desktop\skill-agent`
- **定位**：Minecraft Forge MOD 开发 agent —— 用户通过网页对话，让 agent 生成/迭代 Forge MOD（写代码、跑 GameTest、构建 jar、打包 zip）
- **技术栈**：
  - 后端：`server_app/server.py`（FastAPI，httptools 运行）+ `server_app/run_task.py`（会话子进程入口）
  - 核心：`core/` 纯 Python（agent 循环、工具、任务管理、队友/协议、技能加载）
  - 前端：`server_app/frontend/`（**Vite + React 18 + TypeScript + Tailwind 源码，近期已确认存在**），构建产物输出到 `server_app/web/`（由 server.py 托管）
  - Python 环境：`.\venv\Scripts\python.exe`（OpenAI 协议，默认 base_url `https://api.deepseek.com/v1`）
- **git 远程**：`https://github.com/ZMJJKK123-hub/skill-agent`（origin/main，已推送全部历史）

### 关键环境变量（server.py 注入 run_task 子进程）
| 变量 | 含义 |
|---|---|
| `DSH_MODE` | `chat`（通用对话，默认）/ `mod`（MOD 制作） |
| `DSH_SESSION_ROOT` | 会话根目录（`.chat/` 对话历史所在处） |
| `DSH_SANDBOX_MODE` | `full-access` / `workspace-write` / `read-only` |
| `DSH_MODEL` / `DSH_BASE_URL` | 模型名 / API 地址（前端可切换 flash/pro/自定义 provider） |
| `DSH_RESUME` | `1` = 从断点 `.chat/working.jsonl` 恢复 |
| `DSH_PROMPT_FILE` | 提示词临时文件（绕开 Windows argv GBK 损坏中文） |
| `DSH_DAEMON_IDLE_TIMEOUT` | daemon 空闲退出秒数（默认 600） |

---

## 2. 架构要点

### 每会话一个子进程（隔离）
- `POST /api/task` → server 启动 `python run_task.py <session_dir> <api_key>` 子进程，cwd 切到会话工作目录
- **chat / mod 模式均 daemon 常驻**：首轮跑完不退出，0.5s 轮询 `.chat/pending.jsonl`，新消息即消费（第二轮起零冷启动）
- mod 模式工作目录 = `<session>/mod/`（server 已复制模板 + `mc_java_sources/` 完整 MC+Forge 源码）；chat 模式 = 会话根目录

### daemon 状态文件（server 识别"空闲/工作中"）
- `.chat/daemon.state`：`waiting`（空闲=上一轮完成）/ `working`（跑轮中）
- `.chat/daemon.pid`：pid 文件，server 重启时 `_kill_stale_daemon` 清理遗留进程
- server 的 `_session_stats`：daemon 空闲且 pending=0 → `finished=True`（前端显示"完成"）；**daemon 空闲但 pending>0 → `running=True`**（防前端误提取上一轮 log_tail 为回复——已修的历史 bug）

### 状态持久化（长对话语义）
- daemon 常驻期间：task_manager / todo / teammate_manager / coordinator / bg_manager **跨轮保留，不再清空**
- `.tasks/` 任务文件落盘，进程重启后自动恢复；队友名册/todo/协议为内存态，随进程退出消失（用户已确认可接受）
- 收件箱 `read_inbox` 读完即清；队友线程 60s IDLE 自动 shutdown

### 前端（server_app/frontend/）
- 静态插件式：`src/composition.ts` 装配插件 → `shell/AppShell.tsx` + `shell/registry.tsx`（Slot 注入）
- 插件：`src/plugins/{auth,conversation,generate,settings,sidebar,workspace}.tsx`
- 设置面板 `src/plugins/settings.tsx`：通用（game/loader/version/apiKey/sandbox）/ 模型（官方+自定义 provider）/ 插件开关 / Agent / 语言 / 外观
- 全局状态 `src/lib/store.ts`（localStorage 持久化 `modforge_ui`）；API 封装 `src/lib/api.ts`
- 构建：`cd server_app/frontend && npm run build` → 产物 `server_app/web/`（server.py 托管，需重启 server 生效）
- **重建后必须刷新页面验证**（无 HMR 热更；`pnpm run dev:web` 仅用于 DSH 本体的 web，与本项目无关）

---

## 3. 已完成的工作（按 git 历史）

| commit | 内容 |
|---|---|
| `3637178e` | 169 个技能文件清理/英文化/标准化（MC 官方术语，ID/代码/JSON 逐字保留，巨型枚举压缩指向 `mc_java_sources/`） |
| `4ddda522` | **YAML 修复**：frontmatter `description/whenToUse` 含"冒号+空格"导致 `yaml.safe_load` 崩溃 → 全部加双引号 + 3 文件去 BOM（曾导致对话完全不回复） |
| `8a28e7f6` | **性能优化 opt2/3**：agent 流式输出（`[reply]` 增量写 run.log）+ SkillLoader 扫描只读文件头部 8KB（169 技能 0.96s→0.315s） |
| `7dbc7e48` | **性能优化 opt1**：chat 模式 daemon 常驻化（第二轮起零冷启动），server 侧 daemon 状态识别 + 重启清理遗留进程 |
| `7fa393fb` | **bug 修复**：daemon 空闲但 pending>0 时不得返回 finished（防前端秒回旧回复后停住） |
| `db04f358` | **bug 修复**：run.log 首行 GBK 乱码（reconfigure 补 encoding="utf-8"）+ daemon 被 Ctrl+C 时优雅退出 |
| `f58d2112` | **长对话状态跨轮持久化**：删除 `_reset_round_state`（每轮清空 task/todo/teammate/coordinator 的逻辑）+ 删除 agent.py mod 收尾清空 + **mod 模式也 daemon 常驻** + mod 首轮带历史 |

### 已修的经典 bug（教训）
1. **frontmatter YAML 崩溃**：`description: 值含"冒号+空格"` → `yaml.safe_load` 抛 `mapping values are not allowed here` → SkillLoader 初始化异常 → 全部对话不可用。修复：全 169 文件 description/whenToUse 加双引号。
2. **前端秒回旧回复**：daemon 空闲返回 finished + log_tail 仍是上一轮 → 前端 sr() 轮询把旧回复提取为气泡 → 用户发新消息"秒回旧回复后停住"。修复：`_session_stats` 中 waiting+pending>0 视为 running。
3. **run.log 首行乱码**：run_task 第一行 print 时 stdout 还是 GBK（core/config.py 导入后才切 UTF-8）→ reconfigure 补 encoding。
4. **冷启动 11 秒**：openai SDK import 5.97s + 技能全量扫描 0.96s，每消息一个子进程 → daemon 化后第二轮 3-4s。

---

## 4. 当前进行中的任务（未完成！）：识图模式 = 截屏 + 图片识别工具

### 4.1 需求（用户原话转述）
> "给目前的 agent 接一个识别图片的工具，再给他一个能截屏的工具，让他能够自主循环去判断它的数据包什么的有没有写好。"
> "如果识别图片需要 API 的话，就在网页端开一个新的插件选项，让用户选择开不开启**识图模式**（用户说'师徒模式'，已确认=识图模式）。开启后需要接入**第二个 API**（视觉 API）。"

### 4.2 已确认的决策
- ✅ 开关名：**识图模式**（vision mode）
- ✅ 视觉 API 形态：**通用 OpenAI 兼容**（base_url + api_key + model 三项，与现有自定义 provider 一致；例如 GPT-4o / Qwen-VL / GLM-4V 等）
- ✅ DeepSeek 官方 API **不支持/不可靠**图片输入（见 CherryHQ issue #1110），必须走第二个 API
- ⚠️ **用户要求先不实施**：把任务总结成 plan + 过往对话总结到根目录 md（即本文档），用于交接给新会话

### 4.3 已完成的侦察（接手者可继续）
1. **前端源码存在**：`server_app/frontend/src/`（Vite+React+TS+Tailwind），设置面板 `src/plugins/settings.tsx`（`SectionKey` 含 general/models/plugins/agent/language/appearance），全局状态 `src/lib/store.ts`（`UiState` + `persist()` localStorage），API 封装 `src/lib/api.ts`（`createSession` / `startTask`）
2. **server 注入链路**：`server.py` `Session` 类（api_key/model/base_url/sandbox 字段）→ `start_task` 环境变量注入 run_task 子进程 → run_task `main()` 读取。视觉配置可仿照：Session 加字段 + env `DSH_VISION_*` 注入
3. **agent 工具注册表**：`core/tools.py` —— `TOOL_HANDLERS`（dict，name→handler lambda）+ `TOOLS`（OpenAI function schema 列表）+ `_TOOL_META`（readonly/concurrency_safe 元数据）+ 底部循环注册进 `tool_registry`（toolkit.py 的 ToolDef）
4. **截图库**：已 `pip install Pillow==12.3.0`（venv 内）。Pillow 提供 `ImageGrab.grab()` 截屏 + 图像缩放/JPEG 编码 + base64。**mss/pyautogui/cv2/numpy 均未安装**（不需要额外装）
5. **视觉调用**：`core/config.py` 有 `client = OpenAI(...)` 单例（预置 http_client verify=False/trust_env=False/timeout 600）。**注意**：视觉 API 需要独立的 OpenAI 客户端（不同的 base_url/api_key），应新建第二个 client 或工具内临时构造，不要复用主 client
6. **run_client 工具**：`core/gradletools.py` `run_client`（gradle runClient，timeout 90s，阻塞式）——agent 自主循环截图验证的配合方式需要设计（如 run_in_background 启动游戏 → 等待 → 截图 → 识别 → 判断 → 关闭）

### 4.4 建议实施计划（plan）
1. **core/tools.py 新增两个工具**：
   - `screenshot`：Pillow `ImageGrab.grab()` 截全屏 → 保存到工作区（如 `.screenshots/shot_<ts>.png`）→ 返回路径。参数可选 `region`/`window_title`（先做全屏，window 定位可后续增强）
   - `analyze_image`（或 `vision_analyze`）：入参图片路径 + 可选的提示词（如"描述画面中物品栏/方块显示是否正常"）→ 读图 → 缩放/压缩 → base64 → 调**视觉 API**（`DSH_VISION_BASE_URL/KEY/MODEL`）→ 返回模型文本
   - 注册进 `TOOL_HANDLERS` + `TOOLS` schema + `_TOOL_META`（截图 readonly、视觉分析 readonly）
   - **开关控制**：识图模式关闭时，两个工具不注册（或 analyze 返回"识图模式未开启"）——建议按 `DSH_VISION_ENABLED` 环境变量决定是否注册
2. **server.py**：
   - `Session` 增加字段：`vision_enabled`、`vision_api_key`、`vision_base_url`、`vision_model`
   - `SessionRequest`/`createSession` 接收视觉配置；`start_task` 注入 env：`DSH_VISION_ENABLED`、`DSH_VISION_API_KEY`、`DSH_VISION_BASE_URL`、`DSH_VISION_MODEL`
   - （可选）新增 `/api/session/vision` 更新接口，或复用 startTask 传入
3. **前端**：
   - `store.ts`：`UiState` 增加 `visionEnabled`、`visionApiKey`、`visionBaseUrl`、`visionModel`，`persist()` 落 localStorage
   - `settings.tsx`：新增设置区块（可放 models 区或新 SectionKey `vision`）：开关 + 三项配置
   - `api.ts`：`createSession`/`startTask` 参数带上视觉配置
4. **验证**：mock 测试（截图在无显示环境可能失败——本机是 Windows 桌面，`ImageGrab.grab()` 可直接用）+ 视觉 API 连通性测试 + 前端 build + 重启 server 后手工验收

### 4.5 待注意
- 截图在 agent 子进程运行（无交互桌面会话？本机是用户自己的 Windows 桌面，可正常截屏；若未来跑在服务端无桌面则需改用游戏内截图或 offscreen）
- 图片要压缩（缩放+JPEG）再 base64，避免 token/带宽爆炸；OpenAI 视觉格式：`{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,..."}}`
- 视觉模型推理可能与主模型不同厂商，提示词里应说明"这是游戏截图，请判断 XX 是否正常"
- **绝对约束**：不派发子代理/不用 workflow（用户电脑会卡死）；所有实现由主 agent 直接做
- DSH 文件策略 danger-full-access；approval prompts 禁用（勿设 sandbox_permissions）
- 测试脚本运行用 `PYTHONDONTWRITEBYTECODE=1`，测试后删除残留（agent.log、__pycache__）

---

## 5. 会话/数据布局速查

```
data/sessions/<session_id>/
├── run.log                  # agent 过程日志（[reply]/[tool]/[思考] 增量）
├── agent.log                # logging 模块输出（core/config.py 写入 cwd）
├── owner.txt                # 归属用户
├── mod/                     # MOD 工作区（模板 + mc_java_sources/ + 产物）
├── .chat/
│   ├── conversation.jsonl   # 对话历史（user/assistant）
│   ├── pending.jsonl        # 运行中插话队列（enqueue_pending 同步写历史）
│   ├── working.jsonl        # 断点（pause/resume）
│   ├── daemon.state         # daemon 空闲/工作标记
│   └── daemon.pid           # daemon pid（重启清理用）
├── .tasks/                  # 任务文件（task_N.json，磁盘持久化）
└── .team/                   # 队友名册（config.json + inbox/）
```

前端构建：`cd server_app/frontend && npm run build`（tsc --noEmit && vite build）→ `server_app/web/`。**改了 server.py 必须重启 server；改了 core/* 由 run_task 子进程自动读新代码（但重启 server 会清理旧 daemon，建议重启）**。

---

## 6. 常用命令

```powershell
# 语法检查
.\venv\Scripts\python.exe -m py_compile core\agent.py core\tools.py server_app\server.py server_app\run_task.py
# 前端构建
cd server_app/frontend; npm run build
# git 提交推送
git add -A; git commit -m "..."; git push origin main
# 查看 daemon 状态（会话目录内）
Get-Content .chat\daemon.state
```
