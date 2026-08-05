# server_app —— MOD Forge 应用源码全解

`server_app/` 是「MOD Forge」的完整应用目录：Python(FastAPI) 后端 + React/Next.js 前端一体化。
前端构建成静态文件后由后端直接托管，`python server.py` 一行即可运行整站。

---

## 目录结构总览

```
server_app/
├── server.py          # ★ FastAPI 主服务：全部 HTTP 接口 + 会话子进程管理
├── auth_store.py      # 认证与历史：用户/密码哈希/登录 token/历史记录（纯文件存储）
├── run_task.py        # 每个 MOD 生成任务的独立子进程入口
├── log_events.py      # 日志解析：结构化事件流 / 文件树 / 文件预览
├── assets/            # 前端用到的 MC 图标素材（构建时复制到 web/assets）
├── frontend/          # Next.js 14 前端源码（构建 → web/）
└── web/               # ★ 构建产物（由 server.py 静态托管，勿手改）
```

---

## 1. 后端（Python）

### 1.1 server.py —— 主服务（FastAPI）

**路径常量 / 初始化**
- `PROJECT_ROOT`、`RUN_TASK`、`SESSIONS_DIR`、`TEMPLATES_DIR`、`WEB_DIR`
- 启动时自动创建 `data/sessions/` 与 `mod_templates/`

**Session 类**（每个生成会话）
- 字段：`id` / `mod_dir` / `api_key` / `owner` / `game` / `loader` / `version`
         / `proc`(子进程) / `started_at` / `finished_at` / `result` / `log_path` / `event_cursor`
- `game/loader/version` 用于重置时重建对应模板骨架

**会话生命周期接口**

| 路由 | 功能 |
|---|---|
| `POST /api/session` | 创建会话：按 `mod_templates/<game>/<loader>-<version>/` 复制骨架（子目录不存在回退根目录）、绑定 owner、持久化配置 |
| `DELETE /api/session` | 删除会话：**先 kill 生成子进程**（无论是否运行中，不再 400），再删目录与记录 + 清理过期 token |
| `POST /api/session/reset` | **重置会话（重新生成用）**：kill 进程 → 清运行态 → 删 mod/ 与 run.log → 重建初始骨架；**保留 session_id/api_key/owner** |
| `POST /api/task` | 启动生成：`subprocess.Popen` 跑 `run_task.py`，注入用户 API Key（不落盘） |
| `GET /api/session` | 会话状态（含 elapsed 锁定：进程结束即冻结 finished_at） |
| `GET /api/status` | 状态 + 日志尾部（含 finished 时写 result） |
| `GET /api/result` | 最终结果文本 |

**产物访问（owner 校验）**

| 路由 | 功能 |
|---|---|
| `GET /api/download` | 打包 mod/ 为 mod.zip 下载（前端用 fetch 流式 + token 头） |
| `GET /api/files` | 文件树 / 单文件内容预览 |
| `GET /api/events` | 增量事件流（思考/工具/回合/系统），基于 log_events |
| `GET /api/log` | 原始 run.log 增量拉取 |

**认证与历史**

- `POST /api/register`（注册即发 token）、`POST /api/login`、`POST /api/logout`、`GET /api/me`
- `GET/PUT/DELETE /api/history`（每用户历史，文件隔离）
- `GET /api/games`（动态枚举 mod_templates 下游戏）

**静态托管 / 启动**
- `@app.get("/")` 显式返回 index.html；`app.mount("/", StaticFiles(web))`
- `if __name__ == "__main__": _restore_sessions()` 恢复历史会话 + `uvicorn.run(host=0.0.0.0, port=8000)`

### 1.2 auth_store.py —— 认证与历史存储（无数据库）

- `_load_json` / `_save_json`：JSON 文件读写（自动创建父目录）
- 密码：PBKDF2-SHA256 加盐哈希（`_hash_password`，10 万迭代），绝不落明文
- `register` / `check_credentials`：用户注册/校验（`data/users.json`）
- `create_token` / `validate_token` / `revoke_token` / `prune_expired`：登录 token（`data/auth_sessions.json`，7 天过期，过期自动清理）
- 历史：`load_history` / `upsert_history`（按 sessionId 去重：已存在仅更新耗时/文件数/时间，保留首次 prompt）/ `clear_history`（`data/history/{user}.json`）

### 1.3 run_task.py —— 子进程入口

