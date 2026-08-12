---
name: minecraft-font
description: |
  字体（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于使用资源包自定义字体，请见“自定义字体”。
  
  【涵盖内容】
  - Unifont JP
  - 私用区
  
  【关键定义】
  - 数据包路径：data/assets/minecraft/font/unifont.zip、data/.minecraft/assets/objects、data/assets/minecraft/font/unifont_jp.zip、data/assets/minecraft/font/unifont_pua.zip
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 字体 的完整规范时
---

关于使用资源包自定义字体，请见“自定义字体”。

Minecraft的游戏界面和相关网站使用了多种不同的字体（Font）来展现其艺术风格。

# Mojangles

Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm
Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz
1 2 3 4 5 6 7 8 9 0
! @  #  $  £  %  ^  &  *  (  )  _ - + = ~ [ ] { } | \ : ; " ' , < > . ? /
Mojangles是Minecraft的标志性原创字体，也是多数游戏界面的默认字体。该字体亦称Minecraft Seven，因字模高度为7个像素而得名。

该字体支持的每个字符宽度在1到6个点之间。在32（空格）和126（~）之间的所有ASCII字符均为5个点宽，但以下字符除外：

字符间的间隔为1个点宽。该字体目前支持拉丁字母、希腊字母、西里尔字母、亚美尼亚字母和格鲁吉亚字母，以及希伯来语辅音音素文字。

Mojangles支持很多字符，但并非支持所有字符。其余游戏支持的一些需要更多细节才能展示的字符（例如泰米尔文字和汉字）使用GNU Unifont，见下文。

当前Mojangles支持的所有字符如下：

Mojangles的字形存储在
```
ascii.png
```

、
```
accented.png
```

和
```
nonlatin_european.png
```

中。

在Java版中，将文本组件的
```
font
```

指定为
```
minecraft:default
```

即可使用该字体；这也是游戏默认选用的字体。在基岩版中，可以在聊天屏幕的选项中将聊天字体切换为此。

在基岩版中，Mojangles使用Java版1.13-pre6前的版本，这意味着基岩版的Mojangles字体使用旧字形，且不支持后续加入的字符。基岩版Ore UI中使用的Mojangles（游戏文件中字体名称为Minecraft Seven v2）额外支持希腊字母和西里尔字母。

# GNU Unifont

游戏使用“Unicode字体”显示任何不受Mojangles支持的字符，例如汉字和全角标点等。而这一“Unicode字体”实际上是GNU Unifont。Unifont的字模大小为16×16，线条更细。

默认情况下，如果欲显示的字符不被Mojangles字体支持，则将改用Unifont提供字形。

在Java版中，若打开“强制使用Unicode字体”选项，则游戏中所有的文本都会使用Unifont显示。可以利用此功能让告示牌的文本在关闭强制使用Unicode字体时溢出告示牌。

在基岩版中，“Unicode字体”使用的Unifont版本为
```
v5.1
```

，仅支持基本多文种平面的部分内容；这意味着该字体仅包含了Unicode码位在
```
0000 - FFFF
```

区间内的部分字符，而未包含其他字符。在Java版中，使用的Unifont版本为
```
v17.0.01
```

，对基本多文种平面的支持更完全，还支持其他平面的部分字符。

由于游戏渲染机制的限制，部分需要OpenType特性以正确显示的文字无法在游戏中正确显示。例如，藏文、天城文等文字可以显示单独的部件，但无法显示连字。

在Java版中，Unifont字体文件为散列资源文件，可以用资源路径
```
assets/minecraft/font/unifont.zip
```

在
```
.minecraft/assets/objects
```

中查询。在基岩版中，Unifont的字形存储在
```
assets/resource_packs/vanilla/font/glyph_
NN
.png
```

。

在Java版中，将文本组件的
```
font
```

指定为
```
minecraft:uniform
```

即可使用该字体。

在基岩版中，当显示的字符不被Mojangles字体支持时，整个文本中的字符都会使用Unifont显示。

## Unifont JP

本段落所述内容仅适用于Java版。

在Unicode编码中，不同地区的同源汉字按照特定规律被统合为单一的字符，即中日韩统一表意文字。然而，不同地区的汉字字形标准也不同，如果这些汉字全以同一字形显示，那么可能并不符合读者当地的字形规范。因此，想要正确地在不同语境下显示这些汉字，需要使用多个字体，或是在同一字体中提供多种字形备选。为在日文语境下以日本标准字形显示汉字，Minecraft使用了前一种方案。

Minecraft使用Unifont JP字体提供日本标准的汉字字形，常规版本的Unifont则提供中国大陆的规范汉字字形。Unifont JP字体不会随游戏内语言的切换而自动开关，只能通过“日本字形变体”选项切换，该选项的默认值基于系统语言环境设置。

Unifont JP的字体文件为散列资源文件，可以用资源路径
```
assets/minecraft/font/unifont_jp.zip
```

在
```
.minecraft/assets/objects
```

中查询。游戏使用的Unifont JP版本为
```
v17.0.01
```

。

## 私用区

本段落所述内容仅适用于Java版。
除收录进Unicode的字符外，Unifont还为一些未收录进Unicode的字符制作了字形，并存放在Unicode的私用区。这些字符主要包括一些人造语言使用的字符。这些字符的码位依照CSUR/UCSUR的规则分配。

