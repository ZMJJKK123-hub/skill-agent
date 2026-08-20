"""
第 10 课：团队协议——状态机驱动的协商

两个协议共享同一个 FSM（pending → approved | rejected）：

  关机协议（leader → 队友）：      request_shutdown → 队友检查未提交写入
                                  → APPROVED（安全退出）/ REJECTED（继续运行）
  计划审批协议（队友 → leader）：   submit_plan → leader 审批
                                  → APPROVED（开始执行）/ REJECTED（修改计划）

方向不同，结构相同——ProtocolTracker 不关心 req_type，
它只负责状态流转。req_id 贯穿整个请求-响应生命周期，
respond() 里的状态守卫把非法状态转换变成显式 ValueError。

本模块不依赖 tools.py（避免循环依赖）：
TeamCoordinator 通过 wire() 由 tools.py 注入 MessageBus / 团队名册 / 强制关闭回调。
"""

from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import time
import threading

from .config import logger

# [PROTOCOL] 前缀：MessageBus 里标记协议消息，不走普通任务 Agent Loop
PROTOCOL_FLAG = "[PROTOCOL]"


# ---------- 共享状态机 ----------
class RequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ProtocolRequest:
    """请求-响应生命周期的载体。req_id 关联整个流程。"""
    req_id: str
    req_type: str          # "shutdown" | "plan"
    from_agent: str        # 发起方
    to_agent: str          # 接收方
    payload: dict          # 请求内容
    status: RequestStatus = RequestStatus.PENDING
    response_payload: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


# ---------- 请求追踪器 ----------
class ProtocolTracker:
    """所有请求-响应协议的核心。只管理状态流转，不关心 req_type。"""

    STATE_FILE = ".team/protocol.json"

    def __init__(self):
        self._requests: dict[str, ProtocolRequest] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """从 .team/protocol.json 恢复协议请求（进程重启后继续保留）。"""
        try:
            import os
            if os.path.exists(self.STATE_FILE):
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data or []:
                    try:
                        req = ProtocolRequest(
                            req_id=item["req_id"],
                            req_type=item["req_type"],
                            from_agent=item["from_agent"],
                            to_agent=item["to_agent"],
                            payload=item.get("payload", {}),
                            status=RequestStatus(item.get("status", "pending")),
                            response_payload=item.get("response_payload", {}),
                            created_at=item.get("created_at", time.time()),
                        )
                        self._requests[req.req_id] = req
                    except Exception:
                        continue
                if self._requests:
                    logger.info(f"ProtocolTracker._load | 恢复 {len(self._requests)} 条协议请求")
        except Exception as e:
            logger.warning(f"ProtocolTracker._load 失败: {e}")

    def _save(self) -> None:
        """持久化所有协议请求到 .team/protocol.json。"""
        try:
            import os
            os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
            data = []
            for r in self._requests.values():
                data.append({
                    "req_id": r.req_id,
                    "req_type": r.req_type,
                    "from_agent": r.from_agent,
                    "to_agent": r.to_agent,
                    "payload": r.payload,
                    "status": r.status.value,
                    "response_payload": r.response_payload,
                    "created_at": r.created_at,
                })
            with open(self.STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"ProtocolTracker._save 失败: {e}")

    def create_request(self, req_type, from_agent, to_agent, payload) -> str:
        req_id = f"{req_type}_{uuid.uuid4().hex[:8]}"
        req = ProtocolRequest(
            req_id=req_id, req_type=req_type,
            from_agent=from_agent, to_agent=to_agent, payload=payload,
        )
        with self._lock:
            self._requests[req_id] = req
            self._save()
        logger.info(
            f"ProtocolTracker.create_request | {req_id} | {req_type} | "
            f"{from_agent} → {to_agent}"
        )
        return req_id

    def respond(self, req_id, status, response_payload=None) -> ProtocolRequest:
        """决议请求。状态守卫：已决议的请求不能再改（防并发双重响应）。"""
        with self._lock:
            req = self._requests.get(req_id)
            if req is None:
                raise ValueError(f"Request {req_id} not found")
            if req.status != RequestStatus.PENDING:
                raise ValueError(f"Request {req_id} already resolved")  # 状态守卫
            req.status = status
            req.response_payload = response_payload or {}
            self._save()
        logger.info(
            f"ProtocolTracker.respond | {req_id} → {status.value} | "
            f"response={response_payload}"
        )
        return req

    def get_request(self, req_id) -> ProtocolRequest | None:
        return self._requests.get(req_id)

    def get_pending(self, agent_id: str) -> list[ProtocolRequest]:
        """发给该 agent 且仍待处理（需要响应/处理）的请求。"""
        with self._lock:
            return [r for r in self._requests.values()
                    if r.to_agent == agent_id and r.status == RequestStatus.PENDING]

    def get_resolved(self, agent_id: str | None = None) -> list[ProtocolRequest]:
        """已决议的请求。agent_id 为空返回全部；否则返回该 agent 参与过的。"""
        with self._lock:
            result = [r for r in self._requests.values()
                      if r.status != RequestStatus.PENDING]
            if agent_id:
                result = [r for r in result
                          if r.from_agent == agent_id or r.to_agent == agent_id]
            return result

    def all_requests(self) -> list[ProtocolRequest]:
        with self._lock:
            return list(self._requests.values())

    def reset(self):
        """清空所有请求（session 结束时调用，与 team 清空保持一致）。"""
        with self._lock:
            self._requests.clear()
            self._save()
        logger.info("ProtocolTracker.reset | 已清空所有请求")


