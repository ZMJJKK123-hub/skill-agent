# -*- coding: utf-8 -*-
"""MessageBus / TeammateManager / protocol dispatch implementations (moved from core/tools.py)."""
import json
import os
import threading
import time
from dataclasses import dataclass

from . import config
from .config import logger
from .protocol import coordinator, inject_pending_requests, parse_protocol_flag
from .skillcheck import move_skills_to_end, run_loop_check
from .tools_tasks import task_manager

# ---------- MessageBus（第 9 课：JSONL 收件箱，drain-on-read）----------
class MessageBus:
    """append-only 的 JSONL 收件箱系统。

    每个队友一个 .jsonl 文件，send 追加一行，read_inbox 读取全部并清空。
    drain-on-read：消息只需处理一次，读完就清，不需要已读标记。
    线程安全：用 threading.Lock 保护文件操作（队友在同进程线程中）。
    """

    def __init__(self, inbox_dir: str = ".team/inbox"):
        self.inbox_dir = inbox_dir
        os.makedirs(inbox_dir, exist_ok=True)
        self._lock = threading.Lock()
        # 每次启动清空残留的 inbox 文件——上一次 session 的消息已无意义
        # （队友线程随进程退出而死亡，无人再读取这些孤儿消息）
        self._clean_stale_inbox()
        logger.info(f"MessageBus 初始化 | inbox_dir={inbox_dir} | 已清空残留消息")

    def _clean_stale_inbox(self):
        """清空 inbox 目录下所有 .jsonl 文件的残留内容。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时跳过，避免 os.listdir 抛 FileNotFoundError。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        for fname in os.listdir(self.inbox_dir):
            if fname.endswith(".jsonl"):
                path = os.path.join(self.inbox_dir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    pass  # truncate to empty

    def send(self, from_name: str, to_name: str, content: str):
        """往目标队友的收件箱追加一条消息。"""
        msg = {
            "from": from_name,
            "to": to_name,
            "content": content,
            "timestamp": time.time(),
        }
        path = os.path.join(self.inbox_dir, f"{to_name}.jsonl")
        with self._lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        logger.info(f"MessageBus.send | {from_name} → {to_name} | content={content[:100]}")

    def broadcast(self, from_name: str, content: str, team: dict):
        """群发给所有队友（除自己外）。"""
        for name in team:
            if name != from_name:
                self.send(from_name, name, content)

    def read_inbox(self, name: str) -> list:
        """读取并清空收件箱（drain-on-read）。"""
        path = os.path.join(self.inbox_dir, f"{name}.jsonl")
        if not os.path.exists(path):
            return []
        with self._lock:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # 读完即清
            with open(path, "w", encoding="utf-8") as f:
                pass  # truncate to empty
        msgs = []
        for l in lines:
            if not l.strip():
                continue
            try:
                msgs.append(json.loads(l))
            except json.JSONDecodeError:
                logger.warning(f"MessageBus.read_inbox | {name} | 跳过损坏消息行")
                continue
        logger.info(f"MessageBus.read_inbox | {name} | 读取 {len(msgs)} 条消息")
        return msgs

    def clear_all(self):
        """第 11 课：清空所有收件箱文件（session 收尾时调用）。

        只清空 .jsonl 文件内容，保留目录本身。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时直接跳过，避免 os.listdir 抛 FileNotFoundError 使主循环崩溃。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        with self._lock:
            for fname in os.listdir(self.inbox_dir):
                if fname.endswith(".jsonl"):
                    path = os.path.join(self.inbox_dir, fname)
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            pass  # truncate to empty
                    except OSError:
                        pass
        logger.info(f"MessageBus.clear_all | 已清空 {self.inbox_dir} 下所有收件箱文件")

# ---------- 第 11 课：身份重注入（Context Compact 后防止角色丢失）----------
IDENTITY_THRESHOLD = 3  # 消息列表低于该数时认为刚经历过压缩，需要重注入身份

