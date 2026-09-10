---
name: independent-consensus-audit
description: Runs configurable independent subagent audits that each write isolated Markdown reports, then performs root-only synthesis to identify quorum-backed findings, confidence ratings, disputed issues, and strong minority concerns.
---

# Independent Consensus Audit

## Purpose

Use this skill when a user wants multiple independent reviews of the same target followed by a root-level synthesis.

This skill is useful for:

- Code review against a branch, pull request, commit, diff, or repository
- Security, correctness, performance, maintainability, or architecture audits
- Document, policy, research, product, UX, or general quality audits
- Any review where independent judgment followed by structured consensus is valuable

The core goal is to reduce anchoring and premature agreement. Each reviewer forms its own conclusions first. The root agent reads the completed individual reports only after every reviewer has finished, then deduplicates findings, determines quorum, assigns confidence, preserves important minority concerns, and writes the final report.

## Non-Negotiable Independence Rule

Subagents must work independently.

A reviewer must not:

- Read another reviewer's audit
- Ask another reviewer for opinions
- Use another reviewer's output
- Coordinate findings with another reviewer
- Revise conclusions based on peer findings
- Attempt to infer expected consensus
- Soften, inflate, or suppress findings to match perceived group opinion

The root agent is the only agent allowed to read all completed individual audit files.

## Default Configuration

If the user does not provide configuration, use these defaults:

```yaml
audit_target: "<infer from user request>"
audit_type: "general_audit"
reviewer_count: 5
reviewer_mode: "identical_reviewers"
quorum_threshold: 0.60
include_minority_findings: true
minority_severity_floor: "high"
output_directory: "./audits"
individual_report_pattern: "reviewer-{number}.md"
final_report_filename: "final-consensus-audit.md"
```

The root agent may override defaults only when the user's request clearly requires it.
Do not infer `focused_reviewers` from `audit_type` alone. Use `focused_reviewers`
only when the user explicitly asks for different reviewer lenses, different
focuses, specialist reviewers, or provides reviewer-specific focuses. For
consensus, averaging, same-task review, or independent duplicate review, use
`identical_reviewers`. Resolve relative output paths against the active workspace
or audit target root, not against the installed skill directory.

## Configurable Inputs

Supported configuration fields:

```yaml
audit_target: "<branch, diff, repo path, document, feature, system, or other target>"
audit_type: "<code_review | branch_review | security_audit | architecture_audit | document_audit | product_audit | general_audit | custom>"
reviewer_count: 5
reviewer_mode: "<identical_reviewers | focused_reviewers>"
quorum_threshold: 0.60
include_minority_findings: true
minority_severity_floor: "high"
output_directory: "./audits"
final_report_filename: "final-consensus-audit.md"
individual_report_pattern: "reviewer-{number}.md"
allowed_materials:
    - "<target files, diff, docs, requirements, test output, issue description>"
disallowed_materials:
    - "./audits/reviewer-*.md"
    - "./audits/final-consensus-audit.md"
review_focuses:
    reviewer_01: code_review
    reviewer_02: code_review
    reviewer_03: code_review
```

## Bundled Resources

Use these resources as needed:

- `templates/individual-reviewer-prompt.md`: starting prompt for each isolated reviewer.
- `templates/final-consensus-report-template.md`: final report structure for root synthesis.
- `templates/normalized-finding.schema.yaml`: normalized finding shape for synthesis.
- `checklists/root-synthesis-checklist.md`: checklist to use after all reviewer reports complete.
- `examples/code-review.config.yaml`: sample identical-reviewer configuration for branch or code review.
- `examples/general-audit.config.yaml`: sample identical-reviewer configuration for broad audits.

Load examples only when the user asks for configuration help or when a concrete example
would prevent ambiguity. Do not copy template placeholders into final reports.

## Reviewer Modes

### Identical Reviewers

Use `identical_reviewers` when the user wants several independent reviewers to assess the same target using the same criteria. This is the default and preferred mode for consensus, averaging results, same-task review, and independent duplicate review.

Each reviewer receives the same task, target, review criteria, and allowed materials. They must still reason independently.

### Focused Reviewers

Use `focused_reviewers` only when the user explicitly asks for different lenses, specialist reviewers, or broader coverage instead of repeated identical review.

Assign each reviewer a primary lens. Example set for ten reviewers:

```yaml
reviewer_01: correctness
reviewer_02: security
reviewer_03: performance
reviewer_04: maintainability
reviewer_05: testing
reviewer_06: architecture
reviewer_07: data_integrity
reviewer_08: deployment_risk
reviewer_09: observability
reviewer_10: documentation
```

Focused reviewers may report any issue they find, even outside their assigned lens.

## Root Agent Workflow

The root agent must follow this sequence.

### 1. Define the audit plan

Before launching reviewers, define:

- Audit target
- Audit type
- Number of reviewers
- Reviewer mode
- Review focus for each reviewer
- Quorum threshold
- Output directory and file paths
- Allowed materials
- Disallowed materials
- Final report path

Create the output directory if needed.

### 2. Launch independent reviewers

Spawn the configured number of isolated subagents when the platform supports subagents.

If true subagents are unavailable, emulate independence by running separate review passes and writing each pass to its own file before reading, comparing, or synthesizing any prior pass.

Each reviewer receives only:

- The audit target
- The audit type
- Its review focus
- The review criteria
- The allowed materials
- The disallowed materials
- Its assigned output path
- The individual reviewer report template
- The independence rules

Each reviewer must not receive:

