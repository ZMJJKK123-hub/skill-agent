# DSH 机制适配方案（skill-agent → DSH 设计对齐）

> 状态：**M1-M4 已实施完成（2026-08-15）**，本文件保留为实施记录与后续演进参照。
> 目标读者：本项目维护者
> 原则：只适配、不重写；每步可独立落地、可回滚；前端已按 DSH 形状重写，方案只针对后端 `core/`。

## 实施记录

| 里程碑 | 状态 | 关键验证 |
|---|---|---|
| M1 提示词 section 化 | ✅ 已实施 | 新 `core/promptkit.py`；mod/chat 双模式渲染与旧拼接**逐字节一致**（golden 对照：28,396 / 20,548 字符） |
| M2 Skill 目录动态注入 | ✅ 已实施 | SkillLoader 多源分层（会话 100 > 自定义 300 > 内置 600）+ 平铺 .md + `disable-model-invocation` 策略 + 正文现读 + sha256 digest 目录消息注入（主循环 + 子代理循环）；system prompt 从 28,396 → 8,515 字符 |
| M3 工具注册与执行管线 | ✅ 已实施 | 新 `core/toolkit.py`（ToolDef/ToolRegistry/pre-guard-post 钩子/timeout opt-in/惰性 handler）；leader/subagent/supervisor 过滤改声明式且与旧列表逐条一致；三循环执行统一走 registry |
| M4 子代理异步化 | ✅ 已实施（用户确认） | task 工具异步后台派发（父 agent 不再卡死）；persona 覆盖 + tools 过滤 + stop_event 中断 + stop_reason（completed/error/max-turns/aborted）结构化结果；结果经 `<background-results>` 下一轮注入 |

> 注：M1-M3 均为行为保持型改动（渲染/执行逐字节一致）；M4 按约定改变了 task 工具模型可见行为（异步化），已获用户确认。

---

## 0. 背景与目标

skill-agent 是一个 Minecraft Forge MOD 制作 agent（Python + OpenAI 协议 + FastAPI + React 前端）。
DSH（DeepSeek Harness，参考版本：工作区 `deepseek-harness/` @ 47f9438 master）是一个 Cordis 插件式 agent harness。

已确认的适配优先级（用户选择）：
1. **提示词 section 化组装**
2. **Skill 目录动态注入**
3. **工具注册与执行管线**
4. **子代理协议升级**

（未选：Agent 预设配置化——可作为后续演进方向，方案中仅作展望。）

---

## 1. DSH 关键机制速览（调研结论）

### 1.1 系统提示词组装（packages/core/system-prompt）
- 提示词由多个 **PromptSection** 拼装：`{ name, order, text | (ctx)=>string, complete? }`，按 `order` 升序拼接。
- 顺序约定：`-100` harness 身份（`"You are an AI agent powered by DeepSeek Harness."`）→ `0` deployment persona（配置模板，支持 `{{model}}`/`{{cwd}}` 等**严格变量插值**，未注册变量直接报错）→ `100-199` 工具指引段（每个工具包注册自己的指引段）→ 其他段。
- `complete: true` 的段可整体替换系统提示词（如 preset persona 自持）。
- 另有 **PromptContext**（动态上下文，如 cwd 快照）与 **变量注册表**（`variable(name, provider)`）。
- 每个 agent 有独立 scope；scope 链 `agent → preset → global`，近者遮蔽远者。
- 组装是"注册-组装-渲染"三步：插件注册段 → `assemble()` 合并 → `renderPrompt()` 插值。

