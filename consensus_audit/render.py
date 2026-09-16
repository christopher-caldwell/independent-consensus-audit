from __future__ import annotations

from .contracts import InvestigatorReport, Reconciliation, ScoreResult


def render_report(run_id: str, report_id: str, role: str, round_no: int, report: InvestigatorReport) -> str:
    lines = ["---", "schema_version: 1", "artifact: reviewer-report", f"run_id: {run_id}",
             f"report_id: {report_id}", f"role: {role}", f"round: {round_no}", "status: complete", "---", "",
             f"# {report.summary}", "", report.answer_candidate, "", "## Claims", ""]
    for claim in report.claims:
        lines += [f"### {claim.local_id}", "", claim.statement, "", f"Scope: {claim.scope}", "", claim.why_it_matters, ""]
    if report.limitations:
        lines += ["## Limitations", ""] + [f"- {item}" for item in report.limitations] + [""]
    return "\n".join(lines)


def render_final(run_id: str, status: str, recon: Reconciliation, score: ScoreResult,
                 requested: int, completed: int, failed: int, limitations: list[str], source_summary: str,
                 workflow: str = "standard") -> str:
    lines = ["---", "schema_version: 1", "artifact: final-report", f"run_id: {run_id}", f"status: {status}",
             f"result_kind: {recon.answer.result_kind}", f"confidence: {score.final_score}",
             f"confidence_policy: {score.policy_id}", "confidence_calibrated: false", "---", "", "# Independent Consensus Audit", "",
             "## Answer", "", recon.answer.statement, "", f"**Scope:** {recon.answer.scope}", "",
             f"**{'Consensus' if workflow == 'discovery' else 'Audit'} confidence:** {score.final_score}/100 (`{score.policy_id}`, uncalibrated).", "",
             _score_reason(score), "", "## What to do next", "", recon.answer.next_action, ""]
    for section in recon.answer.answer_sections:
        lines += [section.strip(), ""]
    if workflow == "discovery":
        lines += ["## Discovery report agreement", "",
                  "Agreement counts describe report positions, not evidentiary confidence.", ""]
        claims = {c.id: c for c in recon.canonical_claims}
        for claim_id in recon.answer.decisive_claim_ids:
            claim = claims[claim_id]
            relations = [relation for relation in claim.report_relations if relation.report_id.startswith("input-")]
            counts = {
                name: sum(relation.relation == name for relation in relations)
                for name in ("supports", "contradicts", "related", "not_observed")
            }
            missing = max(0, completed - len({relation.report_id for relation in relations}))
            lines += [
                f"- **{claim.id}:** {counts['supports']} of {completed} support; "
                f"{counts['contradicts']} contradict; {counts['related']} related; "
                f"{counts['not_observed'] + missing} did not observe. {claim.statement}"
            ]
        lines.append("")
    lines += ["## Decisive evidence", ""]
    claims = {c.id: c for c in recon.canonical_claims}
    for claim_id in recon.answer.decisive_claim_ids:
        claim = claims[claim_id]
        lines += [f"- **{claim.id}:** {claim.statement} ({claim.support_assessment.level} support; scope: {claim.scope})"]
    lines += ["", "## Independent assessment accounting", "",
              f"- Original slots requested or supplied: {requested}", f"- Valid completed original reports: {completed}",
              f"- Failed, missing, or excluded original reports: {failed}", "- Follow-up assessments are recorded separately and are not added to the original denominator.", ""]
    if recon.issues:
        lines += ["## Disagreements and open issues", ""]
        for issue in recon.issues:
            lines += [f"- **{issue.id} — {issue.state}:** {issue.question_or_objection} {issue.rationale}"]
        lines.append("")
    if recon.coverage:
        lines += ["## Coverage", ""]
        for item in recon.coverage:
            lines += [f"- **{item.id} — {item.disposition}:** {item.requirement_or_question} {item.rationale}"]
        lines.append("")
    all_limits = list(limitations)
    all_limits.extend(i.question_or_objection for i in recon.issues if i.state in {"open", "deferred"} and i.material_to_answer)
    if all_limits:
        lines += ["## Limitations", ""] + [f"- {item}" for item in dict.fromkeys(all_limits)] + [""]
    lines += ["## Audited sources", "", source_summary, "", "## Confidence basis", "",
              ("This score describes agreement among finalized, verified Discovery opinions for the stated answer and scope; it does not re-verify their underlying evidence."
               if workflow == "discovery" else
               "This is an audit-confidence score for the stated answer and scope, not a probability or software certification."),
              f"The same validated record and `{score.policy_id}` policy replay deterministically; another model run may produce a different semantic record.", ""]
    return "\n".join(lines)


def _score_reason(score: ScoreResult) -> str:
    if score.final_score == 0:
        return "No substantive candidate survived with adequate support; the result is intentionally inconclusive."
    tiers = [v["granted_tier"] for v in score.per_claim.values()]
    reasons = [f"the weakest of {len(tiers)} essential claim(s) received tier {min(tiers)}"]
    if score.caps:
        reasons.append("applicable caps: " + "; ".join(c["reason"] for c in score.caps))
    return "The score reflects " + ", and ".join(reasons) + "."


def render_diagnostic(run_id: str, status: str, message: str) -> str:
    return f"---\nschema_version: 1\nartifact: diagnostic-report\nrun_id: {run_id}\nstatus: {status}\nconfidence: null\n---\n\n# Audit could not be finalized\n\n{message}\n"
