---
name: minecraft-tag-game-event
description: |
  Java版标签/游戏事件（Minecraft Wiki 中文版全量正文）。
  
  【概述】游戏事件标签（Game Event Tags）是游戏事件的组合。
  
  【涵盖内容】
  - allay_can_listen
  - ignore_vibrations_sneaking
  - shrieker_can_listen
  - vibrations
  - warden_can_listen
  - dampenable_vibrations
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/游戏事件 的完整规范时
---

本条目所述内容仅适用于Java版。
游戏事件标签（Game Event Tags）是游戏事件的组合。

# 使用

游戏事件标签不可被主动调用，它们被游戏用来控制振动系统中的各项检测条件。

# 标签列表

## allay_can_listen

- 悦灵可以检测的游戏事件。
- 添加其他游戏事件不影响悦灵的AI活动，默认游戏事件被移除后悦灵将不能被音符盒吸引。

- #allay_can_listen（1项） - ``` note_block_play ```

## ignore_vibrations_sneaking

- 潜行的实体产生这些游戏事件时，不会被振动监听器检测。

- #ignore_vibrations_sneaking（6项） - ``` hit_ground ``` - ``` projectile_shoot ``` - ``` step ``` - ``` swim ``` - ``` item_interact_start ``` - ``` item_interact_finish ```

## shrieker_can_listen

- 幽匿尖啸体可以检测的游戏事件。

- #shrieker_can_listen（1项） - ``` sculk_sensor_tendrils_clicking ```

## vibrations

- 幽匿感测体和校频幽匿感测体可以检测的游戏事件。
- 游戏事件只能移除，游戏不会检测非默认的游戏事件。

- #vibrations（56项） - ``` block_attach ``` - ``` block_change ``` - ``` block_close ``` - ``` block_destroy ``` - ``` block_detach ``` - ``` block_open ``` - ``` block_place ``` - ``` block_activate ``` - ``` block_deactivate ``` - ``` bounce ``` - ``` container_close ``` - ``` container_open ``` - ``` drink ``` - ``` eat ``` - ``` elytra_glide ``` - ``` entity_damage ``` - ``` entity_die ``` - ``` entity_dismount ``` - ``` entity_interact ``` - ``` entity_mount ``` - ``` entity_place ``` - ``` entity_action ``` - ``` equip ``` - ``` explode ``` - ``` fluid_pickup ``` - ``` fluid_place ``` - ``` hit_ground ``` - ``` instrument_play ``` - ``` item_interact_finish ``` - ``` lightning_strike ``` - ``` note_block_play ``` - ``` prime_fuse ``` - ``` projectile_land ``` - ``` projectile_shoot ``` - ``` shear ``` - ``` splash ``` - ``` step ``` - ``` swim ``` - ``` teleport ``` - ``` unequip ``` - ``` resonate_1 ``` - ``` resonate_2 ``` - ``` resonate_3 ``` - ``` resonate_4 ``` - ``` resonate_5 ``` - ``` resonate_6 ``` - ``` resonate_7 ``` - ``` resonate_8 ``` - ``` resonate_9 ``` - ``` resonate_10 ``` - ``` resonate_11 ``` - ``` resonate_12 ``` - ``` resonate_13 ``` - ``` resonate_14 ``` - ``` resonate_15 ``` - ``` flap ```

## warden_can_listen

- 监守者可以检测的游戏事件。

- #warden_can_listen（57项） - ``` block_attach ``` - ``` block_change ``` - ``` block_close ``` - ``` block_destroy ``` - ``` block_detach ``` - ``` block_open ``` - ``` block_place ``` - ``` block_activate ``` - ``` block_deactivate ``` - ``` bounce ``` - ``` container_close ``` - ``` container_open ``` - ``` drink ``` - ``` eat ``` - ``` elytra_glide ``` - ``` entity_damage ``` - ``` entity_die ``` - ``` entity_dismount ``` - ``` entity_interact ``` - ``` entity_mount ``` - ``` entity_place ``` - ``` entity_action ``` - ``` equip ``` - ``` explode ``` - ``` fluid_pickup ``` - ``` fluid_place ``` - ``` hit_ground ``` - ``` instrument_play ``` - ``` item_interact_finish ``` - ``` lightning_strike ``` - ``` note_block_play ``` - ``` prime_fuse ``` - ``` projectile_land ``` - ``` projectile_shoot ``` - ``` shear ``` - ``` splash ``` - ``` step ``` - ``` swim ``` - ``` teleport ``` - ``` unequip ``` - ``` resonate_1 ``` - ``` resonate_2 ``` - ``` resonate_3 ``` - ``` resonate_4 ``` - ``` resonate_5 ``` - ``` resonate_6 ``` - ``` resonate_7 ``` - ``` resonate_8 ``` - ``` resonate_9 ``` - ``` resonate_10 ``` - ``` resonate_11 ``` - ``` resonate_12 ``` - ``` resonate_13 ``` - ``` resonate_14 ``` - ``` resonate_15 ``` - ``` shriek ``` - ``` #shrieker_can_listen ```

# 已移除的标签

## dampenable_vibrations

添加于：22w13a。移除于：22w17a。

- #dampenable_vibrations（2项） - ``` hit_ground ``` - ``` step ```

# 历史

# 导航
