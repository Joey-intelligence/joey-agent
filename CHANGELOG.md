# Changelog

## 1.0.1 — 2026-10-16

- `skills/joey/references/tools.json` is now the snapshot of the Pouch customer
  MCP. It lists the arguments of each tool and the server prompts.
- The tool reference and the skills use the real tool inputs and results:
  - `joey_request_path` takes `linkedinUrl` and `idempotencyKey`.
  - `joey_find_better_path` takes `preference` (`chip`, `text`) and
    `savePreference`.
  - `joey_set_intro_stage` takes `pathKey` and no note. `joey_stop_intro` takes
    no reason.
  - `joey_rate_familiarity` takes `pathKey` and `rating`.
  - `joey_get_intro_draft` returns `to` (`name`, `email`), `mode`,
    `viaTeammate` and `gmailUrl`.
- The package test checks that the tool reference lists the real arguments of
  each tool.

## 1.0.0 — 2026-10-16

- First release.
- The plugin connects the Joey customer MCP at
  `https://pouch.getjoey.io/api/customer/mcp` with OAuth sign-in, for Claude Code
  (`.mcp.json`) and Codex (`mcp.json`).
- Four skills: `joey`, `joey-make-intro`, `joey-intro-follow-up` and
  `joey-tracker-sync`.
- `scripts/build_skill_zips.py` makes one zip for each skill, for claude.ai.
