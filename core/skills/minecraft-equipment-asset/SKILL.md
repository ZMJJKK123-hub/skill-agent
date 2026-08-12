---
name: minecraft-equipment-asset
description: |
  装备资产（Minecraft Wiki 中文版全量正文）。
  
  【概述】装备资产（Equipment Asset），曾称装备模型（Equipment Model），是对盔甲类装备外观的核心定义。
  
  【涵盖内容】
  - （自动提取章节）
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 装备资产 的完整规范时
---

本条目所述内容仅适用于Java版。
装备资产（Equipment Asset），曾称装备模型（Equipment Model），是对盔甲类装备外观的核心定义。

# 定义格式

装备资产定义文件都在资源包
```
assets/<
命名空间
>/equipment
```

目录内，且均为JSON文件。

此文件的格式如下：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]layers：装备在各个不同的装备槽位时，在生物身上渲染的模型。 - [图:NBT列表/JSON数组]<预设模型类型>：当装备模型在某个生物身上渲染时，游戏会根据生物对应的预设模型层类型选择使用哪个具体的模型层信息。预设模型见下文。 - [图:NBT复合标签/JSON对象]：一项模型层信息。 - [图:NBT复合标签/JSON对象]dyeable：设置此模型层受到染色影响，其颜色会由dyed_color物品堆叠组件决定。此项不存在时物品的染色无法影响模型层的渲染。 - [图:整型][图:NBT列表/JSON数组]color_when_undyed：物品未被染色时，模型层的着色。如果此项不存在，当物品未着色时模型层直接不着色，使用纹理本来的颜色。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:字符串]*texture：（命名空间ID）模型使用的纹理，纹理将被如何切分和绑定取决于选择的预设模型类型。游戏在渲染时将此值解析为 ``` assets/< 命名空间 >/textures/entity/equipment/< 预设模型类型 >/< 路径 >.png ``` 。 - [图:布尔型]use_player_texture：（默认为 ``` false ``` ）如果预设模型类型为 ``` wings ``` ，此值代表是否使用玩家披风纹理渲染翅膀模型。 - [图:NBT复合标签/JSON对象]trim_palette_replacements：纹饰调色板置换规则。如果目前使用此装备资产的装备的盔甲纹饰数据的调色板ID在此映射中，则使用对应的替换调色板。参见盔甲纹饰定义格式 § 纹理。 - [图:字符串]<调色板命名空间ID>：（命名空间ID）要覆盖使用的调色板ID。

# 定义行为

装备资产定义了特定模型层上渲染指定纹理的映射：每一个装备资产都定义了它在特定模型层上应该使用何种纹理。

游戏提供了以下可被装备资产使用的预设模型类型：

人形盔甲

- ``` humanoid ``` ：人形生物（玩家、玩家模型、盔甲架、巨人、猪灵、猪灵蛮兵、僵尸类生物和骷髅类生物）的头部、胸部和脚部盔甲模型。
- ``` humanoid_leggings ``` ：人形生物的腿部盔甲模型。
- ``` humanoid_baby ``` ：除盔甲架外，幼年人形生物的盔甲模型，此模型层无法渲染盔甲纹饰。对于这些生物的幼年个体，将只渲染此模型，而不渲染 ``` humanoid ``` 和 ``` humanoid_leggings ``` 。
- ``` wings ``` ：玩家、玩家模型和盔甲架的翅膀模型。此模型使用胸部盔甲模型且可以和 ``` humanoid ``` 的胸部盔甲模型共存。如果游戏渲染了此模型，就不会渲染披风模型。

动物盔甲

- ``` wolf_body ``` ：狼的身体盔甲模型。
- ``` horse_body ``` ：马、骷髅马和僵尸马的身体盔甲模型。
- ``` llama_body ``` ：羊驼和行商羊驼的身体盔甲模型。
- ``` happy_ghast_body ``` ：快乐恶魂的身体盔甲模型。
- ``` nautilus_body ``` ：鹦鹉螺和僵尸鹦鹉螺的身体盔甲模型。

鞍

- ``` pig_saddle ``` ：猪的鞍模型。
- ``` strider_saddle ``` ：炽足兽的鞍模型。
- ``` camel_saddle ``` ：骆驼的鞍模型。
- ``` camel_husk_saddle ``` ：骆驼尸壳的鞍模型。
- ``` horse_saddle ``` ：马的鞍模型。
- ``` donkey_saddle ``` ：驴的鞍模型。
- ``` mule_saddle ``` ：骡的鞍模型。
- ``` skeleton_horse_saddle ``` ：骷髅马的鞍模型。
- ``` zombie_horse_saddle ``` ：僵尸马的鞍模型。
- ``` nautilus_saddle ``` ：鹦鹉螺和僵尸鹦鹉螺的鞍模型。

游戏在渲染盔甲模型时，只要对应的盔甲槽位吻合，游戏就会渲染对应预设模型类型的模型层。如果盔甲模型没有设置对应预设模型类型的模型层，那么游戏就不渲染对应的模型。当
```
humanoid
```

和
```
wings
```

同时存在时，这两个模型可被同时渲染。

# 历史

# 参考

1. ↑ Minecraft Snapshot 25w03a — Minecraft.net。
1. ↑ Minecraft Snapshot 24w36a — Minecraft.net。

# 导航