- 用法：`python run_task.py <session_dir> <api_key> <prompt>`
- 强制 stdout 行缓冲 + write_through（print 实时落盘，前端实时可见）
- 切 cwd → 注入 `DEEPSEEK_API_KEY` → 延迟导入 `core.agent.agent_loop` → 跑完整生成

### 1.4 log_events.py —— 日志 → 结构化事件

- `_parse_run_block`：解析 run.log 的 `[思考] / [工具] / [todo] / [teammate/subagent]` 为事件
- `_parse_agent_block`：从 agent.log 提取「工具调用 / 新一轮 / 队友动作 / 协议」等事件
- `build_event_stream`：增量读取双日志（游标 offset 机制）
- `build_file_tree`：递归产物文件树（跳过 .worktrees/.team/.tasks/.transcripts 等运行时目录）
- `read_file_preview`：单文件内容预览（100KB 上限，路径防越界）

### 1.5 assets/ —— MC 图标素材

| 文件 | 用途 |
|---|---|
| `mc_icon.png` | 配置页 Minecraft 游戏卡图标 |
| `mc_diamondsword_icon.png` | 需求页「武器」快速填充图标 |
| `mc_bread_icon.png` | 需求页「食物」快速填充图标 |
| `mc_grassblock_icon.png` | 需求页「方块」快速填充图标 |

---

## 2. 前端（frontend/，Next.js 14 静态导出）

```
frontend/
├── app/              # 路由层
├── components/
│   ├── common_ui/    # 通用 UI（与游戏无关）
│   └── mc_ui/        # Minecraft 专属 UI
├── lib/              # 业务逻辑（非 UI）
├── scripts/          # 构建导出脚本
└── 配置文件           # package.json / next.config.mjs / tailwind.config.js / tsconfig 等
```

### 2.1 app/page.tsx —— 全站状态机（核心）

三步工作流：`step 1 配置 → 2 填需求 → 3 生成`

- 状态：`view`(制作台/历史) `step` `game` `sessionId` `user` `authOpen/authMode` `savedPrompt` `savedApiKey/savedLoader/savedVersion`
- 关键回调：
  - `handleCreated`：创建会话 + **保存配置(savedApiKey/Loader/Version)** + 启动 10 分钟超时清理
  - `handleRun`：启动生成 + 开始轮询
  - `handleResume`：复用历史会话（hydrate）
  - `handleRegenerate`：`resetSession` 重置本次会话（kill 进程 + 恢复骨架） + 回需求页
  - `deleteSessionAndReset`：**从需求页返回时彻底删除会话**（kill + 删目录）并回配置页
- 历史写入：`polling.finished === true` 才 `saveHistory`（未完整生成不会误记）

### 2.2 lib/ —— 非 UI 业务逻辑

| 文件 | 职责 |
|---|---|
| `types.ts` | 全站 TS 类型（Game / SessionStats / AgentEvent / TreeNode / HistoryEntry / FilePreview…） |
| `api.ts` | 后端 fetch 封装（自动带 token、错误 detail 解析、createSession(含 loader/version) / resetSession / deleteSession / downloadSession…） |
| `auth.ts` | token 存取（localStorage key=modforge_token）+ 登录/注册/登出/免登检查 |
| `history.ts` | 服务端历史读写封装（load/save/clear） |
| `useSessionPolling.ts` | 800ms 轮询 Hook：事件按 id 去重、状态同步、完成回调、hydrate（复用会话一次灌入全量事件） |

### 2.3 components/common_ui/ —— 11 个通用组件（无 MC 硬编码）

| 组件 | 职责 |
|---|---|
| `Navbar.tsx` | 顶栏：制作台/历史 tab（竖线分隔、去图标）+ 登录注册按钮 / 用户下拉入口 |
| `UserNavDropdown.tsx` | 用户下拉菜单（头像/用户名/设置/退出登录，hover 弹出） |
| `AuthModal.tsx` | 登录/注册弹窗（眼睛切换密码、注册二次确认、可关闭） |
| `Toast.tsx` | 全局通知（黑曜石毛玻璃 + error(rose)/warn/success 变体） |
| `Hero.tsx` | 大标题（MOD 青绿渐变高亮 + 精简副标题） |
| `Stepper.tsx` | 顶部三步进度指示 |
| `HistoryView.tsx` | 历史记录列表（服务端数据 + fetch 流式下载 + 复用） |
| `GenerateStep.tsx` | 生成面板（状态/计时/下载/重新生成按钮 + 智能体终端 + 产物浏览器） |
| `EventTimeline.tsx` | 事件流渲染（类型分色、错误关键词暗红高亮） |
| `ArtifactExplorer.tsx` | 产物文件树（紧凑 VS Code 风格 + 横向滚动 + 缩进辅助线）+ highlight.js 代码预览 |
| `MouseEffect.tsx` | 鼠标点击粒子 + 动态光标（GAME_THEMES 字典按游戏驱动，非 MC 零开销） |

