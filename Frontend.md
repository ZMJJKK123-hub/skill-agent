# Frontend.md

覆盖状态：完整；最后核对：2026-10-30。逐文件说明以当前 site/ 源码为准。

每节以仓库根目录相对路径开头。交互按“触发 → 分支 → 请求 → 展示 → 日志”描述。组件不挂载 window.* 业务接口；状态与动作从当前应用 Context 取得。

开发：Vite 默认 127.0.0.1:5173，同源 /api 和 /debug 代理到现有 127.0.0.1:8000，可用 VITE_DEV_API_TARGET 覆盖。生产：后端继续托管 web/index.html，同源 /api。VITE_API_BASE_URL 可覆盖客户端 API 基地址（不含 /api 后缀）；默认留空。

状态码：401 = 未登录/过期；400 = 输入或请求无效；409 = 正在运行等状态冲突。失败只在对应表单/会话/通知显示，暂时轮询失败保留界面等待重试；装配错误 MissingRoot/MissingApplication/DuplicateSlot 会中断相应挂载。诊断通过本地 modforge:diagnostic 事件提供安全元数据，没有远程日志上传。

## 共享样式引用

- `server_app/frontend/site/assets/css/base.css` — 仅由 index/assets/js/main.tsx 引用。
- `server_app/frontend/site/index/assets/css/index.css` — 仅由 index/assets/js/app-shell.tsx 引用。
- `server_app/frontend/site/user_auth/assets/css/user_auth.css` — 仅由 user_auth/assets/js/auth.view.tsx 引用。
- `server_app/frontend/site/conversation/assets/css/conversation.css` — 仅由 conversation/assets/js/conversation.view.tsx 引用。
- `server_app/frontend/site/settings/assets/css/settings.css` — 仅由 settings/assets/js/settings.view.tsx 引用。
- `server_app/frontend/site/session_history/assets/css/session_history.css` — 仅由 session_history/assets/js/history.view.tsx 引用。
- `server_app/frontend/site/generation/assets/css/generation.css` — 仅由 generation/assets/js/generation.view.tsx 引用。
- `server_app/frontend/site/games/assets/css/games.css` — 仅由 games/assets/js/games.view.tsx 引用。

## server_app/frontend/site/assets/css/base.css

仅由 index/assets/js/main.tsx 引用。

## server_app/frontend/site/assets/js/application-context.tsx

ApplicationProvider 接收 services/children，返回 Provider 元素。useApplication 无参数返回当前服务；未装配抛 MissingApplication。useUi/useSession 无参数返回当前快照，卸载自动解绑；useUiActions 返回 setUi（接收 UiState 补丁、无返回）；useSessionActions/useAuthActions 返回当前控制器，不创建实例、不发请求。没有 window 全局业务接口。

## server_app/frontend/site/assets/js/application.ts

createApplication 接收全部基础端口，返回可注入 React 的服务集合。组装设置仓储和状态 → token/http → session 仓储/状态/服务 → auth 服务 → slots；创建本身不发 HTTP 或启动轮询。任务恢复时 getSettings 无参数返回当前设置与解析后的模型参数。dispose 无参数、无返回，结束会话轮询及主题监听。多个实例不共享内存状态；存储失败由设置/token 仓储回退并记录诊断。

## server_app/frontend/site/assets/js/application.types.ts

ApplicationDependencies 声明存储/fetch/计时器/主题/下载/日志/配置；ApplicationServices 声明 UiStore、SessionStore、SessionController、AuthController、SlotRegistryPort、配置与 dispose。此文件不实例化实现。dispose 无参数、无返回，清理当前实例拥有的资源。

## server_app/frontend/site/assets/js/config.ts

FrontendConfig 是公开配置契约。API_PATHS 登记既有端点。DEFAULT_CONFIG：apiBase 默认为同源；requestTimeoutMs=30000；pollingIntervalMs=2000；toastDurationMs=2000；elapsedTickMs=1000；visibleEventLimit=500；titleLimit=24；设置键 modforge_ui；认证键 modforge_token。官方模型默认 deepseek-v4-flash，可选 deepseek-v4-flash/deepseek-v4-pro，默认 baseUrl=https://api.deepseek.com。计时单位为毫秒，标题/事件限制为字符/条目；凭据不在此配置。

## server_app/frontend/site/assets/js/contracts.ts

