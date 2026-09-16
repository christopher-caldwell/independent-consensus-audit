# Independent Consensus Audit entry point for Codex

## Install or update the skill

Treat “install this skill”, “install Independent Consensus Audit”, or “update Independent Consensus Audit” as a request to install it for Codex. Follow [the shared installation procedure](docs/guides/agent-installation.md), using this checkout as the source. Installation does not start an audit.

“Update Independent Consensus Audit” refreshes the shared uv tool and this Codex skill. If the user says “update Independent Consensus Audit for every installed host,” also refresh matching Claude Code and Cursor skill directories that already exist. Do not create a new host installation unless the user asks for it. When updating from an installed skill rather than an open checkout, use the source recorded in its `INSTALLATION.md`.

Install `skills/independent-consensus-audit/` as the personal `independent-consensus-audit` skill. Default to `~/.agents/skills/independent-consensus-audit/`. If Codex already loads a direct copy from `${CODEX_HOME:-$HOME/.codex}/skills/independent-consensus-audit/`, refresh that location instead of creating a duplicate. Keep `agents/openai.yaml` with the skill.

After verification, tell the user to invoke `$independent-consensus-audit` in a new task. Do not edit plugin caches or claim the current task refreshed its cached skill.

## Run an audit

Read [AGENT_GUIDE.md](AGENT_GUIDE.md), or run `consensus-audit guide` when using an installed copy. The host is not the execution provider: managed roles use the configured local Codex CLI. Ordinary repository work does not start an audit.
