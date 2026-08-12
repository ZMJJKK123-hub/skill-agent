---
name: minecraft-item-model-mapping
description: |
  物品模型映射（Minecraft Wiki 中文版全量正文）。
  
  【概述】物品模型映射，官方称之为物品模型（Item Model）、客户端物品信息（client-side item info），是根据物品堆叠的各项条件以选择物品应用哪种烘焙模型的机制。
  
  【涵盖内容】
  - bundle/selected_item
  - composite
  - condition
  - custom_model_data
  - component
  - has_component
  - keybind_down
  - model
  - range_dispatch
  - compass
  - count
  - damage
  
  【关键定义】
  - 数据包路径：data/bundle/selected_item
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 物品模型映射 的完整规范时
---

本条目所述内容仅适用于Java版。

物品模型映射，官方称之为物品模型（Item Model）、客户端物品信息（client-side item info），是根据物品堆叠的各项条件以选择物品应用哪种烘焙模型的机制。

# 定义格式

物品模型映射定义文件都在
```
assets/<
命名空间
>/items
```

目录内，且均为JSON文件。如果物品模型映射文件定义无效，则游戏会自动使用无效模型渲染。在原版游戏下，每个物品都使用
```
assets/minecraft/items/<
物品ID
>
```

作为自己的模型映射。

物品模型映射定义文件包含两部分：物品模型的选择机制和客户端物品的基础属性。此文件的格式如下：

- [图:NBT复合标签/JSON对象] JSON文件根元素 - [图:布尔型]hand_animation_on_swap：（默认为 ``` true ``` ）玩家在快捷栏切换到此物品堆叠时是否应该渲染切换过渡动画。如果物品堆叠只有耐久度属性不同（以 ``` damege ``` 组件判定），则始终不会渲染切换过渡动画。 - [图:布尔型]oversized_in_gui：（默认为 ``` false ``` ）在GUI内渲染时是否允许物品渲染超出槽位大小。 - [图:单精度浮点数]swap_animation_scale：（默认为1）玩家切换手持物品至该物品时切换动画的速度倍率。模型更大的物品设置为更大值可以保证物品能完整展示。 - [图:NBT复合标签/JSON对象]*model：一个物品模型映射，决定游戏如何选择物品的烘焙模型。 - 见下文。

很多时候，需要根据堆叠物品的某个数据或状态来选取不同烘焙模型。物品模型映射将一个与堆叠物品有关的条件和一个烘焙模型建立关联，从而实现了堆叠物品模型的条件性选取。

物品模型映射的JSON结构如下：

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - [图:字符串]*type：（命名空间ID）物品模型映射的类型。 - 与类型有关的其他字段。详见下文。

- - [图:字符串]*type： ``` condition ``` 。 - [图:NBT复合标签/JSON对象]*on_false：谓词为假时选择的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:NBT复合标签/JSON对象]*on_true：谓词为真时选择的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - - 物品模型变换 -

- - [图:字符串]*type： ``` range_dispatch ``` 。 - [图:NBT列表/JSON数组]*entries：定义各个阈值和对应的物品模型映射，此列表不需要排序，游戏会在运行时对这个列表排序。 - [图:NBT复合标签/JSON对象]：一项阈值和对应的物品模型映射。 - [图:NBT复合标签/JSON对象]*model：阈值对应的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:单精度浮点数]*threshold：阈值。 - [图:NBT复合标签/JSON对象]fallback：回落物品模型映射。如果检查数值小于所有阈值则使用此映射。如果此项不存在，且检查数值小于所有阈值，则使用无效模型。 - 递归定义物品模型映射。具体格式详见上文。 - [图:单精度浮点数]scale：（默认为1）与获取的数值属性相乘获得最后的检查数值。 - - 物品模型变换 -

- - [图:字符串]*type： ``` select ``` 。 - [图:NBT列表/JSON数组]*cases：定义枚举值和对应的物品模型映射。枚举值不能重复出现，否则游戏将报错 ``` Duplicate case conditions: < 重复的枚举值列表 > ``` 。 - [图:NBT复合标签/JSON对象]：一项枚举值列表和对应的物品模型映射。 - [图:NBT复合标签/JSON对象]*model：阈值对应的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:任意类型][图:NBT列表/JSON数组]*when：匹配此映射的枚举值。 - [图:任意类型]：一项枚举值。 - [图:NBT复合标签/JSON对象]fallback：回落物品模型映射。如果读取结果不匹配任何一个枚举值，则使用此映射。如果此项不存在，且读取结果不匹配任何一个枚举值，则使用无效模型。 - 递归定义物品模型映射。具体格式详见上文。 - - 物品模型变换 -

- - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]transformation：（默认为单位变换）物品模型的渲染变换，以物品堆叠自身所在的位置为原点，永远在物品的烘焙模型 ``` display ``` 指定的如主手副手的渲染变换之后进行。参见展示实体 § 变换。 - - 若为[图:NBT列表/JSON数组]：使用矩阵形式。其中包含16个浮点数元素，描述一个行主序（Row-major）矩阵： - [图:单精度浮点数]：矩阵中的一个值。其中第13、第14、第15个值对于变换没有任何效果；第16个值会将前12个值进行缩放，即将前12个数字除以此数字。 - - 若为[图:NBT复合标签/JSON对象]：使用分解形式。此标签必须包含下列所有标签，且各个标签按下方列出的顺序依次应用： - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]*right_rotation：初始旋转。此标签对应矩阵形式中矩阵左上角的3x3矩阵奇异值分解后的右奇异向量矩阵。 - - 若为[图:NBT列表/JSON数组]：使用四元数表示旋转（非单位四元数还会使模型缩放）。其中包含4个浮点数。 - [图:单精度浮点数]：四元数中的一个元素。 - - 若为[图:NBT复合标签/JSON对象]：使用轴-角度形式表示旋转。必须包含下列所有标签： - [图:单精度浮点数]*angle：表示绕旋转轴的旋转角度（以弧度为单位）。 - [图:NBT列表/JSON数组]*axis：（列表长度为3）一个3维向量，表示旋转轴。 - [图:单精度浮点数]：一个向量分量。 - [图:NBT列表/JSON数组]*scale：以原点为中心缩放模型。此标签对应矩阵形式中的矩阵左上角的3x3矩阵奇异值分解后的奇异值。此标签为含有3个元素的浮点数列表： - [图:单精度浮点数]：向量的一个分量。 - [图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]*left_rotation：再次旋转模型。此标签对应矩阵形式中矩阵左上角的3x3矩阵奇异值分解后的左奇异向量矩阵。 - - 若为[图:NBT列表/JSON数组]：使用四元数表示旋转（非单位四元数还会使模型缩放）。其中包含4个浮点数。 - [图:单精度浮点数]：四元数中的一个元素。 - - 若为[图:NBT复合标签/JSON对象]：使用轴-角度形式表示旋转。必须包含下列所有标签： - [图:单精度浮点数]*angle：表示绕旋转轴的旋转角度（以弧度为单位）。 - [图:NBT列表/JSON数组]*axis：（列表长度为3）一个3维向量，表示旋转轴。 - [图:单精度浮点数]：一个向量分量。 - [图:NBT列表/JSON数组]*translation：平移变换。此标签对应矩阵形式中的最后一列的前3个元素。此标签为含有3个元素的浮点数列表： - [图:单精度浮点数]：向量的一个分量。

# 类型

物品模型映射有下列类型，不同的映射类型决定了游戏在渲染指定物品堆叠时将使用的物品模型和参数。

## bundle/selected_item

此物品模型映射类型会让游戏渲染当前收纳袋内被选中的物品堆叠。

此渲染器要求渲染的物品堆叠必须具有
```
bundle_contents
```

组件，否则这个渲染器不会渲染任何东西。

- [图:NBT复合标签/JSON对象]*model - [图:字符串]*type： ``` bundle/selected_item ``` 。

## composite

此物品模型映射类型会先计算数组内所有物品模型映射，再根据数组次序从后向前依次渲染。

由于此物品模型映射包含子节点，故变换在子节点的变换之上进行。

- [图:NBT复合标签/JSON对象]*model 物品模型映射
- - [图:字符串]*type： ``` composite ``` 。 - [图:NBT列表/JSON数组]*models：从后向前依次渲染的物品模型映射。 - [图:NBT复合标签/JSON对象]：一个物品模型映射。 - 递归定义物品模型映射。 - - 物品模型变换
- 

在原版资源包中，该类型的物品模型映射用于将收纳袋的前、中、后三层纹理进行组合。其中，中间层纹理由
```
bundle/selected_item
```

类型的物品模型映射定义。

示例
收纳袋物品模型映射JSON文件的部分代码如下，该部分代码会在玩家选取收纳袋中某物品时生效：

```
            
...
 
此处省略部分代码

            
"type"
:
 
"minecraft:composite"
,

            
"models"
:
 
[

              
{

                
"type"
:
 
"minecraft:model"
,

                
"model"
:
 
"minecraft:item/bundle_open_back"

              
},

              
{

                
"type"
:
 
"minecraft:bundle/selected_item"

              
},

              
{

                
"type"
:
 
"minecraft:model"
,

                
"model"
:
 
"minecraft:item/bundle_open_front"

              
}

            
]

            
...
 
此处省略部分代码
```

## condition

布尔条件型物品模型映射类型。此物品模型映射类型会先计算物品堆叠内给定的谓词，当属性为真时选择一个物品模型映射，为假时选择另一个。

由于此物品模型映射包含子节点，故变换在子节点的变换之上进行。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - [图:字符串]*type： ``` condition ``` 。 - [图:NBT复合标签/JSON对象]*on_false：谓词为假时选择的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:NBT复合标签/JSON对象]*on_true：谓词为真时选择的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - - 物品模型变换 - - [图:字符串]*property：（命名空间ID）检查给定的物品模型映射谓词类型。 - 其他元素见下文。

示例1
收纳袋物品模型映射JSON文件的部分代码如下，根据玩家是否选中收纳袋内物品切换模型：

