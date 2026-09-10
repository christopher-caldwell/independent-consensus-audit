---
name: independent-consensus-audit
description: Runs isolated independent audits and root-only evidence-aware synthesis that separates reviewer convergence, evidence, contradiction, verification, and impact.
---

# Independent Consensus Audit

## Purpose

Use this skill when a user wants multiple independent reviews of the same target followed by root-level synthesis.

The skill is appropriate for code, security, architecture, documents, policy, research, product, UX, and other audits where independent judgment can expose blind spots.

The synthesis must keep five questions separate:

1. **Independence:** Did reviewers work without seeing peer output?
2. **Convergence:** How often did comparable reviewers independently identify the same assertion?
3. **Evidence:** What concrete support exists, and does it come from distinct provenance roots?
4. **Contradiction:** Is there credible counter-evidence or an unresolved defeater?
5. **Impact:** How severe would the issue be if the assertion is true?

**Consensus is not verification.** Convergence describes reproducibility of an observation. It does not establish truth by itself.

## Non-Negotiable Independence

A reviewer must not:

- read another reviewer's Markdown or structured findings;
- list or inspect the shared audit output directory except to write its assigned files;
- communicate or coordinate with peers;
- receive peer findings, partial consensus, or root synthesis notes;
- revise conclusions to match expected consensus.

The root is the only agent allowed to read all reviewer artifacts.

The root must not read any reviewer output until every requested reviewer has reached a terminal state: completed, failed, or explicitly excluded.

## Default Configuration

```yaml
audit_target: "<infer from user request>"
audit_type: "general_audit"
reviewer_count: 5
reviewer_mode: "identical_reviewers"
convergence_threshold: 0.60
output_directory: "./audits"
individual_report_pattern: "reviewer-{number}.md"
individual_findings_pattern: "reviewer-{number}.findings.yaml"
final_report_filename: "final-consensus-audit.md"
```

`convergence_threshold` is descriptive only. Crossing it means an assertion recurred across independent reviews; it does not mean the assertion is accepted or verified. The default `0.60` is a reporting convention for grouping recurrence, not a statistically justified truth or probability threshold.

Use `identical_reviewers` by default. Use `focused_reviewers` only when the user explicitly asks for different lenses, specialists, or reviewer-specific focuses.

Resolve relative output paths against the active workspace or audit target root, never the installed skill directory.

### Legacy configuration

Treat `quorum_threshold` as a deprecated alias for `convergence_threshold`.

Do not use legacy `include_minority_findings` or `minority_severity_floor` as acceptance gates. Every distinct finding must be normalized. Severity may affect verification effort and remediation priority, but not epistemic credibility.

## Configurable Inputs

```yaml
audit_target: "<branch, diff, repo path, document, feature, system, or other target>"
audit_type: "<code_review | branch_review | security_audit | architecture_audit | document_audit | product_audit | general_audit | custom>"
reviewer_count: 5
reviewer_mode: "<identical_reviewers | focused_reviewers>"
convergence_threshold: 0.60
output_directory: "./audits"
individual_report_pattern: "reviewer-{number}.md"
individual_findings_pattern: "reviewer-{number}.findings.yaml"
final_report_filename: "final-consensus-audit.md"
allowed_materials:
  - "<target files, diff, docs, requirements, test output, issue description>"
disallowed_materials:
  - "./audits/reviewer-*.md"
  - "./audits/reviewer-*.findings.yaml"
  - "./audits/final-consensus-audit.md"
review_focuses:
  reviewer_01: general_quality
  reviewer_02: general_quality
  reviewer_03: general_quality
```

## Bundled Resources

- `templates/individual-reviewer-prompt.md`: reviewer isolation and Markdown format.
- `templates/reviewer-findings.schema.yaml`: structured reviewer companion.
- `templates/normalized-finding.schema.yaml`: root-level normalized finding.
- `templates/final-consensus-report-template.md`: final synthesis format.
- `checklists/root-synthesis-checklist.md`: root reconciliation checklist.
- `examples/*.config.yaml`: configuration examples.

Do not copy template placeholders into final reports.

## Reviewer Modes

### Identical Reviewers

Each reviewer receives the same target, criteria, focus, and allowed materials.

Detection rate is meaningful as recurrence across comparable assignments.

Context isolation does **not** imply statistically independent errors. Reviewers may still share a model, prompt, specification, source material, toolchain, or assumptions.

### Focused Reviewers

Use only when specialist lenses or broader coverage are explicitly requested.

