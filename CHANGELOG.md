# Changelog

## 1.14.1 — 2026-11-12

- The `joey` skill reads `joey_list_feedback_queue` for the people of each
  path before it asks for feedback. The capacity in `joey_whoami` gives no
  path people.
- At a full quota with no delivered path, the skill asks for no feedback. It
  tells the member that all slots wait for research.
- After feedback, the skill offers a held request only when a slot is free.
  `joey_find_better_path` feedback holds the slot again.
- A verdict on a report path with no activation has no MCP tool. The skill
  gives the `reportUrl`, where the member saves the verdict.
- Before an `INTRO_REQUESTED` write for an ask that the member sent outside
  Joey, the skill asks for the actual recipient, channel, subject, exact text
  and send time. It does not invent them.
- The tools reference activates only a `FOUND` intent company, with the steps
  of the `joey-activate-path` skill. It reuses a saved activation of the report
  path before it prepares a new one.
- Remove the rules for Joey servers before `2.4.0`. The hosted server now
  serves `2.4.0`.
- This release adds no tool and no argument, so `tools.json` does not change.

## 1.14.0 — 2026-11-11

- `joey_list_paths` and `joey_get_path_report` give `steps` (a number) and
  `entry` (`company`, `inside`, `steps`) for each path.
  `joey_list_feedback_queue` and `joey_list_opportunities` give `entry` for
  each path. The last `entry.inside` people of a path work at the target's
  company, and a hop between two of them is not a step.
- `hops` and `hopCount` stay the count of all hops. The `hops` filter of
  `joey_list_paths` keeps that count.
- The `joey` skill tells the member the length of a path in steps: "2 steps",
  or "2 steps into" the company when `entry.inside` is 2 or more. It does not
  say "hops" to the member. The progress step labels of a report, such as
  "Asked David", stay as they are.
- For a server before `2.4.0`, the skill says the count of hops as steps,
  with no company.
- This text needs the Pouch customer MCP release `2.4.0`. This release adds
  no tool and no argument, so `tools.json` does not change.

## 1.13.1 — 2026-11-10

- Remove the rules for Joey servers before `2.2.0`. The Joey server has version
  `2.3.0`. The rule for a server before `2.3.0` stays.

## 1.13.0 — 2026-11-09

- `joey_request_path` takes the new optional `roles` (1 to 3 items, a company
  URL only). Send the roles or the team that the member named, in the
  member's words. `roles` for a person URL fails with `INVALID_ROLES`.
- Without `roles`, a company request takes the first three roles of the ICP.
  If the ICP has no roles, Joey looks for anyone at the company.
- A company request never waits for an ICP, and the ICP never rejects a
  company. `icpScope` only chooses the ICP that gives the default roles. The
  delivery state `WAITING_FOR_ICP` is gone, and `delivery.url` is always null.
- The `joey` skill sends a named role or team as `roles`. It does not ask for
  a usable ICP before a company request. With no named roles, it uses the one
  ICP that has `roles`, and asks the member only when both ICPs have roles.
- To narrow a company request, send `joey_request_path` again with `roles`,
  the same `icpScope` and a new `idempotencyKey`. An open request of the
  member that waits for vetting and has no other subscriber changes its roles,
  takes no new slot and gives `narrowed: true`. Else Joey makes a separate
  request that holds one slot.
- For a server before `2.3.0`, the skill sends no `roles`, and a company
  request can wait for an ICP.
- This text needs the Pouch customer MCP release `2.3.0`. Copy its
  `tools.json` snapshot when `joey_request_path` has `roles`.

## 1.12.0 — 2026-11-06

- Read the new `joey_list_opportunities` (`workspace:read`, optional `level`)
  for the intent companies of the workspace. Each company has its level,
  summary, signal hits with dated evidence, and path state. To activate a
  path, use its `requestId` with the existing intro tools.
- This text needs the Pouch customer MCP release `2.2.0`. Copy its
  `tools.json` snapshot when it has `joey_list_opportunities`.

## 1.11.0 — 2026-11-05

- Each member has a path quota. Each target that the member asks for holds
  one slot. `pathRequests.capacity` in `joey_whoami`, and `capacity` in
  `joey_request_path` and `joey_get_path_request`, give `used`, `limit`,
  `limitSource` and `needsFeedback`. The workspace capacity, the weekly limit
  and `QUEUED_FOR_WEEKLY_CAPACITY` are gone.
- Read the new `joey_list_feedback_queue` (`workspace:read`, no input) for the
  open slots of the member and their delivered paths.
- A full quota refuses a new target, a live path search and an activation
  from a `pathRef` with `MEMBER_FEEDBACK_REQUIRED`. The next action is
  `GIVE_FEEDBACK`. `OPEN_CAPACITY_REACHED` and `QUOTA_OPEN_REACHED` are gone.
- The `joey` skill asks the member how open paths went before a new request.
  It records feedback only for an outcome that the member states, and it asks
  before it sends the held request.
- This text needs the Pouch customer MCP release `2.1.0`. Copy its
  `tools.json` snapshot when it has `joey_list_feedback_queue`.

## 1.10.0 — 2026-11-03

- A report hop has no `suspected` and no `check` field. Each hop is a real
  connection or shared context. Do not state a relationship that the hop's
  `explanation` and `sources` do not show.
- This text needs the Pouch customer MCP release that removes the two fields.

## 1.9.0 — 2026-10-29

- Read one person with the new `joey_get_person_context` (`entityRef`,
  `workspace:read`). It gives the status (`ready`, `stale` or `absent`), the
  dated current roles, career and education, up to 16 profile links and the
  cited sources. Quotes stay in the source language.
- The `joey` skill reads the person context before the connections. It uses
  career and education overlaps as leads, not as proof of a link.
- Copy the new tool entry of the Pouch customer MCP.

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