def maybe_reinject_identity(agent_id: str, role_prompt: str,
                            messages: list) -> list:
    """第 11 课机制四：消息列表过短时在开头插入 <identity> 身份块。

    Context Compact（第 6 课）会压缩消息历史，包括可能丢掉的 system 身份信息。
    若消息列表数量骤降（< IDENTITY_THRESHOLD），说明刚被压缩过——
    此时把"我是谁"用 <identity> 标签重新注入，防止队友角色越权
    （coder 开始审查代码、tester 开始写业务逻辑）。

    用 user 消息而不是改 system——因为 system 在 API 层面只设一次，
    身份重注入需要在对话过程中动态触发。

    :param agent_id: 队友名字（如 "coder"）
    :param role_prompt: 队友的完整 system prompt（角色定义）
    :param messages: 当前对话消息列表
    :return: 注入后的新消息列表（未触发则原样返回）
    """
    if len(messages) >= IDENTITY_THRESHOLD:
        return messages
    identity_block = {
        "role": "user",
        "content": (
            f"<identity>\n你是 {agent_id}。\n"
            f"{role_prompt}\n</identity>"
        ),
    }
    logger.info(f"maybe_reinject_identity | {agent_id} | 消息数={len(messages)} < {IDENTITY_THRESHOLD}，注入身份块")
    return [identity_block] + messages

# ---------- TeammateManager（第 9 课：持久 Agent + 身份管理 + 通信）----------
@dataclass
class TeammateConfig:
    """队友配置：name, system_prompt, status (idle/working/shutdown)。"""
    name: str
    system_prompt: str
    status: str = "idle"