- Other reviewer identities beyond neutral IDs
- Other reviewer outputs
- Root synthesis notes
- Partial consensus
- Any summary of another reviewer's findings

### 3. Require individual Markdown reports

Each reviewer writes exactly one self-contained Markdown report.

Default paths:

```text
./audits/reviewer-01.md
./audits/reviewer-02.md
./audits/reviewer-03.md
./audits/reviewer-04.md
./audits/reviewer-05.md
```

### 4. Wait for all reports to complete

The root agent must not begin synthesis until all expected reviewer files are complete, or until a reviewer failure is explicitly recorded.

The root agent must not read partial reviewer output.

### 5. Read and normalize findings

After all individual reports are complete, read every completed reviewer report.

Normalize every finding into this structure:

```yaml
canonical_title: ""
category: ""
severity: "critical | high | medium | low | informational"
reviewers_supporting: []
reviewers_noting_related_issue: []
support_count: 0
total_reviewers: 0
support_ratio: 0.0
quorum_status: "unanimous | strong_consensus | meets_quorum | split | below_quorum | minority_high_severity | likely_false_positive"
evidence_summary: ""
root_verification: "verified | partially_verified | contradicted | not_verified | unable_to_verify"
confidence_rating: 0
recommended_action: ""
```

### 6. Deduplicate carefully

Treat findings as the same issue only when they describe the same underlying problem.

Do merge:

- Different wording for the same bug
- Different symptoms of the same root cause, when evidence supports a shared cause
- Same issue reported at the same location with different severity estimates

Do not merge:

- Different bugs in the same file
- Different security risks in the same feature
- General category overlap without a shared underlying problem
- Findings with materially different causes or fixes

When uncertain, keep findings separate and note the uncertainty.

### 7. Determine quorum

Calculate:

```text
support_ratio = support_count / total_completed_reviewers
```

A finding meets quorum when:

```text
support_ratio >= quorum_threshold
```

Default quorum threshold is `0.60`.

Useful labels:

```text
10/10 = unanimous
8/10 or 9/10 = strong consensus
6/10 or 7/10 = quorum-backed
5/10 = split finding
2/10 to 4/10 = minority finding
1/10 = isolated finding
```

Adjust the examples proportionally for reviewer counts other than ten.

### 8. Assign confidence

Assign confidence from 1 to 10.

Confidence must consider:

- Support count
- Support ratio
- Quality and specificity of evidence
- Whether the root agent directly verified the issue
- Severity and practical impact
- Whether reviewers disagreed on interpretation
- Whether the finding depends on assumptions
- Whether evidence contradicts the finding

Do not assign confidence from vote count alone.

Rough guide:

```text
10/10: Unanimous, specific, well-evidenced, root-verified
8-9/10: Strong consensus, well-evidenced, likely valid
6-7/10: Meets quorum, plausible, some verification limits
4-5/10: Split or uncertain, needs manual review
2-3/10: Minority finding, weak evidence or unverified
1/10: Isolated, speculative, or likely false positive
```

A high-severity minority finding may receive a mid-level confidence rating if it has concrete evidence. A unanimous finding may be downgraded if the root agent cannot verify it or if the evidence is weak.

### 9. Preserve important minority findings

Do not discard a finding only because it failed quorum.

Include a minority finding when:

- Severity is at or above `minority_severity_floor`
- Evidence is specific and plausible
- The downside risk of ignoring it is high
- The root agent can partially or fully verify it
- It identifies an issue class other reviewers may not have focused on

Put these in `Strong Minority Findings`, not in `Consensus Findings`.

### 10. Write the final consensus report

The final report must be a root-level synthesis, not a concatenation of individual reports.

Default output:

```text
./audits/final-consensus-audit.md
```

The final report must include:

- Audit summary
- Configuration used
- Consensus findings
- Strong minority findings, if any
- Split or disputed findings, if any
- Likely false positives, if useful
- Final prioritized recommendation
- List of individual audit files reviewed
- Caveats about incomplete reviewers or verification limits

## Code Review Criteria

When `audit_type` is `code_review` or `branch_review`, reviewers should examine:

- Correctness
- Regressions
- Edge cases
- Security risks
- Data integrity
- Error handling
- Tests
- Performance
- API compatibility
- Migration or deployment risk
- Maintainability
- Observability
- Documentation impact

Reviewers should cite specific files, functions, line ranges, diffs, commits, tests, or commands where possible.

Prioritize actionable issues over style preferences.

## General Audit Criteria

When `audit_type` is `general_audit`, reviewers should examine:

- Internal consistency
- Completeness
- Factual or logical errors
- Missing requirements
- Risk areas
- Ambiguity
- Unsupported assumptions
- Practical implementation concerns
- Recommendations for improvement

The final report should distinguish defects, risks, recommendations, and optional improvements.

## Failure Handling

If a reviewer fails to complete the audit:

1. Record the failure.
2. Continue only if at least three completed reports remain, unless the user explicitly requested fewer reviewers.
3. Base support ratios on completed reports, not originally requested reports.
4. Include the failure in final caveats.

If fewer than three reviewers complete their reports, warn that consensus quality is weak.

If a reviewer appears to have read or copied another reviewer's output, exclude that report from synthesis and explain why.

## Final User Response

After completing the audit, respond with:

1. Path to the final consensus report
2. Brief summary of top consensus findings
3. Any high-severity minority findings
4. Caveats about incomplete reviewers, verification limits, or low quorum

Do not paste all individual reports into the final response unless the user asks.

Finally, remove the individual audits from disk IF they are no longer needed and have been properly summarized by the final output.
