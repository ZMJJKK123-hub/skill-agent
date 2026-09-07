# -*- coding: utf-8 -*-
"""MOD 制作器后端入口（薄入口：~60 行，全部职责已分层）。

架构（三层，agent.md Rule 2）：
    api/            表现层——路由 + DTO + 校验（create_app 工厂）
    services/       业务层——会话管理/任务派发/打包/统计/知识沉淀/daemon
    infrastructure/ 基础层——磁盘存取/进程治理/daemon 文件协议

会话隔离 = 每会话一个子进程（run_task.py → core.bootstrap 新引擎）。

运行：python server.py
     （或 uvicorn server:app --host 0.0.0.0 --port 8000）
"""
import sys
from pathlib import Path

# 仓库根入 sys.path（core 包可导入）；本目录入 path（api/services 包可导入）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api import create_app  # noqa: E402 — 应用工厂（需先就位 sys.path）

app = create_app()


if __name__ == "__main__":
    import uvicorn
    try:
        # httptools：C 语言 HTTP 解析器，根治 h11 超大响应体 Content-Length bug
        uvicorn.run(app, host="0.0.0.0", port=8000, http="httptools")
    except Exception:
        # 未安装 httptools 时回退默认 h11（内存读方案已绕开大文件流式问题）
        uvicorn.run(app, host="0.0.0.0", port=8000)
