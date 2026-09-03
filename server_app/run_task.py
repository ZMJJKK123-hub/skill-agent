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

import json
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
        # P3 修复：此 pattern 此前没有捕获组却调 group(1) → IndexError
        # "no such group" → 整个 finalize_known_issues 静默失败（d70b3f408f53
        # 实测每轮收尾都崩，KNOWN_ISSUES 自动沉淀全丢）。加组即可。
        m = re.match(r"([A-Za-z_][\w.]*)", s)
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


def finalize_error_list(session_dir: Path) -> None:
    """自动把本次运行的新错误追加到 docs/agent/ERROR_LIST.md（共享知识库）。

    优先读取 run.log 中以 `NEW_ERROR:` 开头的结构化行（agent 在总结里输出的
    `NEW_ERROR: <symptom> | <root cause> | <fix>`）。没有结构化行时，退化为
    提取常规错误信号。无论哪种，都会与现有文档去重，绝不覆盖/删除旧条目。
    """
    log_path = session_dir / "run.log"
    target = PROJECT_ROOT / "docs" / "agent" / "ERROR_LIST.md"
    if not log_path.exists():
        return
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    existing_lower = existing.lower()
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()

    new_entries = []
    seen = set()

    # 1) 结构化 NEW_ERROR: 行（可能在 `[reply] NEW_ERROR:` 或 `NEW_ERROR:` 中）
    for raw in lines:
        m = re.search(r"NEW_ERROR:\s*(.+)", raw, re.I)
        if not m:
            continue
        body = m.group(1).strip()
        if body and body.lower() not in existing_lower and body not in seen:
            seen.add(body)
            new_entries.append(f"- **Auto-recorded:** {body}")

    # 2) 兜底：常规错误信号（最多 10 条，避免刷屏）
    if not new_entries:
        pat = re.compile(
            r"(?i)(:\s*error:|exception|build failed|failed to|cannot find symbol|"
            r"not found|invalid mod|missing language|supported_formats|mandatory=true)",
        )
        cnt = 0
        for raw in lines:
            if cnt >= 10:
                break
            if not pat.search(raw):
                continue
            s = re.sub(r"\s+", " ", raw).strip()
            if len(s) < 20:
                continue
            # 只保留一个代表性症状行，避免时间戳噪音
            sample = s[:220]
            if sample.lower() in existing_lower or sample in seen:
                continue
            seen.add(sample)
            new_entries.append(f"- **Auto-recorded:** {sample}")
            cnt += 1

    if not new_entries:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    section = f"\n## {today} Auto-recorded from runtime\n\n" + "\n".join(new_entries) + "\n"
    try:
        if not existing.endswith("\n"):
            existing += "\n"
        with open(target, "a", encoding="utf-8") as f:
            f.write(section)
        print(f"[finalize_error_list] 已追加 {len(new_entries)} 条到 docs/agent/ERROR_LIST.md", flush=True)
    except OSError as e:
        print(f"[finalize_error_list] 写回失败: {e}", flush=True)


def _run_one_round(messages: list, session_dir: Path,
                   session_root_path: Path, mode: str) -> str:
    """跑一轮 agent_loop 并完成收尾：清断点、写回复历史、收集错误信号。"""
    from core.agent import agent_loop
    try:
        final = agent_loop(messages)
    except Exception as e:
        # 统一失败标记行：前端据此把会话显示为"运行异常"而不是绿色"完成"
        print(f"[run_task] 任务异常终止: {type(e).__name__}: {e}", flush=True)
        raise
    # （最终回复的 stdout 打印移到历史落盘之后，见下方——防 stdout 冻结）

    # 正常完成：清掉断点文件（一轮真正结束，不再需要断点恢复）
    try:
        from core.conversation import clear_working
        clear_working(session_root_path)
    except Exception as e:
        print(f"[run_task] 清断点失败: {e}", flush=True)

    # 把最终回复追加进对话历史（chat 和 mod 模式都写，供历史会话展示）。
    # 必须在往 stdout 打印最终回复之前——stdout 大段写入偶发冻结
    # （实测：进程卡死在打印中途 1 小时，历史没落盘、daemon 永远不进
    #  待机循环）。数据安全优先：先落盘，后打印。
    if mode in ("chat", "mod"):
        try:
            from core.conversation import append_assistant as _append_assistant
            _append_assistant(session_root_path, final or "")
        except Exception as e:
            print(f"[run_task] 保存回复到历史失败: {e}", flush=True)

    # 往 stdout 打印最终回复。这段文本可能很长，且 stdout 写入曾被观测
    # 到卡死（阻塞在 write 中途、进程假死、日志不再增长）——因此：
    #   1) 只打印前 600 字（全文已在 conversation.jsonl，前端也从那里取）
    #   2) 打印本身包 try/except OSError，失败降级为逐行短写
    header = "[run_task] 完成，最终回复:"
    preview = (final or "")[:600]
    try:
        print(f"{header}\n{preview}", flush=True)
    except OSError:
        try:
            for ln in preview.splitlines()[:10]:
                print(header, ln[:120], flush=True)
        except Exception:
            pass

    # 收尾：收集本次运行错误信号 → 去重追加 mod/KNOWN_ISSUES.md
    #    （agent 对 KNOWN_ISSUES.md 只读，新坑统一在这里落账，旧条目永不清除）
    #    仅 mod 模式（chat 模式没有模板 KNOWN_ISSUES.md，函数内部会跳过）
    try:
        finalize_known_issues(session_dir)
    except Exception as e:
        print(f"[run_task] finalize_known_issues 失败: {e}", flush=True)
    # 自动沉淀新错误到共享 docs/agent/ERROR_LIST.md（所有模式都执行）
    try:
        finalize_error_list(session_dir)
    except Exception as e:
        print(f"[run_task] finalize_error_list 失败: {e}", flush=True)
    return final


