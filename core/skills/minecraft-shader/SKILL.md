---
name: minecraft-shader
description: |
  着色器（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是Java版中的着色器。关于其他用法，请见“光影”。
  
  【涵盖内容】
  - 包含着色器
  - 渲染类型参数
  - 渲染类型Uniform
  - 渲染类型列表
  - 方块渲染类型
  - 方块效果渲染类型
  - 实体渲染类型
  - 实体效果渲染类型
  - 光效渲染类型
  - 文字渲染类型
  - GUI渲染类型
  - 杂项渲染类型
  
  【关键定义】
  - 数据包路径：data/assets/minecraft/shaders、data/assets/minecraft/shaders/core、data/assets/minecraft/shaders/post、data/shaders/core/terrain.fsh、data/shaders/core/terrain.vsh、data/shaders/core/rendertype_solid.json
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 着色器 的完整规范时
---

本条目介绍的是Java版中的着色器。关于其他用法，请见“光影”。

本条目所述内容仅适用于Java版。
此条目需要更新。
理由：核心着色器缺失1.21.5+的信息

着色器（Shader）是一种渲染程序，用于控制游戏渲染的过程。在资源包内，着色器都存储于
```
assets/minecraft/shaders
```

目录下。

# 使用着色器

游戏可以使用资源包修改内部定义的着色器。根据游戏渲染的原理，渲染通常按照了这样简单基础的步骤：

1. 使用对应的渲染类型渲染对应的物体。
1. 在场景内所有物体渲染完毕后，调用后处理管线处理场景。

这两个最基础的步骤可以使用资源包修改，但渲染顺序是硬编码的因此不可修改。修改第一个步骤需要修改对应渲染类型的核心着色器，而修改第二个步骤则需要修改后处理管线程序。

当游戏加载资源包时，如果着色器加载发生了异常，那么游戏会立刻禁用所有资源包以保证游戏不出现异常，并关闭极佳！图像品质。

# 着色器格式

游戏内共存在两种着色器格式：

- 核心着色器：位于 ``` assets/minecraft/shaders/core ``` 目录内，负责对应渲染类型的渲染。
- 后处理着色器：位于 ``` assets/minecraft/shaders/post ``` 目录内，负责帧缓冲的后处理渲染。

这两种着色器完全一致，无论着色器是核心着色器还是后处理着色器，一个着色器实例都包括下列可配置数据：

- 顶点着色器（Vertex Shader）文件。
- 片段着色器（Fragment Shader）文件。

## 包含着色器

顶点着色器文件和片段着色器文件可以引用指定的包含着色器以复用代码。

包含着色器全部位于
```
assets/<
命名空间
>/shaders/include
```

目录内，通常以
```
glsl
```

作为后缀，语法和正常的顶点或片段着色器无异。顶点着色器文件和片段着色器文件中使用包含着色器需要使用下列两种格式之一：

```
#moj_import <命名空间ID>

#moj_import "命名空间ID"
```

假设顶点着色器需要引用包含着色器
```
fog.glsl
```

，那么在顶点着色器中需要包含下面这一行：

```
#moj_import <minecraft:fog.glsl>
```

如果游戏找不到包含着色器或包含着色器读取失败，那么就会在日志中警告
```
Could not open GLSL import <
包含着色器
>: <
错误原因
>
```

。包含着色器内不能再引用其他包含着色器，游戏只会解析一次包含着色器的展开，因此不支持这种操作。

游戏默认提供了9个包含着色器，它们可以被其他着色器使用，也可以被其他资源包替换。

# 渲染类型

渲染类型用于处理游戏内各个物体的渲染，包括方块、物品、实体的模型、GUI组件等。不同的物体可能拥有不同的渲染类型，而不同的渲染类型会使用不同的着色器和参数。

## 渲染类型参数

每个渲染类型都有相应的参数，以提供渲染过程中需要的数据。

影响渲染类型渲染的渲染参数在游戏中被称为状态（State），一个渲染类型会拥有下列的状态：

