from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .base import InvocationResult


class CodexRunner:
    """Fresh no-tools Codex invocations over controller-embedded packets."""

    name = "codex"

    def __init__(self, executable: str = "codex"):
        located = shutil.which(executable)
        if not located:
            raise RuntimeError("Codex CLI is unavailable")
        self.executable = located
        version = subprocess.run([located, "--version"], text=True, capture_output=True, check=False)
        self.version = version.stdout.strip() or version.stderr.strip() or "unknown"

    @classmethod
    def _strict_schema(cls, value: Any) -> Any:
        if isinstance(value, dict):
            result = {key: cls._strict_schema(item) for key, item in value.items()}
            if result.get("type") == "object" and "properties" in result:
                result["required"] = list(result["properties"])
                result["additionalProperties"] = False
            return result
        if isinstance(value, list):
            return [cls._strict_schema(item) for item in value]
        return value

    def preflight(self, workspace: Path) -> dict[str, Any]:
        return {"passed": True, "runner": self.name, "runner_version": self.version,
                "boundary": "fresh ephemeral invocation; all model tool surfaces disabled; bounded packet embedded in prompt",
                "runtime_evidence_supported": False}

    def invoke(self, *, role: str, prompt: str, schema: dict[str, Any], workspace: Path,
               model: str | None, timeout: float, max_output_bytes: int) -> InvocationResult:
        schema_path = workspace / "output-schema.json"
        schema_path.write_text(json.dumps(self._strict_schema(schema)), encoding="utf-8")
        command = [self.executable, "exec", "--ephemeral", "--skip-git-repo-check",
                   "--ignore-user-config", "--ignore-rules", "--strict-config",
                   "--json", "--output-schema", str(schema_path), "--color", "never", "-C", str(workspace),
                   "-c", 'approval_policy="never"']
        for feature in ("shell_tool", "code_mode_host", "apps", "browser_use", "browser_use_external", "computer_use",
                        "multi_agent", "hooks", "plugins", "in_app_browser", "web_search_request", "standalone_web_search"):
            command.extend(["--disable", feature])
        if model: command.extend(["--model", model])
        started = time.monotonic()
        try:
            proc = subprocess.run(command, input=prompt.encode(), capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            return InvocationResult(None, 124, exc.stdout or b"", exc.stderr or b"", error="invocation timed out",
                                    metadata={"role": role, "runner": self.name, "duration_seconds": time.monotonic() - started,
                                              "runner_version": self.version})
        if len(proc.stdout) > max_output_bytes:
            return InvocationResult(None, proc.returncode, proc.stdout, proc.stderr, error="runner output exceeded configured byte ceiling")
        events, payload, errors = [], None, []
        for line in proc.stdout.splitlines():
            try:
                event = json.loads(line); events.append(event)
                item = event.get("item", {})
                if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                    try: payload = json.loads(item.get("text", ""))
                    except json.JSONDecodeError as exc: errors.append(str(exc))
            except json.JSONDecodeError as exc: errors.append(str(exc))
        error = None if proc.returncode == 0 and payload is not None else f"Codex returned no valid structured payload: {errors[-1:] or proc.returncode}"
        return InvocationResult(payload, proc.returncode, proc.stdout, proc.stderr, events, error=error,
                                metadata={"role": role, "runner": self.name, "duration_seconds": time.monotonic() - started,
                                          "runner_version": self.version, "argv": command, "effective_model": model or "unknown"})