### 1.2 工具系统（packages/core/tools）
- 工具是注册对象 `ToolDefinition`：`schema + output 声明 + execute + (可选) timeoutMs / isConcurrencySafe / presentCall / presentResult / finalizeContent`。**模型侧只发 `{name, description, parameters}` 白名单**，执行/展示细节绝不泄漏到协议。
- **输出契约强制化**：每个工具必填 `output: { schema, render(args,value) }`，执行后统一校验/快照/渲染，非法输出转 isError（`INVALID_OUTPUT`）。
- 执行管线（waterfall，顺序固定）：`tools/pre-execute`（allow/deny/ask 决策）→ 单调 guard（**只有 deny，无 allow**，监听顺序无法撤销拒绝）→ `tools/execute`（around 分发，可替换 signal 实现超时/重试/指标）→ 函数体 → `tools/post-execute`（accept/block/replace/附加上下文）→ `finalizeContent`（恰好一次）→ `tools/result`（冻结不可变快照）。
- 作用域：`register()` 按 scope 分层注册，近者遮蔽；`restrict({allow|deny})` 只过滤**继承面**、不触及 scope 自身注册（保证子代理保留回报工具）；`executionMode` 按 `isConcurrencySafe` 分类并行/独占（fail-closed，默认独占）。
- 审批：`pre-execute` 返回 `ask` → 审批服务（fail-closed：无回答者即拒绝；`allowed-once` 一次性授权）；会话级 `ApprovalPolicy = ask|never` 持久化可切换。
- 沙箱：`SandboxMode = read-only|workspace-write|danger-full-access`，每操作边界解析（非全局开关）；变更类工具参数表**有条件地**出现 `sandbox_permissions + justification` 升级字段（仅限被拒后的一次严格更宽重试）；拒绝映射为 `[sandbox: …]` 统一标记。
- 文件安全：`fs/observed` 观察事件 + 写意图 gate（`createIfAbsent` / `replaceIfVersion` CAS）实现**先读后写/编辑**（edit 要求先 read，否则 `FS_NOT_OBSERVED`）。
- UI 渲染意图：`presentCall/presentResult` 返回 card 联合类型（generic/terminal/diff/search/read/web），前端据此渲染工具卡片。
- 参考：完整源码级报告见 `dsh-tools-system-report.md`（子代理调研产出，含 write 工具完整示例、执行管道逐段代码、审批/沙箱挂载点）。

### 1.3 Skill 机制（packages/skill）
- 分层注册表：provider 注册到 scope 层；本地发现优先级 rank：
  `100 project .dsh/skills → 200 project .agents/skills → 300 custom → 400 user dshHome/skills → 500 user agentsHome/skills → 600 bundled`。
- 命名：kebab-case；格式：目录包 `<name>/SKILL.md` 或平铺 `<name>.md`（不支持嵌套递归）；frontmatter 字段：**必填 `name` + `description`**，可选 `whenToUse` / `metadata` / `disable-model-invocation` / `user-invocable`（调用策略：模型可调 / 用户可调，双通道）；子目录 `agents/`、`scripts/`、`references/` 均为**按需加载**，绝不自动注入。
- **目录注入**（渐进式披露的核心）：模型会话**永远只看到目录（name + description，XML 转义，description 截断 ≤500 字符）**；目录以 user 角色 `<system-reminder>` 持久消息注入，**sha256 digest 驱动整表替换**（在每次 agent/pre-step 计算 digest，变化才追加新目录消息，不变则零开销）——不是每轮全量重发，更不是拼进 system prompt。
- `skill({name})` 工具按需加载全文，返回 `<skill_content name="...">` 块；正文每次 `get()` 现读现解析（注册表不缓存完整定义）。
- 完整发现快照分 `complete/incomplete`；调用策略在 frontmatter 解析为 `SkillInvocationPolicy`，工具加载前先经 `isModelInvocable` 拒绝无权访问。

### 1.4 子代理（packages/subagent）
- provider 注册表（spawn/fork/acp/codex/claude-code 多后端共存），能力声明 `SubagentCapabilities = { outputSchema, depthLimit, toolFilter, persona }`，**不支持的能力在 start 时显式拒绝**。
- 单次（one-shot）run：`start() → SubagentRun { id, result, dispose }`，结果含 `output + stopReason(completed|aborted|error|max-tokens|refusal)`。
- 可继续（continuable）：持久化子会话 + Activation + `followup()/interrupt()/reportFrom()/listChildren()/listDescendants()`；inbox 是唯一队列。
- 关键委托参数：`persona`（子代理专属 persona，shadow 部署 persona）、`toolFilter`（子代理可见工具过滤，一个可见性）、`maxDepth`（委派深度上限）。
- 控制工具：`subagent / interrupt_agent / list_agents / send_message`。