Minecraft将这些私用区字符单独整合进了一个字体中，而没有混合在默认使用的Unifont字体中。将文本组件的
```
font
```

指定为
```
minecraft:include/unifont_pua
```

即可使用该字体。

Unifont私用区字体的字体文件为散列资源文件，可以用资源路径
```
assets/minecraft/font/unifont_pua.zip
```

在
```
.minecraft/assets/objects
```

中查询。游戏使用的Unifont私用区字体版本为
```
v17.0.01
```

。

# SGA

SGA，全称标准银河字母（Standard Galactic Alphabet），是用于为附魔台添加神秘感的字母代替字体。使用这些字体的粒子会从书架上飞入附魔台，在附魔台的界面中也会使用这种字体来显示附魔选项。该字体是《指挥官基恩》系列电子游戏中使用的一种简单的字母表替代密码，在Minecraft中的SGA被重新设计成了一种点阵字体来符合游戏的风格。

SGA只支持26个英文字母，且没有字母大小写之分。

SGA的字形存储在
```
ascii_sga.png
```

中。

在Java版中，将文本组件的
```
font
```

指定为
```
minecraft:alt
```

即可使用该字体。

# Illageralt

主条目：Minecraft Dungeons:Illageralt
Illageralt是Mojang自创的一套类似于SGA的文字系统，同样也是简单的字母表替代密码，但与SGA所使用的符号不同。该字体首次出现于Minecraft Dungeons，与灾厄村民有关，在Minecraft Dungeons的用户界面的多处均可见到。

Illageralt支持26个英文字母、阿拉伯数字以及标点符号
```
!
```

、​
```
?
```

、​
```
,
```

和​
```
.
```

，且没有字母大小写的区别。

Illageralt的字形存储在
```
asciillager.png
```

中。

在Java版中，将文本组件的
```
font
```

指定为
```
minecraft:illageralt
```

即可使用该字体。

# Minecraft Ten

Minecraft Ten是Minecraft游戏主标题的字体，但需要注意的是，Minecraft Ten中的C比实际Minecraft游戏主标题中的C更窄一些，而E、F这两个字母中央的横线比实际Minecraft游戏主标题中的E、F这两个字母中央的横线更短。该字体同样也被用于基岩版、Minecraft启动器和Minecraft网站各处。它因字模高度为10个像素而得名。

Minecraft Ten支持26个英文字母、阿拉伯数字、西文标点以及部分其他拉丁字母，且没有大小写之分，任何字母输入后都会显示为大写。

# Minecraft Five

Minecraft Five因字模高度为5个像素而得名。它的粗体版本是Minecraft游戏副标题的字体。

# Noto Sans

Noto Sans是由Google和Adobe开发的无衬线字体，其CJK字体又称“思源黑体（Source Han Sans）”，在基岩版中有所使用，在游戏文件中也称为
```
smooth
```

字体。类似于Unifont，这一字体支持Unicode基本平面的所有字符，以及基本平面外的部分字符。

在基岩版中，游戏通常会在有大量文字出现时使用这一字体，以减轻玩家阅读点阵字体的视觉负担。玩家也可以在聊天屏幕的选项中将聊天字体自行切换为此字体。若将语言切换至日语，游戏会使用Noto Sans CJK JP显示大部分文本，以适应日本的字形标准。

在基岩版的Ore UI界面中，当显示的字符不被Mojangles字体支持，则改用Noto Sans提供字形。

# 历史

此段落仍需完善。
你可以帮助我们加入更多信息。

# 你知道吗

- 在基岩版中，聊天栏等各处支持显示一些特殊的彩色图标字符。这些字符位于Unicode中的私用区，其最初的设计目的是在显示游戏指南时提供方便。这些字符的源代码以冒号包裹，可以在聊天栏等各处使用；玩家也可通过手动在 ``` / tellraw ``` 或 ``` / titleraw ``` 内使用转义序列显示图标。但不同平台和版本显示的效果有所差异。

- 在Java版中，阿拉伯文等需要OpenType特性以正确显示连字的文字使用阿拉伯文字表达形式B（U+FE70~U+FEFF）来显示连字，而不是阿拉伯字母（U+0600-06FF）。
- 在中国版使用的基岩版中，绝大多数界面都使用Unifont显示。
- 在基岩版中，游戏会自动去除字符的空白部分，这导致部分字符（例如全角标点）不能正确显示。

# 参考

1. ↑ GNU Unifont Glyphs - Unifoundry
1. ↑ The Encoding of the Han Script - The Unicode Consortium, UTN #26: On The Encoding Of Latin, Greek, Cyrillic, and Han
1. ↑ Do the different CJK fonts styles of for different countries require multiple fonts? - The Unicode Consortium, FAQ: Chinese and Japanese
1. ↑ MC-261846 — “日文使用中文的字体。” — 漏洞状态为“已修复”。
1. ↑ https://www.evertype.com/standards/csur/
1. ↑ https://www.kreativekorp.com/ucsur/
1. ↑ https://www.gameinformer.com/2020/04/09/mojang-takes-its-biggest-brand-in-a-bold-new-direction-with-minecraft-dungeons
1. ↑ MC-17673 — “启动时使用转换后的材质包会导致字体扭曲” — 漏洞状态为“已修复”。
1. ↑ MC-267230 — 漏洞状态为“已修复”。
1. ↑ MC-268370 — “日本CJK字形变体的变音符全部相同。” — 漏洞状态为“已修复”。

# 导航
