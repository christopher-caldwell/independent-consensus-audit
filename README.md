# Independent Consensus Audit

Independent Consensus Audit asks several fresh investigators to examine the same engineering question, then gives their completed reports to a separate reconciler. The result is one Markdown answer with its evidence, disagreements, coverage gaps, and an audit confidence score.

You can also skip the investigation step and supply reports you already have. This is useful when Codex, Claude Code, and Cursor have each produced a separate Discovery document and you want one technical direction instead of three competing drafts.

The tool does not treat agreement as proof. A minority finding can decide the answer when its evidence is stronger. Missing checks stay visible, imported claims remain imported testimony, and a failed run cannot publish a reassuring score.

## What you get

Each run writes a directory under `audits/` unless the request chooses another location. Its main artifact is `final.md`. The same directory retains the request, frozen source identity, original reports, model attempts, accepted structured records, score calculation, and integrity manifest.

A completed audit can still be inconclusive or have low confidence. That is a valid result. It means the available material did not support a stronger answer.

## How the pieces fit

There is one shared workflow and one application:

```text
Codex skill       \
Claude Code skill  -> consensus-audit CLI -> local Codex CLI -> retained run bundle
Cursor skill      /
```

Codex, Claude Code, and Cursor are hosts for the same skill. They prepare the request, invoke the application, and present the retained result. Managed investigator and reconciler calls use the local Codex CLI through the account already configured on the machine.

The audit runtime does not require a Claude subscription. Using Claude Code as the host still requires access to Claude Code. Cursor also remains a host rather than a separate model provider. Version 1 has one execution adapter: Codex.

The instruction layout follows the same split:

- [`AGENT_GUIDE.md`](AGENT_GUIDE.md) contains the shared usage workflow.
- [`AGENTS.md`](AGENTS.md) contains Codex installation and invocation details.
- [`CLAUDE.md`](CLAUDE.md) contains Claude Code installation and invocation details.
- [`.cursor/rules/independent-consensus-audit.mdc`](.cursor/rules/independent-consensus-audit.mdc) contains Cursor installation and invocation details.
- [`skills/independent-consensus-audit/SKILL.md`](skills/independent-consensus-audit/SKILL.md) is the small installed loader that finds the CLI and reads its bundled guide.

The host files do not carry separate copies of the audit workflow.

## Install from an agent chat

Open this checkout in Codex, Claude Code, or Cursor and say:

```text
Install this skill for me.
```

The agent installs the application through uv, places the shared skill in its personal skill directory, and verifies both from outside the checkout. The full procedure is in the [agent installation guide](docs/guides/agent-installation.md).

After installation, start a fresh session and invoke:

- `$independent-consensus-audit` in Codex
- `/independent-consensus-audit` in Claude Code or Cursor

One uv tool installation can serve all three hosts on the same machine.

### Updating

Open the checkout in the host you want to refresh and say:

```text
Update Independent Consensus Audit from this checkout.
```

That updates the shared uv tool and the current host's skill copy. To refresh every existing Codex, Claude Code, and Cursor installation on the machine, say:

```text
Update Independent Consensus Audit from this checkout for every installed host.
```

The update checks each normal host location and changes only matching skill copies that already exist. It does not install the skill into a new host. Each refreshed host may need a new session before it sees the updated instructions.

## Run from the checkout

You need Python 3.11 or newer, uv, and a working local Codex CLI account.

```sh
uv sync
uv run consensus-audit --version
uv run consensus-audit guide
uv run consensus-audit run ./examples/investigation-request.md
```

To install the command yourself:

```sh
uv tool install /absolute/path/to/independent-consensus-audit
consensus-audit --version
```

The installed package includes its prompts and shared guide. It does not depend on the checkout or current working directory.

## Three common uses

### Check an implementation against a specification

Give the request a `target` and a `spec`. The final answer identifies demonstrated violations, supported requirements, and requirements that were not established. One concrete counterexample can support a strong finding of nonconformance without pretending the audit found every defect.

Start with [`examples/conformance-request.md`](examples/conformance-request.md).

### Investigate a bug or performance problem

Describe the observed symptom and label suspected causes as hypotheses. Investigators consider alternatives and state which observations would separate them. If the audit lacks runtime evidence, the final answer says so instead of presenting static inspection as measurement.

Start with [`examples/investigation-request.md`](examples/investigation-request.md).

### Reconcile existing reports

