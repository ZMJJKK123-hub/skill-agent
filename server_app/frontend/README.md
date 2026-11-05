# MOD Forge 前端

按功能分区的 React + TypeScript 单页应用。后端接口保持不变。

```text
site/
├── index/                首页 HTML、入口装配与应用壳
├── user_auth/assets/     认证 UI、服务、仓储与类型
├── conversation/assets/  对话 UI、服务、状态、仓储、纯模型与类型
├── settings/assets/      设置 UI、仓储、状态、纯模型与类型
├── session_history/assets/ 历史列表
├── generation/assets/    生成详情
├── games/assets/         小游戏窗口与配置
└── assets/               跨分区配置、类型、HTTP、日志、状态和槽位
```

各功能拥有 `assets/js/` 和 `assets/css/`；模块使用自己的样式入口。共享区只存跨分区能力。类型、业务、存储分文件；组合根显式注入浏览器端口。未启用的导入占位代码已移除。

界面提供深浅主题、响应式侧栏与详情面板，以及本地 SVG 插画和需求示例。示例只填写草稿；输入文本仅保存在内存，刷新清空。字体、图标与插画无需第三方网络资源，动效遵循系统的减少动态效果偏好。

- [整体架构与 API 边界](../../docs/ARCHITECTURE.md)
- [逐文件流程与分支](../../Frontend.md)
- [当前产品范围](SPEC.md)

## 开发与验证

Node 24+，在本目录执行：

```sh
npm ci
npm run dev
npm run check
npm run build
npm run hooks:install
```

开发地址默认 `http://127.0.0.1:5173`；`/api` 和 `/debug` 代理到现有 `http://127.0.0.1:8000`。可通过 `VITE_DEV_API_TARGET` 覆盖开发代理目标；`VITE_API_BASE_URL` 可覆盖客户端 API 基地址，默认同源。无需修改后端端口。

构建仍输出 `server_app/web/index.html` 与哈希 JS/CSS，可由现有 Python 服务直接托管。不要手改构建文件。`npm run hooks:install` 安装仓库本地 pre-push 门禁；本轮更改保持未提交供审查。

## 隔离浏览器回归

```powershell
npm run test:fixture
# 在另一个终端启动前端，代理指向内存夹具：
$env:VITE_DEV_API_TARGET='http://127.0.0.1:8765'
npm run dev -- --port 5174
```

夹具凭据是任意测试文本，不是真实账号/模型 Key。支持登录、历史、普通发送、`question` 多题、`hold` 持续运行、暂停恢复、mod 与产物响应。测试下载只有夹具字节，不是真实可运行模组；生产不会装载夹具。
