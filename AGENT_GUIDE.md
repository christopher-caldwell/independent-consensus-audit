# Independent Consensus Audit agent guide

This file is the shared operating contract for every host. Codex, Claude Code, and Cursor keep their installation and invocation details in their own entry files. Do not add host specific behavior here.

## Purpose

Use Independent Consensus Audit for:

- conformance review against a specification;
- investigation of a bug or performance symptom;
- reconciliation of separately produced reports or Discovery documents.

The application owns acquisition, isolation, retention, reconciliation, scoring, and rendering. The host agent prepares the request, invokes the CLI, and reports the retained result. Do not reproduce the audit pipeline in the parent chat.

Managed semantic roles use the local Codex CLI. The host loading this guide is not the execution provider.

## Prepare the request

Preserve the user's question, observations, hypotheses, constraints, and selected sources. Do not add the parent agent's preferred diagnosis or recommendation.

Write a self contained Markdown request with YAML frontmatter. When preparing it from a conversation, use absolute source paths. Relative paths in a saved request resolve from that request file.

Use `inputs` for existing reports. Do not also set `reviewers`. Record historical independence as `unknown` unless the user explicitly attests that the reports were produced separately.

Use `discovery_runs` instead of `inputs` when the reports are finalized Discovery runs. Supply each run or export directory, not only its `technical-spec.md`. The workflow treats each finalized export as one verified opinion and retains only its four output artifacts: the technical specification, summary, handoff, and evidence manifest. It does not import underlying run artifacts or repeat Discovery's investigation. The selected direction and its confidence contain only adopted claims with strict-majority support; rejected alternatives and one-report optional details remain visible as disagreements without becoming decisive. `discovery_runs` is mutually exclusive with `inputs`, `reviewers`, `target`, `spec`, and `sources`.

A minimal managed investigation is:

```markdown
---
schema_version: 1
artifact: audit-request
target: /absolute/path/to/project
reviewers: 5
---

# Question

State the observed behavior and the question. Label suspected causes as hypotheses.
```

A minimal supplied report synthesis is:

```markdown
---
schema_version: 1
artifact: audit-request
inputs:
  - /absolute/path/to/report-one.md
  - /absolute/path/to/report-two.md
input_independence: user_attested
---

Produce one actionable technical direction. Preserve material disagreements and do not add product scope.
```

A minimal Discovery synthesis is:

```markdown
---
schema_version: 1
artifact: audit-request
discovery_runs:
  - /absolute/path/to/project/.discovery/runs/first-run-uuid
  - /absolute/path/to/project/.discovery/runs/second-run-uuid
input_independence: unknown
---

Produce one actionable technical direction from the verified opinions. State their common ground and preserve material disagreements.
```

## Run the audit

Resolve the CLI once and verify it:

```sh
consensus-audit --version
consensus-audit guide
```

In a checkout, use this command prefix instead:

```sh
uv run --project /absolute/path/to/checkout consensus-audit
```

Run the request:

```sh
consensus-audit run /absolute/path/to/request.md
```

Do not switch providers, repeat a valid run, or weaken a failed capability check. A low confidence or inconclusive result is a legitimate completed audit.

## Report the result

Read the committed `final.md` and report:

- the answer within its stated scope;
- the applicable audit or Discovery-consensus confidence score;
- the main material limitation;
- the final report path and run directory.

Do not call the score a probability or certification. Do not synthesize a replacement answer in the parent chat if reconciliation failed.

## Later questions

When the user asks whether the result is trustworthy, inspect the retained basis first:

```sh
consensus-audit inspect /absolute/path/to/run --verify
```

Do not rewrite a finalized run. A new investigation requires a new explicit request, preferably tied to new evidence or a stated challenge. Keep the earlier run.

## Boundaries

Managed roles receive only the bounded material selected by the controller. They have no shell, file, browser, app, skill, or subagent tools. They cannot produce runtime command evidence. If the question depends on tests, benchmarks, production data, or another unavailable observation, keep that limitation visible.

Never treat imported testimony as a machine observation. Never infer model identity or independence from a host name. Never rerun merely to seek agreement or a higher score.

Ordinary work on this repository does not start an audit.
