---
name: minecraft-tutorial-custom-armor-trim
description: |
  Tutorial:自定义盔甲纹饰（Minecraft Wiki 中文版全量正文）。
  
  【概述】本教程介绍的是基于1.21.5后版本的教程。关于旧版教程，请见“Tutorial:自定义盔甲纹饰/旧版”。
  
  【涵盖内容】
  - 配方
  - 盔甲纹饰图案
  - 盔甲纹饰材料
  - 装备模型
  - 物品模型
  
  【关键定义】
  - 数据包路径：data/minecraft/atlas/armor_trims.json、data/minecraft/atlas/blocks.json
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Tutorial:自定义盔甲纹饰 的完整规范时
---

本教程介绍的是基于1.21.5后版本的教程。关于旧版教程，请见“Tutorial:自定义盔甲纹饰/旧版”。

本教程所述内容仅适用于Java版。
该教程将告诉你如何通过数据包以及资源包来添加锻造原材料或盔甲纹饰。阅读本文章前，请确保你已经知道了如何制作数据包。

# 数据包

## 配方

主条目：配方 § 盔甲纹饰配方
网页生成器：Misode/Recipe

锻造台的UI界面中从左到右有3个合成输入槽以及1个输出槽。我们的目标是制作一个盔甲纹饰配方。

输入槽

- 第一个输入槽用于放置模板（Template）。

每个模板都唯一对应一个物品。

- 第二个输入槽用于放置要进行锻造处理的物品（一般为各种盔甲），也即基础物品（Base）。
- 第三个输入槽用于放置附加物（Addition）。

填充物一般为锻造原材料
```
#minecraft:trim_materials
```

（如果你希望该配方还可以使用原版所定义的钻石、红石、金锭等锻造原材料合成，则应直接在该物品标签中新增一个物品，然后使用该物品标签作为附加物）
本教程中，限定只能使用竹子附加烈焰粉来为原版的所有可锻造盔甲添加纹饰，则配方JSON应为：

[图:File file.png：Minecraft中file的精灵图] 
```
example:bamboo_smithing_trim
```

json

```
{

  
"type"
:
 
"minecraft:smithing_trim"
,

  
"template"
:
 
"minecraft:bamboo"
,

  
"base"
:
 
"#minecraft:trimmable_armor"
,

  
"addition"
:
 
"minecraft:blaze_powder"
,

  
"pattern"
:
 
"example:bamboo"

}
```

- 物品标签 ``` #minecraft:trimmable_armor ``` 表示所有可添加盔甲纹饰的盔甲。你也可以在其中新增其他物品。
- 这段代码可以复制到生成器中，同时可预览这些物品放在锻造台UI内的效果。
- 在生成器中，你可以通过快捷键Ctrl+S保存到网页上的数据包目录中。

## 盔甲纹饰图案

主条目：盔甲纹饰定义格式 § 盔甲纹饰图案
在上一节中，你应该学会了用网页生成器生成数据包代码并保存为临时文件。接下来我们继续完善——添加配方中的纹饰图案[图:字符串]pattern定义文件。

[图:File file.png：Minecraft中file的精灵图] 
```
example:bamboo
```

json

```
{

  
"asset_id"
:
 
"example:bamboo"
,

  
"description"
:
 
{

    
"translate"
:
 
"trim_pattern.example.bamboo"
,

    
"fallback"
:
 
"Bamboo Trim"

  
},

  
"decal"
:
 
true

}
```

## 盔甲纹饰材料

主条目：盔甲纹饰定义格式 § 盔甲纹饰材料
 参见：数据组件 § provides_trim_material 
纹饰图案由上述的盔甲纹饰锻造配方唯一确定，但纹饰材料不同——它在配方中没有相应的定义字段，由物品上的数据组件
```
provides_trim_material
```

确定。

我们希望烈焰粉作为附加物并提供纹饰材料。执行如下命令：

```
give
 
@s
 
blaze_powder
[
provides_trim_material
=
"example:blaze_powder"
]
```

- 该烈焰粉便可作为用于盔甲纹饰合成的特殊烈焰粉。

接着定义相应的纹饰材料：

[图:File file.png：Minecraft中file的精灵图] 
```
example:blaze
```

json

```
{

  
"asset_name"
:
 
"blaze"
,

  
"description"
:
 
{

    
"translate"
:
 
"trim_material.example.blaze"
,

    
"fallback"
:
 
"Blaze Trim Material"

  
}

}
```

# 资源包

相关生成器页面：Misode/Atlas、Misode/Item
以上完成了数据部分的基础工作。但是只制作数据包还不够，游戏目前还不知道相应的纹饰图案纹理以及颜色。所以接下来我们制作相应的资源包。

## 装备模型

 参见：装备模型和纹理 § 图集 
装备模型上附带纹饰的纹理也使用图集产生。原版的物品纹饰纹理定义在
```
minecraft/atlas/armor_trims.json
```

中，我们也需要使用同名文件以合并内容。

这里需要先绘制2张纹理，分别对应到
```
humanoid
```

和
```
humanoid_leggings
```

装备模型。可以在BlockBench中创建皮肤，在弹窗分类中选择“Armor（Main）”或“Armor（Leggings）”，这样便可以边预览边绘制。在绘制时，可以把调色板全部复制到纹理的空白处，方便取色。

- 调色板键到调色板排列的映射，实际上是将每个调色板图片视作数组进行一一对应，然后改变目标纹理中的相应颜色。如果目标纹理中存在调色板键以外的像素，则不做改变这些像素。

