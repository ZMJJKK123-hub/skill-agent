# DeepSeek Harness 工具（Tool）系统深度研究报告

> 研究对象：`C:\Users\59639\Desktop\skill-agent\deepseek-harness`（TypeScript monorepo，仅读 `src/` 源码与 `docs/`）。
> 只读研究，未修改任何文件。所有路径相对仓库根目录。

---

## 1. 总览：工具系统在架构中的位置

DSH 是 Cordis 插件式 agent harness（"一切皆插件"）。工具系统由三个包协同构成：

| 层 | 包 | 职责 |
| --- | --- | --- |
| 注册表与执行管道 | `packages/core/tools`（`@deepseek-ai/dsh-tools`） | `ToolRuntime` 服务：注册/作用域/限制/守卫/执行管道/Code Mode 传输 |
| 模型协议 | `packages/llm/llm`（`@deepseek-ai/dsh-llm`） | 模型侧 `ToolSchema` 类型、`GenerateOptions.tools`、流式 `tool-call` 块 |
| 循环调度 | `packages/core/agent-loop`（`@deepseek-ai/dsh-agent-loop`） | 把模型输出的 tool-call 解析成 `ToolExecutionInput`，并行/独占调度，记录会话事件 |
| 展示 | `packages/core/agent-tool-presentation` | preset 给 agent 声明工具展示模式（`presentAs`） |

工具本身以"插件行"出现在 `cordis.yml` 里，例如 `packages/fs/tool-fs`、`packages/shell/tool-bash`、`packages/web/tool-web` 等（仓库按 `packages/<group>/tool-<x>` 命名）。`docs/tool-catalog.zh.md` 由生成器 `scripts/gen-tool-catalog.ts` 在**真实上下文启动每个工具插件**后读取 `ctx.tools.schemas()` 生成，因此 schema 与源码严格同步。

设计主线：**注册是受信的同进程约定，执行是"可扩展 waterfall + 单调策略"的管道**；工具自身只声明 `name/description/parameters + output + execute`，权限、审批、沙箱、钩子全部挂在管道事件上，工具与策略解耦。

---

## 2. 工具定义：三层 schema

### 2.1 模型侧：`ToolSchema`（最薄的一层）

`packages/llm/llm/src/types.ts:305-317` —— 这是真正发给模型的 JSON Schema 描述，也是 `GenerateOptions` 的一部分：

```ts
/** JSON-schema description of a tool, as sent to the model. */
export interface ToolSchema {
  name: string
  description: string
  /** JSON Schema object for the arguments. */
  parameters: Record<string, unknown>
}
```

### 2.2 宿主侧：`ToolDefinition`（注册表持有的完整定义）

`packages/core/tools/src/index.ts:222-260`。`ToolDefinition extends ToolSchema`，追加**必需的规范输出声明 `output`**、`execute` 函数、`timeoutMs`、`isConcurrencySafe`、`finalizeContent`、`presentCall/presentResult`。关键约定：

- `execute(args: unknown, exec: ToolRunContext): Promise<unknown>` —— 只返回规范值；工具自行校验输入（第一方工具用 `defineTool` 代校验）。
- `output` 是强制字段，包含 `schema`（JSON Schema，对每个成功规范值强制执行）、`render(args, value): ContentBlock[]`（纯投影：规范值 → 模型可见内容）、`presentationMeta?`（纯展示投影）。
- `schemas()` 只投影 `name/description/parameters` 白名单字段，**`output`/`execute`/`finalizeContent`/`timeoutMs`/`isConcurrencySafe`/`presentCall/presentResult` 绝不泄漏到模型请求**（`packages/core/tools/src/index.ts:1234-1267` `schemas()`/`schemaOf()`）。

```ts
interface ToolDefinition extends ToolSchema {
  readonly output: ToolOutputDefinition        // 必需
  execute(args: unknown, exec: ToolRunContext): Promise<unknown>
  finalizeContent?(exec, result): ContentBlock[] | undefined
  timeoutMs?: number                           // 协同超时预算，绝不发给模型
  isConcurrencySafe?(args): boolean            // 纯分类器，true 才允许并行
  presentCall?(args): ToolCallView | undefined
  presentResult?(args, result): ToolResultView | undefined
}
```