跨分区端口声明，无运行逻辑。StateStore.getSnapshot 无参数返回当前快照；set 接收类型化补丁、无返回；subscribe 接收回调、返回解绑函数。StoragePort 接收键/字符串值，读返回字符串或 null，写/删无返回，可抛存储异常。HttpClient.request 接收相对路由/请求选项、返回响应 DTO；download 返回 Blob，失败抛 FrontendError。TimerPort 以毫秒为单位返回句柄；DownloadPort 保存 Blob；ThemePort 应用枚举主题及清理。Logger.write 接收级别、事件名、安全上下文和可选捕获异常，无返回；异常仅由日志器提取脱敏堆栈。

## server_app/frontend/site/assets/js/errors.ts

FrontendError 接收分类、可展示消息和可选 HTTP 状态，返回异常对象，保留 code/status；不触发日志。errorMessage 接收未知异常和回退文案，Error 返回其消息，其他值返回回退文案；errorType 接收未知异常，返回业务 code、Error.name 或 UnknownError。HTTP/服务层据此分支，不记录密码、令牌或请求正文。

## server_app/frontend/site/assets/js/http-client.ts

createHttpClient 接收 fetch、令牌读取器、配置和日志器，返回 HttpClient。request 接收既有路由与 RequestInit，注入当前 Bearer 令牌；字符串正文使用 JSON MIME，2xx JSON 返回 DTO，204/非 JSON 返回 undefined。非 2xx 优先使用字符串 detail，否则状态码文案；错误体非 JSON 仍走状态码回退。网络失败=NetworkError、超时=RequestTimeout、成功响应 JSON 损坏=InvalidResponse。download 接收路由、返回 Blob。请求计时器 finally 清理，失败写 http.request_failed（分类、状态、耗时），不记录 URL 查询、载荷或正文。

## server_app/frontend/site/assets/js/i18n.ts

共享中英文文案。useT 无参数，订阅当前 locale，返回接收文案键并返回字符串的函数：英语命中用英语，缺失回退中文，再缺失返回键本身；不发请求、不打印日志。语言变更由设置状态驱动。

## server_app/frontend/site/assets/js/logger.ts

createLogger 接收日志 sink、非敏感 traceId 和 debug 开关，返回 Logger。write 接收级别、事件、上下文和可选异常，无返回；默认忽略 debug，只复制 operation/scope/status/errorType/durationMs 白名单，附时间和 traceId，再交给 sink。safeStack 接收捕获异常，返回按原顺序排列的调用帧；移除异常正文及 URL 用户名、密码、查询、片段，保留源码行列；非 Error/无调用帧返回 undefined。未传 sink 时无外部输出；浏览器入口使用本地 CustomEvent，测试使用内存数组。没有远程遥测。

## server_app/frontend/site/assets/js/plugin-catalog.ts

PLUGIN_CATALOG 是分区 ID/显示名元数据，供设置列表使用；不导入组件或组合根，避免设置面板与 composition 的运行时依赖环。移除了没有实现的工作区导入桩。

## server_app/frontend/site/assets/js/slot-view.tsx

SlotView 接收槽位名和可选折叠状态，返回对应组件列表。它从 Context 读注册表和 disabledPlugins；已禁用项跳过，设置分区始终可见。用组件挂载保留独立 hooks 生命周期，组件 key 同时包含 pluginId/id。无请求和独立日志；缺 Provider 抛装配异常。

## server_app/frontend/site/assets/js/slots.ts

createSlotRegistry 无参数，返回独立注册表。scope 接收插件名，将后续 inject 固定绑定该名；重名的同所有者/同槽位 ID 抛 DuplicateSlot。entries 接收槽位返回按 order 排序的副本；注销无参数/无返回，只删自己的项，不丢弃后续注册项。SLOTS 是名称唯一来源，没有 currentPluginId 可变全局单例。

## server_app/frontend/site/assets/js/slots.types.ts

SlotProps 仅含可选 collapsed。SlotName 限定已存在的命名槽位。SlotWriter.inject 接收槽位、分区内 ID、React 组件和可选顺序，返回注销函数；SlotRegistryPort.scope 接收 pluginId、返回固定所有者的写入器，entries 接收槽位、返回排序副本。PluginManifest.apply 接收写入上下文，返回 void 或清理函数。类型文件不挂载 UI。

## server_app/frontend/site/assets/js/state-store.ts

createStateStore 接收初始对象，返回互相隔离的 getSnapshot/set/subscribe。set 接收部分状态，浅合并成新快照并通知；旧快照不被原地改写；subscribe 接收监听器、返回幂等解绑动作。没有网络、存储、React 或导入期状态实例。