```
       
...

        
"model"
:
 
{

          
"type"
:
 
"minecraft:condition"
,

          
"property"
:
 
"minecraft:bundle/has_selected_item"
,

          
"on_false"
:
 
{

            
"type"
:
 
"minecraft:model"
,

            
"model"
:
 
"minecraft:item/bundle"

          
},

          
"on_true"
:
 
{

            
"type"
:
 
"minecraft:composite"
,

            
"models"
:
 
[

              
{

                
"type"
:
 
"minecraft:model"
,

                
"model"
:
 
"minecraft:item/bundle_open_back"

              
},

              
{

                
"type"
:
 
"minecraft:bundle/selected_item"

              
},

              
{

                
"type"
:
 
"minecraft:model"
,

                
"model"
:
 
"minecraft:item/bundle_open_front"

              
}

            
]

          
}

        
},

        
...
```

示例2
原版鞘翅物品模型映射JSON文件如下，当鞘翅即将损坏时将更换为破损鞘翅模型：

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:condition"
,

    
"property"
:
 
"minecraft:broken"
,

    
"on_false"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/elytra"

    
},

    
"on_true"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/elytra_broken"

    
}

  
}

}
```

可用的物品模型映射谓词如下表所示：

其他带有附加元素的谓词如下文所示：

### custom_model_data

读取物品堆叠的
```
custom_model_data
```

组件其中的[图:NBT列表/JSON数组]flags，将给定下标的布尔值作为谓词结果。

如果物品堆叠没有
```
custom_model_data
```

组件，或下标超过了[图:NBT列表/JSON数组]flags的长度范围，则返回假。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 布尔条件型物品模型共通字段 - [图:字符串]*property： ``` custom_model_data ``` 。 - [图:整型]index：（值≥0，默认为0）检查给定物品堆叠 ``` custom_model_data ``` 组件中[图:NBT列表/JSON数组]flags对应下标的元素是否为真。

示例

自定义模型映射，使用此映射的物品的
```
custom_model_data.flags.[1]
```

若存在且为
```
true
```

时渲染成钻石，否则为铁锭：

### component

检查物品堆叠是否满足指定的数据组件谓词。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 布尔条件型物品模型共通字段 - [图:字符串]*property： ``` component ``` 。 - [图:字符串]*predicate：指定数据组件谓词类型。 - [图:任意类型]*value：指定谓词内容。

示例
自定义模型映射，当使用此映射的附魔书存储了不大于3级的锋利魔咒时渲染成钻石：

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:condition"
,

    
"property"
:
 
"minecraft:component"
,

    
"predicate"
:
 
"minecraft:stored_enchantments"
,

    
"value"
:
 
[

      
{

        
"enchantments"
:
 
"minecraft:sharpness"
,

        
"levels"
:
 
{

          
"max"
:
 
3

        
}

      
}

    
],

    
"on_false"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/enchanted_book"

    
},

    
"on_true"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/diamond"

    
}

  
}

}
```

### has_component

检查物品堆叠是否有给定的物品堆叠组件。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 布尔条件型物品模型共通字段 - [图:字符串]*property： ``` has_component ``` 。 - [图:字符串]*component：（物品堆叠组件类型）检查物品堆叠是否具有此组件。 - [图:布尔型]ignore_default：（默认为 ``` false ``` ）若当前的物品堆叠组件内容与物品默认物品堆叠组件内容一致时是否认为此组件不存在而返回假。

示例
原版指南针物品模型映射JSON文件的部分代码如下：

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:condition"
,

    
"property"
:
 
"minecraft:has_component"
,

    
"component"
:
 
"minecraft:lodestone_tracker"
,

    
"on_false"
:
 
{

      
...
  
当lodes
t
o
ne
_
tra
cker组件不存在时，若维度为主世界，则获取获取指南针相对玩家出生点的朝向；否则，获取随机朝向。最后根据朝向选取不同的烘焙模型。

    
},

    
"on_true"
:
 