# ---------- 未提交写入追踪（关机握手的前提）----------
class AgentWriteTracker:
    """记录每个 agent 通过 write_file / edit_file 工具写入过的文件。

    不是"LLM 自觉报告"，而是工具调度层自动登记（handler 拦截）。
    关机请求到达时：有未提交写入 → 拒绝（队友继续写）→ 写完自动 flush → 批准。
    """

    def __init__(self):
        self._writes: dict[str, set[str]] = {}
        self._lock = threading.Lock()

    def record_write(self, agent_id: str, path: str):
        with self._lock:
            self._writes.setdefault(agent_id, set()).add(path)
        logger.info(f"AgentWriteTracker.record_write | {agent_id} → {path}")

    def has_uncommitted_writes(self, agent_id: str) -> bool:
        with self._lock:
            return bool(self._writes.get(agent_id))

    def pending_files(self, agent_id: str) -> list[str]:
        with self._lock:
            return sorted(self._writes.get(agent_id, set()))

    def flush(self, agent_id: str) -> list[str]:
        """把当前批次写入标记为已落盘（清空登记）。"""
        with self._lock:
            files = sorted(self._writes.pop(agent_id, set()))
        logger.info(f"AgentWriteTracker.flush | {agent_id} | 已 flush {len(files)} 个文件")
        return files


