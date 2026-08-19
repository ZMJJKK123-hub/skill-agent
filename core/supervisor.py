"""
监管 Agent（第 13 课：代码强制派发的最高权限观察者）

需求：
- 每次任务开始，由代码强制派发（agent_loop 开头调用 start()，不依赖主 agent 调 task）。
- 后台守护线程持续追踪 run.log / 任务板 / transcript，发现问题写信箱。
- 主 agent 每轮循环开头 drain 信箱：有文件就读取 -> 读完即删 -> 以
  <supervisor-advice>（温和）或 <supervisor-alert>（警告）闭合标签注入。
- 监管 agent 只能使用只读工具（read_file），无执行权；
- 有两种注入方式（用户决策 D 备选）：温和提醒 advice、严重警告 alert。
"""

import json
import logging
import threading
import time
import uuid
from pathlib import Path

from .config import client, MODEL, SUPERVISOR_SYSTEM, SUPERVISOR_MAX_TURNS, logger
from .tools import tool_registry, task_manager
from .subagent import extract_text


# ── 触发参数 ──
SUPERVISOR_INTERVAL = 2.0          # 后台线程停止事件轮询间隔（秒）
SUPERVISOR_EVERY_N_ROUNDS = 5      # 每 N 轮主循环触发一次监管分析
SUPERVISOR_LOG_TAIL_CHARS = 6000   # run.log 尾部取多少字符
SUPERVISOR_TRANSCRIPT_TAIL = 30    # 最新 transcript 取尾部多少行

# ── 项目根（抗 chdir）────────────────────────────
# Bug 修复：run_task.py 会把 cwd chdir 到 <session>/mod，导致
# Path("data/sessions") / Path(".transcripts") 相对 cwd 解析全部失效，
# supervisor 永远读到 "(no run.log)" + "(task board empty)" 而失明，
# 错过"同一问题绕圈"等 ALERT 触发条件。
# 与 SkillLoader 同思路：基于本模块的 __file__
# 定位项目根（core/.. ），与 cwd 无关。
def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


# 监管 agent 的只读工具：只能 read_file，且只允许读工作区内的相对路径
# （docs/agent/ERROR_LIST.md、docs/agent/TOOL_GUIDE.md、KNOWN_ISSUES.md）。
# 不提供 load_skill，避免刷技能目录。
READONLY_NAMES: set[str] = {"read_file"}
READONLY_TOOLS = tool_registry.schemas(include=READONLY_NAMES)