{

      
...
 
当lodes
t
o
ne
_
tra
cker组件存在时，指南针相对磁石的朝向，根据朝向选取不同的烘焙模型。

    
}

  
}

}
```

### keybind_down

检查键位绑定是否被按下。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 布尔条件型物品模型共通字段 - [图:字符串]*property： ``` keybind_down ``` 。 - [图:字符串]*keybind：（键位的本地化键名）检查键位绑定是否被按下。

## model

指定游戏使用哪一个物品模型进行渲染，并且指定各个着色索引使用的颜色。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - [图:字符串]*type： ``` model ``` 。 - [图:字符串]*model：用于渲染的物品模型，游戏解析时转换为 ``` assets/< 命名空间 >/models/< 路径 >.json ``` 。 - [图:NBT列表/JSON数组]tints：（默认为空数组）指定物品模型各个着色索引使用的颜色，数组下标对应着色索引。 - [图:NBT复合标签/JSON对象]：颜色提供器。 - [图:字符串]*type：颜色来源。 - - 如果 ``` type ``` 为 ``` custom_model_data ``` ，游戏将使用 ``` custom_model_data ``` 组件信息作为着色颜色。 - [图:整型][图:NBT列表/JSON数组]*default：当物品堆叠不存在 ``` custom_model_data ``` 组件，或下标超过[图:NBT列表/JSON数组]colors范围时使用的着色颜色。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:整型]index：（值≥0，默认为0）将给定物品堆叠 ``` custom_model_data ``` 组件中[图:NBT列表/JSON数组]colors对应下标的元素作为着色颜色。 - - 如果 ``` type ``` 为 ``` constant ``` ，则使用固定颜色。 - [图:整型][图:NBT列表/JSON数组]*value：着色颜色。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - - 如果 ``` type ``` 为 ``` grass ``` ，游戏将按照生物群系着色中的植物颜色算法，使用温度值和降水值计算颜色，颜色图使用grass.png。 - [图:单精度浮点数]*downfall：（0≤值≤1）降水值。 - [图:单精度浮点数]*temperature：（0≤值≤1）温度值。 - - 如果 ``` type ``` 为 ``` firework ``` ，游戏将使用烟火之星颜色，即 ``` firework_explosion ``` 组件中[图:整型数组]colors内各个颜色的平均值作为着色颜色。 - - 如果 ``` type ``` 为 ``` dye ``` ，游戏将使用物品染色，即 ``` dyed_color ``` 组件信息作为着色颜色。 - - 如果 ``` type ``` 为 ``` potion ``` ，游戏将使用药水颜色，即 ``` potion_contents ``` 组件中的药水颜色作为着色颜色。 - - 如果 ``` type ``` 为 ``` map_color ``` ，游戏将使用地图颜色，即 ``` map_color ``` 组件信息作为着色颜色。 - - 如果 ``` type ``` 为 ``` team ``` ，游戏将获取持有此物品堆叠的生物的队伍颜色作为着色颜色。 - - 上述5种类型均使用下列格式。 - [图:整型][图:NBT列表/JSON数组]*default：游戏获取不到指定信息时（如不存在对应物品堆叠组件）使用的着色颜色。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - - 物品模型变换

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

示例
原版已绘制的地图的烘焙模型有两层，分别是底层和图案层。底层固定着色，而图案层根据[图:整型]map_color值变化，使得探险家地图可以显示与常规地图不同的纹理。

```
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
 
"minecraft:item/filled_map"
,

    
"tints"
:
 
[

      
{

        
"type"
:
 
"minecraft:constant"
,

        
"value"
:
 
-1

      
},

      
{

        
"type"
:
 
"minecraft:map_color"
,

        
"default"
:
 
4603950

      
}

    
]

  
}

}
```

## range_dispatch

值调配型物品模型映射类型。此物品模型映射类型会先计算并返回物品堆叠内给定的一个数值属性，游戏会按照给定阈值从小到大排序，找到数值属性第一个超过或等于的阈值，并使用对应物品模型映射。如果数值属性小于所有阈值，则使用回落映射。

由于此物品模型映射包含子节点，故变换在子节点的变换之上进行。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - [图:字符串]*type： ``` range_dispatch ``` 。 - [图:NBT列表/JSON数组]*entries：定义各个阈值和对应的物品模型映射，此列表不需要排序，游戏会在运行时对这个列表排序。 - [图:NBT复合标签/JSON对象]：一项阈值和对应的物品模型映射。 - [图:NBT复合标签/JSON对象]*model：阈值对应的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:单精度浮点数]*threshold：阈值。 - [图:NBT复合标签/JSON对象]fallback：回落物品模型映射。如果检查数值小于所有阈值则使用此映射。如果此项不存在，且检查数值小于所有阈值，则使用无效模型。 - 递归定义物品模型映射。具体格式详见上文。 - [图:单精度浮点数]scale：（默认为1）与获取的数值属性相乘获得最后的检查数值。 - - 物品模型变换 - - [图:字符串]*property：（命名空间ID）检查给定的物品模型映射数值属性类型。 - 其他元素见下文。

游戏中总共有以下几种物品模型映射数值属性：

带有附加元素的属性及其附加元素如下所示：

### custom_model_data

读取物品堆叠的
```
custom_model_data
```

组件中的[图:NBT列表/JSON数组]floats，获取指定下标的浮点数。如果下标超过[图:NBT列表/JSON数组]floats的长度范围，或物品堆叠不存在
```
custom_model_data
```

组件，则返回0。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` custom_model_data ``` 。 - [图:整型]index：（值≥0，默认为0）获取给定物品堆叠 ``` custom_model_data ``` 组件中[图:NBT列表/JSON数组]floats对应下标的浮点数。

### compass

读取指南针信息，计算指南针指针摆动进度作为返回值，返回值取值为0-1的闭区间。如果指向目标不存在，或指向目标和当前维度不一致，或当前位置与指向目标的距离小于1e-5时，指针摆动进度会使用随机浮点数。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` compass ``` 。 - [图:字符串]*target：指南针指向的目标。 - [图:布尔型]wobble：（默认为 ``` true ``` ）摆动进度是否会有额外摆动浮动。如果没有浮动，摆动进度会立刻平滑到当前的正确值，而不是在正确值附近浮动。

[图:字符串]target可用值和意义如下：

示例
指南针物品模型映射JSON文件的部分代码如下，这段代码会在指南针无
```
lodestone_tracker
```

物品堆叠组件时生效。游戏会获取指南针的指向出生点的数据并乘以32.0，然后和entries中的每一项的threshold进行比对并选择相应烘焙模型。

```
         
