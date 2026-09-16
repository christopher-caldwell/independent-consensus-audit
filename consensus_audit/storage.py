from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode())


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, sort_keys=True, default=str) + "\n").encode())


class RunBundle:
    def __init__(self, root: Path, run_id: str, create: bool = True):
        self.root = root
        self.run_id = run_id
        self.lock_path = root / ".controller.lock"
        self.manifest_path = root / "manifest.json"
        if create:
            root.mkdir(parents=True, exist_ok=False)
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, f"{os.getpid()}\n".encode())
            os.close(fd)
            self.manifest = {
                "schema_version": 1, "run_id": run_id, "status": "running",
                "created_at": utc_now(), "sequence": 0, "artifacts": {}, "cohorts": {},
            }
            self.commit_manifest()
        else:
            self.manifest = json.loads(self.manifest_path.read_text())

    def event(self, event_type: str, outcome: str, **details: Any) -> None:
        self.manifest["sequence"] += 1
        event = {"sequence": self.manifest["sequence"], "timestamp": utc_now(), "run_id": self.run_id,
                 "event_type": event_type, "outcome": outcome, **details}
        with (self.root / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True, default=str) + "\n")

    def publish(self, relative: str, data: bytes, kind: str) -> Path:
        path = self.root / relative
        atomic_bytes(path, data)
        self.manifest["artifacts"][relative] = {"sha256": sha256_bytes(data), "bytes": len(data), "kind": kind}
        return path

    def publish_json(self, relative: str, value: Any, kind: str) -> Path:
        return self.publish(relative, (json.dumps(value, indent=2, sort_keys=True, default=str) + "\n").encode(), kind)

    def verify(self) -> list[str]:
        problems = []
        for relative, recorded in self.manifest.get("artifacts", {}).items():
            path = self.root / relative
            if not path.is_file():
                problems.append(f"missing artifact: {relative}")
            elif sha256_file(path) != recorded["sha256"]:
                problems.append(f"digest mismatch: {relative}")
        return problems

    def commit_manifest(self) -> None:
        atomic_json(self.manifest_path, self.manifest)

    def finalize(self, status: str) -> None:
        self.manifest["status"] = status
        self.manifest["completed_at"] = utc_now()
        self.commit_manifest()
        self.lock_path.unlink(missing_ok=True)


def load_bundle(path: Path) -> RunBundle:
    path = path.resolve()
    if not (path / "manifest.json").is_file():
        raise ValueError(f"not a run directory: {path}")
    return RunBundle(path, json.loads((path / "manifest.json").read_text())["run_id"], create=False)
