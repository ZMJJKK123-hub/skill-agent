# -*- coding: utf-8 -*-
"""队友执行引擎（由 manager.py 拆出，Mixin 模式）。

类职责：_teammate_loop 工作循环（pending-requests 注入/写追踪/身份
重注入）与 _run_teammate_agent 隔离上下文子循环——两个多阶段状态机
编排函数（2026-09-08 用户确认豁免 40 行硬限）。
生命周期：TeammateManager(manager.py) 继承组合。
"""
import json  # 协议消息参数解析
import time  # 轮询/退避节流

from .... import config  # 全局配置（AUTO_MODE 等运行时读取）
from ....config import logger  # 统一日志（子循环内的 SDK/工具导入为函数级局部导入）
from ....protocol import coordinator, inject_pending_requests, parse_protocol_flag  # 团队协议
from ....skillcheck import move_skills_to_end, run_loop_check  # 技能尾部化与循环检查


class TeammateLoopMixin:
    """队友执行循环方法族（self 依赖 manager.py 的团队注册状态）。"""

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
        from ....config import client, MODEL, MAX_SUBAGENT_TURNS, TEAMMATE_SYSTEM_PREFIX
        from ..registry import tool_registry
        from ..handlers import TOOL_HANDLERS

        sub_messages = [{"role": "user", "content": task}]

        # 队友可用的工具：排除团队管理工具（防递归）和 task（防子 Agent 递归）。
        # 队友保留 submit_plan / respond_to_request（第 10 课：队友提计划、响应协议）；
        # 排除 request_shutdown（只有 leader 能发起关机）。
        # 团队成员/子代理不可用（重工具主 agent 独占）：
        #   run_game_test_server / read_game_test_log —— GameTest 进程重、会互踩 run 目录
        excluded = {"spawn_teammate", "send_to_teammate", "team_status", "task",
                    "request_shutdown", "ask_user_question", "run_game_test_server", "read_game_test_log", "run_client", "run_server", "run_data_gen", "run_test_client", "run_test_server", "run_test_data", "run_test_gametest"}
        teammate_tools = tool_registry.schemas(exclude=excluded)

        logger.info(f"=== 队友 Agent 启动 | agent={agent_id} | task={task[:200]} ===")

        response = None
        message = None
        for turn in range(MAX_SUBAGENT_TURNS):
            # ── 第 11 课：身份重注入（Context Compact 后消息列表骤降时触发）──
            from .manager import maybe_reinject_identity  # 延迟导入：manager 组合本模块，调用时已初始化
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
                print(f"\n[teammate 思考] {reasoning}")  # noqa: T201 — run.log 协议输出（前端子代理行渲染依赖；2026-09-08 用户确认豁免）
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
                print(f"[teammate:{tc.function.name}] {output}")  # noqa: T201 — run.log 协议输出（前端子代理行渲染依赖；2026-09-08 用户确认豁免）
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
