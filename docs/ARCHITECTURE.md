# 架构文档（dev 重构版）

> 本文对应 dev 分支重构后的结构（main 仍为重构前稳定版）。
> 分层依据：`agent.md`（Rule 1 文档注释 / Rule 2 三层架构与质量红线）。

## 总览

一句话：用户在网页输入「做一个红宝石剑」，AI 写 Java 代码、画资源、
编译、跑 GameTest，交付能直接放进 `.minecraft/mods/` 的 Forge MOD。

```
浏览器（Vite+React 前端，server_app/web/ 静态产物）
   │ HTTP (/api/*)
   ▼
server_app/  ── FastAPI（三层）
   │  spawn 每会话一个子进程
   ▼
run_task.py ── 子进程入口（cwd=会话工作区）
   │  core.bootstrap 组装引擎
   ▼
core/  ── Agent 引擎（domain / interfaces / services / infrastructure）
   │  85 个注册工具（文件/构建/GameTest/游戏桥/视觉/团队/worktree…）
   ▼
产物：mod/dist/*.jar + mod.zip（下载即玩）
```

## core/（引擎，纯 Python）

| 层 | 目录 | 职责 |
|---|---|---|
| domain | `core/domain/` | 纯类型：消息 DTO（User/Assistant/ToolResult + transport 转换）、流式增量、Mode/SandboxMode、7 个语义异常。零 IO 零依赖 |
| interfaces | `core/interfaces/` | 5 个 Protocol 契约：ModelClient / EventWriter / ToolRegistry / SessionStore / SkillRepository |
| services | `core/services/` | 业务编排。`loop/` 是主循环七模块（runner 编排、state 计数器、injections 注入序列、model_call 流式+空响应熔断、tool_batch 批执行、guards 守卫瀑布、exits 出口闸、profiles 模式策略）；compaction 三层压缩；session_log 事件源 |
| infrastructure | `core/infrastructure/` | 副作用实现：openai_client（适配器：多模态展开/Zen 会话头/超限识别）、session_files（.chat 三文件）、tools/（85 工具包，27 模块 + schemas 分片 + handlers 装配）、config（Settings 收敛全部 DSH_* env）、logging_（统一 logger + run.log 协议写入器）、autowrite/spill |
| 组装根 | `core/bootstrap.py` | 唯一 new 的地方；build_engine(Settings) → AgentLoopEngine；use_legacy=False 可纯 Fake 装配（测试） |

### 主循环行为要点（平价基准 = main 的旧实现）

流式协议行（[reply]/[思考+] JSON 编码逐 delta）→ run.log → server 解析 → 前端；
空响应熔断（5 次→压缩 / 8 次→强制收尾）；GameTest 出口闸（src/test @GameTest +
通过标记 + dist jar；打回 ≥3 且有产物→兜底收尾）；完成闸 25 轮宽限 +
模型总结；写前 6 次/写后 8 次研究预算（starter→骨架二振兜底）；
MAX_TOOL_ROUNDS=200 / MAX_TOTAL_ROUNDS=300；[CONCLUDED] 提前收尾；
队友 working 阻止退出。全部有离线测试锚定（tests/test_engine_parity.py）。

## server_app/（网站，三层）

| 层 | 目录 | 职责 |
|---|---|---|
| api | `server_app/api/` | 表现层：4 个路由模块（sessions/tasks/artifacts/history）+ dto + deps；create_app 工厂含静态托管/debug 兜底/startup 钩子。server.py 仅 ~45 行入口 |
| services | `server_app/services/` | session_manager（实体+恢复+孤儿清理）/ task_dispatcher（模式三层推断唯一实现+排队/恢复/重拉+子进程 env）/ templates / stats（daemon 状态机）/ packaging（zip 缓存+原子替换）/ uploads / round_runner（单轮生命周期）/ daemon_runner（常驻循环）/ finalizers（知识沉淀） |
| infrastructure | `server_app/infrastructure/` | session_disk（key/owner/mode/config.json 四文件——v2 修复重启丢配置）/ process_governor（进程治理四件套）/ daemon_protocol（daemon.state/pid/pending 读侧契约） |

### 跨进程文件协议（server ↔ run_task）

| 文件 | 写侧 | 读侧 | 语义 |
|---|---|---|---|
| `.chat/daemon.state` | daemon_runner.DaemonFiles | daemon_protocol | waiting=空闲 / working=跑轮 |
| `.chat/daemon.pid` | DaemonFiles | process_governor | 重启清理遗留 daemon |
| `.chat/pending.jsonl` | FileSessionStore | 同 | 运行中插话队列（一轮消费一条） |
| `.chat/working.jsonl` | 引擎每轮 | run_task | 断点（暂停/继续） |
| `mode.txt` | task_dispatcher | run_task daemon | 模式切换时 daemon 自杀重拉 |
| `run.log` | EventWriter 协议行 | log_events → /api/events | 前端过程流（协议保持旧格式） |

## tsinghua agent server/（清小搭 8001 接入）

`core.services.loop.run_agent_loop` 门面的第二个消费方（只读 chat 模式，
每会话 session_daemon 子进程）。P5a 已切换引用；main.py 1252 行的文件级
拆分待 P5b。

## 测试

- `tests/test_engine_parity.py` —— FakeModelClient/FakeRegistry 脚本化驱动
  主循环全路径（16 项：协议行/熔断/闸/预算/上限/插话/骨架/spill/压缩）。
- `tests/p7_smoke.py` —— 真实 /mod 端到端冒烟（起临时 server→蓝宝石剑任务
  →jar/zip/事件流验收）。
- `pytest tests/`（引擎离线测试，秒级）。

## 关键设计决策（已确认）

1. **run.log 文本协议保持不变**——EventWriter 封装输出，前端零改动。
2. **行为平价**——以 main 分支旧实现为唯一基准；src/engine 旧半成品的
   9 项行为缺口教训全部写入测试锚定。
3. **裸 dict 只允许出现在 OpenAI SDK 边界**（openai_client 适配器）与
   磁盘序列化格式（SessionEvent.payload / schemas）。
4. **每会话一个子进程**——引擎内全局单例（工具注册表/任务板）的隔离根基。
