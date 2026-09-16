from pathlib import Path

import pytest

from consensus_audit.request import RequestError, parse_request


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8"); return path


def test_relative_paths_resolve_from_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "request-dir"; folder.mkdir(); (folder / "target").mkdir()
    request = write(folder / "audit.md", "---\nschema_version: 1\nartifact: audit-request\ntarget: ./target\n---\n\nCheck it.\n")
    elsewhere = tmp_path / "elsewhere"; elsewhere.mkdir(); monkeypatch.chdir(elsewhere)
    parsed = parse_request(request)
    assert parsed.target == (folder / "target").resolve()
    assert parsed.output_dir == (folder / "audits").resolve()


@pytest.mark.parametrize("frontmatter, phrase", [
    ("schema_version: 1\nschema_version: 1\nartifact: audit-request", "duplicate"),
    ("schema_version: 1\nartifact: audit-request\ninputs: []", "nonempty"),
    ("schema_version: 1\nartifact: audit-request\ninputs: [a.md]\nreviewers: 5", "not applicable"),
    ("schema_version: 1\nartifact: audit-request\nquorum_threshold: 0.6", "legacy"),
    ("schema_version: 1\nartifact: audit-request\nunknown: yes", "Extra inputs"),
])
def test_strict_frontmatter(tmp_path: Path, frontmatter: str, phrase: str) -> None:
    request = write(tmp_path / "audit.md", f"---\n{frontmatter}\n---\nTask\n")
    with pytest.raises(RequestError, match=phrase): parse_request(request)


def test_debug_false_string(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEBUG", "false")
    request = write(tmp_path / "audit.md", "---\nschema_version: 1\nartifact: audit-request\n---\nTask\n")
    assert parse_request(request).debug is False
