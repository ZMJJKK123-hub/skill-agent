# -*- coding: utf-8 -*-
"""infrastructure 层包入口：副作用实现（SDK / 文件 / 进程 / 工具）。

本层是实现细节的家：业务层（services）只通过 interfaces 的
Protocol 引用这里的类；装配只发生在 core/bootstrap.py。
"""
