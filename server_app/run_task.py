"""会话入口：为每个用户的 MOD 生成任务启动一个独立子进程。

原理：
  服务器(server.py)收到用户的生成请求后，为这个会话单独启动一个
  Python 子进程，cwd 切到该用户的独立 mod 目录，然后调用核心的
  agent_loop() 跑完整的 12 课 agent。

  为什么用子进程而不是线程？
  - 现有 agent 的 task_manager / teammate_manager / worktree_manager
    都是模块级全局单例，WORKDIR = Path.cwd() 是进程级的。
    单机跑没问题；但网站 = 多用户并发，如果都跑在同一个进程里，
    两个用户会抢同一个 .tasks/、写进同一个目录。
  - 每会话一个子进程 = 每个进程有自己独立的 cwd 和全局单例，
    天然实现用户间隔离，核心代码一字不用改。

用法（由 server.py 调用）：
  python run_task.py <session_dir> <api_key> <task_prompt>
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 重构：把项目根加入 sys.path，使 core 包可直接导入（与 cwd 无关）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def finalize_known_issues(session_dir: Path) -> None:
    """收尾：把本次运行 run.log 中的错误信号去重后追加进 KNOWN_ISSUES.md。

    KNOWN_ISSUES.md 对 agent 是只读的（system prompt 已改为"读取并遵守"），
    新坑由本函数在 session 结束后统一收集：
      1. 读取 <session>/run.log 的全部行，筛选错误/异常信号
      2. 简单聚类（按归一化首特征词分组），避免同屏错误堆成几十条
      3. 与 KNOWN_ISSUES.md 现有文本做关键词去重，已涵盖的条目跳过
      4. 以"自动记录"条目追加到文件末尾——绝不覆盖/删除旧条目

    KNOWN_ISSUES.md 位于 <session>/mod/（server.py 的 _copy_template 已把
    模板根目录的初始文件复制进去）。
    """
    issues_path = session_dir / "mod" / "KNOWN_ISSUES.md"
    log_path = session_dir / "run.log"
    if not issues_path.exists() or not log_path.exists():
        return

    try:
        existing = issues_path.read_text(encoding="utf-8")
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return

    # 1) 提取错误信号行（含错误关键词才收集；纯日志/正常输出不记录）
    pat = re.compile(
        r"(?:ERROR|Error|Exception|BUILD FAILED|Failed|失败|超时|Timeout|"
        r"Crash|错误|PKIX|SSLHandshake|NoClassDefFound|ClassCastException)",
        re.I,
    )
    signals = []
    for raw in lines:
        if not pat.search(raw):
            continue
        # 归一化：去掉时间戳（含毫秒）/日期/内存地址/行号，压缩空白，
        # 防止同一错误因毫秒级时间戳差异被当成不同条目
        s = re.sub(r"0x[0-9a-fA-F]+", "<addr>", raw)
        s = re.sub(r"\b\d{1,2}:\d{2}:\d{2}(?:[.,]\d+)?\b", "", s)
        s = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) >= 25:  # 过滤过短噪声行
            signals.append(s)
    if not signals:
        return
    signals = signals[:40]  # 上限：本次会话最多记录 40 条信号

    # 2) 聚类：按"根因特征词"分组（同类错误合并为一条）。
    #    优先取构建工具名/异常类型，避免时间戳残留或泛关键词（Error/Exception）
    #    把整屏日志归成一条。
    def _cluster_key(s: str) -> str:
        m = re.search(
            r"\b(Gradle|Maven|PKIX|SSLHandshake|forgeGradle|compileJava|"
            r"Cannot find symbol|NoClassDefFound|ClassCastException)\b",
            s,
            re.I,
        )
        if m:
            return m.group(1).lower()
        m = re.search(r"([A-Za-z_][\w.]*Exception|[A-Za-z_][\w.]*Error)", s)
        if m:
            return m.group(1)
        m = re.match(r"[A-Za-z_][\w.]*", s)
        if m:
            return m.group(1)
        return "other"

    clusters: dict[str, list[str]] = {}
    for s in signals:
        key = _cluster_key(s)
        clusters.setdefault(key, []).append(s)
    # 过泛关键词无区分度，剔除（避免一整个 run.log 全归到"Error"一条）
    for g in ("error", "failed", "exception", "other"):
        clusters.pop(g, None)
    if not clusters:
        return

    # 3) 与现有条目去重（大小写不敏感）：特征词已出现在 KNOWN_ISSUES.md 则跳过
    today = datetime.now().strftime("%Y-%m-%d")
    existing_lower = existing.lower()
    added = []
    for key, samples in clusters.items():
        if key.lower() in existing_lower:
            continue
        sample = samples[0][:200]
        added.append(
            f"## [{today}] {key}（自动记录，来自本次 run.log）\n"
            f"- 症状: {sample}\n"
            f"- 根因: 自动记录待确认（见会话 run.log，同类信号 {len(samples)} 条）\n"
            f"- 规避: 优先参考本文件既有条目与已加载的 skills；若是本会话新问题，"
            f"需下次会话在相同场景下验证后补充确认。\n"
        )

    # 4) 追加写回（旧条目永远保留）
    if not added:
        return
    if existing.endswith("\n\n"):
        sep = ""
    elif existing.endswith("\n"):
        sep = "\n\n"
    else:
        sep = "\n\n"
    try:
        with open(issues_path, "w", encoding="utf-8") as f:
            f.write(existing + sep + "\n".join(added))
    except OSError as e:
        print(f"[finalize_known_issues] 写回失败: {e}", flush=True)
        return
    print(
        f"[finalize_known_issues] 已追加 {len(added)} 条错误记录到 "
        f"mod/KNOWN_ISSUES.md",
        flush=True,
    )


def main() -> int:
    # 强制 stdout 行缓冲 + 直写：print 每行立即落盘（run.log），
    # 否则 Windows 重定向下 print 积压到 ~8KB 才写出，
    # 前端实时轮询读不到增量 → 表现为"卡住、结束才全部蹦出来"。
    # 覆盖 run_task.py 与 core 里所有不带 flush=True 的 print。
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True, write_through=True)
        except (AttributeError, ValueError, OSError):
            pass

    # 参数：会话目录（独立 mod 工作区）、用户自己的 API Key、任务提示词
    if len(sys.argv) < 4:
        print("Usage: python run_task.py <session_dir> <api_key> <task_prompt>")
        return 1

    session_dir = Path(sys.argv[1]).resolve()
    api_key = sys.argv[2]
    task_prompt = sys.argv[3]

    # 1. 确保会话目录存在并切换进去
    #    cwd 决定了 config.WORKDIR = Path.cwd()，也就是该用户 mod 生成的位置
    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))
    print(f"[run_task] 工作目录 => {session_dir}", flush=True)

    # 2. 注入用户自己的 API Key（只在用户自己机器/会话里生效，不落盘）
    os.environ["DEEPSEEK_API_KEY"] = api_key

    # 3. 延迟导入核心 agent（此时 cwd 已切好，config.WORKDIR 才会正确）
    #    重构后从 core 包导入
    try:
        from core.agent import agent_loop
    except Exception as e:
        print(f"[run_task] 导入 agent 失败: {e}", flush=True)
        return 1

    # 4. 跑完整 agent 循环
    messages = [{"role": "user", "content": task_prompt}]
    final = agent_loop(messages)
    print(f"[run_task] 完成，最终回复:\n{final}", flush=True)

    # 5. 收尾：收集本次运行错误信号 → 去重追加 mod/KNOWN_ISSUES.md
    #    （agent 对 KNOWN_ISSUES.md 只读，新坑统一在这里落账，旧条目永不清除）
    try:
        finalize_known_issues(session_dir)
    except Exception as e:
        print(f"[run_task] finalize_known_issues 失败: {e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())