...
 
此处省略部分代码
 

          
"model"
:
 
{

            
"type"
:
 
"minecraft:range_dispatch"
,

            
"property"
:
 
"minecraft:compass"
,

            
"scale"
:
 
32.0
,

            
"target"
:
 
"spawn"
,

            
"entries"
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
 
"minecraft:item/compass_16"

                
},

                
"threshold"
:
 
0.0

              
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
 
"minecraft:item/compass_17"

                
},

                
"threshold"
:
 
0.5

              
},

              
...
 
此处省略若干关于
t
hreshold的枚举
,

              
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
 
"minecraft:item/compass_16"

                
},

                
"threshold"
:
 
31.5

              
}

            
]

          
}

          
...
 
此处省略部分代码
```

另一段与之相应的代码则表达了当前物品有
```
lodestone_tracker
```

物品堆叠组件时所要使用的烘焙模型：

```
      
...
 
此处省略部分代码
 

      
"type"
:
 
"minecraft:range_dispatch"
,

      
"property"
:
 
"minecraft:compass"
,

      
"scale"
:
 
32.0
,

      
"target"
:
 
"lodestone"
,

      
"entries"
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
 
"minecraft:item/compass_16"

          
},

          
"threshold"
:
 
0.0

        
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
 
"minecraft:item/compass_17"

          
},

          
"threshold"
:
 
0.5

        
},

        
...
 
此处省略若干关于
t
hreshold的枚举
,

        
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
 
"minecraft:item/compass_16"

          
},

          
"threshold"
:
 
31.5

        
}

      
]

      
...
 
此处省略部分代码
```

### count

读取物品堆叠的物品数量作为返回值。如果物品数量大于物品最大堆叠数量，则返回物品最大堆叠数量。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` count ``` 。 - [图:布尔型]normalize：（默认为 ``` true ``` ）返回物品数量和物品最大堆叠数量之比，而不是当前的物品数量。

### damage

读取物品堆叠的损坏值（
```
damage
```

组件）。如果物品没有损坏或无法损坏，则返回0。如果损坏值大于最大耐久度（
```
max_damage
```

组件），则返回最大耐久度。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` damage ``` 。 - [图:布尔型]normalize：（默认为 ``` true ``` ）返回物品的损坏进度（即损坏值除以最大耐久度，取值为0-1闭区间），而不是当前的损坏值。

### time

读取当前维度的时间，计算并平滑模拟时钟摆动进度，将时钟摆动进度作为返回值返回，返回值取值为0-1的闭区间。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` time ``` 。 - [图:字符串]*source：时间获取源。可以为 ``` daytime ``` （昼夜时间）、 ``` random ``` （随机数）或 ``` moon_phase ``` （月相）。所有数字均在0到1的闭区间内。 - [图:布尔型]wobble：（默认为 ``` true ``` ）摆动进度是否会有额外摆动浮动。如果没有浮动，摆动进度会立刻平滑到当前的正确值，而不是在正确值附近浮动。

时间源[图:字符串]source指定为月相
```
moon_phase
```

时的返回值可参考下表：

示例
原版时钟物品模型映射JSON文件如下。当维度为主世界时，根据昼夜时间来选取不同的模型；否则根据随机时间选取模型。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:select"
,

    
"property"
:
 
"minecraft:context_dimension"
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
 
"minecraft:range_dispatch"
,

          
"property"
:
 
"minecraft:time"
,

          
"scale"
:
 
64.0
,

          
"source"
:
 
"daytime"
,

          
"entries"
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
 
"minecraft:item/clock_00"

              
},

              
"threshold"
:
 
0.0

            
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
 
"minecraft:item/clock_01"

              
},

              
"threshold"
:
 
0.5

            
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
 
"minecraft:item/clock_02"

              
},

              
"threshold"
:
 
1.5

            
},

            
...
 
省略若干关于
t
hreshold的枚举情况
,

            
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
 
"minecraft:item/clock_00"

              
},

              
"threshold"
:
 
63.5

            
}

          
]

        
},

        
"when"
:
 
"minecraft:overworld"

      
}

    
],

    
"fallback"
:
 
{

      
"type"
:
 
"minecraft:range_dispatch"
,

      
"property"
:
 
"minecraft:time"
,

      
"scale"
:
 
64.0
,

      
"source"
:
 
"random"
,

      
"entries"
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
 
"minecraft:item/clock_00"

          
},

          
"threshold"
:
 
0.0

        
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
 
"minecraft:item/clock_01"

          
},

          
"threshold"
:
 
0.5

        
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
 
"minecraft:item/clock_02"

          
},

          
"threshold"
:
 
1.5

        
},

        
...
 
省略若干关于
t
hreshold的枚举情况
,

        
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
 
"minecraft:item/clock_00"

          
},

          
"threshold"
:
 
63.5

        
}

      
]

    
}

  
}

}
```

