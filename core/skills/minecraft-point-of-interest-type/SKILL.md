---

name: minecraft-point-of-interest-type
description: "Minecraft Points of Interest (POI) 兴趣点机制：POI Types 兴趣点类型（硬编码 仅mod可修改、匹配方块状态、最大认领数量、认领范围、可携带标签 大多数查找使用POI类型标签）、Mechanics 机制（放置/破坏匹配方块创建/移除POI、检索高效 存储在子区块16×16×16 稀有方块携带类型）、Claiming 认领（创建时设置为类型最大可认领数量、认领/释放调整、0时不能被认领、不记录认领者、村民繁殖认领home POI 认领工作站点）、Usages 用途（Villages 村庄：已认领的village标签POI 3×3×3子区块范围 猫需>4个home POI 48方块内 商贩在meeting POI 48方块内生成 劫掠从village标签POI 64方块内计算中心；Nether portals 下界传送门：创建nether_portal POI 传送检查最近128方块内复用；Bees 蜜蜂：回家到bee_home标签POI；Lightning rods 避雷针：创建lightning_rod POI 闪电生成在最近128方块内；Lodestones 磁石：创建lodestone POI 磁石罗盘每刻检查绑定位置POI）、Storage 存储（POI文件 区域文件 维度根目录/poi）。"
whenToUse: "Use when understanding POI mechanics for villages, job sites, or bee behavior."

---

# Points of Interest (POI)

This content applies only to Java Edition.

Points of interest (POIs) are the game's mechanism for quickly finding specific block categories and counting claimed blocks. POI types are hardcoded (modifiable only via mods).

Each POI type has: matched block states (which blocks create/remove the POI), a max claim count, and a claim range. POI types can carry tags; most lookups actually use POI type tags.

## Mechanics

Placing/breaking a matching block creates/removes the POI. Retrieval is efficient because POIs are stored per sub-chunk (16×16×16) and only rare blocks carry types.

Claiming: a POI's claimable count is set to the type's max at creation; claiming/unclaiming adjusts it; at 0 it cannot be claimed. POIs do not record their claimer. Villagers claim `home` POIs when breeding (for babies) and claim job sites.

## Usages

- **Villages**: a position is in a village iff a claimed POI with the `village` tag exists within a 3×3×3 sub-chunk range. Cats need >4 claimed `home` POIs within 48 blocks; wandering traders spawn near `meeting` POIs within 48 blocks; raids compute their center from claimed `village`-tagged POIs within 64 blocks.
- **Nether portals**: create `nether_portal` POIs; teleporting checks for the nearest one within Chebyshev distance 128 and reuses it.
- **Bees**: home to `bee_home`-tagged POIs.
- **Lightning rods**: create `lightning_rod` POIs; lightning bolts spawn at the nearest within 128 blocks.
- **Lodestones**: create `lodestone` POIs; lodestone compasses check the bound position's POI each tick.

## Storage

POI files are region files under `<dimension root>/poi`.
