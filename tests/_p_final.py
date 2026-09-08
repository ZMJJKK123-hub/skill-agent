# -*- coding: utf-8 -*-
"""一次性拆分：最后 10 个超标函数最小块提取（用后即删）。"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def patch(f, pairs):
    p = Path(f)
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (f, old[:70])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"patched {f}")


# 1) gametest：路径解析校验段提取
patch("core/infrastructure/tools/gametest.py", [
    ('''    base = _base_dir()
    base_resolved = Path(base).resolve()
    path = Path(log_path) if log_path else Path(base) / DEFAULT_LOG
    if not path.is_absolute():
        path = Path(base) / path
    if not path.resolve().is_relative_to(base_resolved):
        return f"Error: log_path 越出工作区: {path}"
    if not path.exists():
        return f"Error: GameTest log not found: {path}"
''',
     '''    path, err = _resolve_log_path(log_path)
    if err:
        return err
'''),
])
p = Path("core/infrastructure/tools/gametest.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "def parse_gametest_results(lines: int = 200, log_path: str = None) -> str:",
    '''def _resolve_log_path(log_path) -> tuple[Path, str | None]:
    """解析日志路径（默认 run/logs/latest.log；相对路径挂基座；沙箱校验）。

    Returns:
        (路径, 错误消息或 None)。
    """
    base = _base_dir()
    path = Path(log_path) if log_path else Path(base) / DEFAULT_LOG
    if not path.is_absolute():
        path = Path(base) / path
    if not path.resolve().is_relative_to(Path(base).resolve()):
        return path, f"Error: log_path 越出工作区: {path}"
    if not path.exists():
        return path, f"Error: GameTest log not found: {path}"
    return path, None


def parse_gametest_results(lines: int = 200, log_path: str = None) -> str:''', 1)
p.write_text(s, encoding="utf-8")
print("gametest helper added")

# 2) validate：两个资产分支提取
patch("core/infrastructure/tools/validate.py", [
    ('''    parts = rel.parts

    # Item model definition: assets/<modid>/items/<name>.json
    if "assets" in parts and "items" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        model = (data or {}).get("model")
        if isinstance(model, dict):
            ref = model.get("model")
            if ref:
                _check_model_ref(base, ref, modid, errors, rel)
''',
     '''    parts = rel.parts
    _validate_item_model_json(base, rel, parts, modid, data, errors)
'''),
])
p = Path("core/infrastructure/tools/validate.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "def _validate_json_file(base: Path, rel: Path, modid: str, errors: list, warnings: list) -> None:",
    '''def _validate_item_model_json(base: Path, rel: Path, parts, modid: str,
                               data, errors: list) -> None:
    """Item model 定义校验（assets/<modid>/items/*.json），由 _validate_json_file 拆出。"""
    if "assets" in parts and "items" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        model = (data or {}).get("model")
        if isinstance(model, dict):
            ref = model.get("model")
            if ref:
                _check_model_ref(base, ref, modid, errors, rel)


def _validate_json_file(base: Path, rel: Path, modid: str, errors: list, warnings: list) -> None:''', 1)
p.write_text(s, encoding="utf-8")
print("validate helper added")

# 3) stream_endpoint.stream_agent：result 读取判定段提取
patch("tsinghua agent server/stream_endpoint.py", [
    ('''            if result_file.exists():
                data = json.loads(result_file.read_text(encoding="utf-8-sig"))
                if data.get("error"):
                    raise RuntimeError(data["error"])
                final = data.get("text") or "(no response)"
                final = append_persona_guide(final, messages)
                append_conversation(session_id, messages, final)
                break
''',
     '''            if result_file.exists():
                final = _read_daemon_result(result_file, messages, session_id)
                break
'''),
])
p = Path("tsinghua agent server/stream_endpoint.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "def stream_agent(messages: list, session_id: str, base_url: str):",
    '''def _read_daemon_result(result_file, messages: list, session_id: str) -> str:
    """读 daemon 结果文件（错误转 RuntimeError；正文过人格指南后落历史）。"""
    data = json.loads(result_file.read_text(encoding="utf-8-sig"))
    if data.get("error"):
        raise RuntimeError(data["error"])
    final = data.get("text") or "(no response)"
    final = append_persona_guide(final, messages)
    append_conversation(session_id, messages, final)
    return final


def stream_agent(messages: list, session_id: str, base_url: str):''', 1)
p.write_text(s, encoding="utf-8")
print("stream helper added")

# 4) chat_endpoint：非流式 JSON 构造段提取
p = Path("tsinghua agent server/chat_endpoint.py")
s = p.read_text(encoding="utf-8")
print("chat tail preview:")
print(s[-700:])