class SupervisorManager:
    """后台监管线程 + 信箱（.supervisor/inbox/，读后即删）。"""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._trigger = threading.Event()
        self._round_count = 0
        self._last_key: str | None = None   # 去重：同一建议不重复写信箱
        # 信箱目录也抗 chdir：固定落在项目根下的 .supervisor/inbox
        self._inbox = _project_root() / ".supervisor" / "inbox"
        self._lock = threading.Lock()

    # ── 生命周期：agent_loop 开头 start，返回前 stop ──
    def start(self) -> bool:
        """由 agent_loop 代码强制调用（幂等：线程已在跑则不重复启动）。"""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False
            self._stop_event.clear()
            self._trigger.clear()
            self._round_count = 0
            self._last_key = None
            self._thread = threading.Thread(
                target=self._loop, daemon=True, name="supervisor"
            )
            self._thread.start()
        # 启动立即分析一次（用户要求：任务开始必派发）
        self._trigger.set()
        logger.info("=== Supervisor 监管线程已强制启动 ===")
        return True

    def stop(self) -> None:
        """agent_loop 返回前调用，join 线程防泄漏。"""
        self._stop_event.set()
        self._trigger.set()  # 唤醒线程立即检查停止
        with self._lock:
            thread, self._thread = self._thread, None
        if thread and thread.is_alive():
            thread.join(timeout=3)
        logger.info("=== Supervisor 监管线程已停止 ===")

    # ── 主循环每轮调用：计数 + 触发 + 排空信箱 ──
    def notify_round(self) -> None:
        self._round_count += 1
        if (
            self._round_count % SUPERVISOR_EVERY_N_ROUNDS == 0
            and self._thread and self._thread.is_alive()
        ):
            self._trigger.set()
            logger.info(f"Supervisor 第 {self._round_count} 轮触发监管分析")

    def drain_advice(self) -> list[dict] | None:
        """扫描信箱 -> 读取 -> 读完即删。返回 [{'type','content'}, ...] 或 None。"""
        if not self._inbox.exists():
            return None
        files = sorted(self._inbox.glob("*.md"))
        if not files:
            return None
        out = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                f.unlink()  # ★ 读完即删
            except OSError:
                continue
            typ = "alert" if content.lstrip().startswith("SEVERITY: alert") else "advice"
            out.append({"type": typ, "content": content})
            logger.info(f"Supervisor 信箱已排空: {f.name} -> type={typ}")
        return out or None

    # ── 后台线程循环 ──
    def _loop(self) -> None:
        while not self._stop_event.is_set():
            if self._trigger.wait(timeout=SUPERVISOR_INTERVAL):
                self._trigger.clear()
                if self._stop_event.is_set():
                    break
                try:
                    self._analyze_once()
                except Exception as e:  # 监管线程任何异常都不能炸主循环
                    logger.warning(f"Supervisor 分析异常: {e}")

    # ── 一次监管分析：读证据 -> 调 LLM（先读 skill）-> 按需写信箱 ──
    def _analyze_once(self) -> None:
        log_path = self._resolve_run_log()
        log_tail = self._tail(log_path, SUPERVISOR_LOG_TAIL_CHARS) if log_path else "(no run.log)"
        tasks_snapshot = self._tasks_summary()
        transcript_tail = self._transcript_tail()

        prompt_parts = [
            f"监管轮次: {self._round_count}",
            f"追踪日志: {log_path}",
            "任务板状态:\n---",
            tasks_snapshot,
            "---",
            "run.log 尾部(可引用行内证据):\n---",
            log_tail,
            "---",
        ]
        if transcript_tail:
            prompt_parts += [
                "最新对话记录尾部(参考上下文):\n---",
                transcript_tail,
                "---",
            ]
        prompt_parts.append(
            "请按你的输出契约分析。无问题就输出 NO_ISSUE，不要编造问题。"
        )

        text = self._run_analysis("\n".join(prompt_parts))

        if "NO_ISSUE" in text:
            logger.info("Supervisor 判定当前无问题")
            return
        severity = None
        stripped = text.lstrip()
        if stripped.startswith("SEVERITY: alert"):
            severity = "alert"
        elif stripped.startswith("SEVERITY: advice"):
            severity = "advice"
        if severity is None:
            logger.info(f"Supervisor 输出未按契约，忽略: {text[:120]!r}")
            return
        # 去重：与上次完全相同的建议不重复写（避免每 5 轮重复噪音）
        key = stripped.splitlines()[0] if stripped.splitlines() else ""
        if key and key == self._last_key:
            logger.info("Supervisor 建议与上次重复，跳过写入")
            return
        self._last_key = key
        self._write_advice(severity, text)
        logger.info(f"Supervisor 写信箱 severity={severity}")

    def _run_analysis(self, prompt: str) -> str:
        """隔离上下文的监管分析循环（参考 run_subagent，只读工具集）。"""
        msgs = [{"role": "user", "content": prompt}]
        message = None
        for turn in range(SUPERVISOR_MAX_TURNS):
            logger.info(f"--- Supervisor 第 {turn + 1} 轮 ---")
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SUPERVISOR_SYSTEM}] + msgs,
                tools=READONLY_TOOLS,
                max_tokens=4000,
            )
            choice = resp.choices[0]
            message = choice.message
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                print(f"\n[supervisor 思考] {reasoning}")
                logger.info(f"supervisor reasoning:\n{reasoning}")
            msgs.append(message.to_dict())
            if choice.finish_reason != "tool_calls":
                break
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception as e:
                    logger.warning(f"supervisor 工具参数解析失败 | {tc.function.name} | {e}")
                    msgs.append({"role": "tool", "tool_call_id": tc.id,
                        "content": f"Error: Invalid tool arguments JSON: {e}"})
                    continue
                # M3: 统一走注册表执行管线（total：异常转温和错误，不中断监管分析）
                output = tool_registry.execute(tc.function.name, args)
                logger.info(f"supervisor 工具调用: {tc.function.name}")
                print(f"[supervisor:{tc.function.name}] {output}")
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": str(output)})
        return extract_text(message) if message else "(supervisor produced no output)"

    # ── 证据采集 ──
    def _resolve_run_log(self) -> Path | None:
        """定位最新会话的 run.log（基于项目根，抗 cwd chdir）。

        run_task.py 会把 cwd chdir 到 <session>/mod，因此不能用相对路径。
        优先取 <项目根>/data/sessions/*/run.log 里最新修改的那个；
        回退到 <项目根>/run.log。
        """
        base = _project_root() / "data" / "sessions"
        if base.exists():
            cands = sorted(base.glob("*/run.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            if cands:
                return cands[0]
        root = _project_root() / "run.log"
        return root if root.exists() else None

    def _tail(self, path: Path, chars: int) -> str:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            text = "\n".join(lines[-200:])
            return text[-chars:]
        except OSError as e:
            return f"(run.log 读取失败: {e})"

    def _tasks_summary(self) -> str:
        try:
            tasks = task_manager.list_tasks()
            if not tasks:
                return "(task board empty)"
            lines = [f"- #{t.get('id')} [{t.get('status', '?')}] {t.get('subject', '')[:80]}" for t in tasks]
            return "\n".join(lines)
        except Exception:
            return "(task board unavailable)"

    def _transcript_tail(self) -> str | None:
        base = _project_root() / ".transcripts"
        if not base.exists():
            return None
        files = sorted(base.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            return None
        try:
            lines = files[0].read_text(encoding="utf-8", errors="replace").splitlines()
            return "\n".join(lines[-SUPERVISOR_TRANSCRIPT_TAIL:])
        except OSError:
            return None

    # ── 信箱写入（原子：先写 tmp 再 rename）──
    def _write_advice(self, severity: str, content: str) -> None:
        try:
            self._inbox.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        ts = time.strftime("%Y%m%d_%H%M%S")
        tmp = self._inbox / f".tmp_{ts}_{uuid.uuid4().hex[:4]}"
        final = self._inbox / f"{ts}_{severity}_{uuid.uuid4().hex[:4]}.md"
        try:
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(final)
        except OSError as e:
            logger.warning(f"Supervisor 写信箱失败: {e}")


# 单例（agent.py 导入后直接使用）
supervisor_manager = SupervisorManager()