- 纹理状态（Texture State）：此渲染类型渲染过程中，游戏对着色器输入的采样器纹理。纹理状态共有3种可能的状态，默认为空纹理状态： - 空纹理状态（Empty Texture State）：游戏不提供任何采样器纹理，着色器中无法使用采样器。 - 单纹理状态（(Single) Texture State）：游戏指定一张采样器纹理，并绑定到采样器 ``` Sampler0 ``` 以供着色器使用。 - 多纹理状态（Multi Texture State）：游戏指定一系列采样器纹理，按照顺序依次指定采样器纹理 ``` Sampler0 ``` 、 ``` Sampler1 ``` ，最多可以指定到 ``` Sampler11 ``` 。
- 着色器状态（Shader State）：此渲染类型使用的核心着色器。默认不指定着色器。
- 混合状态（Transparency State）：此渲染类型指定的混合模式，以保证半透明渲染时进行正确地渲染。混合状态共有6种可能的状态，默认为无混合状态： - 无混合（No Transparency）：游戏在此渲染类型渲染过程中关闭混合，即此渲染类型无法渲染任何半透明片段。 - 加性混合（Additive Transparency）：源因子计算模式和目标因子计算模式为 ``` one ``` 。 - 闪电混合（Lightning Transparency）：源因子计算模式为 ``` srcalpha ``` ，目标因子计算模式为 ``` one ``` 。 - 光效混合（Glint Transparency）：源因子RGB计算模式为 ``` srccolor ``` ，A计算模式为 ``` zero ``` ；目标因子RGB计算模式为 ``` one ``` ，A计算模式为 ``` one ``` 。 - 破坏动画混合（Crumbling Transparency）：源因子RGB计算模式为 ``` dstcolor ``` ，A计算模式为 ``` one ``` ；目标因子RGB计算模式为 ``` srccolor ``` ，A计算模式为 ``` zero ``` 。 - 半透明混合（Translucent Transparency）：源因子RGB计算模式为 ``` srcalpha ``` ，A计算模式为 ``` one ``` ；目标因子RGB计算模式为 ``` 1-srcalpha ``` ，A计算模式为 ``` 1-srcalpha ``` 。
- 深度测试状态（Depth Test State）：此渲染类型深度测试的启用状态和模式。深度测试状态有4种可能的状态，默认为小于等于深度测试： - 无深度测试（No Depth Test）：游戏使用此渲染类型渲染时禁用深度测试。 - 等于深度测试（Equal Depth Test）：游戏启用深度测试，且模式为 ``` GL_EQUAL ``` （片段与当前深度缓冲拥有相同深度值时渲染）。 - 小于等于深度测试（Less Equal Depth Test）：游戏启用深度测试，且模式为 ``` GL_LEQUAL ``` （片段深度值小于等于当前深度缓冲深度值时渲染）。 - 大于深度测试（Greater Depth Test）：游戏启用深度测试，且模式为 ``` GL_GREATER ``` （片段深度值大于当前深度缓冲深度值时渲染）。
- 面剔除状态（Cull State）：此渲染类型是否启用面剔除。默认启用面剔除。
- 亮度图状态（Lightmap State）：此渲染类型是否使用了亮度纹理。默认不使用亮度纹理。 - 亮度纹理是根据维度时间和环境光照情况计算出的动态生成纹理，大小为16×16。其横坐标代表方块光照，纵坐标代表天空光照，每个位置都代表对应光照条件下的光照颜色。 - 如果渲染类型使用亮度纹理，那么亮度纹理会被绑定在采样器 ``` Sampler2 ``` 上，并覆盖纹理状态定义的 ``` Sampler2 ``` 。
- 叠加层状态（Overlay State）：此渲染类型是否使用了叠加层纹理。默认不使用叠加层纹理。 - 叠加层纹理是一个动态生成纹理，大小为16×16。纹理的上半部分是半透明的红色 rgba(255,0,0,0.69804)，用于生物受伤时的红色渲染；下半部分是白色梯度，从左到右逐渐变得透明，用于TNT的爆炸闪烁。 - 如果渲染类型使用叠加层纹理，那么叠加层纹理会被绑定在采样器 ``` Sampler1 ``` 上，并覆盖纹理状态定义的 ``` Sampler1 ``` 。
- 叠加状态（Layering State）：此渲染类型渲染时，顶点做出的偏移调整，以避免深度冲突。叠加状态有3种可能状态，默认为无叠加。 - 无叠加（No Layering）：顶点不进行任何处理。 - 深度偏移叠加（Polygon Offset Layering）：使用 ``` glPolygonOffset ``` 进行深度偏移以避免深度冲突。其中 ``` factor ``` 为-1， ``` units ``` 为-10，偏移后深度减小。 - 观察偏移叠加（View Offset Z Layering）：对观察矩阵进行缩放以避免深度冲突。缩放比例为0.99975586。 - 观察偏移叠加（放大）（View Offset Z Layering Forward）：对观察矩阵进行缩放以避免深度冲突。缩放比例为1.0002441。
- 输出状态（Output State）：此渲染类型渲染后写入的目标帧缓冲。默认为主帧缓冲。 - 主帧缓冲（Main Target）：游戏最终渲染到屏幕的帧缓冲。 - 轮廓帧缓冲（Outline Target）：游戏渲染实体轮廓所使用的帧缓冲。 - 半透明帧缓冲（Translucent Target）：（仅极佳！图像品质下）游戏用于渲染半透明物体的帧缓冲。 - 粒子帧缓冲（Particles Target）：（仅极佳！图像品质下）游戏渲染粒子的帧缓冲。 - 天气帧缓冲（Weather Target）：（仅极佳！图像品质下）游戏渲染天气雨雪使用的帧缓冲。 - 云帧缓冲（Clouds Target）：（仅极佳！图像品质下）游戏渲染云使用的帧缓冲。 - 物品实体帧缓冲（Item Entity Target）：（仅极佳！图像品质下）游戏渲染物品使用的帧缓冲。
- 纹理变换状态（Texturing State）：此渲染类型对输入的纹理进行了矩阵变换。纹理变换状态有3种可能状态，默认为无纹理变换。 - 无纹理变换（Default Texturing）：纹理不会被变换。 - 偏移纹理变换（Offset Texturing）：纹理按照一定的偏移进行变换。 - 光效纹理变换（Glint Texturing）：游戏提供对物品和方块光效的纹理变换。 - 实体光效纹理变换（Entity Glint Texturing）：游戏提供对实体光效的纹理变换。
- 写入标记状态（Write Mask State）：此渲染类型渲染过程中是否会修改颜色缓冲和深度缓冲。默认颜色缓冲和深度缓冲都会写入。
- 线宽状态（Line State）：此渲染类型渲染过程中的线宽数据。默认为1。
- 颜色逻辑操作状态（Color Logic State）：此渲染类型渲染过程中，着色器输出颜色和帧缓冲中存在的颜色进行的颜色值逻辑操作。颜色逻辑操作状态有2种可能状态，默认为无颜色逻辑操作。 - 无颜色逻辑操作（No Color Logic）：帧缓冲颜色被忽略，直接写入着色器输出颜色。即 ``` GL_COPY ``` 操作。 - 取反或颜色逻辑操作（Or Reverse Color Logic）：帧缓冲颜色取反并与着色器输出颜色进行逻辑或后作为最终写入颜色。即 ``` GL_OR_REVERSE ``` 操作。

除状态外，渲染类型还拥有其他定义参数：

- 顶点格式（Vertex Format）：规定顶点着色器内传入的顶点属性格式。游戏定义了这些顶点属性以供着色器使用： - Position（vec3）：顶点的局部坐标。 - Color（vec4）：顶点的颜色。 - UV/UV0（vec2）：对于Sampler0的纹理坐标。 - UV1（ivec2）：对于Sampler1（通常为叠加层纹理）的纹理坐标。 - UV2（ivec2）：对于Sampler2（通常为亮度纹理）的纹理坐标。 - Normal（vec3）：顶点的法线方向。 - Padding（float）：用于对齐顶点数据加入的填充数据。
- 渲染模式（Mode）：决定此渲染类型将使用什么模式渲染，同时控制了元素缓冲的格式。绝大多数渲染类型使用四边形（Quad）模式渲染，即定义4个顶点，并使用元素缓冲进行索引。
- 缓冲区大小（Buffer Size）：渲染类型单次渲染时的最大缓冲区大小。绝大多数渲染类型缓冲区大小为1536。

下文中，如果状态或定义参数为默认值则被忽略，与默认值不同的属性将在各个渲染类型内写明。

## 渲染类型Uniform

渲染类型规定了一系列Uniform以传入游戏内的各种数据。除上文提及的采样器外，渲染类型还包含下列Uniform可供着色器使用：

- ``` mat4 ModelViewMat ``` ：当前的模型和观察矩阵的乘积。
- ``` mat4 ProjMat ``` ：当前的投影矩阵。
- ``` vec4 ColorModulator ``` ：与输出颜色相乘的颜色。通常为 ``` (1, 1, 1, 1) ``` ，在部分渲染类型中游戏会修改此Uniform来修改片段颜色，比如天空的颜色。
- ``` float GlintAlpha ``` ：光效的不透明度。此值由选项附魔光效闪烁强度控制。
- ``` float FogStart ``` ：雾效果起始距离，由当前所处环境控制。
- ``` float FogEnd ``` ：雾效果可见距离，由当前所处环境控制。
- ``` vec4 FogColor ``` ：雾效果颜色，由当前所处环境控制。
- ``` mat4 TextureMat ``` ：纹理变换矩阵。由渲染类型的纹理变换状态决定，无纹理变换时为单位矩阵。
- ``` vec2 ScreenSize ``` ：游戏当前窗口大小。
- ``` vec3 Light0_Direction ``` ：控制渲染光照的第一个光照方向。
- ``` vec3 Light1_Direction ``` ：控制渲染光照的第二个光照方向。

部分渲染类型还提供了其他Uniform，在对应渲染类型内会写明。

## 渲染类型列表

下列为所有渲染类型和它们对应的信息，以渲染类型的作用进行分组。