### 1.5 生命周期与事件（packages/core/agent-loop, session）
- **step** = 一次模型请求 + 其工具调用；**turn** = 零或多个 step，从领取输入到不再欠债。
- 持久事件（session log）：`turn/start, user/message, assistant/chunk*, assistant/message, tool/call, tool/result, step/end, turn/end`。
- 实时钩子（waterfall）：`agent/pre-step`（改写/拒绝即将进入模型的 messages）、`agent/request`、`agent/request-error`（错误恢复）、`agent/turn-stopping`。
- 原则：**模型可见即已记录**（model-visible ⟺ logged）；注入用 `agent.inject()`。

---

## 2. 本项目现状 vs DSH（差距分析）

| 维度 | DSH | 本项目现状（core/） | 差距 |
|---|---|---|---|
| 提示词 | section 注册 + 有序拼装 + 变量插值 | `SYSTEM_MOD`/`SYSTEM_CHAT` 两个巨型字符串，`tools.py` 导入时把技能目录一次性拼进去 | 加/改提示词要改代码字符串；技能目录变化（新增 SKILL.md）需要重启进程才生效；无变量插值 |
| 技能 | 分层注册表 + 目录动态注入 + digest 替换 | `SkillLoader` 扫 `core/skills/`，目录**一次性拼接进 system prompt**；`load_skill` 全量注入；`move_skills_to_end` 滚动 | 单源单层；目录不随磁盘变化更新；注入位置固定为 system prompt 而非会话消息 |
| 工具 | 注册对象 + 执行管线 + 作用域过滤 + 结构化错误 | `TOOLS`（OpenAI dict 列表）+ `TOOL_HANDLERS` dict；子代理/leader/supervisor 的工具集靠**手工拷贝列表**过滤 | 无管线钩子（超时/审批/指标）；过滤散落各文件；错误全是裸字符串；无并行/独占声明 |
| 子代理 | 能力声明 + persona 覆盖 + toolFilter + 后台化 + 可中断 | `run_subagent` **同步阻塞**（task 工具 handler 里直接循环执行完才返回）；固定 `SUBAGENT_SYSTEM`；排除集是硬编码 set | 父 agent 等子代理期间完全卡住；无法给子代理定制 persona；无法中断 |
| 生命周期 | turn/step 事件 + 钩子瀑布 | `agent_loop` 内联 Layer 0-3 顺序注入，无抽象 | 注入逻辑与主循环耦合；扩展要改主循环 |
| 会话 | append-only 事件日志，可回放 | `conversation.jsonl` + `working.jsonl` 断点 + `pending.jsonl` | 已有近似能力，方向一致 |

**共同点（不需要动）**：subagent 结果回传（teammate 收件箱 ≈ reportFrom）、后台任务（bg_manager ≈ jobs）、断点恢复（working.jsonl ≈ 会话恢复）、skill-first 纪律（skillcheck 比 DSH 更严——DSH 不校验引用真实性，这是本项目优势，保留）。

**既有移植先例（证明渐进移植可行）**：
- `core/compact.py` 已移植 DSH compaction-basic（三层压缩：micro_compact/auto_compact/compact 工具，含 toolPairingBalancedBefore 边界与 summary-is-smaller 校验）；
- 前端已按 DSH 形状重写（Slot 槽位 + 插件化 + composition.ts ≈ cordis.yml）；
- `config.py` 的 HTTP 自测单命令模式、`tools.py` 的 `[tool]`/`[tool-result]` 结构化日志行等均为 DSH 风格移植。

---

## 3. 适配方案（按优先级，每项独立可落地）

### 3.1 提示词 section 化组装（优先 ①）

**目标**：把 `SYSTEM_MOD`/`SYSTEM_CHAT` 拆成有序 section，支持变量插值，运行时组装。

