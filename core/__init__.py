"""core —— 12 课 Agent 核心引擎包。

纯 Agent 逻辑，不依赖网站服务端。业务代码全部在此目录：
  agent.py      主循环（循环不变，Harness 叠加）
  tools.py      工具实现与注册
  protocol.py   团队协议（关机握手 / 计划审批）
  worktree.py   Worktree 执行面隔离
  subagent.py   子 Agent（隔离上下文）
  compact.py    三层上下文压缩
  config.py     配置与路径沙箱
  skills/       技能库（由 tools 扫描注入）
"""