class TeammateManager:
    """团队名册管理器。spawn/shutdown 队友，每个队友在独立线程中运行。

    队友不是函数调用，是被委托任务的独立 Agent——有自己的 messages、
    自己的工具、自己的上下文。跟第 1 课的 while 循环完全一样。
    状态持久化到 .team/config.json，Agent 重启后团队名册还在。
    """

    def __init__(self):
        self.team_dir = ".team"
        self.config_path = os.path.join(self.team_dir, "config.json")
        os.makedirs(self.team_dir, exist_ok=True)
        os.makedirs(os.path.join(self.team_dir, "inbox"), exist_ok=True)
        self.team: dict = {}
        self.bus = MessageBus(os.path.join(self.team_dir, "inbox"))
        self.threads: dict = {}
        self._lock = threading.Lock()
        # 持久化恢复：上次进程退出时留下的队友名册会恢复为 shutdown（线程已不存在），
        # 用户仍能看到历史队友；需要时 spawn 会重新创建并启动线程。
        self._load_team_config()
        self._save_team_config()
        logger.info(
            f"TeammateManager 初始化 | 恢复 {len(self.team)} 个队友名册 | "
            f"活跃线程: {list(self.threads.keys())}"
        )

    def _load_team_config(self) -> None:
        """从 .team/config.json 加载队友名册；线程不存在，全部标记为 shutdown。"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                for name, data in raw.items():
                    if not isinstance(data, dict):
                        continue
                    cfg = TeammateConfig(
                        name=str(name),
                        system_prompt=str(data.get("system_prompt", "")),
                        status="shutdown",
                    )
                    self.team[str(name)] = cfg
        except Exception as e:
            logger.warning(f"TeammateManager._load_team_config 失败: {e}")

    def _save_team_config(self):
        """保存团队名册到 .team/config.json。

        Bug D 修复：Agent 收尾可能按任务要求用 bash 物理删除 .team 目录，
        此时 .team 可能不存在。写前确保目录存在（自愈重建空目录），
        避免 open('.team/config.json','w') 抛 FileNotFoundError 使主循环崩溃。
        """
        os.makedirs(self.team_dir, exist_ok=True)
        raw = {
            name: {
                "name": cfg.name,
                "system_prompt": cfg.system_prompt,
                "status": cfg.status,
            }
            for name, cfg in self.team.items()
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)

    def spawn(self, name: str, system_prompt: str) -> str:
        """创建队友并启动守护线程。已存在的 idle 队友会重启线程。"""
        with self._lock:
            if name in self.team:
                if self.team[name].status == "shutdown":
                    # shutdown 状态可以重新创建
                    self.team[name] = TeammateConfig(name=name, system_prompt=system_prompt)
                    self._save_team_config()
                elif self.team[name].status == "idle":
                    # idle 状态：更新 system_prompt，重启线程
                    self.team[name].system_prompt = system_prompt
                    self._save_team_config()
                    logger.info(f"TeammateManager.spawn | 队友 {name} 已存在(idle)，重启线程")
                else:
                    # working 状态：不能重新 spawn
                    return f"Error: Teammate '{name}' already exists and is {self.team[name].status}"
            else:
                self.team[name] = TeammateConfig(name=name, system_prompt=system_prompt)
                self._save_team_config()

        thread = threading.Thread(
            target=self._teammate_loop, args=(name,), daemon=True
        )
        self.threads[name] = thread
        thread.start()
        logger.info(f"TeammateManager.spawn | 队友 {name} 已创建并启动")
        return f"Teammate {name} spawned and started"

    def send_task(self, to_name: str, task: str) -> str:
        """给队友发送任务消息。"""
        with self._lock:
            if to_name not in self.team:
                return f"Error: Teammate '{to_name}' not found. Use spawn_teammate first."
            if self.team[to_name].status == "shutdown":
                return f"Error: Teammate '{to_name}' is shutdown."
        self.bus.send("leader", to_name, task)
        with self._lock:
            if self.team[to_name].status == "idle":
                self.team[to_name].status = "working"
                self._save_team_config()
        logger.info(f"TeammateManager.send_task | leader → {to_name} | task={task[:100]}")
        return f"Task sent to {to_name}"

    def shutdown(self, name: str) -> str:
        """关闭队友。"""
        with self._lock:
            if name not in self.team:
                return f"Error: Teammate '{name}' not found."
            self.team[name].status = "shutdown"
            self._save_team_config()
            # 清理线程引用（线程自身会在下次循环检测到 shutdown 后退出）
            self.threads.pop(name, None)
        logger.info(f"TeammateManager.shutdown | 队友 {name} 已关闭")
        return f"Teammate {name} shut down"

    def render_status(self) -> str:
        """渲染团队名册，让模型看到全局状态。"""
        if not self.team:
            return "(no teammates)"
        icons = {"idle": "💤", "working": "🔧", "shutdown": "🚫"}
        lines = ["📋 Team Roster:"]
        for name, cfg in self.team.items():
            icon = icons.get(cfg.status, "?")
            prompt_preview = cfg.system_prompt[:50] + "..." if len(cfg.system_prompt) > 50 else cfg.system_prompt
            lines.append(f"  {icon} {name} [{cfg.status}] — {prompt_preview}")
        return "\n".join(lines)

    def _try_claim_from_board(self, name: str) -> dict | None:
        """第 11 课：IDLE 阶段扫描看板，认领一个可执行任务。

        返回认领到的任务 dict；没有可认领/被抢返回 None（下一轮重试）。
        """
        for task in task_manager.unclaimed_actionable():
            if task_manager.claim(task["id"], name):
                return task
        return None

    def _teammate_loop(self, name: str):
        """队友循环：IDLE 阶段（收件箱 + 扫看板认领）→ WORK 阶段（跑 Agent Loop）。

        第 11 课自治：
        1. 收件箱有直接指派 → 优先处理（与第 9-10 课一致）
        2. 收件箱无活 → 扫描 .tasks 看板自由认领（pending + 无主 + 未阻塞）
        3. 认领成功 → 构造工作消息走 WORK
        4. 每 5s 扫一次，60s 无活 → 自动 SHUTDOWN
        """
        idle_deadline = time.time() + 60  # IDLE 阶段最多等 60s，超时自动关机

        while True:
            with self._lock:
                cfg = self.team.get(name)
                if cfg is None or cfg.status == "shutdown":
                    logger.info(f"TeammateManager._teammate_loop | {name} 退出")
                    return

            # ── IDLE 阶段 ──
            # 1) 收件箱（直接指派优先）
            messages = self.bus.read_inbox(name)

            # 2) 收件箱没活 → 扫描看板认领（第 11 课）
            if not messages:
                try:
                    claimed = self._try_claim_from_board(name)
                except Exception as e:
                    logger.exception(f"TeammateManager._teammate_loop | {name} 扫看板异常: {e}")
                    claimed = None

                if claimed is None:
                    # 没活干：IDLE 超时自动关机
                    if time.time() >= idle_deadline:
                        logger.info(f"TeammateManager._teammate_loop | {name} IDLE 超时 60s 无任务，自动关机")
                        with self._lock:
                            if self.team[name].status != "shutdown":
                                self.team[name].status = "shutdown"
                                self._save_team_config()
                        return
                    time.sleep(5)  # 每 5s 扫一次看板（课文 idle_poll 间隔）
                    continue

                # 3) 认领成功 → 构造工作消息走 WORK
                idle_deadline = time.time() + 60  # WORK 完成后重置 IDLE 超时
                logger.info(f"TeammateManager._teammate_loop | {name} 认领看板任务 #{claimed['id']}，进入 WORK")
                messages = [{
                    "from": "board",
                    "content": (
                        f"你从任务看板认领了任务 #{claimed['id']}：{claimed['subject']}\n"
                        f"完成该任务后，用 task_update 把任务 #{claimed['id']} 标记为 completed。"
                    ),
                }]

            # ── WORK 阶段 ──
            with self._lock:
                if self.team[name].status != "shutdown":
                    self.team[name].status = "working"
                    self._save_team_config()

            # 处理每条消息
            for msg in messages:
                # 检查是否被 shutdown 了
                with self._lock:
                    cfg = self.team.get(name)
                    if cfg is None or cfg.status == "shutdown":
                        break

                content = msg["content"]

                # ── 协议消息（第 10 课）：确定性代码处理，不走 LLM ──
                parsed = parse_protocol_flag(content)
                if parsed:
                    ptype, pargs = parsed
                    if ptype == "shutdown":
                        outcome = coordinator.handle_shutdown_request(name, pargs[0])
                        if outcome == "exit":
                            self.bus.send(
                                name, "leader",
                                f"[{name} 完成] Shutdown approved & buffers flushed, "
                                f"teammate thread exiting now",
                            )
                            with self._lock:
                                self.team[name].status = "shutdown"
                                self._save_team_config()
                            logger.info(f"TeammateManager._teammate_loop | {name} 安全退出（关机握手批准）")
                            return
                        # REJECTED：把拒绝原因也照常发回 leader（走普通汇报格式）
                        self.bus.send(
                            name, "leader",
                            f"[{name} 完成] {outcome}",
                        )
                        logger.info(f"TeammateManager._teammate_loop | {name} 拒绝关机，继续运行: {outcome[:100]}")
                        continue
                    elif ptype in ("plan_result", "shutdown_result"):
                        # 审批结果回执/关机结果回执：无需队友处理，已由 tracker 记录
                        logger.info(f"TeammateManager._teammate_loop | {name} 收到回执: {content[:100]}")
                        continue
                    else:
                        logger.info(f"TeammateManager._teammate_loop | {name} 未知协议消息: {content[:100]}")
                        continue

                # ── 普通任务消息：跑 Agent Loop ──
                logger.info(
                    f"TeammateManager._teammate_loop | {name} 处理消息: "
                    f"{content[:100]}"
                )
                result = self._run_teammate_agent(
                    system=cfg.system_prompt,
                    task=content,
                    agent_id=name,
                )
                # 结果发回 leader（看板认领的任务回报给 leader，便于观测）
                self.bus.send(name, msg["from"], f"[{name} 完成] {result}")

            # 处理完，回到 idle
            with self._lock:
                if self.team[name].status != "shutdown":
                    self.team[name].status = "idle"
                    self._save_team_config()

    def _run_teammate_agent(self, system: str, task: str, agent_id: str) -> str:
        """执行一轮独立的 Agent Loop——跟 subagent.py 模式一样。

        队友拥有除团队管理工具和 task 外的所有工具（防递归）。

        第 10 课改造：
        1. 每轮注入该队友的 pending-requests（计划审批结果 / 关机请求）
        2. 执行 write_file / edit_file 时自动登记到 AgentWriteTracker
        第 11 课改造：身份重注入——compact 后消息列表骤降（<阈值）时，
        在开头插入 <identity> 块，防止队友忘了"我是谁"导致角色越权。
        """
        from .config import client, MODEL, MAX_SUBAGENT_TURNS, TEAMMATE_SYSTEM_PREFIX
        from .tools import TOOLS, TOOL_HANDLERS

        sub_messages = [{"role": "user", "content": task}]

        # 队友可用的工具：排除团队管理工具（防递归）和 task（防子 Agent 递归）。
        # 队友保留 submit_plan / respond_to_request（第 10 课：队友提计划、响应协议）；
        # 排除 request_shutdown（只有 leader 能发起关机）。
        # 团队成员/子代理不可用（重工具主 agent 独占）：
        #   run_game_test_server / read_game_test_log —— GameTest 进程重、会互踩 run 目录
        excluded = {"spawn_teammate", "send_to_teammate", "team_status", "task",
                    "request_shutdown", "ask_user_question", "run_game_test_server", "read_game_test_log", "run_client", "run_server", "run_data_gen", "run_test_client", "run_test_server", "run_test_data", "run_test_gametest"}
        teammate_tools = [t for t in TOOLS if t["function"]["name"] not in excluded]

        logger.info(f"=== 队友 Agent 启动 | agent={agent_id} | task={task[:200]} ===")

        response = None
        message = None
        for turn in range(MAX_SUBAGENT_TURNS):
            # ── 第 11 课：身份重注入（Context Compact 后消息列表骤降时触发）──
            sub_messages = maybe_reinject_identity(agent_id, system, sub_messages)

            # ── 第 10 课：每轮开始注入协议请求（计划审批结果 / 关机请求）──
            inject_pending_requests(sub_messages, agent_id)

            move_skills_to_end(sub_messages)
            logger.info(f"--- 队友 Agent 第 {turn + 1} 轮 ---")
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": TEAMMATE_SYSTEM_PREFIX + system}] + sub_messages,
                tools=teammate_tools,
                max_tokens=8000,
            )

            choice = response.choices[0]
            message = choice.message

            # 打印队友思考过程
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                print(f"\n[teammate 思考] {reasoning}")
                logger.info(f"teammate reasoning:\n{reasoning}")

            sub_messages.append(message.to_dict())
            # skill-source 引用校验仅 mod 模式生效（chat 模式队友任务无需引用块）
            if choice.finish_reason != "tool_calls" and config.MODE == "mod":
                if not run_loop_check("teammate", message.content, sub_messages):
                    continue
            logger.info(f"teammate finish_reason={choice.finish_reason}")

            # 队友决定不再调工具 → 任务完成
            if choice.finish_reason != "tool_calls":
                break

            # 执行工具，收集结果
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception as e:
                    logger.warning(f"teammate 工具参数解析失败 | {tc.function.name} | {e}")
                    sub_messages.append({"role": "tool", "tool_call_id": tc.id,
                        "content": f"Error: Invalid tool arguments JSON for {tc.function.name}: {e}. Please retry with valid JSON."})
                    continue
                # 第 10/11 课：submit_plan / claim_task 需要记录发起方（队友身份）
                if tc.function.name in ("submit_plan", "claim_task"):
                    args["_agent_id"] = agent_id
                handler = TOOL_HANDLERS.get(tc.function.name)
                output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
                logger.info(f"teammate 工具调用: {tc.function.name}")
                # 调试需要：完整输出写入 run.log，不截断
                print(f"[teammate:{tc.function.name}] {output}")
                sub_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": output,
                    }
                )

                # 第 10 课：写入文件后自动登记（关机握手依赖此登记判断未提交写入）
                if tc.function.name in ("write_file", "edit_file"):
                    coordinator.writes.record_write(agent_id, args.get("path", "?"))

        final_text = message.content if message and message.content else "(teammate produced no text output)"

        # 第 10 课修复：队友完成一轮任务后，本轮所有 write_file/edit_file 已同步落盘
        # （write_file 是同步写盘，不是异步缓冲），此时清空写入登记是准确反映
        # "已提交"状态。否则登记永久残留，关机握手会无限 REJECTED（死循环）。
        coordinator.writes.flush(agent_id)

        logger.info(f"=== 队友 Agent 结束 | agent={agent_id} | 最终文本={final_text[:200]} ===")
        return final_text

teammate_manager = TeammateManager()

def _submit_plan(kw: dict) -> str:
    """队友提交计划审批。用 current_agent_id 记录发起方。"""
    agent = kw.get("_agent_id", "unknown")
    plan = {
        "summary": kw.get("plan_summary", ""),
        "files": kw.get("affected_files", []),
        "risk": kw.get("risk_level", "low"),
        "change_count": kw.get("estimated_changes", 0),
    }
    return coordinator.submit_plan_for_review(agent, plan)

def _respond_to_request(kw: dict) -> str:
    """leader 审批/响应协议请求。decision ∈ approve | reject。

    状态守卫温和化：LLM 可能传一个已决议的 req_id（误用/测试/幻觉），
    此时 tracker.respond() 会抛 ValueError。如果让它冒泡，整个 agent 主循环
    会被一个工具调用炸毁。这里捕获并转成温和错误文本，LLM 拿到的只是
    一条 Error 消息，可以继续思考，程序不中断。
    """
    decision = kw.get("decision", "approve")
    reason = kw.get("reason", "")
    try:
        return coordinator.handle_plan_review(kw["req_id"], decision, reason)
    except ValueError as e:
        logger.info(f"respond_to_request 捕获状态守卫异常 | {e}")
        return f"Error: {e}"