**设计**（新增 `core/promptkit.py`，约 250 行）：
```python
# 核心抽象
@dataclass
class PromptSection:
    name: str
    order: int          # 约定: -100 身份 / 0 persona / 100-199 工具指引 / 200+ 规则
    text: str | Callable[[dict], str]
    complete: bool = False

class PromptAssembler:
    def __init__(self, sections: list[PromptSection], variables: dict[str, Callable[[], str]]): ...
    def assemble(self) -> str:          # 排序 + 拼接 + 严格 {{var}} 插值（未知变量抛错）
    def render(self, text: str) -> str  # 单段插值

# 预置 section（对齐 DSH 顺序约定）
HARNESS_IDENTITY = PromptSection("harness:identity", -100, "You are a Minecraft MOD development agent powered by skill-agent.")
PERSONA_MOD      = PromptSection("deployment:persona", 0, lambda ctx: ...)   # 原 SYSTEM_MOD 主体
PERSONA_CHAT     = PromptSection("deployment:persona", 0, lambda ctx: ...)   # 原 SYSTEM_CHAT 主体（按 MODE 选择）
TOOL_GUIDANCE    = PromptSection("tool:guidance", 100, ...)                  # Windows 规则/HTTP 自测模式等
SKILL_CATALOG    = PromptSection("skill:catalog", 110, ...)                  # 由 3.2 动态提供
RULES_*          = PromptSection("rules:gametest", 200, ...)                 # GameTest 纪律 / Forge 硬事实等
```

**关键改造点**：
1. `config.py`：`SYSTEM_MOD`/`SYSTEM_CHAT` 拆段；`SYSTEM` 常量改为 `prompt_assembler.assemble()`（保持向后兼容：`agent.py`/`subagent.py`/`supervisor.py` 里 `{"role":"system","content":SYSTEM}` 的调用点不变，只把 `SYSTEM` 变成函数调用结果或按需重算）。
2. 变量：`{{model}}`、`{{cwd}}`、`{{mode}}`、`{{sandbox_mode}}`、`{{skills_dir}}`（替换现在硬编码在字符串里的值）。
3. `tools.py` 里 `config.SYSTEM += skill_loader.get_descriptions() ...` 的**导入期拼接**改为注册一个 `skill:catalog` section（动态 text provider），并去掉 `config.SYSTEM +=` 副作用。
4. 工具指引段化：每个工具组（bash/write/background/team/worktree/gametest）从大字符串里拆成独立 section，方便按模式裁剪（chat 模式不注入 mod 段——现在靠两个大字符串，拆段后靠 section 集合配置）。

**收益**：改提示词 = 改一个 section，不再动大字符串；新增技能即时进目录；chat/mod 差异变成 section 集合差异；为"预设配置化"铺路。

### 3.2 Skill 目录动态注入（优先 ②）

**目标**：技能目录作为**会话消息**动态注入（DSH 模式），磁盘新增/修改 SKILL.md 后下一轮自动生效，不再依赖重启。

**设计**（改造 `core/tools.py` 的 SkillLoader + 新增注入逻辑）：
1. **多源分层**（对齐 DSH rank）：`core/skills/`（内置，rank 600 语义）→ `<session_root>/skills/`（会话级，rank 100 语义，mod 模板可自带）→ 可配置 `DSH_CUSTOM_SKILL_DIRS`。同名时高优先级源胜出。实现：`SkillLoader` 增加多根目录扫描 + 优先级合并（改动集中在 `_scan` 与 `__init__`）。同时支持**平铺 `<name>.md`**（现状只认目录包 `SKILL.md`，小改动）。
2. **目录动态注入**（核心改动，对齐 DSH digest 机制）：
   - 不再把目录拼进 system prompt；改为在 `agent_loop` 每轮开头（可放 `_drain_interjections` 之后）检查：
     - 计算目录 digest：对 `(name, description 首行)` **entries 列表**（而非渲染文本）排序后整体取 **sha256**；
     - 若与"已注入 digest"不同 → 以 **user 角色消息** 追加目录块（DSH 用 `<system-reminder>` 标签，本项目现状用 `<active-skills>`/XML 标签，**沿用本项目标签风格**保持一致性）：
       `Available skills (use load_skill to access): - name: 首行描述 …`；
     - 相同 → 不注入（省 token）。
   - 首轮必注入（初始 digest 为空 → 不等）。
   - 目录消息**先于**其他注入块追加（DSH 保证 catalog 在 skill-invocation 之前：background first, material last）。
   - `move_skills_to_end` 已把技能全文滚动到末尾——目录注入与其并存，不冲突。
   - **注意**：`micro_compact` 会裁剪旧 tool 消息，但目录是 user 角色消息、不在裁剪范围；`auto_compact` 摘要时目录消息可能被压进摘要区——digest 机制天然自愈（压缩后 digest 与已注入值可能不同 → 下一轮重新注入）。