### 2.3 输出契约 `ToolOutputDefinition`

`packages/core/tools/src/index.ts:212-223`：`{ schema: JsonSchemaNode; render(args, value): ContentBlock[]; presentationMeta?(args, value): JsonValue }`。执行成功后注册表会**快照 + 校验**返回值（`validateJsonSchemaValue`），失败抛 `ToolOutputError`（`INVALID_TOOL_OUTPUT`）。

### 2.4 作者侧 DSL：`ValueSchemaSpec` / `ParameterSchemaSpec`

`packages/core/tools/src/schema.ts`。第一方工具不手写 JSON Schema，而是用类型化 DSL 声明参数与输出，`defineTool` 负责编译与类型推断：

```ts
type ValueSchemaSpec =
  | StringValueSchemaSpec | NumberValueSchemaSpec | IntegerValueSchemaSpec
  | BooleanValueSchemaSpec | NullValueSchemaSpec | ArrayValueSchemaSpec
  | ObjectValueSchemaSpec | JsonValueSchemaSpec | OneOfValueSchemaSpec

/** 参数根是隐式开放对象；必填是逐属性的 required: true 标注 */
type ParameterSchemaSpec = { [key: string]: ParameterPropertySpec; [key: symbol]: never }
type ParameterPropertySpec = ValueSchemaSpec & { required?: true }
```

- `{ type: 'json' }` 是仅作者可用的无约束无损 JSON 节点（编译为仅注解的 schema）。
- `InferValue<S>`/`InferArgs<S>` 做编译期类型推断（16 层容器深度后回退 `JsonValue`，防止 TS 实例化栈爆炸），运行时校验仍走完整 schema。
- `parameterSchemaSpecToJsonSchema()` / `valueSchemaSpecToJsonSchema()` 编译到**已强制执行的原始 JSON Schema 子集**（`assertSupportedJsonSchema`，见 `json-schema.ts`）；不支持的 JSON Schema 关键字被**拒绝**而不是静默放行。
- 参数不匹配抛 `ToolArgsError`（`INVALID_ARGS`）；函数体/后置策略产生无效值抛 `ToolOutputError`（`INVALID_TOOL_OUTPUT`），都走常规工具错误路径。

### 2.5 `defineTool`（schema.ts:545-617）

`defineTool(options)` 把参数 DSL 编译成参数 JSON Schema、输出 schema 编译成规范 schema，包装 `execute` 使其先 `validateArgs` 再调用户函数；`render/presentationMeta/presentCall/presentResult/isConcurrencySafe` 全部用编译后的参数 schema 收窄类型；展示类回调**软校验**（回放旧日志时校验失败回退 `undefined` 而非抛错）。

---

## 3. 真实工具示例：`write`（完整结构）

来源 `packages/fs/tool-fs/src/write.ts`，展示 DSL 参数、输出契约、execute、presentCall/presentResult 的完整写法（摘录关键 55 行）：

