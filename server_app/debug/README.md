# 8000 网页维护占位页

当 8000 网页服务（server_app）停止运行时，用户访问 `http://49.232.37.238:8000/`
会看到这个维护页面，而不是白屏或 502。

## 功能

- 精美暗色 UI（终端风格）
- 随机维护提示文案
- **模拟终端**：输入 help / ping / sudo fix-bug / matrix 等命令
- **贪吃蛇**：吃「📦 版本更新包」长大
- **打砖块**：砖块排列成 UPDATING，打掉弹"已修复 1 个 Bug"
- **2048**：方块显示为 v1.0→v5.0→MAX 版本升级
- **消灭 Bug**：Bug 从角落爬出，点击拍扁计分 + 连击
- **Konami 秘技**：↑↑↓↓←→←→BA → 全屏礼花特效
- **自动探活**：每 15 秒检查 /api/health，恢复后自动跳转首页
- 右上角静音开关（默认静音）
- 全部本地化，零网络依赖

## 部署方式

`index.html` + `css/` + `js/` 一起部署即可（多文件结构，资源路径已用 `<base href="/debug/">` 锚定，
从 `/`、`/debug`、`/debug/` 或 Nginx 502 内部重写等任意路径返回都能正确加载资源）。

### 方式 0：server_app 内建兜底（已实现，无需配置）

`server.py` 已内置三层兜底，主页异常时用户永远落进这个游乐场而不是白屏/裸 404：

1. `/` 路由：`web/index.html` 缺失时直接返回 debug 维护页；
2. 全局 404 处理器：非 `/api/*`、非 `/debug/*` 的未知页面路径全部返回 debug 维护页（API 保持 JSON 404 语义不变）；
3. `/api/health` 健康检查：页面每 15 秒探活，服务恢复后自动跳回主页。

### 方式 1：Nginx 静态托管

```nginx
server {
    listen 80;
    server_name 49.232.37.238;

    location / {
        # 8000 正常时反向代理到 server_app
        proxy_pass http://127.0.0.1:8000;
        # 8000 挂了时返回 debug 页面
        error_page 502 503 504 /debug/index.html;
    }

    location /debug/ {
        alias /opt/skill-agent/server_app/debug/;
    }
}
```

### 方式 2：直接访问

```
http://49.232.37.238:8000/debug/index.html
```

如果 server_app 没有对 `/debug/` 做路由，可以手动加：

```python
# server_app/server.py 里加一行
app.mount("/debug", StaticFiles(directory="debug", html=True), name="debug")
```

### 方式 3：8000 挂了时手动替换

把 `index.html` 放到 Nginx 的默认 502 页面路径。

## 自定义

- 修改 `MAINT_MSGS` 数组可更换维护提示文案
- 修改 `HEALTH_URL` 可更换健康检查接口
- 修改 `HOME_URL` 可更换恢复后跳转地址
- 修改 `POLL_INTERVAL` 可调整检查频率

## 技术栈

- 纯 HTML + CSS + Vanilla JS
- 无框架、无构建步骤、无外部 CDN
- 文件大小约 20KB
- 支持 PC 和移动端