### use_cycle

读取当前物品堆叠的剩余使用时间，并对给定的周期取模作为返回值。如果物品堆叠不在任何生物身上，或生物没有使用这个物品堆叠，则返回0。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` use_cycle ``` 。 - [图:单精度浮点数]period：（值>0，默认为1）周期。

示例
原版刷子物品模型映射JSON文件如下。这里对物品堆叠的剩余使用时间取关于10.0的模，然后乘以0.1，然后根据三种阈值选取不同烘焙模型。item/brush_brushing_0到item/brush_brushing_2的刷子模型仅改变了第三人称下的模型角度，模拟第三人称下的刷子摆动动画效果。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:range_dispatch"
,

    
"period"
:
 
10.0
,

    
"property"
:
 
"minecraft:use_cycle"
,

    
"scale"
:
 
0.1
,

    
"entries"
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
 
"minecraft:item/brush_brushing_0"

        
},

        
"threshold"
:
 
0.25

      
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
 
"minecraft:item/brush_brushing_1"

        
},

        
"threshold"
:
 
0.5

      
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
 
"minecraft:item/brush_brushing_2"

        
},

        
"threshold"
:
 
0.75

      
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
 
"minecraft:item/brush"

    
}

  
}

}
```

### use_duration

读取物品堆叠的使用时间或剩余使用时间作为返回值。如果物品堆叠不在任何生物身上，或生物没有使用这个物品堆叠，则返回0。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 值调配型物品模型共通字段 - [图:字符串]*property： ``` use_duration ``` 。 - [图:布尔型]remaining：（默认为 ``` false ``` ）使用物品堆叠的剩余使用时间而非使用时间。

示例
原版弓物品模型映射JSON文件如下。这里没有设定remaining字段，默认为玩家的拉弓时长。这里指定了use_duration属性，当玩家正在拉弓时，游戏将根据拉弓剩余时间选取不同弓状态下的模型。item/bow_pulling_2模型可表示弓完全拉开，item/bow_pulling_1模型可表示弓半拉开。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:condition"
,

    
"property"
:
 
"minecraft:using_item"
,

    
"on_false"
:
 
{

      
"type"
:
 
"minecraft:model"
,

      
"model"
:
 
"minecraft:item/bow"

    
},

    
"on_true"
:
 
{

      
"type"
:
 
"minecraft:range_dispatch"
,

      
"property"
:
 
"minecraft:use_duration"
,

      
"scale"
:
 
0.05
,

      
"entries"
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
 
"minecraft:item/bow_pulling_1"

          
},

          
"threshold"
:
 
0.65

        
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
 
"minecraft:item/bow_pulling_2"

          
},

          
"threshold"
:
 
0.9

        
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
 
"minecraft:item/bow_pulling_0"

      
}

    
}

  
}

}
```

## select

枚举条件型物品模型映射类型。此物品模型映射类型会先计算物品堆叠内给定的一个枚举属性，游戏会使用枚举属性值对应的物品模型映射。如果没有匹配的枚举值，则使用回落物品模型映射。

由于此物品模型映射包含子节点，故变换在子节点的变换之上进行。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - [图:字符串]*type： ``` select ``` 。 - [图:NBT列表/JSON数组]*cases：定义枚举值和对应的物品模型映射。枚举值不能重复出现，否则游戏将报错 ``` Duplicate case conditions: < 重复的枚举值列表 > ``` 。 - [图:NBT复合标签/JSON对象]：一项枚举值列表和对应的物品模型映射。 - [图:NBT复合标签/JSON对象]*model：阈值对应的物品模型映射。 - 递归定义物品模型映射。具体格式详见上文。 - [图:任意类型][图:NBT列表/JSON数组]*when：匹配此映射的枚举值。 - [图:任意类型]：一项枚举值。 - [图:NBT复合标签/JSON对象]fallback：回落物品模型映射。如果读取结果不匹配任何一个枚举值，则使用此映射。如果此项不存在，且读取结果不匹配任何一个枚举值，则使用无效模型。 - 递归定义物品模型映射。具体格式详见上文。 - - 物品模型变换 - - [图:字符串]*property：（命名空间ID）检查给定的物品模型映射枚举属性类型。 - 其他元素见下文。

示例1
原版指南针JSON文件的部分代码如下。这里首先判断维度是否为主世界，若是，则指定指针朝向为玩家出生点，否则不指定指针朝向，此时指针为随机朝向。

```
      
...

      
"type"
:
 
"minecraft:select"
,

      
"property"
:
 
"minecraft:context_dimension"
,

      
"cases"
:
 
[

        
{

          
"when"
:
 
"minecraft:overworld"
,

          
"model"
:
 
{

            
"type"
:
 
"minecraft:range_dispatch"
,

            
"property"
:
 
"minecraft:compass"
,

            
"scale"
:
 
32.0
,

            
"target"
:
 
"spawn"
,

            
"entries"
:
 
[

              
...
 
若干关于
t
hreshold的枚举...

            
]

          
}

        
}

      
],

      
"fallback"
:
 
{

        
"type"
:
 
"minecraft:range_dispatch"
,

        
"property"
:
 
"minecraft:compass"
,

        
"scale"
:
 
32.0
,

        
"target"
:
 
"none"
,

        
"entries"
:
 
[

          
...
 
若干关于
t
hreshold的枚举...

        
]

      
}

      
...
```

