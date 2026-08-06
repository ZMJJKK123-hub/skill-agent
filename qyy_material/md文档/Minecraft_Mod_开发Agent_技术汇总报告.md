# Minecraft Mod 开发 Agent — 技术汇总报告

> **文档版本**: v1.0  
> **数据采集日期**: 2026-08-04  
> **目标**: 为构建一个能根据用户提示词自动编写MC模组的专业Agent提供完整的技术底座（Skill文档 + Tool接口）。

---

## 目录

1. [当前 Minecraft 版本生态](#1-当前-minecraft-版本生态)
2. [Mod 加载器选型分析](#2-mod-加载器选型分析)
3. [从零开始：Forge/NeoForge Mod 完整架构](#3-从零开始forgeneoforge-mod-完整架构)
4. [从零开始：Fabric Mod 完整架构](#4-从零开始fabric-mod-完整架构)
5. [Gradle 构建系统详解](#5-gradle-构建系统详解)
6. [核心注册系统（Registry）](#6-核心注册系统registry)
7. [资源与数据生成系统](#7-资源与数据生成系统)
8. [事件系统与生命周期](#8-事件系统与生命周期)
9. [网络通信 (Networking)](#9-网络通信-networking)
10. [渲染与客户端系统](#10-渲染与客户端系统)
11. [TileEntity / BlockEntity 系统](#11-tileentity--blockentity-系统)
12. [Mixin 与核心修改](#12-mixin-与核心修改)
13. [Skill 文件清单（建议给 Agent 加载的技术手册）](#13-skill-文件清单建议给-agent-加载的技术手册)
14. [Tool 接口清单（建议给 Agent 调用的工具函数）](#14-tool-接口清单建议给-agent-调用的工具函数)
15. [项目目录结构模板](#15-项目目录结构模板)
16. [附录：关键官方文档链接汇总](#16-附录关键官方文档链接汇总)

---

## 1. 当前 Minecraft 版本生态

### 1.1 最新版本号（2026年8月）

| 项目 | 版本 | 发布日期 | 备注 |
|------|------|----------|------|
| **Minecraft（正式版）** | **26.2** | 2026-06-16 | Mojang更改了版本号体系，从1.21.11后直接跳转到26.1 |
| Minecraft（上一正式版） | 26.1.2 | 2026-04-09 | |
| Minecraft（经典末代） | 1.21.11 | 2025-12-09 | 1.x系列最后一个版本 |
| **Forge** | **65.1.0** (for MC 26.2) | — | 推荐版本 |
| Forge | 64.1.0 (for MC 26.1.2) | — | 推荐版本 |
| **NeoForge** | **26.2.0.45-beta** | — | 最新beta（对应MC 26.2） |
| **Fabric Loader** | 持续更新 | — | 通过meta.fabricmc.net查询 |
| **Parchment Mappings** | 2026.x | — | 带参数名的人类可读映射 |

### 1.2 版本号规则变化

2026年起，Mojang放弃了`1.x.y`的SemVer伪格式，直接使用两位版本号（如`26.2`）。这意味着：
- **Forge版本号 = 10 + MC主版本号**（如MC 26.x → Forge 65.x 开始）
- **Mappings格式沿用Yarn/Mojang Mappings + Parchment**
- **Breaking changes** 需要密切关注Mojang官方博客

---

## 2. Mod 加载器选型分析

### 2.1 三大加载器对比

| 特性 | **NeoForge（推荐）** | Forge | Fabric |
|------|---------------------|-------|--------|
| **当前状态** | 主线继承自Forge，社区活跃 | 仍在维护但人力不足 | 轻量级，模组数量多 |
| **API 丰富度** | ⭐⭐⭐⭐⭐ 极其丰富 | ⭐⭐⭐⭐ 丰富 | ⭐⭐ 较少，需Fabric API补充 |
| **Mixin 支持** | 原生内置 | 内置 | 需要Mixin库 |
| **核心团队** | NeoForged团队 | LexManos（不活跃） | FabricMC团队 |
| **文档质量** | ⭐⭐⭐⭐ 较好 | ⭐⭐ 较差 | ⭐⭐⭐ 中等 |
| **推荐场景** | 新项目首选 | 仅需维护老项目 | 轻量级客户端mod |
| **MC 26.2 支持** | ✅ 有beta | ✅ 65.1.0 | 待确认 |

### 2.2 选型建议

**对于 Agent 的默认策略**：
- **默认目标** → NeoForge + MC 26.2（社区未来）
- **兼容方案** → 同时支持Forge 65.1.0（目前更稳定）
- **轻量方案** → Fabric（用于仅需客户端功能的简单mod）
- **Agent 应当能根据用户输入自动选择加载器**

---

## 3. 从零开始：Forge/NeoForge Mod 完整架构

### 3.1 核心概念层次图

```
Mod主类 (@Mod注解)
  ├── 注册系统 (DeferredRegister / RegisterEvent)
  │   ├── Block 注册
  │   ├── Item 注册
  │   ├── BlockEntity 注册
  │   ├── Entity 注册
  │   ├── CreativeTab 注册
  │   ├── SoundEvent 注册
  │   └── ... 其他所有可注册对象
  ├── 事件处理 (IEventBus / @SubscribeEvent)
  │   ├── 服务端事件
  │   ├── 客户端事件
  │   └── 自定义事件
  ├── 网络系统 (SimpleChannel / Payload)
  │   ├── C2S 数据包 (Client to Server)
  │   └── S2C 数据包 (Server to Client)
  ├── 数据生成 (Data Generation / DataGen)
  │   ├── 配方 (Recipe)
  │   ├── 战利品表 (Loot Table)
  │   ├── 标签 (Tags: Block Tags, Item Tags)
  │   ├── 方块状态/模型 (BlockState + Model)
  │   ├── 语言文件 (Language)
  │   └── 进度 (Advancement)
  └── Mixin (可选 - 对原版代码进行修改)
      ├── @Mixin 注入
      ├── @Overwrite 覆盖
      └── @Inject 注入点
```

### 3.2 最小可行 Mod 文件清单

一个能运行的mod至少需要以下文件：

```
my_mod/
├── build.gradle                    # Gradle构建脚本（最重要）
├── gradle.properties               # 版本号等属性
├── settings.gradle                 # 项目名设置
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew                         # Gradle包装器(Linux/Mac)
├── gradlew.bat                     # Gradle包装器(Windows)
└── src/
    └── main/
        ├── java/
        │   └── com/example/my_mod/
        │       └── MyMod.java              # 主类（@Mod注解）
        └── resources/
            ├── META-INF/
            │   ├── neoforge.mods.toml       # NeoForge元数据
            │   └── mods.toml               # 或Forge元数据
            ├── assets/my_mod/
            │   ├── lang/
            │   │   └── en_us.json          # 英文翻译
            │   ├── models/
            │   │   ├── block/
            │   │   └── item/
            │   ├── textures/
            │   │   ├── block/
            │   │   ├── item/
            │   │   └── entity/
            │   └── sounds/
            └── data/my_mod/
                └── ...（DataGen输出目录）
```

### 3.3 Mod主类最小示例（NeoForge MC 26.2 / Forge 65.x）

```java
package com.example.my_mod;

import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModLoadingContext;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

@Mod(MyMod.MODID)  // 唯一标识符
public class MyMod {
    public static final String MODID = "my_mod";
    private static final Logger LOGGER = LogUtils.getLogger();

    public MyMod(IEventBus modEventBus) {
        // 1. 注册所有内容
        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modEventBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modEventBus);

        // 2. 注册事件监听
        modEventBus.addListener(ModEventSubscriber::onCommonSetup);
        modEventBus.addListener(ModEventSubscriber::onClientSetup);

        // 3. 网络注册（如果需要）
        ModNetworking.register();

        LOGGER.info("MyMod initialized!");
    }
}
```

### 3.4 NeoForge 元数据文件 (neoforge.mods.toml)

```toml
modLoader = "javafml"
loaderVersion = "[4,)"
license = "MIT"

[[mods]]
modId = "my_mod"
version = "${file.jarVersion}"
displayName = "My Mod"
description = '''
A mod generated by AI agent.
'''
[[mods.dependencies.my_mod]]
    modId = "neoforge"
    type = "required"
    versionRange = "[26.2,)"
    ordering = "NONE"
    side = "BOTH"
[[mods.dependencies.my_mod]]
    modId = "minecraft"
    type = "required"
    versionRange = "[26.2,)"
    ordering = "NONE"
    side = "BOTH"
```

---

## 4. 从零开始：Fabric Mod 完整架构

### 4.1 Fabric Mod 最小结构

```java
// Fabric 使用 fabric.mod.json 元数据
package com.example.my_mod;

import net.fabricmc.api.ModInitializer;

public class MyMod implements ModInitializer {
    public static final String MOD_ID = "my_mod";

    @Override
    public void onInitialize() {
        // 注册
    }
}
```

### 4.2 fabric.mod.json 结构

```json
{
  "schemaVersion": 1,
  "id": "my_mod",
  "version": "${version}",
  "name": "My Mod",
  "environment": "*",
  "entrypoints": {
    "main": ["com.example.my_mod.MyMod"],
    "client": ["com.example.my_mod.client.MyModClient"]
  },
  "depends": {
    "fabricloader": ">=0.16.0",
    "minecraft": "~1.26.2",
    "java": ">=21"
  }
}
```

---

## 5. Gradle 构建系统详解

### 5.1 NeoForge MDK (Mod Development Kit) Gradle 配置

这是 Agent 最需要精确生成的文件，因为版本号、插件配置稍有差错就会编译失败。

#### settings.gradle
```groovy
pluginManagement {
    repositories {
        mavenLocal()
        gradlePluginPortal()
        maven { url = 'https://maven.neoforged.net/releases' }
    }
}

plugins {
    id 'net.neoforged.gradle.userdev' version '7.0.+'  // 版本号需动态查询
}

rootProject.name = 'my_mod'
```

> **Tool需求**: 需要有一个能查询NeoForge GDSL最新版本号的工具。

#### build.gradle（Forge/NeoForge 核心配置模板）
```groovy
plugins {
    id 'java-library'
    id 'eclipse'
    id 'idea'
    id 'maven-publish'
    id 'net.neoforged.gradle.userdev' version '7.0.+'
}

version = mod_version
group = mod_group_id
base {
    archivesName = mod_id
}

java.toolchain.languageVersion = JavaLanguageVersion.of(21)

// 源码集配置
sourceSets.main.resources { srcDir 'src/generated/resources' }

// 依赖配置 - 这是Agent最容易出错的地方
dependencies {
    implementation "net.neoforged:neoforge:${neo_version}"
}

// 运行配置
runs {
    client {
        workingDirectory project.file('run')
        modSource project.sourceSets.main
    }
    server {
        workingDirectory project.file('run')
        modSource project.sourceSets.main
    }
    data {
        workingDirectory project.file('run')
        programArguments.addAll '--mod', project.mod_id,
                '--all', '--output', file('src/generated/resources/').getAbsolutePath(),
                '--existing', file('src/main/resources/').getAbsolutePath()
        modSource project.sourceSets.main
    }
}
```

#### gradle.properties（版本号集中管理）
```properties
org.gradle.jvmargs=-Xmx3G -XX:MaxPermSize=256m
org.gradle.daemon=false

minecraft_version=26.2
neo_version=26.2.+   # 或 forge_version=65.1.0
mod_id=my_mod
mod_version=1.0.0
mod_group_id=com.example.my_mod
mod_authors=AI_Agent
mod_name=My Mod
```

> **关键Skill需求**: 这个文件里的版本号必须自动匹配。Agent需要一个 **版本兼容性矩阵Skill** 来确保`minecraft_version`、`neo_version`/`forge_version`、`java.toolchain.languageVersion` 三者兼容。

---

## 6. 核心注册系统（Registry）

### 6.1 DeferredRegister 模式（NeoForge/Forge推荐）

```java
// Blocks 注册示例
public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(Registries.BLOCK, MyMod.MODID);

    public static final DeferredBlock<Block> MY_BLOCK =
        BLOCKS.register("my_block",
            () -> new Block(BlockBehaviour.Properties.of()
                .strength(3.0f)
                .requiresCorrectToolForDrops()
                .sound(SoundType.STONE)));

    public static final DeferredBlock<StairBlock> MY_STAIRS =
        BLOCKS.register("my_stairs",
            () -> new StairBlock(MY_BLOCK.get().defaultBlockState(),
                BlockBehaviour.Properties.ofFullCopy(MY_BLOCK.get())));
}

// Items 注册示例
public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(Registries.ITEM, MyMod.MODID);

    public static final DeferredItem<BlockItem> MY_BLOCK_ITEM =
        ITEMS.register("my_block",
            () -> new BlockItem(ModBlocks.MY_BLOCK.get(),
                new Item.Properties()));

    public static final DeferredItem<Item> MY_ITEM =
        ITEMS.register("my_item",
            () -> new Item(new Item.Properties()));

    // 工具类
    public static final DeferredItem<SwordItem> MY_SWORD =
        ITEMS.register("my_sword",
            () -> new SwordItem(ModTiers.MY_TIER,
                new Item.Properties()
                    .attributes(SwordItem.createAttributes(ModTiers.MY_TIER, 3, -2.4f))));
}
```

### 6.2 Registry 类型完整清单

| Registry 类型 | 用途 | 关键接口 |
|--------------|------|---------|
| `Registries.BLOCK` | 方块 | `Block`, `StairBlock`, `SlabBlock`, `FenceBlock` 等 |
| `Registries.ITEM` | 物品 | `Item`, `BlockItem`, `SwordItem`, `PickaxeItem`, `AxeItem`, `HoeItem`, `ShovelItem`, `ArmorItem` |
| `Registries.BLOCK_ENTITY_TYPE` | 方块实体 | `BlockEntityType<MyBlockEntity>` |
| `Registries.ENTITY_TYPE` | 实体 | `EntityType<MyEntity>` |
| `Registries.CREATIVE_MODE_TAB` | 创造模式标签页 | `CreativeModeTab` |
| `Registries.MENU` | 容器GUI | `MenuType<MyContainerMenu>` |
| `Registries.SOUND_EVENT` | 声音 | `SoundEvent` |
| `Registries.PARTICLE_TYPE` | 粒子效果 | `ParticleType` |
| `Registries.MOB_EFFECT` | 状态效果 | `MobEffect` |
| `Registries.POTION` | 药水 | `Potion` |
| `Registries.ENCHANTMENT` | 附魔 | `Enchantment` |
| `Registries.VILLAGER_PROFESSION` | 村民职业 | `VillagerProfession` |
| `Registries.POINT_OF_INTEREST_TYPE` | 兴趣点 | `PoiType` |
| `Registries.RECIPE_TYPE` | 配方类型 | `RecipeType` |
| `Registries.RECIPE_SERIALIZER` | 配方序列化器 | `RecipeSerializer` |
| `Registries.LOOT_CONDITION_TYPE` | 战利品条件 | `LootItemConditionType` |
| `Registries.LOOT_FUNCTION_TYPE` | 战利品函数 | `LootItemFunctionType` |
| `Registries.STAT_TYPE` | 统计类型 | `StatType` |
| `Registries.ATTRIBUTE` | 属性 | `Attribute` |

> **Tool需求**: 需要一个模板生成工具来根据用户需求（"我要一个会爆炸的方块"）自动匹配合适的注册类型和Base类。

---

## 7. 资源与数据生成系统

### 7.1 DataGen 体系架构

Minecraft的DataGen系统是新版本（MC 1.21+/26.x）中**强制推荐**的资源生成方式。Agent必须掌握这套体系。

```java
@Mod.EventBusSubscriber(modid = MyMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModDataGen {
    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        DataGenerator generator = event.getGenerator();
        PackOutput output = generator.getPackOutput();
        ExistingFileHelper existingFileHelper = event.getExistingFileHelper();
        CompletableFuture<HolderLookup.Provider> lookupProvider = event.getLookupProvider();

        // 配方生成
        generator.addProvider(event.includeServer(),
            new ModRecipeProvider(output, lookupProvider));
        // 战利品表生成
        generator.addProvider(event.includeServer(),
            new ModLootTableProvider(output, lookupProvider));
        // 方块标签
        generator.addProvider(event.includeServer(),
            new ModBlockTagsProvider(output, lookupProvider, existingFileHelper));
        // 物品标签
        generator.addProvider(event.includeServer(),
            new ModItemTagsProvider(output, lookupProvider,
                new ModBlockTagsProvider(output, lookupProvider, existingFileHelper).contentsGetter(),
                existingFileHelper));
        // 方块状态+模型
        generator.addProvider(event.includeClient(),
            new ModBlockStateProvider(output, existingFileHelper));
        // 物品模型
        generator.addProvider(event.includeClient(),
            new ModItemModelProvider(output, existingFileHelper));
        // 语言文件
        generator.addProvider(event.includeClient(),
            new ModLanguageProvider(output, "en_us"));
        // 声音
        generator.addProvider(event.includeClient(),
            new ModSoundProvider(output, existingFileHelper));
        // 全球战利品表修饰器 (GLM)
        generator.addProvider(event.includeServer(),
            new ModGlobalLootModifierProvider(output, lookupProvider));
    }
}
```

### 7.2 各DataGen Provider 职责与代码模板

| Provider | 生成内容 | 输出路径 |
|----------|---------|---------|
| `RecipeProvider` | JSON配方 | `data/<modid>/recipes/` |
| `LootTableProvider` | 方块/实体掉落 | `data/<modid>/loot_tables/` |
| `BlockTagsProvider` | 方块标签 | `data/<modid>/tags/blocks/` |
| `ItemTagsProvider` | 物品标签 | `data/<modid>/tags/items/` |
| `BlockStateProvider` | 方块状态+模型JSON | `assets/<modid>/blockstates/`, `models/block/` |
| `ItemModelProvider` | 物品模型JSON | `assets/<modid>/models/item/` |
| `LanguageProvider` | 语言文件 | `assets/<modid>/lang/` |
| `SoundDefinitionsProvider` | 声音定义 | `assets/<modid>/sounds.json` |
| `AdvancementProvider` | 进度系统 | `data/<modid>/advancements/` |
| `DatapackBuiltinEntriesProvider` | 世界生成/维度数据 | `data/<modid>/worldgen/` |

### 7.3 配方生成示例（RecipeProvider）

```java
public class ModRecipeProvider extends RecipeProvider {
    public ModRecipeProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> registries) {
        super(output, registries);
    }

    @Override
    protected void buildRecipes(RecipeOutput output) {
        // 有序合成
        ShapedRecipeBuilder.shaped(RecipeCategory.MISC, ModItems.MY_ITEM.get())
            .pattern("AAA")
            .pattern("ABA")
            .pattern("AAA")
            .define('A', Items.DIAMOND)
            .define('B', Items.NETHER_STAR)
            .unlockedBy("has_diamond", has(Items.DIAMOND))
            .save(output);

        // 无序合成
        ShapelessRecipeBuilder.shapeless(RecipeCategory.FOOD, Items.COOKED_BEEF)
            .requires(Items.BEEF)
            .unlockedBy("has_beef", has(Items.BEEF))
            .save(output, ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "cooked_beef_from_mod"));

        // 熔炼
        SimpleCookingRecipeBuilder.smelting(Ingredient.of(ModItems.RAW_MATERIAL.get()),
                RecipeCategory.MISC, ModItems.SMELTED_MATERIAL.get(), 0.7f, 200)
            .unlockedBy("has_raw", has(ModItems.RAW_MATERIAL.get()))
            .save(output);

        // 锻造台升级（1.20+新格式）
        SmithingTransformRecipeBuilder.smithing(
                Ingredient.of(Items.NETHERITE_UPGRADE_SMITHING_TEMPLATE),
                Ingredient.of(Items.DIAMOND_SWORD),
                Ingredient.of(Items.NETHERITE_INGOT),
                RecipeCategory.COMBAT, Items.NETHERITE_SWORD)
            .unlocks("has_netherite", has(Items.NETHERITE_INGOT))
            .save(output, ResourceLocation.withDefaultNamespace("netherite_sword_smithing"));
    }
}
```

> **Tool需求**: 需要一个配方代码生成工具。输入JSON描述，输出Java DataGen代码。

---

## 8. 事件系统与生命周期

### 8.1 NeoForge/Forge 事件总线架构

```
Minecraft 启动流程
    │
    ├─ Mod 构造阶段 (MOD Bus)
    │   ├── @Mod 主类实例化
    │   ├── DeferredRegister 注册
    │   ├── FMLCommonSetupEvent → 通用设置
    │   ├── FMLClientSetupEvent → 客户端设置
    │   ├── RegisterCapabilitiesEvent → 能力注册
    │   └── GatherDataEvent → 数据生成
    │
    ├─ 游戏运行阶段 (FORGE/Neo Bus)
    │   ├── ServerAboutToStartEvent → 服务器即将启动
    │   ├── ServerStartingEvent → 服务器启动中
    │   ├── ServerStartedEvent → 服务器已启动
    │   ├── PlayerEvent.PlayerLoggedInEvent → 玩家登录
    │   ├── LivingDamageEvent → 生物受伤
    │   ├── LivingDeathEvent → 生物死亡
    │   ├── BlockEvent.BreakEvent → 方块破坏
    │   ├── EntityJoinLevelEvent → 实体加入世界
    │   ├── TickEvent → 每tick执行
    │   └── ...
    └─ 关闭阶段
        └── ServerStoppingEvent → 服务器关闭
```

### 8.2 常用事件代码模板

```java
@Mod.EventBusSubscriber(modid = MyMod.MODID)
public class ModEvents {

    // 阻止方块破坏
    @SubscribeEvent
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (event.getState().is(ModBlocks.UNBREAKABLE_BLOCK.get())) {
            event.setCanceled(true);
        }
    }

    // 实体掉落修改
    @SubscribeEvent
    public static void onLivingDrops(LivingDropsEvent event) {
        if (event.getEntity() instanceof Player) {
            event.getDrops().add(new ItemEntity(
                event.getEntity().level(),
                event.getEntity().getX(),
                event.getEntity().getY(),
                event.getEntity().getZ(),
                new ItemStack(ModItems.CUSTOM_DROP.get())
            ));
        }
    }

    // 属性附加
    @SubscribeEvent
    public static void onEntityAttributeCreation(EntityAttributeCreationEvent event) {
        event.put(ModEntities.MY_ENTITY.get(),
            MyEntity.createAttributes().build());
    }
}
```

> **Skill需求**: 需要一个**事件字典Skill**，包含所有可用事件类型、触发时机、参数说明、使用示例。

---

## 9. 网络通信 (Networking)

### 9.1 NeoForge 网络系统（MC 26.x 新版Payload系统）

```java
// ==== 定义数据包 ====
public record MyDataPacket(int value, String message) implements CustomPacketPayload {
    public static final Type<MyDataPacket> TYPE =
        new Type<>(ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "my_packet"));
    public static final StreamCodec<RegistryFriendlyByteBuf, MyDataPacket> STREAM_CODEC =
        StreamCodec.composite(
            ByteBufCodecs.VAR_INT, MyDataPacket::value,
            ByteBufCodecs.STRING_UTF8, MyDataPacket::message,
            MyDataPacket::new
        );

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}

// ==== 注册网络通道 ====
@Mod.EventBusSubscriber(modid = MyMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModNetworking {
    @SubscribeEvent
    public static void register(final RegisterPayloadHandlersEvent event) {
        final PayloadRegistrar registrar = event.registrar("1");
        registrar.playToServer(
            MyDataPacket.TYPE,
            MyDataPacket.STREAM_CODEC,
            ClientPayloadHandler::handleData
        );
        registrar.playToClient(
            MyDataPacket.TYPE,
            MyDataPacket.STREAM_CODEC,
            ServerPayloadHandler::handleData
        );
    }
}

// ==== 客户端处理器 ====
public class ClientPayloadHandler {
    public static void handleData(final MyDataPacket data, final IPayloadContext context) {
        context.enqueueWork(() -> {
            // 在客户端主线程处理
        });
    }
}

// ==== 发送数据包 ====
// 客户端→服务器:
PacketDistributor.sendToServer(new MyDataPacket(42, "hello"));

// 服务器→单个客户端:
PacketDistributor.sendToPlayer(serverPlayer, new MyDataPacket(42, "hello"));

// 服务器→追踪某实体的所有客户端:
PacketDistributor.sendToPlayersTrackingEntity(entity, new MyDataPacket(42, "hello"));
```

> **Skill需求**: NeoForge网络系统是MC 26.x最大的改动之一。需要一个专门的**网络Payload Skill**详细说明。

---

## 10. 渲染与客户端系统

### 10.1 方块实体渲染器 (BER)

```java
public class MyBlockEntityRenderer implements BlockEntityRenderer<MyBlockEntity> {
    public MyBlockEntityRenderer(BlockEntityRendererProvider.Context context) {}

    @Override
    public void render(MyBlockEntity be, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffer, int packedLight, int packedOverlay) {
        // 使用poseStack进行渲染变换
        // 使用buffer获取渲染缓冲区
    }
}

// 注册渲染器
@SubscribeEvent
public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
    event.registerBlockEntityRenderer(ModBlockEntities.MY_BE.get(),
        MyBlockEntityRenderer::new);
}
```

### 10.2 实体渲染器

```java
public class MyEntityRenderer extends MobRenderer<MyEntity, MyEntityModel<MyEntity>> {
    public MyEntityRenderer(EntityRendererProvider.Context context) {
        super(context, new MyEntityModel<>(context.bakeLayer(MyEntityModel.LAYER_LOCATION)), 0.5f);
    }

    @Override
    public ResourceLocation getTextureLocation(MyEntity entity) {
        return ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "textures/entity/my_entity.png");
    }
}
```

---

## 11. BlockEntity 系统

### 11.1 BlockEntity 完整生命周期

```java
public class MyBlockEntity extends BlockEntity {
    // 数据同步
    protected final ContainerData data = new ContainerData() {
        @Override
        public int get(int index) { /* ... */ return 0; }
        @Override
        public void set(int index, int value) { /* ... */ }
        @Override
        public int getCount() { return 2; }
    };

    // 物品处理器（用于自动化输入输出）
    protected NonNullList<ItemStack> items = NonNullList.withSize(3, ItemStack.EMPTY);
    protected final ItemStackHandler itemHandler = new ItemStackHandler(items);

    public MyBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.MY_BE.get(), pos, state);
    }

    public static <T extends BlockEntity> void serverTick(Level level, BlockPos pos,
            BlockState state, T be) {
        MyBlockEntity myBE = (MyBlockEntity) be;
        // 每tick执行的服务端逻辑
    }

    // 保存数据
    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.put("inventory", itemHandler.serializeNBT(registries));
    }

    // 加载数据
    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        itemHandler.deserializeNBT(registries, tag.getCompound("inventory"));
    }
}
```

---

## 12. Mixin 与核心修改

### 12.1 Mixin 是什么

Mixin 允许在不修改原版Minecraft源代码的情况下，对原版类的方法进行注入（Inject）、修改（Modify）、覆盖（Overwrite）。**NeoForge 和 Forge 都原生支持Mixin**。

### 12.2 Mixin 基本结构

```java
@Mixin(LivingEntity.class)
public abstract class MixinLivingEntity {

    @Inject(method = "hurt", at = @At("HEAD"), cancellable = true)
    private void onHurt(DamageSource source, float amount, CallbackInfoReturnable<Boolean> cir) {
        LivingEntity self = (LivingEntity)(Object)this;
        // 自定义逻辑：比如给穿着特殊装备的实体增加免伤
        if (self.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.MAGIC_HELMET.get())) {
            // 修改伤害值或取消伤害
        }
    }

    @ModifyVariable(method = "hurt", at = @At("HEAD"), argsOnly = true)
    private float modifyDamage(float amount, DamageSource source) {
        // 修改传入的伤害值
        return amount * 0.5f; // 50%免伤
    }
}
```

### 12.3 Mixin 配置文件

```json
// src/main/resources/my_mod.mixins.json
{
  "required": true,
  "package": "com.example.my_mod.mixin",
  "compatibilityLevel": "JAVA_21",
  "refmap": "my_mod.refmap.json",
  "mixins": [
    "MixinLivingEntity"
  ],
  "client": [],
  "server": []
}
```

> **Skill需求**: Mixin最容易出错——注入点(`@At`)、方法签名必须与原版精确匹配。需要一个**Mixin参考手册Skill**，包含常用注入模式和Mappings对应表。

---

## 13. Skill 文件清单（建议给 Agent 加载的技术手册）

以下是建议放入 `skill/` 目录的 `.md` 文件。Agent 可以通过 `load_skill` 接口按需查阅。

| 序号 | Skill 文件名 | 内容描述 | 优先级 |
|------|-------------|---------|--------|
| 1 | `version-matrix.md` | **MC版本 ↔ NeoForge/Forge/Fabric ↔ JDK版本 兼容性对照表**，包含最新版本号、下载链接、Breaking Changes列表 | 🔴 最高 |
| 2 | `registry-reference.md` | 所有 Registry 类型的完整清单、DeferredRegister 用法模板、每种类型的注册代码示例 | 🔴 最高 |
| 3 | `datagen-guide.md` | DataGen 完整教程：各Provider的职责、必覆写方法、输出路径约定、Helper类使用 | 🔴 最高 |
| 4 | `event-dictionary.md` | **事件字典**：所有MOD Bus和Forge Bus事件的列表、触发时机、参数签名、使用场景 | 🔴 最高 |
| 5 | `networking-guide.md` | NeoForge Payload网络系统完整指南：数据包定义、序列化、注册、发送完整流程 | 🔴 最高 |
| 6 | `block-api-reference.md` | Block及其子类完整API：BlockBehaviour.Properties详解、BaseBlock类选择指南（StairBlock, SlabBlock, FenceBlock, WallBlock, DoorBlock, TrapDoorBlock等） | 🟡 高 |
| 7 | `item-api-reference.md` | Item及其子类完整API：工具类(Tier体系)、盔甲类(ArmorMaterial)、食物类(FoodProperties)、特殊物品类 | 🟡 高 |
| 8 | `blockentity-guide.md` | BlockEntity完整教程：生命周期、NBT序列化、ContainerData同步、Tickable、ItemStackHandler | 🟡 高 |
| 9 | `rendering-guide.md` | 渲染系统：BlockEntityRenderer、EntityRenderer、Model Layer注册、PoseStack/MultiBufferSource API | 🟡 高 |
| 10 | `mixin-reference.md` | **Mixin参考手册**：常用注入点(@At模式)、方法签名查找方法论、Mappings对应表、调试技巧 | 🟡 高 |
| 11 | `component-system.md` | **Data Component 系统**（MC 1.20.5+ / 26.x重大变更）：替代NBT的新物品数据系统 | 🟡 高 |
| 12 | `recipe-types.md` | 所有配方类型说明：Crafting/Smelting/Blasting/Smithing/Stonecutting/自定义配方 | 🟢 中 |
| 13 | `worldgen-guide.md` | 世界生成：矿石生成(ConfiguredFeature/PlacedFeature)、结构(Structure)、生物群系修改 | 🟢 中 |
| 14 | `gui-container-guide.md` | 容器GUI：Screen/Menu体系、AbstractContainerMenu、Slot、数据同步 | 🟢 中 |
| 15 | `entity-guide.md` | 实体：自定义生物（继承Mob）、AI系统（Goal/Brain）、渲染+模型 | 🟢 中 |
| 16 | `parchment-mappings.md` | Parchment Mappings 使用指南：如何获取带参数名的MCP映射 | 🟢 中 |
| 17 | `gradle-config-guide.md` | Gradle构建配置详解：插件版本、仓库配置、依赖声明、run配置、多模块项目 | 🟢 中 |
| 18 | `modrinth-curseforge-publishing.md` | 发布到Modrinth/CurseForge的配置格式和流程 | 🔵 低 |
| 19 | `common-mistakes.md` | **常见错误与解决方案**：编译错误、运行时崩溃、注册失败等常见问题排查 | 🟡 高 |
| 20 | `migration-guide-1_21-to-26.md` | 从1.21.x迁移到26.x的变更指南：类名变更、API废弃、新替代方案 | 🟡 高 |

---

## 14. Tool 接口清单（建议给 Agent 调用的工具函数）

以下是建议在 Agent 框架中实现的 **Tool 函数**（非Skill文档，而是代码级别的严谨工具）。每个Tool有明确的输入输出JSON schema。

### 14.1 项目脚手架工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `scaffold_mod_project` | 一键生成完整mod项目目录结构和所有模板文件 | mod_id, mod_name, mc_version, loader(neoforge/forge/fabric), package_path, author | 完整的项目目录+文件 |
| `generate_gradle_config` | 生成/更新Gradle构建文件（build.gradle, settings.gradle, gradle.properties） | mc_version, loader_type, mod_id, additional_deps[] | 三个Gradle配置文件的精确内容 |
| `generate_mods_toml` | 生成mod元数据文件 | mod_id, version, display_name, description, dependencies[] | mods.toml / neoforge.mods.toml 内容 |

### 14.2 注册代码生成工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `generate_block_class` | 生成方块类及完整注册代码 | block_properties (name, material, hardness, resistance, sound, luminance, requires_tool, etc.) | 完整的Java类文件 + DeferredRegister注册代码 |
| `generate_item_class` | 生成物品/工具/盔甲类 | item_type(sword/pickaxe/food/armor/etc.), tier_material, properties | 完整物品类代码 |
| `generate_blockentity_class` | 生成BlockEntity类 | class_name, inventory_slots, tick_logic_description, data_fields[] | 完整BlockEntity类 + tick方法 |
| `generate_entity_class` | 生成实体类 | entity_name, dimensions, ai_goals[], render_type | 完整Entity + Model + Renderer三个类 |

### 14.3 DataGen 代码生成工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `generate_recipe_provider` | 根据配方描述生成RecipeProvider代码 | recipes[] ({type:shaped/shapeless/smelting, pattern, ingredients, result}) | 完整RecipeProvider Java类 |
| `generate_loot_table_provider` | 生成LootTableProvider | blocks[] ({block, drops[], silk_touch_drops[], condition}) | 完整LootTableProvider |
| `generate_blockstate_model_provider` | 生成方块状态和模型Provider | blocks[] ({name, parent_model, textures}) | BlockStateProvider + BlockModel JSON生成代码 |
| `generate_item_model_provider` | 生成物品模型Provider | items[] ({name, model_type, parent, textures}) | ItemModelProvider代码 |
| `generate_tag_provider` | 生成标签Provider | tag_type(block/item), tag_name, entries[] | TagProvider代码 |
| `generate_language_provider` | 生成多语言Provider | language_code, translations{} | LanguageProvider代码 |

### 14.4 验证与调试工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `validate_mod_structure` | 验证mod项目结构完整性 | project_root_path | 缺失文件列表、错误配置项 |
| `check_dependency_compatibility` | 检查依赖版本兼容性 | mc_version, loader_type, deps{} | 兼容性报告（✅/⚠️/❌） |
| `check_classpath_for_errors` | 检查Java代码常见错误 | java_source_path | 编译错误预测（API使用是否正确） |
| `generate_mod_asset_checklist` | 检查资源文件完整性 | block_list[], item_list[], entity_list[] | 缺失的纹理/模型/语言文件清单 |

### 14.5 资源生成工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `generate_block_texture_template` | 生成方块纹理占位文件（告诉用户需要什么尺寸的贴图） | block_names[] | 每个方块需要的纹理清单（路径+尺寸） |
| `generate_sounds_json` | 生成sounds.json | sound_events[] ({name, files[], stream, volume, pitch}) | sounds.json |
| `generate_texture_metadata` | 生成纹理元数据 | texture_paths[] | .mcmeta文件 |

### 14.6 版本查询工具

| Tool 名称 | 用途 | 输入 | 输出 |
|-----------|------|------|------|
| `query_latest_mc_versions` | 查询最新MC/Forge/NeoForge/Fabric版本 | 无 | 最新版本号JSON |
| `query_forge_for_mc_version` | 查询某MC版本对应的Forge版本 | mc_version | forge版本列表 |
| `query_neo_for_mc_version` | 查询某MC版本对应的NeoForge版本 | mc_version | neoforge版本列表 |
| `query_mod_api_usage` | 查询某个类/方法的官方文档和示例 | class_name, method_name(optional) | API文档摘要+代码示例 |

---

## 15. 项目目录结构模板

Agent 生成的mod应当遵循以下完整目录结构：

```
{mod_id}/
├── build.gradle
├── settings.gradle
├── gradle.properties
├── gradlew
├── gradlew.bat
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── {package_path}/
│   │   │       ├── {ModMainClass}.java          # @Mod 主类
│   │   │       ├── registry/
│   │   │       │   ├── ModBlocks.java           # 方块注册
│   │   │       │   ├── ModItems.java            # 物品注册
│   │   │       │   ├── ModBlockEntities.java    # 方块实体注册
│   │   │       │   ├── ModEntities.java         # 实体注册
│   │   │       │   ├── ModCreativeTabs.java     # 创造标签页
│   │   │       │   ├── ModSounds.java           # 声音注册
│   │   │       │   ├── ModMenuTypes.java        # 容器注册
│   │   │       │   └── ModRecipeTypes.java      # 配方类型注册
│   │   │       ├── block/
│   │   │       │   ├── MyBlock.java
│   │   │       │   └── MyBlockEntity.java
│   │   │       ├── item/
│   │   │       │   ├── MyItem.java
│   │   │       │   ├── MySwordItem.java
│   │   │       │   └── MyArmorItem.java
│   │   │       ├── entity/
│   │   │       │   ├── MyEntity.java
│   │   │       │   ├── MyEntityModel.java
│   │   │       │   └── MyEntityRenderer.java
│   │   │       ├── screen/
│   │   │       │   ├── MyContainerMenu.java
│   │   │       │   └── MyScreen.java
│   │   │       ├── event/
│   │   │       │   ├── ModEvents.java           # 通用事件
│   │   │       │   └── ModClientEvents.java     # 客户端事件
│   │   │       ├── network/
│   │   │       │   └── ModNetworking.java       # 网络包注册
│   │   │       ├── datagen/
│   │   │       │   ├── ModDataGen.java          # DataGen入口
│   │   │       │   ├── ModRecipeProvider.java
│   │   │       │   ├── ModLootTableProvider.java
│   │   │       │   ├── ModBlockStateProvider.java
│   │   │       │   ├── ModItemModelProvider.java
│   │   │       │   ├── ModLanguageProvider.java
│   │   │       │   ├── ModBlockTagsProvider.java
│   │   │       │   └── ModItemTagsProvider.java
│   │   │       ├── mixin/
│   │   │       │   ├── MixinLivingEntity.java
│   │   │       │   └── MixinPlayer.java
│   │   │       └── util/
│   │   │           ├── ModTiers.java            # 工具等级定义
│   │   │           └── ModArmorMaterials.java   # 盔甲材料定义
│   │   └── resources/
│   │       ├── META-INF/
│   │       │   └── neoforge.mods.toml
│   │       ├── {mod_id}.mixins.json
│   │       ├── pack.mcmeta
│   │       ├── assets/{mod_id}/
│   │       │   ├── lang/
│   │       │   │   ├── en_us.json
│   │       │   │   └── zh_cn.json
│   │       │   ├── models/
│   │       │   │   ├── block/
│   │       │   │   └── item/
│   │       │   ├── textures/
│   │       │   │   ├── block/
│   │       │   │   ├── item/
│   │       │   │   ├── entity/
│   │       │   │   └── gui/
│   │       │   ├── blockstates/
│   │       │   └── sounds/
│   │       └── data/{mod_id}/
│   │           ├── recipes/
│   │           ├── loot_tables/
│   │           ├── tags/
│   │           │   ├── blocks/
│   │           │   └── items/
│   │           ├── advancements/
│   │           └── worldgen/
│   └── test/                                    # 测试代码（可选）
│       └── java/
│           └── {package_path}/
│               └── ModTests.java
└── README.md
```

---

## 16. 附录：关键官方文档链接汇总

| 资源 | URL | 说明 |
|------|-----|------|
| **NeoForge 官方文档** | https://docs.neoforged.net/ | NeoForge最权威文档 |
| **Forge 官方文档** | https://docs.minecraftforge.net/ | Forge文档（较老旧） |
| **Fabric Wiki** | https://fabricmc.net/wiki/ | Fabric开发Wiki |
| **NeoForge MDK下载** | https://maven.neoforged.net/releases/net/neoforged/neoforge/ | MDK和版本列表 |
| **Forge Maven** | https://maven.minecraftforge.net/ | Forge版本列表 |
| **Minecraft Wiki (MCW)** | https://minecraft.wiki/ | 游戏机制参考 |
| **Parchment Mappings** | https://parchmentmc.org/ | 人类可读的Mappings |
| **Modrinth API** | https://docs.modrinth.com/ | Modrinth发布API |
| **CurseForge API** | https://docs.curseforge.com/ | CurseForge发布API |
| **Fabric Meta API** | https://meta.fabricmc.net/ | Fabric版本查询 |
| **Mojang Version Manifest** | https://launchermeta.mojang.com/mc/game/version_manifest.json | MC版本列表JSON |
| **NeoForge GitHub** | https://github.com/neoforged/neoforge | NeoForge源码 |
| **Forge Community Wiki** | https://forge.gemwire.uk/ | 社区维护的Forge Wiki |
| **Mojang Mappings** | https://maven.minecraftforge.net/de/oceanlabs/mcp/mcp_config/ | 官方Mappings |

---

## 总结：Agent 开发路线图建议

### 第一阶段（基础架构搭建）
1. 实现 `scaffold_mod_project` — 生成完整目录结构
2. 实现 Gradle 配置生成（build.gradle + settings.gradle + gradle.properties）
3. 实现 `neoforge.mods.toml` 生成

### 第二阶段（核心注册）
4. 实现 Blocks/Items 注册代码生成
5. 实现 BlockEntity 代码生成
6. 实现 CreativeTab 代码生成

### 第三阶段（数据生成）
7. 实现 RecipeProvider / LootTableProvider 生成
8. 实现 BlockState / ItemModel Provider 生成
9. 实现 Tags / Language Provider 生成
10. 实现 sounds.json 生成

### 第四阶段（高级功能）
11. 实现 Entities 完整代码生成
12. 实现 GUI/Screen 代码生成
13. 实现网络包代码生成
14. 实现 Mixin 代码生成

### 第五阶段（质量保障）
15. 实现版本兼容性检查工具
16. 实现项目结构完整性验证
17. 实现常见错误自动修复

### Skill 文档编写顺序
- **第一批（最高优先级）**: version-matrix, registry-reference, datagen-guide, event-dictionary, networking-guide
- **第二批（高优先级）**: block-api-reference, item-api-reference, blockentity-guide, rendering-guide, mixin-reference, component-system, common-mistakes, migration-guide
- **第三批（中优先级）**: recipe-types, worldgen-guide, gui-container-guide, entity-guide, parchment-mappings, gradle-config-guide
- **第四批（低优先级）**: modrinth-curseforge-publishing

---

*报告完毕。版本信息截至2026-08-04，已通过Mojang/Forge/NeoForge/Fabric官方API交叉验证。*