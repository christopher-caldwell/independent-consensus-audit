from __future__ import annotations

from .contracts import InvestigatorReport, Reconciliation


class IntegrityError(ValueError):
    pass


def validate_report(report: InvestigatorReport) -> None:
    claim_ids = [c.local_id for c in report.claims]
    check_ids = [c.local_id for c in report.checks]
    if len(claim_ids) != len(set(claim_ids)) or len(check_ids) != len(set(check_ids)):
        raise IntegrityError("report-local IDs must be unique")
    for check in report.checks:
        missing = set(check.claim_refs) - set(claim_ids)
        if missing:
            raise IntegrityError(f"check {check.local_id} references missing claims: {sorted(missing)}")


def validate_reconciliation(value: Reconciliation, source_claim_ids: set[str], report_ids: set[str], prior_issue_ids: set[str] | None = None) -> None:
    canonical = {c.id for c in value.canonical_claims}
    if len(canonical) != len(value.canonical_claims):
        raise IntegrityError("canonical claim IDs must be unique")
    missing_decisive = set(value.answer.decisive_claim_ids) - canonical
    if missing_decisive:
        raise IntegrityError(f"answer references missing decisive claims: {sorted(missing_decisive)}")
    disposition_ids = [item.source_claim_id for item in value.candidate_dispositions]
    if len(disposition_ids) != len(set(disposition_ids)):
        raise IntegrityError("candidate dispositions must be unique per source claim")
    missing_dispositions = source_claim_ids - set(disposition_ids)
    if missing_dispositions:
        raise IntegrityError(f"source claims lack dispositions: {sorted(missing_dispositions)}")
    for claim in value.canonical_claims:
        if set(claim.origin_claim_ids) - source_claim_ids:
            raise IntegrityError(f"canonical claim {claim.id} has unknown origin claims")
        if {relation.report_id for relation in claim.report_relations} - report_ids:
            raise IntegrityError(f"canonical claim {claim.id} has unknown report relations")
        for relation in claim.report_relations:
            if relation.relation != "not_observed" and not relation.evidence_refs:
                raise IntegrityError(f"canonical claim {claim.id} has an unsupported {relation.relation} relation")
        if claim.synthesis_inference and claim.origin_claim_ids:
            raise IntegrityError("synthesis inference cannot fabricate original claim votes")
    issue_ids = {issue.id for issue in value.issues}
    if prior_issue_ids and prior_issue_ids - issue_ids:
        raise IntegrityError(f"prior issues disappeared without disposition: {sorted(prior_issue_ids - issue_ids)}")
    parents = canonical | issue_ids
    for proposal in value.follow_up_proposals:
        if not proposal.parent_issue_or_claim_refs or set(proposal.parent_issue_or_claim_refs) - parents:
            raise IntegrityError(f"follow-up {proposal.id} has invalid parent references")
