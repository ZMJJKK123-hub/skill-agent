# 项目阅读与重构准备记录

日期：2026-10-29。基线：`main` / `b4d973ac`。

本轮只做阅读、静态检查和离线核验，不修改业务代码，不启动真实模型任务或 Minecraft。
开始阅读时已有 `server_app/server.py` 修改，以及未跟踪的 `agent.md`、`agent_loop/`；均保留原状。
`agent.md` 已阅读，本记录不确定新的目录架构，也不开始重构实现。

## 1. 阅读范围与边界

覆盖项目目录、入口、第一方 Python 模块、前端状态与插件、构建配置、模板配置和开发文档。
核心调用链及关键分支作详细阅读；技能库作目录、加载机制和全量 frontmatter 校验；Minecraft/Forge 参考树作版本与挂载关系检查。
没有逐行审计两套 Minecraft 反编译源码、全部领域知识正文、压缩后的前端产物、音频图片或历史运行数据。
没有读取 `.env` 凭据及用户认证数据内容。历史开发文档只用作背景，实际行为以当前源码为准。

| 区域 | 当前内容与作用 |
| --- | --- |
| `core/` | 46 个 Python 文件，11,089 行；实际使用的引擎、工具、团队和会话机制 |
| `agent_loop/` | 6 个 Python 文件，377 行；未接入产品的最小重构骨架 |
| `server_app/` | 5 个直接 Python 模块，2,714 行；网页 API、认证存储、任务进程、日志解析与 CLI 启动器 |
| `server_app/frontend/src/` | 18 个源码/样式/声明文件；Vite + React 18 + TypeScript + Tailwind |
| `tsinghua agent server/` | 3 个 Python 文件，1,601 行，含调试服务；OpenAI 兼容接口和独立 daemon |
| `core/skills/` | 172 份内置技能文档 |
| `mod_templates/minecraft/` | 5 个模板目录；包含 1.21.11 和 26.2 两种实际构建目标 |
| `mc_java_sources_1.21.11/`、`mc_java_sources_26.2/` | 分别 7,572 / 8,543 个参考文件；不是 Agent 引擎自身源码 |
| `server_app/debug/` | 独立小游戏页面与脚本，由网页游戏插件通过 iframe 使用 |
| `data/`、`.team/`、`.tasks/`、`.worktrees/` 等 | 运行时工作区与状态，不作为重构源码或验证样本 |

## 2. 实际架构与调用链

### 网页调用链

```text
frontend/src/main.tsx
  → composition.ts 装配插件
  → shell/registry.tsx 注册槽位 + AppShell.tsx 渲染
  → plugins/conversation.tsx 发送普通聊天或 /mod
  → lib/session.ts 编排会话、轮询、暂停、恢复、历史
  → lib/api.ts 调用 /api/*
  → server.py 鉴权、会话配置、模板准备、启动任务进程
  → run_task.py 切工作目录、设置环境、恢复历史/断点
  → core.agent.agent_loop(messages)
  → 模型流输出 → 工具执行 → 校验/收尾
  → run.log / agent.log → log_events.py → 前端事件与状态
```

网页 chat 和 mod 都有常驻 daemon。首轮结束后进程继续等待，消费 `.chat/pending.jsonl`。
chat 工作目录是会话根；mod 工作目录是会话下的 `mod/`，部分状态仍放会话根。
`daemon.state`、`daemon.pid` 和进程存活情况共同参与网页运行状态判定。

### 清小搭调用链

```text
main.py /v1/chat/completions
  → 鉴权、消息/附件归一化、人格与固定回复分支
  → 按 sessionId 分配 .runtime/sessions/<id>/
  → daemon/queue/<request>.json
  → session_daemon.py
  → core.agent.agent_loop(messages)
  → daemon/results/*.json + daemon/reasoning/*.jsonl
  → JSON 或 SSE 响应、附件链接
```

清小搭与网页的进程管理、队列和结果协议分别实现，但最终使用同一套旧引擎。
SSE 的思考文本来自增量文件；最终正文在引擎完成后分片发送。

### 旧引擎内部边界

