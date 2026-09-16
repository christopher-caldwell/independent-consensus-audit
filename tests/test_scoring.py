import pytest

from consensus_audit.contracts import Reconciliation
from consensus_audit.scoring import score, score_discovery_consensus


def reconciliation(*, level="direct", assessments=2, basis="bounded_claim", issues=None,
                   coverage="supported", decisive=False, result_kind="supported") -> Reconciliation:
    assessment_refs = [f"report-{i}:c1" for i in range(assessments)]
    data = {
        "answer": {"statement": "Scoped answer", "result_kind": result_kind, "scope": "narrow",
                   "answer_basis": basis, "decisive_claim_ids": [] if result_kind == "inconclusive" else ["cc1"],
                   "answer_sections": ["## Direction\n\nAct on the scoped finding."], "next_action": "Verify locally."},
        "canonical_claims": [{"id": "cc1", "statement": "Claim", "scope": "narrow", "origin_claim_ids": ["report-0:c1"],
            "report_relations": [{"report_id": "report-0", "relation": "supports", "evidence_refs": ["report-0:c1"]}], "relation_evidence_refs": ["report-0:c1"], "disposition": "supported",
            "support_assessment": {"level": level, "supporting_reference_ids": ["report-0:c1"], "applicability_rationale": "Applicable",
                "counterevidence_handling": "None material", "separated_assessment_refs": assessment_refs,
                "decisive_observation_refs": ["event:1"] if decisive else [], "decisive_author_actor": "report-0" if decisive else None,
                "non_author_check_ref": "report-1:c1" if decisive else None}, "affected_questions": ["q"],
            "contrary_evidence_handling": "None", "assumption_handling": "None"}],
        "candidate_dispositions": [{"source_claim_id": "report-0:c1", "disposition": "merged into cc1"}],
        "coverage": [] if coverage is None else [{"id": "cov1", "requirement_or_question": "q", "source_refs": ["task"],
            "disposition": coverage, "evidence_refs": ["report-0:c1"], "rationale": "Recorded"}],
        "issues": issues or [], "follow_up_proposals": [], "stop_reason": "Enough evidence",
    }
    return Reconciliation.model_validate(data)


@pytest.mark.parametrize("level,assessments,expected", [("asserted", 5, 25), ("indirect", 3, 50), ("direct", 1, 70), ("direct", 2, 85)])
def test_required_tiers(level: str, assessments: int, expected: int) -> None:
    assert score(reconciliation(level=level, assessments=assessments), requested=5, completed=5, independence="user_attested").final_score == expected


def test_decisive_counterexample_can_reach_95() -> None:
    assert score(reconciliation(decisive=True, basis="counterexample"), requested=5, completed=1, independence="user_attested").final_score == 95


def test_material_objection_caps_at_50() -> None:
    issue = {"id": "i1", "source_candidate_or_question_refs": ["cc1"], "question_or_objection": "Alternative remains",
             "relevance_to_requested_answer": "Could invalidate it", "state": "open", "resolution_evidence_refs": [],
             "rationale": "Unresolved", "material_to_answer": True}
    assert score(reconciliation(issues=[issue]), requested=5, completed=5, independence="user_attested").final_score == 50


def test_three_of_five_broad_answer_caps_at_70() -> None:
    assert score(reconciliation(basis="synthesis"), requested=5, completed=3, independence="user_attested").final_score == 70


def test_positive_conformance_gap_caps_at_50() -> None:
    assert score(reconciliation(basis="broad_conformance", coverage="unresolved"), requested=5, completed=5, independence="user_attested").final_score == 50


def test_unknown_import_independence_cannot_promote_by_multiplicity() -> None:
    assert score(reconciliation(), requested=3, completed=3, independence="unknown").final_score == 70


def test_inconclusive_is_zero() -> None:
    assert score(reconciliation(result_kind="inconclusive"), requested=5, completed=5, independence="user_attested").final_score == 0


def discovery_reconciliation(relations: list[str], issues=None) -> Reconciliation:
    value = reconciliation(issues=issues)
    data = value.model_dump()
    report_relations = []
    origin_claim_ids = []
    dispositions = []
    for index, relation in enumerate(relations, 1):
        report_id = f"input-{index:02d}"
        claim_id = f"{report_id}:c1"
        report_relations.append({
            "report_id": report_id, "relation": relation,
            "evidence_refs": [] if relation == "not_observed" else [claim_id],
        })
        origin_claim_ids.append(claim_id)
        dispositions.append({"source_claim_id": claim_id, "disposition": "accounted for"})
    data["canonical_claims"][0]["origin_claim_ids"] = origin_claim_ids
    data["canonical_claims"][0]["report_relations"] = report_relations
    data["candidate_dispositions"] = dispositions
    return Reconciliation.model_validate(data)


def test_discovery_consensus_scores_verified_opinion_agreement() -> None:
    recon = discovery_reconciliation(["supports", "supports", "supports"])
    report_ids = {f"input-{index:02d}" for index in range(1, 4)}
    unknown = score_discovery_consensus(recon, requested=3, completed=3, independence="unknown", report_ids=report_ids)
    attested = score_discovery_consensus(recon, requested=3, completed=3, independence="user_attested", report_ids=report_ids)
    assert unknown.final_score == 70 and unknown.policy_id == "discovery-consensus-v1"
    assert attested.final_score == 85


def test_discovery_consensus_preserves_material_disagreement() -> None:
    recon = discovery_reconciliation(["supports", "supports", "contradicts"])
    report_ids = {f"input-{index:02d}" for index in range(1, 4)}
    result = score_discovery_consensus(recon, requested=3, completed=3, independence="user_attested", report_ids=report_ids)
    assert result.final_score == 50