```ts
ctx.tools.register(defineTool({
  name: 'write',
  description: 'Create or fully replace a UTF-8 text file.',
  parameters: {
    file_path: { type: 'string', required: true, description: 'Path to write, resolved by the filesystem backend.' },
    content: { type: 'string', required: true, description: 'Full UTF-8 text content to write.' },
    ...sandbox.escalationModes.length > 0 ? sandbox.schemaFields() : {},  // 有条件地追加沙箱升级字段
  },
  output: {
    schema: {
      type: 'object', additionalProperties: false,
      properties: {
        path: { type: 'string', required: true },
        operation: { type: 'string', required: true, enum: ['create', 'update'] },
        before: { required: true, oneOf: [{ type: 'string' }, { type: 'null' }] },
        after: { type: 'string', required: true },
      },
    },
    render: (_args, value) => [{ type: 'text', text: formatWriteOutput(value.path, value) }],
    presentationMeta: (args, value) => ({ diffs: value.before === null ? [] : computeHunkDiffs(...) }),
  },
  async execute(args: WriteToolArgs, exec) {
    const sandboxPolicy = await sandbox.resolvePolicy('write', args, exec)  // 沙箱策略解析
    const target = await ctx.fs.resolve(input.filePath, sessionResolveOptions(exec, input.filePath, ...))
    const intent = await ctx.waterfall('fs/write-intent', target, exec, () => undefined)  // 单槽策略
    let outcome = await ctx.fs.writeText(target, input.content, intent, exec.signal, sandboxPolicy)
    // 失败映射为模型可识别的 [sandbox: …] 标记
    ctx.emit('fs/observed', target, { kind: 'present', version: outcome.version }, exec)  // 记录观察
    return { path: target.displayPath, operation: outcome.operation, before: outcome.before, after: outcome.after }
  },
  presentCall(args): DiffCallView {
    return { card: 'diff', title: `Write ${args.file_path}`,
      diffs: [{ path: args.file_path, oldText: null, newText: args.content }], locations: [{ path: args.file_path }] }
  },
  presentResult(args, result: ToolResult): DiffResultView | undefined {
    if (result.isError) return undefined
    const diffs = diffsFromMeta(result.meta) ?? [{ path: args.file_path, oldText: null, newText: args.content }]
    return { card: 'diff', title: `Write ${args.file_path}`, diffs }
  },
}))
```

要点：参数 DSL 编译出的 `parameters` 与目录一致；`output.schema` 是严格闭对象；`render` 产生模型可见文本；`presentCall/presentResult` 是纯 UI 渲染意图（`diff` 卡片），可在流式与回放中重复调用。

---

## 4. 注册机制（`ToolRuntime`，`packages/core/tools/src/index.ts:787`）

`ToolRuntime extends Service`，`static inject = ['systemPrompt']`；构造函数注册 `ctx.systemPrompt.tools(ctx => this.wireSchemas(ctx.scope))`，使每次提示词组装都能拿到该 scope 可见工具的 schema 投影（`wireSchemas` 在 980-1001 行）。

公开 API（`ctx.tools`）：

| 方法 | 语义 |
| --- | --- |
| `register(definition): () => void` | 全局或当前 agent scope 注册；同名冲突与保留名 `run_code` 报错；返回精确 disposer（`layers.effect`，HMR 安全） |
| `restrict(filter): () => void` | 仅限 scoped 上下文；`allow`/`deny` 全局工具名，交集生效；`run_code` 与未知名拒绝 |
| `guard(guard): () => void` | 注册单调守卫（见 §5.3） |
| `get(name, scope?)` | 按 scope 解析可见定义 |
| `schemas(scope?)` | 白名单投影，深克隆，供模型请求 |
| `executionMode(exec)` | 分类并行/独占（fail-closed：只有 `isConcurrencySafe === true` 才并行） |
| `execute(exec)` | 完整管道入口（见 §5） |
| `presentAs(mode)` | scope 级展示模式声明（native/code/both） |

注册校验（`register`，1037-1062）：必须声明 `output { schema, render, presentationMeta? }`、`assertSupportedJsonSchema(output.schema)`、`timeoutMs` 必须是正有限数、拒绝保留名 `RUN_CODE_NAME`。

### 4.1 作用域：`ScopedLayers`

工具分层存储（全局层 + 每 agent scope 层），`view(scope)`（1152-1193）计算可见集：**继承面** = 全局层 + 祖先 scope 层（近者遮蔽远者），先应用整条链上的 restrictions 交集，再叠加该 scope **自己注册的**工具（不受限制约束 —— 保证被委派子 agent 保留其回报工具），最后按需插入保留传输 `run_code`。这就是"子 agent 继承父工具、又被父级 `toolFilter` 限制"的机制。

### 4.2 变化通知

