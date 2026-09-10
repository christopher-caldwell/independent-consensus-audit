# Independent Consensus Audit

Independent Consensus Audit is a Codex skill for running several isolated reviews of the same target and turning them into one evidence-based consensus report.

It is designed for situations where a single review is too vulnerable to anchoring, blind spots, or individual judgment. Each reviewer inspects the target independently, writes a private Markdown report, and finishes before the root agent reads any reviewer output. The root agent then normalizes and deduplicates the findings, checks which findings meet quorum, verifies important claims, preserves credible minority concerns, and writes a final prioritized audit.

The skill works for code and branch reviews, security and architecture audits, documents and policies, product or UX reviews, research artifacts, and other targets where multiple independent judgments are useful.

## Why use it?

A normal multi-agent review can accidentally become groupthink: early findings shape later reviewers, similar wording is mistaken for independent support, or majority votes are treated as proof. This skill makes independence an explicit part of the workflow.

Its key properties are:

- **Independent first-pass reviews.** Reviewers cannot read or coordinate with peers.
- **Configurable consensus.** Choose the reviewer count and quorum threshold.
- **Evidence-aware confidence.** Confidence uses evidence and root verification, not vote count alone.
- **Careful deduplication.** Related wording is merged only when it describes the same underlying issue.
- **Minority-risk preservation.** Credible high-severity concerns can survive even when they miss quorum.
- **Auditable output.** Individual reports and the final synthesis are plain Markdown.

## How it works

```text
Audit target
    |
    +--> Reviewer 01 --> isolated Markdown report --+
    +--> Reviewer 02 --> isolated Markdown report --+
    +--> Reviewer 03 --> isolated Markdown report --+--> Root synthesis
    +--> Reviewer 04 --> isolated Markdown report --+       |
    +--> Reviewer 05 --> isolated Markdown report --+       +--> Consensus findings
                                                            +--> Strong minority findings
                                                            +--> Disputed findings
                                                            +--> Prioritized recommendations
```

The root agent follows five broad phases:

1. Define the target, reviewer mode, criteria, quorum, allowed materials, and output paths.
2. Launch isolated reviewers with equivalent instructions or explicitly assigned specialist lenses.
3. Wait until every expected report is complete or its failure is recorded.
4. Read, normalize, deduplicate, compare, and directly verify the findings.
5. Write a root-level synthesis instead of concatenating reviewer reports.

The independence boundary matters: reviewers must not inspect the audit output directory or receive peer findings, partial consensus, or root synthesis notes.

## Installation

### Clone into your Codex skills directory

```bash
git clone <repository-url> ~/.codex/skills/independent-consensus-audit
```

Restart Codex or begin a new session so the skill catalog is refreshed.

### Develop from a working clone

Clone the repository wherever you keep source projects, then symlink it into the Codex skills directory:

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
Run an independent consensus audit of this architecture proposal with 7 identical reviewers and a 70% quorum.
```

Unless you specify otherwise, the skill uses five identical reviewers, a 60% quorum, includes credible high-severity minority findings, and writes results under `./audits` relative to the active workspace or audit target.

### Default configuration

```yaml
audit_target: "<inferred from the request>"
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

See [`examples/code-review.config.yaml`](examples/code-review.config.yaml) and [`examples/general-audit.config.yaml`](examples/general-audit.config.yaml) for complete examples.

## Reviewer modes

### Identical reviewers

This is the default and the right choice when you want repeated independent judgment. Every reviewer receives the same target, criteria, focus, and allowed materials. Agreement is therefore meaningful evidence of reproducibility across independent reviews.

Use it for requests such as:

- “Have five reviewers independently review this diff.”
- “Average several independent audits.”
- “Find consensus on the most important defects.”

### Focused reviewers

Use focused reviewers only when you explicitly want specialist lenses or broader coverage. For example:

```yaml
reviewer_mode: "focused_reviewers"
review_focuses:
  reviewer_01: correctness
  reviewer_02: security
  reviewer_03: performance
  reviewer_04: maintainability
  reviewer_05: testing
```

Focused review is valuable for coverage, but support ratios should be interpreted carefully: reviewers were asked different primary questions. Reviewers may still report important issues outside their assigned lens.

