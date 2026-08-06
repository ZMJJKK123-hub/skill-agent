# Fabric Agent — Skill 与 Tool 需求明细表

> **版本**: v2.0 | **日期**: 2026-08-04 | **加载器**: Fabric (MC 26.2 → Fabric Loader + Fabric API 0.156.0)  
> **定位**: 按元素类型逐个拆解——Agent 生成每种东西需要创建哪些文件、依赖哪些Skill文档、调用哪些Tool函数。  
> **注意**: Fabric 与 Forge/NeoForge 是**完全不同的生态**，几乎每个环节都有差异。

---

## Fabric vs Forge/NeoForge 全局差异概览

| 维度 | **Fabric** | **Forge/NeoForge** |
|------|-----------|-------------------|
| **核心理念** | 轻量、模块化、用Mixin修改原版 | 重型、API丰富、用事件系统扩展 |
| **Mod入口** | `implements ModInitializer` 接口 | `@Mod` 注解 + 构造器 |
| **元数据文件** | `fabric.mod.json` (JSON格式) | `mods.toml` / `neoforge.mods.toml` (TOML格式) |
| **Gradle插件** | `fabric-loom` | `net.neoforged.gradle.userdev` / `net.minecraftforge.gradle` |
| **Mixin** | **核心机制**，几乎所有mod都用Mixin | 内置但非必须 |
| **注册系统** | 直接使用 `Registry.register()`（原版Registry） | `DeferredRegister` 辅助类 |
| **网络系统** | 底层 `PacketByteBuf` + `ServerPlayNetworking` | `SimpleChannel` / `Payload` |
| **事件系统** | **无内置事件系统**，用Mixin+回调 | 完整的 MOD Bus + Forge Bus 双层事件 |
| **能力系统** | **无Capability**，用Cardinal Components API（第三方） | Forge有Capability |
| **渲染API** | Fabric Rendering API（需要显式依赖） | 内置 |
| **必需依赖** | **Fabric API**（几乎所有mod都依赖） | 无强制第三方依赖 |
| **DataGen** | 无官方DataGen，手动写JSON | 完整的DataGen系统 |
| **MC 26.2** | Fabric API 0.156.0+26.2 支持 | Forge 65.1.0 / NeoForge 26.2.0.45-beta 支持 |

> **关键结论**: Fabric的代码量和概念比Forge/NeoForge**更少但更底层**。Agent需要掌握的API更多来自Minecraft原版（`net.minecraft.*`），而非加载器提供。Fabric API作为补充库承担了Forge中很多内置功能。

---

## 目录