Focused reviewers may report issues outside their assigned lens, but raw support percentages are normally not comparable because reviewers had different primary detection opportunities.

Record positions and contradictions. Mark convergence `not_comparable` unless a genuinely common denominator exists.

## Reviewer Output Contract

Each completed reviewer writes two durable artifacts:

```text
./audits/reviewer-01.md
./audits/reviewer-01.findings.yaml
```

The Markdown report is the human-readable forensic record. The YAML companion is a normalization aid and must represent the same findings, evidence, assumptions, and severities.

If the two conflict, root synthesis must inspect the discrepancy rather than silently trusting either.

Reviewer artifacts are provenance and must never be deleted automatically. Cleanup requires an explicit user request.

## Root Workflow

### 1. Plan

Before launching reviewers, define the target, type, reviewer count/mode/focus, descriptive convergence threshold, allowed/disallowed materials, both reviewer output paths, final report path, and known common-mode dependencies.

Create the output directory before launching reviewers so reviewers do not need to inspect or manage the shared directory.

### 2. Launch isolated reviewers

Use true isolated subagents when available.

If subagents are unavailable, emulate independence by running separate passes and writing both artifacts for each pass before reading, comparing, or synthesizing any prior pass.

Each reviewer receives only its target, criteria, focus, materials, assigned paths, reviewer prompt/schema, and independence rules.

### 3. Require terminal completion

A reviewer should not report successful completion until both assigned artifacts are written and it has stopped auditing.

The root records the actual outcome. If a reviewer finishes a complete, self-contained Markdown audit but its structured companion is missing or malformed, record the artifact defect; the Markdown audit may remain eligible and can be normalized manually after the isolation barrier opens. An incomplete Markdown audit is not an eligible completed review.

### 4. Wait for every terminal outcome

Do not synthesize until each requested reviewer is completed, failed, or excluded.

Do not read partial reviewer output.

When practical, replace a failed reviewer with a fresh isolated reviewer before synthesis if that preserves the requested review count without exposing peer results.

### 5. Record reviewer coverage

Record coverage before interpreting findings:

```yaml
reviewer_coverage:
  requested: 5
  completed: 3
  eligible: 3
  failed: 2
  excluded: 0
  completion_ratio: 0.60
  eligible_ratio: 0.60
```

`eligible` means a completed reviewer valid for synthesis after integrity checks.

Never hide missing review capacity by reporting only `3/3 = 100%`.

If one eligible reviewer remains, root may verify and report findings but reviewer convergence is unavailable. With zero eligible reviewers, synthesis is impossible.

Do not use a universal minimum such as "three reviewers" as a proxy for quality.

### 6. Normalize every distinct assertion

After the isolation barrier opens, read every eligible Markdown report and structured companion.

For each normalized finding, assign every eligible reviewer exactly one position:

- `supports`: explicitly supports the same underlying assertion;
- `contradicts`: explicitly evaluates and rejects that assertion or supplies counter-evidence;
- `related`: discusses related evidence without taking a position on the same assertion;
- `not_observed`: provides no position.

Silence is `not_observed`, never `contradicts`.

### 7. Deduplicate semantically

Merge only findings that assert the same underlying problem.

Do not merge merely because findings share a title, category, file, source, symptom, or recommended fix. If the shared root cause is uncertain, keep them separate and record the uncertainty.

### 8. Measure convergence without turning it into truth

For comparable identical reviewers:

```text
detection_rate = supporting_reviewers / eligible_completed_reviewers
```

This is recurrence/detection frequency.

When at least one reviewer explicitly supports or contradicts:

```text
position_agreement = supporting_reviewers / (supporting_reviewers + contradicting_reviewers)
```

This excludes `not_observed` and `related`.

Use descriptive labels:

- `unanimous_among_completed`: every eligible completed reviewer supports;
- `recurrent`: detection rate is at or above `convergence_threshold`;
- `limited`: more than one supports but the rate is below threshold;
- `isolated`: exactly one supports;
- `none`: no reviewer supports;
- `not_comparable`: no meaningful common denominator.

Always show raw counts and reviewer coverage with the label.

A finding can be recurrent and contradicted at the same time. Four supporters and one explicit contradictor is not a majority win.

### 9. Assess evidence separately

Use:

- `strong`: direct observation, successful reproduction, decisive code/data inspection, or a primary source directly establishes the material assertion with little inference;
- `moderate`: specific evidence supports the assertion but material inference, environmental dependence, or unresolved limitations remain;
- `weak`: incomplete, indirect, speculative, or mostly inferential;
- `none`: no meaningful concrete support.

