# 方块模型JSON规范 (Block Model Spec)

> **通用**: Minecraft原生资源包规范，适用于 Forge/NeoForge/Fabric。  
> **路径**: `assets/<modid>/models/block/*.json`

---

## 所有方块模型 Parent 类型

### 完整方块

| Parent | 纹理数 | 典型用法 |
|--------|-------|---------|
| `minecraft:block/cube_all` | 1 (`all`) | 矿石、石材、玻璃 |
| `minecraft:block/cube_bottom_top` | 3 (`top`, `bottom`, `side`) | 草方块、工作台 |
| `minecraft:block/cube` | 6 (`north/south/east/west/up/down`) | 熔炉、发射器 |
| `minecraft:block/cube_column` | 2 (`end`, `side`) | 原木 |

### 非完整方块

| Parent | 用途 |
|--------|------|
| `minecraft:block/stairs` | 楼梯 |
| `minecraft:block/slab` | 半砖 |
| `minecraft:block/slab_top` | 上半砖 |
| `minecraft:block/fence_post` | 栅栏柱 |
| `minecraft:block/fence_side` | 栅栏侧面 |
| `minecraft:block/fence_inventory` | 栅栏物品形态 |
| `minecraft:block/wall_post` | 墙柱 |
| `minecraft:block/wall_side` | 墙侧面 |
| `minecraft:block/wall_inventory` | 墙物品形态 |
| `minecraft:block/door_bottom_left` | 门下左 |
| `minecraft:block/door_top_right` | 门上右 |
| `minecraft:block/trapdoor_bottom` | 活板门下 |
| `minecraft:block/trapdoor_top` | 活板门上 |
| `minecraft:block/cross` | 十字模型（花、草） |
| `minecraft:block/crop` | 农作物 |
| `minecraft:block/orientable` | 朝向型（3纹理: top/front/side） |

---

## 完整代码示例

### cube_all（六个面一样）
```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "mymod:block/my_block"
  }
}
```

### cube_bottom_top（顶底侧面不同）
```json
{
  "parent": "minecraft:block/cube_bottom_top",
  "textures": {
    "top": "mymod:block/my_block_top",
    "bottom": "mymod:block/my_block_bottom",
    "side": "mymod:block/my_block_side"
  }
}
```

### cube（六个面全部不同）
```json
{
  "parent": "minecraft:block/cube",
  "textures": {
    "north": "mymod:block/my_block_front",
    "south": "mymod:block/my_block_back",
    "east": "mymod:block/my_block_side",
    "west": "mymod:block/my_block_side",
    "up": "mymod:block/my_block_top",
    "down": "mymod:block/my_block_bottom",
    "particle": "mymod:block/my_block_front"
  }
}
```

### stairs
```json
{
  "parent": "minecraft:block/stairs",
  "textures": {
    "bottom": "mymod:block/my_block",
    "top": "mymod:block/my_block",
    "side": "mymod:block/my_block"
  }
}
```

### slab
```json
{
  "parent": "minecraft:block/slab",
  "textures": {
    "bottom": "mymod:block/my_block",
    "top": "mymod:block/my_block",
    "side": "mymod:block/my_block"
  }
}
```

### fence（栅栏）
```json
// fence_post.json
{ "parent": "minecraft:block/fence_post", "textures": { "texture": "mymod:block/my_block" } }
// fence_side.json
{ "parent": "minecraft:block/fence_side", "textures": { "texture": "mymod:block/my_block" } }
// fence_inventory.json
{ "parent": "minecraft:block/fence_inventory", "textures": { "texture": "mymod:block/my_block" } }
```

### orientable（朝向型机器）
```json
{
  "parent": "minecraft:block/orientable",
  "textures": {
    "top": "mymod:block/my_machine_top",
    "front": "mymod:block/my_machine_front",
    "side": "mymod:block/my_machine_side"
  }
}
```

### cross（植物/花）
```json
{
  "parent": "minecraft:block/cross",
  "textures": { "cross": "mymod:block/my_flower" }
}
```

---

## 方块物品形态模型 (items/)
```json
{ "parent": "mymod:block/my_block" }
```

---

## 纹理命名约定

| 面 | 推荐命名 | 尺寸 |
|----|---------|------|
| 所有面 | `{name}.png` | 16x16 |
| 顶面 | `{name}_top.png` | 16x16 |
| 底面 | `{name}_bottom.png` | 16x16 |
| 侧面 | `{name}_side.png` | 16x16 |
| 正面 | `{name}_front.png` | 16x16 |
| 背面 | `{name}_back.png` | 16x16 |
| 粒子 | `{name}_particle.png` | 16x16 |
| 叠加层 | `{name}_overlay.png` | 16x16 (半透明) |

---

## Agent 生成规则

| 用户描述 | 模型策略 |
|---------|---------|
| "六个面都一样" | `cube_all`，1个纹理文件 |
| "顶部和侧面不同" | `cube_bottom_top`，3个纹理文件 |
| "正面不同（像熔炉）" | `cube` 或 `orientable`，3-6个纹理 |
| "楼梯" | `stairs` parent + 对应blockstate |
| "半砖" | `slab` parent + `type=bottom/top/double` blockstate |
| "栅栏" | fence_post + fence_side + fence_inventory |
| "门" | door_bottom/top × left/right |
| "植物" | `cross` parent |
| 方块物品模型 | `{"parent": "mymod:block/<block_name>"}` |
