# -*- coding: utf-8 -*-
"""services 层包入口：业务编排（纯逻辑，依赖 domain + interfaces）。

例外说明（过渡期）：loop/deps.py 的适配器在 core/bootstrap.py 中
引用旧模块单例（core.tools 等），P2b 工具包迁移完成后消除。
"""
