# Root Synthesis Checklist

Use this checklist only after every requested reviewer has reached a terminal state.

## Before Reading Reviewer Artifacts

- [ ] Confirm every requested reviewer is completed, failed, or explicitly excluded.
- [ ] Confirm no reviewer had access to peer reports or peer structured findings.
- [ ] Confirm the root has not read partial reviewer output.
- [ ] Record requested, completed, eligible, failed, and excluded reviewer counts.
- [ ] Record completion and eligible coverage ratios.
- [ ] Record reviewer mode and descriptive convergence threshold.
- [ ] Record known common-mode dependencies: model, prompt, specification, source material, toolchain, fixtures.

## Artifact Integrity

- [ ] Confirm each completed reviewer wrote a Markdown report.
- [ ] Confirm each completed reviewer wrote a structured findings companion.
- [ ] If a companion is missing or malformed, reconstruct only from the Markdown report and record the structural failure.
- [ ] If Markdown and structured findings conflict, investigate the discrepancy.
- [ ] Preserve all reviewer artifacts; do not schedule automatic cleanup.

## Normalization

- [ ] Extract every distinct reviewer finding into the normalized schema.
- [ ] Deduplicate by underlying assertion, not title or category.
- [ ] Assign each eligible reviewer exactly one position per normalized finding: supports, contradicts, related, or not observed.
- [ ] Treat silence as `not_observed`, never contradiction.
- [ ] Preserve checked non-issues because they may establish an explicit contradiction.
- [ ] Preserve assumptions, uncertainty, location, impact, and evidence provenance.

## Convergence

- [ ] For comparable identical reviewers, calculate detection rate: supporters / eligible completed reviewers.
- [ ] Calculate position agreement only from supporters + explicit contradictors.
- [ ] Show raw counts with every convergence label.
- [ ] Do not use convergence threshold as an acceptance rule.
- [ ] Mark focused-reviewer convergence `not_comparable` unless a common denominator is genuinely defensible.
- [ ] If only one eligible reviewer completed, do not claim reviewer convergence.

## Evidence and Correlation

- [ ] Rate evidence strength independently of vote count.
- [ ] Identify shared evidence provenance roots where material.
- [ ] Do not count repeated references to the same source as independent evidence.
- [ ] Note shared-model, shared-prompt, shared-specification, shared-tool, or shared-assumption risks when they could explain convergence.
- [ ] Do not assume context isolation implies statistically independent errors.

## Contradictions and Defeaters

- [ ] Preserve every explicit contradiction to the same underlying assertion.
- [ ] Assess the counter-evidence itself, not the reviewer's vote weight.
- [ ] Do not let a majority erase credible counter-evidence.
- [ ] Keep the finding `contested` while a credible material contradiction remains unresolved.
- [ ] Distinguish actual evidence conflict from different assumptions or environments.

## Root Verification

- [ ] Inspect original allowed materials rather than relying only on reviewer prose.
- [ ] Attempt verification for every critical/high finding.
- [ ] Attempt verification for findings that will drive recommended action.
- [ ] Attempt verification for isolated/limited findings with concrete evidence.
- [ ] Attempt verification for every explicit contradiction.
- [ ] Attempt verification for recurrent findings that depend on a shared evidence root or shared inference.
- [ ] Record method, evidence, result, and limitations.
- [ ] Use `not_attempted` only for low-materiality findings that do not drive action.

## Severity and Disposition

- [ ] Keep severity/impact separate from evidence and verification.
- [ ] Never raise epistemic confidence because hypothetical impact is severe.
- [ ] Do not assign an uncalibrated 1-10 confidence score.
- [ ] Assign final disposition: verified, partially verified, contested, unverified, or rejected.
- [ ] Verify that final disposition is supported by root verification and contradiction status, not quorum.

## Final Report

- [ ] Put reviewer coverage near the top.
- [ ] Make convergence, evidence, contradiction, verification, severity, assumptions, and final disposition separately visible.
- [ ] Include verified isolated findings alongside verified recurrent findings.
- [ ] Include recurrent but unverified findings separately from verified findings.
- [ ] Include contested findings even when support is overwhelming.
- [ ] Include useful rejected findings so false positives are auditable.
- [ ] Prioritize action first by epistemic status, then severity and urgency.
- [ ] List every preserved reviewer artifact used or excluded.
