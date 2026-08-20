# Tsinghua Agent Server（清小搭接入服务）

这个文件夹是一个独立的 **OpenAI 兼容 HTTP 服务**，专门用于把本项目 `skill-agent` 的
自研 Agent 引擎（`core/agent.py` 的 `agent_loop()`）接入清小搭智能体广场。

它**不替代** `server_app/` 里的网站。`server_app/` 是你的网页前端；本文件夹是给清小搭
探测/试聊用的 API 服务。

> 端口约定（已按需求解耦）：
> - `8000` 端口：运行 `server_app/server.py`，打开你自己的网页。
> - `8001` 端口：运行本服务，只提供清小搭 OpenAI 兼容接口，不再挂载网页。

---

## 1. 这个服务实现了什么

清小搭接入要求你的服务提供两个端点：

| 端点 | 说明 |
|---|---|
| `GET /v1/models` | 连通性 + 凭证校验 |
| `POST /v1/chat/completions` | 对话，支持非流式 JSON 和流式 SSE |

本服务还实现了：

- Bearer Token 鉴权（也兼容 `x-api-key`）
- 清小搭探测的 `max_tokens:1` 快速通道，避免探测超时
- `sessionId` 会话支持
- 流式帧规范：`role` 帧 → `content` 帧 → `stop` 帧 → `data: [DONE]`
- **文件产物下载（L2 attachments）**：agent 生成的 zip/jar/pdf/图片/文档等会收集到 `x_soda.attachments`，通过 `GET /files/{path}` 公网下载
- **文件/图片输入**：`file` / `image_url` 的 OSS URL 会自动下载到工作区 `inputs/`，agent 可用 `read_file` 等工具读取
- **流式思考（L1 reasoning）**：`core/agent.py` 收到模型 `reasoning_content` 时实时转发为 `delta.reasoning`，清小搭可显示“思考中”
- **对话结尾引导**：回复末尾提示用户可访问网页版 `http://49.232.37.238:8000/`（可用环境变量 `DSH_WEB_URL` 覆盖）
- **按 sessionId 隔离会话**：每个清小搭 `sessionId` 使用独立工作目录 `.runtime/sessions/<sessionId>/`，对话历史/断点/事件不串号

---

## 2. 目录结构

```
tsinghua agent server/
├── main.py        # FastAPI 服务本体
└── README.md      # 本说明
```

### 2.1 新增的文件能力

| 能力 | 说明 |
|---|---|
| `GET /files/{path}` | 公网下载 agent 生成的可交付文件；路径相对于服务工作区 `.runtime/` |
| `x_soda.attachments` | agent 运行结束后自动收集本次新生成的可交付文件（zip/jar/pdf/图片/文档等），非流式放在响应顶层，流式放在 stop 帧 |
| `file` / `image_url` 输入 | 清小搭传来的 OSS URL 会自动下载到 `.runtime/inputs/`，agent 通过 `read_file` 等工具读取 |
| 流式思考 `delta.reasoning` | `core/agent.py` 实时回调 reasoning，流式响应中转发为 `reasoning` 帧 |
| 对话结尾提示 | 自动追加“完整功能见网页版”的提示，可用 `DSH_WEB_URL` 修改地址 |

> 可配置环境变量：
> - `DSH_PUBLIC_BASE_URL`：附件 `fileUrl` 的公开基地址（默认取当前请求的 base_url）
> - `DSH_WEB_URL`：回复末尾引导用户访问的网页地址（默认 `http://49.232.37.238:8000/`）

---

## 3. 本地运行

### 3.1 前提

- 项目根目录的 `.env` 里已有 `DEEPSEEK_API_KEY`（或你设置环境变量）
- 已安装依赖：`pip install -r requirements.txt`
- 本服务接入密钥：默认 `sk-test-123`，用环境变量 `TSINGHUA_API_KEY` 覆盖

### 3.2 启动

在项目根目录执行：

```powershell
cd "tsinghua agent server"
..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001
```

看到类似输出即成功：

```text
Uvicorn running on http://0.0.0.0:8001
```

### 3.3 本地自测

用 PowerShell 或 Git Bash 执行下面命令，把 `BASE`/`KEY` 换成你的。

```bash
BASE="http://127.0.0.1:8001/v1"
KEY="sk-test-123"

# 1) /models
curl -i "$BASE/models" -H "Authorization: Bearer $KEY"

# 2) 非流式
curl -s -X POST "$BASE/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'

# 3) 流式
curl -N -X POST "$BASE/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"stream":true,"max_tokens":1,"messages":[{"role":"user","content":"你好"}]}'

# 4) 错误凭证应返回 401
curl -i "$BASE/models" -H "Authorization: Bearer wrong-key"
```

自检清单：

- [ ] `/v1/models` 返回 200
- [ ] 错误密钥返回 401
- [ ] 非流式响应含 `choices[0].message.content`
- [ ] 流式响应含 `data: [DONE]`
- [ ] `max_tokens:1` 的探测请求能快速返回

---

## 4. 清小搭平台信息怎么填

当你的服务已经部署到公网后，在清小搭接入向导中填：