[图:File file.png：Minecraft中file的精灵图] 
```
minecraft:armor_trims
```

json

```
{

  
"sources"
:
 
[

    
{

      
"type"
:
 
"paletted_permutations"
,

      
"textures"
:
 
[

        
"example
:
trims/entity/humanoid/bamboo
",

        
"example:trims/entity/humanoid_leggings/bamboo"

      
],

      
"palette_key"
:
 
"minecraft:trims/color_palettes/trim_palette"
,

      
"permutations"
:
 
{

        
"blaze"
:
 
"example:trims/color_palettes/blaze"

      
}

    
}

  
]

}
```

- ``` palette_key ``` 定义了原灰度颜色。
- ``` permutations ``` 定义了纹饰材料所对应的颜色。这里的纹饰材料使用其[图:字符串]asset_name表示。
- ``` textures ``` 定义了要被“染色”的纹理。
- 该文件如果被游戏正常加载，不会覆盖原版资源包中的 ``` minecraft/atlas/armor_trims.json ``` ，而是在其基础上进行增添。

## 物品模型

 参见：物品模型映射和纹理 § 图集 
物品模型纹理使用图集产生。原版的物品纹饰纹理定义在
```
minecraft/atlas/blocks.json
```

中，我们也需要使用同名文件以合并内容。

本教程直接使用原版的物品纹饰纹理。

[图:File file.png：Minecraft中file的精灵图] 
```
minecraft:blocks
```

json

```
{

  
"sources"
:
 
[

    
{

      
"type"
:
 
"paletted_permutations"
,

      
"palette_key"
:
 
"minecraft:trims/color_palettes/trim_palette"
,

      
"permutations"
:
 
{

        
"blaze"
:
 
"example:trims/color_palettes/blaze"

      
},

      
"textures"
:
 
[

        
"minecraft
:
trims/items/helmet_trim
",

        
"minecraft:trims/items/chestplate_trim"
,

        
"minecraft:trims/items/leggings_trim"
,

        
"minecraft:trims/items/boots_trim"

      
]

    
}

  
]

}
```

- 以上图集会将 ``` textures ``` 中的每个元素和 ``` permutations ``` 中的每个键进行组合，随后将产生4个新的带 ``` blaze ``` 后缀的纹理。比如 ``` minecraft:trims/items/helmet_trim_blaze ```

以上图集能够产生所有被染色后的纹饰图案。那么物品是如何选择到这些纹饰图案的纹理的？很简单，游戏将读取物品的
```
trim
```

数据组件，然后根据
```
trim
```

组件的值选择对应的物品模型。

以下即铁胸甲的物品模型映射文件——它将根据
```
trim
```

中存储的纹饰材料选择物品模型。其他盔甲（护腿、头盔）同理：

[图:File file.png：Minecraft中file的精灵图] 
```
minecraft:iron_chestplate
```

json

...

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:select"
,

    
"cases"
:
 
[

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_quartz_trim"

        
},

        
"when"
:
 
"minecraft:quartz"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_iron_trim"

        
},

        
"when"
:
 
"minecraft:iron"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_netherite_trim"

        
},

        
"when"
:
 
"minecraft:netherite"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_redstone_trim"

        
},

        
"when"
:
 
"minecraft:redstone"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_copper_trim"

        
},

        
"when"
:
 
"minecraft:copper"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_gold_trim"

        
},

        
"when"
:
 
"minecraft:gold"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_emerald_trim"

        
},

        
"when"
:
 
"minecraft:emerald"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_diamond_trim"

        
},

        
"when"
:
 
"minecraft:diamond"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_lapis_trim"

        
},

        
"when"
:
 
"minecraft:lapis"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_amethyst_trim"

        
},

        
"when"
:
 
"minecraft:amethyst"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"minecraft:item/iron_chestplate_resin_trim"

        
},

        
"when"
:
 
"minecraft:resin"

      
},

      
{

        
"model"
:
 
{

          
"type"
:
 
"minecraft:model"
,

          
"model"
:
 
"example:item/iron_chestplate_blaze_trim"

        
},

        
"when"
:
 
"example:blaze"

      
}

    
],

    
"fallback"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/iron_chestplate"

    
},

    
"property"
:
 
"minecraft:trim_material"

  
}

}
```

以上物品模型映射文件实际上就是在原版铁胸甲的基础上增加了一个判断情况：当
```
trim
```

中的纹饰材料为
```
example:blaze
```

时，选择带烈焰粉纹饰的铁胸甲模型
```
example:item/iron_chestplate_blaze_trim
```

。

以下，定义带烈焰粉纹饰的铁胸甲模型：

[图:File file.png：Minecraft中file的精灵图] 
```
example:item/iron_chestplate_blaze_trim
```

json

...

```
{

  
"parent"
:
 
"minecraft:item/generated"
,

  
"textures"
:
 
{

    
"layer0"
:
 
"minecraft:item/iron_helmet"
,

    
"layer1"
:
 
"minecraft:trims/items/helmet_trim_blaze"

  
}

}
```

- ``` layer0 ``` 将被首先渲染。
- ``` layer1 ``` 将被最后渲染，并覆盖到 ``` layer0 ``` 之上。其来源于之前所定义的 ``` blocks.json ``` 图集。

# 参见

- Github公共仓库，包含该教程用到的所有文件。

# 导航
