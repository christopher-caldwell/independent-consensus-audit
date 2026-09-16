import json
import hashlib
from copy import deepcopy
from pathlib import Path

import pytest

from consensus_audit.application import run_audit
from consensus_audit.runners.base import InvocationResult


REPORT = {
    "summary": "A report", "answer_candidate": "Choose the compatible narrow design.", "scope_reviewed": ["document"],
    "checks": [{"local_id": "k1", "requirement_or_question": "Does it fit?", "normative_source_ref": None,
                "status": "supported", "claim_refs": ["c1"], "evidence_refs": [], "rationale": "The document says so."}],
    "claims": [{"local_id": "c1", "statement": "Use the narrow design", "kind": "recommendation", "scope": "implementation",
                "source_refs": [{"artifact_id": "input", "locator": "lines 1-2", "brief_relation_to_claim": "explicit recommendation"}],
                "evidence_refs": [], "assumption_refs": [], "contrary_evidence_refs": [], "why_it_matters": "It is actionable."}],
    "assumptions": [], "open_questions": [], "limitations": ["Historical execution was not observed."], "unparsed_sections": []}


class ScriptedRunner:
    def __init__(self): self.extract = 0; self.calls = []
    def preflight(self, workspace): return {"passed": True, "fixture": True}
    def invoke(self, **kwargs):
        self.calls.append(kwargs["role"])
        if kwargs["role"] == "extractor":
            self.extract += 1; return InvocationResult(REPORT, 0, b"{}\n", metadata={"fixture": True})
        recon = {
            "answer": {"statement": "Adopt the shared narrow design and preserve the unique supported constraint.", "result_kind": "supported",
                "scope": "supplied implementation direction", "answer_basis": "synthesis", "decisive_claim_ids": ["cc1"],
                "answer_sections": ["## Selected design\n\nUse the narrow design.\n\n## Acceptance criteria\n\nThe constraint remains testable."],
                "next_action": "Implement the selected design and its acceptance criterion."},
            "canonical_claims": [{"id": "cc1", "statement": "Use the narrow design", "scope": "implementation",
                "origin_claim_ids": ["input-01:c1", "input-02:c1", "input-03:c1"],
                "report_relations": [{"report_id": f"input-0{i}", "relation": "supports", "evidence_refs": [f"input-0{i}:c1"]} for i in range(1,4)],
                "relation_evidence_refs": ["input-01:c1", "input-02:c1"], "disposition": "supported",
                "support_assessment": {"level": "direct", "supporting_reference_ids": ["input-01:c1"],
                    "applicability_rationale": "Directly addresses the supplied request", "counterevidence_handling": "No material conflict",
                    "separated_assessment_refs": ["input-01:c1", "input-02:c1", "input-03:c1"], "decisive_observation_refs": [],
                    "decisive_author_actor": None, "non_author_check_ref": None}, "affected_questions": ["direction"],
                "contrary_evidence_handling": "No contradiction", "assumption_handling": "Historical isolation is user-attested"}],
            "candidate_dispositions": [{"source_claim_id": f"input-0{i}:c1", "disposition": "merged into cc1"} for i in range(1,4)],
            "coverage": [{"id": "cov1", "requirement_or_question": "Produce actionable direction", "source_refs": ["task"],
                "disposition": "supported", "evidence_refs": ["cc1"], "rationale": "Direction and criteria are present."}],
            "issues": [], "follow_up_proposals": [], "stop_reason": "Material direction is settled"}
        return InvocationResult(recon, 0, b"{}\n", metadata={"fixture": True})


def make_discovery_run(root: Path, run_uuid: str, observation: str) -> Path:
    run = root / run_uuid
    export = run / "exports" / "export-1"
    artifact = run / "artifacts" / "sha256" / "evidence"
    export.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    artifact.write_text(observation, encoding="utf-8")
    artifact_bytes = artifact.read_bytes()
    (export / "technical-spec.md").write_text(f"# Result\n\n{observation}\n", encoding="utf-8")
    (export / "discovery-summary.md").write_text(observation, encoding="utf-8")
    (export / "handoff.json").write_text(json.dumps({"run_uuid": run_uuid, "final": True, "confidence": {"status": "current"}}), encoding="utf-8")
    (export / "evidence-manifest.json").write_text(json.dumps({
        "evidence": [{"evidence_id": 1, "evidence_kind": "empirical", "artifact_id": 1, "observation": observation}],
        "arguments": [{"argument_id": 1, "verification_status": "passed"}],
        "artifacts": [{
            "artifact_id": 1,
            "storage_path": "artifacts/sha256/evidence",
            "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
            "byte_size": len(artifact_bytes),
        }],
    }), encoding="utf-8")
    return run