| 模块 | 实际职责与依赖 |
| --- | --- |
| `core/agent.py` | 编排、流响应解析、消息注入、重试、压缩、工具执行、预算、写码提醒、GameTest 出口和收尾 |
| `config.py`、`promptkit.py`、`tool_guide.py` | 环境读取、提示词分段、客户端、日志、预算及路径基准；存在导入期副作用 |
| `tools.py`、`toolkit.py`、`tool_gate.py` | schema、handler、元数据及注册表；chat 白名单和 mod 分阶段工具开放 |
| `conversation.py`、`session_log.py`、`step_machine.py`、`agent_hooks.py` | 对话历史、工作断点、消息队列、事件记录、工具配对修复及轮次钩子 |
| `tools_mod.py`、`gradletools.py`、`tools_loop.py` | Gradle 构建、GameTest、日志解释、jar 复制、源码 ZIP 和验证闭环 |
| `tools_validate.py`、`tools_gametest.py`、`tools_artifact.py` | 资源、测试日志和交付物检查；结果主要是文本 |
| `tools_fs.py`、`tools_shell.py`、其他 `tools_*.py` | 文件、命令、搜索、下载、截图识图、游戏输入和进程工具 |
| `tools_tasks.py`、`protocol.py`、`tools_team.py`、`subagent.py` | 任务板、关机/计划协议、线程队友和异步子代理 |
| `tools_runtime.py`、`worktree.py` | 全局实例接线、线程本地工作目录、Git worktree 生命周期 |
| `supervisor.py` | mod 模式后台观察、模型分析和建议文件信箱 |

工具表中有 84 个静态 schema，另有按配置追加的视觉工具。主循环与子代理使用 `ToolRegistry.execute()`；队友仍直接调用 `TOOL_HANDLERS`。

### 新骨架的当前状态

`agent_loop/agent.py` 调用 `prompt → llm → exit_gate → tools`，没有导入 `core`。
已有 `ToolCall`、`LlmResult`、`GateDecision`，以及 schema/handler 联合登记入口。
工具实现尚未迁入；jar 和 ZIP 构建为桩；没有接入历史、断点、流输出、压缩、重试、取消、技能和真实 GameTest 判定。
目前网页、清小搭和 CLI 都没有切换到它；`pyproject.toml` 也只打包 `core`。

## 3. 已发现的问题与证据

“离线复现”只表示针对该分支的最小核验，不等于完整网站或真实 Minecraft 端到端测试。

| 优先级 | 问题 | 证据与影响 |
| --- | --- | --- |
| 高 | GameTest 失败可能被判为完成 | `core/agent.py:692` 的通过标记包含 `[gametest]`；`tools_mod.py:253` 的启动失败、超时等也使用此前缀。离线执行原判定表达式，失败文本得到 `True`；若 dist 有旧 jar，就可能提前结束。还缺少测试结果与本次源码/构建的关联。 |
| 高 | 监管器状态没有按会话隔离 | `supervisor.py:59` 使用仓库级 `.supervisor/inbox`；`:219` 从所有会话选择最新 run.log；转录路径也是仓库级。多会话运行时可能观察别的会话或消费其建议。此项为源码确认，未启动并发模型任务。 |
| 高 | 重置接口的请求契约不匹配 | `frontend/src/lib/api.ts:148` 发送 JSON `{session_id}`；`server.py:693` 将参数声明为查询参数。保留原签名、用空函数体做 FastAPI 隔离核验：JSON 请求 422，查询参数请求 200。 |
| 高 | 源码 ZIP 预生成有确定类型错误 | `tools_mod.py:35` 对 `base` 使用 `.parent`，但 `worktree.py:371` 的 `resolve_dir()` 返回 `str`。离线调用原函数得到 `AttributeError: 'str' object has no attribute 'parent'`，且该语句在 try 之前。网页下载有独立打包实现，因此不能据此断言所有 ZIP 下载都失败。 |
| 高 | mod 模式提问文件位置不一致 | `tools_ask.py:45` 在 cwd 写 question/answer，即 mod 目录；`server.py:1348`、`:1374` 在会话根读写。chat 目录恰好相同，mod 目录不同。 |
| 中 | 运行状态和业务成功混用 | `server.py` 把进程退出/daemon 等待映射为 finished；结果又来自日志尾部。失败、取消、预算耗尽和业务验证通过没有统一的类型化结果。 |
| 中 | 配置与会话状态依赖导入时机 | `config.py` 导入时构造客户端、读取 cwd/模式/预算；`tools_runtime.py` 导入时组装管理器。当前子进程隔离是行为前提，不能直接改成多用户共享线程。常驻进程的 queued 分支还先于会话配置覆盖返回，模型配置变更需要单独定义生效时机。 |
| 中 | 工具执行和错误格式不统一 | 队友在 `tools_team.py:501` 绕过注册表执行管线；工具输出有 Error 文本、JSON 字符串和 build/gametest 前缀。错误判定和权限控制分散，不能只迁 schema。 |
| 中 | 文件状态缺少统一原子更新策略 | `auth_store.py:43` 直接覆盖 JSON；`conversation.py:204` 读队列后清空，生产者位于另一进程，未见进程间锁。存在并发丢更新/读到半写文件的风险，需通过并发验证界定。 |
| 中 | 模板选择与真实目标版本不一致 | `forge-1.21.9`、`forge-1.21.10` 的 build.gradle 实际也指向 1.21.11；26.2 模板用 Java 25，旧提示词/参考挂载仍大量固定 1.21.11。`_copy_template()` 对缺失目标回退游戏根目录，不能把“目录存在”当作目标已正确准备。 |
| 中 | 10 份技能 frontmatter 无法解析 | 全量 YAML 校验确认，当前 SkillLoader 会回退为空元数据并保留原文本，导致描述/调用策略降级；不是整个服务必然崩溃。见下一节清单。 |
| 低 | 文档、依赖与包入口有漂移 | `server_app/README.md` 仍描述 Next.js；SPEC 的导入等说明与已注释实现不一致；新包说明中的 `python -m agent_loop` 缺少 `__main__.py`；`requirements.txt` 未声明视觉模块使用的 Pillow，`pyproject.toml` 未登记运行依赖。 |

