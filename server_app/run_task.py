"""会话入口：为每个用户的生成任务启动一个独立子进程。

原理：
  服务器(server.py)收到用户的生成请求后，为这个会话单独启动一个
  Python 子进程，cwd 切到该用户的工作目录，然后调用核心的
  agent_loop() 运行 agent。

  支持两种模式（由环境变量 DSH_MODE 注入）：
    - chat（默认）：通用对话。工作目录 = 会话根目录（不复制 mod 模板/源码）。
      多轮对话：启动前从 <session_root>/.chat/conversation.jsonl 读历史，
      跑完后把最终回复追加回历史，下一轮继续。
    - mod：MOD 制作。工作目录 = 会话的 mod/ 子目录（server 已复制模板+源码）。

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


def _reset_round_state() -> None:
    """daemon 每轮开始前重置进程内存级状态，防止跨轮污染。

    agent_loop 使用模块级全局单例（task_manager / todo_manager /
    teammate_manager / bg_manager / coordinator），一轮跑完后这些状态
    会残留到下一轮（例如上一轮建的 .tasks/ 任务、队友名册、协议请求）。
    每轮开始前把它们清回初始状态——与"每任务一个全新进程"的语义对齐。
    """
    try:
        from core.tools import (
            task_manager, todo_manager, teammate_manager, bg_manager,
        )
        from core.protocol import coordinator
        task_manager.clear()
        todo_manager.todos = []
        teammate_manager.team.clear()
        teammate_manager.threads.clear()
        teammate_manager._save_team_config()
        teammate_manager.bus.clear_all()
        coordinator.reset()
        # 后台任务残留：清空注册表与通知队列（线程本身 daemon=True 不阻塞退出）
        try:
            bg_manager.tasks.clear()
            q = bg_manager.notification_queue
            while not q.empty():
                try:
                    q.get_nowait()
                except Exception:
                    break
        except Exception:
            pass
    except Exception as e:
        print(f"[run_task] 重置内存状态失败（继续）: {e}", flush=True)


def _run_one_round(messages: list, session_dir: Path,
                   session_root_path: Path, mode: str) -> str:
    """跑一轮 agent_loop 并完成收尾：清断点、写回复历史、收集错误信号。"""
    from core.agent import agent_loop
    final = agent_loop(messages)
    print(f"[run_task] 完成，最终回复:\n{final}", flush=True)

    # 正常完成：清掉断点文件（一轮真正结束，不再需要断点恢复）
    try:
        from core.conversation import clear_working
        clear_working(session_root_path)
    except Exception as e:
        print(f"[run_task] 清断点失败: {e}", flush=True)

    # 把最终回复追加进对话历史（chat 和 mod 模式都写，供历史会话展示）
    if mode in ("chat", "mod"):
        try:
            from core.conversation import append_assistant as _append_assistant
            _append_assistant(session_root_path, final or "")
        except Exception as e:
            print(f"[run_task] 保存回复到历史失败: {e}", flush=True)

    # 收尾：收集本次运行错误信号 → 去重追加 mod/KNOWN_ISSUES.md
    #    （agent 对 KNOWN_ISSUES.md 只读，新坑统一在这里落账，旧条目永不清除）
    #    仅 mod 模式（chat 模式没有模板 KNOWN_ISSUES.md，函数内部会跳过）
    try:
        finalize_known_issues(session_dir)
    except Exception as e:
        print(f"[run_task] finalize_known_issues 失败: {e}", flush=True)
    return final


def daemon_loop(session_dir: Path, session_root_path: Path, mode: str) -> None:
    """chat 模式常驻循环（M-opt1：消除每轮冷启动）。

    首轮跑完后不退出进程：每 0.5s 轮询 .chat/pending.jsonl，
    有新消息就（drain 消费队列 → 重置内存状态 → 组装历史上下文 →
    agent_loop → 收尾），再回到等待。第二轮起零 import / 零技能扫描开销。

    空闲超时（env DSH_DAEMON_IDLE_TIMEOUT，默认 600s）后自动退出，
    由 server 下次请求时重新拉起（长时间不用时释放进程资源）。

    兼容性（已核对 server.py 逻辑）：
    - 运行中插话：server 在进程存活时把新消息 enqueue_pending 并同步写历史，
      daemon 每 0.5s 消费 → 与"排队等当前轮跑完"语义一致；
    - pause：server kill 进程，断点 working.jsonl 保留，resume 新进程照常恢复；
    - 会话删除/reset：server kill 进程 + 清历史，daemon 随之消亡；
    - 多会话并发：每会话一个 daemon 进程，与现状一致。
    - server 重启：_restore_sessions 读 .chat/daemon.pid kill 遗留 daemon，
      防止新旧进程同时消费同一队列。
    """
    import time as _time
    from core.conversation import (
        pending_count, drain_pending, load_recent_history,
    )

    idle_timeout = float(os.environ.get("DSH_DAEMON_IDLE_TIMEOUT", "600"))
    last_activity = _time.time()

    # 状态文件（.chat/daemon.state：waiting | working）：
    # server 据此把"daemon 空闲"识别为 finished（进程存活但上一轮已完成，
    # 前端应显示"完成"而不是一直转圈）。用状态文件而非 run.log 打印——
    # 避免污染日志尾部，导致前端按"最终回复:"提取回复时带上标记行。
    daemon_state_file = session_root_path / ".chat" / "daemon.state"
    # pid 文件：server 重启时可据此 kill 遗留 daemon（防双进程抢队列）。
    daemon_pid_file = session_root_path / ".chat" / "daemon.pid"
    try:
        daemon_state_file.parent.mkdir(parents=True, exist_ok=True)
        daemon_pid_file.write_text(str(os.getpid()), encoding="utf-8")
    except OSError as e:
        print(f"[run_task] 写 daemon 状态文件失败: {e}", flush=True)

    def _set_state(state: str) -> None:
        try:
            daemon_state_file.write_text(state, encoding="utf-8")
        except OSError as e:
            print(f"[run_task] 写 daemon 状态失败: {e}", flush=True)

    _set_state("waiting")

    try:
        while True:
            _time.sleep(0.5)
            try:
                n = pending_count(session_root_path)
            except Exception:
                n = 0

            if n <= 0:
                if _time.time() - last_activity > idle_timeout:
                    print("[run_task] daemon idle exit", flush=True)
                    return
                continue

            # 有排队消息：消费队列（enqueue_pending 已同步写入历史，
            # 这里只需清空队列文件，历史里已有该消息，避免 load 时重复）
            last_activity = _time.time()
            _set_state("working")  # server 据此转 running
            try:
                drain_pending(session_root_path)
            except Exception as e:
                print(f"[run_task] drain_pending 失败: {e}", flush=True)
                continue

            # 重置内存级状态（对齐"每任务全新进程"语义）
            _reset_round_state()

            # 组装上下文：历史已包含新消息（enqueue_pending 同步写历史）
            try:
                messages = load_recent_history(session_root_path)
            except Exception as e:
                print(f"[run_task] 加载对话历史失败（跳过本轮）: {e}", flush=True)
                continue
            if not messages:
                print("[run_task] daemon 轮无历史消息，跳过", flush=True)
                continue

            try:
                _run_one_round(messages, session_dir, session_root_path, mode)
            except Exception as e:
                import traceback
                print(f"[run_task] daemon 轮异常（继续等待）: {e}", flush=True)
                traceback.print_exc()
                continue

            # 本轮结束，回到空闲等待（server 据此再次显示"完成"）
            _set_state("waiting")
    finally:
        try:
            daemon_pid_file.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            daemon_state_file.unlink(missing_ok=True)
        except OSError:
            pass


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

    # 参数：会话目录（工作区）、用户自己的 API Key
    # 任务提示词：优先从 DSH_PROMPT_FILE（UTF-8 临时文件，server 写入）读取——
    # 避免 Windows 子进程 argv 的 GBK 编码损坏中文；无该环境变量时回退 argv[3]。
    if len(sys.argv) < 3:
        print("Usage: python run_task.py <session_dir> <api_key> [task_prompt]")
        return 1

    session_dir = Path(sys.argv[1]).resolve()
    api_key = sys.argv[2]
    prompt_file = os.environ.get("DSH_PROMPT_FILE", "")
    if prompt_file:
        try:
            task_prompt = Path(prompt_file).read_text(encoding="utf-8")
            # 读完后删除临时文件（server 不再管它）
            try:
                Path(prompt_file).unlink()
            except OSError:
                pass
        except OSError as e:
            print(f"[run_task] 读取提示词文件失败: {e}", flush=True)
            return 1
    else:
        task_prompt = sys.argv[3] if len(sys.argv) >= 4 else ""

    # 模式：chat（默认，通用对话）| mod（MOD 制作，由 server 注入 DSH_MODE）
    mode = os.environ.get("DSH_MODE", "chat")
    # 会话根目录（.chat/ 对话历史所在处）：由 server 注入；未注入时取 session_dir 的父目录
    session_root = os.environ.get("DSH_SESSION_ROOT", str(session_dir.parent))
    session_root_path = Path(session_root).resolve()

    # 1. 确保会话目录存在并切换进去
    #    cwd 决定了 config.WORKDIR = Path.cwd()，也就是 agent 操作的位置
    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))
    print(f"[run_task] 模式={mode} | 工作目录 => {session_dir}", flush=True)

    # 2. 注入用户自己的 API Key（只在用户自己机器/会话里生效，不落盘）
    os.environ["DEEPSEEK_API_KEY"] = api_key

    # 2.5 立即把用户消息写入对话历史（必须在 import agent 之前！）
    #     agent import 要 7-8 秒（openai SDK），若等 import 完再写，
    #     用户发消息后立刻点开历史会话会读到空记录（实测 bug）。
    #     conversation 模块很轻，不触发 openai，可安全提前导入。
    #     chat 和 mod 模式都写：历史会话打开时能显示用户 prompt 气泡。
    if mode in ("chat", "mod"):
        try:
            from core.conversation import append_user as _early_append_user
            _early_append_user(session_root_path, task_prompt or "")
        except Exception as e:
            print(f"[run_task] 提前写入历史失败: {e}", flush=True)

    # 3. 延迟导入核心 agent（此时 cwd 已切好，config.WORKDIR 才会正确）
    #    重构后从 core 包导入
    try:
        from core.agent import agent_loop
    except Exception as e:
        print(f"[run_task] 导入 agent 失败: {e}", flush=True)
        return 1

    # 4. 组装 messages
    #    - 恢复模式（DSH_RESUME=1）：从 .chat/working.jsonl 原样加载断点（暂停/继续）
    #    - chat 模式：加载历史对话 + 当前 prompt
    #    - mod 模式：直接当前 prompt
    #    - 若运行中排队的消息尚未被 agent 消费（例如恢复时队列里有消息），
    #      会由 agent_loop 每轮开头的 _drain_interjections 自动注入
    messages = []
    resume = os.environ.get("DSH_RESUME", "") == "1"
    if resume:
        try:
            from core.conversation import load_working
            loaded = load_working(session_root_path)
            if loaded:
                messages = loaded
                print(f"[run_task] 恢复模式 | 已从断点加载 {len(messages)} 条消息", flush=True)
            else:
                print(f"[run_task] 恢复模式但无断点，回退到普通启动", flush=True)
        except Exception as e:
            print(f"[run_task] 断点加载失败（回退普通启动）: {e}", flush=True)
    if not messages:
        if mode == "chat":
            try:
                from core.conversation import load_recent_history
                messages = load_recent_history(session_root_path)
            except Exception as e:
                print(f"[run_task] 加载对话历史失败（继续，仅当前 prompt）: {e}", flush=True)
                messages = []
            # 把当前 prompt 作为本轮 user 消息（历史已在步骤 2.5 提前写入，
            # 这里只组装进模型上下文，不重复 append）
            messages.append({"role": "user", "content": task_prompt})
        else:
            messages = [{"role": "user", "content": task_prompt}]

    # 5. 跑完整 agent 循环（首轮）
    _run_one_round(messages, session_dir, session_root_path, mode)

    # 6. chat 模式常驻：首轮与 resume 恢复后都进入 daemon 循环，
    #    第二轮起零冷启动（openai SDK / 技能扫描只在首轮支付一次）。
    #    mod 模式维持"每任务一进程"（7s 占比小，且 mod 状态污染风险高）。
    if mode == "chat":
        daemon_loop(session_dir, session_root_path, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())