### 方块渲染类型

游戏内有多种方块，而这些方块具有各种不同方式的渲染，而这就对应了它们不同的渲染类型。

方块渲染可分为三类：完全不带有透明的渲染、带有完全透明的渲染和带有半透明的渲染。第一种完全不带有透明渲染的方块被称为渲染不透明方块或固体渲染方块，第二种和第三种都被称为渲染透明方块。方块纹理带有的透明部分会因为渲染类型有不同的渲染效果，而单纯的修改方块纹理无法将不透明变为透明或半透明的渲染。

25w07a更新后，方块渲染类型的核心着色器由
```
shaders/core/terrain.fsh
```

和
```
shaders/core/terrain.vsh
```

文件控制。

solid（25w07a前）

状态：启用亮度纹理，使用单纹理状态（方块纹理图集，使用多级渐远纹理）
核心着色器：rendertype_solid
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（vec2）、Normal（vec3）、Padding（float）
额外Uniform：ModelOffset（vec3） - 渲染中的方块的子区块坐标
缓冲区大小：4194304B
渲染所有固体渲染方块，包括移动中的固体渲染方块。使用此渲染类型渲染的方块其纹理会忽略Alpha通道，所以对这些方块而言透明部分没有效果，游戏渲染时会将它们的RGB通道颜色渲染在游戏内，而不是剔除这些像素。在25w07a之前，可以在资源包中修改
```
shaders/core/rendertype_solid.json
```

文件，增加定义一个"ALPHA_CUTOUT"属性值，此值应在0～1之间。当此json定义文件所设定的片段着色器为原版的shaders/core/terrain.fsh时，若一个使用此渲染类型的方块使用了Alpha通道不为1（即含有半透明部分）的纹理，则有如下判定：若透明度低于设定的属性值，游戏将直接放弃对此部分像素的片元着色。这会使这一部分纹理呈现为全透明。
游戏使用此渲染类型渲染世界中的非方块实体方块时，会按照一个子区块为单位上传数据并渲染，以减少渲染调用次数。在作为移动的活塞渲染时按照批次渲染。
cutout_mipped（25w07a前）

状态：启用亮度纹理，使用单纹理状态（方块纹理图集，使用多级渐远纹理）
核心着色器：rendertype_cutout_mipped
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
额外Uniform：ModelOffset（vec3） - 渲染中的方块的子区块坐标
缓冲区大小：4194304B
渲染各种使用多级渐远纹理的渲染透明方块，并渲染移动中的对应方块。此渲染类型的方块可以拥有Alpha通道，默认情况下游戏会丢弃Alpha通道小于0.5的片段以实现透明效果。在25w07a之前，可以在资源包中修改
```
shaders/core/rendertype_cutout_mipped.json
```

文件来更改透明度丢弃判定阈值。
游戏使用此渲染类型渲染世界中的非方块实体方块时，会按照一个子区块为单位上传数据并渲染，以减少渲染调用次数。在作为移动的活塞渲染时按照批次渲染。
使用此渲染类型的方块如下所示：

- 草方块
- 铁栏杆
- 玻璃板
- 绊线钩
- 漏斗
- 铁链
- 铜链
- 红树根
- 高品质或极佳！图像品质下的树叶

cutout（25w07a前）

状态：启用亮度纹理，使用单纹理状态（方块纹理图集）
核心着色器：rendertype_cutout
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
额外Uniform：ModelOffset（vec3） - 渲染中的方块的子区块坐标
缓冲区大小：786432B
渲染各种渲染透明方块，并渲染移动中的对应方块。此渲染类型的方块可以拥有Alpha通道，默认情况下游戏会丢弃Alpha通道小于0.1的片段以实现透明效果。在25w07a之前，可以在资源包中修改
```
shaders/core/rendertype_cutout.json
```

文件来更改丢弃判定阈值。
游戏使用此渲染类型渲染世界中的非方块实体方块时，会按照一个子区块为单位上传数据并渲染，以减少渲染调用次数。在作为移动的活塞渲染时按照批次渲染。
使用此渲染类型的方块如下所示：

- 花
- 棕色蘑菇
- 红色蘑菇
- 草、高草丛、蕨和大型蕨
- 小麦、甜菜根、胡萝卜、马铃薯、下界疣、可可果、仙人掌和甘蔗
- 海带、海草和高海草
- 缠怨藤、垂泪藤、下界苗、下界菌和菌索
- 南瓜茎、结果的南瓜茎、西瓜茎和结果的西瓜茎
- 大型垂滴叶、小型垂滴叶和大型垂滴叶茎
- 杜鹃花丛和盛开的杜鹃花丛
- 甜浆果
- 枯萎的灌木
- 紫颂植株
- 紫颂花
- 树苗
- 竹子
- 藤蔓
- 洞穴藤蔓
- 发光地衣
- 睡莲
- 覆地苔藓
- 孢子花
- 粉红色花簇
- 垂根
- 珊瑚、珊瑚扇
- 海泡菜
- 蜘蛛网
- 玻璃
- 红石线
- 红石中继器和红石比较器
- 门
- 梯子
- 活板门
- 铁轨、激活铁轨、动力铁轨和探测铁轨
- 火把、灵魂火把和红石火把
- 火和灵魂火
- 灯笼和灵魂灯笼
- 营火和灵魂营火
- 刷怪笼、试炼刷怪笼和宝库
- 酿造台
- 信标
- 潮涌核心
- 末地烛
- 花盆
- 脚手架
- 切石机
- 避雷针
- 海龟蛋
- 滴水石锥
- 紫晶芽和紫水晶簇
- 幽匿感测体、幽匿尖啸体和幽匿脉络
- 青蛙卵

translucent

状态：启用亮度纹理，使用单纹理状态（方块纹理图集，使用多级渐远纹理），使用半透明混合，渲染由远到近排序，极佳！图像品质下输出至半透明帧缓冲
核心着色器：rendertype_translucent
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
额外Uniform：ModelOffset（vec3） - 渲染中的方块的子区块坐标
缓冲区大小：786432B
渲染各种半透明方块。使用此渲染类型的方块渲染时纹理可以和后方已经渲染的方块进行混合，以达到半透明效果。
游戏使用此渲染类型渲染世界中的非方块实体方块时，会按照一个子区块为单位上传数据并渲染，以减少渲染调用次数。
使用此渲染类型的方块如下所示：

- 冰和霜冰
- 下界传送门
- 染色玻璃
- 染色玻璃板
- 遮光玻璃
- 黏液块
- 蜂蜜块
- 气泡柱
- 流动水和水

translucent_moving_block

状态：启用亮度纹理，使用单纹理状态（方块纹理图集，使用多级渐远纹理），使用半透明混合，渲染由远到近排序，极佳！图像品质下输出至物品实体帧缓冲
核心着色器：rendertype_translucent_moving_block
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
缓冲区大小：786432B
渲染移动中的使用translucent渲染类型的方块。
与其他渲染类型不同，这类渲染类型一定是被方块实体（移动的活塞）或实体（下落的方块）渲染的，因此此渲染类型不会按子区块为单位渲染，而是按批次渲染的。
tripwire

