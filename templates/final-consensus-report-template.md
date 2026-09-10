# Final Consensus Audit

## Summary

Briefly summarize the audit target, audit type, number of completed reviewers, quorum threshold, and overall result.

## Configuration Used

```yaml
audit_target: ""
audit_type: ""
reviewer_count_requested: 0
reviewer_count_completed: 0
reviewer_mode: ""
quorum_threshold: 0.60
include_minority_findings: true
minority_severity_floor: "high"
```

## Consensus Findings

Findings that met quorum.

### Finding 1: {canonical title}

**Severity:** critical | high | medium | low | informational  
**Confidence:** {rating}/10  
**Support:** {support_count}/{total_reviewers} reviewers  
**Quorum Status:** unanimous | strong consensus | meets quorum  
**Category:** correctness | security | performance | maintainability | testing | documentation | design | other  
**Root Verification:** verified | partially verified | contradicted | not verified | unable to verify  

**Issue:**  
Explain the issue clearly.

**Evidence:**  
Summarize evidence from individual audits and, when applicable, direct root verification.

**Why It Matters:**  
Explain the risk or consequence.

**Recommended Action:**  
Describe the suggested fix, mitigation, or next review step.

**Reviewers Supporting:**  
`reviewer-01`, `reviewer-03`, `reviewer-05`

## Strong Minority Findings

Include this section only when meaningful minority findings exist.

### Minority Finding 1: {canonical title}

**Severity:** critical | high | medium | low | informational  
**Confidence:** {rating}/10  
**Support:** {support_count}/{total_reviewers} reviewers  
**Quorum Status:** below quorum  
**Root Verification:** verified | partially verified | contradicted | not verified | unable to verify  

**Issue:**  
Explain the concern.

**Reason for Inclusion:**  
Explain why this finding is worth reviewing despite not meeting quorum.

**Recommended Action:**  
Describe the next step.

## Split or Disputed Findings

Include findings where reviewers identified related evidence but disagreed on interpretation.

For each disputed finding, explain:

- What some reviewers believed
- What others omitted or implicitly disagreed with
- Whether the root agent could verify the issue
- What should be checked next

## Likely False Positives

Include findings that appeared in individual reports but should not be treated as accepted issues.

For each false positive, include:

- Brief title
- Support count
- Why it was not accepted
- Whether any follow-up is needed

## Final Recommendation

State the most important actions to take next.

Prioritize by:

1. Critical consensus findings
2. High-confidence high-severity findings
3. Quorum-backed medium-severity findings
4. Strong minority findings that warrant manual review
5. Lower-confidence cleanup items

## Caveats

List incomplete reviewers, verification limits, low quorum, unavailable files, or assumptions.

## Audit Files Reviewed

- `./audits/reviewer-01.md`
- `./audits/reviewer-02.md`
- `./audits/reviewer-03.md`