List the reports under `inputs`. The tool preserves their original bytes, normalizes each document separately, and reconciles the results without launching another full reviewer cohort. Duplicate documents do not create extra votes.

Start with [`examples/synthesis-request.md`](examples/synthesis-request.md).

For finalized Discovery runs, use `discovery_runs` rather than listing only their Markdown exports. This first-class workflow treats each finalized export as one verified opinion, retains only its four output artifacts, and finds the common ground among the opinions. It does not import underlying run artifacts or repeat Discovery's verification. The selected direction and its confidence use only adopted claims with strict-majority support; rejected alternatives and one-report optional details remain visible but cannot become decisive. It reports agreement separately from consensus confidence. Start with [`examples/discovery-synthesis-request.md`](examples/discovery-synthesis-request.md).

## Request format

An audit request is Markdown with YAML frontmatter:

```markdown
---
schema_version: 1
artifact: audit-request
target: ../my-project
spec: ../my-project/specs/feature.md
reviewers: 5
sources:
  - ./observations.txt
output_dir: ./audits
---

Determine whether the implementation satisfies the specification.
Identify concrete deviations and requirements that cannot yet be verified.
```

Only `schema_version` and `artifact` are required. The Markdown body must contain the actual question.

Relative paths are resolved from the request file, not from the shell directory. Without `inputs` or `discovery_runs`, `reviewers` defaults to 5 and an omitted `target` defaults to the request directory. When supplied reports are present, `reviewers` is invalid because they replace the initial reviewer cohort.

`discovery_runs` is mutually exclusive with `inputs`, `reviewers`, `target`, `spec`, and `sources`. Each entry may be a Discovery run directory with exactly one complete export, or that export directory itself. The importer requires a finalized handoff and retains `technical-spec.md`, `discovery-summary.md`, `handoff.json`, and `evidence-manifest.json`. Those four files form one verified opinion and never become additional votes. Referenced run artifacts remain behind Discovery's verification boundary.

Unknown fields, duplicate YAML keys, unsafe YAML tags, empty input lists, invalid ranges, and old quorum configuration fail before any model call.

## Commands

```text
consensus-audit run REQUEST.md
consensus-audit guide
consensus-audit inspect RUN_DIR [--verify]
consensus-audit rescore RUN_DIR --policy pilot-v1
```

`inspect` reads the retained result. With `--verify`, it recalculates artifact digests without calling a model. `rescore` also runs offline and writes a new score artifact without changing the original report.

Exit code 0 means the tool produced a valid final audit, including a limited or inconclusive one. Exit code 2 means the request was invalid. Exit code 3 reports an operational or capability failure. Exit code 4 means integrity or schema validation prevented a trustworthy result.

## Confidence means audit confidence

The `pilot-v1` policy returns one of six scores: 0, 25, 50, 70, 85, or 95. It never returns 100.

The score describes support for the final answer within its stated scope. It is not a probability, a certification, or a percentage of the specification implemented. The policy is deterministic for the same accepted record, but it is not empirically calibrated.

The broad shape is simple:

- 25 means the answer is still an assertion without adequate inspectable support.
- 50 means traceable reasoning or testimony exists, but primary support remains indirect or unverified.
- 70 means direct source material or observed behavior supports the scoped claim.
- 85 adds at least two eligible separated assessments, relevant coverage, and no unresolved material objection.
- 95 is reserved for a narrow decisive demonstration or counterexample that a fresh assessor checked.

When the answer depends on several claims, the weakest essential claim controls the score. Many easy facts cannot average away one unresolved dependency.

## Boundaries worth knowing

Managed roles receive a bounded copy of the permitted material inside their prompt. Their shell, file, browser, app, skill, and subagent tools are disabled. This keeps peer reports and controller state out of reach without relying on operating system specific sandbox code.

That choice also means managed roles cannot run tests, benchmarks, or profilers. When runtime evidence is necessary, the audit must remain limited and name the missing observation. Imported statements such as “tests passed” remain testimony unless the run contains the corresponding captured evidence.

Run bundles can contain private source code and supplied documents. Keep them local unless you have reviewed what they contain.

## Development

```sh
uv run pytest -q
uv build
```

The ordinary test suite uses scripted role outputs and does not require a live model. Fixture success proves the controller mechanics, not model judgment. See the [implementation delta](docs/implementation-delta.md) for the changes from the original instruction only repository.
