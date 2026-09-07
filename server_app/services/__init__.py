# -*- coding: utf-8 -*-
"""server_app/services 层包入口：会话业务编排。

组成：
    round_runner —— 单轮生命周期（跑引擎/清断点/落历史/沉淀收尾）。
    daemon_runner —— 常驻循环 + daemon 状态文件契约。
    finalizers —— KNOWN_ISSUES / ERROR_LIST 知识沉淀。
"""