3. **正文每次现读（一致性修复，配套必须）**：现状 `SkillLoader._scan` 启动时把全文读入内存，`get_content` 直接返回内存副本——会话中编辑 SKILL.md 后目录 digest 已更新但正文仍是旧版。改为 `get_content(name)` 时**重新读盘 + 重解析 frontmatter**（对齐 DSH "body-only edits change later tool calls"，无缓存协议）。
4. **frontmatter 调用策略**（小改动）：解析 `disable-model-invocation: true`（目录不出现 + `load_skill` 拒绝加载，报错提示"不可由模型调用"）与 `user-invocable`（预留用户手势通道），对齐 DSH `SkillInvocationPolicy` 双通道；解析失败 **fail-closed 整文件丢弃 + 日志告警**（现状 `_parse_frontmatter` 失败时静默当无 frontmatter 处理，需改为告警）。
5. **description 截断**：目录条目只保留首行标题（现有 `_shorten_description` 已实现，≤100 字符 < DSH 500 上限，无需改）。
6. **输出格式参照**（可选对齐）：DSH `load_skill` 等价物返回 `<skill_content name="...">` + `<skill_resources>` + `<skill_instructions>` 三段式；**本项目保持现有 `<skill name="...">` 格式**（`skillcheck.py` 的 `_SKILL_BLOCK_RE` 依赖它，改格式会破坏引用校验）——DSH 三段式仅作未来参考。

**收益**：会话运行中新增/修改技能 → 下一轮模型即见新目录；mod 模板自带技能自动被发现；token 更省（目录不变时零开销）。

### 3.3 工具注册与执行管线（优先 ③）

**目标**：工具从"dict 列表 + handler dict"升级为注册对象 + 可扩展执行管线，消除手工过滤列表。

**设计**（新增 `core/toolkit.py`，约 300 行；`tools.py` 渐进迁移，不动现有 35 个 handler 函数体）：
```python
# 注册对象（对齐 ToolDefinition 的模型可见面 + 执行元数据）
@dataclass
class ToolDef:
    name: str
    description: str
    parameters: dict                 # OpenAI function calling 参数 schema（保持协议不变）
    handler: Callable                # 现有 handler 直接包进来
    timeout_ms: int | None = None    # 超时（用线程/信号实现，Windows 上线程 + join(timeout)）
    concurrency_safe: bool = False   # 并行声明（对齐 executionMode）
    readonly: bool = False           # 声明只读（supervisor 过滤用）
    needs_approval: str | None = None  # 预留：审批模式 ask/allow/deny（对齐 pre-execute）

class ToolRegistry:
    def register(self, tool: ToolDef): ...
    def schemas(self, *, include: set[str] | None = None, exclude: set[str] | None = None) -> list[dict]: ...
    def execute(self, name: str, args: dict, *, pre: list[Callable] | None = None, ...) -> str: ...
    # 管线钩子：pre_execute（返回 allow/deny/ask）/ guard / post_execute
    def add_pre_hook(self, fn): ...   # 对齐 tools/pre-execute
    def add_guard(self, fn): ...      # 单调守卫：返回 reason 即拒绝
    def add_post_hook(self, fn): ...  # 对齐 tools/post-execute（可改写结果/附加上下文）
```

**关键改造点**：
1. **注册表化**：`TOOLS` → `ToolRegistry`；`TOOL_HANDLERS` 查询改为 `registry.get(name).handler`。为兼容，保留 `TOOLS`/`TOOL_HANDLERS` 兼容层（`property` 或迁移期双写），避免一次性改 35 个调用点。
2. **声明式过滤**（消灭手工列表）：
   - leader：`registry.schemas(exclude={"submit_plan"})`（替换 `LEADER_TOOLS` 推导）；
   - subagent：`registry.schemas(exclude={...现有 excluded set...})`（替换 `subagent.py` 硬编码）；
   - supervisor：`registry.schemas(include={"load_skill","read_file"})`（替换 `READONLY_TOOLS`，且未来新增只读工具时用 `readonly: True` 声明自动纳入）；
   - teammate：`registry.schemas(exclude=team 管理工具集)`。
