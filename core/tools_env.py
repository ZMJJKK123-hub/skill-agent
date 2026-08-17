# -*- coding: utf-8 -*-
"""detect_environment: report Java/Gradle/MC/Forge workspace facts."""
import os
import re
import subprocess
from pathlib import Path

from .tools_runtime import worktree_manager
from .tools_validate import _find_modid


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _run(cmd: list, timeout: int = 10) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        out = (p.stdout or "").strip()
        return out[:500] or f"(exit {p.returncode})"
    except Exception as e:
        return f"(error: {e})"


def detect_environment() -> str:
    base = Path(_base_dir())
    lines = [f"Working directory: {base}"]

    # Java
    if os.name == "nt":
        java_ver = _run(["java", "-version"])
    else:
        java_ver = _run(["java", "-version"])
    lines.append(f"Java: {java_ver}")

    # Gradle wrapper
    has_gradlew = (base / "gradlew.bat").exists() or (base / "gradlew").exists()
    has_gradle = (base / "gradle").exists() or (base / "build.gradle").exists()
    lines.append(f"Gradle wrapper: {'yes' if has_gradlew else 'no'} | build.gradle: {'yes' if (base / 'build.gradle').exists() else 'no'}")

    # Mod loader / mod id
    modid = _find_modid(str(base))
    lines.append(f"Mod id: {modid or '(not detected)'}")
    has_forge = (base / "src/main/resources/META-INF/mods.toml").exists()
    has_neoforge = (base / "src/main/resources/META-INF/neoforge.mods.toml").exists()
    has_fabric = (base / "src/main/resources/fabric.mod.json").exists()
    loader = "neoforge" if has_neoforge else ("forge" if has_forge else ("fabric" if has_fabric else "unknown"))
    lines.append(f"Loader: {loader}")

    # MC/Forge version from build.gradle
    bg = base / "build.gradle"
    version = "(not found)"
    if bg.exists():
        try:
            text = bg.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"net\.minecraftforge:forge:([0-9][\w.-]+)", text)
            if m:
                version = m.group(1)
            else:
                m2 = re.search(r"minecraft\s*=\s*['\"]([^'\"]+)['\"]", text)
                if m2:
                    version = m2.group(1)
        except OSError:
            pass
    lines.append(f"MC/Forge version: {version}")

    # Source layout
    lines.append(f"src/main: {'yes' if (base / 'src/main').is_dir() else 'no'}")
    lines.append(f"src/test: {'yes' if (base / 'src/test').is_dir() else 'no'}")
    lines.append(f"mc_java_sources: {'yes' if (base / 'mc_java_sources').is_dir() else 'no'}")

    # Resource roots
    res = base / "src/main/resources"
    if res.is_dir():
        assets = sorted((res / "assets").glob("*")) if (res / "assets").is_dir() else []
        data = sorted((res / "data").glob("*")) if (res / "data").is_dir() else []
        lines.append(f"Resource assets namespaces: {', '.join(p.name for p in assets) or '(none)'}")
        lines.append(f"Resource data namespaces: {', '.join(p.name for p in data) or '(none)'}")

    return "\n".join(lines)