## server_app/frontend/site/conversation/assets/css/conversation.css

仅由 conversation/assets/js/conversation.view.tsx 引用。

## server_app/frontend/site/conversation/assets/js/conversation.view.tsx

conversationPlugin.apply 接收槽位写入器，挂载 Messages/Composer，无返回。Messages 无参数，空会话显示欢迎页；运行时订阅服务轮询并更新本地计时；事件白名单过滤后按配置截取，回复分组、旧助手文本去重，错误显示在对话底部。卸载清计时器/订阅。

- Composer 无参数返回输入区。send 无参数、无返回：空文本跳过；登录/配置缺失时禁用；/mod 解析需求并显示确认，取消不发送，确认调用 sendPrompt；普通文字调用 chat 动作，已有 mod 由服务保留模式。暂停按钮调用 pauseTask，继续按钮调用 resumeTask；模型选择更新设置。
- QuestionCard 无参数，无问题返回 null；pick 接收题目索引/选项，type 接收索引/文本，更新本地草稿。confirmAll 无参数，提交类型化答案数组；全部回答才启用；失败保留草稿，问题消失后清草稿。
- ChatBubble 接收角色/正文：用户纯文本，助手调用 Markdown。ThinkingGroup 接收思考事件/翻译器，空数组返回 null，点击展开；thinkingName 接收事件/翻译器返回来源名，未知来源用主 Agent 名称。
- ToolCallRow/ToolResultRow/ReplyRow/DividerRow/LogRow 接收单个事件返回展示元素；展开只改本地状态，结果状态决定颜色。EventView 接收事件，按映射选择组件，未知类型回退 LogRow。EmptyState 无参数返回欢迎元素。errMsg 接收未知失败返回展示字符串；下载失败由按钮显示错误。

本文件不直接 fetch 或操作浏览器存储；运行日志由服务发出。缺 Provider 属于入口装配错误。

## server_app/frontend/site/conversation/assets/js/markdown.tsx

Markdown 接收正文与可选 className，返回经过 marked → DOMPurify 的展示元素。空正文按空文本处理；GFM/换行规则在本模块设置，原始 HTML 不绕过清洗。没有网络请求或 window 业务挂载，不单独打印日志。

## server_app/frontend/site/conversation/assets/js/session.model.ts

emptySession 接收可选历史列表返回空闲快照。phaseFromStatus 接收后端状态，暂停优先，其次完成、运行，否则空闲。appendEvents 接收现有/新增事件返回按 ID 去重的新数组。pendingQuestions 接收新旧问题协议，pending 时返回标准问题数组，无问题返回 null。extractFinalReply 接收日志尾部，返回最终标记后的文本；没有标记则跳过工具/思考噪声取末行，无可用内容返回 null。均无 I/O 或全局状态。

## server_app/frontend/site/conversation/assets/js/session.repository.ts

createSessionRepository 接收 HTTP/config 返回仓储；sessionPayload 接收 GenSettings 返回 SessionRequestDTO，无 I/O。create 发 POST /api/session；prepare 发 POST /api/session/mod?session_id；start 发原有任务字段；pause/reset/remove 将 ID 放查询参数。events 接收 ID/可选游标，返回事件和新游标；status/question/conversation 返回既有 DTO；list 返回 sessions。answer 接收 ID、单题答案或多题数组，POST /api/answer；download 接收 ID/产物种类返回 Blob。HTTP 失败不吞掉，统一向服务传播。

## server_app/frontend/site/conversation/assets/js/session.service.ts

createSessionService 接收 SessionDependencies 返回 SessionController。每份实例拥有 revision、账户世代、轮询句柄和 inFlight；任意异步结果写状态前核对所属会话。

