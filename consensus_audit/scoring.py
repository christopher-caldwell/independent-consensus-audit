from __future__ import annotations

import hashlib
import json

from .contracts import Reconciliation, ScoreResult
from .storage import canonical_digest


POLICY_TEXT = "pilot-v1: tiers 0/25/50/70/85/95; minimum essential claim; material-objection and broad-coverage caps"
POLICY_DIGEST = hashlib.sha256(POLICY_TEXT.encode()).hexdigest()
DISCOVERY_POLICY_TEXT = (
    "discovery-consensus-v1: finalized Discovery exports are verified opinions; tiers reflect per-claim report agreement, "
    "minimum adopted strict-majority claim, material-disagreement and participation caps; no underlying evidence re-audit"
)
DISCOVERY_POLICY_DIGEST = hashlib.sha256(DISCOVERY_POLICY_TEXT.encode()).hexdigest()


def score(recon: Reconciliation, *, requested: int, completed: int, independence: str) -> ScoreResult:
    if recon.answer.result_kind == "inconclusive" or not recon.answer.decisive_claim_ids:
        return ScoreResult(policy_digest=POLICY_DIGEST, input_record_digest=canonical_digest(recon.model_dump()),
                           scope=recon.answer.scope, answer_basis=recon.answer.answer_basis,
                           essential_claim_ids=recon.answer.decisive_claim_ids, per_claim={}, caps=[], final_score=0)
    claims = {c.id: c for c in recon.canonical_claims}
    per_claim, caps = {}, []
    scores = []
    for claim_id in recon.answer.decisive_claim_ids:
        claim = claims[claim_id]
        assessment = claim.support_assessment
        base = {"none": 0, "asserted": 25, "indirect": 50, "direct": 70}[assessment.level]
        eligible_assessments = len(set(assessment.separated_assessment_refs))
        relevant_open = any(i.material_to_answer and i.state in {"open", "deferred"} and
                            (claim_id in i.source_candidate_or_question_refs or not i.source_candidate_or_question_refs)
                            for i in recon.issues)
        coverage_complete = all(c.disposition != "unresolved" for c in recon.coverage) if recon.coverage else False
        granted = base
        if base == 70 and eligible_assessments >= 2 and not relevant_open and coverage_complete:
            granted = 85
        decisive = bool(assessment.decisive_observation_refs and assessment.decisive_author_actor and assessment.non_author_check_ref)
        if granted == 85 and decisive and recon.answer.answer_basis in {"bounded_claim", "counterexample"}:
            granted = 95
        if relevant_open and granted > 50:
            granted = 50
            caps.append({"claim_id": claim_id, "cap": 50, "reason": "unresolved material objection or assumption"})
        if independence == "unknown" and eligible_assessments >= 2 and granted > 70:
            granted = 70
            caps.append({"claim_id": claim_id, "cap": 70, "reason": "historical independence is unknown"})
        per_claim[claim_id] = {"support_level": assessment.level, "base_tier": base, "separated_assessments": eligible_assessments,
                               "decisive_demonstration": decisive, "granted_tier": granted}
        scores.append(granted)
    result = min(scores)
    if recon.answer.answer_basis == "broad_conformance" and any(c.disposition == "unresolved" for c in recon.coverage):
        result = min(result, 50); caps.append({"cap": 50, "reason": "incomplete recorded coverage for broad conformance"})
    if requested > completed and recon.answer.answer_basis not in {"counterexample", "bounded_claim"}:
        result = min(result, 70); caps.append({"cap": 70, "reason": f"only {completed} of {requested} requested initial reports completed"})
    return ScoreResult(policy_digest=POLICY_DIGEST, input_record_digest=canonical_digest(recon.model_dump()),
                       scope=recon.answer.scope, answer_basis=recon.answer.answer_basis,
                       essential_claim_ids=recon.answer.decisive_claim_ids, per_claim=per_claim, caps=caps, final_score=result)


def score_discovery_consensus(recon: Reconciliation, *, requested: int, completed: int,
                              independence: str, report_ids: set[str]) -> ScoreResult:
    if recon.answer.result_kind == "inconclusive" or not recon.answer.decisive_claim_ids:
        return ScoreResult(
            policy_id="discovery-consensus-v1", policy_digest=DISCOVERY_POLICY_DIGEST,
            input_record_digest=canonical_digest(recon.model_dump()), scope=recon.answer.scope,
            answer_basis=recon.answer.answer_basis, essential_claim_ids=recon.answer.decisive_claim_ids,
            per_claim={}, caps=[], final_score=0,
        )
    claims = {claim.id: claim for claim in recon.canonical_claims}
    per_claim: dict[str, dict] = {}
    caps: list[dict] = []
    scores: list[int] = []
    for claim_id in recon.answer.decisive_claim_ids:
        claim = claims[claim_id]
        relations = {relation.report_id: relation.relation for relation in claim.report_relations if relation.report_id in report_ids}
        supports = sum(relation == "supports" for relation in relations.values())
        contradicts = sum(relation == "contradicts" for relation in relations.values())
        related = sum(relation == "related" for relation in relations.values())
        not_observed = completed - supports - contradicts - related
        unanimous = completed > 0 and supports == completed
        majority = supports > completed / 2
        if unanimous and completed >= 3:
            granted = 85
        elif unanimous or (majority and contradicts == 0):
            granted = 70
        elif majority:
            granted = 50
        elif supports:
            granted = 25
        else:
            granted = 0
        relevant_open = any(
            issue.material_to_answer and issue.state in {"open", "deferred"}
            and (claim_id in issue.source_candidate_or_question_refs or not issue.source_candidate_or_question_refs)
            for issue in recon.issues
        )
        if relevant_open and granted > 50:
            granted = 50
            caps.append({"claim_id": claim_id, "cap": 50, "reason": "unresolved material disagreement"})
        if independence == "unknown" and granted > 70:
            granted = 70
            caps.append({"claim_id": claim_id, "cap": 70, "reason": "historical independence is unknown"})
        per_claim[claim_id] = {
            "support_level": "verified_opinion_consensus",
            "supports": supports,
            "contradicts": contradicts,
            "related": related,
            "not_observed": not_observed,
            "completed_reports": completed,
            "granted_tier": granted,
        }
        scores.append(granted)
    result = min(scores)
    if requested > completed and result > 50:
        result = 50
        caps.append({"cap": 50, "reason": f"only {completed} of {requested} requested Discovery opinions completed"})
    return ScoreResult(
        policy_id="discovery-consensus-v1", policy_digest=DISCOVERY_POLICY_DIGEST,
        input_record_digest=canonical_digest(recon.model_dump()), scope=recon.answer.scope,
        answer_basis=recon.answer.answer_basis, essential_claim_ids=recon.answer.decisive_claim_ids,
        per_claim=per_claim, caps=caps, final_score=result,
    )
