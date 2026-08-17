# -*- coding: utf-8 -*-
"""validate_resources: deterministic MOD resource loading validator for MC 1.21.11+ Forge."""
import json
import os
import re
from pathlib import Path

from .config import logger
from .tools_runtime import worktree_manager

_RESOURCE_ROOT_NAMES = ("assets", "data")


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _resource_root(base: str) -> Path | None:
    """Return src/main/resources if present, otherwise base (some templates put assets at root)."""
    p = Path(base) / "src" / "main" / "resources"
    return p if p.is_dir() else Path(base)


def _find_modid(base: str) -> str | None:
    """Auto-detect mod id from mods.toml / neoforge.mods.toml / @Mod annotation."""
    root = _resource_root(base)
    for name in ("META-INF/mods.toml", "META-INF/neoforge.mods.toml"):
        f = root / name
        if f.exists():
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                m = re.search(r'modId\s*=\s*"([^"]+)"', text)
                if m:
                    return m.group(1).strip()
            except OSError:
                pass
    # Fallback: search Java files for @Mod("...")
    java_root = Path(base) / "src" / "main" / "java"
    if java_root.is_dir():
        for f in java_root.rglob("*.java"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            m = re.search(r'@Mod\s*\(\s*"([^"]+)"\s*\)', text)
            if m:
                return m.group(1).strip()
    return None


def _load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def _check_model_ref(base: Path, ref: str, modid: str, errors: list, path: Path) -> None:
    """ref like 'modid:item/foo' -> assets/modid/models/item/foo.json"""
    if ":" not in ref:
        return
    ns, _, p = ref.partition(":")
    if not p:
        return
    # Only validate the current mod's own references; other namespaces (minecraft/deps) may live outside workspace.
    if ns != modid:
        return
    if p.endswith(".json") or p.endswith(".png"):
        errors.append(f"{path}: model/texture reference must NOT include extension: {ref}")
    target = base / "assets" / ns / "models" / f"{p}.json"
    if not target.is_file():
        errors.append(f"{path}: model not found for '{ref}' -> expected {target.relative_to(base)}")


def _check_texture_ref(base: Path, ref: str, modid: str, errors: list, path: Path) -> None:
    """ref like 'modid:item/foo' -> assets/modid/textures/item/foo.png"""
    if ":" not in ref:
        return
    ns, _, p = ref.partition(":")
    if not p:
        return
    if ns != modid:
        return
    if p.endswith(".json") or p.endswith(".png"):
        errors.append(f"{path}: texture reference must NOT include extension: {ref}")
    target = base / "assets" / ns / "textures" / f"{p}.png"
    if not target.is_file():
        errors.append(f"{path}: texture not found for '{ref}' -> expected {target.relative_to(base)}")


def _validate_json_file(base: Path, rel: Path, modid: str, errors: list, warnings: list) -> None:
    data, err = _load_json(base / rel)
    if err:
        errors.append(f"{rel}: invalid JSON -> {err}")
        return
    rel_str = rel.as_posix()
    parts = rel.parts

    # Item model definition: assets/<modid>/items/<name>.json
    if "assets" in parts and "items" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        model = (data or {}).get("model")
        if isinstance(model, dict):
            ref = model.get("model")
            if ref:
                _check_model_ref(base, ref, modid, errors, rel)

    # Model JSON: assets/<modid>/models/...
    if "assets" in parts and "models" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        parent = (data or {}).get("parent")
        if isinstance(parent, str) and ":" in parent:
            _check_model_ref(base, parent, modid, errors, rel)
        textures = (data or {}).get("textures")
        if isinstance(textures, dict):
            for key, val in textures.items():
                if isinstance(val, str) and ":" in val:
                    _check_texture_ref(base, val, modid, errors, rel)

    # Blockstate JSON: assets/<modid>/blockstates/<name>.json
    if "assets" in parts and "blockstates" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        variants = (data or {}).get("variants")
        if isinstance(variants, dict):
            for state, v in variants.items():
                if isinstance(v, dict) and isinstance(v.get("model"), str):
                    _check_model_ref(base, v["model"], modid, errors, rel)
                elif isinstance(v, list):
                    for entry in v:
                        if isinstance(entry, dict) and isinstance(entry.get("model"), str):
                            _check_model_ref(base, entry["model"], modid, errors, rel)
        multipart = (data or {}).get("multipart")
        if isinstance(multipart, list):
            for part in multipart:
                if isinstance(part, dict) and isinstance(part.get("apply"), dict):
                    apply = part["apply"]
                    if isinstance(apply.get("model"), str):
                        _check_model_ref(base, apply["model"], modid, errors, rel)

    # Recipe JSON: data/<modid>/recipe/<name>.json
    if "data" in parts and "recipe" in parts and len(parts) >= 4 and parts[parts.index("data") + 1] == modid:
        result = (data or {}).get("result")
        if isinstance(result, dict):
            rid = result.get("id")
            if isinstance(rid, str) and ":" in rid:
                ns = rid.split(":", 1)[0]
                if ns != modid:
                    warnings.append(f"{rel}: result id namespace '{ns}' does not match modid '{modid}'")
        ingredients = (data or {}).get("ingredients")
        if isinstance(ingredients, list):
            for ing in ingredients:
                if isinstance(ing, dict):
                    warnings.append(f"{rel}: ingredient should be a plain string in MC 1.21.11+, got {ing}")

    # Generic: flag accidental .json/.png in common resource location string values
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, str) and ("/" in val or ":" in val):
                if val.endswith(".json") or val.endswith(".png"):
                    # Only warn; some fields legitimately contain file names (e.g. logoFile)
                    warnings.append(f"{rel}: value '{key}' ends with .json/.png; check if it should be a resource location without extension")


