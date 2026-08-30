# 马拉松复杂 MOD 验证记录（2026-08-31）

> 每项均通过三重验证：构建（jar 产出）+ GameTest（逻辑断言）+ 实际可玩性（隐形客户端内真实操作 + 截图识图）。
> 运行环境：glm-5.3（智谱 Coding Plan）、Forge 1.21.11-61.2.0、完全后台模式（窗口隐身/函数级点击/游戏内截图）。

## celestialheaven-1.0.0.jar — 天国维度（全新维度生成）

| 验证项 | 结果 |
|---|---|
| 构建 | 61 文件 jar：dimension + dimension_type + **noise_settings（自定义噪声）** + biome + configured_feature 完整链 |
| GameTest | 4/4 通过（方块/物品注册、传送逻辑） |
| 服务端 | GameTestServer 无 datapack 错误（agent 修复 3 处 worldgen JSON 结构错误后达成） |
| 可玩性 | 隐形客户端内 `/execute in celestialheaven:heaven run tp` 传送成功；3 次识图（最终判定 Yes） |
| git 快照 | a7baf7ae |

## storm-1.0.0.jar — 风暴要塞维度 + Boss 实体（实体/AI/渲染）

| 验证项 | 结果 |
|---|---|
| 构建 | 64 文件 jar：维度链 + `StormLordEntity`/`StormLordRenderer`/`StormCitadelClient`（客户端渲染注册）+ 刷怪蛋 |
| GameTest | 全绿（Boss 血量/属性/受击/掉落断言） |
| 可玩性 | 隐形客户端内进入维度 → `/summon storm:storm_lord` → **Boss 血条渲染（识图确认 "Storm Lord" 紫色血条）** → 实体贴图无缺失 → **近战 AI 生效（Boss 击杀了测试玩家，出现死亡界面——AI 与伤害系统铁证）** |
| 轮次 | 150 轮硬顶正常收尾（含 8 次编译迭代：实体 API 签名坑） |

## 已知限制

- Boss 模型在截图中未居中入镜（视角/距离问题，非渲染缺失——贴图检查正常）
- 风暴之心掉落物未入镜验证（Boss 死亡位置不在石台）
- glm-5.3 在超大上下文下会出现连续空响应（引擎已有 5 次压缩/8 次收尾兜底）

## 引擎侧配套修复（本轮马拉松沉淀）

- 空响应连续上限（`ac31fc68`）、鼠标左右键键名（`05b93161`）、MAX_TOTAL_ROUNDS=150 硬顶实战生效
- AgentBridge 服务端 dist 守卫、jar 排除 bridge 类（`4672e3f0`）

## stardustenergy-1.0.0.jar — 星尘能源（多系统联动：BlockEntity + 能量传输 + 物品充能）

| 验证项 | 结果 |
|---|---|
| 构建 | 55 文件 jar：`StardustGeneratorBlockEntity`（燃料→能量）/`EnergyCollectorBlockEntity`（跨方块接收）双方块实体 + 能量水晶 |
| GameTest | 通过：塞燃料 tick 推进 → 聚能器能量 >0（跨方块传输断言）→ 水晶充能 NBT 断言 |
| 可玩性 | 隐形客户端内放置方块组、发放充能水晶（含 custom_data Charge 组件验证 1.21.11 物品 NBT 写法）、背包截图识图；**客户端日志零 missing texture/model 警告**（权威渲染证据） |
| 已知限制 | 方块远景截图未能入镜（相机角度），以 GameTest 能量断言 + 客户端零警告为准确认 |
