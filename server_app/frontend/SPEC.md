# MOD Forge 新前端 — 规格说明（SPEC）

> 按 dsh 源码形状重写。技术底座：**Vite + React 18 + TypeScript + Tailwind**。
> 后端 **FastAPI + Python agent 原样保留**，新前端构建产物仍由 `server.py` 托管（`server_app/web/`）。
> 旧 Next.js 前端已备份到 `server_app/frontend-nextjs.bak/`。

---

## 1. 架构（仿 dsh 形状，静态插件化）

```
src/
├── main.tsx            # 壳启动：按 composition 装配插件 → 挂载 AppShell
├── composition.ts      # 组合配置（等价 cordis.yml）：声明启用哪些插件及顺序
├── shell/
│   ├── registry.tsx    # 迷你槽位系统（SlotRegistry + SLOTS 常量 + SlotView）
│   └── AppShell.tsx    # 三栏可伸缩壳（侧栏 256↔56 / 对话 / 详情）+ 全局浮层
├── plugins/            # 功能插件（每个插件一个 apply(ctx)，向槽位注册 UI）
│   ├── sidebar.tsx     # logo/工作区/会话/设置入口
│   ├── conversation.tsx# 对话空态 + 输入框（快速填充/模型选择/附件/发送）
│   ├── auth.tsx        # 右上角登录/注册
│   ├── settings.tsx    # 设置面板（通用/模型/插件/Agent预设/语言/外观）
│   ├── workspace.tsx   # 导入已有 mod 文件夹
│   └── generate.tsx    # 生成监控 + jar 下载（详情面板）
└── lib/
    └── store.ts        # 轻量全局 UI 状态（登录用户/设置开关/工作区）
```

**插件模型**：每个插件导出 `{ id, name, apply(ctx) }`；`ctx.slots.inject(槽位, id, render, order)` 注册 UI；壳层用 `<SlotView name=.../>` 渲染槽位。等价 dsh 的 client 插件 + Slot 注入，但为**静态装配**（启动时一次 apply，运行时不可动态增删）。

---

## 2. 槽位清单

| 槽位 | 谁注册 | 位置 |
|---|---|---|
| `sidebar.logo` | sidebar | 左侧栏顶 logo（占位） |
| `sidebar.workspaces` | sidebar | 工作区列表（每会话一文件夹） |
| `sidebar.sessions` | sidebar | 历史会话列表 |
| `sidebar.footer` | sidebar / workspace | 底部：设置 + 导入文件夹 |
| `header.actions` | auth | 顶栏右上：登录/注册 |
| `conversation.messages` | conversation | 对话消息流 |
| `conversation.composer` | conversation | 底部输入框 |
| `details` | generate | 右侧详情：生成状态 + jar 下载 |
| `shell.overlay` | settings | 全局浮层：设置面板 |

---

## 3. 后端对接（复用现有接口 + 新增 2 个）

| 用途 | 接口 |
|---|---|
| 登录/注册 | `POST /api/register` `POST /api/login`（已有） |
| 建会话（建工作区文件夹+复制模板） | `POST /api/session`（已有） |
| 启动生成 | `POST /api/task`（已有） |
| 状态/日志/事件流 | `GET /api/status` `/api/log` `/api/events`（已有） |
| 历史会话 | `GET /api/history`（已有） |
| **导入已有 mod 文件夹** | `POST /api/import`（**已新增**：请求体=zip 原始字节，api_key 走 `X-API-Key` 头，game/loader/version 走 query，零新增依赖） |
| **jar 直接下载** | `GET /api/download/jar`（**后端已有**，无需改动） |

> 核心 `core/agent.py` / `run_task.py` 完全不动；只新增了 `POST /api/import` 一个薄接口。

---

## 4. 需要你填的清单（TODO 汇总）

骨架已跑通，以下是我留空、需要后续填入/决策的地方：

**必须填（否则功能缺失）**
1. **Logo / 图标**（`sidebar.tsx` 顶部"M"占位块）：换成正式 logo 图片或 SVG。
2. **快速填充图标**（`conversation.tsx`）：`⚔️🍞🧱` 占位 → 换成原 `server_app/assets/` 的 `mc_diamondsword_icon.png` / `mc_bread_icon.png` / `mc_grassblock_icon.png`（需复制进 `src/assets` 或 public）。
3. **API 对接**：所有 `TODO: 对接 /api/...` 处 —— 登录/注册、建会话、启动生成、状态/事件流轮询、历史、下载。

**需要决策**
4. **导入文件夹**：确认用 File System Access API（Chrome/Edge + HTTPS）+ zip 上传 + `POST /api/import`？还是只做"输入服务器路径"（但你要部署到服务器，前者更合理）。
5. **模型提供方**：纯 UI 模拟（当前）还是真要支持多 provider？—— 你之前说"照着模拟"，我按纯 UI 做了。
6. **语言**：是否真要中英切换（要接 i18n），还是先只做界面样式？—— 当前是界面占位。

**可后续迭代**
7. 会话消息流（`conversation.messages` 目前是空态，需接事件流渲染工具卡片/思考/结果）。
8. 右侧详情面板默认关闭，生成进行中自动展开（交互细节）。
9. 主题深浅色切换（`appearance` 目前是占位，需接 `dark` class 切换）。

---

## 5. 本地开发 / 构建

```bash
cd server_app/frontend
npm install
npm run dev        # 开发：http://localhost:5173，/api 代理到 :8000
npm run build      # 构建：产物输出到 ../web（server.py 托管）
```