状态：启用亮度纹理，使用单纹理状态（方块纹理图集，使用多级渐远纹理），使用半透明混合，渲染由远到近排序，极佳！图像品质下输出至天气帧缓冲
核心着色器：rendertype_tripwire
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
额外Uniform：ModelOffset（vec3） - 渲染中的方块的子区块坐标
渲染绊线方块。
对于与绊线连接的绊线钩，绊线钩中的绊线部分不会以此渲染类型渲染，而是使用绊线钩的渲染类型（cutout_mipped）进行渲染。
end_portal

状态：使用多纹理状态

- 第一张纹理（Sampler0）：末地天空纹理（ ``` minecraft:textures/environment/end_sky.png ``` ）
- 第二张纹理（Sampler1）：末地传送门纹理（ ``` minecraft:textures/entity/end_portal.png ``` ）

核心着色器：rendertype_end_portal
顶点格式：Position（vec3）
渲染末地传送门方块。末地传送门方块使用玩家的视角位置计算纹理的渲染坐标。
方块的破坏动画裂痕永远不会在末地传送门方块上渲染。
end_gateway

状态：使用多纹理状态

- 第一张纹理（Sampler0）：末地天空纹理（ ``` minecraft:textures/environment/end_sky.png ``` ）
- 第二张纹理（Sampler1）：末地传送门纹理（ ``` minecraft:textures/entity/end_portal.png ``` ）

核心着色器：rendertype_end_gateway
顶点格式：Position（vec3）
渲染末地折跃门方块。末地折跃门方块使用玩家的视角位置计算纹理的渲染坐标，其算法与末地传送门方块渲染算法相同。
方块的破坏动画永远不会在末地折跃门方块上渲染。

### 方块效果渲染类型

crumbling

状态：使用单纹理状态，使用破坏动画混合，渲染由远到近排序，使用深度偏移叠加，仅写入颜色缓冲
纹理状态：根据破坏程度，分别绑定
```
minecraft:textures/block/destroy_stage_<
n
>.png
```

，其中n是整数，范围0-10，代表方块被破坏的程度。
核心着色器：rendertype_crumbling
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染方块的破坏动画。所有非方块实体都可以自动生成破坏动画，而方块实体根据其渲染类型的不同方块破坏动画会在一部分被创建或根本没有破坏动画。
破坏动画不受平滑光照（环境光遮蔽）和光照影响，顶点属性Color固定为白色（
```
(1, 1, 1, 1)
```

），且不会传入亮度纹理。
beacon_beam

状态：使用单纹理状态（
```
minecraft:textures/entity/beacon_beam.png
```

），渲染由远到近排序
混合状态：渲染外层光柱使用半透明混合，渲染内层不混合
写入状态：渲染外层光柱仅写入颜色缓冲，渲染内层颜色缓冲和深度缓冲都会写入
核心着色器：rendertype_beacon_beam
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染信标和末地折跃门的光柱。

### 实体渲染类型

entity_solid

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关）
核心着色器：rendertype_entity_solid
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染部分实体和部分方块实体的不透明部分：

- 未激活的潮涌核心、床、饰纹陶罐、盾牌、三叉戟
- 钟的铃铛部分
- 旗帜的支撑杆部分
- 附魔台和讲台上面的书部分
- 物品展示框和画的背景部分
- 玩家的披风渲染层、Deadmau5专属皮肤的耳朵部分、潜影贝头部分
- 玩家第一人称视角下主手的第一层皮肤

entity_cutout

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关）
核心着色器：rendertype_entity_cutout
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染部分实体和部分方块实体的使用不带有半透明像素纹理的渲染部分：

- 蝙蝠、箭、浮漂、箱子
- 游戏内除地形渲染外所有带有非渲染半透明方块和对应方块物品的渲染部分，包括物品实体、矿车、方块展示实体等实体内部渲染方块和方块物品的部分，也包括GUI内
- 着火实体的火焰渲染层

entity_cutout_no_cull

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），禁用面剔除
核心着色器：rendertype_entity_cutout_no_cull
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染绝大多数实体使用不带有半透明像素纹理的渲染部分，这些渲染部分不会进行面剔除，视角在这些模型内部时仍然能看到外围的面。下列渲染部分使用此渲染类型：

- 绝大多数实体的所有渲染层，如果没有特殊说明指定某个渲染层使用某个渲染类型，则默认为此渲染类型
- 守卫者和远古守卫者的光柱
- 激活的潮涌核心
- 潜影盒以及对应方块物品在所有渲染位置的渲染
- 告示牌的背景

entity_cutout_no_cull_z_offset

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），禁用面剔除，观察偏移叠加
核心着色器：rendertype_entity_cutout_no_cull_z_offset
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染实体中可能发生深度冲突的渲染层：

- 潜影贝的壳
- 生物头颅（玩家的头除外）及其方块物品在所有渲染位置的渲染

entity_smooth_cutout

状态：启用亮度纹理，使用单纹理状态（
```
minecraft:textures/entity/end_crystal/end_crystal_beam.png
```

），禁用面剔除
核心着色器：rendertype_entity_smooth_cutout
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染末地水晶光柱。

entity_no_outline

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），禁用面剔除，半透明混合，渲染由远到近排序，仅写入颜色缓冲
核心着色器：rendertype_entity_no_outline
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染下列实体部分：

- 旗帜的颜色和图案
- 盾牌的颜色和图案

与其他实体渲染类型不同，此渲染类型永远不会将信息写入轮廓数据中，当游戏渲染实体的发光轮廓时这部分将不会参与轮廓计算，从而不影响实体的轮廓渲染。
eyes

状态：使用单纹理状态（纹理与当前渲染物体有关），加性混合，渲染由远到近排序，仅写入颜色缓冲
核心着色器：rendertype_eyes
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染末影人、幻翼、蜘蛛和末影龙的眼睛。
渲染眼睛时游戏并不是只渲染眼睛部分，而是将实体所有部分都渲染，即对实体的模型渲染了两次，但使用了不同的纹理。其中一张是正常的实体纹理，另一张是专门的眼睛纹理，两张纹理的各个纹理位置保持一致。第一次游戏渲染实体非眼睛的部分，第二次游戏使用此渲染类型渲染眼睛。由于此渲染类型使用了加性混合模式，此渲染类型渲染的片段会与第一次渲染的实体模型互相混合，使得这一次渲染看起来像带有内置透明度，但实际上只是混合的结果。
entity_translucent_emissive

状态：启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，禁用面剔除，仅写入颜色缓冲
核心着色器：rendertype_entity_translucent_emissive
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染下列实体部分：

- 监守者可自发光部分
- 旋风人眼睛部分

与eyes渲染类型类似，此渲染类型渲染时也是渲染整个实体模型，而非只渲染一部分。
entity_alpha

状态：使用单纹理状态（
```
minecraft:textures/entity/enderdragon/dragon_exploding.png
```