示例2
原版锁链靴子JSON文件的部分代码如下。这里根据trim组件的纹饰材料来选取不同的烘焙模型，从而实现显示带不同颜色纹饰的锁链靴子物品模型。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:select"
,

    
"property"
:
 
"minecraft:trim_material"
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
 
"minecraft:item/chainmail_boots_quartz_trim"

        
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
 
"minecraft:item/chainmail_boots_iron_trim"

        
},

        
"when"
:
 
"minecraft:iron"

      
},

      
...
 
若干关于纹饰材料的枚举...

      
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
 
"minecraft:item/chainmail_boots_resin_trim"

        
},

        
"when"
:
 
"minecraft:resin"

      
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
 
"minecraft:item/chainmail_boots"

    
}

  
}

}
```

物品模型映射枚举属性类型如下所示：

带有附加元素的类型如下所示：

### block_state

读取物品堆叠的
```
block_state
```

组件，并获取指定方块属性的值作为返回值。如果物品堆叠不存在此组件，或方块不具有对应方块属性，则返回null，无法匹配。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 枚举条件型物品模型共通字段 - [图:字符串]*property： ``` block_state ``` 。 - [图:字符串]*block_state_property：获取方块的指定方块属性。

示例
原版蜂巢、蜂箱物品模型映射文件就利用该属性来根据
```
honey_level
```

方块状态显示不同烘焙模型。如下两个烘焙模型仅纹理有所差别，实现了蜜脾满和未满时分别显示不同纹理。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:select"
,

    
"block_state_property"
:
 
"honey_level"
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
 
"minecraft:block/bee_nest_honey"

        
},

        
"when"
:
 
"5"

      
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
 
"minecraft:block/bee_nest_empty"

    
},

    
"property"
:
 
"minecraft:block_state"

  
}

}
```

### component

读取物品堆叠的可持久化组件数据，获取此组件的数据作为返回值。指定不可持久化的组件或枚举值不符合对应组件的数据要求时此模型映射会直接加载失败。

游戏会完全匹配物品模型映射指定的组件值和物品的组件值。例如，对于
```
custom_data
```

组件而言，
```
{a:data,b:true}
```

和
```
"{\"a\":\"data\",\"b\":true}"
```

最终会转变为相同的内容（SNBT导出均为
```
{a: data,b :true}
```

），因此这两种写法尽管形式不同，但会被视为相同的组件值：枚举值同时指定会被游戏警告重复的枚举值，物品数据定义和枚举值定义使用任何一种形式都被视为匹配成功。由于游戏会完全匹配，因此不能单独筛选组件中某个键值对的精确值，例如枚举值
```
{"a":"data"}
```

不会匹配上述示例。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 枚举条件型物品模型共通字段 - [图:字符串]*property： ``` component ``` 。 - [图:字符串]*component：获取物品堆叠的指定组件。

### custom_model_data

读取物品堆叠的
```
custom_model_data
```

组件中的[图:NBT列表/JSON数组]strings，获取指定下标的字符串。如果下标超过[图:NBT列表/JSON数组]strings的长度范围，或物品堆叠不存在
```
custom_model_data
```

组件，则返回null，无法匹配。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 枚举条件型物品模型共通字段 - [图:字符串]*property： ``` custom_model_data ``` 。 - [图:整型]index：（值≥0，默认为0）获取给定物品堆叠 ``` custom_model_data ``` 组件中[图:NBT列表/JSON数组]strings对应下标的字符串。

### local_time

读取当前时间，并根据指定时区、地区设置和日期格式获得日期字符串。此字符串每秒最多获取一次。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - - 枚举条件型物品模型共通字段 - [图:字符串]*property： ``` local_time ``` 。 - [图:字符串]locale：（默认为空字符串）时间格式化为字符串时使用的地区设置。格式可参照此文档和RFC3066。 - [图:字符串]*pattern：根据时区获取当前时间后，游戏将时间格式化为字符串的日期格式。日期格式可参照此文档。 - [图:字符串]time_zone：（默认为系统设置的时区）获取时间使用的时区。格式可参照此文档和此条目。

示例
原版箱子的物品模型JSON文件如下。这里pattern为MM-dd，表示“月-日”格式。通过when设定仅在每年12月24到26日使用圣诞箱子模型，否则使用普通箱子模型。

```
{

  
"model"
:
 
{

    
"type"
:
 
"minecraft:select"
,

    
"pattern"
:
 
"MM-dd"
,

    
"property"
:
 
"minecraft:local_time"
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
 
"minecraft:special"
,

          
"base"
:
 
"minecraft:item/chest"
,

          
"model"
:
 
{

            
"type"
:
 
"minecraft:chest"
,

            
"texture"
:
 
"minecraft:christmas"

          
}

        
},

        
"when"
:
 
[

          
"12-24"
,

          
"12-25"
,

          
"12-26"

        
]

      
}

    
],

    
"fallback"
:
 
{

      
"type"
:
 
"minecraft:special"
,

      
"base"
:
 
"minecraft:item/chest"
,

      
"model"
:
 
{

        
"type"
:
 
"minecraft:chest"
,

        
"texture"
:
 
"minecraft:normal"

      
}

    
}

  
}

}
```