- [0. 全局基础：Fabric项目脚手架](#0-全局基础fabric项目脚手架)
- [1. 简单物品 (Item)](#1-简单物品-item)
- [2. 方块 (Block)](#2-方块-block)
- [3. 工具 (Sword / Pickaxe / Axe / Shovel / Hoe)](#3-工具)
- [4. 盔甲 (Armor)](#4-盔甲-armor)
- [5. 食物 (Food)](#5-食物-food)
- [6. 方块实体 (BlockEntity)](#6-方块实体-blockentity)
- [7. 容器/GUI (ScreenHandler + Screen)](#7-容器gui-screenhandler--screen)
- [8. 实体/生物 (Entity)](#8-实体生物-entity)
- [9. 粒子效果 (Particle)](#9-粒子效果-particle)
- [10. 声音 (Sound)](#10-声音-sound)
- [11. 状态效果 (StatusEffect)](#11-状态效果-statuseffect)
- [12. 附魔 (Enchantment)](#12-附魔-enchantment)
- [13. 世界生成 (Ore/Feature/Biome)](#13-世界生成-orefeaturebiome)
- [14. 网络数据包 (Networking)](#14-网络数据包-networking)
- [15. Mixin（Fabric核心）](#15-mixinfabric核心)
- [16. Fabric特有API（Rendering / Object Builder / etc.）](#16-fabric特有apirendering--object-builder--etc)
- [17. 纹理/图片资源生成](#17-纹理图片资源生成)
- [18. Skill文档完整清单（Fabric版）](#18-skill文档完整清单fabric版)
- [19. Tool接口完整清单（Fabric版）](#19-tool接口完整清单fabric版)
- [20. Fabric vs Forge/NeoForge 元素对照表](#20-fabric-vs-forgeneoforge-元素对照表)

---

## 0. 全局基础：Fabric项目脚手架

### 0.1 Fabric 全局文件清单

```
my_fabric_mod/
├── build.gradle                    # Fabric Loom 构建（完全不同于Forge）
├── settings.gradle                 # 项目名+插件仓库
├── gradle.properties               # 版本号
├── gradle/wrapper/
│   ├── gradle-wrapper.jar
│   └── gradle-wrapper.properties
├── gradlew / gradlew.bat
└── src/
    └── main/
        ├── java/
        │   └── {package_path}/
        │       ├── MyMod.java                      # 主类 implements ModInitializer
        │       ├── MyModClient.java                # 客户端入口 implements ClientModInitializer
        │       ├── registry/
        │       │   ├── ModBlocks.java
        │       │   ├── ModItems.java
        │       │   ├── ModBlockEntities.java
        │       │   ├── ModEntities.java
        │       │   ├── ModSounds.java
        │       │   └── ...
        │       ├── mixin/                          # Mixin配置
        │       │   └── MixinExample.java
        │       └── network/
        │           └── ModNetworking.java
        └── resources/
            ├── fabric.mod.json                     # Fabric元数据（JSON！）
            ├── {mod_id}.mixins.json                # Mixin配置文件
            ├── assets/{mod_id}/
            │   ├── lang/en_us.json
            │   ├── models/block/ & item/
            │   ├── textures/
            │   ├── blockstates/
            │   └── sounds/
            └── data/{mod_id}/
                ├── recipes/
                ├── loot_tables/
                ├── tags/
                └── ...
```

### 0.2 Fabric build.gradle

```groovy
plugins {
    id 'fabric-loom' version '1.7-SNAPSHOT'  // 注意：用fabric-loom，不是neoforge userdev
    id 'maven-publish'
}

version = project.mod_version
group = project.maven_group

base {
    archivesName = project.archives_name
}

repositories {
    // Fabric特有的附加仓库
}

dependencies {
    // Fabric Loom会自动下载Minecraft
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    mappings "net.fabricmc:yarn:${project.yarn_mappings}:v2"  // Fabric用Yarn Mappings
    modImplementation "net.fabricmc:fabric-loader:${project.loader_version}"

    // Fabric API（几乎所有Fabric mod都依赖）
    modImplementation "net.fabricmc.fabric-api:fabric-api:${project.fabric_version}"
}

processResources {
    inputs.property "version", project.version
    filteringCharset "UTF-8"
    filesMatching("fabric.mod.json") {
        expand "version": project.version
    }
}

loom {
    runs {
        client {
            client()
            name "Minecraft Client"
        }
        server {
            server()
            name "Minecraft Server"
        }
    }
}
```

### 0.3 gradle.properties（Fabric版）

```properties
org.gradle.jvmargs=-Xmx2G

minecraft_version=26.2
yarn_mappings=26.2+build.1           # Yarn mappings版本（需动态查询）
loader_version=0.16.+                # Fabric Loader版本
fabric_version=0.156.0+26.2          # Fabric API版本
mod_version=1.0.0
maven_group=com.example
archives_name=my_fabric_mod
```

> **Skill必需**: `gradle-config-guide-fabric.md` — **新建**：Fabric Loom Gralde配置、Yarn Mappings版本选择、Fabric API版本匹配。

### 0.4 fabric.mod.json（核心元数据！）

```json
{
  "schemaVersion": 1,
  "id": "my_fabric_mod",
  "version": "${version}",
  "name": "My Fabric Mod",
  "description": "A fabric mod generated by AI agent.",
  "authors": ["AI_Agent"],
  "contact": {},
  "license": "MIT",
  "icon": "assets/my_fabric_mod/icon.png",
  "environment": "*",
  "entrypoints": {
    "main": [
      "com.example.my_fabric_mod.MyMod"
    ],
    "client": [
      "com.example.my_fabric_mod.MyModClient"
    ],
    "fabric-datagen": [
      "com.example.my_fabric_mod.datagen.ModDataGen"
    ]
  },
  "mixins": [
    "my_fabric_mod.mixins.json"
  ],
  "depends": {
    "fabricloader": ">=0.16.0",
    "minecraft": "~26.2",
    "java": ">=21",
    "fabric-api": ">=0.156.0"
  },
  "suggests": {
    "another-mod": "*"
  }
}
```

> **Skill必需**: `fabric-mod-json-spec.md` — **新建**：fabric.mod.json的完整格式（entrypoints类型、depends/suggests/conflicts/breaks语义）。

### 0.5 Fabric Mod主类

```java
package com.example.my_fabric_mod;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MyMod implements ModInitializer {  // 实现接口，不是@Mod注解！
    public static final String MOD_ID = "my_fabric_mod";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        // Fabric中没有IEventBus，直接调用静态初始化
        ModBlocks.register();    // 在static方法中完成注册
        ModItems.register();
        ModBlockEntities.register();
        ModEntities.register();
        ModSounds.register();
        ModNetworking.register();

        LOGGER.info("MyMod initialized!");
    }
}
```

```java
// 客户端入口
package com.example.my_fabric_mod;

import net.fabricmc.api.ClientModInitializer;

public class MyModClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        // 客户端专用初始化
        ModBlockEntities.registerRenderers();
        ModEntities.registerRenderers();
        ModScreens.register();
    }
}
```

> **核心差异**: Fabric 没有事件总线的概念。初始化是线性的——`onInitialize()` 执行完后mod就启动完毕。需要"事件"的场景用 **Mixin 注入**代替。

### 0.6 必需的 Skill

| Skill | 备注 |
|-------|------|
| `gradle-config-guide-fabric.md` | **新建**：Fabric Loom配置 |
| `fabric-mod-json-spec.md` | **新建**：fabric.mod.json完整格式 |
| `yarn-mappings-guide.md` | **新建**：Yarn Mappings命名规范（与Mojang Mappings/Parchment的对应关系） |
| `fabric-api-overview.md` | **新建**：Fabric API各模块说明（哪些功能需要哪个Fabric API子模块） |

### 0.7 必需的 Tool

| Tool | 说明 |
|------|------|
| `scaffold_mod_project` | 需支持 `loader=fabric`，生成Fabric版完整目录 |
| `generate_gradle_config` | 需支持Fabric Loom |
| `generate_fabric_mod_json` | 生成fabric.mod.json |
| `query_latest_mc_versions` | 查询Fabric Loader + Fabric API版本 |

---

## 1. 简单物品 (Item)

### 1.1 注册方式（关键差异！）

```java
public class ModItems {
    // Fabric 直接使用原版Registry.register()
    public static final Item MY_ITEM = register(
        "my_item",
        new Item(new Item.Settings())  // 注意: Fabric用Item.Settings，不是Item.Properties
    );

    private static Item register(String name, Item item) {
        return Registry.register(Registries.ITEM,
            Identifier.of(MOD_ID, name), item);
    }

    public static void register() {
        // 空方法，仅为了触发静态初始化（类加载时static块/字段初始化自动完成注册）
    }
}
```

> **对比**:
> - Forge/NeoForge: `DeferredRegister.create(Registries.ITEM, MODID)` → `ITEMS.register("name", () -> ...)`
> - Fabric: 直接 `Registry.register(Registries.ITEM, id, item)` + 静态字段

### 1.2 物品模型JSON — 与Forge完全相同

模型和纹理是Minecraft原生的资源包规范，**不依赖加载器**。

### 1.3 配方JSON — 完全相同

### 1.4 物品组（创造标签页）

```java
// Fabric 物品组注册
public static final ItemGroup MY_TAB = FabricItemGroup.builder()
    .icon(() -> new ItemStack(ModItems.MY_ITEM))
    .displayName(Text.translatable("itemGroup.my_fabric_mod.my_tab"))
    .entries((displayContext, entries) -> {
        entries.add(ModItems.MY_ITEM);
        entries.add(ModBlocks.MY_BLOCK.asItem());
    })
    .build();

// 在注册时:
Registry.register(Registries.ITEM_GROUP,
    Identifier.of(MOD_ID, "my_tab"), MY_TAB);
```

> **Fabric特有**: `FabricItemGroup`（来自Fabric API），比Forge的`CreativeModeTab`更简洁。

### 1.5 需要的 Skill（Fabric版）

| Skill | 说明 |
|-------|------|
| `item-api-reference-fabric.md` | Fabric版Item API（Item.Settings vs Item.Properties） |
| `registry-reference-fabric.md` | Fabric注册方式（Registry.register直接注册） |
| `fabric-item-group-api.md` | FabricItemGroup用法 |
| `item-model-spec.md` | 与Forge共用 |

### 1.6 需要的 Tool（Fabric版）

| Tool | 说明 |
|------|------|
| `generate_fabric_item_registration` | 生成Registry.register代码 |
| `generate_fabric_item_group` | 生成FabricItemGroup |
| `generate_item_model_json` | 共用 |
| `describe_item_texture` | 共用 |
| `generate_recipe_json` | 共用 |

---

## 2. 方块 (Block)

### 2.1 注册方式

```java
public class ModBlocks {
    public static final Block MY_BLOCK = register(
        "my_block",
        new Block(AbstractBlock.Settings.create()  // Fabric用AbstractBlock.Settings
            .strength(3.0f)
            .requiresTool()
            .sounds(BlockSoundGroup.STONE)),
        true  // 是否自动创建BlockItem
    );

    private static Block register(String name, Block block, boolean shouldRegisterItem) {
        Identifier id = Identifier.of(MOD_ID, name);
        // 如果有BlockItem自动注册
        if (shouldRegisterItem) {
            Registry.register(Registries.ITEM, id, new BlockItem(block, new Item.Settings()));
        }
        return Registry.register(Registries.BLOCK, id, block);
    }

    public static void register() {} // 触发类加载
}
```

### 2.2 六个面纹理生成 — **与Forge完全相同**

Blockstate JSON、模型JSON、纹理资源 → 全部是Minecraft原生规范，**不依赖加载器**。

### 2.3 掉落表

```json
// data/{mod_id}/loot_tables/blocks/my_block.json
// 格式与Forge完全相同
```

### 2.4 方块标签

```json
// data/{mod_id}/tags/blocks/mineable/pickaxe.json
// 格式与Forge完全相同
```

> **重要**: 方块在Minecraft中的资源格式（模型、纹理、掉落表、标签、配方）是原版规范，**三种加载器完全通用**。

### 2.5 需要的 Skill

Fabric版额外需要：
- `registry-reference-fabric.md` — Fabric注册方式
- 其余（block-api-reference、blockstate-spec、block-model-spec）与Forge共用，但API类名可能有小差异（`AbstractBlock.Settings` vs `BlockBehaviour.Properties`）

---

## 3. 工具

与Forge**核心逻辑相同**（都继承原版SwordItem等），差异：

| 差异点 | Fabric | Forge/NeoForge |
|--------|--------|---------------|
| Tier注册 | 直接在SwordItem构造时传入自定义Tier | 需要在DeferredRegister中注册 |
| 攻击事件 | 用**Mixin注入**代替事件监听 | 用`AttackEntityEvent`事件 |
| 属性修改 | `Item.Settings.attributeModifiers()` | 一致 |

### 3.1 攻击时粒子效果（Fabric方式 = Mixin）

```java
// Fabric没有事件系统，用Mixin注入
@Mixin(PlayerEntity.class)
public class MixinPlayerEntity {
    @Inject(method = "attack", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/entity/Entity;damage(...)"), locals = LocalCapture.CAPTURE_FAILHARD)
    private void onAttack(Entity target, CallbackInfo ci) {
        PlayerEntity self = (PlayerEntity)(Object)this;
        if (self.getMainHandStack().isOf(ModItems.DRAGON_TOOTH_SWORD)) {
            // 生成粒子
            self.getWorld().addParticle(...);
        }
    }
}
```

> **Skill必需**: `mixin-reference-fabric.md` — Mixin注入替代事件系统的完整指南。

---

## 4. 盔甲 (Armor)

### 4.1 Fabric盔甲注册

```java
// Fabric方式注册盔甲
public static final Item DRAGON_SCALE_HELMET = register(
    "dragon_scale_helmet",
    new ArmorItem(
        ModArmorMaterials.DRAGON_SCALE,
        ArmorItem.Type.HELMET,  // MC 1.20.5+ / 26.x 新API
        new Item.Settings().maxDamage(ArmorItem.Type.HELMET.getMaxDamage(33))
    )
);
```

layer_1/layer_2纹理 → **与Forge完全相同**。

---

## 5. 食物 (Food)

```java
// Fabric方式
public static final Item MAGIC_CAKE = register(
    "magic_cake",
    new Item(new Item.Settings()
        .food(new FoodComponent.Builder()
            .nutrition(8)
            .saturationModifier(12.0f)
            .statusEffect(
                new StatusEffectInstance(StatusEffects.SPEED, 100, 1), 1.0f)
            .build()))
);
```

### 5.1 食物粒子效果（Fabric = Mixin）

```java
@Mixin(LivingEntity.class)
public class MixinLivingEntity {
    @Inject(method = "eatFood", at = @At("HEAD"))
    private void onEatFood(World world, ItemStack stack, CallbackInfoReturnable<ItemStack> cir) {
        if (stack.isOf(ModItems.MAGIC_CAKE)) {
            // 食物碎屑粒子
            LivingEntity self = (LivingEntity)(Object)this;
            for (int i = 0; i < 8; i++) {
                self.getWorld().addParticle(...);
            }
        }
    }
}
```

> **Fabric替代方案**: 如果不想写复杂Mixin，可以用Fabric API提供的 `ItemStackEvents` 等回调（需要Fabric API特定模块）。

---

## 6. 方块实体 (BlockEntity)

### 6.1 Fabric BlockEntity 注册

```java
public class ModBlockEntities {
    public static final BlockEntityType<MyBlockEntity> MY_BE = Registry.register(
        Registries.BLOCK_ENTITY_TYPE,
        Identifier.of(MOD_ID, "my_be"),
        BlockEntityType.Builder.create(MyBlockEntity::new, ModBlocks.MY_BLOCK).build()
    );

    public static void register() {}

    // 客户端注册渲染器
    public static void registerRenderers() {
        BlockEntityRendererRegistry.register(MY_BE, MyBlockEntityRenderer::new);
    }
}
```

BlockEntity类本身的逻辑（tick, NBT, ItemStackHandler）→ **与Forge相同**。

### 6.2 物品槽同步

Fabric使用 `ImplementedInventory` 接口（Fabric API提供），比Forge的 `ItemStackHandler` 更简洁：

```java
public class MyBlockEntity extends BlockEntity implements ImplementedInventory {
    private final DefaultedList<ItemStack> items = DefaultedList.ofSize(3, ItemStack.EMPTY);

    @Override
    public DefaultedList<ItemStack> getItems() { return items; }
    // ImplementedInventory 自动提供 getStack, setStack, getMaxCountPerStack 等
}
```

> **Skill必需**: `fabric-inventory-api.md` — **新建**：ImplementedInventory接口、SidedInventory、Storage（Fabric Transfer API）。

---

## 7. 容器/GUI (ScreenHandler + Screen)

### 7.1 Fabric方式

```java
// ScreenHandler（Fabric命名，不是Menu）
public class MyScreenHandler extends ScreenHandler {
    // 逻辑与Forge的AbstractContainerMenu一致
    public MyScreenHandler(int syncId, PlayerInventory playerInventory) {
        super(ModScreenHandlers.MY_SCREEN_HANDLER, syncId);
        // 添加槽位
        this.addSlot(new Slot(inventory, 0, 80, 35));
        addPlayerInventory(playerInventory);
        addPlayerHotbar(playerInventory);
    }
}

// 注册
public static final ScreenHandlerType<MyScreenHandler> MY_SCREEN_HANDLER =
    Registry.register(
        Registries.SCREEN_HANDLER,  // Fabric用SCREEN_HANDLER，Forge用MENU
        Identifier.of(MOD_ID, "my_screen_handler"),
        new ScreenHandlerType<>(MyScreenHandler::new, FeatureFlags.VANILLA_SET)
    );

// 客户端注册Screen
public static void register() {
    HandledScreens.register(MY_SCREEN_HANDLER, MyScreen::new);
}
```

> **术语差异**: Forge叫 `MenuType` + `AbstractContainerMenu` + `Screen`；Fabric叫 `ScreenHandlerType` + `ScreenHandler` + `HandledScreen`。

### 7.2 GUI纹理

与Forge完全相同（256×256 PNG）。

### 7.3 需要的 Skill（Fabric版）

| Skill | 说明 |
|-------|------|
| `fabric-screen-handler-guide.md` | **新建**：Fabric ScreenHandler体系（术语与Forge不同） |
| `fabric-inventory-api.md` | **新建**：ImplementedInventory |

---

## 8. 实体/生物 (Entity)

### 8.1 Fabric实体注册

```java
public class ModEntities {
    public static final EntityType<MyEntity> MY_ENTITY = Registry.register(
        Registries.ENTITY_TYPE,
        Identifier.of(MOD_ID, "my_entity"),
        EntityType.Builder.create(MyEntity::new, SpawnGroup.CREATURE)
            .dimensions(0.6f, 1.8f)
            .build()
    );

    public static void register() {}

    // 注册属性 + 渲染器
    public static void registerAttributes() {
        FabricDefaultAttributeRegistry.register(MY_ENTITY, MyEntity.createMobAttributes());
    }
    public static void registerRenderers() {
        EntityRendererRegistry.register(MY_ENTITY, MyEntityRenderer::new);
    }
}
```

### 8.2 刷怪蛋

```java
// Fabric刷怪蛋
public static final Item MY_ENTITY_SPAWN_EGG = Registry.register(
    Registries.ITEM,
    Identifier.of(MOD_ID, "my_entity_spawn_egg"),
    new SpawnEggItem(MY_ENTITY, 0x123456, 0x789ABC, new Item.Settings())
);
```

### 8.3 实体模型 + 渲染器 + AI — 与Forge完全相同

EntityModel的Java代码定义、EntityRenderer继承体系、GoalSelector AI → 全部是原版Minecraft规范。

> **Skill必需**: Fabric版实体guide与Forge共用entity-model-guide/entity-rendering-guide/entity-ai-guide。

---

## 9. 粒子效果 (Particle)

```java
public class ModParticles {
    public static final ParticleType<MyParticleEffect> MY_PARTICLE = Registry.register(
        Registries.PARTICLE_TYPE,
        Identifier.of(MOD_ID, "my_particle"),
        FabricParticleTypes.complex(MyParticleEffect::createCodec, MyParticleEffect::createPacketCodec)
    );

    // 客户端注册Provider
    public static void registerFactories() {
        ParticleFactoryRegistry.getInstance().register(MY_PARTICLE, MyParticle.Factory::new);
    }
}
```

粒子类本身（Particle子类、纹理、行为）→ **与Forge完全相同**。

---

## 10. 声音 (Sound)

```java
public class ModSounds {
    public static final SoundEvent MY_SOUND = Registry.register(
        Registries.SOUND_EVENT,
        Identifier.of(MOD_ID, "my_sound"),
        SoundEvent.of(Identifier.of(MOD_ID, "my_sound"))
    );
    public static void register() {}
}
```

sounds.json → **与Forge完全相同**。

---

## 11. 状态效果 (StatusEffect)

```java
public class ModEffects {
    public static final StatusEffect MY_EFFECT = Registry.register(
        Registries.STATUS_EFFECT,
        Identifier.of(MOD_ID, "my_effect"),
        new MyStatusEffect(StatusEffectCategory.HARMFUL, 0x9900FF)
    );
    public static void register() {}
}
```

Effect图标 (18×18 PNG) → **与Forge完全相同**。

---

## 12. 附魔 (Enchantment)

Fabric附魔注册与Forge类似的 `Registry.register` 方式。API差异在MC 26.x中趋于统一。

---

## 13. 世界生成 (Ore/Feature/Biome)

### 13.1 Fabric世界生成

Fabric使用 **Fabric Biome API** 来添加矿石生成和生物群系修改：

```java
// 矿石生成
public class ModWorldGen {
    public static void register() {
        BiomeModifications.addFeature(
            BiomeSelectors.foundInOverworld(),
            GenerationStep.Feature.UNDERGROUND_ORES,
            RegistryKey.of(Registries.PLACED_FEATURE,
                Identifier.of(MOD_ID, "my_ore"))
        );
    }
}
```

`configured_feature` 和 `placed_feature` JSON 格式 → **与Forge完全相同**（原版数据包规范）。

> **Skill必需**: `fabric-worldgen-guide.md` — **新建**：Fabric BiomeModifications API（不同于NeoForge的biome_modifier JSON）。

---

## 14. 网络数据包 (Networking)

### 14.1 Fabric网络（底层PacketByteBuf）

```java
public class ModNetworking {
    public static final Identifier SYNC_PACKET_ID = Identifier.of(MOD_ID, "sync_packet");

    public static void register() {
        // 服务端接收
        ServerPlayNetworking.registerGlobalReceiver(SYNC_PACKET_ID,
            (server, player, handler, buf, responseSender) -> {
                int data = buf.readVarInt();
                server.execute(() -> {
                    // 在服务端主线程处理
                });
            });

        // 客户端接收
        ClientPlayNetworking.registerGlobalReceiver(SYNC_PACKET_ID,
            (client, handler, buf, responseSender) -> {
                int data = buf.readVarInt();
                client.execute(() -> {
                    // 在客户端主线程处理
                });
            });
    }

    // 发送到服务端
    public static void sendToServer(int data) {
        PacketByteBuf buf = PacketByteBufs.create();
        buf.writeVarInt(data);
        ClientPlayNetworking.send(SYNC_PACKET_ID, buf);
    }

    // 发送到客户端
    public static void sendToPlayer(ServerPlayerEntity player, int data) {
        PacketByteBuf buf = PacketByteBufs.create();
        buf.writeVarInt(data);
        ServerPlayNetworking.send(player, SYNC_PACKET_ID, buf);
    }
}
```

> **对比**:
> - Forge: `SimpleChannel` + `encode/decode/handle` 静态方法
> - NeoForge: `CustomPacketPayload` Record + `StreamCodec`
> - Fabric: 最底层 —— 直接读写 `PacketByteBuf`，无类型包装

> **Skill必需**: `networking-guide-fabric.md` — **新建**：Fabric网络API（PacketByteBuf + ServerPlayNetworking/ClientPlayNetworking）。

---

## 15. Mixin（Fabric核心）

Fabric mod中Mixin**几乎是必需品**（不像Forge中是可选的）。

### 15.1 Mixin配置

```json
// src/main/resources/my_fabric_mod.mixins.json
{
  "required": true,
  "package": "com.example.my_fabric_mod.mixin",
  "compatibilityLevel": "JAVA_21",
  "mixins": [
    "MixinLivingEntity",
    "MixinPlayerEntity",
    "MixinServerWorld"
  ],
  "client": [
    "MixinTitleScreen"
  ],
  "injectors": {
    "defaultRequire": 1
  }
}
```

Mixin类本身写法与Forge完全相同（SpongePowered Mixin）。

> **Skill必需**: `mixin-reference-fabric.md` — **新建**：Fabric下Mixin的最佳实践（Fabric的Mixin注入点常用列表）。

---

## 16. Fabric特有API（Rendering / Object Builder / etc.）

### 16.1 Fabric API 关键模块

Fabric API是一个**模块化集合**，Agent需要知道哪些功能对应哪个模块：

| Fabric API 模块 | 功能 | 对应Forge |
|----------------|------|-----------|
| `fabric-rendering-v1` | 自定义方块/实体渲染 | 内置 |
| `fabric-object-builder-api-v1` | 简化方块/实体构建 | DeferredRegister辅助 |
| `fabric-item-group-api-v1` | FabricItemGroup | CreativeModeTab |
| `fabric-biome-api-v1` | BiomeModifications | BiomeModifier |
| `fabric-networking-api-v1` | 网络通信 | SimpleChannel/Payload |
| `fabric-transfer-api-v1` | 物品/流体/能量传输 | Capability |
| `fabric-registry-sync-v0` | 注册表同步 | 内置 |
| `fabric-data-generation-api-v1` | DataGen（Fabric版） | GatherDataEvent |
| `fabric-renderer-indigo` | Indigo渲染器 | 内置 |

> **Skill必需**: `fabric-api-modules-guide.md` — **新建**：所有Fabric API关键模块的功能、导入方式、版本要求。

### 16.2 Cardin Components API（第三方，替代Capability）

Fabric生态中没有内置Capability系统，社区用 **Cardinal Components API** 代替。

```java
// 给Player附加数据
public class ManaComponent implements ComponentV3 {
    private int mana;
    @Override public void readFromNbt(NbtCompound tag) { mana = tag.getInt("mana"); }
    @Override public void writeToNbt(NbtCompound tag) { tag.putInt("mana", mana); }
}
```

> 这是**可选**的。Agent需要时引用第三方库。

---

## 17. 纹理/图片资源生成

**与Forge/NeoForge完全相同**。所有纹理尺寸、格式、命名约定是Minecraft原生的资源包规范，不依赖任何加载器。

重复强调：**资源文件（models/、textures/、lang/、sounds/、recipes/、loot_tables/、tags/）在三种加载器中完全通用**。

---

## 18. Skill文档完整清单（Fabric版）

### 🔴 第一批（最高优先级 — Fabric基础）

| # | 文件名 | 内容 | 备注 |
|---|--------|------|------|
| 1 | `gradle-config-guide-fabric.md` | **新建**：Fabric Loom Gradle配置 | 完全不同于Forge |
| 2 | `fabric-mod-json-spec.md` | **新建**：fabric.mod.json完整格式 | 核心元数据 |
| 3 | `registry-reference-fabric.md` | **新建**：Fabric注册方式（Registry.register直接注册） | 不同于DeferredRegister |
| 4 | `yarn-mappings-guide.md` | **新建**：Yarn Mappings体系 | 不同于Mojang Mappings |
| 5 | `fabric-api-modules-guide.md` | **新建**：Fabric API各模块说明 | 按需依赖 |

### 🟡 第二批（高优先级 — 核心元素）

| # | 文件名 | 内容 | 备注 |
|---|--------|------|------|
| 6 | `item-api-reference-fabric.md` | Fabric版Item API | Item.Settings vs Item.Properties |
| 7 | `fabric-item-group-api.md` | FabricItemGroup | 创造标签页 |
| 8 | `fabric-screen-handler-guide.md` | **新建**：ScreenHandler体系 | 不同术语 |
| 9 | `fabric-inventory-api.md` | **新建**：ImplementedInventory | Fabric特有 |
| 10 | `mixin-reference-fabric.md` | **新建**：Fabric Mixin最佳实践 | 常用注入点 |
| 11 | `networking-guide-fabric.md` | **新建**：PacketByteBuf网络 | 底层网络 |
| 12 | `fabric-worldgen-guide.md` | **新建**：BiomeModifications API | 世界生成 |
| 13 | `event-dictionary-fabric.md` | **新建**：Fabric回调事件（替代Forge事件） | 不同的"事件"哲学 |

### 🟢 第三批（中优先级）

| # | 文件名 | 内容 | 备注 |
|---|--------|------|------|
| 14 | `fabric-rendering-api.md` | **新建**：Fabric Rendering API | 自定义渲染 |
| 15 | `fabric-transfer-api.md` | **新建**：Transfer API | 替代Capability |
| 16 | `fabric-data-generation.md` | **新建**：Fabric DataGen | Furnace比Forge简单 |
| 17 | `cardinal-components-guide.md` | **新建**：第三方Capability替代 | 可选 |

### 共用的Skill（从NeoForge版直接复用）

以下Skill **完全通用**（基于原版Minecraft，不依赖加载器）：
- `blockstate-spec.md`, `block-model-spec.md` — 方块状态和模型JSON
- `item-model-spec.md` — 物品模型JSON
- `recipe-types.md` — 配方JSON（MC 26.x格式）
- `tag-guide.md` — 标签系统
- `loot-table-spec.md` — 掉落表
- `sounds-spec.md` — sounds.json
- `entity-model-guide.md`, `entity-rendering-guide.md`, `entity-ai-guide.md` — 实体通用
- `particle-api-reference.md` — 粒子类（Java API部分略有差异，JSON格式通用）
- `armor-texture-mapping.md` — 盔甲UV映射
- `mobeffect-reference.md`, `enchantment-reference.md` — 效果和附魔
- `worldgen-guide.md` — 世界生成JSON（configured_feature/placed_feature）
- `structure-guide.md` — 结构JSON
- `fluid-guide.md` — 流体（Fabric流体API略有不同）
- `texture-standards.md` — 纹理标准

### Fabric Skill 总数：17个新建 + 约20个共用 ≈ 37个

---

## 19. Tool接口完整清单（Fabric版）

### 独有的Tool（因架构差异需要）

| Tool | 说明 |
|------|------|
| `scaffold_fabric_mod_project` | Fabric版脚手架（含fabric.mod.json、Loom build.gradle） |
| `generate_fabric_mod_json` | 生成fabric.mod.json |
| `generate_fabric_gradle_config` | 生成Loom Gradle配置 |
| `generate_fabric_item_registration` | 生成Registry.register代码 |
| `generate_fabric_block_registration` | 生成方块注册代码（含自动BlockItem） |
| `generate_fabric_blockentity_registration` | 生成BlockEntityType注册 |
| `generate_fabric_screen_handler` | 生成ScreenHandler + Screen |
| `generate_fabric_network_packet` | 生成PacketByteBuf网络代码 |
| `generate_fabric_mixin` | 生成Mixin类（常用模板） |
| `generate_fabric_entrypoints` | 生成ModInitializer + ClientModInitializer |
| `generate_fabric_item_group` | 生成FabricItemGroup |
| `generate_fabric_spawn_egg` | 生成SpawnEggItem注册 |
| `generate_fabric_worldgen` | 生成BiomeModifications代码 |

### 共用的Tool（加载器无关，直接复用）

| Tool | 说明 |
|------|------|
| `generate_item_model_json` | 物品模型（Minecraft原生） |
| `generate_blockstate_json` | 方块状态（Minecraft原生） |
| `generate_block_model_json` | 方块模型（Minecraft原生） |
| `generate_loot_table_json` | 掉落表（Minecraft原生） |
| `generate_recipe_json` | 配方（Minecraft原生） |
| `generate_block_tags` | 标签（Minecraft原生） |
| `generate_sounds_json` | sounds.json（Minecraft原生） |
| `generate_language_entry` | 翻译（Minecraft原生） |
| `describe_*_texture` | 所有纹理描述（Minecraft原生） |
| `generate_placeholder_texture` | 占位纹理（Minecraft原生） |
| `validate_mod_structure` | 结构调整 |
| `check_missing_textures` | 纹理检查 |
| `query_latest_mc_versions` | 版本查询 |

---

## 20. Fabric vs Forge/NeoForge 元素对照表

| 元素/功能 | **Fabric实现方式** | **Forge/NeoForge实现方式** | 资源文件兼容？ |
|-----------|-------------------|--------------------------|-------------|
| 物品注册 | `Registry.register(Registries.ITEM, id, item)` | `DeferredRegister.create(...).register(...)` | ✅ 纹理/模型JSON通用 |
| 方块注册 | `Registry.register(Registries.BLOCK, id, block)` | `DeferredRegister.create(Registries.BLOCK, ...)` | ✅ blockstate/模型通用 |
| BlockItem | 手动注册或自动 | DeferredRegister自动 | ✅ |
| 创造标签页 | `FabricItemGroup.builder()` | `CreativeModeTab.builder()` | ✅ |
| 工具 | 继承SwordItem等 | 继承SwordItem等 | ✅ |
| 盔甲 | 继承ArmorItem | 继承ArmorItem | ✅ layer贴图通用 |
| 食物 | `Item.Settings.food()` | `Item.Properties.food()` | ✅ |
| BlockEntity | `BlockEntity` 一致 | `BlockEntity` 一致 | ✅ |
| ScreenHandler | `ScreenHandler` + `HandledScreen` | `AbstractContainerMenu` + `Screen` | ✅ GUI纹理通用 |
| 实体 | `EntityType.Builder` 一致 | `EntityType.Builder` 一致 | ✅ 渲染/模型通用 |
| 粒子 | ParticleType+Particle一致 | ParticleType+Particle一致 | ✅ 粒子纹理通用 |
| 声音 | SoundEvent+sounds.json通用 | SoundEvent+sounds.json通用 | ✅ |
| 状态效果 | StatusEffect通用 | MobEffect通用 | ✅ |
| 附魔 | Enchantment通用 | Enchantment通用 | — |
| 配方 | JSON通用 | JSON通用 | ✅ |
| 掉落表 | JSON通用 | JSON通用 | ✅ |
| 标签 | JSON通用 | JSON通用 | ✅ |
| 网络 | `PacketByteBuf` + `ServerPlayNetworking` | `SimpleChannel` / `Payload` | — |
| Mixin | **核心必需** | 内置可选 | ✅ Mixin类通用 |
| 事件/回调 | Mixin注入 / Fabric回调 | MOD Bus + Forge Bus | ❌ 完全不同 |
| Capability/数据附加 | Cardinal Components (第三方) | Capability / Data Component | ❌ 不同 |
| 矿石生成 | `BiomeModifications` (Fabric API) | `biome_modifier` JSON (NeoForge) | ✅ configured_feature JSON通用 |
| 结构 | JSON通用 | JSON通用 | ✅ |
| 流体 | Fabric Fluid API | FluidType | 纹理通用 |
| 村民 | `VillagerProfession` 注册 | `VillagerProfession` 注册 | ✅ |

---

## 总结：Fabric Agent 开发优先级

### Skill 编写顺序
1. `gradle-config-guide-fabric.md` — 连build.gradle都写不对就别玩了
2. `fabric-mod-json-spec.md` — 元数据
3. `registry-reference-fabric.md` — 所有注册
4. `item-api-reference-fabric.md` — 物品API
5. `mixin-reference-fabric.md` — Mixin是Fabric的灵魂
6. `networking-guide-fabric.md` — 网络通信
7. `fabric-api-modules-guide.md` — Fabric API各模块
8. `fabric-screen-handler-guide.md` — GUI
9. 其余…按需

### Tool 编写顺序
1. `scaffold_fabric_mod_project` — 脚手架
2. `generate_fabric_mod_json` — 元数据
3. `generate_fabric_item_registration` + `generate_fabric_block_registration` — 核心注册
4. `generate_fabric_network_packet` — 网络
5. `generate_fabric_mixin` — Mixin模板
6. `generate_item_model_json` + `generate_block_model_json` + `generate_blockstate_json` — 共用资源Tool
7. `describe_*_texture` 系列 — 纹理描述
8. 其余…按需

---

*基于 Fabric Loader 最新版本 + Fabric API 0.156.0+26.2 编写。Fabric与Forge/NeoForge是不同生态，核心区别在于：注册方式（直接Registry.register）、网络（PacketByteBuf）、事件（Mixin替代）、元数据（fabric.mod.json）、构建（Loom）。但所有资源文件（纹理/模型/配方/掉落表/标签/声音）完全通用。*