# Changelog

## 1.3.1 — 2026-10-20

- Add the exact OAuth endpoints and a sign-in fault procedure.
- Keep callback, state, PKCE and token exchange with the host MCP client.
- Verify setup through `joey_whoami` before a success claim.
- Keep unexposed connector request fields unknown.
- Check connection URLs in the package tests.

## 1.3.0 — 2026-10-20

- Propose and prepare the next path action within the member's goal.
- Include paths that need their first request and reuse saved activations.
- Check relevant progress through connected host plugins in approved tasks.
- Create and verify approved reminders and repeated progress checks.
- Keep task scope, time zone, duplicate checks and stop conditions explicit.
- Require a new exact approval before each send. Resolve uncertain sends
  without duplicate contact.
- Add simulated path action cases. Keep the existing MCP contract.
- Add package tests and the ZIP build to CI for pull requests and `main`.

## 1.2.1 — 2026-10-20

- Allow the numeric `id` query in canonical Facebook profile URLs.
- Keep other identity URL queries invalid.

## 1.2.0 — 2026-10-19

- Find people, connections and warm paths in the live graph without a report.
- Keep confirmed profile identity, source attribution and unknown strength clear.
- Save private activation steps without a research request or delivered report.
- Use host message tools after exact recipient, channel and text approval.
- Keep intermediate progress separate from final-target progress.
- Add confirmed outcomes with separate consent, private sources and withdrawal.
- Refresh the generated MCP snapshot and the prompts for clients without skills.

## 1.1.1 — 2026-10-19

- Use four relationship strengths. A weak relationship is positive.
- Explain shared personal answers and attributed negative statements.
- Refresh the customer MCP tool snapshot from Pouch.
- Keep exact-text approval before each send.

## 1.1.0 — 2026-10-18

- Rename the path skills to `joey-activate-path` and `joey-path-follow-up`.
- Add a weekly update check when a skill runs.
- Clarify path activation, member claims and evidence limits.
- Distinguish a local statement save from graph delivery and withdrawal.
- Add `joey-attest` for member statements, consent for each chat, correction and
  withdrawal. Structured claims go to the Joey trust network; source excerpts
  stay private to the author.
- Add `joey-trust` for relationship context, source attribution, conflicts and
  derived trust support. Keep people, agent products and specific agents separate.
- Add `trust:read` and `trust:write` permissions. Refresh the Pouch MCP snapshot
  and keep all six skill ZIPs self-contained.
- The skills act only when the host loads or invokes them. The plugin has no
  background listener.

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