- sendPrompt 接收需求、设置、可选模式，返回 Promise<void>：空输入不发送，缺 Key 显示错误；创建中尚无 ID 提示稍候；运行中发原任务接口排队；暂停态 resume=true；新会话先 create，mod 再 prepare，然后 start、poll 和列表刷新。明确从 chat 发起 /mod 新建会话，以兼容后端固定模式 daemon；mod 后续普通文字继续使用 mod。
- pauseTask/resumeTask 无参数，返回 Promise<void>：暂停隔离旧轮询并清理计时器，失败恢复轮询；恢复带当前配置，失败保留暂停及错误。
- poll 无参数，返回当前请求 Promise；同世代重入共享请求。pollOnce 接收当前 ID/世代，依次 events → status → question；去重事件并推进空事件游标，兼容旧最终日志；完成且有 pending 时按既有协议续跑。网络失败记录 warning 供下轮重试；401 停止轮询并显示登录失效。迟到结果直接丢弃。
- loadHistory 无参数返回 Promise<void>，失败保留已有列表；账户已变化则丢弃结果。openHistorySession 接收 ID，清旧展示、恢复对话/模式并探测状态，运行中才恢复轮询；失败写 error。
- answerQuestion 接收单题文本或多题数组，返回 Promise<void>；成功清问题，失败保留问题供重试。
- regenerate 无参数，POST 原 reset；成功清展示但保留 ID 和 chat/mod 模式，失败保留当前信息。deleteSession 接收 ID，成功刷新历史，删除当前选择时清展示，失败显示 error。
- downloadJar/downloadSourceZip 接收 ID，返回 Promise<void>；仓储取 Blob 后交给下载端口，失败向组件传播。
- startPolling 接收可选毫秒，幂等创建计时器，非正数回退配置；stopPolling 无参数、无返回，仅清理计时器。newConversation 无参数，返回 Promise<void>，清当前展示、保留服务器历史。clearAccount 无参数，清展示和历史并隔离旧账户请求；dispose 无参数，清理轮询并拒绝旧结果写回。

状态错误落在对话区；日志 session.operation_failed/session.poll_failed/history.load_failed 只含操作和错误分类，不含提示词和凭据。

## server_app/frontend/site/conversation/assets/js/session.store.ts

createSessionStore 无参数返回独立 SessionStore，初始值来自 emptySession；不读浏览器存储，不发请求，不启动轮询。

## server_app/frontend/site/conversation/assets/js/session.types.ts

定义 chat/mod、阶段枚举、消息、事件、游标、问题、历史、GenSettings 和既有 HTTP DTO。SessionRequestDTO 固定创建请求字段；TaskInput 为类型化业务输入。SessionRepository 约定 create/prepare/start/pause/reset/remove/list/conversation/events/status/question/answer/download 的请求与返回。SessionController 约定界面动作，均由 session.service 实现；状态快照与控制器分开。SessionDependencies 注入所有 I/O 和当前设置读取器，无浏览器实现。

## server_app/frontend/site/games/assets/css/games.css

仅由 games/assets/js/games.view.tsx 引用。

## server_app/frontend/site/games/assets/js/games.config.ts

GAMES 定义当前可选游戏；FORWARD_KEYS 是键盘转发白名单。INIT_W/INIT_H/MIN_W/MIN_H 单位为像素，由小游戏面板消费；未放进跨分区共享配置。

## server_app/frontend/site/games/assets/js/games.view.tsx

GameWindow 无参数，关闭态返回入口，打开态返回浮动窗口与 /debug/game.html?g=... iframe。选择改变游戏，重开增加 nonce；标题拖动接受鼠标事件，窗口移动限制在视口内；尺寸拖动遵守最小值。键盘监听仅打开时启用，输入/选择控件中不转发，其他白名单键发送给已挂载 iframe；关闭/卸载解绑 mouse/keyboard 监听。gamesPlugin.apply 注册浮层，无返回。静态资源由既有 /debug 路径提供，不增加后端路由。

## server_app/frontend/site/generation/assets/css/generation.css

仅由 generation/assets/js/generation.view.tsx 引用。

## server_app/frontend/site/generation/assets/js/generation.view.tsx

GeneratePanel 无参数，订阅当前会话，返回阶段、耗时、模式和截断 ID 的详情面板；无会话显示占位。generatePlugin.apply 接收槽位写入器并挂载 details，无返回。不额外轮询、不请求后端、不打印日志。

## server_app/frontend/site/index/assets/css/index.css

仅由 index/assets/js/app-shell.tsx 引用。

## server_app/frontend/site/index/assets/js/app-shell.tsx

AppShell 无参数，返回三栏与浮层；折叠按钮只改本地宽度，详情按钮只改本地显隐，分区关闭时整栏及分隔线消失。Toast 无参数，通知为空返回 null；非空时按配置延时通过 setUi 清除，卸载取消定时器。依赖应用 Context，缺 Provider 是装配异常；本文件不发请求、不自行打印日志。

## server_app/frontend/site/index/assets/js/browser-adapters.ts

