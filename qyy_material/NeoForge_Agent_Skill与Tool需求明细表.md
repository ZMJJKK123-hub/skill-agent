# NeoForge Agent — Skill 与 Tool 需求明细表

> **版本**: v2.0 | **日期**: 2026-08-04 | **加载器**: NeoForge (MC 26.2 / Forge 65.x)  
> **定位**: 按元素类型逐个拆解——Agent 生成每种东西需要创建哪些文件、依赖哪些Skill文档、调用哪些Tool函数。

---

## 目录

- [0. 全局基础：任何mod都需要的](#0-全局基础任何mod都需要的)
- [1. 简单物品 (Item)](#1-简单物品-item)
- [2. 方块 (Block)](#2-方块-block)
- [3. 工具 (Sword / Pickaxe / Axe / Shovel / Hoe)](#3-工具-sword--pickaxe--axe--shovel--hoe)
- [4. 盔甲 (Armor)](#4-盔甲-armor)
- [5. 食物 (Food)](#5-食物-food)
- [6. 方块实体 (BlockEntity)](#6-方块实体-blockentity)
- [7. 容器/GUI (Menu + Screen)](#7-容器gui-menu--screen)
- [8. 自定义实体/生物 (Entity/Mob)](#8-自定义实体生物-entitymob)
- [9. 投掷物/弹射物 (Projectile)](#9-投掷物弹射物-projectile)
- [10. 粒子效果 (Particle)](#10-粒子效果-particle)
- [11. 声音 (Sound)](#11-声音-sound)
- [12. 状态效果/药水 (MobEffect + Potion)](#12-状态效果药水-mobeffect--potion)
- [13. 附魔 (Enchantment)](#13-附魔-enchantment)
- [14. 流体 (Fluid)](#14-流体-fluid)
- [15. 世界生成 (Ore/Structure/Biome)](#15-世界生成-orestructurebiome)
- [16. 村民交易/职业 (Villager)](#16-村民交易职业-villager)
- [17. 网络数据包 (Networking Payload)](#17-网络数据包-networking-payload)
- [18. 纹理/图片资源生成（重点）](#18-纹理图片资源生成重点)
- [19. Skill 文档完整清单（落地版）](#19-skill-文档完整清单落地版)
- [20. Tool 接口完整清单（落地版）](#20-tool-接口完整清单落地版)
- [21. 跨元素共享的公用 Skill/Tool](#21-跨元素共享的公用-skilltool)

---

## 0. 全局基础：任何mod都需要的

Agent 收到第一个mod请求时，必须首先生成以下基础设施。

### 0.1 必需的全局文件

| 文件 | 用途 | 生成方式 |
|------|------|----------|
| `build.gradle` | Gradle构建脚本 | Tool: `generate_gradle_config` |
| `settings.gradle` | 项目名称+插件仓库 | Tool: `generate_gradle_config` |
| `gradle.properties` | 版本号集中管理 | Tool: `generate_gradle_config` |
| `gradle/wrapper/gradle-wrapper.properties` | Gradle版本 | Tool: `scaffold_mod_project` |
| `gradlew` / `gradlew.bat` | Gradle包装器脚本 | Tool: `scaffold_mod_project` |
| `src/main/resources/META-INF/neoforge.mods.toml` | Mod元数据 | Tool: `generate_mods_toml` |
| `src/main/resources/pack.mcmeta` | 资源包元数据 | Tool: `scaffold_mod_project` |
| `src/main/java/{package}/{ModMainClass}.java` | @Mod主类 | Tool: `scaffold_mod_project` |

### 0.2 必需的 Skill

| Skill | 为什么需要 |
|-------|-----------|
| `version-matrix.md` | Agent生成build.gradle/gradle.properties时，必须知道MC版本↔NeoForge版本↔JDK版本的精确映射，否则编译失败 |
| `gradle-config-guide.md` | Agent需要知道NeoForge Gradle插件版本号、仓库配置、run配置等精确写法 |
| `parchment-mappings.md` | Agent生成代码时用人类可读的参数名，不用SRG混淆名 |

### 0.3 必需的 Tool

| Tool | 说明 |
|------|------|
| `scaffold_mod_project` | 输入mod_id, mc_version, package_path → 生成完整项目目录+所有模板文件 |
| `generate_gradle_config` | 生成三个Gradle文件的精确内容 |
| `generate_mods_toml` | 生成neoforge.mods.toml |
| `query_latest_mc_versions` | 查询当前最新版本号 |
| `validate_mod_structure` | 验证项目完整性 |

---

## 1. 简单物品 (Item)

> 用户说："我要一个叫'烈焰核心'的物品"  
> Agent需要自动生成以下所有内容：

### 1.1 需要生成的文件清单

```
物品 (my_item) 需要生成:
├── Java代码
│   ├── MyItem.java                    # 物品类（可选，简单物品直接用Item）
│   └── registry/ModItems.java        # 注册代码（追加register）
├── 资源文件
│   ├── assets/<modid>/models/item/my_item.json       # 物品模型JSON
│   ├── assets/<modid>/textures/item/my_item.png      # 物品纹理（16×16或32×32）
│   └── assets/<modid>/lang/en_us.json                # 英文翻译
│   └── assets/<modid>/lang/zh_cn.json                # 中文翻译
├── 数据文件
│   ├── data/<modid>/recipes/my_item.json             # 配方（如果可合成）
│   └── data/<modid>/tags/items/xxx.json              # 物品标签（如果有分类）
└── 创造模式
    └── registry/ModCreativeTabs.java                 # 追加到某个创造标签页
```

### 1.2 文件生成细节

#### a) `assets/<modid>/models/item/my_item.json`
```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "<modid>:item/my_item"
  }
}
```
> **Skill必需**: `item-api-reference.md` — Agent需要知道`item/generated` vs `item/handheld` 的区别（普通物品用generated，工具用handheld）。

#### b) 纹理 `my_item.png`
- 尺寸：16×16 像素（原版风格）或用户自定义
- 格式：PNG，透明背景
> **Tool必需**: `describe_item_texture` — 向用户/图片生成服务描述这个物品的视觉外观。  
> **Tool必需**: `generate_placeholder_texture` — 如果用户没有提供图片，生成一个带文字标注的占位PNG。

#### c) `data/<modid>/recipes/my_item.json`
```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": ["XXX", "XYX", "XXX"],
  "key": {
    "X": { "item": "minecraft:diamond" },
    "Y": { "item": "minecraft:nether_star" }
  },
  "result": { "id": "<modid>:my_item", "count": 1 }
}
```
> **Skill必需**: `recipe-types.md` — Agent需要知道所有配方类型的JSON格式，以及1.21+/26.x中`result`的新格式（`{id, count}` 而非 `"result": "modid:item"`）。

### 1.3 需要的 Skill（按Agent读取顺序）

| 顺序 | Skill | 作用 |
|------|-------|------|
| 1 | `registry-reference.md` | 知道如何用DeferredRegister注册Item |
| 2 | `item-api-reference.md` | 知道Item.Properties的各种设置（堆叠数、耐久、稀有度、食物属性等） |
| 3 | `item-model-spec.md` | 物品模型JSON格式规范（generated/handheld/parent等） |
| 4 | `recipe-types.md` | 各种配方JSON格式 |
| 5 | `tag-guide.md` | 物品标签的用途和格式 |
| 6 | `component-system.md` | MC 26.x的Data Component系统（替代旧NBT） |
| 7 | `common-mistakes.md` | 避免常见注册/模型/配方错误 |

### 1.4 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_item_registration` | item_name, properties{stack_size, durability, rarity, fire_resistant} | ModItems.java片段 | 生成注册代码 |
| `generate_item_model_json` | item_name, model_type(generated/handheld), texture_path | JSON文件 | 生成模型JSON |
| `describe_item_texture` | item_name, description, style(vanilla_16x/hd_32x) | 纹理描述Prompt | 供图片生成AI使用 |
| `generate_placeholder_texture` | item_name, base_color, icon_shape | PNG文件 | 如果用户没有提供纹理 |
| `generate_recipe_json` | recipe_type, pattern, ingredients, result | JSON文件 | 生成配方 |
| `generate_language_entry` | key, en_text, zh_text | lang JSON片段 | 追加翻译 |
| `add_to_creative_tab` | item_registry_name, tab_name | Java代码片段 | 追加到创造标签页 |

---

## 2. 方块 (Block)

> 用户说："我要一个叫'虚空晶石'的方块，石头质感，硬度5，需要钻石镐采集"  
> Agent需要同时生成方块+对应的BlockItem+六个面的模型和纹理。

### 2.1 需要生成的文件清单

```
方块 (my_block) 需要生成:
├── Java代码
│   ├── block/MyBlock.java                    # 方块类（可继承Block或特殊子类）
│   ├── registry/ModBlocks.java               # 方块注册（追加）
│   ├── registry/ModItems.java                # BlockItem注册（追加）
│   └── registry/ModCreativeTabs.java         # 追加到创造标签页
├── 模型/渲染
│   ├── assets/<modid>/blockstates/my_block.json              # 方块状态定义
│   ├── assets/<modid>/models/block/my_block.json             # 方块模型
│   ├── assets/<modid>/models/item/my_block.json              # 物品形态模型
│   └── assets/<modid>/textures/block/my_block.png            # 方块纹理
│       或六个面分别：
│       ├── my_block_top.png
│       ├── my_block_bottom.png
│       ├── my_block_side.png
│       ├── my_block_front.png
│       └── my_block_back.png
├── 数据文件
│   ├── data/<modid>/loot_tables/blocks/my_block.json         # 掉落表
│   ├── data/<modid>/recipes/my_block.json                    # 配方
│   └── data/<modid>/tags/blocks/
│       ├── mineable/pickaxe.json                             # 挖掘工具标签
│       └── needs_diamond_tool.json                           # 挖掘等级标签
└── 语言文件
    └── assets/<modid>/lang/en_us.json + zh_cn.json
```

### 2.2 关键生成细节

#### a) 方块状态 `blockstates/my_block.json`
```json
{
  "variants": {
    "": { "model": "<modid>:block/my_block" }
  }
}
```
如果有朝向/开关等属性，variants需要展开。例如：
```json
{
  "variants": {
    "facing=north": { "model": "<modid>:block/my_block", "y": 0 },
    "facing=east":  { "model": "<modid>:block/my_block", "y": 90 },
    "facing=south": { "model": "<modid>:block/my_block", "y": 180 },
    "facing=west":  { "model": "<modid>:block/my_block", "y": 270 }
  }
}
```
> **Skill必需**: `blockstate-spec.md` — 所有方块属性(facing/half/open/powered/lit...) 和对应variants格式。

#### b) 方块模型 `models/block/my_block.json`

**单一纹理（六个面都一样）：**
```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "<modid>:block/my_block"
  }
}
```

**顶部/底部/侧面不同（像草方块）：**
```json
{
  "parent": "minecraft:block/cube_bottom_top",
  "textures": {
    "top": "<modid>:block/my_block_top",
    "bottom": "<modid>:block/my_block_bottom",
    "side": "<modid>:block/my_block_side"
  }
}
```

**前后左右+上下不同（像熔炉）：**
```json
{
  "parent": "minecraft:block/cube",
  "textures": {
    "north": "<modid>:block/my_block_front",
    "south": "<modid>:block/my_block_back",
    "east": "<modid>:block/my_block_side",
    "west": "<modid>:block/my_block_side",
    "up": "<modid>:block/my_block_top",
    "down": "<modid>:block/my_block_bottom"
  }
}
```

**非完整方块（楼梯/半砖/栅栏/墙/门/活板门）：** 各自有不同的parent模型和旋转规则。Agent需要根据用户意图自动选择合适的Base Block类和对应模型parent。
> **Skill必需**: `block-model-spec.md` — 所有方块模型parent类型及纹理命名约定。

#### c) 六个面纹理的生成

这是你说的重点。方块通常需要以下纹理变量：
| 纹理文件 | 何时需要 | 尺寸 |
|---------|---------|------|
| `textures/block/{name}.png` | 所有面一样 | 16×16 |
| `textures/block/{name}_top.png` | 顶面不同 | 16×16 |
| `textures/block/{name}_bottom.png` | 底面不同 | 16×16 |
| `textures/block/{name}_side.png` | 侧面 | 16×16 |
| `textures/block/{name}_front.png` | 正面 | 16×16 |
| `textures/block/{name}_back.png` | 背面 | 16×16 |
| `textures/block/{name}_overlay.png` | 叠加层（如草方块顶部） | 16×16（带透明） |
| `textures/block/{name}_particle.png` | 粒子纹理（破坏粒子、掉落后的粒子） | 16×16 |

> **Tool必需**: `describe_block_textures` — 根据方块描述，生成每个面需要的纹理prompt。例如：
> - "石头质感，但要半透明带紫色光晕" → top: 深灰石纹+紫光叠加, side: 深灰石纹, bottom: 纯深灰
> **Tool必需**: `generate_block_model_json` — 根据提供的面纹理配置，自动选parent并生成模型JSON

#### d) 掉落表 `loot_tables/blocks/my_block.json`
```json
{
  "type": "minecraft:block",
  "pools": [{
    "rolls": 1,
    "entries": [{
      "type": "minecraft:item",
      "name": "<modid>:my_block"
    }],
    "conditions": [{
      "condition": "minecraft:survives_explosion"
    }]
  }]
}
```
若需精准采集掉自身、否则掉其他物品，需更复杂配置。
> **Skill必需**: `loot-table-spec.md` — 所有掉落条件、函数、池配置。

#### e) 方块标签
```json
// data/<modid>/tags/blocks/mineable/pickaxe.json
{ "values": ["<modid>:my_block"] }

// data/<modid>/tags/blocks/needs_diamond_tool.json
{ "values": ["<modid>:my_block"] }
```
> **Skill必需**: `tag-guide.md` — 所有原版标签清单（mineable/*, needs_*_tool, incorrect_for_*_tool, walls, fences, logs, etc.）

### 2.3 需要的 Skill

| 顺序 | Skill | 作用 |
|------|-------|------|
| 1 | `registry-reference.md` | Block + BlockItem 注册 |
| 2 | `block-api-reference.md` | 方块属性设置（BlockBehaviour.Properties: strength, sound, luminance, requiresCorrectTool, noOcclusion, etc.）以及Base Block类选择指南 |
| 3 | `blockstate-spec.md` | 方块状态JSON格式，所有原版BlockState属性 |
| 4 | `block-model-spec.md` | 所有方块模型parent类型、纹理命名约定 |
| 5 | `loot-table-spec.md` | 掉落表条件、函数、所有条目类型 |
| 6 | `tag-guide.md` | 所有原版标签 |
| 7 | `recipe-types.md` | 配方JSON格式 |
| 8 | `component-system.md` | Data Component系统 |
| 9 | `common-mistakes.md` | 常见方块注册/模型/掉落表错误 |

### 2.4 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_block_class` | name, properties{hardness, resistance, sound_type, luminance, no_occlusion, requires_tool...} | MyBlock.java | 方块类代码 |
| `generate_block_registration` | block_name, block_class | ModBlocks.java + ModItems.java片段 | 注册代码 |
| `generate_blockstate_json` | block_name, properties{facing/half/open...} | blockstate JSON | 自动生成variants |
| `generate_block_model_json` | block_name, face_textures{top, bottom, side, front, back, all, particle} | 模型JSON | 根据提供的面自动选parent |
| `generate_item_block_model_json` | block_name | 物品模型JSON（parent指向block model） | |
| `describe_block_textures` | block_name, visual_description, face_count(1或6) | 每个面的纹理Prompt | 供图片生成AI |
| `generate_placeholder_block_texture` | block_name, face, base_color, pattern | PNG文件 | 占位纹理（含面标注文字） |
| `generate_loot_table_json` | block_name, drops[], silk_touch_variant, conditions[] | loot_table JSON | 掉落表 |
| `generate_block_tags` | block_name, block_properties | tags JSON | 自动分析所需标签（矿镐/斧/等级/红石/等） |
| `generate_recipe_json` | 同上 | JSON | 配方 |
| `generate_language_entry` | 同上 | lang片段 | 翻译 |

---

## 3. 工具 (Sword / Pickaxe / Axe / Shovel / Hoe)

> 用户说："我要一把叫'龙牙之刃'的剑，攻击力+8，攻速1.6，耐久2000，材质像龙牙"  
> Agent需要处理：Tier定义 + 工具类 + 手持模型 + 材质 + 3D动作适配说明。

### 3.1 需要生成的文件清单

```
剑 (dragon_tooth_sword) 需要生成:
├── Java代码
│   ├── item/DragonToothSword.java          # 剑类（可选，扩展SwordItem）
│   ├── util/ModTiers.java                  # 自定义Tier等级（首次需新建）
│   ├── registry/ModItems.java              # 物品注册（追加）
│   └── registry/ModCreativeTabs.java
├── 资源文件
│   ├── assets/<modid>/models/item/dragon_tooth_sword.json    # 手持模型
│   ├── assets/<modid>/textures/item/dragon_tooth_sword.png   # 物品纹理
│   └── assets/<modid>/lang/...
├── 数据文件
│   └── data/<modid>/recipes/dragon_tooth_sword.json
└── 可能的额外资源（视需求）
    ├── 特殊攻击效果 → 事件监听器（ModEvents.java追加）
    └── 粒子效果 → 粒子注册 + 事件中生成粒子
```

### 3.2 "适配动作" 的详细说明

原版Minecraft中，工具的挥动动画由以下机制控制：

#### a) 第一人称手持动画
由 `models/item/xxx.json` 的 **parent** 决定：
- `"parent": "minecraft:item/handheld"` → 剑/工具的手持姿势（斜45度）
- `"parent": "minecraft:item/generated"` → 平放在手中（普通物品）

这是**纯模型层面**的，Agent只需要生成正确的parent即可。✅ 简单。

#### b) 第三人称攻击动画
原版MC对SwordItem等工具类有**内置的**攻击动画处理。如果Agent继承`SwordItem`：
- 玩家挥剑 → 原版自动播放手臂挥动动画
- 不需要额外代码或模型

Agent只需要确保继承正确的Base类（SwordItem/PickaxeItem/AxeItem/ShovelItem/HoeItem）。

#### c) 如果需要**自定义3D模型**（非扁平贴图，而是真正的3D物品）
需要：Blockbench模型 `.json` + `"parent": "builtin/entity"` + 渲染器
> **高级内容**，仅特殊需求。Agent需要判断用户是否要求3D工具模型。

#### d) 攻击时附带粒子特效
需要在**事件**中处理：
```java
@SubscribeEvent
public static void onAttack(AttackEntityEvent event) {
    if (event.getEntity().getMainHandItem().is(ModItems.DRAGON_TOOTH_SWORD.get())) {
        // 在攻击位置生成粒子
        event.getTarget().level().addParticle(
            ModParticles.DRAGON_FLAME.get(),
            event.getTarget().getX(), event.getTarget().getY() + 1,
            event.getTarget().getZ(), 0, 0.1, 0
        );
    }
}
```
> 这意味着如果工具需要特殊攻击特效，Agent还需要生成：事件监听代码 + 粒子定义（如果粒子是新类型）。

### 3.3 Tier 定义 (ModTiers.java)

```java
public class ModTiers {
    public static final Tier DRAGON_TOOTH = new Tier() {
        @Override public int getUses() { return 2000; }
        @Override public float getSpeed() { return 8.0f; }
        @Override public float getAttackDamageBonus() { return 3.0f; }
        @Override public int getEnchantmentValue() { return 15; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.DRAGON_TOOTH.get()); }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_DIAMOND_TOOL; }
    };

    // 或者用新API（26.x推荐）：
    // 详见 component-system.md
}
```

### 3.4 需要的 Skill

| 顺序 | Skill | 作用 |
|------|-------|------|
| 1 | `item-api-reference.md` | SwordItem/PickaxeItem等工具类API、Tier接口、createAttributes方法 |
| 2 | `registry-reference.md` | 注册 |
| 3 | `tier-definition-guide.md` | **新建**：Tier接口全部方法说明、与BlockTags的对应关系、INCORRECT_FOR vs NEEDS标签区别 |
| 4 | `item-model-spec.md` | 手持模型handheld vs generated |
| 5 | `recipe-types.md` | 配方 |
| 6 | `event-dictionary.md` | 如果需要攻击事件：AttackEntityEvent, LivingHurtEvent等 |
| 7 | `particle-api-reference.md` | 如果需要攻击粒子效果 |
| 8 | `component-system.md` | 工具属性现在通过Data Component管理 |

### 3.5 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_tool_class` | tool_type, tier_name, tier_stats, attack_damage, attack_speed | Java类 | 生成SwordItem/PickaxeItem等 |
| `generate_tier_definition` | tier_name, uses, speed, damage_bonus, enchantability, repair_item | ModTiers.java片段 | Tier定义 |
| `generate_item_model_json` | item_name, model_type=handheld, texture | JSON | 手持模型 |
| `describe_tool_texture` | tool_name, visual_description | 纹理Prompt | |
| `generate_recipe_json` | 同上 | JSON | |
| `generate_attack_particle_effect` | tool_name, particle_type, particle_color, count | 事件代码片段 | 攻击粒子逻辑 |

---

## 4. 盔甲 (Armor)

> 用户说："我要一套龙鳞盔甲，防御力比钻石高一点，特殊效果是穿上后免疫火焰伤害"

### 4.1 需要生成的文件清单

```
盔甲 (dragon_scale_armor) 需要生成:
├── Java代码
│   ├── item/DragonScaleArmorItem.java          # 盔甲类（可选）
│   ├── util/ModArmorMaterials.java             # 盔甲材料定义
│   ├── registry/ModItems.java                  # 4件盔甲注册（头盔/胸甲/护腿/靴子）
│   └── 事件监听（免疫火焰等效果）
├── 资源文件
│   ├── assets/<modid>/models/item/
│   │   ├── dragon_scale_helmet.json
│   │   ├── dragon_scale_chestplate.json
│   │   ├── dragon_scale_leggings.json
│   │   └── dragon_scale_boots.json
│   ├── assets/<modid>/textures/item/            # 物品图标
│   │   ├── dragon_scale_helmet.png
│   │   ├── dragon_scale_chestplate.png
│   │   ├── dragon_scale_leggings.png
│   │   └── dragon_scale_boots.png
│   ├── assets/<modid>/textures/models/armor/    # 穿戴时的盔甲层
│   │   ├── dragon_scale_layer_1.png             # 头盔+胸甲+靴子
│   │   └── dragon_scale_layer_2.png             # 护腿
│   └── assets/<modid>/lang/...
└── 数据文件
    └── data/<modid>/recipes/ (4个配方)
```

### 4.2 盔甲的特殊资源：穿戴贴图

这是盔甲独有的。需要**2张**穿戴层的纹理：

| 文件 | 覆盖哪些槽位 | 尺寸 | 说明 |
|------|-------------|------|------|
| `dragon_scale_layer_1.png` | 头盔 + 胸甲 + 靴子 | 64×64 | 基于vanilla armor layer 1的UV映射 |
| `dragon_scale_layer_2.png` | 护腿 | 64×64 | 基于vanilla armor layer 2的UV映射 |

> **Skill必需**: `armor-texture-mapping.md` — **新建**：说清楚layer_1和layer_2各自的UV映射区域（头/身/臂/腿/脚的像素位置），供图片生成AI参考。

### 4.3 盔甲特殊效果

免疫火焰伤害 → 事件监听：
```java
@SubscribeEvent
public static void onLivingHurt(LivingHurtEvent event) {
    if (event.getSource().is(DamageTypes.IN_FIRE) || event.getSource().is(DamageTypes.ON_FIRE)) {
        LivingEntity entity = event.getEntity();
        if (entity.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.DRAGON_SCALE_HELMET.get())
            && entity.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.DRAGON_SCALE_CHESTPLATE.get())
            && entity.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.DRAGON_SCALE_LEGGINGS.get())
            && entity.getItemBySlot(EquipmentSlot.FEET).is(ModItems.DRAGON_SCALE_BOOTS.get())) {
            event.setCanceled(true);
        }
    }
}
```
> **Skill必需**: `event-dictionary.md` — LivingHurtEvent, LivingDamageEvent, 装备槽检查方法。
> **Skill必需**: `damage-type-reference.md` — **新建**：MC 26.x的DamageType体系（不再是简单的DamageSource）。

### 4.4 需要的 Skill

| Skill | 作用 |
|-------|------|
| `item-api-reference.md` | ArmorItem API、ArmorMaterial接口 |
| `armor-texture-mapping.md` | **新建**：layer_1/layer_2 UV映射图 |
| `item-model-spec.md` | 盔甲物品模型 |
| `event-dictionary.md` | 穿戴效果事件 |
| `damage-type-reference.md` | **新建**：DamageType体系 |
| `registry-reference.md` | 注册 |
| `recipe-types.md` | 配方 |
| `component-system.md` | 盔甲属性通过Component管理（26.x） |

### 4.5 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_armor_set` | material_name, defense_values[], toughness, enchantability, repair_item, special_effects_description | 4个ArmorItem注册 + ModArmorMaterials | 一键生成整套盔甲 |
| `describe_armor_texture` | armor_name, visual_description, layer(1或2) | 纹理Prompt（含UV映射说明） | |
| `describe_armor_item_icon` | armor_name, slot(helmet/chestplate/leggings/boots) | 物品图标Prompt | |
| `generate_armor_effect_code` | effect_description, condition | 事件监听代码 | 如免疫火焰 |

---

## 5. 食物 (Food)

> 用户说："我要一种叫'魔法蛋糕'的食物，回复8点饥饿、12点饱食度，吃完后获得5秒速度II效果，吃的时候有蛋糕碎屑粒子掉落"

### 5.1 需要生成的文件清单

```
食物 (magic_cake) 需要生成:
├── Java代码
│   ├── registry/ModItems.java             # 物品注册（内联FoodProperties）
│   └── 事件监听（吃食物时的粒子效果）
├── 资源文件
│   ├── assets/<modid>/models/item/magic_cake.json
│   ├── assets/<modid>/textures/item/magic_cake.png
│   └── assets/<modid>/lang/...
├── 数据文件
│   └── data/<modid>/recipes/magic_cake.json
└── 额外
    ├── 粒子效果 → 如果有自定义食物碎屑粒子
    └── sounds.json → 如果自定义吃食物声音
```

### 5.2 "吃东西的动作" 和 "食物碎渣粒子"

#### a) 吃东西的动作
原版MC中，吃东西的动画是**内置的**，不需要Agent额外生成：
- 玩家手持食物右键 → 自动播放举臂动画
- 吃完后自动播放吞咽效果
- **Agent不需要为这个生成任何代码或模型**

#### b) 食物碎渣掉下来的粒子效果
这是你说的重点。需要在事件中处理：

```java
// 在玩家吃完食物时生成粒子
@SubscribeEvent
public static void onItemUseFinish(LivingEntityUseItemEvent.Finish event) {
    if (event.getItem().is(ModItems.MAGIC_CAKE.get())) {
        LivingEntity entity = event.getEntity();
        Level level = entity.level();
        // 生成蛋糕碎屑粒子
        for (int i = 0; i < 8; i++) {
            level.addParticle(
                ModParticles.CAKE_CRUMB.get(),  // 自定义粒子 或 使用原版item粒子
                entity.getX(), entity.getY() + 1.5, entity.getZ(),
                (level.random.nextDouble() - 0.5) * 0.2,  // vx
                0.1,                                       // vy
                (level.random.nextDouble() - 0.5) * 0.2,  // vz
                Item.getId(ModItems.MAGIC_CAKE.get())      // 如果用的是原版item粒子
            );
        }
    }
}
```

如果使用**原版粒子**（`ParticleTypes.ITEM`），传入物品ID即可生成对应纹理的粒子——**不需要自定义粒子类**。
如果需要**自定义粒子纹理**，则需要额外注册ParticleType。

> **Skill必需**: `event-dictionary.md` — LivingEntityUseItemEvent.Finish 等
> **Skill必需**: `particle-api-reference.md` — **新建**：所有原版粒子类型、自定义粒子注册、addParticle参数说明

### 5.3 "吃东西的音效"

原版食物默认使用 `SoundEvents.GENERIC_EAT`。若要自定义：
> **SoundEvent注册** → 见 [第11章 声音](#11-声音-sound)

### 5.4 需要的 Skill

| Skill | 作用 |
|-------|------|
| `item-api-reference.md` | FoodProperties构造、.nutrition()、.saturationMod()、.effect() |
| `registry-reference.md` | 注册 |
| `item-model-spec.md` | 物品模型 |
| `recipe-types.md` | 配方 |
| `event-dictionary.md` | 食物使用事件（Start/Finish/Tick） |
| `particle-api-reference.md` | **新建**：粒子系统API |
| `mobeffect-reference.md` | 状态效果类型（速度、力量等） |

### 5.5 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_food_item` | name, nutrition, saturation, effects[{effect, duration, amplifier, chance}], always_eatable, fast_food | 注册代码 | 生成带FoodProperties的物品 |
| `describe_food_texture` | food_name, visual_description | 纹理Prompt | |
| `generate_food_eat_particle_code` | food_name, particle_type, particle_count, custom_particle_description | 事件代码 | 吃完后的粒子效果 |
| `generate_food_eat_sound` | food_name, custom_sound_description | sounds.json + SoundEvent注册 | 自定义吃食物声音（可选） |
| `generate_recipe_json` | 同上 | JSON | |

---

## 6. 方块实体 (BlockEntity)

> 用户说："我要一个'自动熔炼炉'，能自动把放入的矿石熔炼成锭，有GUI界面，有进度条动画"  
> 这是最复杂的类型之一，因为它涉及BlockEntity + Menu + Screen + 网络同步。

### 6.1 需要生成的文件清单

```
BlockEntity (auto_furnace) 需要生成:
├── Java代码
│   ├── block/AutoFurnaceBlock.java              # 方块类（需实现EntityBlock）
│   ├── block/AutoFurnaceBlockEntity.java        # BlockEntity类（核心逻辑）
│   ├── screen/AutoFurnaceMenu.java              # 容器Menu
│   ├── screen/AutoFurnaceScreen.java            # 客户端Screen（GUI渲染）
│   ├── registry/ModBlocks.java                  # 注册
│   ├── registry/ModItems.java                   # BlockItem
│   ├── registry/ModBlockEntities.java           # BlockEntityType注册
│   ├── registry/ModMenuTypes.java               # MenuType注册
│   └── network/ModNetworking.java               # 数据同步（如果需要）
├── 资源文件
│   ├── gui纹理
│   │   └── assets/<modid>/textures/gui/auto_furnace.png    # GUI背景图
│   ├── 方块资源（同普通方块的所有资源）
│   └── 语言文件
└── 数据文件
    ├── 配方（自定义配方类型？）
    └── 所有方块数据
```

### 6.2 核心概念拆解

| 组件 | 职责 | 关键父类 |
|------|------|---------|
| Block | 方块本体、右键打开GUI、状态更新 | `BaseEntityBlock` |
| BlockEntity | 数据存储、tick逻辑、NBT序列化、物品槽管理 | `BlockEntity` |
| Menu | 服务端-客户端数据同步桥梁、槽位定义、quickMoveStack | `AbstractContainerMenu` |
| Screen | 客户端GUI渲染：背景图、进度条、提示文字 | `AbstractContainerScreen` |
| BlockEntityRenderer | （可选）方块世界中的特殊渲染 | `BlockEntityRenderer` |

### 6.3 GUI纹理要求

`textures/gui/auto_furnace.png`：
- 尺寸：256×256像素（原版标准）
- 包含：背景、进度条各阶段、输入输出槽位标识
- 原版熔炉GUI是256×256，进度条的火焰箭头在特定像素位置

> **Skill必需**: `gui-texture-spec.md` — **新建**：GUI纹理标准尺寸、各元素像素坐标约定、进度条动画帧布局。

### 6.4 需要的 Skill

| Skill | 作用 |
|-------|------|
| `blockentity-guide.md` | 完整BlockEntity教程（生命周期、tick、序列化、ItemStackHandler） |
| `gui-container-guide.md` | ContainerMenu + Screen 体系、Slot定义、quickMoveStack、数据同步 |
| `gui-texture-spec.md` | **新建**：GUI纹理标准 |
| `block-api-reference.md` | EntityBlock接口 |
| `networking-guide.md` | 如果需要网络同步进度条数据 |
| `event-dictionary.md` | RegisterMenuScreensEvent 等 |
| `registry-reference.md` | BlockEntityType / MenuType 注册 |
| `component-system.md` | Data Component（新物品数据） |

### 6.5 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_blockentity_class` | name, slot_count, tick_logic, data_fields[], sync_fields[] | BlockEntity.java | 完整的BE类 |
| `generate_menu_class` | name, slot_layout[], container_size | Menu.java | Menu类 |
| `generate_screen_class` | name, gui_texture, progress_bar_config | Screen.java | Screen类 |
| `generate_blockentity_block_class` | name, be_class | Block.java | 关联BlockEntity的方块 |
| `describe_gui_texture` | gui_description, slot_positions[], progress_bar_positions[] | GUI纹理Prompt | |
| `generate_blockentity_registration` | name, be_class, block_class | 所有注册代码片段 | 一站式注册 |

---

## 7. 容器/GUI (Menu + Screen)

已经在第6章BlockEntity中详细覆盖。如果只是单纯的容器（没有BlockEntity），比如玩家背包扩展，结构类似但更简单。

---

## 8. 自定义实体/生物 (Entity/Mob)

> 用户说："我要一个'暗影龙'，会飞、会喷火球、死亡后掉落龙鳞，有自定义模型"

### 8.1 需要生成的文件清单

这是**最复杂**的元素类型：

```
实体 (shadow_dragon) 需要生成:
├── Java代码
│   ├── entity/ShadowDragonEntity.java           # 实体类（继承Mob/FlyingMob）
│   ├── entity/ShadowDragonModel.java            # 实体模型（Layer Definition）
│   ├── entity/ShadowDragonRenderer.java         # 实体渲染器
│   ├── entity/ai/ShadowDragonAi.java            # AI目标（或内联）
│   ├── entity/goal/ShadowDragonFireballGoal.java # 自定义AI目标
│   ├── registry/ModEntities.java                # EntityType注册
│   ├── registry/ModItems.java                   # 刷怪蛋
│   ├── registry/ModSounds.java                  # 声音事件
│   └── event/ModEntityEvents.java               # 属性注册、刷怪规则
├── 资源文件
│   ├── assets/<modid>/textures/entity/shadow_dragon.png        # 实体纹理
│   ├── assets/<modid>/textures/entity/shadow_dragon_glow.png   # 发光层（可选）
│   ├── assets/<modid>/sounds/entity/shadow_dragon/
│   │   ├── idle.ogg          # 空闲声音
│   │   ├── hurt.ogg          # 受伤声音
│   │   ├── death.ogg         # 死亡声音
│   │   └── fireball.ogg      # 喷火声音
│   ├── assets/<modid>/sounds.json                               # 声音注册
│   ├── assets/<modid>/lang/...                                  # 名称+刷怪蛋名
│   └── 实体模型JSON（如果用Blockbench/GeckoLib）
│       └── assets/<modid>/geo/shadow_dragon.geo.json
├── 数据文件
│   ├── data/<modid>/loot_tables/entities/shadow_dragon.json     # 掉落表
│   └── data/<modid>/tags/entity_types/...                       # 实体标签
└── 可能的额外
    ├── 自定义火球实体（如果有特殊弹射物）
    └── 粒子效果（喷火粒子、翅膀粒子等）
```

### 8.2 实体模型（重要！）

Minecraft实体模型有**三种方式**：

| 方式 | 用途 | 复杂度 |
|------|------|--------|
| **原版EntityModel** | 简单实体（用Java代码定义box/旋转） | 中等 |
| **Blockbench + geckolib** | 复杂生物、动画丰富 | 高 |
| **Blockbench + 原版动画** | 折中方案 | 中高 |

对于Agent自动生成的场景，**推荐先支持原版EntityModel**，后续再支持GeckoLib。

> **Skill必需**: `entity-model-guide.md` — **新建**：EntityModel体系（ModelPart, CubeListBuilder, 动画关键帧）、LayerDefinition注册、animation文件格式。
> **Skill必需**: `entity-rendering-guide.md` — **新建**：EntityRenderer, RenderLayer, 发光层, 尺寸scale。

### 8.3 实体AI

```java
// 在Entity构造中添加AI目标
this.goalSelector.addGoal(1, new FloatGoal(this));
this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, false));
this.goalSelector.addGoal(3, new WaterAvoidingRandomStrollGoal(this, 1.0D));
this.goalSelector.addGoal(4, new LookAtPlayerGoal(this, Player.class, 8.0F));
this.goalSelector.addGoal(5, new RandomLookAroundGoal(this));
```

> **Skill必需**: `entity-ai-guide.md` — **新建**：所有原版AI Goal类型、自定义Goal编写、Brain系统（1.20+新AI）。

### 8.4 需要的 Skill

| Skill | 作用 |
|-------|------|
| `entity-guide.md` | **新建**：Entity完整教程（属性、AI、刷怪、数据追踪） |
| `entity-model-guide.md` | **新建**：EntityModel体系、LayerDefinition |
| `entity-rendering-guide.md` | **新建**：渲染器、发光层、尺寸 |
| `entity-ai-guide.md` | **新建**：Goal体系 |
| `sounds-spec.md` | **新建**：sounds.json格式、SoundEvent注册 |
| `loot-table-spec.md` | 实体掉落表 |
| `event-dictionary.md` | EntityAttributeCreationEvent, RegisterRenderers等 |
| `registry-reference.md` | EntityType注册 |
| `tag-guide.md` | 实体标签 |

### 8.5 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_entity_class` | name, dimensions, max_health, movement_speed, ai_goals[], attack_damage, drops_description | Entity.java | 完整实体类 |
| `generate_entity_model` | entity_name, body_parts[{name, size, pivot, rotation}], animations[] | EntityModel.java | 模型类（Java代码） |
| `generate_entity_renderer` | entity_name, texture_description, glow_layer, scale | EntityRenderer.java | 渲染器 |
| `generate_entity_registration` | entity_name, spawn_egg_color_primary, spawn_egg_color_secondary | 注册代码+刷怪蛋 | |
| `describe_entity_texture` | entity_name, visual_description, has_glow_layer | 纹理Prompt | |
| `generate_entity_loot_table` | entity_name, drops[], xp_amount | JSON | |
| `generate_entity_sounds` | entity_name, sound_descriptions{ambient, hurt, death, step, ...} | SoundEvent注册 + sounds.json | |
| `generate_entity_ai_goals` | goals[{priority, type, params}] | AI目标代码 | |
| `generate_entity_spawn_eggs` | entity_name, primary_color, secondary_color | 刷怪蛋注册 | |
| `generate_entity_animation` | animation_name, keyframes[] | animation JSON | |

---

## 9. 投掷物/弹射物 (Projectile)

> 用户说："暗影龙要喷火球"

### 9.1 需要生成的文件

```
弹射物 (shadow_fireball) 需要生成:
├── Java代码
│   ├── entity/ShadowFireballEntity.java      # 弹射物实体（继承AbstractHurtingProjectile）
│   ├── entity/ShadowFireballRenderer.java    # 弹射物渲染器
│   └── registry/ModEntities.java             # 注册
├── 资源文件
│   ├── assets/<modid>/textures/entity/shadow_fireball.png    # 弹射物纹理
│   └── assets/<modid>/lang/...
└── (如果自定义爆炸效果)
    └── 事件监听或覆写onHit方法
```

> **Skill必需**: `projectile-guide.md` — **新建**：AbstractHurtingProjectile、ThrowableProjectile等基类、碰撞处理、弹道。

### 9.2 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_projectile_class` | name, damage, explosion_power, on_fire, particle_trail | Entity.java | |
| `generate_projectile_renderer` | name, texture_scale | Renderer.java | |
| `generate_projectile_registration` | name | 注册代码 | |

---

## 10. 粒子效果 (Particle)

> 用户说："暗影龙喷火时要有紫色火焰粒子"  
> 或者 "魔法蛋糕吃完要有蛋糕碎屑粒子"

### 10.1 需要生成的文件

```
粒子 (dragon_flame) 需要生成:
├── Java代码
│   ├── particle/DragonFlameParticle.java     # 粒子类（实现TextureSheetSprite）
│   ├── particle/DragonFlameParticleType.java  # ParticleType
│   ├── particle/DragonFlameParticleProvider.java # ParticleProvider（客户端）
│   ├── registry/ModParticles.java            # 粒子注册
│   └── event/ModClientEvents.java            # 注册ParticleProvider
├── 资源文件
│   ├── assets/<modid>/textures/particle/dragon_flame.png    # 粒子纹理（可以是精灵图）
│   └── assets/<modid>/particles/dragon_flame.json           # 粒子定义JSON（1.21+/26.x新格式）
└── 使用代码
    └── 在Entity/BlockEntity中使用 addParticle()
```

### 10.2 MC 26.x 新粒子系统

MC 26.x 引入了**粒子定义JSON**（类似旧版但更灵活）：
```json
// assets/<modid>/particles/dragon_flame.json
{
  "textures": ["<modid>:dragon_flame"],
  "lifetime": { "base": 20, "deviation": 5 }
}
```

> **Skill必需**: `particle-api-reference.md` — **新建**：ParticleEngine、粒子JSON格式、ParticleProvider注册、原版粒子类型全清单。

### 10.3 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_particle_class` | name, texture, lifetime, size, behavior{gravity, collision, fade} | Particle.java + Provider.java | |
| `generate_particle_definition_json` | name, textures[], lifetime, size | particles JSON | |
| `describe_particle_texture` | particle_name, visual_description, sprite_sheet_frames | 纹理Prompt | |

---

## 11. 声音 (Sound)

> 任何需要自定义声音的元素都需要

### 11.1 需要生成的文件

```
声音 (dragon_roar) 需要生成:
├── Java代码
│   └── registry/ModSounds.java              # SoundEvent注册
├── 资源文件
│   ├── assets/<modid>/sounds/dragon_roar.ogg       # 实际音频文件
│   └── assets/<modid>/sounds.json                  # 声音定义
```

### 11.2 sounds.json 格式
```json
{
  "entity.shadow_dragon.ambient": {
    "sounds": [
      { "name": "<modid>:entity/shadow_dragon/idle", "volume": 0.8, "pitch": 1.0 }
    ],
    "subtitle": "subtitles.entity.shadow_dragon.ambient"
  }
}
```

> **Skill必需**: `sounds-spec.md` — **新建**：sounds.json完整格式、sound event命名约定、.ogg文件要求、字幕key命名约定。

### 11.3 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_sound_event_registration` | sound_name | ModSounds.java片段 | |
| `generate_sounds_json` | sound_definitions[{name, files[], volume, pitch, stream, subtitle}] | sounds.json | |
| `describe_sound_requirements` | sound_description | 音频生成Prompt | 描述需要什么样的声音（供TTS或音效生成） |

---

## 12. 状态效果/药水 (MobEffect + Potion)

> 用户说："被暗影龙攻击后获得'暗影诅咒'效果，持续掉血+屏幕变紫"

### 12.1 需要生成的文件

```
效果 (shadow_curse) 需要生成:
├── Java代码
│   ├── effect/ShadowCurseEffect.java       # MobEffect子类
│   ├── registry/ModEffects.java            # 效果注册
│   ├── registry/ModPotions.java            # 药水注册（可选）
│   └── event/ModEvents.java                # 应用效果的逻辑
├── 资源文件
│   ├── assets/<modid>/textures/mob_effect/shadow_curse.png    # 效果图标（18×18）
│   └── assets/<modid>/lang/...
```

### 12.2 效果图标

- 尺寸：18×18像素
- 位置：物品栏右上角效果显示区

> **Skill必需**: `mobeffect-reference.md` — **新建**：MobEffect API、applyEffectTick、isDurationEffectTick、效果颜色。

### 12.3 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_mob_effect_class` | name, color, harmful, tick_interval, tick_logic | MobEffect.java | |
| `generate_effect_icon_texture` | name, color, icon_description | PNG (18×18) | |
| `generate_potion_registration` | effect_name, base_duration | 药水注册代码 | |

---

## 13. 附魔 (Enchantment)

### 13.1 需要生成的文件

```
附魔 (life_steal) 需要生成:
├── Java代码
│   ├── enchantment/LifeStealEnchantment.java   # 附魔类
│   ├── registry/ModEnchantments.java           # 注册
│   └── event/ModEvents.java                    # 附魔效果逻辑
└── 资源文件
    └── assets/<modid>/lang/...
```

> **Skill必需**: `enchantment-reference.md` — **新建**：Enchantment API（MC 26.x变化较大）、附魔分类、附魔等级、附魔效果事件。

### 13.2 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_enchantment_class` | name, rarity, max_level, compatible_slots, effect_description | Enchantment.java | |
| `generate_enchantment_effect_code` | enchantment_name, effect_description, trigger_event | 事件代码 | |

---

## 14. 流体 (Fluid)

### 14.1 需要生成的文件

```
流体 (liquid_shadow) 需要生成:
├── Java代码
│   ├── fluid/ShadowFluid.java            # Fluid + Flowing/FluidType
│   ├── block/ShadowFluidBlock.java       # 流体方块
│   ├── registry/ModFluids.java
│   └── registry/ModBlocks.java
├── 资源文件
│   ├── assets/<modid>/textures/block/shadow_fluid_still.png     # 静止纹理（16×512）
│   ├── assets/<modid>/textures/block/shadow_fluid_flowing.png   # 流动纹理（32×1024）
│   └── assets/<modid>/lang/...
└── 数据文件
    └── data/<modid>/tags/fluids/...
```

### 14.2 流体纹理特殊性

流体纹理是**动画纹理**：
- 静止贴图：16×512像素（16×16 的32帧垂直排列）
- 流动贴图：32×1024像素（32×32 的32帧垂直排列）
- `.mcmeta` 文件控制动画速度

> **Skill必需**: `fluid-guide.md` — **新建**：FluidType体系、流体纹理动画格式、.mcmeta animation配置。

### 14.3 需要的 Tool

| Tool | 输入 | 输出 | 说明 |
|------|------|------|------|
| `generate_fluid_classes` | name, color, viscosity, density, luminance, damage | Fluid全套类 | |
| `describe_fluid_texture` | fluid_name, color, animation_description | 动画纹理Prompt（含尺寸说明） | |
| `generate_fluid_mcmeta_animation` | frame_count, frametime | .mcmeta文件 | |

---

## 15. 世界生成 (Ore/Structure/Biome)

> 用户说："在世界中生成'虚空晶石矿石'" 或 "添加一个暗影龙巢穴结构"

### 15.1 需要生成的文件

```
矿石生成 (void_crystal_ore) 需要生成:
├── Java代码
│   └── worldgen/ModWorldGen.java            # 矿石生成逻辑（BiomeModifier）
├── 数据文件
│   ├── data/<modid>/worldgen/configured_feature/void_crystal_ore.json
│   ├── data/<modid>/worldgen/placed_feature/void_crystal_ore.json
│   └── data/<modid>/neoforge/biome_modifier/add_void_crystal_ore.json
└── 方块本身（按方块类型生成）
```

### 15.2 MC 26.x 世界生成体系

26.x 使用**JSON数据驱动**的世界生成：
- `configured_feature` → 定义"生成什么"（矿石类型、数量）
- `placed_feature` → 定义"在哪生成"（高度、频率、生物群系过滤）
- `biome_modifier` → NeoForge特有，将feature注入生物群系

> **Skill必需**: `worldgen-guide.md` — 所有configured_feature/placed_feature/biome_modifier的JSON格式。

### 15.3 结构生成

结构更复杂，需要：
- 结构NBT文件（用structure block导出）
- 结构模板池JSON（如果是拼图结构）
- 结构set JSON
- BiomeModifier关联

> **Skill必需**: `structure-guide.md` — **新建**：Jigsaw/Structure体系、template_pool、processor_list。

---

## 16. 村民交易/职业 (Villager)

> 用户说："添加一个'宝石商人'村民，出售龙鳞"

### 16.1 需要生成的文件

```
村民职业 (gem_merchant) 需要生成:
├── Java代码
│   ├── registry/ModVillagerProfessions.java  # 职业+POI注册
│   └── event/ModEvents.java                  # 交易注册（VillagerTradesEvent）
├── 资源文件
│   └── assets/<modid>/lang/...
└── 数据文件
    └── data/<modid>/tags/worldgen/point_of_interest_type/acquirable_job_site.json
```

> **Skill必需**: `villager-guide.md` — **新建**：VillagerProfession注册、PoiType注册、VillagerTradesEvent、交易列表构建。

---

## 17. 网络数据包 (Networking Payload)

> 任何需要在服务端↔客户端同步自定义数据的场景

### 17.1 需要生成的文件

```
网络包 (sync_progress) 需要生成:
├── Java代码
│   ├── network/SyncProgressPacket.java      # Payload定义（Record）
│   ├── network/ModNetworking.java           # 注册（追加）
│   └── 发送方/接收方处理代码
```

### 17.2 MC 26.x Payload 模板

```java
public record SyncProgressPacket(int progress, BlockPos pos) implements CustomPacketPayload {
    public static final Type<SyncProgressPacket> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(MODID, "sync_progress"));
    public static final StreamCodec<RegistryFriendlyByteBuf, SyncProgressPacket> STREAM_CODEC = StreamCodec.composite(
        ByteBufCodecs.VAR_INT, SyncProgressPacket::progress,
        BlockPos.STREAM_CODEC, SyncProgressPacket::pos,
        SyncProgressPacket::new
    );
    @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
```

> **Skill必需**: `networking-guide.md` — Payload注册、StreamCodec、PacketDistributor。

---

## 18. 纹理/图片资源生成（重点）

这是你说的核心问题。Agent生成mod时，**纹理是必须的**。但Agent自己不会画画，所以需要两种方案：

### 方案A：生成纹理描述 → 用户自己提供/调用外部图片生成服务

Agent通过Tool输出精确的纹理需求描述，用户可以将这些prompt输入到图片生成工具中。

| 纹理类型 | 尺寸 | 格式 | 描述Tool |
|---------|------|------|---------|
| 物品纹理 | 16×16或32×32 | PNG, 透明背景 | `describe_item_texture` |
| 方块纹理（单面） | 16×16 | PNG | `describe_block_textures` (指定face) |
| 方块纹理（顶面） | 16×16 | PNG | `describe_block_textures` (face=top) |
| 方块纹理（侧面） | 16×16 | PNG | `describe_block_textures` (face=side) |
| 方块纹理（正面） | 16×16 | PNG | `describe_block_textures` (face=front) |
| 盔甲穿戴层1 | 64×64 | PNG | `describe_armor_texture` (layer=1) |
| 盔甲穿戴层2 | 64×64 | PNG | `describe_armor_texture` (layer=2) |
| 盔甲物品图标 | 16×16 | PNG | `describe_armor_item_icon` |
| 实体纹理 | 64×64或128×128 | PNG | `describe_entity_texture` |
| 实体发光层 | 64×64 | PNG | `describe_entity_texture` (glow=true) |
| GUI纹理 | 256×256 | PNG | `describe_gui_texture` |
| 粒子纹理（单帧） | 8×8~16×16 | PNG | `describe_particle_texture` |
| 粒子纹理（精灵图） | 16×(16×N) | PNG | `describe_particle_texture` (frames=N) |
| 流体静止纹理 | 16×512 | PNG | `describe_fluid_texture` (still) |
| 流体流动纹理 | 32×1024 | PNG | `describe_fluid_texture` (flowing) |
| 效果图标 | 18×18 | PNG | `describe_effect_icon` |
| 声音.ogg | — | OGG Vorbis | `describe_sound_requirements` |

### 方案B：生成占位纹理

如果用户暂时没有纹理，Agent可以用Tool生成带文字标注的占位PNG（纯色背景+白色文字），让mod可以**先跑起来**，纹理后续再替换。

> **Tool必需**: `generate_placeholder_texture` — 输入name, color, size → 输出一个PNG文件，包含名字文字。
> **Tool必需**: `generate_all_placeholder_textures_for_element` — 输入element_type, name → 一键生成该元素需要的所有占位纹理。

### 18.1 纹理描述Tool的详细输出格式

`describe_block_textures` 输出示例：
```json
{
  "element": "block",
  "name": "void_crystal",
  "textures": {
    "all": null,  // 如果使用cube_all则六个面都一样
    "top": {
      "path": "assets/modid/textures/block/void_crystal_top.png",
      "size": "16x16",
      "prompt": "Top face of a dark purple crystal block with glowing cyan veins, Minecraft vanilla 16x16 pixel art style, flat top-down view, seamless tiling"
    },
    "side": {
      "path": "assets/modid/textures/block/void_crystal_side.png",
      "size": "16x16",
      "prompt": "Side face of a dark purple crystal block with layered crystalline structure, vertical cyan glow streaks, Minecraft vanilla 16x16 pixel art style, seamless tiling"
    },
    "bottom": {
      "path": "assets/modid/textures/block/void_crystal_bottom.png",
      "size": "16x16",
      "prompt": "Bottom face of a dark purple crystal block, rough dark stone-like texture, Minecraft vanilla 16x16 pixel art style, seamless tiling"
    }
  }
}
```

---

## 19. Skill 文档完整清单（落地版）

以下是最终需要写入 `skill/` 目录的所有 `.md` 文件。Agent通过 `load_skill` 接口按需读取。

### 🔴 第一批（最高优先级 — 没有这些Agent寸步难行）

| # | 文件名 | 内容 | 覆盖的元素类型 |
|---|--------|------|---------------|
| 1 | `version-matrix.md` | MC ↔ NeoForge ↔ JDK兼容矩阵 | 全部 |
| 2 | `registry-reference.md` | 所有Registry类型的DeferredRegister模板 | 全部 |
| 3 | `neoforge-mods-toml-spec.md` | neoforge.mods.toml完整格式 | 全部 |
| 4 | `gradle-config-guide.md` | build.gradle/settings.gradle/gradle.properties精确模板 | 全部 |

### 🟡 第二批（高优先级 — 核心元素生成必备）

| # | 文件名 | 内容 | 覆盖的元素类型 |
|---|--------|------|---------------|
| 5 | `block-api-reference.md` | Block体系、BlockBehaviour.Properties、所有Base Block类选择指南 | 方块、BlockEntity、流体 |
| 6 | `blockstate-spec.md` | 所有原版BlockState属性+facing/half等variants格式 | 方块 |
| 7 | `block-model-spec.md` | 所有方块模型parent类型(cube_all/cube/cube_bottom_top/stairs/slab等) | 方块 |
| 8 | `item-api-reference.md` | Item体系、Item.Properties、工具Tier、食物FoodProperties、盔甲ArmorMaterial | 物品、工具、食物、盔甲 |
| 9 | `item-model-spec.md` | 物品模型JSON格式(generated/handheld/parent) | 物品、工具、食物、盔甲 |
| 10 | `event-dictionary.md` | 所有MOD Bus + Neo Bus事件的完整字典 | 工具(攻击)、食物(吃)、盔甲(效果)、实体、BlockEntity |
| 11 | `recipe-types.md` | 所有配方类型JSON格式（含MC 26.x新result格式） | 物品、方块、工具、食物、盔甲 |
| 12 | `tag-guide.md` | 所有原版标签清单(mineable/needs_tool/等) + 自定义标签格式 | 方块、物品、实体 |
| 13 | `loot-table-spec.md` | 掉落表条件/函数/池全部类型 | 方块、实体 |
| 14 | `component-system.md` | MC 26.x Data Component系统（替代NBT） | 物品、工具、盔甲、食物 |
| 15 | `common-mistakes.md` | 常见编译/运行时错误及解决方案 | 全部 |
| 16 | `migration-guide-1_21-to-26.md` | 1.21.x→26.x变更清单 | 全部 |

### 🟢 第三批（中优先级 — 高级元素）

| # | 文件名 | 内容 | 覆盖的元素类型 |
|---|--------|------|---------------|
| 17 | `blockentity-guide.md` | BlockEntity生命周期/tick/NBT/ItemStackHandler | BlockEntity |
| 18 | `gui-container-guide.md` | Menu+Screen体系完整教程 | 容器GUI |
| 19 | `gui-texture-spec.md` | **新建**：GUI纹理尺寸标准、槽位坐标约定 | 容器GUI |
| 20 | `entity-guide.md` | **新建**：Entity完整教程 | 实体、弹射物 |
| 21 | `entity-model-guide.md` | **新建**：EntityModel+LayerDefinition | 实体 |
| 22 | `entity-rendering-guide.md` | **新建**：EntityRenderer体系 | 实体、弹射物 |
| 23 | `entity-ai-guide.md` | **新建**：Goal/Brain AI体系 | 实体 |
| 24 | `projectile-guide.md` | **新建**：弹射物基类+碰撞处理 | 弹射物 |
| 25 | `particle-api-reference.md` | **新建**：粒子系统完整API + MC 26.x粒子JSON | 粒子、工具(攻击)、食物(吃)、实体 |
| 26 | `sounds-spec.md` | **新建**：sounds.json格式+SoundEvent注册+.ogg要求 | 声音、实体、方块 |
| 27 | `armor-texture-mapping.md` | **新建**：layer_1/layer_2 UV映射图 | 盔甲 |
| 28 | `mobeffect-reference.md` | **新建**：MobEffect API | 效果、药水、食物 |
| 29 | `enchantment-reference.md` | **新建**：Enchantment API（MC 26.x） | 附魔 |
| 30 | `worldgen-guide.md` | ConfiguredFeature/PlacedFeature/BiomeModifier JSON | 世界生成 |
| 31 | `structure-guide.md` | **新建**：Jigsaw/Structure体系 | 结构 |
| 32 | `fluid-guide.md` | **新建**：FluidType+流体纹理动画 | 流体 |
| 33 | `villager-guide.md` | **新建**：村民职业+交易 | 村民 |
| 34 | `networking-guide.md` | Payload定义+StreamCodec+PacketDistributor | 网络、BlockEntity、实体 |
| 35 | `damage-type-reference.md` | **新建**：DamageType体系（MC 26.x） | 盔甲、实体、效果 |
| 36 | `tier-definition-guide.md` | **新建**：Tier接口详解+BlockTags映射 | 工具 |

### 🔵 第四批（低优先级 — 发布/调试）

| # | 文件名 | 内容 |
|---|--------|------|
| 37 | `modrinth-curseforge-publishing.md` | 发布到Modrinth/CurseForge |
| 38 | `rendering-guide.md` | 高级渲染（BER、Shader、PoseStack） |
| 39 | `mixin-reference.md` | Mixin注入参考手册 |
| 40 | `texture-standards.md` | **新建**：所有纹理类型的尺寸/格式/命名约定总表 |

---

## 20. Tool 接口完整清单（落地版）

### 20.1 按功能分类汇总

#### A. 项目脚手架（5个）

| Tool | 输入 | 输出 |
|------|------|------|
| `scaffold_mod_project` | mod_id, mod_name, mc_version, package_path, author | 完整项目目录+所有模板文件 |
| `generate_gradle_config` | mc_version, mod_id | build.gradle + settings.gradle + gradle.properties |
| `generate_mods_toml` | mod_id, version, display_name, description, dependencies[] | neoforge.mods.toml |
| `validate_mod_structure` | project_root_path | 完整性报告 |
| `check_dependency_compatibility` | mc_version, deps{} | 兼容性报告 |

#### B. 方块（8个）

| Tool | 说明 |
|------|------|
| `generate_block_class` | 方块Java类 |
| `generate_block_registration` | 注册代码 |
| `generate_blockstate_json` | 方块状态JSON |
| `generate_block_model_json` | 方块模型JSON |
| `generate_item_block_model_json` | 物品形态模型JSON |
| `generate_loot_table_json` | 掉落表 |
| `generate_block_tags` | 方块标签 |
| `describe_block_textures` | 纹理描述（支持1面或6面） |

#### C. 物品/工具/食物/盔甲（10个）

| Tool | 说明 |
|------|------|
| `generate_item_registration` | 简单物品注册 |
| `generate_tool_class` | 工具类 |
| `generate_tier_definition` | Tier定义 |
| `generate_armor_set` | 整套盔甲 |
| `generate_food_item` | 食物（含效果） |
| `generate_item_model_json` | 物品模型JSON |
| `describe_item_texture` | 物品纹理Prompt |
| `describe_armor_texture` | 盔甲穿戴纹理Prompt |
| `describe_armor_item_icon` | 盔甲图标Prompt |
| `describe_food_texture` | 食物纹理Prompt |

#### D. 实体/生物/弹射物（10个）

| Tool | 说明 |
|------|------|
| `generate_entity_class` | 实体类 |
| `generate_entity_model` | 实体模型 |
| `generate_entity_renderer` | 实体渲染器 |
| `generate_entity_registration` | 实体+刷怪蛋注册 |
| `generate_entity_loot_table` | 实体掉落表 |
| `generate_entity_sounds` | 声音注册 |
| `generate_entity_ai_goals` | AI目标 |
| `generate_entity_spawn_eggs` | 刷怪蛋 |
| `generate_projectile_class` | 弹射物类 |
| `generate_projectile_renderer` | 弹射物渲染器 |

#### E. BlockEntity / GUI（8个）

| Tool | 说明 |
|------|------|
| `generate_blockentity_class` | BlockEntity类 |
| `generate_blockentity_registration` | 注册 |
| `generate_blockentity_block_class` | 关联方块 |
| `generate_menu_class` | Menu类 |
| `generate_screen_class` | Screen类 |
| `describe_gui_texture` | GUI纹理Prompt |
| `generate_container_data_sync` | 数据同步代码 |
| `generate_quick_move_logic` | quickMoveStack代码 |

#### F. 粒子/声音/效果/附魔/流体（12个）

| Tool | 说明 |
|------|------|
| `generate_particle_class` | 粒子类 |
| `generate_particle_definition_json` | 粒子JSON |
| `describe_particle_texture` | 粒子纹理Prompt |
| `generate_sound_event_registration` | 声音事件注册 |
| `generate_sounds_json` | sounds.json |
| `describe_sound_requirements` | 声音Prompt |
| `generate_mob_effect_class` | 效果类 |
| `generate_effect_icon_texture` | 效果图标 |
| `generate_potion_registration` | 药水注册 |
| `generate_enchantment_class` | 附魔类 |
| `generate_fluid_classes` | 流体类 |
| `describe_fluid_texture` | 流体动画纹理Prompt |

#### G. 事件/行为代码（6个）

| Tool | 说明 |
|------|------|
| `generate_attack_particle_effect` | 攻击粒子代码 |
| `generate_food_eat_particle_code` | 食物粒子代码 |
| `generate_armor_effect_code` | 盔甲特殊效果代码 |
| `generate_enchantment_effect_code` | 附魔效果代码 |
| `generate_block_right_click_behavior` | 方块右键行为 |
| `generate_entity_attack_behavior` | 实体攻击行为 |

#### H. 验证/调试（5个）

| Tool | 说明 |
|------|------|
| `validate_mod_structure` | 完整性验证 |
| `check_classpath_for_errors` | API使用检查 |
| `generate_mod_asset_checklist` | 资源完整性清单 |
| `check_missing_textures` | 缺失纹理检查 |
| `check_missing_language_entries` | 缺失翻译检查 |

#### I. 全局工具（5个）

| Tool | 说明 |
|------|------|
| `query_latest_mc_versions` | 版本查询 |
| `query_mod_api_usage` | API文档查询 |
| `generate_language_entry` | 翻译条目生成 |
| `generate_recipe_json` | 配方JSON |
| `add_to_creative_tab` | 创造标签页追加 |

---

## 21. 跨元素共享的公用 Skill/Tool

### 21.1 每个元素都需要的公用 Skill

| Skill | 为什么每个元素都需要 |
|-------|-------------------|
| `registry-reference.md` | 所有内容都需要注册 |
| `event-dictionary.md` | 大部分有特殊行为的元素需要事件监听 |
| `component-system.md` | MC 26.x Data Component渗透到所有物品相关 |
| `common-mistakes.md` | 避免重复错误 |
| `tag-guide.md` | 方块需要工具标签、物品需要分类标签、实体需要实体标签 |
| `recipe-types.md` | 任何可合成的东西都需要 |

### 21.2 每个元素都需要的公用 Tool

| Tool | 为什么 |
|------|--------|
| `generate_language_entry` | 所有元素都需要翻译 |
| `add_to_creative_tab` | 所有物品/方块需要放创造模式 |
| `generate_recipe_json` | 任何可合成的东西 |

### 21.3 纹理描述类Tool的设计原则

所有 `describe_*_texture` 系列Tool应输出统一格式：
```json
{
  "texture_paths": ["<modid>:block/name_top.png", "..."],
  "each": {
    "path": "...",
    "size": "16x16",
    "prompt": "英文Prompt供AI图片生成",
    "prompt_zh": "中文描述供用户理解",
    "style_notes": "Minecraft vanilla pixel art, 16x16, seamless tiling if applicable"
  }
}
```

---

## 附录：每个元素类型 → 所需Skill+Tool 速查表

| 元素类型 | 必需Skill数量 | 必需Tool数量 | 最关键的Skill | 最关键的Tool |
|---------|-------------|-------------|--------------|-------------|
| 简单物品 | 7 | 6 | item-api-reference, item-model-spec | generate_item_model_json, describe_item_texture |
| 方块（简单） | 9 | 8 | block-model-spec, blockstate-spec | generate_blockstate_json, describe_block_textures |
| 方块（六个面不同） | 9 | 9 | block-model-spec, blockstate-spec | describe_block_textures (生成6个面的prompt) |
| 工具 | 8 | 5 | tier-definition-guide, item-api-reference | generate_tool_class, describe_tool_texture |
| 食物 | 8 | 5 | item-api-reference, mobeffect-reference | generate_food_item, generate_food_eat_particle_code |
| 盔甲 | 8 | 5 | armor-texture-mapping, item-api-reference | generate_armor_set, describe_armor_texture |
| BlockEntity | 10 | 8 | blockentity-guide, gui-container-guide | generate_blockentity_class, describe_gui_texture |
| 实体 | 13 | 10 | entity-guide, entity-model-guide, entity-ai-guide | generate_entity_class, describe_entity_texture |
| 弹射物 | 9 | 3 | projectile-guide | generate_projectile_class |
| 粒子 | 5 | 3 | particle-api-reference | generate_particle_class |
| 声音 | 3 | 3 | sounds-spec | generate_sounds_json |
| 效果/药水 | 5 | 4 | mobeffect-reference | generate_mob_effect_class |
| 附魔 | 5 | 3 | enchantment-reference | generate_enchantment_class |
| 流体 | 6 | 4 | fluid-guide | describe_fluid_texture |
| 世界生成(矿石) | 6 | 3 | worldgen-guide | (主要是JSON生成) |
| 结构 | 8 | 4 | structure-guide, worldgen-guide | (需要NBT+JSON) |
| 村民 | 5 | 3 | villager-guide | (注册+交易代码) |
| 网络包 | 3 | 2 | networking-guide | (代码生成) |

---

## 总结：最小可行 Skill 集（MVP）

如果只能先写 **10个Skill**，它们的优先级是：

1. `version-matrix.md` — 没有这个连build.gradle都写不对
2. `registry-reference.md` — 所有注册都在这里
3. `block-api-reference.md` + `block-model-spec.md` + `blockstate-spec.md` — 方块三件套
4. `item-api-reference.md` + `item-model-spec.md` — 物品二件套
5. `event-dictionary.md` — 所有行为逻辑
6. `recipe-types.md` — 合成配方
7. `tag-guide.md` — 标签系统
8. `loot-table-spec.md` — 掉落表
9. `networking-guide.md` — 网络同步
10. `common-mistakes.md` — 排错手册

如果只能先做 **10个Tool**，它们的优先级是：

1. `scaffold_mod_project` — 脚手架
2. `generate_mods_toml` — 元数据
3. `generate_block_registration` + `generate_block_model_json` + `generate_blockstate_json` — 方块核心
4. `describe_block_textures` — 方块纹理描述（最重要！覆盖6面）
5. `generate_item_registration` + `generate_item_model_json` — 物品核心
6. `describe_item_texture` — 物品纹理描述
7. `generate_language_entry` — 翻译
8. `generate_loot_table_json` — 掉落表
9. `generate_recipe_json` — 配方
10. `validate_mod_structure` — 验证

---

*基于NeoForge MC 26.2 + Forge 65.1.0 当前最新生态编写。AI Agent应当能通过 `load_skill` 接口按需查阅上述Skill文档，通过 `tool_call` 接口调用上述Tool函数。*