def _strip_pending_messages(messages: list, session_root) -> list:
    """把仍在排队（pending 文件里）的消息移出本轮上下文。

    enqueue_pending 会同步写历史——运行中排队的消息会出现在
    load_recent_history 的结果里，但它们属于"之后的轮次"（daemon 一轮
    只消费一条）。不滤掉的话本轮模型会看到多条待答需求，常合并处理
    只答最后一条（实测 甲/乙/丙 三连发，乙被吞、丙的轮次回复"收到
    上下文更新"）。按 (role, content) 对照，pending 空时原样返回。
    """
    try:
        from core.conversation import pending_path as _pending_path
        _pset = set()
        _pp = _pending_path(session_root)
        if _pp.exists():
            import json as _json
            for _ln in _pp.read_text(encoding="utf-8").splitlines():
                _ln = _ln.strip()
                if not _ln:
                    continue
                try:
                    _pm = _json.loads(_ln)
                    _pset.add((_pm.get("role"), _pm.get("content")))
                except ValueError:
                    continue
        if _pset:
            _before = len(messages)
            messages = [m for m in messages if (m.get("role"), m.get("content")) not in _pset]
            if len(messages) != _before:
                print(f"[run_task] 已把 {_before - len(messages)} 条排队消息移出本轮（等 daemon 逐条处理）", flush=True)
    except Exception as e:
        print(f"[run_task] 排队消息对照失败（忽略）: {e}", flush=True)
    return messages