），禁用面剔除
核心着色器：rendertype_entity_alpha
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
初步渲染末影龙死亡动画中的末影龙模型，为接下来的末影龙模型渲染做准备。
此渲染类型顶点中的Color（vec4）属性随末影龙死亡动画的进行程度从黑色逐渐转为白色。默认情况下，游戏使用此渲染类型过滤末影龙模型噪声纹理中颜色暗于当前顶点Color属性的部分，留下颜色亮于Color属性的部分，以创造末影龙逐渐破损消失的效果。更多信息见下文entity_decal。
entity_decal

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（
```
minecraft:textures/entity/enderdragon/dragon.png
```

），禁用面剔除，等于深度测试
核心着色器：rendertype_entity_decal
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染末影龙死亡动画中的末影龙。
游戏先使用entity_alpha渲染类型渲染整个末影龙模型，根据当前动画程度过滤掉部分片段，留下的片段写入深度缓冲。之后游戏再使用entity_decal渲染类型渲染整个末影龙模型，启用等于深度测试，只保留当前深度缓冲中与当前末影龙模型深度相同的片段，以实现entity_alpha的过滤效果。如果当前深度缓冲中有与末影龙模型深度相同的片段，那么此渲染类型也会在这个片段上渲染，从而造成错误渲染。
entity_translucent

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，禁用面剔除
核心着色器：rendertype_entity_translucent
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染大多数带有半透明纹理的实体或方块实体部分：

- 恼鬼、悦灵、旋风人、风弹
- 玩家除第一人称视角下主手第一层皮肤外的所有渲染层
- 史莱姆、潜影弹的外层渲染
- 马的斑纹，狼身上的狼铠
- 玩家的头
- 远古守卫者施加挖掘疲劳时产生的屏幕粒子效果
- [图:布尔型]Marker为true的盔甲架对于可以看到此盔甲架的玩家的渲染

item_entity_translucent_cull

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，极佳！图像品质下输出至物品实体帧缓冲
核心着色器：rendertype_item_entity_translucent_cull
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染部分物品、方块和部分实体的渲染：

- 不满足entity_cutout所有要求的物品和方块渲染
- 经验球
- 不可见生物对于可以看到此生物的玩家的渲染

armor_cutout_no_cull、armor_decal_cutout_no_cull

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），禁用面剔除，观察偏移叠加
深度测试：armor_cutout_no_cull为小于等于深度测试，armor_decal_cutout_no_cull为等于深度测试
核心着色器：rendertype_armor_cutout_no_cull
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
armor_cutout_no_cull用于各种盔甲和鞘翅的渲染，也用于[图:布尔型]decal为false的盔甲纹饰渲染。
armor_decal_cutout_no_cull用于[图:布尔型]decal为true的盔甲纹饰渲染。

lightning

状态：闪电混合，渲染由远到近排序，极佳！图像品质下输出至天气帧缓冲
核心着色器：rendertype_lightning
顶点格式：Position（vec3）、Color（vec4）
渲染闪电和末影龙死亡动画中的闪光。

### 实体效果渲染类型

entity_shadow

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（
```
minecraft:textures/misc/shadow.png
```

），半透明混合，观察偏移叠加，仅写入颜色缓冲
核心着色器：rendertype_entity_shadow
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染实体的阴影。当游戏渲染实体后，游戏会计算有多少方块会被阴影覆盖，并在每个方块的上表面开始渲染阴影，换言之阴影是按照方块网格对齐进行渲染的。
阴影有下列渲染要求，当其中任何一条不满足时阴影就不会渲染：

- 选项实体阴影开启
- 实体不在物品栏内渲染
- 实体必须可见
- 实体阴影半径和阴影强度大于0
- 实体距离摄像机256格内

阴影半径最大32格，以实体底面中心点计算一个半球形，游戏会将涉及的方块都参与计算。每个方块游戏也会判断是否应该在这个方块的上表面上渲染：

- 方块必须有方块模型，即无模型的方块实体将无法渲染阴影
- 方块必须具有完整的碰撞箱
- 方块必须有轮廓箱
- 方块此处的内部光照等级大于3

根据方块与实体的距离，阴影也会有相应的顶点颜色Color改变。
leash

状态：启用亮度纹理，禁用面剔除
核心着色器：rendertype_leash
顶点格式：Position（vec3）、Color（vec4）、UV2（ivec2）
渲染模式：三角形条带（Triangle Strip）
渲染拴绳，不包括拴绳结。

water_mask

状态：仅写入深度缓冲
核心着色器：rendertype_water_mask
顶点格式：Position（vec3）
在船渲染之后，如果船没有沉入水下，那么游戏在船的内部使用此渲染模型渲染一个水面补丁（Water Patch）模型，使得船内部有一个完全透明的空间，以阻止水面在这个透明空间内渲染。
由于此渲染类型仅写入深度缓冲，修改核心着色器的输出颜色将完全不起效果。能对渲染产生效果的方式只有下方两种方式：

- 修改顶点着色器使得模型渲染偏移
- 修改片段着色器丢弃片段

breeze_wind

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，偏移纹理变换，禁用面剔除
核心着色器：rendertype_breeze_wind
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染旋风人和风弹周围的旋风

energy_swirl

状态：启用亮度纹理，启用叠加层纹理，使用单纹理状态（纹理与当前渲染物体有关），加性混合，渲染由远到近排序，偏移纹理变换，禁用面剔除
核心着色器：rendertype_energy_swirl
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV1（ivec2）、UV2（ivec2）、Normal（vec3）、Padding（float）
渲染苦力怕的旋转电弧和半血凋灵的护甲。

outline

状态：使用单纹理状态（纹理与当前渲染物体有关），禁用深度测试，输出至轮廓帧缓冲
面剔除状态：作为实体轮廓时与实体渲染类型是否禁用面剔除有关，其他情况下禁用面剔除
核心着色器：rendertype_outline
顶点格式：Position（vec3）、UV0（vec2）、Color（vec4）
渲染轮廓：

- 实体的轮廓
- 不可见发光实体的轮廓
- 不可见发光哞菇背上的蘑菇
- 不可见发光羊身上的羊毛渲染层
- 不可见发光史莱姆的外层渲染
- 不可见发光雪傀儡的南瓜头

### 光效渲染类型

glint

状态：使用单纹理状态（
```
minecraft:textures/misc/enchanted_glint_item.png
```

，模糊状态与独立纹理设置相同），光效混合，禁用面剔除，等于深度测试，光效纹理变换，仅写入颜色缓冲
核心着色器：rendertype_glint
顶点格式：Position（vec3）、UV0（vec2）
渲染物品的光效。根据图像品质不同渲染的物品光效不同：

- 非极佳！图像品质下，渲染所有物品（三叉戟除外）的光效
- 极佳！图像品质下，渲染不使用item_entity_translucent_cull渲染类型的物品的光效

glint_translucent

状态：使用单纹理状态（
```
minecraft:textures/misc/enchanted_glint_item.png
```

