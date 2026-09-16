# Update the installed skill

Use the source checkout recorded in `INSTALLATION.md`. If it is missing or unavailable, use a checkout the user explicitly supplied. Do not guess a registry or repository source.

For an ordinary update, refresh the shared uv tool from that checkout, then refresh this skill directory from `skills/independent-consensus-audit/`. Preserve a new `INSTALLATION.md` with the resolved CLI path, uv path, source path and commit, dirty state, version, installation scope, and update time. Keep the prior installation in a backup outside scanned skill roots until verification succeeds.

If the user explicitly asks to update every installed host, inspect the normal Codex, Claude Code, and Cursor skill locations. Refresh only existing directories that contain this skill's matching `name` in `SKILL.md`. Do not create a skill for a host where it is not already installed, overwrite an unrelated skill, or edit managed plugin caches.

Install the CLI once:

```sh
uv tool install --force --reinstall /absolute/path/to/checkout
```

Verify the absolute installed executable from outside the checkout with `--version` and `guide`. Compare each refreshed `SKILL.md` with the source. Tell the user which host copies were refreshed, which were absent, where the CLI lives, and whether a new host session is required to reload the skill.