3. **管线钩子落点**（首批 4 个，全部可选落地）：
   - **超时**：`timeout_ms` + 执行线程 `join(timeout)`，超时返回温和错误（对齐 DSH `timeoutMs` + tool-call-timeout-policy 作为 `tools/execute` 包装层，不发给模型）；
   - **守卫**：现有 `safe_path`/`_sandbox_mode`/`_is_mutating` 逻辑改造成 guard（写文件/跑命令前的策略集中化，而非散在 handler 里）——**注意**：这是重构，必须逐工具验证沙箱行为不变；
   - **审批预留**：`needs_approval` + pre 钩子返回 `ask` → 走现有 `ask_user_question` 通道（对齐 DSH ApprovalService fail-closed 语义：无人应答即拒绝）；会话级策略 `ask|never` 用环境变量 `DSH_APPROVAL_POLICY` 表达（现状 `DSH_SANDBOX_MODE` 同族）；
   - **沙箱升级字段**（对齐 DSH `sandbox_permissions + justification`）：可选为 write/edit/bash 参数表追加升级字段——**建议第二阶段**，改动模型可见 schema 需同步回归。
4. **结构化错误**（小改动）：handler 返回统一 `ToolResult` 对象或保留字符串但统一 `Error:` 前缀（现状已是），可选升级为 `{ok, error_code, message}` 结构——**建议第二阶段再做**，先保证现有行为不变。
5. **先读后写（CAS）**（对齐 DSH fs-observation-policy）：`edit_file` 要求目标文件先被 `read_file` 观察过，否则拒绝——本项目**暂缓**（现状 edit 直接跑，行为已稳定；如需防覆盖可后续加）。

**风险控制**：执行管线改造是**行为敏感区**（bash 沙箱、写文件 UTF-8、GameTest 工具），方案要求：每个工具迁移后跑一遍该工具的回归（现有 `__main__` 演示任务就是回归用例）。

### 3.4 子代理协议升级（优先 ④）

**目标**：子代理支持 persona 覆盖、工具过滤声明化、异步后台化、可中断。

**设计**（改造 `core/subagent.py` + `core/agent.py` 的 task handler）：
1. **persona 覆盖**：`run_subagent(prompt, *, persona=None)`；缺省用 `SUBAGENT_SYSTEM`；`task` 工具参数加可选 `persona` 字段（对齐 DSH per-child persona）。teammate 已有自定义 system_prompt（`spawn_teammate(name, system_prompt)`），子代理补齐同一能力。
2. **工具过滤声明化**：`run_subagent(..., tools=None)`，缺省 `excluded` 集不变；调用方可用 `tools=` 精确指定（对齐 toolFilter）。
3. **异步化**（最大收益点）：
   - 现状：`TOOL_HANDLERS["task"] = lambda **kw: run_subagent(kw["prompt"])` —— 父 agent 的模型调用循环里**同步执行**整个子代理（最长 30 轮），父 agent 完全卡死，前端显示"无响应"。
   - 方案 A（推荐，改动小）：`task` handler 改为**后台派发**——复用现有 `BackgroundManager`（`bg_manager`）：把 `run_subagent` 丢进 daemon 线程，立即返回 `task_id`；子代理完成后结果以 `<background-results>` 标签注入下一轮（现有机制已支持）。工具描述文本更新为"异步执行，结果下一轮注入"。
   - 方案 B（激进，第二阶段）：子代理结果走 teammate 收件箱（`teammate_manager.bus`），支持多子代理并行 + 逐个回报。
4. **可中断**：异步化后天然可中断——`job_kill`/`task 取消` 语义映射到子代理线程的 stop_event（现有 `BackgroundTask` 若有取消机制则复用；没有则加）。
5. **结果结构**（小改动）：`run_subagent` 返回结构化结果（`{output, stop_reason}`），stop_reason ∈ completed/error/max-turns/refusal，对齐 DSH `SubagentResult`；父侧据此判断是否重试/报告失败。

