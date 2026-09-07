# -*- coding: utf-8 -*-
"""请求追踪器：pending → approved | rejected 共享状态机 + 磁盘持久化。
由 protocol.py 原样迁出。
"""
import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..config import logger


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