def _item_definitions_exist(base: Path, modid: str, warnings: list) -> None:
    """Every models/item/<name>.json should have a matching assets/<modid>/items/<name>.json."""
    items_dir = base / "assets" / modid / "items"
    models_item_dir = base / "assets" / modid / "models" / "item"
    if not models_item_dir.is_dir():
        return
    for model_file in sorted(models_item_dir.glob("*.json")):
        name = model_file.stem
        if not (items_dir / f"{name}.json").is_file():
            warnings.append(f"assets/{modid}/models/item/{name}.json has no matching assets/{modid}/items/{name}.json (inventory icon may be missing)")


def _blockstates_exist(base: Path, modid: str, warnings: list) -> None:
    """Every models/block/<name>.json should have a matching blockstate (unless intentionally a sub-model)."""
    models_block_dir = base / "assets" / modid / "models" / "block"
    blockstates_dir = base / "assets" / modid / "blockstates"
    if not models_block_dir.is_dir():
        return
    for model_file in sorted(models_block_dir.glob("*.json")):
        name = model_file.stem
        if not (blockstates_dir / f"{name}.json").is_file():
            warnings.append(f"assets/{modid}/models/block/{name}.json has no matching blockstate; if this is a sub-model you can ignore this warning")


def validate_resources(modid: str = None) -> str:
    """Validate all MOD resource JSON/PNG references under the current workspace."""
    base = Path(_base_dir())
    root = _resource_root(str(base))
    if not root.is_dir():
        return "Error: resource root not found (expected src/main/resources or current dir)"
    if not modid:
        modid = _find_modid(str(base))
    if not modid:
        return "Error: cannot auto-detect modid; pass modid parameter or fix mods.toml/@Mod"

    errors: list = []
    warnings: list = []
    checked = 0

    for rel in sorted(root.rglob("*.json")):
        # Skip build/generated runtime dirs
        if any(part in (".gradle", "build", "run", ".git") for part in rel.relative_to(root).parts):
            continue
        checked += 1
        _validate_json_file(root, rel.relative_to(root), modid, errors, warnings)

    _item_definitions_exist(root, modid, warnings)
    _blockstates_exist(root, modid, warnings)

    # Texture existence is already checked from model refs; also list missing common textures quickly
    lines = [f"Resource validation for modid='{modid}' | checked {checked} JSON files"]
    lines.append(f"ERRORS: {len(errors)}")
    for e in errors[:100]:
        lines.append(f"  [ERROR] {e}")
    if len(errors) > 100:
        lines.append(f"  ... and {len(errors) - 100} more errors")
    lines.append(f"WARNINGS: {len(warnings)}")
    for w in warnings[:100]:
        lines.append(f"  [WARN] {w}")
    if len(warnings) > 100:
        lines.append(f"  ... and {len(warnings) - 100} more warnings")
    if not errors and not warnings:
        lines.append("RESULT: OK")
    elif not errors:
        lines.append("RESULT: PASS (warnings only)")
    else:
        lines.append("RESULT: FAIL")
    return "\n".join(lines)