# ---------- 团队协调器：两种协议，一个 FSM ----------
class TeamCoordinator:
    """关机握手 + 计划审批。

    依赖通过 wire() 注入（bus / team / force_shutdown_fn），
    由 tools.py 在模块底部完成接线，避免循环导入。
    """

    def __init__(self):
        self.tracker = ProtocolTracker()
        self.writes = AgentWriteTracker()
        self.bus = None
        self.team = None
        self._force_shutdown = None

    def wire(self, bus, team, force_shutdown_fn):
        """由 tools.py 调用，注入消息总线 / 团队名册 / 强制关闭回调。"""
        self.bus = bus
        self.team = team
        self._force_shutdown = force_shutdown_fn
        logger.info("TeamCoordinator.wire | 已注入 bus/team/force_shutdown_fn")

    # ── 关机协议（leader → 队友）──────────────────────
    def request_shutdown(self, target_agent: str, reason: str = "task_complete") -> str:
        """leader 发起关机握手，返回 req_id。不再直接杀线程。"""
        if self.team is None or target_agent not in self.team:
            return f"Error: Teammate '{target_agent}' not found"

        req_id = self.tracker.create_request(
            req_type="shutdown", from_agent="leader",
            to_agent=target_agent, payload={"reason": reason},
        )
        # 协议消息走 [PROTOCOL] 前缀，队友 loop 识别后交给代码确定性处理
        self.bus.send("leader", target_agent, f"{PROTOCOL_FLAG} shutdown {req_id}")
        logger.info(
            f"TeamCoordinator.request_shutdown | {req_id} | target={target_agent} | "
            f"reason={reason}"
        )
        return f"Shutdown request sent to {target_agent}: {req_id}"

    def handle_shutdown_request(self, agent_id: str, req_id: str) -> str:
        """队友侧：确定性处理关机请求——检查写入 → 清理/拒绝 → 回复。

        返回 'exit' 表示已批准（队友线程应立即安全退出）；
        否则返回拒绝原因文本（队友 Agent 继续完成工作）。
        """
        if self.writes.has_uncommitted_writes(agent_id):
            files = self.writes.pending_files(agent_id)
            self.tracker.respond(
                req_id, RequestStatus.REJECTED,
                {"reason": "uncommitted_writes", "files": files},
            )
            self.bus.send(
                agent_id, "leader",
                f"{PROTOCOL_FLAG} shutdown_result {req_id} rejected "
                f"uncommitted_writes {len(files)}",
            )
            logger.info(
                f"TeamCoordinator.handle_shutdown_request | {agent_id} 拒绝关机 | "
                f"{len(files)} 个文件未提交: {files[:5]}"
            )
            return (
                f"Shutdown REJECTED: {len(files)} file(s) with uncommitted writes: "
                f"{', '.join(files[:10])}{'...' if len(files) > 10 else ''}. "
                f"Finish writing and flushing these files first."
            )

        # 无未提交写入 → 刷盘 → 批准安全退出
        self.writes.flush(agent_id)
        self.tracker.respond(req_id, RequestStatus.APPROVED)
        self.bus.send(
            agent_id, "leader",
            f"{PROTOCOL_FLAG} shutdown_result {req_id} approved",
        )
        logger.info(f"TeamCoordinator.handle_shutdown_request | {agent_id} 同意关机，缓冲区已刷盘")
        return "exit"

    def check_shutdown(self, agent_id: str) -> str | None:
        """队友每轮调用。有 pending 的 shutdown 请求就确定性处理。

        返回 'exit' → 队友线程应退出；返回其它文本 → 拒绝原因（注入队友上下文）；
        没有请求 → 返回 None。
        """
        pending = [r for r in self.tracker.get_pending(agent_id)
                   if r.req_type == "shutdown"]
        if not pending:
            return None
        return self.handle_shutdown_request(agent_id, pending[0].req_id)

    # ── 计划审批协议（队友 → leader）──────────────────
    def submit_plan_for_review(self, agent_id: str, plan: dict) -> str:
        """队友提交计划，创建 plan 请求等待 leader 审批。"""
        req_id = self.tracker.create_request(
            req_type="plan", from_agent=agent_id, to_agent="leader",
            payload={
                "plan_summary": plan.get("summary", ""),
                "affected_files": plan.get("files", []),
                "risk_level": plan.get("risk", "low"),
                "estimated_changes": plan.get("change_count", 0),
            },
        )
        self.bus.send(agent_id, "leader", f"{PROTOCOL_FLAG} plan_ready {req_id}")
        logger.info(f"TeamCoordinator.submit_plan_for_review | {req_id} | from={agent_id}")
        return f"Plan submitted for review: {req_id}（等待 <pending-requests> 中的审批结果）"

    def handle_plan_review(self, req_id: str, decision: str, reason: str = "") -> str:
        """leader 侧：审批计划请求。decision ∈ approve | reject。

        角色守卫：只允许审批 plan 类型请求。shutdown 请求由队友侧确定性代码
        （handle_shutdown_request）处理，队友不能用 respond_to_request 手动响应——
        否则会造成双重响应，触发状态守卫 ValueError。
        """
        req = self.tracker.get_request(req_id)
        if req is None:
            return f"Error: Request {req_id} not found"
        if req.req_type != "plan":
            return (
                f"Error: Request {req_id} is type={req.req_type}, "
                f"not a plan approval. Shutdown requests are handled automatically."
            )
        status = (RequestStatus.APPROVED if decision == "approve"
                  else RequestStatus.REJECTED)
        req = self.tracker.respond(req_id, status, {"reason": reason})
        # 通知队友审批结果，队友在下轮 Agent 循环的 <pending-requests> 里看到
        self.bus.send(
            "leader", req.from_agent,
            f"{PROTOCOL_FLAG} plan_result {req_id} {status.value} {reason}",
        )
        logger.info(f"TeamCoordinator.handle_plan_review | {req_id} → {status.value} | reason={reason}")
        if status == RequestStatus.REJECTED:
            return f"Plan {req_id} rejected: {reason or 'no reason given'}"
        return f"Plan {req_id} approved, proceed with execution"

    def auto_review_plan(self, req_id: str) -> str:
        """课文逻辑：按风险自动审批。high_risk → 拒绝（建议拆小）；否则批准。"""
        req = self.tracker.get_request(req_id)
        if req is None:
            return f"Error: Request {req_id} not found"
        if req.payload.get("risk_level") == "high":
            return self.handle_plan_review(
                req_id, "reject",
                "high_risk: Break into smaller changes",
            )
        return self.handle_plan_review(req_id, "approve")

    # ── 通用辅助 ────────────────────────────────────
    def render_status(self) -> str:
        """渲染所有协议请求的状态，供模型查看全局协商进度。"""
        reqs = self.tracker.all_requests()
        if not reqs:
            return "(no protocol requests)"
        icons = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
        lines = ["📡 Protocol Requests:"]
        for r in sorted(reqs, key=lambda x: x.created_at):
            icon = icons.get(r.status.value, "?")
            preview = ""
            if r.req_type == "plan" and r.status == RequestStatus.PENDING:
                p = r.payload
                preview = f" | {p.get('plan_summary', '')[:40]} | risk={p.get('risk_level')}"
            lines.append(
                f"  {icon} [{r.req_id}] {r.req_type} | {r.from_agent} → {r.to_agent} "
                f"| {r.status.value}{preview}"
            )
        return "\n".join(lines)

    def reset(self):
        self.tracker.reset()
        self.writes._writes.clear()
        logger.info("TeamCoordinator.reset | 已清空请求与写入登记")