createBrowserAdapters 接收当前 Window/Document，返回 storage、timer、theme、downloads 和 log 端口。storage 的读写异常向仓储传播；theme.apply 接收 system/light/dark，无返回，系统模式跟随媒体查询，dispose 解绑监听。下载端口接收 Blob/文件名，无返回，创建临时链接后释放 URL。计时器端口接收回调/毫秒并返回句柄，清理接收句柄。log 接收安全 LogEntry，发出 modforge:diagnostic 事件；不调用网络。

## server_app/frontend/site/index/assets/js/composition.ts

声明 sidebar → conversation → auth → settings → generate → games 的静态装配顺序。各 apply 接收绑定自身 pluginId 的槽位写入器，无业务返回；不访问后端或用户存储。功能开关只过滤渲染，注册信息仍保留。

## server_app/frontend/site/index/assets/js/main.tsx

页面加载 → 创建浏览器端口、配置、traceId 和应用实例 → 按 composition 注册分区 → Provider 包裹 AppShell。没有 window.* 业务服务挂载。缺 root 节点抛 MissingRoot；HMR/pagehide 的 dispose 无参数、无返回，逆序注销分区并清理 React、主题和轮询。traceId 在 HTTP 环境不支持 randomUUID 时使用非凭据回退。

## server_app/frontend/site/index/index.html

首页唯一 HTML：提供 root 挂载点，加载 index/assets/js/main.tsx；不含认证、任务或存储业务。开发 / 映射此入口，构建导出为 web/index.html。

## server_app/frontend/site/session_history/assets/css/session_history.css

仅由 session_history/assets/js/history.view.tsx 引用。

## server_app/frontend/site/session_history/assets/js/history.view.tsx

sidebarPlugin.apply 接收自身槽位写入器，注册 logo、新对话、历史列表，无返回。新对话调用 newConversation 并更新选择/通知；登录后通过 loadHistory 读取列表，未登录显示提示、空列表显示空态。历史点击传 ID 给 openHistorySession；remove 接收 ID 返回 Promise<void>，先确认，取消不请求，确认调用控制器删除；错误由会话服务展示。折叠时隐藏列表文本；无直接 HTTP、令牌或存储操作。

## server_app/frontend/site/settings/assets/css/settings.css

仅由 settings/assets/js/settings.view.tsx 引用。

## server_app/frontend/site/settings/assets/js/settings.config.ts

VERSIONS 保留 1.21.11/1.21.10/1.21.9；LOADERS 保留 forge/neoforge/fabric。这里只声明已有设置选项，不新增模板或后端加载器实现。

## server_app/frontend/site/settings/assets/js/settings.model.ts

defaultUiState 接收配置返回完整默认值；restoreUiState 接收未知存储值/配置，按字段校验并回退，忽略账户/消息/弹窗恢复，过滤损坏 provider 和不能禁用的设置项。resolveModelConfig 接收 apiKey/model/providers 及公开配置，返回 API Key/baseUrl/model；官方模型用官方地址，自定义命中取提供方，未知模型回退默认。savedSettings 接收完整 UI 快照，返回可持久化投影；其余字段不落盘。所有函数无 I/O。

## server_app/frontend/site/settings/assets/js/settings.repository.ts

createSettingsRepository 接收 StoragePort/键/logger，返回 load/save。load 无参数，合法 JSON 返回未知值供模型校验；损坏 JSON、存储失败返回 null 并发 settings.load_failed。save 接收可持久化设置，无返回，失败发 settings.save_failed；内存设置继续有效。日志不含原始 JSON 和 Key。

## server_app/frontend/site/settings/assets/js/settings.store.ts

createUiStore 接收设置仓储、配置、主题端口，返回 UiStore。显式创建时 load → restore → applyTheme；set 接收类型化补丁，无返回，合并后持久化、按需应用主题、发布快照；设置插件无法被禁用。getSnapshot/subscribe 语义见共享容器。无导入期 localStorage 或 document 访问。

## server_app/frontend/site/settings/assets/js/settings.types.ts

Provider/ModelConfig 定义提供方和模型解析结果；UiState 定义界面/配置快照，SavedSettings 排除用户、当前会话和临时界面态。Locale=zh/en，ThemePref=system/light/dark，SandboxMode=full-access/workspace-write/read-only。SettingsRepository.load 无参数返回未知存储值，save 接收 SavedSettings、无返回；UiStore 使用通用状态契约。SettingsDraft/SectionKey 约束表单与分区选择。

## server_app/frontend/site/settings/assets/js/settings.view.tsx

