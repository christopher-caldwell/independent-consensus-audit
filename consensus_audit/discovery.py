from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .storage import RunBundle, canonical_digest, sha256_file


REQUIRED_EXPORT_FILES = (
    "technical-spec.md",
    "discovery-summary.md",
    "handoff.json",
    "evidence-manifest.json",
)


@dataclass(frozen=True)
class DiscoveryImport:
    run_root: Path
    export_root: Path
    run_uuid: str
    digest: str
    files: tuple[tuple[str, Path, str, int], ...]
    handoff: dict[str, Any]
    evidence_manifest: dict[str, Any]

    @property
    def total_bytes(self) -> int:
        return sum(size for _, _, _, size in self.files)


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Discovery JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Discovery JSON artifact must contain an object: {path}")
    return value


def _resolve_roots(path: Path) -> tuple[Path, Path]:
    supplied = path.resolve()
    if not supplied.is_dir():
        raise ValueError(f"Discovery run does not exist or is not a directory: {supplied}")
    if all((supplied / name).is_file() for name in REQUIRED_EXPORT_FILES):
        if supplied.parent.name != "exports":
            raise ValueError(f"Discovery export is not inside a run exports directory: {supplied}")
        return supplied.parent.parent, supplied
    exports = supplied / "exports"
    candidates = [] if not exports.is_dir() else [
        item for item in sorted(exports.iterdir())
        if item.is_dir() and all((item / name).is_file() for name in REQUIRED_EXPORT_FILES)
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"Discovery run must contain exactly one complete export; found {len(candidates)} in {exports}"
        )
    return supplied, candidates[0]


def inspect_discovery_run(path: Path, max_bytes: int) -> DiscoveryImport:
    run_root, export_root = _resolve_roots(path)
    handoff = _read_object(export_root / "handoff.json")
    evidence_manifest = _read_object(export_root / "evidence-manifest.json")
    run_uuid = handoff.get("run_uuid")
    if not isinstance(run_uuid, str) or not run_uuid:
        raise ValueError(f"Discovery handoff has no run_uuid: {export_root / 'handoff.json'}")
    if handoff.get("final") is not True:
        raise ValueError(f"Discovery handoff is not finalized: {export_root / 'handoff.json'}")

    files: list[tuple[str, Path, str, int]] = []
    for name in REQUIRED_EXPORT_FILES:
        source = export_root / name
        files.append((name, source, sha256_file(source), source.stat().st_size))

    total = sum(size for _, _, _, size in files)
    if total > max_bytes:
        raise ValueError(f"Discovery output packet exceeds {max_bytes} bytes: {export_root} ({total} bytes)")
    digest = canonical_digest({"run_uuid": run_uuid, "files": [(relative, sha) for relative, _, sha, _ in files]})
    return DiscoveryImport(run_root, export_root, run_uuid, digest, tuple(files), handoff, evidence_manifest)


def retain_discovery_run(bundle: RunBundle, import_id: str, item: DiscoveryImport) -> Path:
    prefix = f"originals/{import_id}"
    for relative, source, _, _ in item.files:
        bundle.publish(f"{prefix}/{relative}", source.read_bytes(), "discovery-output")
    return bundle.root / prefix