任何注册/注销/限制变化触发 `tools/change` emit 事件（unfiltered）；由于 `wireSchemas` 在每次提示词组装时重新求值，工具集变化自动进入下一次模型请求（`request/header` 会话事件记录"完整且有变动的请求"）。

---

## 5. 执行管道（核心）

文档图 `docs/tool-execution-pipeline.zh.md`；实现全在 `packages/core/tools/src/index.ts`。完整顺序：

```
模型 assistant 消息含 tool-call 块
  → 会话事件 tool/call（执行前记录）
  → UI pending 卡片 presentCall(args)
  → tools/pre-execute waterfall（钩子/权限/审批策略）
  → 单调 guard（deny 或 abstain）
  → （ask 时）ctx.approval 一次性询问，无回答者即 deny
  → tools/execute waterfall（around 分发：超时/重试/指标）
  → 工具 execute() 函数体
  → fs/write-intent / fs/edit-intent gate（仅 tool-fs 变更类）
  → tools/post-execute waterfall（accept/block/replace/附加上下文）
  → 注册表外层规范化（异常转 isError）
  → ToolDefinition.finalizeContent（最后的仅内容不变式）
  → tools/result 同步通知（冻结的权威结果）
  → 会话事件 tool/result（唯一模型可见结果）
  → UI 完成卡片 presentResult(args, result)
```

### 5.1 入口与执行对象

- `execute(exec)`（1342）→ `prepareExecution()`（1463）→ `createExecution()`（1364）。
- `createExecution` 物化并**深冻结**参数（非无损 JSON 立即失败）、分配不透明 `ToolExecutionToken`（Symbol）、解析 `rootCallId`、在策略前**快照 `finalizeContent` 回调**、注册 `deferContext`/`concludeTurn` 能力。
- `ToolExecution`（379）只读承载 `callId/rootCallId/name/arguments/agent/parent/token/signal`；`ToolRunContext`（404）额外给工具 `deferContext()`（把上下文挂到自己结果上，供组合工具转运嵌套派发）与 `concludeTurn()`（标记本轮终结）。
- Code Mode 下模型直接调非 `run_code` 工具在**策略管道之前**就被 `collapses()` 判定拒绝（`UNKNOWN_TOOL`），确保策略监听器永不"批准一个必然失败的调用"。

### 5.2 `tools/pre-execute` waterfall（可重排策略）

`prepareExecution`（1473-1507）调用 `ctx.waterfall('tools/pre-execute', exec, default-allow)`，监听器返回 `PreToolDecision = { kind:'allow' } | { kind:'deny'; reason } | { kind:'ask'; reason? }`。之后：

- `ask` → `serviceAsk()`（1689-1729）经 `ctx.get('approval')`（机会式消费，无服务则降级 deny）→ `approval.request({agent, toolName, callId, reason, signal})`，四个结果 `allowed-once | rejected | cancelled | unavailable` 一一映射（仅 `allowed-once` 放行）。
- 之后才运行单调 guard `guardReason()`。

### 5.3 单调守卫（不可撤销的拒绝）

`ToolGuard = (execution) => string | undefined`（711）：返回 reason 即拒绝，`undefined` 保持放行。**没有 allow 结果**，因此监听器顺序无法把拒绝变回允许。守卫注册在全局或 agent scope 层（`guard()`，1110），`guardReason`（1119）先全局后 scope 链取第一个拒绝。

### 5.4 `tools/execute` waterfall（around 分发）

`dispatchScheduledExecution`（1569）用 waterfall 包装真正的 `dispatchToolBody()`（1532）。包装层只能替换 `exec.signal`（`ToolDispatchExecution`），注册表在调用函数体前用 `fuseToolSignals` **重新融合**调用方原始 signal —— 包装层无法脱离调用方取消。真实例子：`packages/guard/timeout-policy/src/index.ts:56-74`：

```ts
ctx.on('tools/execute', async (exec, next): Promise<ToolExecutionResult> => {
  const timeoutMs = ctx.tools.get(exec.name, exec.agent)?.timeoutMs
  if (timeoutMs === undefined) return next()
  using d = deadline(exec.signal, timeoutMs, TOOL_TIMEOUT)
  const result = await next()
  // 超时 → toolTimeoutResult(timeoutMs)（isError 结果）
})
```

