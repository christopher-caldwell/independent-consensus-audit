from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Limits(StrictModel):
    max_follow_up_rounds: int = Field(default=2, ge=0, le=5)
    max_follow_up_questions: int = Field(default=3, ge=0, le=12)
    follow_up_reviewers: int = Field(default=2, ge=1, le=5)
    max_concurrency: int = Field(default=3, ge=1, le=10)
    max_attempts_per_slot: int = Field(default=2, ge=1, le=3)
    agent_timeout_seconds: int = Field(default=600, ge=10, le=3600)
    run_timeout_seconds: int = Field(default=2400, ge=30, le=14400)
    max_role_output_bytes: int = Field(default=2 * 1024 * 1024, ge=1024, le=8 * 1024 * 1024)
    max_diagnostic_bytes: int = Field(default=16 * 1024 * 1024, ge=1024, le=128 * 1024 * 1024)
    max_input_bytes: int = Field(default=8 * 1024 * 1024, ge=1024, le=64 * 1024 * 1024)


class AuditRequest(StrictModel):
    schema_version: Literal[1]
    artifact: Literal["audit-request"]
    target: Path | None = None
    spec: Path | None = None
    sources: list[Path] = Field(default_factory=list)
    inputs: list[Path] | None = None
    discovery_runs: list[Path] | None = None
    reviewers: int | None = Field(default=None, ge=1, le=10)
    input_independence: Literal["unknown", "user_attested"] = "unknown"
    output_dir: Path | None = None
    runner: Literal["codex"] = "codex"
    model: str | None = None
    debug: bool | None = None
    limits: Limits = Field(default_factory=Limits)
    task: str
    request_path: Path

    @model_validator(mode="after")
    def workflow_rules(self) -> "AuditRequest":
        if not self.task.strip():
            raise ValueError("Markdown task body must be nonempty")
        if self.inputs is not None and self.discovery_runs is not None:
            raise ValueError("inputs and discovery_runs are mutually exclusive")
        if self.discovery_runs is not None and (self.target is not None or self.spec is not None or self.sources):
            raise ValueError("target, spec, and sources are not applicable with discovery_runs")
        supplied = self.inputs if self.inputs is not None else self.discovery_runs
        if supplied is not None:
            if not supplied:
                name = "inputs" if self.inputs is not None else "discovery_runs"
                raise ValueError(f"{name} must be a nonempty list")
            if self.reviewers is not None:
                raise ValueError("reviewers is not applicable when supplied reports are used")
        if self.target is None and supplied is None:
            self.target = self.request_path.parent
        if self.reviewers is None and supplied is None:
            self.reviewers = 5
        return self


class Ref(StrictModel):
    artifact_id: str
    locator: str
    brief_relation_to_claim: str


class Check(StrictModel):
    local_id: str
    requirement_or_question: str
    normative_source_ref: Ref | None = None
    status: Literal["supported", "violated", "unresolved", "not_applicable"]
    claim_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[Ref] = Field(default_factory=list)
    rationale: str


class Claim(StrictModel):
    local_id: str
    statement: str
    kind: Literal["observation", "interpretation", "defect", "recommendation"]
    scope: str
    source_refs: list[Ref] = Field(default_factory=list)
    evidence_refs: list[Ref] = Field(default_factory=list)
    assumption_refs: list[str] = Field(default_factory=list)
    contrary_evidence_refs: list[Ref] = Field(default_factory=list)
    why_it_matters: str


class InvestigatorReport(StrictModel):
    summary: str
    answer_candidate: str
    scope_reviewed: list[str]
    checks: list[Check]
    claims: list[Claim]
    assumptions: list[str]
    open_questions: list[str]
    limitations: list[str]
    unparsed_sections: list[str] = Field(default_factory=list)


class SupportAssessment(StrictModel):
    level: Literal["none", "asserted", "indirect", "direct"]
    supporting_reference_ids: list[str] = Field(default_factory=list)
    applicability_rationale: str
    counterevidence_handling: str
    separated_assessment_refs: list[str] = Field(default_factory=list)
    decisive_observation_refs: list[str] = Field(default_factory=list)
    decisive_author_actor: str | None = None
    non_author_check_ref: str | None = None


class ReportRelation(StrictModel):
    report_id: str
    relation: Literal["supports", "contradicts", "related", "not_observed"]
    evidence_refs: list[str] = Field(default_factory=list)


class CanonicalClaim(StrictModel):
    id: str
    statement: str
    scope: str
    origin_claim_ids: list[str]
    report_relations: list[ReportRelation]
    relation_evidence_refs: list[str] = Field(default_factory=list)
    disposition: Literal["supported", "rejected", "unresolved"]
    support_assessment: SupportAssessment
    affected_questions: list[str]
    contrary_evidence_handling: str
    assumption_handling: str
    synthesis_inference: bool = False
    premise_claim_ids: list[str] = Field(default_factory=list)


class Issue(StrictModel):
    id: str
    source_candidate_or_question_refs: list[str]
    question_or_objection: str
    relevance_to_requested_answer: str
    state: Literal["open", "resolved", "out_of_scope", "deferred"]
    resolution_evidence_refs: list[str] = Field(default_factory=list)
    rationale: str
    material_to_answer: bool


class FollowUpProposal(StrictModel):
    id: str
    parent_issue_or_claim_refs: list[str]
    neutral_question: str
    permitted_source_refs: list[str]
    what_observation_would_change_the_answer: str
    why_existing_evidence_does_not_settle_it: str


class CoverageItem(StrictModel):
    id: str
    requirement_or_question: str
    source_refs: list[str]
    disposition: Literal["supported", "violated", "unresolved", "not_applicable"]
    evidence_refs: list[str]
    rationale: str


class Answer(StrictModel):
    statement: str
    result_kind: Literal["supported", "tentative", "inconclusive"]
    scope: str
    answer_basis: Literal["bounded_claim", "broad_conformance", "counterexample", "synthesis"]
    decisive_claim_ids: list[str]
    answer_sections: list[str]
    next_action: str


class CandidateDisposition(StrictModel):
    source_claim_id: str
    disposition: str


class Reconciliation(StrictModel):
    answer: Answer
    canonical_claims: list[CanonicalClaim]
    candidate_dispositions: list[CandidateDisposition]
    coverage: list[CoverageItem]
    issues: list[Issue]
    follow_up_proposals: list[FollowUpProposal]
    stop_reason: str


class ScoreResult(StrictModel):
    policy_id: Literal["pilot-v1", "discovery-consensus-v1"] = "pilot-v1"
    policy_digest: str
    input_record_digest: str
    calibrated: Literal[False] = False
    scope: str
    answer_basis: str
    essential_claim_ids: list[str]
    per_claim: dict[str, dict]
    caps: list[dict]
    final_score: int
