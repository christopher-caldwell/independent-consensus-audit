# Root Synthesis Checklist

Use this checklist after all individual reviewer files are complete.

## Before Reading Reports

- [ ] Confirm all expected reviewer files exist, or record failures.
- [ ] Confirm no reviewer had access to peer reports.
- [ ] Confirm the final synthesis has not started from partial reports.
- [ ] Confirm quorum threshold and completed reviewer count.

## While Reading Reports

- [ ] Extract every finding into the normalized schema.
- [ ] Preserve severity and confidence as reported by each reviewer.
- [ ] Record specific evidence and location.
- [ ] Track non-issues and things checked.
- [ ] Track assumptions and open questions.

## Deduplication

- [ ] Merge only findings with the same underlying issue.
- [ ] Do not merge unrelated issues from the same category or file.
- [ ] Keep uncertain merges separate and explain the uncertainty.
- [ ] Preserve important differences in root cause or recommended fix.

## Verification

- [ ] Verify critical and high-severity findings where possible.
- [ ] Verify quorum-backed findings where possible.
- [ ] Downgrade confidence when evidence is weak or unverifiable.
- [ ] Mark findings as contradicted when direct inspection refutes them.

## Final Report

- [ ] Separate consensus findings from strong minority findings.
- [ ] Include support count and confidence for every accepted finding.
- [ ] Include root verification status for every accepted finding.
- [ ] Include high-severity minority findings when evidence warrants it.
- [ ] Include split or disputed findings when useful.
- [ ] Include likely false positives when they could otherwise confuse the user.
- [ ] Prioritize final recommendations by severity, confidence, and actionability.