### 5.5 函数体执行与文件系统 gate

`dispatchToolBody`（1532-1560）：解析执行定义（未知 → `ToolNotFoundError`，`UNKNOWN_TOOL`）、置 `bodyInvoked`、调 `tool.execute(args, exec)`、`createSuccessResult`（快照/校验/渲染，见 1793）。tool-fs 的变更类工具在函数体内部通过 `ctx.waterfall('fs/write-intent'|'fs/edit-intent', ...)` 单槽询问策略（`write.ts:111`）；`fs-observation-policy`（`packages/fs/fs-observation-policy/src/index.ts`）监听这三个 `fs/*` 事件实现**先读后写/编辑**：写需 `createIfAbsent` 或 `replaceIfVersion`（CAS），编辑要求先 `read` 过（否则 `FS_NOT_OBSERVED`）。

### 5.6 `tools/post-execute` waterfall

`postExecute`（1742-1781），监听器返回 `PostToolDecision = { kind:'accept'; content? } | { kind:'accept'; value } | { kind:'block'; feedback; additionalContexts? }`：accept 可替换 content（保留规范值）或 value（重新校验/渲染，二者不可同时）；block 把纠正反馈转成 isError；两种决策都可附带 `additionalContexts`（进入下轮请求的 FIFO）。

### 5.7 归一化、finalizeContent、tools/result

- `finishScheduledExecution`（1631）：`materializeFinalResult`（无损物化，失败转 isError）→ `applyFinalContent`（1631/1649，恰好调用一次快照的 `finalizeContent`）→ 再物化 → `notifyResult`（1657：冻结 exec，dispatch `tools/result` emit，监听器失败被隔离）。
- 结果类型 `ToolExecutionResult = ToolExecutionSuccess | ToolExecutionFailure`（556-580）：成功含 `value`（仅执行期存在，**不进持久化事件**）+ `content` + 可选 `meta`/`additionalContexts`/`concludesTurn`；失败含 `error { message, info? }`。
- 取消语义：函数体未启动的取消 → `ABORTED_BEFORE_DISPATCH`；已启动的成功结果被取消替代 → `ABORTED`（1919-1944）；已开始的 promise 从不被放弃（drain 到 quiescence）。

---

## 6. 模型侧的调用闭环（agent-loop）

`packages/core/agent-loop/src/agent.ts`：

1. `assemble()`（230）→ `systemPrompt.assemble()` 收集 `toolProviders` 的 schema（`structuredClone` 参数，`system-prompt/src/index.ts:467-542`）。
2. `buildRequest()`（407）把 tools 放进 `GenerateOptions.tools` 并记录 `request/header` 会话事件（463-470）。
3. LLM 适配器序列化：`packages/llm/llm-deepseek/src/serialize.ts:161-168` —— 每个工具转 `{ type:'function', function:{ name, description, parameters } }`（OpenAI chat-completions wire 格式）；流式 `tool-call-delta` 在 `translate.ts` 反向解析。
4. 模型返回 `tool-call` 块 → `executeToolCalls()`（`packages/core/agent-loop/src/tool-calls.ts:59`）：解析参数（`JSON.parse`，坏 JSON 保留原文）、构造 `ToolExecutionInput`，按 `ctx.tools.executionMode()` 分类 —— `exclusive` 形成顺序屏障，`parallel` 用 `maxParallelToolCalls` 有界滚动池；通过注册表的 `TOOL_RUNTIME_SCHEDULER` 符号（`prepare/dispatch/finalize/finish` 分阶段接口，index.ts:451-466）**让策略有序、分发重叠**。
5. 结果按模型顺序 `commitReady` 提交：追加 `tool/result` 会话事件（`appendToolResult`，267-289，附 `error.info` 与 `meta`），`additionalContexts` 进入下轮 inbox，`concludesTurn` 终止本轮。
6. 中止时未启动的调用获得合成 `ABORTED_BEFORE_DISPATCH` 结果（249-259），保证回放完整。

