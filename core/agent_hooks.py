# -*- coding: utf-8 -*-
"""Pre-step hook infrastructure (lightweight port of dsh agent/pre-step waterfall).

Plugins/agents can register callables that run before every model request.
Each hook receives the mutable messages list and can inject/replace context.
"""
from datetime import datetime, timezone
import os

from .tools_tasks import task_manager, todo_manager

REPEAT_TOOL_THRESHOLD = int(os.environ.get("DSH_REPEAT_TOOL_THRESHOLD", "5"))

PRE_STEP_HOOKS = []
POST_STEP_HOOKS = []
REQUEST_ERROR_HOOKS = []


def register_pre_step_hook(fn):
    """Register a hook fn(messages) -> None. Returns fn for decorator use."""
    PRE_STEP_HOOKS.append(fn)
    return fn


def register_post_step_hook(fn):
    """Register a hook fn(messages, tool_counts) -> None, run after a step/tool round."""
    POST_STEP_HOOKS.append(fn)
    return fn


def register_request_error_hook(fn):
    """Register a hook fn(exc, messages) -> list[str] | None (extra user messages to inject)."""
    REQUEST_ERROR_HOOKS.append(fn)
    return fn


def run_pre_step_hooks(messages):
    """Run all registered pre-step hooks in order."""
    for fn in PRE_STEP_HOOKS:
        try:
            fn(messages)
        except Exception:
            continue


def run_post_step_hooks(messages, tool_counts):
    """Run all registered post-step hooks in order."""
    for fn in POST_STEP_HOOKS:
        try:
            fn(messages, tool_counts)
        except Exception:
            continue


def run_request_error_hooks(exc, messages):
    """Run all registered request-error hooks; collect extra user messages to inject."""
    extra = []
    for fn in REQUEST_ERROR_HOOKS:
        try:
            out = fn(exc, messages)
            if out:
                extra.extend(out)
        except Exception:
            continue
    return extra


def _replace_runtime_slot(messages, tag_prefix, content):
    """Replace ephemeral runtime-context messages of a given tag prefix."""
    messages[:] = [
        m for m in messages
        if not (
            m.get("role") == "user"
            and isinstance(m.get("content"), str)
            and m["content"].lstrip().startswith(f"<{tag_prefix}")
        )
    ]
    messages.append({"role": "user", "content": content})


@register_post_step_hook
def _repeat_tool_reminder(messages, tool_counts):
    """Advisory reminder when a single step repeats the same tool too many times."""
    too_many = [(name, cnt) for name, cnt in tool_counts.items() if cnt >= REPEAT_TOOL_THRESHOLD]
    if too_many:
        details = ", ".join(f"{name} x{cnt}" for name, cnt in too_many)
        from . import config as _config
        if getattr(_config, "MODE", "chat") == "mod":
            advice = "请先写/改一个文件，或换个工具，不要继续重复同一操作。"
        else:
            # chat 只读模式：不能催模型"写文件"，读文件/搜索本来就是正常工作流
            advice = "请换个角度或工具；信息足够时直接用文字回答用户。"
        _replace_runtime_slot(
            messages,
            "reminder",
            f"<reminder>同一轮内重复调用工具过多：{details}。{advice}</reminder>",
        )


@register_pre_step_hook
def _inject_runtime_context_snapshot(messages):
    """Inject a single replaceable <runtime-context> snapshot of time/todo/task state."""
    parts = []
    try:
        parts.append("Current time (UTC): " + datetime.now(timezone.utc).isoformat(timespec="seconds"))
        if todo_manager.todos:
            parts.append("Todo progress:\n" + todo_manager.render())
        tasks = task_manager.list_tasks()
        if tasks:
            parts.append("Task board:\n" + "\n".join(
                f"- #{t.get('id')} [{t.get('status', '?')}] {t.get('subject', '')[:80]}"
                for t in tasks
            ))
    except Exception:
        return
    if parts:
        _replace_runtime_slot(
            messages,
            "runtime-context",
            "Current runtime context. This snapshot supersedes earlier runtime-context snapshots.\n\n"
            + "\n\n".join(parts),
        )