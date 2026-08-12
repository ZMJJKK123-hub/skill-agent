---
name: minecraft-tag-dialogue
description: |
  Java版标签/对话框（Minecraft Wiki 中文版全量正文）。
  
  【概述】对话框标签（Dialog Tags）是对话框的组合。
  
  【涵盖内容】
  - pause_screen_additions
  - quick_actions
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/对话框 的完整规范时
---

本条目所述内容仅适用于Java版。
对话框标签（Dialog Tags）是对话框的组合。

# 使用

游戏内部使用对话框标签定义了无需通过命令即可调用的对话框。除此以外，对话框标签目前仅能被
```
dialog_list
```

类型的对话框调用。

# 标签列表

## pause_screen_additions

- 持有该标签的对话框可通过暂停菜单直接进入。
- 标签中对话框数量>1时，进入 ``` custom_options ``` 对话框列表。

- #pause_screen_additions（0项） - 无内容

## quick_actions

- 持有该标签的对话框可通过快捷操作选项绑定键（默认为G）直接进入。
- 标签中对话框数量>1时，进入 ``` quick_actions ``` 对话框列表。

- #quick_actions（0项） - 无内容

# 历史

# 导航
