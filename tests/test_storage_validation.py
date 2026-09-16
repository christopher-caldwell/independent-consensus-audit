import json
from pathlib import Path

from consensus_audit.storage import RunBundle, load_bundle


def test_sealed_artifact_mutation_is_detected(tmp_path: Path) -> None:
    bundle = RunBundle(tmp_path / "run", "run-1")
    artifact = bundle.publish("reports/one.json", b"{}\n", "accepted-report")
    bundle.commit_manifest()
    artifact.write_text('{"changed": true}\n')
    assert load_bundle(bundle.root).verify() == ["digest mismatch: reports/one.json"]
