---
name: independent-consensus-audit
description: Run or inspect evidence-aware independent audits through the local consensus-audit CLI.
metadata:
  version: "0.1.0"
---

# Independent Consensus Audit

This is the optional skill entry point. The complete, agent-neutral workflow is bundled with the CLI and returned by `consensus-audit guide`.

When the user asks to install or update the skill, do not start an audit. Read [references/update.md](references/update.md) and follow it using the scope the user requested.

When asked to run or inspect an audit:

1. If this installed skill has an `INSTALLATION.md`, read it and use the recorded absolute CLI executable.
2. Otherwise try `consensus-audit` on `PATH`, then the directory returned by `uv tool dir --bin`.
3. In a checkout, use `uv run --project /absolute/path/to/checkout consensus-audit`.

Verify the resolved executable with `--version` and `guide`, then follow the returned workflow. If no CLI or checkout is available, report the missing prerequisite rather than reproducing the audit in the parent chat.

For ordinary work developing this repository, follow the user's task without starting an audit.
