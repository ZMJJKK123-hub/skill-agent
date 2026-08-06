# 方块状态JSON规范 (BlockState Spec)

> **通用**: Minecraft原生资源包规范，适用于所有加载器。  
> **路径**: `assets/<modid>/blockstates/<block_name>.json`

---

## 基础格式

```json
{
  "variants": {
    "<property>=<value>": {
      "model": "<modid>:block/<model_name>",
      "x": 0,
      "y": 0,
      "uvlock": false
    }
  }
}
```

---

## 常见BlockState属性

### facing（朝向，6方向）
值: `north`, `south`, `east`, `west`, `up`, `down`

```json
{
  "variants": {
    "facing=north": { "model": "mymod:block/my_machine" },
    "facing=east":  { "model": "mymod:block/my_machine", "y": 90 },
    "facing=south": { "model": "mymod:block/my_machine", "y": 180 },
    "facing=west":  { "model": "mymod:block/my_machine", "y": 270 },
    "facing=up":    { "model": "mymod:block/my_machine", "x": 270 },
    "facing=down":  { "model": "mymod:block/my_machine", "x": 90 }
  }
}
```

### horizontal_facing（水平朝向，4方向）
值: `north`, `south`, `east`, `west`

```json
{
  "variants": {
    "facing=north": { "model": "mymod:block/my_furnace" },
    "facing=east":  { "model": "mymod:block/my_furnace", "y": 90 },
    "facing=south": { "model": "mymod:block/my_furnace", "y": 180 },
    "facing=west":  { "model": "mymod:block/my_furnace", "y": 270 }
  }
}
```

### type（半砖）
值: `bottom`, `top`, `double`

```json
{
  "variants": {
    "type=bottom": { "model": "mymod:block/my_slab" },
    "type=top":    { "model": "mymod:block/my_slab_top" },
    "type=double": { "model": "mymod:block/my_block" }
  }
}
```

### 楼梯 (facing + half + shape)
需要 facing(4) x half(2) x shape(5) = 40种变体。核心四种shape:
- `straight` → `my_stairs`
- `outer_right` / `outer_left` → `my_stairs_outer`
- `inner_right` / `inner_left` → `my_stairs_inner`

### powered（红石开关）
```json
{
  "variants": {
    "powered=false": { "model": "mymod:block/my_block" },
    "powered=true":  { "model": "mymod:block/my_block_on" }
  }
}
```

### lit（红石灯类）
```json
{
  "variants": {
    "lit=false": { "model": "mymod:block/my_lamp" },
    "lit=true":  { "model": "mymod:block/my_lamp_on" }
  }
}
```

### 无属性方块
```json
{ "variants": { "": { "model": "mymod:block/my_block" } } }
```

---

## 多重属性 (multipart)

用于栅栏、墙等需要组合多个模型的方块：

```json
{
  "multipart": [
    { "when": { "up": "true" },   "apply": { "model": "mymod:block/my_fence_post" } },
    { "when": { "north": "true" }, "apply": { "model": "mymod:block/my_fence_side", "uvlock": true } },
    { "when": { "east": "true" },  "apply": { "model": "mymod:block/my_fence_side", "y": 90, "uvlock": true } },
    { "when": { "south": "true" }, "apply": { "model": "mymod:block/my_fence_side", "y": 180, "uvlock": true } },
    { "when": { "west": "true" },  "apply": { "model": "mymod:block/my_fence_side", "y": 270, "uvlock": true } }
  ]
}
```

---

## Agent 生成规则

| 用户描述 | BlockState 策略 |
|---------|----------------|
| "普通方块" | `variants: { "": {...} }` |
| "有朝向的机器" | `facing` 6方向 |
| "熔炉一样的" | `facing` 4方向(水平) |
| "楼梯" | `facing x half x shape` 完整组合 |
| "半砖" | `type=bottom/top/double` |
| "栅栏/墙" | `multipart` |
| "门" | `facing x half x hinge x open` |
| "活板门" | `facing x half x open` |
| "按钮/拉杆" | `powered` + `facing` |
| "红石灯" | `lit=true/false` |