# ---------- 单例（tools.py 底部 wire）----------
coordinator = TeamCoordinator()


# ---------- 协议消息与上下文注入 ----------
def parse_protocol_flag(content: str):
    """解析 [PROTOCOL] 前缀的协议消息，返回 (type, args) 或 None。"""
    if not content.startswith(PROTOCOL_FLAG):
        return None
    parts = content[len(PROTOCOL_FLAG):].strip().split()
    if not parts:
        return None
    return parts[0], parts[1:]


def inject_pending_requests(messages: list, agent_id: str) -> None:
    """把需要该 agent 注意的协议请求以 <pending-requests> 标签注入。

    让模型明确区分这是协议事件，而非用户输入或工具结果。

    注入两类：
    1. 发给该 agent 且仍 PENDING 的请求（leader 需要审批 plan；队友需要处理 shutdown）
    2. 该 agent 发起、已决议的 plan 请求（队友看到自己的审批结果）
    """
    parts = []

    # 1. 待响应 / 待处理的 pending 请求
    for req in coordinator.tracker.get_pending(agent_id):
        if req.req_type == "plan":
            p = req.payload
            files = p.get("affected_files", [])
            parts.append(
                f"[{req.req_id}] type=plan from={req.from_agent} (awaiting your approval)\n"
                f"  summary: {p.get('plan_summary', '')}\n"
                f"  files: {', '.join(files) if files else '(none)'}\n"
                f"  risk: {p.get('risk_level', 'unknown')} | estimated changes: {p.get('estimated_changes', 0)}\n"
                f"  → respond with respond_to_request(req_id='{req.req_id}', "
                f"decision='approve'|'reject', reason=...) or auto_review_plan(req_id='{req.req_id}')"
            )
        else:
            parts.append(
                f"[{req.req_id}] type={req.req_type} from={req.from_agent} "
                f"payload={req.payload}"
            )

    # 2. 自己发起、已决议的请求（队友看计划审批结果；leader 看关机结果）
    for req in coordinator.tracker.get_resolved(agent_id):
        if req.from_agent == agent_id:
            if req.req_type == "plan":
                resp = req.response_payload
                outcome = "approved ✅" if req.status == RequestStatus.APPROVED else "rejected ❌"
                reason = resp.get("reason", "") if resp else ""
                parts.append(
                    f"[{req.req_id}] type=plan from={req.from_agent} → leader: {outcome}"
                    + (f" | reason: {reason}" if reason else "")
                    + (" | → 已批准：可以开始执行" if req.status == RequestStatus.APPROVED
                       else " | → 被拒绝：请修改计划后重新 submit_plan")
                )
            elif req.req_type == "shutdown" and req.from_agent == "leader":
                resp = req.response_payload
                outcome = "approved ✅" if req.status == RequestStatus.APPROVED else "rejected ❌"
                reason = resp.get("reason", "") if resp else ""
                parts.append(
                    f"[{req.req_id}] type=shutdown from={req.from_agent} → {req.to_agent}: {outcome}"
                    + (f" | reason: {reason}" if reason else "")
                )

    if not parts:
        return

    # 替换旧的 pending-requests 块，避免多轮重复堆积
    messages[:] = [
        m for m in messages
        if not (
            m.get("role") == "user"
            and isinstance(m.get("content"), str)
            and m["content"].lstrip().startswith("<pending-requests>")
        )
    ]
    messages.append({"role": "user", "content": "\n".join(["<pending-requests>"] + parts + ["</pending-requests>"])})
    logger.info(f"inject_pending_requests | {agent_id} | 注入 {len(parts)} 条协议请求")