，模糊状态与独立纹理设置相同），光效混合，禁用面剔除，等于深度测试，光效纹理变换，仅写入颜色缓冲，输出至物品实体帧缓冲
核心着色器：rendertype_glint_translucent
顶点格式：Position（vec3）、UV0（vec2）
仅在极佳！图像品质下生效，渲染使用item_entity_translucent_cull渲染类型的物品的光效。

armor_entity_glint

状态：使用单纹理状态（
```
minecraft:textures/misc/enchanted_glint_entity.png
```

，模糊状态与独立纹理设置相同），光效混合，禁用面剔除，等于深度测试，实体光效纹理变换，观察偏移叠加，仅写入颜色缓冲
核心着色器：rendertype_armor_entity_glint
顶点格式：Position（vec3）、UV0（vec2）
渲染盔甲和鞘翅的光效。

entity_glint
状态：使用单纹理状态（
```
minecraft:textures/misc/enchanted_glint_entity.png
```

，模糊状态与独立纹理设置相同），光效混合，禁用面剔除，等于深度测试，实体光效纹理变换，仅写入颜色缓冲，极佳！图像品质下输出至物品实体帧缓冲
核心着色器：rendertype_entity_glint
顶点格式：Position（vec3）、UV0（vec2）
此渲染类型没有任何作用。

### 文字渲染类型

text

状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序
核心着色器：rendertype_text
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
缓冲区大小：786432B
渲染下列物体：

- 地图的背景和地图内部图形
- 使用非灰度图的位图字体、unihex字体和丢失的字体的文本（不包括[图:布尔型]see_through为true的文本展示实体内的文本和未潜行时的实体名牌，也不包括所有告示牌内的文本）

text_polygon_offset
状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，深度偏移叠加
核心着色器：rendertype_text
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
与text类似渲染文本，但不同点在于此渲染类型防止深度冲突进行了偏移。渲染使用非灰度图的位图字体、unihex字体和丢失的字体的告示牌内的文本。
text_see_through

状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，禁用深度测试，仅写入颜色缓冲
核心着色器：rendertype_text_see_through
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
[图:布尔型]see_through为true的文本展示实体内和未潜行时的实体名牌中使用非灰度图的位图字体、unihex字体和丢失的字体的文本。

text_intensity

状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序
核心着色器：rendertype_text_intensity
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
缓冲区大小：786432B
渲染使用灰度图的位图字体或矢量字体的文本（不包括[图:布尔型]see_through为true的文本展示实体内的文本和未潜行时的实体名牌，也不包括所有告示牌内的文本）
text_intensity_polygon_offset
状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，深度偏移叠加
核心着色器：rendertype_text_intensity
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
与text_intensity类似渲染文本，但不同点在于此渲染类型防止深度冲突进行了偏移。渲染使用灰度图的位图字体或矢量字体的告示牌内的文本。
text_intensity_see_through

状态：启用亮度纹理，使用单纹理状态（纹理与当前渲染物体有关），半透明混合，渲染由远到近排序，禁用深度测试，仅写入颜色缓冲
核心着色器：rendertype_text_intensity_see_through
顶点格式：Position（vec3）、Color（vec4）、UV0（vec2）、UV2（ivec2）
[图:布尔型]see_through为true的文本展示实体内和未潜行时的实体名牌中使用灰度图的位图字体或矢量字体的文本。

text_background

状态：启用亮度纹理，半透明混合，渲染由远到近排序
核心着色器：rendertype_text_background
顶点格式：Position（vec3）、Color（vec4）、UV2（ivec2）
渲染[图:布尔型]see_through为false的文本展示实体的背景。

text_background_see_through

状态：启用亮度纹理，半透明混合，渲染由远到近排序，禁用深度测试，仅写入颜色缓冲
核心着色器：rendertype_text_background_see_through
顶点格式：Position（vec3）、Color（vec4）、UV2（ivec2）
渲染[图:布尔型]see_through为true的文本展示实体的背景。

### GUI渲染类型

gui

状态：半透明混合
核心着色器：rendertype_gui
顶点格式：Position（vec3）、Color（vec4）
缓冲区大小：786432B
渲染GUI内的各种纯色和渐变元素，包括各种垂直和水平的连接线、各种GUI组件中纯色或渐变色背景等。

gui_overlay

状态：半透明混合，禁用深度测试，仅写入颜色缓冲
核心着色器：rendertype_gui_overlay
顶点格式：Position（vec3）、Color（vec4）
渲染各种在其他GUI组件上的其他渲染效果：

- 物品栏内光标悬浮于物品上的高亮遮罩效果
- 物品栏内物品的耐久条组件和冷却效果
- 加载屏幕的背景
- 所有调试图表
- 编辑框组件内的插入文本光标
- 睡觉的屏幕遮罩和使用望远镜时的屏幕遮罩

gui_text_highlight

状态：半透明混合，禁用深度测试，取反或颜色逻辑操作
核心着色器：rendertype_gui_text_highlight
顶点格式：Position（vec3）、Color（vec4）
所有可编辑区域中文本选中区域高亮效果。

gui_ghost_recipe_overlay

状态：半透明混合，大于深度测试，仅写入颜色缓冲
核心着色器：rendertype_gui_ghost_recipe_overlay
顶点格式：Position（vec3）、Color（vec4）
渲染所有合成类槽位内的物品虚影。

### 杂项渲染类型

clouds

状态：使用单纹理状态（
```
minecraft:textures/environment/clouds.png
```

），半透明混合，渲染由远到近排序，极佳！图像品质下输出至云帧缓冲
写入状态：在云为高品质时仅写入深度缓冲，其他情况下颜色缓冲和深度缓冲都写入
核心着色器：rendertype_clouds
顶点格式：Position（vec3）、Color（vec3）
渲染云。

lines

状态：半透明混合，渲染由远到近排序，禁用面剔除，观察偏移叠加，极佳！图像品质下输出至物品实体帧缓冲
核心着色器：rendertype_lines
顶点格式：Position（vec3）、Color（vec4）、Normal（vec3）、Padding（float）
渲染模式：线（Lines）
额外Uniform：LineWidth（float） - 线的宽度，按像素计
渲染游戏中出现的各种线：

- 方块的轮廓箱边界显示
- 调试中的区块角落的竖线
- 调试中的实体碰撞箱边界显示
- 调试屏幕中的准星
- 结构方块的范围边界显示

line_strip
状态：半透明混合，渲染由远到近排序，禁用面剔除，观察偏移叠加，极佳！图像品质下输出至物品实体帧缓冲
核心着色器：rendertype_lines
顶点格式：Position（vec3）、Color（vec4）、Normal（vec3）、Padding（float）
渲染模式：线条（Line Strip）
额外Uniform：LineWidth（float） - 线的宽度，按像素计
渲染钓鱼线。
world_border

状态：禁用面剔除，观察偏移叠加，使用单纹理状态（
```
minecraft:textures/misc/forcefield.png
```

），使用半透明混合，渲染由远到近排序，极佳！图像品质下输出至天气帧缓冲
核心着色器：rendertype_world_border
顶点格式：Position（vec3）、UV0（vec2）
渲染世界边界。

# 非渲染类型核心着色器

