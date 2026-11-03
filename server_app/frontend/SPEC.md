# 当前前端范围

- 技术：React 18、TypeScript、Vite、Tailwind；保留现有界面和交互。
- 组织：`site/` 按首页、认证、对话、设置、历史、生成、小游戏分区；只有跨分区依赖放共享区。
- 装配：首页组合根创建应用实例，注入存储、HTTP、日志、计时器、主题和下载端口；面板通过类型化 Context 消费。
- 能力：登录/注册/退出、模型与视觉配置、聊天和 /mod、排队、多题回答、暂停恢复、历史、下载、分区开关、中英文、主题及小游戏窗口。
- 后端：继续使用既有 `/api/*` 和 `/debug/*`，不新增或修改 Python 接口。
- 模式：普通文字延续已有 mod 会话；明确从 chat 发起 /mod 时新建 mod 会话，以兼容既有 daemon 固定模式。
- 产物：Vite 仍输出到 `server_app/web/`，根首页仍为 `index.html`。
- 非本轮范围：工作区导入、增加加载器模板、真实模型/Gradle/Minecraft 行为修复。未实现的导入桩和注释备份已经移除。

实现定位见 [Frontend.md](../../Frontend.md)，总体依赖和契约见 [ARCHITECTURE.md](../../docs/ARCHITECTURE.md)，运行方式见 [README.md](README.md)。
