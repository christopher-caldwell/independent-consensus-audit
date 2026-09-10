# Final Independent Consensus Audit

## Decision Summary

Briefly state what should be acted on now, what remains contested or unverified, and any material reviewer-coverage or correlated-failure limitation.

Do not describe a finding as true merely because it recurred across reviewers.

## Audit Configuration and Coverage

```yaml
audit_target: ""
audit_type: ""
reviewer_mode: ""
reviewer_count_requested: 0
reviewer_count_completed: 0
reviewer_count_eligible: 0
reviewer_count_failed: 0
reviewer_count_excluded: 0
completion_ratio: 0.0
eligible_ratio: 0.0
convergence_threshold: 0.60
```

State whether reviewer convergence is measurable. If only one eligible reviewer completed, say explicitly that convergence is unavailable.

### Correlated-Failure Context

Record material common-mode dependencies such as:

- same model or model family;
- same reviewer prompt;
- same specification or source material;
- same toolchain or test fixture;
- shared assumptions discovered during reconciliation.

These are caveats on what convergence means, not reasons to discard it.

## Findings at a Glance

Use a compact table.

| ID | Finding | Severity | Reviewer convergence | Evidence | Contradiction | Root verification | Final disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 |  |  |  |  |  |  |  |

For reviewer convergence, show counts rather than a naked percentage. Example:

`recurrent — 4/5 support; 1 contradicts; 5/5 requested reviewers eligible`

If reviewer coverage is degraded, make it visible in the same phrase or immediately below the table.

## Verified Actionable Findings

Findings whose material assertion was independently substantiated by root verification.

A finding belongs here whether it was unanimous, recurrent, limited, or isolated.

### F-001: {canonical title}

**Severity:** critical | high | medium | low | informational  
**Final Disposition:** verified  
**Reviewer Convergence:** unanimous among completed | recurrent | limited | isolated | none | not comparable  
**Reviewer Positions:** {supporting} support, {contradicting} contradict, {related} related, {not_observed} not observed  
**Reviewer Coverage:** {eligible}/{requested} eligible reviewers; {completed}/{requested} completed  
**Detection Rate:** {supporting}/{eligible} ({ratio}) | not comparable  
**Position Agreement:** {supporting}/{supporting_plus_contradicting} ({ratio}) | not applicable  
**Evidence Strength:** strong | moderate | weak | none  
**Root Verification:** verified  
**Category:** correctness | security | performance | maintainability | testing | documentation | design | other  

**Assertion:**  
State the normalized assertion.

**Evidence:**  
Summarize the concrete evidence. Distinguish repeated reviewer observations from distinct evidence provenance roots.

**Root Verification:**  
Describe what the root inspected, reproduced, tested, or checked directly.

**Contradictions / Defeaters:**  
Record any counter-evidence and how it was resolved. Use `None observed` only when no reviewer explicitly contradicted the assertion.

**Impact if True:**  
Describe consequence separately from evidentiary confidence.

**Assumptions / Correlation Notes:**  
Record unresolved assumptions and shared-source or shared-model risks that matter.

**Recommended Action:**  
State the next action.

## Partially Verified Findings

Use for assertions where root verification substantiated only part of the material claim.

Keep the same per-finding fields as above and identify exactly what was and was not verified.

## Contested Findings

Use when credible support and credible counter-evidence remain unresolved.

High reviewer recurrence does not override this section.

For each finding include:

- normalized assertion;
- severity;
- reviewer positions and coverage;
- evidence supporting the assertion;
- evidence contradicting it;
- provenance roots for both sides where useful;
- root verification attempted;
- why the contradiction remains unresolved;
- the next discriminating test, source, or inspection.

## Unverified Recurrent Findings

Use for findings that recurred across comparable reviewers but root verification did not substantiate.

For each finding state:

- recurrence counts and coverage;
- evidence strength;
- root verification status and limitation;
- shared-source/shared-assumption risks;
- why it is not being presented as verified;
- whether further investigation is warranted.

## Unverified Limited or Isolated Findings

Use for unique or low-recurrence findings that remain unresolved after root review.

Do not omit a concrete isolated finding solely because it failed the convergence threshold.

For each finding state:

- reviewer support count;
- evidence strength;
- root verification status;
- severity if true;
- reason it remains unresolved;
- recommended next step.

## Rejected Findings

Include when documenting false positives or resolved contradictions is useful.

For each rejected finding include:

- original assertion;
- reviewer support count;
- root contradiction or stronger counter-evidence;
- why the assertion was rejected;
- whether any residual concern remains.

## Assumption-Driven Disagreements

Include when reviewers appeared to disagree because they used different assumptions rather than conflicting evidence.

For each material case identify:

- the competing assumptions;
- which findings or reviewer positions they affected;
- whether the root resolved the assumption;
- what would change under each assumption if unresolved.

## Prioritized Actions

Prioritize first by epistemic status, then by severity and practical urgency.

A typical order is:

1. verified critical/high findings;
2. verified lower-severity findings;
3. partially verified findings needing bounded follow-up;
4. contested findings with a clear discriminating check;
5. unverified findings worth additional investigation.

Do not promote an unverified severe claim above a verified finding merely because its hypothetical impact is larger. Severity can justify faster verification, not stronger belief.

## Caveats

Record:

- incomplete or excluded reviewers;
- unavailable verification tools or source material;
- shared model/prompt/source dependencies;
- unresolved assumptions;
- focused-reviewer denominators that are not comparable;
- malformed or missing structured companion files.

## Audit Artifacts Preserved

List every individual reviewer Markdown report and structured companion used or excluded.

Example:

- `./audits/reviewer-01.md`
- `./audits/reviewer-01.findings.yaml`
- `./audits/reviewer-02.md`
- `./audits/reviewer-02.findings.yaml`

These artifacts are part of the audit provenance and are retained by default.
