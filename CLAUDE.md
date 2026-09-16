# Independent Consensus Audit entry point for Claude Code

## Install or update the skill

Treat “install this skill”, “install Independent Consensus Audit”, or “update Independent Consensus Audit” as a request to install it for Claude Code. Follow [the shared installation procedure](docs/guides/agent-installation.md), using this checkout as the source. Installation does not start an audit.

“Update Independent Consensus Audit” refreshes the shared uv tool and this Claude Code skill. If the user says “update Independent Consensus Audit for every installed host,” also refresh matching Codex and Cursor skill directories that already exist. Do not create a new host installation unless the user asks for it. When updating from an installed skill rather than an open checkout, use the source recorded in its `INSTALLATION.md`.

Install `skills/independent-consensus-audit/` at `~/.claude/skills/independent-consensus-audit/`, or under `CLAUDE_CONFIG_DIR` when configured. Honor an explicit project installation by using `<project>/.claude/skills/independent-consensus-audit/`. No plugin or legacy command file is required.

After verification, tell the user to invoke `/independent-consensus-audit` in a fresh Claude Code session. A Claude subscription is not required for the audit runtime; the installed skill invokes the same local CLI, whose managed roles use Codex.

## Run an audit

Read [AGENT_GUIDE.md](AGENT_GUIDE.md), or run `consensus-audit guide` when using an installed copy. Ordinary repository work does not start an audit.
