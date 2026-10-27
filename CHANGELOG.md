# Changelog

## 1.8.0 — 2026-10-27

- Document the `TRACKING` stage of a company workspace intro. A member starts
  to track a path before the first request and becomes its owner.
- Read the intro `owner` and the `progress` steps that the web shows, such as
  "Asked David" and "Introduced to Sarah", in `joey_get_path_report` and
  `joey_get_intro_tracker`. The tracker also gives `members`.
- Move a company report intro to a step with the new `joey_set_intro_progress`.
  Give `pathKey` to track or move to a specific path of `progress.paths`. Only
  the `ASKED` step needs the approval and send receipt of `INTRO_REQUESTED`.
  A failed send gives `SEND_FAILED`. A later step needs the member's
  confirmation and no receipt. Give the intro to another member with the new
  `joey_set_intro_owner`, after a yes.
- Use the progress steps in the tracker sync and follow-up flows. Activations
  and personal workspaces keep `joey_set_intro_stage`.
- Copy the two new tool entries of server version 1.4.0.

## 1.7.0 — 2026-10-26

- Let each member keep a personal ICP beside the workspace ICP. Read both
  with `joey_get_icp`. Change the member's own ICP with `joey_update_my_icp`
  or remove it with `joey_clear_my_icp`, after a yes. No admin is necessary.
- Before a company request, ask the member which ICP to use when both are
  usable. When only one is usable, use it and name it. Send `icpScope`
  `PERSONAL` for the member's own ICP.
- Document the `personal-icp:write` scope, the errors
  `PERSONAL_ICP_REQUIRED` and `INVALID_ICP_SCOPE`, and the new `SET_ICP` rule.
- Copy the tool snapshot of server version 1.3.0.

## 1.6.0 — 2026-10-23

- Give the installed release to `joey_whoami` as `pluginVersion`. The Joey
  server gives `agentPlugin` and tells the agent about a new release. The
  skills no longer read the release page.
- After a yes, update the plugin with the steps of the host. In Claude Code,
  also turn on marketplace auto-update, so later releases need no reminder.
- Report a mechanical Joey failure with the new `joey_report_bug` and tell the
  member in one line. Send a problem that the member reports only after a yes.
- Copy the tool snapshot of server version 1.2.0.

## 1.5.0 — 2026-10-22

- Continue a new connection into a first run: one identity line, the
  onboarding step from `joey_whoami`, one goal question and a first path.
- Give the web link of each onboarding step and of a next action to the
  member. Never confirm a profile for the member.
- Ask for the missing facts of a brief in one question.
- Run the weekly update check only for uploaded skills, after the first
  result, and with no new permission. Plugin manager installs skip it.
- Add install steps for Claude Duet, Muse, Grok, Grok Bot and Dots, and a
  quick start with the setup prompt.

## 1.4.0 — 2026-10-21

- Follow `outcome`, `reason.code` and `recommendedNextAction` of each graph
  read and each error. Keep `NOT_IN_GRAPH`, `AMBIGUOUS`, `IDENTITY_UNRESOLVED`
  and `NO_PERMISSION` separate.
- Find a company and its people with `joey_search_graph_companies`. Select a
  company from `company.candidates` of a company path search.
- Read request capacity in `joey_whoami` before a request. Report the delivery
  state and its estimate. Read a request again with `joey_get_path_request`.
- Apply the same rules to scheduled and interactive calls. Report an unknown
  denial code as a host limit.
- Detect the server version through `joey_whoami`. Copy the new tool snapshot.

## 1.3.2 — 2026-10-20

- Require explicit member strength for each new or corrected positive relationship.
- Ask for a missing strength before a save. Preserve old unknown records on read.
- Keep trust, no-acquaintance and confirmed outcomes separate from familiarity.

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
