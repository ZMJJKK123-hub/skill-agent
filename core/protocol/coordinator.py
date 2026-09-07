# -*- coding: utf-8 -*-
"""团队协调器：关机握手 + 计划审批（两种协议一个 FSM）。
由 protocol.py 原样迁出。
"""
import threading

#: [PROTOCOL] 前缀：MessageBus 里标记协议消息，不走普通任务 Agent Loop
PROTOCOL_FLAG = "[PROTOCOL]"

from ..config import logger
from .tracker import ProtocolRequest, ProtocolTracker, RequestStatus

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


