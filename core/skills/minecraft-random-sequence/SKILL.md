---
name: minecraft-random-sequence
description: |
  随机序列存储格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】随机序列（Random Sequences）是游戏内提供可控随机化的随机数发生器序列。随机序列存储文件是存档内存储随机序列所使用的文件。
  
  【涵盖内容】
  - 创建
  - 生成随机数
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 随机序列存储格式 的完整规范时
---

本条目所述内容仅适用于Java版。
随机序列（Random Sequences）是游戏内提供可控随机化的随机数发生器序列。随机序列存储文件是存档内存储随机序列所使用的文件。

# 存储格式

随机序列存储文件位于
```
<
存档根目录
>/data/minecraft/random_sequences.dat
```

。

随机序列存储文件使用GZip压缩的NBT文件格式保存，其内部有下列NBT结构：

- [图:NBT复合标签/JSON对象] 根标签 - [图:NBT复合标签/JSON对象]* *data：随机序列数据。 - [图:布尔型]*include_sequence_id：计算随机序列时是否代入随机序列的命名空间ID计算。此项可由 ``` / random reset * ``` 修改。如果不存在则认为是 ``` true ``` 。 - [图:布尔型]*include_world_seed：计算随机序列时是否代入世界种子计算，如果不代入世界种子则任何存档内此随机序列行为一致。此项可由 ``` / random reset * ``` 修改。如果不存在则认为是 ``` true ``` 。 - [图:整型]*salt：初始化随机序列时掺入的盐。如果不存在则认为是0。 - [图:NBT复合标签/JSON对象]* *sequences：当前存档内已创建的随机序列。 - [图:NBT复合标签/JSON对象]<命名空间ID>：一个随机序列。 - [图:长整型数组]* *source：随机数源数据。 - [图:长整型]：随机数种子的低64位。 - [图:长整型]：随机数种子的高64位。 - [图:整型]*DataVersion：保存此强制加载区块存储文件的游戏的数据版本。如果此项不存在则游戏认为此项是1343（Java版1.12.2）。

# 随机序列

## 创建

创建随机序列需要有3个参数：随机序列的命名空间IDidentifier、世界种子worldSeed和盐salt。根据[图:布尔型]include_sequence_id和[图:布尔型]include_world_seed，游戏会决定是否将命名空间ID和世界种子加入计算中以提高随机序列的随机化程度。

游戏使用的随机数发生器是Xoroshiro128++，这个随机数发生器使用128位的种子。

游戏首先计算出来一个64位的初始种子，再将初始种子拆开成为128位的未混合的种子：

```
long
 
initialSeed
 
=
 
salt
;

if
 
(
include_world_seed
)

	
initialSeed
 
^=
 
worldSeed
;

long
 
unmixedLo64
 
=
 
initialSeed
 
^
 
0x6A09E667F3BCC909L
;

long
 
unmixedHi64
 
=
 
unmixedLo64
 
+
 
0x9E3779B97F4A7C15L
;
```

此处如果指定了[图:布尔型]include_world_seed，那么游戏会把世界种子代入计算，使得同样配置的随机序列在不同的存档中产生的随机数发生器种子不同。

接下来，如果随机序列指定了[图:布尔型]include_sequence_id为true，则计算命名空间ID的MD5值，并与未混合的种子进行异或。这使得同一个存档中，不同命名空间ID的随机序列可以具有不同的随机数发生器种子。

```
if
 
(
include_sequence_id
)
 
{

	
byte
[]
 
md5sum
 
=
 
computeMD5
(
identifier
);

    
long
 
md5Lo64
 
=
 
md5Low64bit
(
md5sum
);

    
long
 
md5Hi64
 
=
 
md5High64bit
(
md5sum
);

    
unmixedLo64
 
^=
 
md5Lo64
;

    
unmixedHi64
 
^=
 
md5Hi64
;

}
```

最后，将未混合的种子进行混合，得到Xoroshiro128++随机数发生器的种子。

```
public
 
static
 
long
 
mixStafford13
(
long
 
l
)
 
{

	
l
 
=
 
(
l
 
^
 
l
 
>>>
 
30
)
 
*
 
0xBF58476D1CE4E5B9L
;

	
l
 
=
 
(
l
 
^
 
l
 
>>>
 
27
)
 
*
 
0x94D049BB133111EBL
;

	
return
 
l
 
^
 
l
 
>>>
 
31
;

}

long
 
mixedLo64
 
=
 
mixStafford13
(
unmixedLo64
);

long
 
mixedHi64
 
=
 
mixStafford13
(
unmixedHi64
);
```

如果计算生成的种子为0，那么游戏会将低64位设置为-7046029254386353131L，高64位设置为7640891576956012809L。

## 生成随机数

当游戏需要使用随机序列生成整数时，游戏会根据Xoroshiro128++随机数发生器算法产生随机数；如果生成的是浮点数，则根据浮点数的位数生成对应的随机浮点数；如果生成的是符合高斯分布的浮点数，则需要附加使用Marsaglia极坐标高斯方法生成。

# 存储行为

当随机序列存储文件不存在或不完整时，游戏按照下列参数初始化文件：

- [图:布尔型]include_sequence_id初始化为 ``` true ``` 。
- [图:布尔型]include_world_seed初始化为 ``` true ``` 。
- [图:整型]salt初始化为0。

当游戏使用随机序列时，随机序列会被取出，计算后更新为新的种子再被放回。如果使用随机序列时命名空间ID对应的随机序列不存在，游戏会创建对应的随机序列。

游戏内绝大多数战利品表计算都使用了随机序列，包括破坏方块时的掉落物、杀死实体时的掉落物、钓鱼时可以钓上的物品和猪灵的以物易物等，但世界生成过程中产生的战利品箱不由随机序列控制，而受到世界种子的直接影响。

使用
```
/
random
 reset
```

会重置指定的随机序列，并根据给出的参数重新创建随机序列。
```
/
random
 reset *
```

会重置创建所有随机序列，并且给出的参数会被同步入随机序列存储文件内。

# 历史

# 导航
