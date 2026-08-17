# -*- coding: utf-8 -*-
"""Git checkpoint/rollback tools for self-looping MOD development."""
import os
import subprocess

from .tools_runtime import worktree_manager


def _base_dir():
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _run_git(args, workdir):
    try:
        p = subprocess.run(
            ["git"] + args,
            cwd=workdir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        out = (p.stdout or "") + (p.stderr or "")
        if p.returncode != 0:
            return f"[git] exit={p.returncode}\n{out.strip()}"
        return out.strip() or "(empty)"
    except Exception as e:
        return f"[git] failed: {e}"


def git_status(workdir=None):
    workdir = workdir or _base_dir()
    return _run_git(["status", "--short"], workdir)


def git_diff(workdir=None, stat=True):
    workdir = workdir or _base_dir()
    args = ["diff", "--stat" if stat else ""]
    args = [a for a in args if a]
    return _run_git(args, workdir)


def git_commit(message, workdir=None, files=None, push=False):
    workdir = workdir or _base_dir()
    if not message or not str(message).strip():
        return "Error: git_commit requires a non-empty message"
    if files:
        if isinstance(files, str):
            files = [files]
        add = ["add", "--"] + [str(f) for f in files]
    else:
        add = ["add", "-A"]
    add_out = _run_git(add, workdir)
    commit_out = _run_git(["commit", "-m", str(message).strip()], workdir)
    if push:
        push_out = _run_git(["push"], workdir)
        return f"add: {add_out}\ncommit: {commit_out}\npush: {push_out}"
    return f"add: {add_out}\ncommit: {commit_out}"


def snapshot(name="checkpoint", workdir=None, message=None):
    """Create a git checkpoint commit; returns the commit hash."""
    workdir = workdir or _base_dir()
    if not name or not str(name).strip():
        name = "checkpoint"
    msg = message or f"snapshot: {name}"
    add_out = _run_git(["add", "-A"], workdir)
    commit_out = _run_git(["commit", "-m", msg], workdir)
    rev = _run_git(["rev-parse", "--short", "HEAD"], workdir)
    return f"{add_out}\n{commit_out}\nHEAD={rev}"


def restore_snapshot(ref, workdir=None):
    """Hard-reset to a snapshot/commit. Destructive: discards uncommitted changes."""
    workdir = workdir or _base_dir()
    if not ref or not str(ref).strip():
        return "Error: restore_snapshot requires ref (commit hash/branch/tag)"
    return _run_git(["reset", "--hard", str(ref).strip()], workdir)