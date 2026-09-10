# Independent Consensus Audit

Independent Consensus Audit is a Codex skill for running several isolated reviews of the same target and reconciling them into one evidence-aware audit.

The design is intentionally narrow: reviewers work independently, preserve their own artifacts, and finish before the root agent sees any peer output. The root then compares the reports, normalizes findings, checks evidence and contradictions, directly verifies meaningful claims, and writes a final report optimized for action.

The key rule is:

> **Consensus is not verification.**

Five reviewers reaching the same conclusion is useful information about independent convergence. It is not proof that the conclusion is true, especially when reviewers share the same model, prompt, specification, source material, tools, or assumptions.

## What the skill separates

The final synthesis keeps these dimensions distinct:

- **Reviewer coverage:** how much of the requested independent review capacity completed and remained eligible.
- **Convergence:** how often comparable reviewers independently identified the same assertion.
- **Reviewer position:** support, explicit contradiction, related observation, or no observation.
- **Evidence strength:** how concrete the support is.
- **Evidence provenance:** whether several reviewers are relying on the same underlying source.
- **Root verification:** what the orchestrator could substantiate directly from original materials.
- **Severity:** how bad the issue would be if true.
- **Final disposition:** verified, partially verified, contested, unverified, or rejected.

Severity affects verification and remediation priority. It does not make a claim more believable.

## Why independent review still matters

Independent duplicate review can expose blind spots and reveal whether an observation recurs without reviewer-to-reviewer anchoring. But independence of process does not guarantee independent errors.

That distinction changes how the skill treats several important cases:

| Situation | Result |
| --- | --- |
| 5/5 reviewers agree and root verifies the evidence | High convergence, verified finding |
| 5/5 agree but root cannot substantiate it | High convergence, unverified finding |
| 1/5 finds an issue and root reproduces it | Isolated discovery, verified finding |
| 4/5 support and 1/5 supplies credible counter-evidence | Recurrent finding, contested until the contradiction is resolved |
| 3/5 requested reviewers complete and all 3 support | Unanimous among completed reviewers, with 60% reviewer coverage |
| Reviewers repeat the same inference from one bad source | Convergence is recorded, shared-provenance risk is recorded, root verification decides whether the claim survives |
| Reviewers differ because they assumed different environments | Assumption-driven disagreement, not automatically an evidence conflict |

## How it works

```text
Audit target
    |
    +--> Reviewer 01 --> reviewer-01.md + reviewer-01.findings.yaml --+
    +--> Reviewer 02 --> reviewer-02.md + reviewer-02.findings.yaml --+
    +--> Reviewer 03 --> reviewer-03.md + reviewer-03.findings.yaml --+--> Root synthesis
    +--> Reviewer 04 --> reviewer-04.md + reviewer-04.findings.yaml --+       |
    +--> Reviewer 05 --> reviewer-05.md + reviewer-05.findings.yaml --+       +--> verify
                                                                               +--> reconcile
                                                                               +--> final audit
```

The root follows these broad phases:

1. Define the target, reviewer mode, allowed materials, output paths, and convergence threshold.
2. Launch isolated reviewers with equivalent instructions or explicitly requested specialist lenses.
3. Wait until every requested reviewer is complete, failed, or excluded.
4. Record reviewer coverage before reading any report.
5. Read Markdown reports and structured companions, then normalize every distinct finding.
6. Distinguish support, contradiction, related observations, and silence.
7. Measure recurrence without treating a percentage as truth.
8. Verify meaningful findings against the original materials.
9. Preserve unresolved contradictions and shared-source/common-mode risks.
10. Write a final report grouped by epistemic status and actionability.

## Installation

### Clone into your Codex skills directory

```bash
git clone <repository-url> ~/.codex/skills/independent-consensus-audit
```

Restart Codex or begin a new session so the skill catalog is refreshed.

### Develop from a working clone

```bash
git clone <repository-url> ~/Code/projects/independent-consensus-audit
ln -s ~/Code/projects/independent-consensus-audit \
  ~/.codex/skills/independent-consensus-audit
```

If that destination already exists, move or remove it first. Do not overlay a symlink on an existing installed copy.

## Usage

Invoke the skill by name and describe the audit target:

```text
Use $independent-consensus-audit to review the current branch against main.
```

```text
Use $independent-consensus-audit to audit docs/security-policy.md for gaps and contradictions.
```

```text
Run an independent consensus audit of this architecture proposal with 7 identical reviewers.
```

Unless specified otherwise, the skill uses five identical reviewers, a descriptive 60% convergence threshold, and writes results under `./audits` relative to the active workspace or audit target.

### Default configuration

```yaml
audit_target: "<inferred from the request>"
audit_type: "general_audit"
reviewer_count: 5
reviewer_mode: "identical_reviewers"
convergence_threshold: 0.60
output_directory: "./audits"
individual_report_pattern: "reviewer-{number}.md"
individual_findings_pattern: "reviewer-{number}.findings.yaml"
final_report_filename: "final-consensus-audit.md"
```

See [`examples/code-review.config.yaml`](examples/code-review.config.yaml) and [`examples/general-audit.config.yaml`](examples/general-audit.config.yaml).

## Reviewer modes

### Identical reviewers

This is the default when the goal is repeated independent judgment. Every reviewer receives the same target, criteria, focus, and allowed materials.

For comparable identical reviewers:

```text
detection_rate = supporting_reviewers / eligible_completed_reviewers
```

Detection rate answers how often the assertion was independently discovered.

When reviewers explicitly take a position on the same assertion:

```text
position_agreement = supporting_reviewers / (supporting_reviewers + contradicting_reviewers)
```