---

## 7. 内置工具总览（15 个代表）

（schema 全文见 `docs/tool-catalog.zh.md`，为生成器从真实启动的插件读取）

| 工具（包） | 用途（一句话） | 输入 → 输出要点 |
| --- | --- | --- |
| `read`（`fs/tool-fs`） | 读 UTF-8 文本文件返回带行号内容 | `file_path`(+`offset`/`limit`) → 行号文本；触发 `fs/observed` 为后续 edit 提供 CAS 依据 |
| `write`（`fs/tool-fs`） | 创建或整体覆盖文件 | `file_path`+`content`(+沙箱升级字段) → `{path,operation,before,after}`；先写后读策略门禁 |
| `edit`（`fs/tool-fs`） | 字面量替换编辑 | `file_path`+`old_string`+`new_string`(+`replace_all`) → 同 write 输出；要求先 read |
| `read_image`（`fs/tool-fs`） | 读图像返回图像本身 | `file_path` → 图像块；要求模型支持图像输入 |
| `glob`/`grep`（`fs/tool-fs-search`） | 路径/内容搜索 | `pattern`(+`path`) → 最多 100 路径 / 250 匹配行；基于随包 ripgrep 子进程 |
| `str_replace_editor`（`fs/tool-str-replace-editor`） | 有状态编辑（view/create/str_replace/insert） | `command`+`path`+... → 编辑结果文本 |
| `bash`（`shell/tool-bash`） | 执行 bash 命令 | `command`+`description`(+`timeoutMs`/`workdir`/`run_in_background`) → stdout/stderr；沙箱化，可入 `ctx.jobs` |
| `pwsh`（`shell/tool-pwsh`） | PowerShell 方言 | 同 bash 结构（Windows 原生路径） |
| `web_search`/`web_fetch`（`web/tool-web`） | 搜索/抓取网页 | `query` / `url` → 摘要+源列表 / 页面文本；后端经 `ctx.web` 可替换 |
| `ask_user_question`（`interaction/tool-ask-user`） | 向用户提问 | `questions[]`（id/question/options/multi_select）→ 人类答案；暂停直到 UI 回答 |
| `todo_write`（`todo/tool-todo`） | 维护结构化任务列表 | `todos[]`（content/status）→ 确认文本；`todo/write` 事件驱动 UI 清单 |
| `create_goal`/`get_goal`/`update_goal`（`goal/tool-goal`） | 持久会话目标 | `objective`/`goal_id`+`action` → 目标状态；要求人类根权限 |
| `subagent`（`subagent/tool-subagent`） | 委派独立子任务 | `description`+`prompt`(+`run_in_background`) → 子结果/后台 job id |
| `job_list`/`job_output`/`job_kill`（`jobs/tool-jobs`） | 通用后台任务控制 | `job_id`(+`wait`/`timeout_ms`) → 任务状态与输出 |
| `workflow`（`workflow/tool-workflow`） | 大规模 subagent 编排 | `script`(JS 函数体)+`meta`(+`args`) → 脚本返回值；前台执行 |
| `skill`（`skill/tool-skill`） | 加载 skill 指令 | `name` → skill 完整说明注入会话 |
| `run_code`（`core/tools` code-mode.ts） | 保留传输：执行 TypeScript 程序调用工具 | `code`+`description` → `{logs,result}`；子调用重入完整守卫管道 |
| `cordis_define` 等 7 个（`extensions/tool-cordis`） | 动态插件生命周期 | `plugin`+`name`+`purpose`+`code` → pluginId/packageId |

> 注：工具目录完整清单 30+ 工具，含 terminal_*、session_event_*、schedule_*、lsp、ralph、report、send_message、interrupt_agent、list_agents、exit_plan_mode 等，见 `docs/tool-catalog.zh.md`。

---

## 8. 动态工具 vs 静态工具

