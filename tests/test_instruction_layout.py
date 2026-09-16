from pathlib import Path

from consensus_audit.cli import main


ROOT = Path(__file__).parents[1]


def test_packaged_guide_matches_the_shared_source() -> None:
    shared = (ROOT / "AGENT_GUIDE.md").read_text(encoding="utf-8")
    packaged = (ROOT / "consensus_audit/prompts/host-guide.md").read_text(encoding="utf-8")
    assert packaged == shared


def test_host_entries_do_not_duplicate_the_audit_workflow() -> None:
    entries = (
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / ".cursor/rules/independent-consensus-audit.mdc",
    )
    workflow_markers = ("schema_version", "input_independence", "pilot-v1", "reviewers: 5")
    for entry in entries:
        text = entry.read_text(encoding="utf-8")
        assert "AGENT_GUIDE.md" in text
        assert "agent-installation.md" in text
        assert "every installed host" in text
        assert not any(marker in text for marker in workflow_markers)


def test_shared_guide_contains_no_host_install_destinations() -> None:
    shared = (ROOT / "AGENT_GUIDE.md").read_text(encoding="utf-8")
    assert "~/.codex" not in shared
    assert "~/.agents" not in shared
    assert "~/.claude" not in shared
    assert "~/.cursor" not in shared


def test_guide_command_prints_the_shared_source_exactly(capsys) -> None:
    assert main(["guide"]) == 0
    assert capsys.readouterr().out == (ROOT / "AGENT_GUIDE.md").read_text(encoding="utf-8")


def test_installed_loader_routes_updates_to_one_reference() -> None:
    skill = ROOT / "skills/independent-consensus-audit"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "references/update.md" in text
    assert (skill / "references/update.md").is_file()
