# MOD Forge V0.1.0 预览版

输入一句话（如「做一个红宝石剑，攻击力 7」），AI 自动写代码、画纹理、编译、测试，交付一个可直接放进 `.minecraft/mods/` 玩的 MOD。全程网页操作，无需写一行代码。

## 快速开始（3 步）

```bat
git clone https://github.com/ZMJJKK123-hub/skill-agent
cd skill-agent
server_app\启动.bat
```

浏览器打开 **http://127.0.0.1:8000** 即可使用（启动.bat 会自动打开）。

> 没有启动.bat？手动两步：
> ```bat
> pip install -r requirements.txt
> cd server_app && python server.py
> ```

## 首次使用（约 1 分钟）

1. 点左下角「⚙️ 设置」→「模型」页，添加一个模型提供方（填 Base URL / 模型名 / API Key），点应用
2. 聊天框输入 `/mod 你的想法`，确认后开始生成

常用模型服务（任选其一）：

| 服务 | Base URL | 模型名示例 |
|---|---|---|
| 智谱 Coding Plan | `https://open.bigmodel.cn/api/coding/paas/v4` | `glm-5.3` / `glm-5.3-flash` |
| DeepSeek 官方 | `https://api.deepseek.com` | `deepseek-chat` |

## 下载你的 MOD

生成完成（绿字「完成 ✓」）后，对话底部出现两个按钮：

- **⬇ 下载 mod jar** → 放进 `.minecraft/mods/` 直接玩
- **⬇ 下载源码 zip** → 完整 Gradle 工程，可继续开发

## 环境要求

Windows 10/11 · JDK 21（`java -version` 显示 21.x）· Python 3.10+

## 遇到问题？

- 提示 API Key 为空 → 服务重启后旧会话不保留 Key，设置里重填即可
- 首次生成较慢 → Gradle 首次下载依赖要几分钟，之后有缓存
- 加作者微信咨询：**lyx525100**（网站首页也有）