| 字段 | 填什么 |
|---|---|
| 智能体平台 | 标准协议接入 |
| API 地址 | `https://你的域名/v1` 或 `http://你的公网IP:8001/v1` |
| API 密钥 | 你在服务端设置的 `TSINGHUA_API_KEY` |
| 鉴权方式 | Bearer Token |
| 流式终止符 | `[DONE]` |
| usage 位置 | stop 帧内 |

> 注意：`baseUrl` 要填到 `/v1`，因为清小搭会拼 `baseUrl + /chat/completions` 和
> `baseUrl + /models`，它不会帮你去重 `/v1`。

---

## 5. 云服务器 + 公网 IP 部署教程

### 5.1 你需要理解的概念

- **云服务器（ECS/CVM）**：你租的一台一直开机的远程电脑，有公网 IP。
- **公网 IP**：互联网上别人访问你这台机器的地址，类似你家的门牌号。
- **安全组/防火墙**：云服务器上的“门禁”，默认只开少数端口；你想让清小搭访问 8001 端口，必须放行。
- **域名（可选）**：公网 IP 不好记，可以买域名解析到 IP；不买域名也能用 IP 接入，但 HTTPS 通常需要域名。

### 5.2 租服务器时怎么选

建议最低配置：

| 项 | 建议 |
|---|---|
| 云厂商 | 阿里云 / 腾讯云 / 华为云 均可 |
| 系统 | Ubuntu 24.04（省钱、稳定）或 Windows Server（和你本地环境更接近） |
| 配置 | 2 核 4G 起 |
| 带宽 | 1~3M 够用（对话 API 流量不大） |
| 安全组 | 放行 TCP 8001（或 80/443） |

### 5.3 拿到云服务器后的部署步骤（Linux 示例）

```bash
# 1) 登录服务器（在你本地终端）
ssh root@你的公网IP

# 2) 安装 Python 和 git
apt update
apt install -y python3 python3-venv python3-pip git

# 3) 上传/克隆项目
# 可以把本地 skill-agent 压缩后 scp 上去，或 git clone 你的仓库
cd /opt
git clone https://github.com/ZMJJKK123-hub/skill-agent.git
cd skill-agent

# 4) 创建虚拟环境并装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5) 设置密钥
export TSINGHUA_API_KEY="给清小搭用的密钥"
export DEEPSEEK_API_KEY="你的大模型 API Key"

# 6) 启动服务
cd "tsinghua agent server"
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### 5.4 安全组/防火墙放行

在你的云厂商控制台找到“安全组”或“防火墙”，添加入站规则：

- 协议：TCP
- 端口：8001
- 来源：0.0.0.0/0（表示允许所有人访问；如果你只想自己测试，也可填你的 IP）

### 5.5 用公网 IP 自测

在你本地电脑执行：

```bash
curl http://你的公网IP:8001/v1/models -H "Authorization: Bearer 你的密钥"
```

能返回 JSON 就说明公网访问通了。

### 5.6 建议：长期运行用 systemd

不要用 `nohup` 裸跑，建议写一个 systemd 服务，开机自启、崩溃自动重启。

```bash
sudo tee /etc/systemd/system/tsinghua-agent.service > /dev/null <<'EOF'
[Unit]
Description=Tsinghua Agent Server
After=network.target

[Service]
WorkingDirectory=/opt/skill-agent/tsinghua agent server
Environment=TSINGHUA_API_KEY=xxx
Environment=DEEPSEEK_API_KEY=xxx
ExecStart=/opt/skill-agent/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now tsinghua-agent
sudo systemctl status tsinghua-agent
```

### 5.7 是否需要域名和 HTTPS？

- 清小搭文档说支持 `HTTP/HTTPS`，所以**测试阶段用 `http://公网IP:8001/v1` 也能试**。
- 但正式上架/稳定使用建议用 HTTPS。常见方式：
  1. 买一个域名，解析 A 记录到你的公网 IP；
  2. 用 Nginx/Caddy 做反向代理 + 自动 HTTPS 证书；
  3. 或保留 `http://IP:8001/v1`，先跑通再说。

---

## 6. 常见问题

### 6.1 探测连通性红叉
- 检查安全组是否放行 8001；
- 检查服务是否真的在运行；
- 检查 `baseUrl` 是否填到 `/v1`。

### 6.2 凭证红叉
- 确认填的密钥等于服务端 `TSINGHUA_API_KEY`；
- 确认鉴权方式选的是 Bearer Token。

### 6.3 最小对话红叉
- 用 3.3 的 curl 先本地自测；
- 如果 `agent_loop` 跑太慢，探测会超时；
- 本服务已对 `max_tokens:1` 做快速通道，正常应能通过。

### 6.4 为什么我不需要改 `server_app/` 网站？
清小搭只需要 OpenAI 兼容 API。你的网页是给人看的，这个服务是给清小搭看的，两者互不干扰。

---

## 7. 后续可扩展

当前版本是“最快能接上”的版本。如果想体验更好，可以继续加：

- 真正的逐 token 流式输出（从 `agent_loop` 内部把流式 token 转发出来）
- `delta.reasoning` 真实思考过程
- 图片输入：拉取 `image_url` 并接入视觉模型
- 文件输入/附件输出：实现 `x_soda.attachments`
- 高并发：每个 `sessionId` 对应一个独立子进程，避免全局单例冲突