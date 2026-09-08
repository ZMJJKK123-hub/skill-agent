# -*- coding: utf-8 -*-
"""协议消息解析与 <pending-requests> 上下文注入。
由 protocol.py 原样迁出。
"""
from ..config import logger
from .coordinator import coordinator


# ---------- 协议消息与上下文注入 ----------
def parse_protocol_flag(content: str):
    """解析 [PROTOCOL] 前缀的协议消息，返回 (type, args) 或 None。"""
    if not content.startswith(PROTOCOL_FLAG):
        return None
    parts = content[len(PROTOCOL_FLAG):].strip().split()
    if not parts:
        return None
    return parts[0], parts[1:]


def _render_pending_requests(agent_id: str) -> list[str]:
    """渲染两类协议请求文本块（由 inject_pending_requests 拆出）。

    1. 发给该 agent 且仍 PENDING 的请求；2. 自己发起、已决议的请求。
    Globals Used: coordinator.tracker / RequestStatus。
    """
    parts = []
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
    return parts


def inject_pending_requests(messages: list, agent_id: str) -> None:
    """把需要该 agent 注意的协议请求以 <pending-requests> 标签注入。

    让模型明确区分这是协议事件，而非用户输入或工具结果。

    注入两类：
    1. 发给该 agent 且仍 PENDING 的请求（leader 需要审批 plan；队友需要处理 shutdown）
    2. 该 agent 发起、已决议的 plan 请求（队友看到自己的审批结果）
    """
    parts = _render_pending_requests(agent_id)
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