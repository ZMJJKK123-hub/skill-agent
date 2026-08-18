---
name: forge-simple-min-mod
description: "最小可运行 Forge 1.21.11 MOD 固定套路：注册物品 + 资源 + GameTest 一键闭环。用于要求『快、能跑、能通过 GameTest、物品注册/渲染可用』的任务。"
whenToUse: "任务是让 MOD 能运行、需要一个简单物品/方块并能通过构建与 GameTest 时。"
---

# Forge 1.21.11 最小可运行 MOD 固定套路

目标：用最少步骤做出一个能构建、能通过 GameTest、物品注册与渲染都正常的 MOD。
已在本机验证：`validate_resources` 0 错误 → `gradlew build` 成功 → `run_test_gametest` All tests passed。

## 0. 命名规则（必须先做）

**禁止保留模板默认名**：`examplemod`、`example_item`、`example_block`、`com.example.examplemod` 只允许出现在示例代码里。

每次生成/修改 MOD 时，必须先根据用户需求确定：
- `modid`（如 `myhero`、`enchantedtools`）
- Java 包名（如 `com.xxx.myhero`）
- 主类名（如 `MyHeroMod`）
- 物品/方块 id（如 `legend_sword`）
- 资源路径、lang key、GameTest namespace 全部跟着 modid/物品名走

并且同步修改：
- `build.gradle` 的 `group`
- `META-INF/mods.toml` 的 `modId` / description
- `src/main/java` 包路径与类名
- `assets/<modid>/...` 与 `data/<modid>/...`
- `src/test` 的包名、类名、`@GameTestNamespace`

## 1. 固定工作流（按顺序，别跳）

```text
1. load_skill（加载本技能 / minecraft-resource-loading）
2. 先调用 activate_test_mode 解锁全部测试工具
3. 写/改代码资源
4. validate_resources → 修复到 0 错误
5. run_mod_test_cycle（内含 build + GameTest）→ 循环修复直到 RESULT: PASS
6. 通过后 git_commit / snapshot 打检查点
```

## 2. 注册一个物品（1.21.11 固定套路）

### 2.1 Java 注册（src/main）
在 Mod 主类注册 Item（可用食物/普通物品均可），例如：

```java
public static final DeferredRegister.Items ITEMS =
    DeferredRegister.createItems(Registries.ITEM, MODID);

public static final Supplier<Item> EXAMPLE_ITEM =
    ITEMS.register("example_item", () -> new Item(new Item.Properties().food(
        new FoodProperties.Builder().nutrition(1).saturationModifier(0.2f).build())));

// Mod 构造器里：
ITEMS.register(bus);
```

### 2.2 物品模型定义（必须！1.21.11 加了这层）
`assets/<modid>/items/example_item.json`：

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<modid>:item/example_item"
  }
}
```

> 没有这层，物品即使注册了也会“模型缺失/不显示”。这是最容易漏的一步。

### 2.3 父模型 + 贴图
`assets/<modid>/models/item/example_item.json`：

```json
{
  "parent": "minecraft:item/generated",
  "textures": { "layer0": "<modid>:item/example_item" }
}
```

贴图必须是 `assets/<modid>/textures/item/example_item.png`（16×16），引用不带 `.png`。

### 2.4 语言文件（必须同时覆盖 en_us + zh_cn，且覆盖所有注册的物品和方块）

`assets/<modid>/lang/en_us.json`：

```json
{
  "item.<modid>.example_item": "Example Item",
  "block.<modid>.example_block": "Example Block"
}
```

`assets/<modid>/lang/zh_cn.json`：

```json
{
  "item.<modid>.example_item": "示例物品",
  "block.<modid>.example_block": "示例方块"
}
```

> 常见坑：只写了 `en_us.json` 的 item 翻译，漏了 `zh_cn.json` 或漏了 block 的翻译键。
> 如果 `zh_cn.json` 缺了某个键，游戏在中文环境下会**回退到英文**，导致同一个 MOD 里既有中文名又有英文名，很混乱。
> 每个注册的 Item 和 Block 必须在两个语言文件里都有对应的条目。

### 2.5 配方（可选，1.21.11 新格式）
`data/<modid>/recipe/example_item.json`：

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": ["I", "S"],
  "key": {
    "I": "minecraft:iron_ingot",
    "S": "minecraft:stick"
  },
  "result": { "id": "<modid>:example_item", "count": 1 }
}
```

> 结果必须是 `{"id": ..., "count": ...}`，原料用字符串 id，不要用旧的 `"item"` 键。

## 3. GameTest（src/test，固定套路）

测试类放 `src/test/java/<pkg>/tests/`，注解 `@GameTestNamespace`，方法加 `@GameTest`，参数用 1.21.11 标准 `GameTestHelper`：

```java
@GameTestNamespace("<modid>")
public class SimpleItemTest {
    @GameTest(template = "empty")
    public static void item_registered(GameTestHelper helper) {
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM,
            ResourceLocation.fromNamespaceAndPath("<modid>", "example_item"));
        if (!helper.getLevel().registryAccess().registryOrThrow(Registries.ITEM).containsKey(key)) {
            helper.fail("example_item 未注册");
        } else {
            helper.succeed();
        }
    }
}
```

> GameTest 放在 src/test，不是 src/main；自检用 `run_test_gametest`，不要用 `run_game_test_server`。

## 4. 常见坑（先查 ERROR_LIST.md）

- 忘写 `items/<name>.json` → 物品不显示。
- 引用写了 `.json` / `.png` → 校验报错。
- 配方结果写成旧格式 → 配方不加载。
- `src/test` 有源码但无 JUnit → `gradlew build` 的 `:test` 失败：模板已加 `failOnNoDiscoveredTests=false`，不要删。
- Paratera 思考模式要求 `assistant` 消息带 `reasoning_content` 回传（agent.py 已修，别回退）。

## 5. 完成后检查

- `validate_resources` → 0 errors / 0 warnings
- `build_mod_jar_forge` → BUILD SUCCESSFUL，`dist/*.jar` 存在
- `run_test_gametest` → All required tests passed
- item 的 items/、models/item/、textures/item/、lang 齐全 → 渲染可用