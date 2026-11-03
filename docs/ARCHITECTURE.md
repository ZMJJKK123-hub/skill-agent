# 前端架构

本轮范围：`server_app/frontend/`、生成的 `server_app/web/` 和前端文档。Python 后端及其 HTTP 接口不修改。

前端采用现有 React + TypeScript，按 `agent.md` 的功能分区方式组织：

```text
server_app/frontend/
├── site/
│   ├── index/               首页入口、应用壳和装配
│   │   ├── index.html
│   │   └── assets/{js,css}/
│   ├── user_auth/assets/    认证界面、认证服务、令牌存储和接口适配
│   ├── conversation/assets/ 对话界面、会话服务、会话状态、接口适配与类型
│   ├── settings/assets/     设置界面、持久化、模型选择与类型
│   ├── session_history/assets/ 会话列表与选择/删除交互
│   ├── generation/assets/   生成详情面板
│   ├── games/assets/        小游戏窗口及其配置
│   └── assets/{js,css}/     仅跨分区使用的配置、契约、HTTP、日志、状态与槽位基础设施
├── tests/                  前端契约、状态机与隔离的浏览器测试数据
├── package.json
├── tsconfig.json
└── vite.config.ts
```

功能分区是当前单页应用中的面板，不新增独立登录页或改变现有导航。页面/面板使用自己的样式入口；Markdown 样式归对话分区。未使用的工作区导入桩与注释备份删除。

依赖方向：页面组件 → 类型化服务接口 → 仓储接口 → HTTP/浏览器存储。类型声明与业务实现、存储实现分别放置。组合根负责创建和注入实例，模块导入不启动轮询、发请求或读取用户存储。

核心契约：

- `StateStore<T>`：获取快照、更新状态、订阅和解绑。
- `HttpClient`：发送既有 `/api/*` 请求，注入 Bearer 令牌、超时与业务异常。
- `SettingsRepository`：读写既有 `modforge_ui` 存储，损坏数据按字段回退并记录诊断。
- `AuthRepository` / `AuthController`：认证请求与登录生命周期；只有明确失效才清理令牌。
- `SessionRepository` / `SessionController`：既有会话、任务、事件、问题和历史接口；服务负责状态转换、轮询和异步结果所属会话校验。
- `Logger`：记录操作标识与错误类别等结构化上下文；失败异常提取脱敏调用堆栈，不记录密码、Key、令牌、提示词和响应正文。

开发使用 Vite 同源代理，默认后端仍为现有 `http://127.0.0.1:8000`；可通过前端开发配置覆盖，不要求修改后端端口。生产仍生成 `server_app/web/index.html`，保留后端 `/` 静态托管方式。

API 契约保持后端现状：`/api/session/reset` 的会话 ID 按后端签名放查询参数，其余端点/载荷字段保持现有名称。前端不得增加后端路由、修改 daemon 或依赖新的后端返回字段。

异步结果按账户和会话世代隔离，切换、退出、暂停后不允许旧请求覆盖当前展示。后端 daemon 模式在创建时固定，显式 `/mod` 从聊天切换时创建新会话；重新生成保留当前会话 ID 和原模式。

迁移门禁：严格类型检查、前端业务与接口契约测试、生产构建、浏览器关键交互、旧路径扫描与后端文件哈希比对。具体文件说明与分支行为单独维护在根目录 `Frontend.md`。