部分核心着色器不作为渲染类型进行渲染，或在某些条件下不作为渲染类型渲染，那么它们就是非渲染类型的核心着色器。在命名规范上，所有渲染类型核心着色器都以rendertype开头，而非渲染类型核心着色器不以rendertype开头以作区分，但实际上渲染类型可能使用非渲染类型的核心着色器。

与渲染类型核心着色器类似，非渲染类型的核心着色器仍然带有顶点格式这一基本参数，Uniform也与渲染类型核心着色器一致，状态也类似。但是因为非渲染类型用途广泛其状态在不同情况下有较大的不同，下文不会具体说明这些着色器的状态。

particle

顶点格式：Position（vec3）、UV0（vec2）、Color（vec4）、UV2（ivec2）
渲染所有粒子，以及雨雪效果。
渲染粒子受到亮度纹理（Sampler2）影响。

position

顶点格式：Position（vec3）
渲染下列物体：

- 主世界的天空和星星
- 位于海平面以下的虚空黑幕

position_color

顶点格式：Position（vec3）、Color（vec4）
渲染各种纯色物体：

- 日出与日落的天空颜色效果
- 调试屏幕的饼图
- 调试中的区块边界

position_tex

顶点格式：Position（vec3）、UV0（vec2）
渲染各种不需要额外着色的纹理：

- 太阳与月亮
- 世界边界
- 水下的屏幕效果
- GUI内所有精灵图贴图组件，包括按钮、各种屏幕背景、各种图标等

position_tex_color

顶点格式：Position（vec3）、UV0（vec2）、Color（vec4）
渲染各种需要额外着色的纹理：

- 全景图
- 末地的天空
- 窒息屏幕效果的遮罩层
- 玩家着火的遮罩层
- GUI内所有需要额外着色精灵图贴图组件

blit_screen
顶点格式：Position（vec3）
转移帧缓冲数据的着色器，见下文后处理管线。
此着色器无法被资源包覆盖，游戏在预载着色器时使用原版资源包数据预载此着色器，在之后此着色器就不会被卸载。
如果此着色器有错误等无法正常加载的情况，那么游戏会崩溃退出。
lightmap

顶点格式：Position（vec3）
动态生成亮度纹理的着色器。
如果此着色器无法被加载，则亮度纹理永远不会被更新。
游戏对此着色器提供下列额外的Uniform：

- ``` float AmbientLightFactor ``` ：维度的环境光照强度，此值为维度类型定义中的[图:单精度浮点数]ambient_light。
- ``` float SkyFactor ``` ：天空光强度因子，此值主要受到时间影响，按照昼夜循环周期变化。当产生闪电时此值变为1。
- ``` float BlockFactor ``` ：方块光强度因子，此值不受外界因素影响，随机波动。
- ``` float NightVisionFactor ``` ：夜视强度因子，受到夜视和潮涌能量（必须在水中时）状态效果影响。
- ``` float DarknessScale ``` ：黑暗系数，受到黑暗状态效果影响。
- ``` float DarkenWorldFactor ``` ：世界黯淡系数，受到Boss迷雾影响（Boss栏数据中的[图:布尔型]DarkenScreen）。
- ``` float BrightnessFactor ``` ：明亮系数，此值受到选项“亮度”的影响，不低于0。
- ``` vec3 SkyLightColor ``` ：天空光基础颜色，只受到时间影响随昼夜循环周期变化。
- ``` vec3 AmbientColor ``` ：环境颜色，只与当前是否存在末地天空闪光有关。

position_color_lightmap
此核心着色器没有任何作用。
position_color_tex_lightmap
此核心着色器没有任何作用。

# 后处理管线

当游戏渲染整个世界场景或处理各种屏幕效果时，游戏会调用后处理管线以进行后处理效果渲染。

游戏调用后处理管线时，调试屏幕的
```
post_effect
```

行也会显示当前调用的后处理管线。

## 后处理管线程序格式

后处理管线程序文件都位于
```
assets/minecraft/post_effect
```

内。游戏不支持添加后处理管线程序，只允许修改已有的后处理管线。游戏有内置的后处理管线程序，见下。

后处理管线程序文件拥有下面的通用格式：

- [图:NBT复合标签/JSON对象] JSON文件根元素 - [图:NBT复合标签/JSON对象]targets：指定后处理管线中需要创建以使用的自定义渲染目标。 - [图:NBT复合标签/JSON对象]<命名空间ID>：以指定的命名空间ID创建一个渲染目标。 - 见下文后处理渲染目标。 - [图:NBT列表/JSON数组]passes：渲染过程列表。 - [图:NBT复合标签/JSON对象]：一个渲染过程。 - 见下文后处理渲染过程。

## 后处理渲染目标

后处理管线可以创建临时的渲染目标用于辅助渲染。

每个后处理渲染目标都有3个属性：

- 名称：在之后的渲染过程中调用此帧缓冲的唯一名称。
- 宽度：渲染目标内帧缓冲的宽度。如果未指定则为当前窗口宽度。
- 高度：渲染目标内帧缓冲的高度。如果未指定则为当前窗口高度。

在JSON文件中，后处理帧缓冲必须使用一个对象定义。如果设置渲染目标内帧缓冲为窗口大小，则只需要填入空对象；如果需要特殊设置渲染目标内的帧缓冲大小，则需要按照下列格式定义：

- [图:字符串][图:NBT复合标签/JSON对象] - [图:整型]*width：渲染目标帧缓冲的宽度。 - [图:整型]*height：渲染目标帧缓冲的高度。 - [图:布尔型]persistent：（默认为 ``` false ``` ）渲染目标是否在每帧之间持久化存在。调整屏幕大小时渲染目标的内容会被清除。 - [图:整型][图:NBT列表/JSON数组]clear_color：（默认为 ``` [0, 0, 0, 0] ``` ）渲染目标被创建或清除时，将使用此值填充颜色。内部的四个浮点数分别表示R、G、B、A的值。 - - ARGB颜色，见Template:Nbt inherit/argb color/source

后处理渲染目标不允许重复定义。如果有两个渲染目标的名称一致，那么游戏会在日志中产生下列警告并阻止资源包加载：

```
<后处理渲染目标名称> is already defined
```

除自定义的后处理渲染目标外，游戏会向渲染管线提供一些后处理渲染目标。这些目标的名称带有minecraft命名空间，且命名空间不能省略。游戏向所有的后处理管线都提供了
```
minecraft:main
```

渲染目标，它代表的是游戏当前主屏幕渲染目标，即最后游戏渲染效果的渲染目标。除了
```
minecraft:main
```

外，在不同的后处理管线中，游戏还会提供一些不同的额外的渲染目标，见下文的说明，如果后处理管线程序手动定义了与这些渲染目标名称相同的渲染目标，那么这项自定义目标会被忽略，游戏仍然使用游戏通过的渲染目标。

## 后处理渲染过程

在后处理管线中可以有多次渲染过程，每次渲染过程都进行下述步骤：