**注意**：异步化会改变模型可见行为（工具返回立即变短、结果下一轮到），需同步更新 `SYSTEM`（section 3.1 里的 tool:task 指引段）中的描述文字，并回归测试（现有 `__main__` 演示任务含子代理派发路径）。

---

## 4. 实施顺序与里程碑

| 阶段 | 内容 | 涉及文件 | 预计工作量 | 验证 |
|---|---|---|---|---|
| **M1** | 3.1 提示词 section 化 | `core/promptkit.py`(新)、`config.py`、`tools.py` | 1-2 天 | 运行 chat + mod 各一轮，对比 system prompt 渲染结果一致 |
| **M2** | 3.2 Skill 目录动态注入（含正文现读一致性修复） | `tools.py`(SkillLoader)、`agent.py`(agent_loop) | 1 天 | 会话运行中新增/编辑 SKILL.md → 下一轮目录与正文均为新内容 |
| **M3** | 3.3 工具注册与执行管线 | `core/toolkit.py`(新)、`tools.py`、`subagent.py`、`agent.py` | 2-3 天 | 35 工具逐一回归 + 现有演示任务全流程 |
| **M4** | 3.4 子代理协议升级 | `subagent.py`、`agent.py`、`config.py` | 1-2 天 | 演示任务含子代理派发路径回归；前端观察无卡死 |
| **M5**(可选) | 3.3 结构化错误 + 3.4 方案 B | 同上 | 2 天 | 全流程回归 |

**M1-M4 相互独立**（M3 的兼容层设计保证 M4 之前现有代码不受影响），可任意顺序或并行。

---

## 5. 明确不做 / 暂缓

- **Agent 预设配置化**（用户未选）：M1 的 section 集合已为它铺路，未来可用一个 `agents/<name>.yaml`（persona 段 + 工具 include/exclude + 技能范围）替代 MODE 环境变量，作为 M5+ 演进。参照 DSH preset 形态（`agent.cordis.yml` = 插件行列表 + persona 模板 + 工具行；`preset.yml` = 展示元数据；roster 按目录发现；`{{model}}`/`{{cwd}}` 模板插值）——Python 侧等价物：`agents/mod.yaml` / `agents/chat.yaml`，字段对齐即可，不需要 Cordis 插件树。
- **事件化生命周期**（turn/step 事件 + 钩子瀑布）：当前 `agent_loop` 的 Layer 0-3 顺序注入已工作良好；完整事件化收益有限且风险大，暂缓。M3 的管线钩子已覆盖工具侧需求。
- **审批（ask/deny）**：`needs_approval` 只预留字段，不落地交互；现有 `ask_user_question` 工具继续承担"问用户"职责。
- **会话事件日志重构**：现有 jsonl 三件套已够用，不重构。

---

## 6. 调研来源与状态

| 领域 | 来源 | 状态 |
|---|---|---|
| 提示词组装 | `docs/subsystems/system-prompt.zh.md`、system-prompt 包测试、agent-loop 测试（grep） | ✅ 已读 |
| 生命周期 | `docs/agent-lifecycle.zh.md`、`docs/architecture.zh.md` | ✅ 已读 |
| 工具系统 | `docs/subsystems/tools.zh.md`、子代理源码级报告 `dsh-tools-system-report.md` | ✅ 已读（源码级） |
| Skill 机制 | `docs/subsystems/skills.zh.md`、子代理报告（skill-filesystem/tool-skill 源码） | ✅ 已读（源码级） |
| Subagent | `docs/subsystems/subagent.zh.md` | ✅ 已读 |
| Preset | `packages/preset/agent-presets/README.zh.md`、`examples/headless-agent/cordis.yml` + `advanced.cordis.yml` | ✅ 已读 |
| 工具目录 | `docs/tool-catalog.md`（40+ 工具全清单） | ✅ 已读 |

> 说明：两个源码级深读子代理（agent-loop、preset/subagent/session）运行超 1 小时被判定卡死并中断；对应领域已通过直接阅读官方子系统文档与测试源码补齐，结论已体现在第 1-3 节。

---

*文档位置：项目根 `DSH_ADAPTATION_PLAN.md`（不提交到 git 前请确认；确认后实施前可移入 `docs/` 或删除）*