## Configuration reference

| Field | Meaning |
| --- | --- |
| `audit_target` | Branch, diff, repository, file, document, system, or other artifact being reviewed. |
| `audit_type` | Review criteria family, such as `branch_review`, `security_audit`, or `general_audit`. |
| `reviewer_count` | Number of independent review passes requested. |
| `reviewer_mode` | `identical_reviewers` or explicitly requested `focused_reviewers`. |
| `quorum_threshold` | Minimum support ratio required for a consensus finding. |
| `include_minority_findings` | Whether credible findings below quorum may appear separately. |
| `minority_severity_floor` | Minimum severity normally considered for minority inclusion. |
| `output_directory` | Directory for individual reports and the final synthesis. |
| `individual_report_pattern` | Filename pattern for isolated reviewer reports. |
| `final_report_filename` | Filename for the root synthesis. |
| `allowed_materials` | Sources each reviewer is permitted to inspect. |
| `disallowed_materials` | Sources reviewers must not inspect, especially peer reports. |
| `review_focuses` | Per-reviewer focus, repeated for identical mode or specialized in focused mode. |

Relative output paths resolve from the active workspace or audit target root, never from the installed skill directory.

## Quorum and confidence

Support is calculated from completed, eligible reviewers:

```text
support_ratio = support_count / total_completed_reviewers
```

A finding meets quorum when its support ratio is at least `quorum_threshold`. With five reviewers and the default threshold, three supporting reviewers are enough.

Quorum is not the same as confidence. The final confidence rating also considers:

- specificity and quality of evidence;
- direct verification by the root agent;
- disagreement about cause or impact;
- assumptions and unavailable context;
- contradicting evidence;
- severity and practical consequences.

A unanimous but vague finding can receive lower confidence. A concrete, root-verified security concern raised by one reviewer can remain a strong minority finding with meaningful confidence.

## Output

The default output layout is:

```text
audits/
├── reviewer-01.md
├── reviewer-02.md
├── reviewer-03.md
├── reviewer-04.md
├── reviewer-05.md
└── final-consensus-audit.md
```

The final report includes:

- an audit summary and the configuration used;
- quorum-backed consensus findings;
- strong minority findings, when warranted;
- split or disputed findings;
- useful likely-false-positive notes;
- prioritized recommendations;
- verification caveats and reviewer failures;
- the list of reviewer reports included in synthesis.

Individual reports may be removed after they have been completely summarized and are no longer needed. Keep them when traceability, later re-analysis, or regulated review requires the original evidence trail.

## Failure handling

If a reviewer fails, the root agent records the failure and calculates support using completed eligible reviewers. The audit normally continues only when at least three reports remain, unless the user intentionally requested fewer. If fewer than three complete, the final output warns that consensus quality is weak.

A report should be excluded if the reviewer appears to have read or copied another reviewer’s work, because it no longer represents independent evidence.

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
    └── normalized-finding.schema.yaml
```

- [`SKILL.md`](SKILL.md) contains the authoritative orchestration rules.
- [`templates/individual-reviewer-prompt.md`](templates/individual-reviewer-prompt.md) defines the isolation contract and reviewer report format.
- [`templates/final-consensus-report-template.md`](templates/final-consensus-report-template.md) defines the synthesis structure.
- [`templates/normalized-finding.schema.yaml`](templates/normalized-finding.schema.yaml) defines the common finding representation.
- [`checklists/root-synthesis-checklist.md`](checklists/root-synthesis-checklist.md) guards the root-only comparison and verification phase.

## Design principles

1. Independence comes before consensus.
2. Evidence matters more than voting.
3. Similar wording does not automatically mean the same root cause.
4. A missed quorum is not proof that a risk is harmless.
5. The final report is a judgment-bearing synthesis, not a report bundle.
6. Reviewer failures and verification limits belong in the result.

## Contributing

Changes to the workflow should preserve reviewer isolation and root-only synthesis. When editing templates or examples, keep them consistent with the authoritative rules in `SKILL.md`. Before committing, check that YAML files parse, Markdown links resolve, and example paths do not allow reviewers to read audit outputs.

## License

Licensed under the [MIT License](LICENSE).