### 2.4 components/mc_ui/ —— 3 个 Minecraft 专属组件

| 组件 | 职责 |
|---|---|
| `ConfigureStep.tsx` | 配置页：DeepSeek API Key（错误 shake + 红框）+ 目标游戏（点卡片展开 Inline Drawer）+ Mod Loader(Forge 可选/NeoForge/Fabric 锁 WIP) + 游戏版本（老版本非阻塞兼容警告）+ 双条件点亮 + 错误 Toast；**savedApiKey/savedLoader/savedVersion 回显**（返回配置页不重输） |
| `PromptStep.tsx` | 需求页：受控 textarea（value/onChange 来自父级，返回保留内容）+ 快速开始（钻石剑/面包/草方块图片）+ 会话 ID 复制 + 开始生成（竖线夹槽） |
| `VoxelBackground.tsx` | MC 主题背景（像素网格/直角地形/Creeper 荧光脸/Enderman 紫眼/Pig 线框 + XP 粒子上浮 + 径向压暗） |

### 2.5 scripts/export.mjs —— 构建部署

任务链路：清空 `web/` 旧产物（index.html/_next/css/js）→ 将 `next build` 的 `out/` 拷贝到 `web/` → 复制 `assets/` 到 `web/assets/`

### 2.6 关键配置

- `package.json`：`build` = `next build`；Next.js 14.2
- `next.config.mjs`：`output: "export"` 静态导出 + images.unoptimized + reactStrictMode
- `tailwind.config.js`：主题色（ink 深灰 / forge 青绿）、字体、动画（breathe/shine/pulseSoft/fadeUp/skeleton）、自定义阴影
- `tsconfig.json`：strict + `@/*` 别名 + next 插件
- `postcss.config.js`：Tailwind
- `global.d.ts` / `next-env.d.ts`：类型声明（CSS 模块 / Next 全局）

---

## 3. web/ —— 构建产物（只读）

| 内容 | 说明 |
|---|---|
| `index.html` | 首页（Next 静态导出，含 RSC payload 单行压缩） |
| `404.html` | 404 兜底页 |
| `_next/` | JS/CSS chunk（带内容哈希） |
| `assets/` | 前端图片素材（export.mjs 从 server_app/assets 复制） |

> 每次 `npm run build && node scripts/export.mjs` 全量重新生成；已被 `.gitignore` 忽略，不手动改。

---

## 4. 数据落点（项目根 data/，git 忽略）

```
data/
├── users.json          用户（加盐 PBKDF2 哈希，密码不落明文）
├── auth_sessions.json  登录 token（7 天过期，随删除会话清理）
├── history/{user}.json 每用户历史（sessionId 去重）
└── sessions/{id}/      每会话：mod/（产物）+ owner.txt + run.log
```

---

## 5. 关键流程速览

```
浏览器 登录(AuthModal) → ConfigureStep 配置(api_key/game/loader/version)
  → POST /api/session → 复制 mod_templates/<game>/<loader>-<version>/
  → PromptStep 填需求 → POST /api/task → 起 run_task.py 子进程（注入用户 Key）
  → 前端 800ms 轮询 /api/events 实时显示思考/工具/产物
  → 完整生成后 saveHistory + 可下载 mod.zip（带 token fetch）
  → 重新生成：resetSession（kill 进程 + 重置 mod 骨架，保留 session_id/Key）
  → 从需求页返回配置页：deleteSession（kill + 删会话目录），已填配置回显
  → 未开始任务 10 分钟自动清理（deleteSession）
```

---

## 6. 启动方式

```bash
# 安装依赖
pip install -r requirements.txt
cd server_app/frontend && npm install

# 构建前端（改动前端源码后执行）
cd server_app/frontend && npm run build && node scripts/export.mjs

# 启动服务（后端主入口；前端静态产物已由 server.py 托管）
python server_app/server.py
# → 浏览器访问 http://localhost:8000