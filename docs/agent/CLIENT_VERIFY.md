# Client Verification (Required for Entity/Item-Icon MODs)

> 独立指导文件：当 MOD 包含“自定义实体渲染”或“物品图标”，只跑 `run_mod_test_cycle` 不充分。
> `run_test_gametest` 是**纯服务端**，永远不会发现客户端渲染崩溃/图标缺失。

## 何时必须做客户端验证

至少满足以下任一条件时，**必须**执行客户端验证，否则不得宣布完成：
- 注册了任何自定义 `EntityType`
- 注册了任何自定义刷怪蛋/物品图标
- 引用了任何客户端渲染器 / 客户端模型 / 客户端贴图

## 标准验证流程（固定的 Run 序列）

```text
1. 先通过 run_mod_test_cycle（服务端 build + GameTest）
2. 启动真实客户端：
     start_mc_client 或 run_client
3. 等待客户端就绪：
     wait_for_mc_ready  / wait_for_screen
4. 召唤/生成每一个自定义实体：
     send_game_command "summon skyforge:sky_golem ~ ~1 ~"
     send_game_command "summon skyforge:skyforge_guardian ~ ~1 ~"
5. 等待 3~5 秒让实体渲染：
     screenshot
6. 视觉验证截图：
     analyze_image / verify_visual_loop
     确认：不是 purple/black，不是隐形/崩溃，实体出现且贴图正常
7. 检查客户端崩溃：
     读取 crash-reports/ 下最新的 crash-*.txt 和 latest.log
     确认没有新增异常
8. 检查刷怪蛋物品栏图标：
     打开物品栏/创造模式，screenshot 确认图标是自定义贴图
9. 只有以上全部通过，才算完成
```

## 常见客户端问题（已记录在 ERROR_LIST）

- 实体没有 `EntityRenderers.register(...)` → 客户端渲染时 `entityrenderer is null` 闪退
- 刷怪蛋 `items/*.json` 指向默认模板但没有自定义贴图 → 显示默认/缺失图标
- 客户端类在公共代码里被直接引用 → 专用服务器加载时报 `DEDICATED_SERVER` 错误
- `HumanoidRenderState`/`MobRenderer` 泛型参数错 → 编译报 `createRenderState/getTextureLocation` 找不到

## 硬件/资源警告（重要）

- 启动 Minecraft Forge 客户端需要**独立 JVM + 2GB 以上内存**，通常建议 4GB+。
- 在 2GB 内存的服务器上同时跑：
  - agent 服务
  - Minecraft 服务端
  - Minecraft 客户端
  几乎必然 OOM/卡死。
- **不要把客户端跑到低配服务器上**。正确做法：
  - 在本地桌面/游戏电脑上运行客户端验证；
  - 服务器只负责 build + GameTest + 产生 jar；
  - 完成后由用户在本地安装 jar 做实际客户端验证，或由有条件的机器执行本流程。

## 用户禁止自动启动客户端时的处理（重要）

- 如果当前运行环境是服务器，或用户明确表示“不要在本机自动启动 Minecraft 客户端/服务端弹窗”，则：
  - **不得调用** `runClient` / `start_mc_client` / `run_client` / `runServer`。
  - 客户端验证退化为“资源/静态检查”：`validate_resources`、PNG 文件有效性、item 模型/JSON 引用完整性、无缺失纹理路径。
  - 在最终总结中明确标注：“真实客户端渲染未在此环境启动，由用户本地手动验证。”