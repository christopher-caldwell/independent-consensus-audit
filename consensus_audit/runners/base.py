from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class InvocationResult:
    payload: dict[str, Any] | None
    returncode: int
    stdout: bytes = b""
    stderr: bytes = b""
    events: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Runner(Protocol):
    def preflight(self, workspace: Path) -> dict[str, Any]: ...
    def invoke(self, *, role: str, prompt: str, schema: dict[str, Any], workspace: Path,
               model: str | None, timeout: float, max_output_bytes: int) -> InvocationResult: ...