| 维度 | 静态工具（随产品发布） | 动态工具（`cordis_*` 插件运行时注册） |
| --- | --- | --- |
| 定义来源 | 编译期 TS，`defineTool` 强类型 | 沙箱内动态代码，`harness.defineTool`（`packages/extensions/cordis-host-runner/src/guard.ts`） |
| 定义校验 | TS 类型 + `assertSupportedJsonSchema` | `sandboxDefineTool`（guard.ts:551）对选项做纯运行时校验（plain record、own keys、schema 克隆、marker 标记 `[DYNAMIC_TOOL]`），错误信息带 `harness.defineTool <path>` 教学前缀 |
| 注册 | `ctx.tools.register(definition)` | `harness.registerTool(ctx, tool)`（guard.ts:626）—— `assertDynamicTool` 拒绝非 marker 定义；或经受守卫的 sandbox `ctx.tools.register` |
| 沙箱暴露 | 直接注入服务 | `sandboxContext`（guard.ts:718）白名单：`ctx.tools` 只暴露 `register`（marker 守卫）+ 只读 `schemas`/`get`（**绝不暴露可调用的 execute**，防止绕过管道）；注入服务仅限 `inject` 声明且返回值过 `denyContext`（禁止泄出 Cordis Context） |
| 生命周期 | cordis.yml 行，随组合装载 | `cordis_run`/`cordis_stop`/`cordis_undefine`；`ctx.effect` 注册的 disposer 在包停止时自动回收；运行中的 Package 可注册**额外模型可见工具**，经 `tools/change` → 下次组装进入请求头 |
| 工具管道 | 相同 | **完全相同** —— 动态工具注册进同一个 `ToolRuntime`，照走 pre-execute/guard/execute/post-execute/finalize/result |

核心差异不是执行路径，而是**信任边界**：动态工具的定义要经过更严的入站校验、数据要 clone、能力面被收窄（读不到别的工具 execute、拿不到 Context、服务要声明 inject）。

---

## 9. 审批 / 权限 / 沙箱如何挂在工具执行上

### 9.1 审批（`packages/interaction/user-approval`）

- `ApprovalService`（`ctx.approval`）：`request()`（index.ts:257）要求"开着的 turn"，先记 `approval/asked` 审计事件，经 `approval/request` waterfall（答案者链）取 `ApprovalOutcome`，再记 `approval/decided`；答案者缺失/抛错/返回非词汇 → fail-closed `unavailable`。
- 会话级 `ApprovalPolicy = 'ask' | 'never'`，以 `approval/policy` 会话事件持久化（`effectiveApprovalPolicy` 折叠日志）；`'never'` 在服务内**先于任何监听器**确定性拒绝；`setPolicy()` 切换时 `agent.inject()` 通知模型。
- 挂接点：工具管道只在 `PreToolDecision.kind === 'ask'` 时经 `serviceAsk` 调用它；`'allowed-once'` 是一次性授权，只对本调用有效。

### 9.2 权限预设（`packages/interaction/permission-presets`）

`PermissionPresetService` 把 `sandbox 模式 + approval 策略`捆绑成具名预设（默认 `workspace-write`=workspace-write+ask、`danger-full-access`=danger-full-access+never），以 `permission/preset` 事件持久化，新会话按 `defaultPreset` 初始化；要求挂载受约束的 `ctx.shell`（无 sandboxMode 报错）。

### 9.3 沙箱（`packages/sandbox/*`）

- `SandboxMode = 'read-only' | 'workspace-write' | 'danger-full-access'`，`ctx.sandboxPolicy.resolve({session})`（`packages/sandbox/sandbox-policy/src/index.ts`）每个操作边界解析一次；会话覆盖经 `sandbox/mode` 事件。
- 策略注入系统提示词上下文（order 110，`renderPolicyContext`），让模型知道当前文件策略。
- 工具级执行：bash 与 fs 共用 `@deepseek-ai/dsh-sandbox` 的升级词汇 —— 受约束后端存在时，变更类工具参数表**有条件地**出现 `sandbox_permissions`（enum 锁定升级目标）+ `justification`（`fs/tool-fs/src/sandbox.ts:59-73`）；`resolvePolicy` 在函数体内先校验"仅限一次被拒后的严格更宽重试"，经 `approveEscalation`（走 `ctx.approval`）获批才执行；拒绝映射为 `[sandbox: file access denied under <mode> mode]` 标记（模型从 bash 学会识别）。
- 底层执行器：`packages/sandbox/sandbox-local`（本地目录 ACL/进程包装）、`sandbox-windows-acl`、`fs-sandbox`、`bash-sandbox`、`subprocess-local` 等按平台/组合提供 enforce。

