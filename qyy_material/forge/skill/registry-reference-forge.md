# Forge 注册系统参考 (Registry Reference)

> **用途**: Agent 生成所有注册代码时查询 Registry 类型、DeferredRegister 用法。  
> **加载器**: Forge 65.x (MC 26.2)

---

## 核心注册模式: DeferredRegister

Forge 使用 `DeferredRegister` 来管理所有注册。基本流程：

```java
// 1. 创建 DeferredRegister
public static final DeferredRegister<Type> REGISTRY =
    DeferredRegister.create(ForgeRegistries.TYPE, MODID);

// 2. 注册条目
public static final DeferredHolder<Type, MyType> MY_THING =
    REGISTRY.register("name", () -> new MyType(...));

// 3. 在Mod构造器中绑定事件总线
REGISTRY.register(modEventBus);  // Forge通过FMLJavaModLoadingContext获取
```

---

## 所有 ForgeRegistries 类型

| ForgeRegistries 常量 | 对应原版 Registries | 用途 |
|---------------------|-------------------|------|
| `ForgeRegistries.BLOCKS` | `Registries.BLOCK` | 方块 |
| `ForgeRegistries.ITEMS` | `Registries.ITEM` | 物品 |
| `ForgeRegistries.BLOCK_ENTITY_TYPES` | `Registries.BLOCK_ENTITY_TYPE` | 方块实体类型 |
| `ForgeRegistries.ENTITY_TYPES` | `Registries.ENTITY_TYPE` | 实体类型 |
| `ForgeRegistries.CREATIVE_MODE_TABS` | `Registries.CREATIVE_MODE_TAB` | 创造标签页 |
| `ForgeRegistries.MENU_TYPES` | `Registries.MENU` | 容器菜单类型 |
| `ForgeRegistries.SOUND_EVENTS` | `Registries.SOUND_EVENT` | 声音事件 |
| `ForgeRegistries.PARTICLE_TYPES` | `Registries.PARTICLE_TYPE` | 粒子类型 |
| `ForgeRegistries.MOB_EFFECTS` | `Registries.MOB_EFFECT` | 状态效果 |
| `ForgeRegistries.POTIONS` | `Registries.POTION` | 药水 |
| `ForgeRegistries.ENCHANTMENTS` | `Registries.ENCHANTMENT` | 附魔 |
| `ForgeRegistries.VILLAGER_PROFESSIONS` | `Registries.VILLAGER_PROFESSION` | 村民职业 |
| `ForgeRegistries.POI_TYPES` | `Registries.POINT_OF_INTEREST_TYPE` | 兴趣点 |
| `ForgeRegistries.RECIPE_TYPES` | `Registries.RECIPE_TYPE` | 配方类型 |
| `ForgeRegistries.RECIPE_SERIALIZERS` | `Registries.RECIPE_SERIALIZER` | 配方序列化器 |
| `ForgeRegistries.LOOT_CONDITION_TYPES` | — | 战利品条件 |
| `ForgeRegistries.LOOT_FUNCTION_TYPES` | — | 战利品函数 |
| `ForgeRegistries.ATTRIBUTES` | `Registries.ATTRIBUTE` | 属性 |
| `ForgeRegistries.FLUIDS` | `Registries.FLUID` | 流体 |
| `ForgeRegistries.FLUID_TYPES` | — | Forge特有：流体类型 |

---

## 完整注册代码模板

### 方块注册
```java
public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(ForgeRegistries.BLOCKS, MyMod.MODID);

    public static final DeferredBlock<Block> MY_BLOCK = BLOCKS.register("my_block",
        () -> new Block(BlockBehaviour.Properties.of()
            .strength(3.0f)
            .requiresCorrectToolForDrops()
            .sound(SoundType.STONE)));
}
```

### 物品注册 + BlockItem
```java
public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, MyMod.MODID);

    // BlockItem - 必须和方块同时注册
    public static final DeferredItem<BlockItem> MY_BLOCK_ITEM = ITEMS.register("my_block",
        () -> new BlockItem(ModBlocks.MY_BLOCK.get(), new Item.Properties()));

    // 普通物品
    public static final DeferredItem<Item> MY_ITEM = ITEMS.register("my_item",
        () -> new Item(new Item.Properties()));
}
```

### 方块实体注册
```java
public class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
        DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, MyMod.MODID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<MyBE>> MY_BE =
        BLOCK_ENTITIES.register("my_be",
            () -> BlockEntityType.Builder.of(MyBE::new, ModBlocks.MY_BLOCK.get()).build(null));
}
```

