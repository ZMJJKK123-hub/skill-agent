# Tool: describe_block_textures

## 用途
根据方块描述生成每个面需要的纹理Prompt，供图片生成AI使用。

## 输入
```json
{
  "block_name": "void_crystal",
  "visual_description": "深紫色水晶方块，带青色发光脉络",
  "face_count": "6",
  "style": "vanilla_16x16"
}
```

## 输出
```json
{
  "element": "block",
  "name": "void_crystal",
  "model_parent": "minecraft:block/cube_bottom_top",
  "textures": {
    "top": {
      "path": "assets/modid/textures/block/void_crystal_top.png",
      "size": "16x16",
      "prompt": "Top face of dark purple crystal block with glowing cyan veins, Minecraft vanilla 16x16 pixel art, top-down, seamless tiling",
      "prompt_zh": "深紫色水晶方块顶部，带发光青色脉络，Minecraft原版16x16像素风格，俯视图，无缝平铺"
    },
    "bottom": {
      "path": "assets/modid/textures/block/void_crystal_bottom.png",
      "size": "16x16",
      "prompt": "Bottom face of dark purple crystal block, rough stone texture, Minecraft vanilla 16x16 pixel art, seamless tiling",
      "prompt_zh": "深紫色水晶方块底部，粗糙石质纹理"
    },
    "side": {
      "path": "assets/modid/textures/block/void_crystal_side.png",
      "size": "16x16",
      "prompt": "Side face of dark purple crystal block with layered crystalline structure, vertical cyan glow streaks, Minecraft vanilla 16x16 pixel art, seamless tiling",
      "prompt_zh": "深紫色水晶方块侧面，层叠晶体结构，垂直青色光芒条纹"
    }
  }
}
```
