import json
import subprocess

from consensus_audit.contracts import InvestigatorReport
from consensus_audit.runners.codex import CodexRunner


def test_output_schema_requires_every_property_for_strict_runner_format() -> None:
    schema = CodexRunner._strict_schema(InvestigatorReport.model_json_schema())
    assert set(schema["required"]) == set(schema["properties"])
    check = schema["$defs"]["Check"]
    assert set(check["required"]) == set(check["properties"])
    assert check["additionalProperties"] is False


def test_invoke_allows_generated_non_git_workspace(monkeypatch, tmp_path) -> None:
    invocations: list[list[str]] = []

    monkeypatch.setattr("consensus_audit.runners.codex.shutil.which", lambda executable: f"/bin/{executable}")

    def fake_run(command, **kwargs):
        invocations.append(command)
        if command[-1] == "--version":
            return subprocess.CompletedProcess(command, 0, stdout="codex-cli test", stderr="")
        payload = json.dumps({"summary": "ok"})
        event = json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": payload}})
        return subprocess.CompletedProcess(command, 0, stdout=f"{event}\n".encode(), stderr=b"")

    monkeypatch.setattr("consensus_audit.runners.codex.subprocess.run", fake_run)

    runner = CodexRunner()
    result = runner.invoke(
        role="test",
        prompt="bounded packet",
        schema={"type": "object", "properties": {"summary": {"type": "string"}}},
        workspace=tmp_path,
        model=None,
        timeout=30,
        max_output_bytes=10_000,
    )

    command = invocations[-1]
    assert "--skip-git-repo-check" in command
    assert command[command.index("-C") + 1] == str(tmp_path)
    assert result.payload == {"summary": "ok"}
    assert result.error is None
