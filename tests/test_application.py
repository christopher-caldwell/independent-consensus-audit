import json
from pathlib import Path

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