Silence is excluded from position agreement because failing to mention a finding is not a vote against it.

### Focused reviewers

Use focused reviewers only when specialist lenses or broader coverage are explicitly requested.

```yaml
reviewer_mode: "focused_reviewers"
review_focuses:
  reviewer_01: correctness
  reviewer_02: security
  reviewer_03: performance
  reviewer_04: maintainability
  reviewer_05: testing
```

Because reviewers were given different primary tasks, raw support percentages are normally not comparable. The root still records support and contradiction, but convergence should be marked `not_comparable` unless there is a genuinely common denominator.

## Convergence labels

The default `convergence_threshold` is `0.60`. It is a descriptive threshold, not an acceptance threshold.

For identical reviewers:

- `unanimous_among_completed`: every eligible completed reviewer supports the assertion;
- `recurrent`: support rate is at or above the configured threshold;
- `limited`: more than one reviewer supports it but the rate is below the threshold;
- `isolated`: exactly one reviewer supports it;
- `none`: no reviewer supports it;
- `not_comparable`: reviewer assignments do not support a meaningful common denominator.

Always read the label together with raw counts and reviewer coverage.

A legacy `quorum_threshold` config is treated as an alias for `convergence_threshold`, but it no longer means a finding is accepted when the threshold is crossed.

## Evidence and contradiction

Each reviewer records an evidence-strength category instead of a numeric confidence score:

- `strong`
- `moderate`
- `weak`
- `none`

The root can strengthen or weaken the synthesis assessment after checking the original materials.

A reviewer who never mentions a finding is `not_observed`.

A reviewer who explicitly evaluates the same assertion and provides a reason it is wrong is `contradicts`.

Those states are not interchangeable.

A credible evidence-backed contradiction prevents the final report from presenting a finding as settled until the root resolves it. Majority support does not erase counter-evidence.

## Root verification

The root is expected to verify meaningful claims rather than merely judge reviewer prose.

For code, verification can include source inspection, focused tests, reproduction, caller tracing, and relevant diff/history checks.

For documents or research, it can include primary-source inspection, quotation/source validation, assumption checks, and contradiction investigation.

Root verification uses:

- `verified`
- `partially_verified`
- `contradicted`
- `unable_to_verify`
- `not_attempted`

The root should use original allowed materials and tools whenever possible. Asking the same model to reread a report is not independent verification.

## Final disposition

The final audit does not use a 1–10 confidence score.

Each normalized finding ends with one disposition:

- `verified`
- `partially_verified`
- `contested`
- `unverified`
- `rejected`

Convergence is reported alongside the disposition but does not determine it.

An isolated finding can be verified. A unanimous finding can remain unverified. A recurrent finding can be contested.

## Reviewer failures and coverage

Reviewer failures are never hidden by changing the denominator without explanation.

The audit records:

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

If only one eligible reviewer completes, the root may still verify and report findings, but reviewer convergence is unavailable. If zero eligible reviewers remain, synthesis cannot proceed.

There is no universal rule that "three reviewers" makes an audit reliable. The report exposes actual coverage instead.

## Output

The default layout is:

```text
audits/
├── reviewer-01.md
├── reviewer-01.findings.yaml
├── reviewer-02.md
├── reviewer-02.findings.yaml
├── reviewer-03.md
├── reviewer-03.findings.yaml
├── reviewer-04.md
├── reviewer-04.findings.yaml
├── reviewer-05.md
├── reviewer-05.findings.yaml
└── final-consensus-audit.md
```

Individual reviewer artifacts are part of the provenance record and are retained by default. The skill never deletes them automatically. Cleanup requires an explicit user request.

## Repository layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── checklists/
│   └── root-synthesis-checklist.md
├── examples/
│   ├── code-review.config.yaml
│   └── general-audit.config.yaml
└── templates/
    ├── final-consensus-report-template.md
    ├── individual-reviewer-prompt.md
    ├── reviewer-findings.schema.yaml
    └── normalized-finding.schema.yaml
```

- [`SKILL.md`](SKILL.md) is authoritative.
- [`templates/individual-reviewer-prompt.md`](templates/individual-reviewer-prompt.md) defines reviewer isolation and human-readable output.
- [`templates/reviewer-findings.schema.yaml`](templates/reviewer-findings.schema.yaml) defines the structured reviewer companion.
- [`templates/normalized-finding.schema.yaml`](templates/normalized-finding.schema.yaml) defines root-level reconciliation.
- [`templates/final-consensus-report-template.md`](templates/final-consensus-report-template.md) defines the final synthesis.
- [`checklists/root-synthesis-checklist.md`](checklists/root-synthesis-checklist.md) guards the root-only reconciliation phase.

## Design principles

1. Preserve reviewer independence.
2. Treat reviewer convergence as recurrence, not truth.
3. Treat silence as no observation, not disagreement.
4. Let concrete evidence outrank vote count.
5. Preserve credible counter-evidence as a defeater.
6. Investigate unique findings instead of discarding them below a threshold.
7. Keep severity separate from evidentiary confidence.
8. Expose reviewer coverage and common-mode dependencies.
9. Verify against original materials, not only reviewer prose.
10. Preserve every reviewer artifact by default.
11. Keep the skill lightweight: Markdown, YAML, and root reasoning rather than a workflow engine or database.

## Contributing

Changes to the workflow should preserve reviewer isolation and root-only synthesis. Keep `SKILL.md`, prompts, schemas, examples, checklist, and final-report template consistent.

Before committing, check that YAML files parse, Markdown links resolve, and reviewer disallowed-material patterns prevent peer-artifact access.

## License

Licensed under the [MIT License](LICENSE).
