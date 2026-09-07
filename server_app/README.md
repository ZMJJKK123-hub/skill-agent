# server_app —— MOD 制作器网站（FastAPI + Vite 前端）

> 本 README 对应 dev 分支重构后结构；整体架构见 `docs/ARCHITECTURE.md`。

## 目录结构

```
server_app/
├── server.py            薄入口（~45 行）：create_app() + uvicorn
├── run_task.py          会话子进程入口（装配新引擎 + daemon 常驻）
├── api/                 表现层：路由 + DTO + 认证/归属校验
│   ├── sessions.py      会话生命周期（创建/mod准备/删除/重置/状态/图片）
│   ├── tasks.py         任务（启动/排队/暂停/状态/结果/问答）
│   ├── artifacts.py     产物（zip/jar 下载/文件树/事件流/日志/模板列表）
│   └── history.py       历史 + 会话列表 + 对话历史（登录接口冻结保留）
├── services/            业务层
│   ├── session_manager.py   Session 实体 + 会话表 + 磁盘恢复 + 孤儿清理
│   ├── task_dispatcher.py   模式三层推断（唯一实现）+ 排队/恢复/重拉 + 子进程 env
│   ├── templates.py         模板复制 + mc_java_sources/docs junction + git init
│   ├── stats.py             daemon 状态机 + 产物统计 + 日志尾部 + 会话标题
│   ├── packaging.py         源码 zip（mtime 缓存 + 原子替换）+ jar 定位
│   ├── uploads.py           图片上传落盘（data URL → .chat/uploads）
│   ├── round_runner.py      单轮生命周期（跑引擎→清断点→落历史→沉淀）
│   ├── daemon_runner.py     常驻循环 + daemon 状态文件契约（写侧）
│   └── finalizers.py        KNOWN_ISSUES 聚类 + ERROR_LIST 自动沉淀
├── infrastructure/       基础层
│   ├── session_disk.py       key/owner/mode/config.json 读写（v2：重启不丢配置）
│   ├── process_governor.py   遗留 daemon/游戏进程/Gradle JVM 清理 + 目录重试删除
│   └── daemon_protocol.py    daemon.state/pid/pending 读侧契约（与 run_task 配对）
├── frontend/            前端源码（Vite + React18 + TS + Tailwind）
├── web/                 前端构建产物（git 跟踪；`npm run build` 输出到此）
└── debug/               维护页 + 游乐场（自包含静态，不参与重构）
```

## 运行

```bat
启动.bat                      :: 或：pip install -r requirements.txt && cd server_app && python server.py
```

浏览器打开 http://127.0.0.1:8000 ；设置里填模型提供方（Base URL/模型名/API Key），
聊天框输入 `/mod 你的想法` 开始生成。

## 数据落点（仓库根 data/）

| 路径 | 内容 |
|---|---|
| `data/sessions/<id>/` | 会话工作区（mod/、run.log、mod.zip、owner.txt、mode.txt、config.json） |
| `data/sessions/<id>/.chat/` | 对话历史/断点/插话队列/daemon 状态/上传图片/API Key |
| `data/users.json` 等 | 历史记录存储（登录部分已冻结，本地单用户） |

## 关键流程

1. **创建**：`POST /api/session` 轻量建目录 + 落 owner/api_key/config.json。
2. **准备**：用户输入 `/mod` 确认 → `POST /api/session/mod` 复制模板 + junction + git init（幂等）。
3. **生成**：`POST /api/task` →（运行中则排队 pending.jsonl）→ spawn run_task 子进程
   （cwd=mod/，全量 DSH_* env 注入）→ 新引擎跑轮 → daemon 常驻待下一条。
4. **过程**：前端轮询 `GET /api/events`（run.log 协议行 → 事件流增量）。
5. **下载**：`GET /api/download/jar`（dist 首个 jar）/ `GET /api/download`（源码 zip）。
6. **暂停/继续**：pause kill 子进程（断点 working.jsonl 保留）→ resume 从断点续跑。
7. **模式切换**：`/chat` `/mod` 前缀或 mode.txt 记忆；daemon 检测到切换自杀，前端自动续跑重拉。

## 前端构建

```bat
cd server_app\frontend
npm install
npm run build        :: tsc --noEmit && vite build → 产物输出 ../web/
```

改后端需重启 server；改 core/* 由 run_task 子进程下次启动自动生效。