def daemon_loop(session_dir: Path, session_root_path: Path, mode: str) -> None:
    """chat / mod 模式常驻循环（M-opt1：消除每轮冷启动）。

    首轮跑完后不退出进程：每 0.5s 轮询 .chat/pending.jsonl，
    有新消息就（drain 消费队列 → 组装历史上下文 → agent_loop → 收尾），
    再回到等待。第二轮起零 import / 零技能扫描开销。

    状态持久化（长对话语义）：daemon 常驻期间，进程内存状态
    （task_manager / todo / teammate_manager / coordinator / bg_manager）
    跨轮保留——上一轮建的任务、队友名册、协议请求在下一轮继续可用。
    不主动清空；队友线程自身有 60s IDLE 自动 shutdown，不会泄漏。
    空闲超时（env DSH_DAEMON_IDLE_TIMEOUT，默认 600s）后进程退出，
    内存状态随之消失（.tasks/ 任务文件仍落盘，下次进程自动恢复）。

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
        pending_count, drain_pending_one, load_recent_history,
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

    def _cleanup_game_processes_if_idle() -> None:
        """空闲时关掉 agent 启动的游戏客户端/服务器。

        此前没有任何收尾清理——完成闸提示词又只说"停止调用工具"，模型
        从不主动关客户端，任务跑完后游戏窗口永远留在用户桌面（26ad6024224f
        实测：客户端 + Gradle 守护共 4 个 java 进程幸存）。
        有排队消息时保留进程（下一轮立即继续验证，避免反复重启客户端）。
        """
        try:
            from core.process_manager import stop_all as _stop_all
            if pending_count(session_root_path) == 0:
                _stopped = _stop_all(str(session_dir), force=True)
                if _stopped and _stopped != "No running game processes.":
                    print(f"[run_task] 空闲收尾，已关闭游戏进程: {_stopped}", flush=True)
        except Exception as e:
            print(f"[run_task] 游戏进程收尾清理失败: {e}", flush=True)

    # daemon 启动 = 首轮已跑完：立刻做一次空闲清理（首轮启动的客户端
    # 就是在这里被关掉的），此后每轮正常结束再各清一次
    _cleanup_game_processes_if_idle()
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

            # 有排队消息：每轮只消费最早的一条。出队后立刻写进对话历史
            # （enqueue 不再同步落盘）——磁盘历史保持"处理顺序"：
            # [u甲,a甲,乙,...]，模型本轮末尾是待答的 user，而不是上一轮
            # 的 assistant（否则模型没有可答的问题，只能回"收到上下文
            # 更新"，实测 7ddb68f750e0）。
            last_activity = _time.time()
            _set_state("working")  # server 据此转 running
            try:
                from core.conversation import append_user as _daemon_append_user
                _drained = drain_pending_one(session_root_path)
                for _dm in _drained:
                    _daemon_append_user(session_root_path,
                                        str(_dm.get("content", "")),
                                        _dm.get("images"))
            except Exception as e:
                print(f"[run_task] drain_pending_one 失败: {e}", flush=True)
                _set_state("waiting")
                continue

            # 组装上下文：历史已包含新消息（enqueue_pending 同步写历史）。
            # 过滤仍在排队的消息（一轮只答一条）；不重置任何状态：
            # 长对话语义下任务/队友/协议状态跨轮保留。
            try:
                messages = load_recent_history(session_root_path)
            except Exception as e:
                print(f"[run_task] 加载对话历史失败（跳过本轮）: {e}", flush=True)
                _set_state("waiting")
                continue
            messages = _strip_pending_messages(messages, session_root_path)
            if not messages:
                print("[run_task] daemon 轮无历史消息，跳过", flush=True)
                _set_state("waiting")
                continue

            try:
                _run_one_round(messages, session_dir, session_root_path, mode)
            except Exception as e:
                import traceback
                print(f"[run_task] daemon 轮异常（继续等待）: {e}", flush=True)
                traceback.print_exc()
                _set_state("waiting")
                continue

            # 本轮正常结束：空闲即关游戏进程（提示词引导之外的代码兜底）
            _cleanup_game_processes_if_idle()

            # 本轮结束，回到空闲等待（server 据此再次显示"完成"）
            _set_state("waiting")
    except KeyboardInterrupt:
        # server 被 Ctrl+C 停止时，Windows 控制台会把中断广播给
        # 同一控制台的 daemon 子进程 → 优雅退出，不打印吓人的 traceback
        print("[run_task] daemon stopped (interrupt)", flush=True)
    finally:
        # 退出兜底：daemon 结束时杀掉本进程托管的游戏进程（Ctrl+C 优雅
        # 退出路径；被 server 强杀时走 server 侧 _kill_session_game_processes）
        try:
            from core.process_manager import stop_all as _stop_all_finally
            _stop_all_finally(str(session_dir), force=True)
        except Exception:
            pass
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
    # 必须同时设 encoding="utf-8"：core/config.py 导入前 stdout 还是
    # Windows 默认 GBK，第一行 print（模式/工作目录）会以 GBK 写入
    # run.log，前端按 UTF-8 读 → 首行乱码（实测：ģʽ=chat | ����Ŀ¼）。
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True, write_through=True,
                                   encoding="utf-8", errors="replace")
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
    #    同时声明「不加载仓库 .env」：8000 网页版用户完全自备 Key/模型/地址，
    #    服务器 owner 的 .env（8001 清小搭配置，含 DEEPSEEK/TSINGHUA 密钥）
    #    不得进入用户会话进程——既避免计费串号，也避免密钥经 env 泄漏给用户。
    #    必须在任何 core 导入之前设置（首个 core 导入在本函数稍后的
    #    core.conversation / core.agent）。
    os.environ["DSH_NO_ENV_FILE"] = "1"
    os.environ["DEEPSEEK_API_KEY"] = api_key

    # 用户随消息上传的图片（.chat/uploads 文件名 JSON 数组，可为空）：
    # 写历史供前端回显 / agent 恢复；模型调用边界再展开为 image_url 片段
    prompt_images = []
    _pi = os.environ.get("DSH_PROMPT_IMAGES", "")
    if _pi:
        try:
            _parsed = json.loads(_pi)
            if isinstance(_parsed, list):
                prompt_images = [str(n) for n in _parsed if isinstance(n, str) and n]
        except ValueError:
            print("[run_task] DSH_PROMPT_IMAGES 解析失败，忽略图片附件", flush=True)

    # 2.5 立即把用户消息写入对话历史（必须在 import agent 之前！）
    #     agent import 要 7-8 秒（openai SDK），若等 import 完再写，
    #     用户发消息后立刻点开历史会话会读到空记录（实测 bug）。
    #     conversation 模块很轻，不触发 openai，可安全提前导入。
    #     chat 和 mod 模式都写：历史会话打开时能显示用户 prompt 气泡。
    #     空 prompt（自动续跑 resume）不写——否则历史里出现空气泡；
    #     纯图片消息 DSH_USER_PROMPT 已由 server 回退为"（图片）"。
    #     mod 模式优先写 DSH_USER_PROMPT（用户原始输入）：包装后的 task_prompt
    #     以"你是一个 MOD 制作器…（C:\本地路径）"开头，直接进历史会污染
    #     侧栏标题并泄漏服务器路径。
    #     resume 一律不写：带消息的 resume 已把消息 enqueue 进队列（由
    #     daemon 消费时落盘，保证处理顺序），这里写会双写且顺序错乱。
    _is_resume = os.environ.get("DSH_RESUME", "") == "1"
    user_prompt = os.environ.get("DSH_USER_PROMPT", "") or task_prompt
    if mode in ("chat", "mod") and user_prompt and not _is_resume:
        try:
            from core.conversation import append_user as _early_append_user
            _early_append_user(session_root_path, user_prompt, images=prompt_images)
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
    #    - chat / mod 模式：加载历史对话 + 当前 prompt（长对话语义：
    #      首轮即带历史，agent 能看到之前的对话，mod 制作可多轮迭代）
    #    - 若运行中排队的消息尚未被 agent 消费（例如恢复时队列里有消息），
    #      会由 agent_loop 每轮开头的 _drain_interjections 自动注入
    # 禁止 agent_loop 中途 drain 排队消息：排队一律由 daemon 逐条消费
    # （每轮一条，严格"问一条答一条"）。首轮 import 要 7-8 秒，期间到达
    # 的排队消息若被轮中途注入，会与本轮需求合并处理、只答最后一条
    # （实测 甲/乙/丙 三连发，乙被吞）。无条件设置（而非仅组装时检测）：
    # 组装时队列可能还空，消息几秒后才到。
    os.environ["DSH_DEFER_DRAIN"] = "1"
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
        try:
            from core.conversation import load_recent_history
            messages = load_recent_history(session_root_path)
        except Exception as e:
            print(f"[run_task] 加载对话历史失败（继续，仅当前 prompt）: {e}", flush=True)
            messages = []
        # 把当前 prompt 作为本轮 user 消息（历史已在步骤 2.5 提前写入）。
        # 空 prompt（自动续跑 resume）不追加——排队消息已在历史里。
        if not task_prompt:
            if not messages:
                print("[run_task] 无 prompt 且无历史可续，退出", flush=True)
                return 1
        else:
            # ① 排队消息被 server 同步写进历史（enqueue 竞态）时，它们属于
            # "本轮之后"的需求：从 messages 滤掉，由 daemon 逐条消费——
            # 否则模型把多条需求当作一轮合并处理，只答最后一条
            # （实测：回复"二"永远丢失）。
            messages = _strip_pending_messages(messages, session_root_path)
            # ② 查重必须扫全列表而非只看末条：运行中排队时末条可能是
            # "下一条排队消息"而非本轮 prompt，只看末条会重复 append
            # （实测 288f3a3a1f41：messages=[u1,u2,u1] 重复）。
            # chat 模式：历史已有本轮 prompt → 跳过（图片挂到该条上）。
            # mod 模式：历史是原始输入，这里追加包装版给 agent（有意并存，
            # 图片只挂包装消息，历史那条同轮剥离避免双份图）。
            if any(m.get("role") == "user" and m.get("content") == task_prompt for m in messages):
                print("[run_task] 历史已包含当前 prompt，跳过重复追加", flush=True)
                if prompt_images:
                    for m in reversed(messages):
                        if m.get("role") == "user" and m.get("content") == task_prompt:
                            m["images"] = prompt_images
                            break
            else:
                if prompt_images and messages and messages[-1].get("role") == "user":
                    messages[-1].pop("images", None)  # 同一轮的裸 prompt 不再带图
                messages.append({"role": "user", "content": task_prompt,
                                 **({"images": prompt_images} if prompt_images else {})})

    # 5. 跑完整 agent 循环（首轮）
    _run_one_round(messages, session_dir, session_root_path, mode)

    # 6. chat / mod 模式都常驻：首轮与 resume 恢复后都进入 daemon 循环，
    #    第二轮起零冷启动（openai SDK / 技能扫描只在首轮支付一次）。
    #    状态跨轮保留：任务/队友/协议等长对话状态不清空（见 daemon_loop 注释）。
    daemon_loop(session_dir, session_root_path, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())