---
name: forge-event-dictionary
description: Forge 事件字典：常用 Forge/Mod 事件及监听用法
---

# Forge 事件字典

> **加载器**: Forge 65.x (MC 26.2)  
> **用途**: Agent 需要处理自定义行为时查询可用事件。

---

## 事件总线注册

```java
// MOD Bus 事件
modEventBus.addListener(MyHandler::onCommonSetup);

// Forge Bus 事件（游戏运行时）
MinecraftForge.EVENT_BUS.register(MyForgeEvents.class);
```

---

## MOD Bus 事件（初始化阶段）

| 事件 | 触发时机 | 常用场景 |
|------|---------|---------|
| `FMLCommonSetupEvent` | Mod通用初始化 | 注册Capability、网络包 |
| `FMLClientSetupEvent` | 客户端初始化 | 注册KeyBinding、渲染器 |
| `RegisterCapabilitiesEvent` | Capability注册 | 注册Capability |
| `GatherDataEvent` | DataGen | 数据生成入口 |
| `EntityAttributeCreationEvent` | 实体属性 | 注册实体属性 |
| `RegisterMenuScreensEvent` | GUI注册 | 客户端Screen绑定 |
| `RegisterRenderersEvent` | 渲染器注册 | EntityRenderer, BER |

---

## Forge Bus 事件（游戏运行时）

### 玩家/实体事件

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| `AttackEntityEvent` | 玩家攻击实体 | 攻击粒子特效 |
| `LivingHurtEvent` | 生物受伤(可取消) | 盔甲免伤效果 |
| `LivingDamageEvent` | 伤害计算后(不可取消) | 伤害记录 |
| `LivingDeathEvent` | 生物死亡 | 自定义死亡逻辑 |
| `LivingDropsEvent` | 生物掉落 | 修改掉落物 |
| `LivingEntityUseItemEvent.Start` | 开始使用物品 | — |
| `LivingEntityUseItemEvent.Tick` | 使用物品中 | 粒子效果 |
| `LivingEntityUseItemEvent.Finish` | 使用物品完成 | 食物粒子 |
| `PlayerEvent.PlayerLoggedInEvent` | 玩家登录 | 初始物品 |
| `LivingFallEvent` | 摔落 | 免摔落伤害 |
| `EntityJoinLevelEvent` | 实体加入世界 | 实体初始化 |

### 方块事件

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| `BlockEvent.BreakEvent` | 方块破坏 | 阻止破坏 |
| `BlockEvent.EntityPlaceEvent` | 方块放置 | 放置限制 |
| `BonemealEvent` | 骨粉使用 | 自定义骨粉 |
| `RightClickBlock` | 右键方块 | 自定义交互 |

### Tick事件

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| `TickEvent.ServerTickEvent` | 每tick | 定时任务 |
| `TickEvent.PlayerTickEvent` | 玩家每tick | 持续效果 |
| `TickEvent.LevelTickEvent` | 世界每tick | 世界逻辑 |

### 渲染事件（客户端）

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| `RenderLivingEvent.Pre/Post` | 生物渲染 | 渲染修改 |
| `RenderGuiOverlayEvent` | GUI渲染 | HUD添加 |
| `InputEvent.Key` | 按键 | 快捷键 |