def test_supplied_documents_produce_complete_bundle(tmp_path: Path) -> None:
    docs = []
    for name, text in (("codex.md", "Narrow design from Codex."), ("cursor.md", "Narrow design with constraint."), ("claude.md", "Claude selects the narrow design.")):
        path = tmp_path / name; path.write_text(text); docs.append(path)
    request = tmp_path / "audit.md"
    request.write_text("---\nschema_version: 1\nartifact: audit-request\ninputs:\n" + "".join(f"  - ./{p.name}\n" for p in docs) +
                       "input_independence: user_attested\noutput_dir: ./runs\n---\n\nProduce one actionable direction.\n")
    runner = ScriptedRunner(); run_dir = run_audit(request, runner)
    manifest = json.loads((run_dir / "manifest.json").read_text()); score = json.loads((run_dir / "score.json").read_text())
    assert manifest["status"] == "completed" and score["final_score"] == 85
    final = (run_dir / "final.md").read_text()
    assert "Adopt the shared narrow design" in final and "## Acceptance criteria" in final
    assert runner.calls == ["extractor", "extractor", "extractor", "reconciler"]


def test_duplicate_import_is_alias_not_vote(tmp_path: Path) -> None:
    doc = tmp_path / "one.md"; doc.write_text("same")
    alias = tmp_path / "two.md"; alias.write_text("same")
    request = tmp_path / "audit.md"
    request.write_text("---\nschema_version: 1\nartifact: audit-request\ninputs: [./one.md, ./two.md]\noutput_dir: ./runs\n---\nTask\n")
    runner = ScriptedRunner()
    # The scripted reconciliation expects three reports; prove acquisition dedupe before it reaches reconciliation.
    try: run_audit(request, runner)
    except Exception: pass
    assert runner.calls.count("extractor") == 1


def test_reconciler_retries_after_semantic_integrity_rejection(tmp_path: Path) -> None:
    docs = []
    for index, name in enumerate(("one.md", "two.md", "three.md"), 1):
        path = tmp_path / name
        path.write_text(f"Report {index}: use the narrow design.")
        docs.append(path)
    request = tmp_path / "audit.md"
    request.write_text(
        "---\nschema_version: 1\nartifact: audit-request\ninputs:\n"
        + "".join(f"  - ./{path.name}\n" for path in docs)
        + "output_dir: ./runs\n---\n\nProduce one actionable direction.\n"
    )
    runner = ScriptedRunner()
    normal_invoke = runner.invoke
    rejected_once = False

    def invoke(**kwargs):
        nonlocal rejected_once
        result = normal_invoke(**kwargs)
        if kwargs["role"] == "reconciler" and not rejected_once:
            rejected_once = True
            invalid = deepcopy(result.payload)
            invalid["canonical_claims"][0]["synthesis_inference"] = True
            return InvocationResult(invalid, 0, b"{}\n", metadata={"fixture": True})
        return result

    runner.invoke = invoke
    run_dir = run_audit(request, runner)

    assert (run_dir / "final.md").is_file()
    assert runner.calls.count("reconciler") == 2
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
    rejected = [event for event in events if event["event_type"] == "invocation_failed"]
    assert rejected[0]["attempt_id"] == 1
    assert "cannot fabricate original claim votes" in rejected[0]["error"]


