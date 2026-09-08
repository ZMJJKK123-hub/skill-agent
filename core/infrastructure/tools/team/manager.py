# -*- coding: utf-8 -*-
"""TeammateManager：持久 Agent + 身份管理 + 通信 + 工具入口。
由 team.py 原样迁出（含身份重注入与队友线程循环）。
"""
import json
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from .... import config
from ....config import logger
from ....protocol import coordinator, inject_pending_requests, parse_protocol_flag
from ....skillcheck import move_skills_to_end, run_loop_check
from ..tasks import task_manager
from .loop import TeammateLoopMixin  # 队友执行引擎（拆分模块）
from .bus import MessageBus


def _is_safe_agent_name(name: str) -> bool:
    return bool(name and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name))



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

class TeammateManager(TeammateLoopMixin):
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
        if not _is_safe_agent_name(name):
            return "Error: 队友名只能包含字母、数字、下划线或短横线"
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

teammate_manager = TeammateManager()  # 单例（loop mixin 在类定义处组合）

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
