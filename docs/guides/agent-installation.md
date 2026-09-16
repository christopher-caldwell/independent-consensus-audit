# Install Independent Consensus Audit from an agent chat

Open this checkout in Codex, Claude Code, or Cursor and say:

```text
Install this skill for me.
```

To refresh the CLI and the current host's skill later, say:

```text
Update Independent Consensus Audit from this checkout.
```

To refresh every host where the skill is already installed on the same machine, say:

```text
Update Independent Consensus Audit from this checkout for every installed host.
```

The native entry file selects that host's skill destination. The agent performs the procedure below. This is a local skill installation backed by one shared uv-managed CLI; it does not install separate model providers.

## Instructions for the installing agent

### 1. Resolve the source

Use the checkout the user opened or explicitly supplied. For an update requested from an installed skill, use the source path in its `INSTALLATION.md` when that checkout still exists. Resolve the absolute path and confirm that `pyproject.toml` names `independent-consensus-audit`, and that `AGENT_GUIDE.md` and `skills/independent-consensus-audit/SKILL.md` exist. Confirm `uv --version`. Do not infer a registry package from the bare project name.

### 2. Install the CLI through uv

Inspect `uv tool list` and any existing `consensus-audit` executable. Install from the checkout:

```sh
uv tool install /absolute/path/to/independent-consensus-audit
uv tool dir --bin
```

For an existing installation from this project, refresh it even when the version is unchanged:

```sh
uv tool install --force --reinstall /absolute/path/to/independent-consensus-audit
```

Do not use an editable install for the normal personal installation. Resolve the executable inside the uv tool bin directory and verify it by absolute path rather than assuming the current shell refreshed `PATH`.

### 3. Install the shared skill

Copy the contents of `skills/independent-consensus-audit/` into the personal or explicitly requested project destination named by the current host entry file. Copy only the skill contents, including optional metadata and references. Do not copy the repository, `.git`, `.venv`, audits, artifacts, or build output.

Inspect the destination first. Back up an existing matching skill outside every scanned skill root before refreshing it. Do not overwrite an unrelated skill or edit managed plugin caches. Avoid duplicate copies in locations the same host scans.

An ordinary install or update changes only the current host's skill directory. When the user explicitly requests every installed host, inspect the normal Codex, Claude Code, and Cursor locations and refresh only existing directories whose `SKILL.md` declares `name: independent-consensus-audit`. Do not create missing host installations as part of an update.

Add `INSTALLATION.md` inside the installed skill directory. Record the absolute CLI path, uv path, source checkout, source commit when available, dirty-state observation, and CLI version. Do not record credentials. The note contains installation metadata only, not competing workflow rules.

### 4. Verify without starting an audit

From outside the checkout, run:

```sh
/absolute/uv-bin/consensus-audit --version
/absolute/uv-bin/consensus-audit guide
```

Confirm that the guide output matches the packaged shared workflow. Compare the installed `SKILL.md` with the source and confirm `INSTALLATION.md` exists. Do not create a test audit solely to prove installation.

Report every skill directory refreshed, any host location that was absent, the CLI path, and the verification result. Use `$independent-consensus-audit` in Codex and `/independent-consensus-audit` in Claude Code or Cursor. Tell the user to open a fresh session if a host has cached its skill list.

The host loading the skill is not the model provider used for managed audit roles. V1 always uses the locally configured Codex CLI and does not require Claude or Cursor subscriptions.