def test_discovery_runs_retain_provenance_without_adding_votes(tmp_path: Path) -> None:
    runs = [make_discovery_run(tmp_path, f"00000000-0000-0000-0000-00000000000{index}", f"Observation {index}") for index in range(1, 4)]
    renamed = tmp_path / "external-run-identifier"
    runs[0].rename(renamed)
    runs[0] = renamed
    # Underlying run artifacts are outside the consensus boundary, even when the export references them.
    (runs[1] / "artifacts/sha256/evidence").write_text("changed after finalization", encoding="utf-8")
    request = tmp_path / "audit.md"
    request.write_text(
        "---\nschema_version: 1\nartifact: audit-request\ndiscovery_runs:\n"
        + "".join(f"  - ./{run.name}\n" for run in runs)
        + "output_dir: ./runs\n---\n\nProduce one direction and report agreement.\n"
    )
    runner = ScriptedRunner()
    run_dir = run_audit(request, runner)

    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert runner.calls == ["extractor", "extractor", "extractor", "reconciler"]
    assert manifest["cohorts"]["initial"]["requested_or_supplied"] == 3
    assert len(manifest["imports"]) == 3
    assert all(item["import_type"] == "discovery_run" and item["retained_outputs"] == 4 for item in manifest["imports"])
    assert (run_dir / "originals/input-01/handoff.json").is_file()
    assert (run_dir / "originals/input-01/evidence-manifest.json").is_file()
    assert not (run_dir / "originals/input-01/artifacts").exists()
    final = (run_dir / "final.md").read_text()
    assert "## Discovery report agreement" in final
    assert "3 of 3 support" in final
    assert "Consensus confidence:** 70/100 (`discovery-consensus-v1`" in final
    assert "12 retained output artifacts; underlying run artifacts were not imported" in final


@pytest.mark.parametrize("invalid_kind", ["rejected", "minority"])
def test_discovery_reconciler_retries_when_decisive_claim_is_not_consensus(tmp_path: Path, invalid_kind: str) -> None:
    runs = [make_discovery_run(tmp_path, f"00000000-0000-0000-0000-00000000000{index}", f"Observation {index}") for index in range(1, 4)]
    request = tmp_path / "audit.md"
    request.write_text(
        "---\nschema_version: 1\nartifact: audit-request\ndiscovery_runs:\n"
        + "".join(f"  - ./{run.name}\n" for run in runs)
        + "output_dir: ./runs\n---\n\nProduce one direction and report agreement.\n"
    )
    runner = ScriptedRunner()
    normal_invoke = runner.invoke
    rejected_once = False

    def invoke(**kwargs):
        nonlocal rejected_once
        result = normal_invoke(**kwargs)
        if kwargs["role"] == "reconciler" and not rejected_once:
            rejected_once = True
            invalid = deepcopy(result.payload)
            if invalid_kind == "rejected":
                invalid["canonical_claims"][0]["disposition"] = "rejected"
            else:
                invalid["canonical_claims"][0]["report_relations"][1]["relation"] = "related"
                invalid["canonical_claims"][0]["report_relations"][2]["relation"] = "related"
            return InvocationResult(invalid, 0, b"{}\n", metadata={"fixture": True})
        return result

    runner.invoke = invoke
    run_dir = run_audit(request, runner)

    assert (run_dir / "final.md").is_file()
    assert runner.calls.count("reconciler") == 2
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
    rejected = [event for event in events if event["event_type"] == "invocation_failed"]
    expected = "must be supported" if invalid_kind == "rejected" else "lacks strict majority support"
    assert expected in rejected[0]["error"]


def test_discovery_run_must_be_finalized(tmp_path: Path) -> None:
    run = make_discovery_run(tmp_path, "00000000-0000-0000-0000-000000000001", "Observed")
    handoff = run / "exports/export-1/handoff.json"
    handoff.write_text(json.dumps({"run_uuid": run.name, "final": False}), encoding="utf-8")
    request = tmp_path / "audit.md"
    request.write_text(
        f"---\nschema_version: 1\nartifact: audit-request\ndiscovery_runs: [./{run.name}]\noutput_dir: ./runs\n---\nTask\n"
    )
    runner = ScriptedRunner()
    try:
        run_audit(request, runner)
    except ValueError as exc:
        assert "not finalized" in str(exc)
    else:
        raise AssertionError("non-final Discovery output was accepted")
    assert runner.calls == []
