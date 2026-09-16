from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .storage import sha256_file


EXCLUDED_NAMES = {".git", ".venv", "node_modules", "target", "dist", "build", "__pycache__", ".pytest_cache"}


def _git_metadata(target: Path) -> dict:
    try:
        top = subprocess.run(["git", "-C", str(target), "rev-parse", "--show-toplevel"], text=True, capture_output=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return {"git": False}
    def run(*args: str) -> str:
        return subprocess.run(["git", "-C", top, *args], text=True, capture_output=True, check=False).stdout.strip()
    return {"git": True, "root": top, "head": run("rev-parse", "HEAD"),
            "branch": run("branch", "--show-current") or None, "dirty": bool(run("status", "--porcelain")),
            "status_porcelain": run("status", "--porcelain=v1")}


def freeze_sources(targets: list[tuple[str, Path]], destination: Path, excluded: set[Path], max_bytes: int) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    entries, exclusions, total = [], [], 0
    excluded = {p.resolve() for p in excluded}
    for artifact_id, source in targets:
        source = source.resolve()
        if not source.exists():
            raise ValueError(f"source does not exist: {source}")
        files = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.is_file() or p.is_symlink())
        base = source.parent if source.is_file() else source
        for item in files:
            resolved = item.resolve()
            relative = item.relative_to(base)
            if any(part in EXCLUDED_NAMES for part in relative.parts) or any(resolved == blocked or blocked in resolved.parents for blocked in excluded):
                exclusions.append({"path": str(item), "reason": "excluded source/control path"})
                continue
            if item.is_symlink():
                raise ValueError(f"symlink source is rejected to prevent escape: {item}")
            data_size = item.stat().st_size
            total += data_size
            if total > max_bytes:
                raise ValueError(f"source packet exceeds {max_bytes} bytes")
            out = destination / artifact_id / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, out, follow_symlinks=False)
            entries.append({"artifact_id": artifact_id, "source_path": str(item), "snapshot_path": str(out.relative_to(destination)),
                            "bytes": data_size, "sha256": sha256_file(out)})
    manifest = {"entries": entries, "exclusions": exclusions, "git_targets": {a: _git_metadata(p) for a, p in targets}}
    return manifest


def snapshot_changed(manifest: dict) -> list[str]:
    changed = []
    for entry in manifest["entries"]:
        path = Path(entry["source_path"])
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            changed.append(entry["source_path"])
    return changed