## special

调用游戏的特殊模型渲染物品堆叠。物品堆叠渲染时的渲染变换、粒子纹理变量等可以从物品模型中获取。

- [图:NBT复合标签/JSON对象]*model 物品模型映射 - [图:字符串]*type： ``` special ``` 。 - [图:字符串]*base：（命名空间ID）特殊模型使用的基础物品模型。游戏会读取物品模型中的渲染变换、GUI光照和粒子纹理变量。 - [图:NBT复合标签/JSON对象]*model：特殊模型的配置。 - [图:字符串]*type：（命名空间ID）使用的特殊模型类型。 - 其他元素见下文。 - - 物品模型变换

游戏内包含下列特殊模型类型：

### banner

根据底色和
```
banner_patterns
```

物品堆叠组件渲染旗帜。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` banner ``` 。 - [图:字符串]attachment：（默认为 ``` ground ``` ）指定旗帜的渲染方式。取值可以为 ``` wall ``` （墙上的旗帜）和 ``` ground ``` （站立的旗帜）。 - [图:字符串]*color：旗帜底色，可用枚举值见颜色。

### book

根据指定的角度渲染书。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` book ``` 。 - [图:单精度浮点数]*open_angle：书的封面和书的中轴线的角度，按角度制计。为0时表示书完全合上，为90时表示书完全摊平。 - [图:单精度浮点数]*page1：第一个书页的位置。为0.0时表示在书的最左侧，为1.0时表示在书的最右侧。 - [图:单精度浮点数]*page2：第二个书页的位置，同[图:单精度浮点数]page1。

### chest

根据指定的纹理和开合程度渲染箱子。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` chest ``` 。 - [图:字符串]chest_type：（默认为 ``` single ``` ）指定箱子的渲染方式。取值可以为 ``` single ``` （小箱子）、 ``` left ``` （大箱子的左半侧）和 ``` right ``` （大箱子的右半侧）。 - [图:单精度浮点数]openness：（默认为0）箱子打开的程度。 - [图:字符串]*texture：（命名空间ID）渲染箱子使用的纹理。游戏在渲染时将纹理解析为 ``` assets/< 命名空间 >/textures/entity/chest/< 路径 >.png ``` 。

### copper_golem_statue

根据指定的纹理渲染铜傀儡像。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` copper_golem_statue ``` 。 - [图:字符串]*pose：铜傀儡像的姿势，可以为 ``` standing ``` 、​ ``` sitting ``` 、​ ``` running ``` 和​ ``` star ``` 。 - [图:字符串]*texture：（命名空间ID）渲染铜傀儡像使用的纹理。游戏在渲染时将纹理解析为 ``` assets/< 命名空间 >/< 路径 > ``` 。

### end_cube

根据指定的纹理渲染一个特殊效果的立方体。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` end_cube ``` 。 - [图:字符串]*effect：渲染的效果，必须为 ``` portal ``` （末地传送门）或 ``` gateway ``` （末地折跃门）之一。

### head

按照指定的头颅类型渲染生物头颅。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` head ``` 。 - [图:单精度浮点数]animation：（默认为0）头颅动画进度，控制龙首和猪灵的头渲染时动态部分的动画进度。此值仅当[图:字符串]*kind为 ``` dragon ``` 或 ``` piglin ``` 时才有实际作用。 - [图:字符串]*kind：头颅类型，可以为 ``` creeper ``` 、​ ``` dragon ``` 、​ ``` piglin ``` 、​ ``` player ``` 、​ ``` skeleton ``` 、​ ``` wither_skeleton ``` 和​ ``` zombie ``` 。此项决定了游戏使用哪种动态模型渲染。 - [图:字符串]texture：（命名空间ID）使用指定的纹理渲染对应的头颅，游戏在渲染时将纹理解析为 ``` assets/< 命名空间 >/textures/entity/< 路径 >.png ``` 。

### shulker_box

根据指定的纹理、开合程度和方向渲染潜影盒。

- [图:NBT复合标签/JSON对象]*model 硬编码特殊模型 - [图:字符串]*type： ``` shulker_box ``` 。 - [图:单精度浮点数]openness：（默认为0）潜影盒打开的程度。 - [图:字符串]*texture：（命名空间ID）渲染潜影盒使用的纹理。游戏在渲染时将纹理解析为 ``` assets/< 命名空间 >/textures/entity/shulker/< 路径 >.png ``` 。

# 历史

# 参考

1. ↑ Minecraft Snapshot 24w45a — Minecraft.net。
1. ↑ Minecraft 1.21.4 Pre-Release 1 — Minecraft.net。
1. ↑ MC-279557 — 漏洞状态为“无效”。

# 导航