1. 游戏读取这次渲染过程中需要的输入渲染目标（Input Target），并传入采样器。 - 输入渲染目标的名称使用[图:字符串]sampler_name自定义。 - 输入渲染目标可以来自现有的帧缓冲，也可以来自于纹理。 - 输入渲染目标可以来自于帧缓冲的颜色缓冲，也可以来自于帧缓冲的深度缓冲，定义时两者差别仅在[图:布尔型]use_depth_buffer设置值。 - 输入渲染目标可以直接来自于纹理，游戏会根据[图:字符串]location的值自动查找纹理。如果查找失败，则资源包加载失败，日志报错 ``` Texture '< 纹理路径 >' does not exist ``` 。
1. 游戏根据当前的状态设置各种Uniform。游戏会提供下列Uniform，后处理着色器都可以使用这些Uniform进行渲染： - ``` sampler2D < 输入渲染目标名称 >Sampler ``` ：输入渲染目标的绑定的采样器。 - ``` vec2 < 输入渲染目标名称 >Size ``` ：输入渲染目标的尺寸，以像素为单位。 - ``` vec2 OutSize ``` ：输出渲染目标帧缓冲的尺寸，以像素为单位。 - ``` vec2 ScreenSize ``` ：窗口尺寸，以像素为单位。 - ``` float GameTime ``` ：渲染计时器，取值为0到1，以20分钟（即1200秒）为单位，每20分钟重置一次。 - ``` mat4 ProjMat ``` ：后处理着色器的投影矩阵。此矩阵是一个正射投影矩阵，宽度为窗口宽度，高度为窗口高度，近平面为0.1，远平面为1000。
1. 根据渲染过程单独定义的Uniform，将对应的数据传入对应的Uniform。这些设置值会覆盖着色器内定义的Uniform默认值。 - 与着色器内不同，这里设置的Uniform长度最大只有4，使得无法设置类型为mat3或mat4的Uniform，且只允许使用单精度浮点数。
1. 调用指定的着色器，将渲染结果写入输出渲染目标（Output Target）。

输入渲染目标和输出渲染目标不应该一致。如果需要修改输入的渲染目标，则应该先创建一个临时的渲染目标，写入临时渲染目标后再写回原渲染目标。

渲染过程的JSON格式如下所示：

- [图:NBT复合标签/JSON对象] - [图:字符串]*output：（命名空间ID）输出渲染目标。 - [图:NBT列表/JSON数组]inputs：输入渲染目标列表。 - [图:NBT复合标签/JSON对象]：一个输入渲染目标。 - [图:布尔型]bilinear：（默认为 ``` false ``` ）渲染目标帧缓冲是否采用线性过滤，否则将使用邻近过滤。 - [图:字符串]*sampler_name：输入渲染目标名称。 - - 如果输入目标是一个后处理帧缓冲： - [图:字符串]*target：（命名空间ID）输入渲染目标绑定的后处理帧缓冲。 - [图:布尔型]use_depth_buffer：（默认为 ``` false ``` ）是否使用渲染目标内帧缓冲中的深度缓冲而不是颜色缓冲。 - - 如果输入目标是一个纹理： - [图:字符串]*location：（命名空间ID）输入渲染目标绑定的纹理。游戏将此命名空间ID自动转换为资源包内 ``` assets/< 命名空间 >/textures/effect/< 路径 >.png ``` - [图:整型]*width：纹理的宽度。 - [图:整型]*height：纹理的高度。 - [图:字符串]*vertex_shader：此次渲染过程使用的顶点着色器。游戏将此名称自动转换为 ``` assets/< 命名空间 >/shaders/< 路径 >.vsh ``` 路径。 - [图:字符串]*fragment_shader：此次渲染过程使用的片段着色器。游戏将此名称自动转换为 ``` assets/< 命名空间 >/shaders/< 路径 >.fsh ``` 路径。 - [图:NBT复合标签/JSON对象]uniforms：设置这次渲染过程中的Uniform。 - [图:NBT列表/JSON数组]<分组名称>：一组Uniform。 - [图:NBT复合标签/JSON对象]：设置一个Uniform。 - [图:字符串]*name：Uniform变量名。 - [图:字符串]*type：Uniform的类型。 - [图:任意类型]*value：Uniform的值。数据类型取决于Uniform的类型。

## 可用后处理管线

游戏提供了下列可以修改的后处理管线，资源包可以修改这些后处理管线文件从而修改不同的渲染效果。

transparency
极佳！图像品质中，游戏将半透明、物品实体、粒子、云、天气渲染目标传入此后处理管线，组合渲染出整个世界的渲染。

游戏对这个后处理管线额外传入了下列渲染目标：

- translucent - 绑定半透明帧缓冲
- item_entity - 绑定物品实体帧缓冲
- particles - 绑定粒子帧缓冲
- weather - 绑定天气帧缓冲
- clouds - 绑定云帧缓冲

此后处理管线最后需要写入主屏幕渲染目标才可以起到作用。

当此后处理管线加载失败时，游戏会强制崩溃，输出崩溃报告，并将图像品质设置为高品质。

entity_outline
处理轮廓帧缓冲，后处理实体轮廓。

游戏对这个后处理管线额外传入了
```
final
```

后处理渲染目标，用于保存实体轮廓后处理结果。此管线不应该修改主屏幕渲染目标，当游戏处理轮廓后处理后会自动合并到主屏幕渲染目标内。

当此后处理管线读取失败或JSON格式错误时，游戏会静默处理，只在日志中输出警告，而不会终止资源包加载，但此时游戏将不能渲染任何轮廓。

blur
游戏渲染GUI模糊背景时使用此后处理管线后处理主屏幕渲染目标，之后在后处理过的主屏幕渲染目标再渲染其他GUI。

游戏会自动传入一个名为
```
Radius
```

的Uniform，类型为
```
float
```

。此值与选项中的菜单背景模糊程度一致。

当此后处理管线读取失败或JSON格式错误时，游戏会静默处理，只在日志中输出警告，而不会终止资源包加载，但此时游戏将无法模糊GUI背景。

creeper
当玩家以旁观模式进入苦力怕视角时，屏幕的后处理管线效果。此后处理管线需要写入到主屏幕渲染目标。

当此后处理管线读取失败或JSON格式错误时，游戏会静默处理，只在日志中输出警告，而不会终止资源包加载，但此时游戏将不能渲染苦力怕视角效果。

spider
当玩家以旁观模式进入蜘蛛视角时，屏幕的后处理管线效果。此后处理管线需要写入到主屏幕渲染目标。

当此后处理管线读取失败或JSON格式错误时，游戏会静默处理，只在日志中输出警告，而不会终止资源包加载，但此时游戏将不能渲染蜘蛛视角效果。

invert
当玩家以旁观模式进入末影人视角时，屏幕的后处理管线效果。此后处理管线需要写入到主屏幕渲染目标。

当此后处理管线读取失败或JSON格式错误时，游戏会静默处理，只在日志中输出警告，而不会终止资源包加载，但此时游戏将不能渲染末影人视角效果。

# 历史

# 参考

1. ↑ MC-46727（评论#219617）
1. ↑ https://twitter.com/_grum/status/627141591942209536

# 导航