SettingsPanel 无参数，返回弹窗或 null。打开时复制通用/视觉设置为草稿；apply 无参数、无返回，trim Key 后 setUi 并关闭；cancel 只关闭、不提交通用草稿。GeneralSection/VisionSection 接收草稿及更新回调，返回表单。ModelsSection 的 save/remove 接收表单状态/提供方 ID，名称或模型空不保存，提供方增删立即持久化；插件、语言、外观也即时生效。PluginsSection.toggle 接收插件 ID，设置项锁定。SectionContent 接收 SectionKey/草稿，按映射返回面板。Field 接收标签/children 返回布局；SettingsEntry 接收可选 collapsed，点击打开设置。无独立网络或日志。

## server_app/frontend/site/user_auth/assets/css/user_auth.css

仅由 user_auth/assets/js/auth.view.tsx 引用。

## server_app/frontend/site/user_auth/assets/js/auth.repository.ts

createTokenStore 接收存储、既有 token 键和日志，返回令牌仓储；存储不可用时使用当前页内存，刷新后需重新登录；get/set/clear 失败记录 auth.storage_*，不输出值。createAuthRepository 接收 HttpClient/config，返回 /api/login、/api/register、/api/me、/api/logout 的适配器。登录/注册正文仍为 username/password；仓储不更新 UI，HTTP 失败向服务传播。

## server_app/frontend/site/user_auth/assets/js/auth.service.ts

createAuthService 接收认证仓储/token/UI/会话清理接口/logger，返回认证控制器。login/register 接收用户名/密码、返回 Promise<void>：成功隔离旧账户请求、写 token、发布 user；失败向弹窗传播。restore 无参数，有 token 才 GET /api/me；401/403 清 token 和会话，网络失败保留 token 并显示 toast；晚于退出返回的请求丢弃。logout 无参数，POST /api/logout，失败仍清本地态；旧退出请求不能清新登录账户。事件日志 auth.authenticated、auth.restore_failed、auth.logout_failed 只含安全元数据。

## server_app/frontend/site/user_auth/assets/js/auth.types.ts

User/AuthResult 声明认证响应。AuthRepository.login/register 接收用户名/密码、返回含 token 的响应；me 无参数返回 User；logout 无参数返回 Promise<void>，失败抛标准异常。TokenStore.get 无参数返回 token/null，set 接收 token、clear 无参数，写/清无返回。AuthController 对外登录/注册仅返回 Promise<void>，由服务更新界面；restore/logout 同样无参数。

## server_app/frontend/site/user_auth/assets/js/auth.view.tsx

AuthButton 无参数：挂载调用 restore，显示登录入口或用户名；退出按钮调用 logout。AuthModal 接收关闭回调、返回弹窗；登录/注册切换只改本地状态，用户名/密码空则显示本地错误；submit 无参数、返回 Promise<void>，调用对应认证动作，成功关闭、失败在弹窗显示消息，finally 恢复按钮。表单不接触 localStorage/token，不单独打印日志。

## 开发门禁与回归入口

- `server_app/frontend/vite.config.ts` — 开发首页重写、既有 API/debug 代理与生产根 index.html 导出；不修改 Python 服务。
- `server_app/frontend/tsconfig.json` — strict、无隐式返回/未使用声明检查与类型化导入。
- `server_app/frontend/tests/check-architecture.ts` — 检查分区路径、导入说明、显式函数返回、any、内联导入、原生控制台、业务层浏览器副作用和运行时依赖环；失败以非零退出阻断推送。
- `server_app/frontend/hooks/pre-push` — 安装后依次执行 typecheck 和 check:architecture，任一失败阻断推送。
- `server_app/frontend/tests/application.test.ts` — 应用实例隔离、订阅解绑、槽位所有权与注销。
- `server_app/frontend/tests/http-contract.test.ts` — 当前 HTTP 端点、参数、认证头、多题答案、错误和二进制下载。
- `server_app/frontend/tests/session.test.ts` — 发送/排队/模式切换、暂停恢复、过期异步结果、提问、reset、删除、下载和失败分支。
- `server_app/frontend/tests/settings-auth.test.ts` — 设置损坏回退、自定义模型、存储受限、令牌失效/网络区分和账户生命周期。
- `server_app/frontend/tests/fixture-server.ts` — 仅回环地址内存接口夹具；不写 data/，不调用模型，不导入真实后端。用于浏览器关键操作；关闭进程即丢弃夹具会话。

执行：`npm run check` → `npm run build`。安装本地推送门禁：`npm run hooks:install`。测试脚本使用 Node 原生 TypeScript 支持，要求 Node 24+。