### 实体注册
```java
public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
        DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, MyMod.MODID);

    public static final DeferredHolder<EntityType<?>, EntityType<MyEntity>> MY_ENTITY =
        ENTITIES.register("my_entity",
            () -> EntityType.Builder.of(MyEntity::new, MobCategory.CREATURE)
                .sized(0.6f, 1.8f)
                .build("my_entity"));
}
```

### 创造标签页
```java
public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
        DeferredRegister.create(ForgeRegistries.CREATIVE_MODE_TABS, MyMod.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MY_TAB =
        CREATIVE_MODE_TABS.register("my_tab",
            () -> CreativeModeTab.builder()
                .icon(() -> new ItemStack(ModItems.MY_ITEM.get()))
                .title(Component.translatable("itemGroup.mymod.my_tab"))
                .displayItems((params, output) -> {
                    output.accept(ModItems.MY_ITEM.get());
                    output.accept(ModBlocks.MY_BLOCK.get());
                })
                .build());
}
```

### SoundEvent 注册
```java
public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS =
        DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, MyMod.MODID);

    public static final DeferredHolder<SoundEvent, SoundEvent> MY_SOUND =
        SOUNDS.register("my_sound",
            () -> SoundEvent.createVariableRangeEvent(
                ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "my_sound")));
}
```

### ParticleType 注册
```java
public class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES =
        DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, MyMod.MODID);

    public static final DeferredHolder<ParticleType<?>, SimpleParticleType> MY_PARTICLE =
        PARTICLES.register("my_particle",
            () -> new SimpleParticleType(false));
}
```

### MenuType 注册
```java
public class ModMenuTypes {
    public static final DeferredRegister<MenuType<?>> MENU_TYPES =
        DeferredRegister.create(ForgeRegistries.MENU_TYPES, MyMod.MODID);

    public static final DeferredHolder<MenuType<?>, MenuType<MyContainerMenu>> MY_MENU =
        MENU_TYPES.register("my_menu",
            () -> new MenuType<>(MyContainerMenu::new, FeatureFlags.DEFAULT_FLAGS));
}
```

### MobEffect 注册
```java
public class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS =
        DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, MyMod.MODID);

    public static final DeferredHolder<MobEffect, MyEffect> MY_EFFECT =
        EFFECTS.register("my_effect",
            () -> new MyEffect(MobEffectCategory.HARMFUL, 0x9900FF));
}
```

### Enchantment 注册 (MC 26.x 新API)
```java
public class ModEnchantments {
    public static final DeferredRegister<Enchantment> ENCHANTMENTS =
        DeferredRegister.create(ForgeRegistries.ENCHANTMENTS, MyMod.MODID);

    public static final ResourceKey<Enchantment> MY_ENCHANT_KEY =
        ResourceKey.create(Registries.ENCHANTMENT,
            ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "my_enchant"));

    public static final DeferredHolder<Enchantment, Enchantment> MY_ENCHANT =
        ENCHANTMENTS.register("my_enchant",
            () -> new Enchantment(...));
}
```

---

## Forge Mod 主类汇总注册

```java
@Mod(MyMod.MODID)
public class MyMod {
    public static final String MODID = "my_mod";

    public MyMod() {
        var modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        // 按需注册
        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modEventBus);
        ModEntities.ENTITIES.register(modEventBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modEventBus);
        ModSounds.SOUNDS.register(modEventBus);
        ModParticles.PARTICLES.register(modEventBus);
        ModMenuTypes.MENU_TYPES.register(modEventBus);
        ModEffects.EFFECTS.register(modEventBus);
        ModEnchantments.ENCHANTMENTS.register(modEventBus);
    }
}
```

---

## 命名约定

| 注册名格式 | 示例 | 说明 |
|-----------|------|------|
| 小写+下划线 | `my_block`, `dragon_tooth_sword` | 所有注册名必须 |
| BlockItem同名 | Block和BlockItem使用相同的注册名 | 系统自动关联 |
| 纹理路径相同 | 注册名 = 模型/纹理文件名 | `my_block` → `my_block.png` |

---

## 常见错误

1. ❌ 在static初始化块中注册 → ✅ 使用DeferredRegister
2. ❌ BlockItem注册名与Block不同 → ✅ 必须相同
3. ❌ 忘记在Mod构造器调用 `REGISTRY.register(modEventBus)` → ✅ 必须调用
4. ❌ 使用 `Registries.BLOCK` → ✅ Forge使用 `ForgeRegistries.BLOCKS`