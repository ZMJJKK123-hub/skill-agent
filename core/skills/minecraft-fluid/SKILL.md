---

name: minecraft-fluid
description: "Minecraft Fluid 流体系统：Overview 概述（water 和 lava 两种液体、source blocks 源方块、confined sources 限制源 不流动 静态渲染、flowing blocks 流动方块 深度随距离变浅、液体相互作用 推动实体/物品）、Mechanics 机制（Depth 深度：源方块0 水平流动每方块+1 最大7 垂直流动0 岩浆最大深度主世界/末地3 地狱7；Spreading 扩散：源放置后加入扩散队列 形成溪流 4方向深度限制 扩散规则：空气替换/含水方块停止/流体影响方块尝试掉落物品/固体方块扩散4面/液体混合/同液体源停止/4邻居固体停止；Flow Direction 流动方向：5方块/水平流动距离内检查空气/纯液体/可冲刷方块 形成溪流；水源转换 water_source_conversion 游戏规则 相邻≥2水源方块 含水块）、Droplets 水滴（粒子 液体下方方块形成滴落粒子 岩浆水滴不伤害/点燃 新放置液体需数秒渗透）、Block Updates 方块更新（NC更新 PP更新 结构生成从不更新液体）、Liquid Interactions 液体交互（touch 相邻和 flow-in 同方块 流入需先接触；岩浆源水平/上方遇水→黑曜石、岩浆源/流动下方遇水→无反应、岩浆流动水平/上方遇水→圆石、岩浆向下流入水→石头、岩浆接触灵魂土+蓝冰→玄武岩；所有反应发生在岩浆侧）。"
whenToUse: "Use when working with water/lava mechanics (spreading, source conversion, fluid interactions)."

---

# Fluid

Liquids (fluids) are special blocks that flow freely, forming rivers, waterfalls, and lakes.

## Overview

Two liquids: water and lava. All liquid blocks originate from **source blocks** (full blocks). Confined sources (surrounded by solid or liquid blocks) don't flow and render still; once at least part is unconfined, they flow per basic fluid dynamics, rendering flowing with animated directional lines; flowing blocks get shallower with distance.

Liquids interact with each other and with blocks; they push most entities/items (drown or float). Most mobs (including players) can swim/float; undead generally can't swim well. Sources can be picked up with buckets (Java: liquids have no item form). Liquid blocks are replaceable — placing a block replaces them. Java: snow doesn't accumulate under liquids; water under water doesn't freeze.

## Mechanics

### Depth

Depth describes how "empty" a block is: sources are always depth 0; horizontal flow increases depth by 1 per block from the source; max depth 7 (no more horizontal spreading beyond). Vertically falling liquid is depth 0. Lava's max depth is 3 in the Overworld/End, but 7 in the Nether.

### Spreading

When a source is placed (in air or waterlogging), it's added to a spreading queue. It first tries to form streams on each open face — a flat surface spreads in four directions up to the depth limit (a floating source still spreads 1 block horizontally even with air below). Then, for the block below the source and each flowing block in the queue:

1. Air → replaced by liquid.
2. Waterlogged non-solid block → stop (each waterlogged block has its own queue).
3. Fluid-affected non-solid blocks, bamboo shoots, cobwebs → try to drop as items and get replaced; the upper block is removed from the queue.
4. Solid blocks (or a few unaffected non-solids) → spread to the four open faces; new flows join the queue.
5. Another liquid → liquid mixing; new flows join the queue.
6. Same-liquid source → stop.
7. All four neighbors solid → stop (why 1-block-wide columns don't spread at the ground).

At max depth no horizontal spreading happens. Flow speed: water 1 block per 5 ticks (0.25 s; can't be placed in the Nether but still flows); lava 1 block per 60 ticks (3 s) in the Overworld/End, 1 per 10 ticks (0.5 s) in the Nether.

### Flow Direction

The liquid checks terrain within 5 blocks/horizontal flow distance for air, pure liquid, or flushable blocks below (Java: also waterlogged blocks with exposed liquid tops) and tries to form streams toward the nearest found spot (1-block-wide streams near edges; those blocks are removed from the spreading queue).

Java **water source conversion**: with the `water_source_conversion` game rule true, a non-waterlogged waterloggable block horizontally adjacent to ≥2 water source blocks (or waterlogged blocks with unobstructed liquid faces; flowing water counts as full) with a solid/water/waterlogged block below becomes waterlogged when water flows into it.

## Droplets

With particles fully enabled, dripping particles form under blocks with liquid above (Java: blocks whose top touches liquid and whose bottom is above the neighbor below). Lava droplets don't damage or ignite. Newly placed liquid takes seconds to "percolate" before dripping.

## Block Updates (Java)

Liquid updates from NC updates (liquid flowing in / neighbor drying) and PP updates (depth changes). Structure generation never updates liquids on load — e.g. cave entrances cut into underground lakes stay static until something updates them; structure-generated liquids flow immediately.

## Liquid Interactions

Two behaviors: **touch** (adjacent blocks) and **flow-in** (occupying the same block). Flow-in requires touch first. Results (all reactions happen on the lava side):

- Lava source touching water horizontally or above → obsidian.
- Lava source/flow touching water below → no reaction.
- Lava flow touching water horizontally or above → cobblestone.
- Lava flowing down into water → stone.
- Lava touching soul soil below + blue ice horizontally/above → basalt.

Notes: down-flowing tendencies make the "no reaction" cases transient; the only permanent no-reaction case is lava above a waterlogged block (blocks the flow). Horizontal lava-water contact only touches (reacts immediately); vertically only lava flows into water (water touching lava reacts); all reactions occur on the lava side.
