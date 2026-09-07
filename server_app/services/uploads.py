# -*- coding: utf-8 -*-
"""图片上传（server_app/services 层；原 _save_upload_images 迁移）。

前端 data URL 图片落盘 <session>/.chat/uploads/，文件名（非全路径）
写进对话历史——不泄漏服务器路径；前端经 /api/session/image 取回。
"""
from __future__ import annotations

import base64
import re
import time
from pathlib import Path

from fastapi import HTTPException

#: 上传约束（与前端 MAX_IMAGES_PER_MESSAGE 对齐）。
UPLOAD_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
MAX_IMAGES = 4
MAX_BYTES = 12 * 1024 * 1024

#: data URL 格式（png/jpeg/webp/gif）。
DATAURL_RE = re.compile(r"^data:image/(png|jpe?g|webp|gif);base64,(.+)$", re.S)

#: MIME 子类型 → 落盘扩展名。
EXT_MAP = {"png": "png", "jpg": "jpg", "jpeg": "jpg",
           "webp": "webp", "gif": "gif"}


def valid_upload_name(name: str) -> bool:
    """输入：文件名。返回：是否合法上传名（防路径穿越）。"""
    return bool(UPLOAD_NAME_RE.match(name))


def save_upload_images(session_root: Path, images: list) -> list[str]:
    """把 data URL 图片列表落盘，返回文件名列表。

    Args:
        session_root: 会话根（.chat/uploads 所在）。
        images: data URL 字符串列表（≤4 张，超出截断）。
    Returns:
        落盘文件名列表（按序对应消息附件）。
    Raises:
        HTTPException: 格式不支持/解码失败/超大/写盘失败（400/500）。
    """
    names: list[str] = []
    if not images:
        return names
    uploads = session_root / ".chat" / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    ts = int(time.time() * 1000)
    for i, item in enumerate(images[:MAX_IMAGES]):
        if not isinstance(item, str):
            continue
        m = DATAURL_RE.match(item.strip())
        if not m:
            raise HTTPException(400, "图片格式不受支持（仅支持 png/jpeg/webp/gif）")
        try:
            data = base64.b64decode(m.group(2))
        except Exception:
            raise HTTPException(400, "图片数据解码失败")
        if len(data) > MAX_BYTES:
            raise HTTPException(400, "单张图片过大（>12MB），请压缩后重试")
        name = f"upload_{ts}_{i}.{EXT_MAP[m.group(1).lower()]}"
        try:
            (uploads / name).write_bytes(data)
        except OSError as e:
            raise HTTPException(500, f"图片保存失败: {e}")
        names.append(name)
    return names