Track provenance roots where relevant.

Five reviewers citing the same code location, specification, test, document, or external source are five independent reviewer observations, not five independent evidence sources.

### 10. Preserve contradictions as defeaters

An evidence-backed contradiction is qualitatively different from silence.

Record who contradicted the assertion, the counter-evidence, its strength/provenance, and whether root verification resolved it.

A credible unresolved contradiction prevents the finding from being presented as settled regardless of vote count.

Majority vote must never erase material counter-evidence.

### 11. Perform root verification

The root must inspect original allowed materials and use available tools to challenge meaningful findings. It is not merely a vote counter or LLM judge.

Verification is especially required for:

- critical/high findings;
- findings that drive recommended action;
- isolated/limited findings with concrete evidence;
- explicit contradictions;
- recurrent findings relying on a shared source or shared inference;
- disagreements that may be assumption-driven.

For code, inspect surrounding code, reproduce behavior, run focused tests, trace callers/data flow, and inspect relevant diffs/history when material.

For documents/research, inspect primary sources, validate quotations/locators, distinguish fact from inference, identify shared provenance, and investigate contradictory evidence.

Record:

- `verified`
- `partially_verified`
- `contradicted`
- `unable_to_verify`
- `not_attempted`

Use `not_attempted` only for low-materiality findings that do not drive action.

Root verification should use evidence outside reviewer prose whenever possible. Having the same model merely reread or self-critique the reports is not independent verification.

### 12. Keep severity separate

Severity answers:

> How bad would this be if true?

Evidence and verification answer:

> How much reason do we have to treat it as substantiated?

Never increase evidence strength because a claim is severe. Severity may increase verification effort and remediation urgency only.

### 13. Use categorical final disposition

Do not assign a 1-10 confidence rating or an uncalibrated probability.

Use:

- `verified`: root substantiates the material assertion;
- `partially_verified`: root substantiates only part;
- `contested`: credible support and credible counter-evidence remain unresolved;
- `unverified`: root did not substantiate the assertion;
- `rejected`: root verification or stronger counter-evidence materially refutes it.

Convergence informs the explanation but is not an acceptance rule.

### 14. Reconcile isolated findings

Every distinct finding must be normalized.

An isolated finding is low recurrence, not automatically weak evidence. If it has concrete evidence or material potential impact, root must investigate it.

Do not discard a finding solely because it falls below the convergence threshold.

### 15. Record assumptions and correlated-failure risks

When reviewers disagree, determine whether the difference comes from conflicting evidence, different assumptions, different interpretations, different environments/configurations, or an actual contradiction.

Record unresolved assumptions.

Where material, note common-mode risks such as the same model/model family, prompt, specification, external source, toolchain, fixture/test, or implicit assumption.

Optional model/provider heterogeneity may reduce some common-mode risks, but it changes the ensemble and does not guarantee independent errors. Do not require it by default.

### 16. Write the final report for action

Use `templates/final-consensus-report-template.md`.

Make reviewer coverage, convergence, evidence strength, contradiction, root verification, severity, assumptions, and final disposition separately visible.

Organize by epistemic status:

1. Verified actionable findings
2. Partially verified findings
3. Contested findings
4. Unverified recurrent findings
5. Unverified limited/isolated findings
6. Rejected findings when useful

Within a section, severity can prioritize remediation.

## Review Criteria

For code/branch review, examine correctness, regressions, edge cases, security, data integrity, error handling, tests, performance, API compatibility, migration/deployment risk, maintainability, observability, and documentation impact.

For general audits, examine internal consistency, completeness, factual/logical errors, missing requirements, risks, ambiguity, unsupported assumptions, and practical implementation concerns.

Reviewers should cite specific locations and prioritize actionable issues over style preferences.

## Failure Handling

If a reviewer fails:

1. Record the failure without reading completed peer output.
2. Replace with a fresh isolated reviewer when practical.
3. Wait for all requested/replacement reviewers to become terminal.
4. Record requested, completed, eligible, failed, and excluded counts.
5. Never change the denominator silently.
6. Do not claim convergence with only one eligible reviewer.
7. Stop if zero eligible reviewers remain.

Exclude a reviewer that appears to have read or copied peer work. Preserve the excluded artifact for provenance unless the user explicitly requests cleanup.

## Final User Response

Return:

1. path to the final report;
2. highest-priority verified or contested findings;
3. any verified isolated finding that materially changes the result;
4. reviewer coverage and important verification/correlation limits.

Do not paste all individual reports unless asked.

Never automatically delete reviewer reports or structured findings.
