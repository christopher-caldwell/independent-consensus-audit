from pathlib import Path


def test_runtime_has_no_operating_system_branches_or_shell_paths() -> None:
    root = Path(__file__).parents[1] / "consensus_audit"
    text = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py"))
    forbidden = ("sys.platform", "platform.system", "platform.release", "/bin/sh", "sandbox-exec", "powershell.exe")
    assert not [marker for marker in forbidden if marker in text]