### 9.4 钩子桥（`packages/hooks/*`）

`hooks-codex`（index.ts:225-240）与 `hooks-claude-code` 是 `tools/pre-execute`/`tools/post-execute` 的典型第三方策略监听者：把 Codex 的 `PreToolUse` 钩子输出合并后，在 pre 阶段返回 `{ kind:'deny', reason }`（Codex 只支持 deny），在 post 阶段返回 block。这印证了管道设计：**审批/权限/钩子全部是 waterfall 监听者，与工具本身解耦**。

---

## 10. 对 Python 版 agent 的借鉴（总结）

1. **三层 schema 分离**：模型侧只发 `{name, description, parameters}` 白名单（OpenAI 兼容 JSON Schema），宿主侧持有 `output.schema + execute + render`，执行/展示细节永不泄漏到协议 —— Python 版应同样分离"发给模型的最小 schema"与"宿主完整定义"。
2. **输出契约强制化**：每个工具声明结构化输出 schema，执行后统一校验/快照/渲染，非法输出转成模型可见 isError —— Python 版可统一 `(value) -> content` 投影器，保证结果可 JSON 无损序列化。
3. **类型化 schema DSL + 类型推断**：DSL 编译到 JSON Schema 并同时做 TS 类型推断（16 层上限回退）—— Python 版可用 zod/pydantic 类似物实现"一份声明，双端（wire + 类型）同步"。
4. **可扩展执行管道优于内置策略**：pre-execute(allow/deny/ask) → 单调 guard → around-execute → post-execute(accept/block) 的 waterfall，审批、钩子、超时、指标都以监听者接入；guard 只有 deny 结果保证"拒绝不可被监听顺序撤销"。
5. **审批 fail-closed**：`ask` 无回答者即拒绝；`allowed-once` 一次性授权；会话级 `ask/never` 策略可切换并持久化、对模型可见 —— Python 版应提供确定性无提示模式（CI）。
6. **沙箱作为每调用策略而非全局开关**：`sandbox_permissions + justification` 的条件参数表 + 一次性升级审批 + 统一 `[sandbox: …]` 错误标记，让模型学会自行重试而非硬编码。
7. **先读后写（CAS）文件策略**：观察事件（`fs/observed`）+ 写意图事件（createIfAbsent / replaceIfVersion）实现无锁文件安全编辑。
8. **作用域可见性与委派**：全局 + 每 agent scope 分层，`allow/deny` 限制作用于继承面、不触及自身注册 —— 子 agent 委派时保留回报工具，Python 版可用同一规则做 subagent 工具过滤。
9. **并发调度**：`isConcurrencySafe` 纯分类器 + exclusive 屏障 / 有界并行池，策略有序、函数体重叠；取消时未启动调用补合成错误结果保回放完整。
10. **可观测性内建**：tool/call、tool/result、approval/asked、approval/decided 全会话事件化、可回放、模型可见内容与日志一致 —— Python 版应在第一天就把工具调用写进持久化日志。
11. **动态工具与静态工具同管道**：动态工具仅加"入站校验 + 数据克隆 + 能力面收窄"，执行仍走同一管道 —— Python 版插件系统（如注册可执行函数）应复用同一执行管线，避免双轨。
12. **超时协同化**：`timeoutMs` 由工具自声明、经 `tools/execute` wrapper 强制执行且不发给模型 —— Python 版应把超时视为管道关注点而非工具内部细节。