YAML 解析失败的技能：

- `forge-items`
- `minecraft-custom-font`
- `minecraft-function`
- `minecraft-noise`
- `minecraft-pack-mcmeta`
- `minecraft-snbt-format`
- `minecraft-superflat-preset`
- `minecraft-tutorial-datapack-create`
- `minecraft-world-preset`
- `simple-mod-template`

主要原因是双引号字符串内的未转义引号和反斜杠转义。

## 4. 本轮验证结果

| 检查 | 结果与范围 |
| --- | --- |
| Python AST 语法解析 | 64 个第一方 Python 文件通过；没有导入并运行网站或旧 Agent |
| 新骨架最终回复 | 假模型单轮返回通过 |
| 新骨架工具往返 | 假模型发起工具，再返回最终文本，通过 |
| 模型异常与工具错误 | 模型异常、未知工具、无效 JSON 返回错误文本，通过 |
| 轮次出口 | 达到上限时返回结束决策，通过 |
| SessionLog | JSONL 序列化/反序列化及消息还原通过 |
| 工具 guard | 拒绝执行的基本行为通过 |
| 上述基础冒烟合计 | 7 项通过；脚本仅内存执行，未新增测试源文件 |
| 缺陷复现 | GameTest 失败误判、ZIP 类型异常、reset 请求参数位置不匹配均复现 |
| 技能元数据 | 172 份检查，10 份解析错误，无重复技能名 |
| 前端类型检查 | 未执行：项目本地 node_modules/TypeScript 不存在；未自动安装依赖 |
| 自动化测试基础 | 未发现专用 Agent 回归测试套件/CI 配置；本机未安装 pytest。根目录连通性脚本会调用真实模型，未运行 |
| 真实模型、Gradle、GameTest、游戏 GUI | 未执行，本记录不声称完整产品验证通过 |

## 5. 后续重构顺序建议

以下是职责迁移顺序，不是已经确定的新目录架构或接口契约。

1. **固定现有行为与复现场景。** 优先建立完成判定、会话隔离、暂停恢复、reset、提问应答和打包的回归基线。将已确认缺陷与纯行为迁移分开记录。
2. **明确配置和状态归属。** 定义会话级配置、路径、运行状态、结果和事件的契约；显式组装客户端与管理器。保留当前进程隔离前提，直到有证据允许改变。
3. **统一工具执行入口。** schema、实现和元数据单处登记，主 Agent/队友/子代理都走同一执行管线；将人类日志与机器可判定的工具结果分开。
4. **先迁可独立核验的循环能力。** 模型适配、消息配对、预算、取消、重试、压缩、事件发布分别建立行为对照；新循环保持编排职责。
5. **迁入 Minecraft 交付闭环。** 统一构建、资源校验、测试结果和产物清单；只有当前工作对应的验证结果满足要求，才允许成功收尾。
6. **逐入口接入新骨架。** 网页 chat、网页 mod、清小搭分别验证，保留迁移阶段的回退路径。达到功能对等后再删除旧实现和过时文档。

必须保留并验证的行为：用户 Key 不被仓库 `.env` 覆盖、会话归属校验、chat/mod 工作目录差异、运行中插话、暂停断点、daemon 空闲状态、工具调用与结果配对、历史回放、jar/源码下载，以及模板构建约束。

重构边界应由职责、状态所有者和副作用决定，不以文件行数决定。已有 `agent_loop/` 可作为迁移起点，当前尚不具备替换旧引擎的条件。
下一轮确定重构范围后，再细化对应目录和接口契约；本轮没有开始代码迁移。
