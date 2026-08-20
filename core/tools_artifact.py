# -*- coding: utf-8 -*-
"""verify_artifact: inspect built jars and source zips for required entries."""
import os
import zipfile
from pathlib import Path

from .tools_runtime import worktree_manager


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _inspect_jar(path: Path) -> list:
    out = []
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            out.append(f"Jar: {path} ({path.stat().st_size} bytes, {len(names)} entries)")
            checks = {
                "META-INF/mods.toml": "Forge mod metadata",
                "META-INF/neoforge.mods.toml": "NeoForge mod metadata",
                "fabric.mod.json": "Fabric mod metadata",
                "pack.mcmeta": "Resource pack metadata",
            }
            for entry, label in checks.items():
                out.append(f"  {'OK' if entry in names else 'MISSING'} {label}: {entry}")
            assets = sorted(n for n in names if n.startswith("assets/"))
            data = sorted(n for n in names if n.startswith("data/"))
            out.append(f"  assets entries: {len(assets)} | data entries: {len(data)}")
            if assets:
                out.append("  first assets entries: " + ", ".join(assets[:5]))
            if data:
                out.append("  first data entries: " + ", ".join(data[:5]))
    except Exception as e:
        out.append(f"Jar inspect failed: {e}")
    return out


def verify_artifact(jar_path: str = None) -> str:
    """Verify the latest built jar (and source zip) contains expected metadata/resources."""
    base = Path(_base_dir())
    lines = []

    dist = base / "dist"
    jars = []
    if jar_path:
        p = Path(jar_path)
        if p.is_absolute():
            if not p.resolve().is_relative_to(base.resolve()):
                return "Error: jar_path 越出工作区"
            if p.exists():
                jars = [p]
        elif (base / jar_path).exists():
            jars = [base / jar_path]
    elif dist.is_dir():
        jars = sorted(dist.glob("*.jar"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not jars:
        lines.append("No jar found in dist/ (or given path). Build may not have succeeded.")
    else:
        for j in jars[:3]:
            lines.extend(_inspect_jar(j))

    zip_path = base.parent / "mod.zip"
    if zip_path.exists():
        try:
            with zipfile.ZipFile(zip_path) as zf:
                names = set(zf.namelist())
                bad = [n for n in names if n.startswith(("build/", "dist/", ".git/", "mc_java_sources/"))]
                lines.append(f"Source zip: {zip_path} ({zip_path.stat().st_size} bytes, {len(names)} entries)")
                lines.append(f"  forbidden runtime dirs included: {len(bad)} {'(bad)' if bad else '(OK)'}")
                if bad:
                    lines.append("  examples: " + ", ".join(bad[:5]))
        except Exception as e:
            lines.append(f"Source zip inspect failed: {e}")
    else:
        lines.append("Source zip not found (may not have been pre-generated).")

    return "\n".join(lines)
