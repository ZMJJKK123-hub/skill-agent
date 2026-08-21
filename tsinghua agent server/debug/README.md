# 8001 Debug / 占位服务

当真实 agent 服务关闭、你在调试代码时，用本目录下的 `debug_server.py`
在 8001 端口启动一个**固定回复占位服务**，清小搭会收到“正在调试中”的提示，
而不是连接失败/超时。

## 启动方式

在项目根目录执行：

```bash
cd "/opt/skill-agent/tsinghua agent server/debug"
nohup /opt/skill-agent/venv/bin/python -m uvicorn debug_server:app --host 0.0.0.0 --port 8001 > /tmp/tsinghua-debug.log 2>&1 &
```

## 可配置

- `TSHINGHUA_API_KEY`（或原来的 `TSINGHUA_API_KEY`）：清小搭凭证，默认 `sk-test-123`
- `DSH_DEBUG_MESSAGE`：自定义返回给清小搭的调试提示语

示例：

```bash
DSH_DEBUG_MESSAGE="系统正在升级维护，请稍后再试" \
  /opt/skill-agent/venv/bin/python -m uvicorn debug_server:app --host 0.0.0.0 --port 8001
```

## 返回内容

- `GET /v1/models`：正常模型列表，保证清小搭连通性探测通过
- `POST /v1/chat/completions`：非流式/流式都返回固定的调试提示文字
- `GET /`：服务状态说明

## 停止

```bash
pkill -f "uvicorn main:app" || true
pkill -f "uvicorn debug_server:app" || true
```

> 注意：真实服务启动命令仍用 `tsinghua agent server/main.py`；本目录只在调试/维护时使用。