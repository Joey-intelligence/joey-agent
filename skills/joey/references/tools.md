# Joey MCP tool reference

The Joey customer MCP is at `https://pouch.getjoey.io/api/customer/mcp`. Each
tool acts for one member in one workspace. The member chose the workspace when
the member approved the agent.

The input schema that the server sends is the authority. If this page and the
schema do not agree, follow the schema. [tools.json](tools.json) lists the
tool names, scopes, arguments and prompts.

Each result has the form `{data}`. A service error has a stable `code` and
`recommendedNextAction`. Input errors can have `isError` and text without a
service code. See [Errors](#errors) and
[Outcomes and next actions](#outcomes-and-next-actions).

`joey_whoami` gives `server.version` and `server.changes`. This page describes
server version `1.1.0`. An earlier server gives no `outcome`,
`recommendedNextAction`, `delivery`, `joey_search_graph_companies` or
`joey_get_path_request`.

## Scopes

| Scope | Who | Tools |
| --- | --- | --- |
| `workspace:read` | All members | Workspace read tools |
| `intros:write` | All members | Introduction and target write tools |
| `icp:write` | Workspace admins only | `joey_update_icp` |
| `trust:read` | Members with this permission | Trust subject lookup, own statements and trust context |
| `trust:write` | Members with this permission | Capture sessions, subjects, statements and withdrawal |

A member who is not an admin does not see `joey_update_icp`. Personal workspaces
have fewer report and workspace tools. Use the connected server schema. Live
graph reads and private activations work for personal and company workspaces.
Shared graph reads also need `trust:read`; shared outcomes need both trust scopes
and separate outcome consent. Public graph context access adds no new charge.

## Scheduled and interactive calls

Joey sees only the connection's token. It applies the same scopes, limits and
errors to scheduled, background and interactive calls. `joey_whoami` gives
`contextPolicy.scheduledCalls: "SAME_AS_INTERACTIVE"`. A Joey HTTP refusal has
a JSON `code` and `recommendedNextAction`, for example `ORIGIN_NOT_ALLOWED` or
`RATE_LIMITED`. A denial with a code that this page does not give, such as
`read_only_preparation`, comes from the host or its proxy. Report it as a host
limit. Do not retry it in a loop.

## Host tools and scheduled work

Joey supplies path context, drafts and progress records. It has no message-send
tool or scheduler. Inspect connected host plugins for the required message,
contact, calendar and task tools. Use their actual schemas and the member's
authorized account. A Joey connected-account record alone grants no host access.

The `joey` skill proposes and prepares the next action within a path goal.
The `joey-activate-path` skill sends through the host only after exact approval
and records a matching receipt. The `joey-path-follow-up` skill creates and
verifies approved host reminders or repeated checks. The `joey-tracker-sync`
skill reads only relevant evidence within the agreed account and task scope.
Stage changes still need the member's actual confirmation.

A host schedule must use durable activation or report references and the
correct member and workspace. It must not keep an old scoped `pathRef`, a whole
report or an old send approval as permission for future contact. Each send
needs a new exact yes. Keep unchanged checks quiet and end the task at its
approved stop condition. The plugin adds no background listener or connection
hook. A server prompt alone does not create a schedule.

## Read tools

### joey_whoami

- Input: none.
- Result: `user` (`id`, `name`, `email`), `workspace` (`id`, `name`), `role`
  (`ADMIN` or `MEMBER`), `scopes`, `client`, `capabilities` and `graphIdentity`.
  Identity has status, revision, confirmed entity reference/profile URL and a
  hidden-edge reason. `CLAIMED` is the confirmed profile state; a missing
  profile must not become a synthetic account node.
- Also: `server` (`name`, `version`, `changes`), `pathRequests.capacity` (see
  [Capacity](#capacity)) and `contextPolicy` (see
  [Scheduled and interactive calls](#scheduled-and-interactive-calls)).
- Also: `onboarding` (`complete`, `steps`, `nextStep`). Each step has `step`
  (`CONFIRM_PROFILE`, `SET_ICP` or `CONNECT_ACCOUNTS`), `status` (`DONE`,
  `TODO` or `NOT_AVAILABLE`), `required`, `url` and `text`. `nextStep` is the
  first required step that is `TODO`, or null. `url` is the page of the Joey
  web app where the member does the step; it is null in a personal workspace.
  Only `CONFIRM_PROFILE` blocks a default path search. A member who cannot set
  the ICP gets `NOT_AVAILABLE`; a workspace admin sets it. Give `text` and
  `url` to the member once. Do not do the step for the member.
- Read `pathRequests.capacity` before `joey_request_path`.
- Call it first when the task needs workspace context and `workspace:read` is
  present. A known-statement or known-session withdrawal needs only
  `trust:write` and can proceed without this read.

### joey_list_connected_accounts

- Input: none.
- Result: the member's connected provider accounts and current access state.
  This read contains no provider credentials.
- Use it when the member asks which accounts Joey can use.

### joey_list_paths

- Input:
  - `introStage` (optional): one of the [intro stages](#intro-stages), or
    `STOPPED` for stopped intros.
  - `savedOnly` (optional): `true` gives only saved targets.
  - `query` (optional): a part of a name: the target, the target company, or a
    person on a path.
  - `company` (optional): the exact company name of the target.
  - `hops` (optional): 1 to 4. Only the targets whose best path has this number
    of hops.
  - `limit` (optional): 1 to 50 rows on one page. The default is 20.
  - `cursor` (optional): the `nextCursor` of the last page.
- Result: `{paths, total, nextCursor}`. One row for each target with a
  delivered path. Open intros come first, then the newest paths. Each row has:
  - `requestId` and `target` (`name`, `role`, `organization`).
  - `hops`, `strength` (a [strength word](#strength-words)) and `people` of the
    best path. `people` gives the names in order, with "(you)" after the member.
  - `pathCount`, `lastDeliveredAt`, `intro` (see [Intro state](#intro-state)),
    `savedTarget` and `betterPathOpen`.

### joey_get_path_report

- Input:
  - `requestId`: from `joey_list_paths`.
- Result: the report of one target:
  - `target` (`name`, `role`, `organization`).
  - `paths`: each delivered path, path 1 (the best path) first. Each path has
    `pathKey`, `number`, `name`, `summary`, `hopCount`, `strength`,
    `deliveredAt` and `verifiedAt`, and:
    - `people`: the people in order, each with `name`, `role`, `organization`
      and `you`.
    - `hops`: each hop with `from`, `to`, `title` (for example "You and David
      Cohen"), `explanation`, `strength`, `basis` ("Public source", "Inferred"
      or "User-confirmed"), `suspected`, `check` and `sources` (`label`, `url`).
      `check` is set for a suspected hop: it says what to ask to find out if the
      two people know each other.
    - `askTo`: the person to write to: `name`, `mode` (`ASK_INTRO` or
      `REACH_OUT`), `viaTeammate` and `email` (it can be `null`).
    - `rate`: the person that `joey_rate_familiarity` rates on this path
      (`name`, `rating`), or `null`.
  - `intro` (with the `pathKey` of the path that the intro uses),
    `savedTarget` and `betterPath` (`open`, `lastPreference`).

### joey_get_intro_draft

- Input:
  - `requestId` (optional): a delivered report. Select this or `activationId`.
  - `activationId` (optional): a saved activation from a live path or delivered report. Select this or `requestId`.
  - `stepIndex` (optional): the selected activation step; default 0.
  - `pathKey` (optional): the selected report path.
  - `regenerate` (optional): request a new report draft.
- Result: a draft for the next recipient. A live draft has `activationId`,
  `stepIndex`, `to` (`recipientRef`, nullable `entityRef`, `name`, `email`), `target`, `subject`, `body`,
  `brief`, `briefDisclosure` and `recipientInterest: "UNKNOWN"`. The live path is
  revalidated. A report draft has `pathKey`, `to` (`recipientRef`, `name`,
  `email`), `mode`, `viaTeammate`, `contextChips`, `gmailUrl` and `cached`.
- Keep `to.recipientRef` as the send's `recipientRef` for an activation or
  report draft. A report person can have no canonical `entityRef`. An absent email address is not permission to guess one.
  Adapt the draft to the requested host channel. Show exact recipient, channel,
  subject and text before a send. A draft or compose link is not a send.

### joey_get_intro_tracker

- Input:
  - `stage` (optional): one of the [intro stages](#intro-stages), or `STOPPED`.
  - `staleDays` (optional): only the open intros (not `MET`, not stopped) with
    no change for at least this number of days.
- Result: `{counters, openCount, rows, activations, activationCompleteness}`.
  Activations have revisions, per-step stages and private outcomes. The result
  has limits of 100 activations and 500 outcomes. Check completeness before a
  claim that all records are shown. A stage filter can match an intermediate
  step; final-stage progress remains separate.
  - `counters`: `pathsDiscovered`, `introsRequested`, `introsMade` and
    `meetings`.
  - Each row has `requestId`, `target` (`name`, `organization`), `connector`,
    `intro`, `daysSinceChange`, `requestedAt` and `stageTimes` (the date of each
    stage). `connector` gives the names of the people between the member and the
    target. The first name is the person that the member asks.

### joey_list_path_preferences

- Input: none.
- Result: `{preferences, limit}`. Each preference has `preferenceId`, `chip`,
  `text` and `createdAt`. A member can save at most 10.

### joey_list_prospects

- Input:
  - `query` (optional): a part of a company name, a person name or a role.
  - `limit` (optional): 1 to 50 prospects on one page. The default is 20.
  - `cursor` (optional): the `nextCursor` of the last page.
- Result: `{prospects, nextCursor}`. Each prospect has `prospectId`,
  `company`, `person`, `role`, `priority`, `status` and `updatedAt`. Saved
  targets have the priority `HIGH`.

### joey_get_icp

- Input: none.
- Result: the ICP of the workspace: `description` (free text), `roles`,
  `industries`, `countries`, `employeeRanges`, `usable` and `version`.

## Write tools

### joey_request_path

- Input:
  - `linkedinUrl`: the LinkedIn URL of a person
    (`https://www.linkedin.com/in/...`) or of a company
    (`https://www.linkedin.com/company/...`).
  - `idempotencyKey`: see [Idempotency keys](#idempotency-keys).
- Result: `{requestId, status, targetUrl, targetKind, deliveredPaths,
  capacity, delivery}`. Joey researches the path. The path shows in
  `joey_list_paths` when Joey delivers it. See [Capacity](#capacity) and
  [Delivery state](#delivery-state). A personal workspace also gives `created`.
- `status: "SEARCHING"` means that Joey researches the target. It does not
  promise a delivery date. Read `delivery.state` for that.
- If the workspace asked for this target before, the member joins that request.
- A full open request limit refuses the request with `OPEN_CAPACITY_REACHED`
  or `QUOTA_OPEN_REACHED`. Joey saves no request then.

### joey_get_path_request

- Input:
  - `requestId`: from `joey_request_path`.
- Result: the same shape as `joey_request_path`, read again. Use it to report
  the current research and delivery state of a request. Company and personal
  workspaces have it.

### joey_save_target

- Input:
  - `requestId`: from `joey_list_paths`.
  - `saved` (optional): `true` (the default) saves the target. `false` removes
    the save.
- Result: `{savedTarget, prospectId}`. A saved target is a prospect with high
  priority.

### joey_find_better_path

- Input:
  - `requestId`: from `joey_list_paths`.
  - `preference`: a `chip`, a `text`, or both.
    - `chip` is one of the [preference chips](#preference-chips).
    - `text` is the member's own words, at most 280 characters.
  - `savePreference`: `true` saves the preference for future searches.
    `false` uses it only for this search.
  - `idempotencyKey`: see [Idempotency keys](#idempotency-keys).
- Result: `{open, preference, saved}`. A target has at most one open search.

### joey_set_intro_stage

- Input:
  - `requestId` (optional): a delivered report. Select this or `activationId`.
  - `activationId` (optional): a saved activation from a live path or delivered report. Select this or `requestId`.
  - `expectedRevision` (optional): required for an activation change.
  - `idempotencyKey` (optional): new UUID for an activation action; same key for an exact retry.
  - `stepIndex` (optional): selected activation step; default 0. A report
    `requestId` alone refuses this field; prepare its activation first.
  - `confirmation` (optional): the member's actual progress confirmation; required for later activation stages.
  - `approval` (optional): required for `INTRO_REQUESTED`. Exact `recipientRef`,
    actual `recipient`, `channel`, `subject`, `text` and affirmative `response`.
  - `sendReceipt` (optional): required for `INTRO_REQUESTED`. Required fields
    are `recipientRef`, actual `recipient`, `channel`, `subject`, exact `text`,
    `status`, `source`, `messageReference` and `sentAt`. The first five fields
    must equal the corresponding approval fields.
  - `stage`: one of the [intro stages](#intro-stages).
  - `pathKey` (optional): selected report path; omit for an activation.
- Result: current report intro or activation with its revision and steps.
  `SENT` must match the exact approved version. `FAILED` changes no progress.
  Channels are `EMAIL`, `SLACK`, `SMS` or `OTHER`; use null for no subject.
  Source is `HOST_TOOL_REPORTED` or `MEMBER_CONFIRMED`, as the evidence requires.
  A receipt proves only the reported send. It creates no relationship edge.
- Intermediate activation stages do not advance the final target. The next
  step requires the preceding introduction. Other stage changes need actual
  member confirmation. A calendar date alone does not prove a completed meeting.
  A changed revision needs a fresh tracker read. A stopped record takes no change.

### joey_stop_intro

- Input:
  - `requestId` (optional): delivered report. Select this or `activationId`.
  - `activationId` (optional): saved activation. Select this or `requestId`.
  - `expectedRevision` (optional): required for an activation stop.
  - `idempotencyKey` (optional): required new UUID for an activation action.
- Result: stopped report intro or private activation. A stop is final.
  Ask the member before the call. A repeat with the same action key changes nothing.

### joey_rate_familiarity

- Input:
  - `requestId`: from `joey_list_paths`.
  - `pathKey` (optional): the path. Path 1 if you do not give it.
  - `rating`: `weak`, `medium`, `strong` or `very_strong`, or `null` to remove the
    answer.
- Result: `{pathKey, person, rating}`. The tool rates the next person after the
  member on the path: the `rate` person of `joey_get_path_report`.
- Joey shares all old and new personal relationship answers as attributed member statements.
  Other members can see the member as a possible introducer on relevant paths.
- Weak is positive. An explicit No needs the `joey-attest` skill; it is not a weak rating.

### joey_delete_path_preference

- Input:
  - `preferenceId`: from `joey_list_path_preferences`.
- Result: `{deleted, preferenceId}`.

### joey_update_icp

- Input:
  - `expectedVersion`: the `version` from `joey_get_icp`.
  - `description` (optional): free text, at most 2000 characters.
  - `roles` (optional): job titles, at most 20.
  - `industries` (optional): at most 20.
  - `countries` (optional): two-letter country codes, at most 50.
  - `employeeRanges` (optional): for example `51-200` or `5001+`.
- Result: the new ICP and its new version.
- A field that you do not give keeps its value.
- Only an admin with the `icp:write` scope can call it. Read the ICP first and
  send its version as `expectedVersion`. If another person changed the ICP
  after your read, the call fails with `ICP_CHANGED`.

## Values

### Intro stages

| Stage | Meaning |
| --- | --- |
| `PATH_FOUND` | Joey delivered the path. Nobody asked for the intro yet. |
| `INTRO_REQUESTED` | The member asked the introducer for the intro (or wrote to the target for a REACH_OUT). |
| `INTRODUCED` | The introducer made the introduction. |
| `MEETING_SET` | The member and the target set a meeting. |
| `MET` | The member and the target met. |

A stop (`joey_stop_intro`) ends the intro at any stage after `PATH_FOUND`.

### Intro state

Each `intro` has `stage`, `stopped`, `stoppedAt`, `updatedAt`, `source`,
`agentClient` and `actorName`.

- `source` is `AGENT` when an agent made the last change. Then `agentClient`
  gives the name of the agent.
- `actorName` is the member who made the last change.

### Strength words

Each hop has one strength word. The word comes from the Joey graph. The strength
of a path is the word of its weakest hop.

| Word | What to tell the member |
| --- | --- |
| Very strong | The strongest tie that Joey records. The ask is easy. |
| Strong | A clear, direct tie. |
| Moderate | A real tie with less contact. Give the introducer a clear reason. |
| Light | The weakest tie. Ask the introducer how well they know the person first. |

### Preference chips

| Chip | Words in the Joey app |
| --- | --- |
| `KNOW_WELL` | People I know well |
| `FORMER_COLLEAGUES` | Former colleagues |
| `EMPLOYEES` | Employees |
| `CUSTOMERS` | Customers |
| `FRIENDS` | Friends |
| `SAME_COMPANY` | Same company (people at the target company) |

### Familiarity ratings

| Rating | Words in the Joey app |
| --- | --- |
| `weak` | Weak |
| `medium` | Medium |
| `strong` | Strong |
| `very_strong` | Very strong |

### Capacity

`capacity` has `openUsed`, `openLimit`, `weekDelivered`, `weekLimit`,
`limited`, `openRemaining`, `weekRemaining`, `weekStart` and `weekResetsAt`.
`null` in `openRemaining` or `weekRemaining` means no limit. With
`limited: false`, the workspace has no open request limit and no weekly
delivery limit; `openLimit` and `weekLimit` then give only the nominal values.

### Delivery state

`delivery` has `state`, `reason`, `queuePosition`, `pathFound`,
`estimatedDelivery` and `message`. For `WAITING_FOR_ICP`, `url` gives the
ICP page of the Joey web app, and `message` says who can set the ICP.

| `state` | Meaning |
| --- | --- |
| `RESEARCHING` | Joey researches the target, and the week has capacity. |
| `QUEUED_FOR_WEEKLY_CAPACITY` | The weekly limit is full. A found path waits for a later week. `queuePosition` and `estimatedDelivery` (`notBefore`, `notAfter`, `basis: "ESTIMATE"`) are set. |
| `DELIVERED` | The member can read a delivered path. |
| `WAITING_FOR_ICP` | A company request waits for the workspace ICP. |
| `READY_NO_PATH` | The research ended without a delivered path. |
| `UNAVAILABLE` | Joey cannot research this target. |

An estimate can change. Do not promise a date to the member.

## Outcomes and next actions

`joey_search_graph_people`, `joey_search_graph_companies` and
`joey_find_graph_paths` give `outcome`, `reason` (`code`, `message`) and
`recommendedNextAction` (`action`, `tool`, `missingScopes`, `text`, `url`).
`url` is a page of the Joey web app for a member step, or null. `status` keeps
its old values.

| `outcome` | Meaning | `reason.code` |
| --- | --- | --- |
| `MATCHED` | One person has the profile, or one company has exactly the name. | `PROFILE_MATCHED`, `COMPANY_MATCHED` |
| `CANDIDATE` | One name match. It is not an identity. | `NAME_SINGLE_CANDIDATE`, `COMPANY_CANDIDATES` |
| `AMBIGUOUS` | More than one match. The member selects one. | `NAME_CANDIDATES`, `PROFILE_CANDIDATES`, `COMPANY_CANDIDATES` |
| `NOT_IN_GRAPH` | No match in the current graph. | `NAME_NOT_FOUND`, `PROFILE_NOT_FOUND`, `COMPANY_NOT_FOUND`, `COMPANY_HAS_NO_CURRENT_PEOPLE` |
| `IDENTITY_UNRESOLVED` | A record exists, but Joey cannot read its canonical person now, or the selected people are not current. | `PROFILE_NOT_CANONICAL`, `TARGET_NOT_CURRENT` |
| `NO_PERMISSION` | The only paths use shared member evidence. The connection has no `trust:read`. | `MEMBER_PERMISSION_REQUIRED` |
| `PATHS_FOUND` | Joey found current paths within the limits. | `PATHS_FOUND` |
| `NO_PATH_WITHIN_LIMITS` | The target is known, but no path is within the limits. | `NO_PATH_WITHIN_LIMITS`, `SEARCH_INCOMPLETE` |

Next action codes: `FIND_PATHS`, `CONFIRM_CANDIDATE`, `SELECT_CANDIDATE`,
`SELECT_COMPANY`, `REQUEST_RESEARCH`, `ASK_FOR_PROFILE_URL`,
`SEARCH_PERSON_AGAIN`, `RETRY_LATER`, `WIDEN_SEARCH`, `READ_PATH_CONTEXT` and
`RECONNECT_WITH_SCOPE`. A next action is advice. It grants no permission and
it is not the member's request. `missingScopes` names the scopes of the step
that the connection does not have. Use `REQUEST_RESEARCH` only when the member
asks for research, and only with a confirmed URL.

## Idempotency keys

`joey_request_path` and `joey_find_better_path` take an `idempotencyKey`.

1. Make a new random UUID for each new request.
2. Use the same key again only when you retry the same call with the same
   input.
3. Do not use one key for two different requests.

## Errors

| Error | What to do |
| --- | --- |
| HTTP 401 or an auth error | Tell the member to connect Joey again in the agent (for example `/mcp` in Claude Code). |
| `FORBIDDEN` or `NOT_FOUND` | The path is not in this workspace, or the member has no access. Do not retry. |
| `RATE_LIMITED` or `DRAFT_LIMIT` | Stop. Tell the member to try again later. Do not loop. |
| `DRAFT_UNAVAILABLE` or `DRAFT_FAILED` | Joey cannot write the draft now. Write the email with the member from the report. |
| `ICP_CHANGED` | Read the ICP again. Show the new version to the member before a new change. |
| `INTRO_STOPPED` | The intro is stopped. Tell the member. Do not change it. |
| `INTRO_NOT_STARTED` | The intro is not requested yet, so it cannot stop. |
| `BETTER_PATH_OPEN` | Joey already looks for a better path to this target. Tell the member to wait for it. |
| `OPEN_CAPACITY_REACHED` or `QUOTA_OPEN_REACHED` | The workspace has the most open searches that it can have. Joey saved no request. Tell the member. |
| `GRAPH_IDENTITY_UNRESOLVED` | The member's public profile is not confirmed. Ask the member to confirm it in Joey, or select explicit `originRefs`. |
| `GRAPH_UNAVAILABLE`, `GRAPH_BUSY` or `GRAPH_MEMBER_SYNC_PENDING` | Try again later. Do not loop. |
| `ORIGIN_NOT_ALLOWED` (HTTP 403) | A browser page called the MCP. Call it from the MCP client. |
| `RATING_NOT_ALLOWED` | This path has no person that the member can rate. Do not retry. |
| `TARGET_COMPANY_REQUIRED` | Joey does not know the company of the target, so it cannot save the target. |
| `INVALID_TARGET_URL` | Ask the member for a LinkedIn person or company URL. Do not guess one. |
| `IDEMPOTENCY_CONFLICT` | The key has different content. Inspect the earlier action before a new write; do not duplicate an uncertain save. |
| Other code | Tell the member the code in plain words. Do not guess a cause. |

Each Joey error also gives `recommendedNextAction` (`action`, `tool`, `text`,
`url`). Follow it when it fits the member's task. `GRAPH_IDENTITY_UNRESOLVED`
gives the profile page of the Joey web app in `url`. Give it to the member.
Never confirm a profile for the member.

## Server prompts

Clients without skills can use these prompts. The skills in this plugin do the
same work.

| Prompt | Arguments | Same as |
| --- | --- | --- |
| `joey_make_intro` | one `requestId`, `pathRef` or `activationId` | the `joey-activate-path` skill |
| `joey_follow_up` | none | the `joey-path-follow-up` skill |
| `joey_weekly_review` | none | the `joey` skill and the `joey-path-follow-up` skill |

## Connected account metadata

### joey_get_connected_account_candidates

- Input:
  - `query` (optional): a name or text filter.
  - `limit` (optional): the maximum candidate count.
  - `cursor` (optional): the next page cursor.
- Result: account metadata that the member permitted for this workspace. Contacts
  are candidates, not relationship proof. Private evidence stays private.

## Relationship and trust tools

Existing OAuth grants do not receive trust permissions automatically. Reconnect
Joey to select them. Use the server input schema for nested statement fields.

### joey_resolve_trust_subject

- Input:
  - `query`: a name, subject ID or identity URL.
  - `kind` (optional): `PERSON`, `AGENT_PRODUCT` or `AGENT_INSTANCE`.
  - `limit` (optional): 1 to 50.
- Result: `{subjects, incomplete}`. A name match is a candidate. Never merge by name.

### joey_register_trust_subject

- Input:
  - `sessionId`: the active capture session.
  - `idempotencyKey`: a new UUID for this request.
  - `kind`: `PERSON`, `AGENT_PRODUCT` or `AGENT_INSTANCE`.
  - `label`: the subject name.
  - `identityUri` (optional): a public HTTPS identity URL without credentials or fragment.
    A canonical Facebook profile URL can contain its numeric `id` query. Other query parameters are not permitted.
  - `subjectId` (optional): the member's unresolved record to identify.
  - `expectedRevision` (optional): its current revision; required with `subjectId`.
- Result: the distinct subject, identity status, identity basis and revision.
  A member-provided URL does not prove ownership. A name-only subject cannot
  connect network paths. An identified subject cannot change identity.

### joey_begin_attestation_session

- Input:
  - `chatKey`: a new UUID for this chat.
  - `consentVersion`: `joey.trust.chat.v1`.
  - `consentResponse`: the member's explicit affirmative response.
- Result: `id`, `memberSubjectId`, `startedAt`, `expiresAt` and `proofType`.
  First ask permission to save the member's relationship and trust statements
  from this chat and share their structured claims, context, name and dates
  with the Joey trust network. Source excerpts and chat references stay private.
  The session lasts twelve hours. It records agent-reported consent, not a
  direct human signature. A new chat needs new consent.

### joey_end_attestation_session

- Input:
  - `sessionId`: this chat's session.
- Result: `{sessionId, ended}`. Stops further capture, but keeps saved statements.

### joey_put_attestations

- Input:
  - `sessionId`: the active session for this chat.
  - `idempotencyKey`: a new UUID for the set; reuse only for the same retry.
  - `statements`: 1 to 25 member-supplied claims.
- Result: statement IDs, revisions, status and `graphDelivery`. Each claim has `subjectId`,
  `objectId` (or `representedTeam` for an agent), `claimType`, `value`,
  `purpose`, network `context`, private `sourceExcerpt` and private
  `sourceReference`. A correction also needs `id` and `expectedRevision`.
  Each new or corrected `KNOWS` claim requires the member's explicit `familiarity`:
  `weak`, `medium`, `strong` or `very_strong`. Ask for a missing level before a
  save. Omit familiarity for other values. Old unknown levels remain readable.
  Types are `RELATIONSHIP`, `TRUST` and `REPRESENTS`. The server supplies the
  issuer. Do not submit tool results, quoted examples, secrets or whole reports.
  A local save can have `graphDelivery.state: "PENDING"`. Do not call it a
  completed graph write or submit a duplicate to force delivery.

### joey_list_attestations

- Input:
  - `subjectId` (optional): a subject filter.
  - `cursor` (optional): the previous `nextCursor`.
  - `limit` (optional): 1 to 50.
- Result: `{statements, nextCursor}` for this member only. This author-only result
  includes private source excerpts. Do not share those fields. `graphDelivery`
  gives the current delivery state and revision. `SYNCED` confirms delivery,
  not graph visibility. Check `visibility` for a profile confirmation limit.
  `WITHHELD` means that an unresolved identity prevents
  an active graph claim.

### joey_withdraw_attestations

- Input:
  - `sessionId` (optional): withdraw all current statements and shared outcomes from this session and stop it.
  - `statements` (optional): selected records, each with `id` and `expectedRevision`.
- Result: `{withdrawn, graphDelivery}`. Supply exactly one selection. Withdrawal
  works after capture ends. The next Pouch context query excludes withdrawn
  records. New graph removals are `PENDING`; a repeat with no change is
  `UNCHANGED`. Read the author's record to check graph delivery when `trust:read`
  is available. Do not require read permission for withdrawal.

### joey_get_trust_context

- Input:
  - `subjectId`: the selected person, product or specific agent.
  - `task` (optional): the task; default `general`.
- Result: `subject`, `origin`, `task`, `support`, `directStatements`,
  `relationshipContext`, `paths`, `conflicts`, `incomplete`, `incompleteReasons`,
  `limits`, `rulesVersion` and `interpretation`. Paths have at most three links,
  and the result has at most five paths. Support is `HIGH`, `MEDIUM`, `LOW` or
  `UNKNOWN`, from the weakest link. It gives no action permission or outcome
  prediction. The result has source attribution, but no private source fields.

### joey_search_graph_people

- Input:
  - `query`: person name or public profile URL; 2 to 2,048 characters.
  - `limit` (optional): 1 to 20 candidates.
- Result: `status`, `outcome`, `reason`, `recommendedNextAction`, `people`,
  `needsSelection`, `identityRule` and `revisions`. A name match is a
  candidate, not proof of identity. Select a clear canonical profile before a
  path search.
- `NOT_IN_GRAPH` with `NAME_NOT_FOUND` means that no graph person has a name
  that contains the text. Another spelling or the public profile URL can still
  match. `PROFILE_NOT_FOUND` means that no graph person has the profile.

### joey_search_graph_companies

- Input:
  - `query`: a company name; 2 to 200 characters.
  - `limit` (optional): 1 to 10 companies; default 5.
  - `peopleLimit` (optional): 0 to 50 people for each company; default 10.
- Result: `outcome`, `reason`, `recommendedNextAction`, `companies` and
  `revisions`. Each company has `name`, `aliases` (other spellings of the
  same name), `exactName`, `currentPeople`, `formerPeople`, `peopleComplete`
  and `people`. Each person has `entityRef`, `label`, `anchors`, `current` and
  `roles` (`organization`, `title`, `capacity`, `status`).
- The graph has no company records. A company is the organization name of
  people's roles. The search compares close spellings, such as "AcmeWorks",
  "Acme Works" and "Acme Works Ventures". A company is a candidate name, not a
  merge of people. Each person keeps its own `entityRef`.
- `MATCHED` means that one company has exactly the name. Otherwise ask the
  member to select one company. `NOT_IN_GRAPH` means that no graph person has
  a role at a company with this name or a close spelling.


### joey_get_graph_connections

- Input:
  - `entityRef`: canonical graph person UUID.
  - `offset` (optional): start position.
  - `limit` (optional): 1 to 100 connections.
- Result: current connections with exact source evidence, strength, review state,
  revisions and completeness. Public reads need `workspace:read`; shared member
  evidence also needs `trust:read`. Unknown familiarity stays unknown.


### joey_find_graph_paths

- Input:
  - `originRefs` (optional): 1 to 20 canonical graph person UUIDs. If absent,
    the member must have a confirmed public graph profile.
  - `target`: `entityRefs` (1 to 20 UUIDs), `profileUrl`, or `company` with
    optional `roles` (at most 10). Use a supplied or confirmed profile URL.
  - `maxHops` (optional): 1 to 5; default 3.
  - `maxPaths` (optional): 1 to 10; default 5.
- Result: `status`, `outcome`, `reason`, `recommendedNextAction`, `company`,
  live paths with scoped `pathRef` values, people, hop evidence, revisions and
  completeness limits. It creates no report or research request. An empty
  bounded search does not prove that no path exists. Shared member evidence
  needs `trust:read`; no name-based member identity is allowed.
- A `company` target resolves through the company search first. `company`
  gives `query`, `outcome`, `resolved` and `candidates`. With no exact company,
  the result has no paths and lists `candidates`. Call again with the exact
  `name` that the member selects. The path search uses the current people of
  the resolved company.


### joey_read_path_context

- Input:
  - `pathRef`: selected scoped reference from a live path search.
  - `brief` (optional): private `goal`, `target`, `proposedValue` and `timing`.
- Result: revalidated path, evidence, available trust context, next recipient,
  private brief and completeness. Recipient interest stays unknown. Do not
  disclose the brief without the member's approval. Read this before a live
  path explanation or activation. An old reference needs a fresh search.


### joey_prepare_activation

- Input:
  - `pathRef` (optional): selected scoped live path reference. Select this or `requestId`.
  - `requestId` (optional): current delivered report. Select this or `pathRef`.
  - `pathKey` (optional): selected delivered report path.
  - `brief` (optional): private `goal`, `target`, `proposedValue` and `timing`.
  - `idempotencyKey`: new UUID; reuse only for an exact retry.
- Result: private `activationId`, `revision`, ordered `steps`, `finalStage`,
  selected path context and dates. Each step has a recipient, target and stage.
  It revalidates a live path or reads the current delivered report. The result
  keeps its LIVE_GRAPH or DELIVERED_REPORT source. It creates no research
  request or delivered report. Save this record before an introduction with
  intermediate progress or outcomes. It sends no message.


### joey_record_path_outcome

- Input:
  - `activationId`: saved activation UUID, from a live path or delivered report.
  - `action`: `SAVE` or `WITHDRAW`.
  - `idempotencyKey`: new UUID for this exact action.
  - `outcomeId` (optional): existing outcome for a correction or withdrawal.
  - `expectedRevision` (optional): required with `outcomeId`.
  - `visibility` (optional): required for SAVE; `PRIVATE` or `NETWORK`.
  - `sessionId` (optional): active chat capture session; required for NETWORK.
  - `outcomeConsent` (optional): first NETWORK capture needs
    `version: "joey.outcomes.chat.v1"` and the member's explicit affirmative
    `response`. Statement consent does not cover outcome capture.
  - `observation` (optional): required for SAVE. See fields below.
- Observation fields: `kind`, `channel`, exactly two `participants`,
  `occurredAt`, safe `context`, and `source`. Each participant has `label` and
  confirmed `entityRef` and `profileUrl` when known. A name alone cannot bind an
  identity. Source fields are `type`, private `reference`, private exact
  `excerpt`, matching `event`, `identityProof`, and actual `confirmation` or
  `occurrenceConfirmation` when needed. Source types are `HOST_MESSAGE_TOOL`,
  `HOST_CALENDAR_TOOL` and `MEMBER_CONFIRMATION`. Identity proof is
  `HOST_VERIFIED_PARTICIPANTS` or `MEMBER_CONFIRMED_IDENTITIES`.
  `HOST_MESSAGE_TOOL` requires `HOST_VERIFIED_PARTICIPANTS`. For member-confirmed
  identities, use `type: "MEMBER_CONFIRMATION"`,
  `identityProof: "MEMBER_CONFIRMED_IDENTITIES"` and the actual affirmative
  `confirmation`. Do not label member proof as a host-verified message.
- Result: attributed outcome with ID, revision, visibility and `graphDelivery`.
  Only identity-bound `REPLY_RECEIVED`, `INTRO_ACCEPTED` or confirmed
  `MEETING_OCCURRED` can add an interaction edge. `MESSAGE_SENT` and
  `MEETING_SCHEDULED` remain private progress. A calendar source needs member
  confirmation that the meeting occurred. Unknown identities stay withheld.
  No outcome creates familiarity, general trust or contact permission.
- NETWORK also needs `trust:read` and `trust:write`, in addition to
  `intros:write`. Before its first capture, explain the shared issuer, confirmed
  profiles, event type, date and safe context; keep source excerpts and
  references private. Wait for a separate explicit yes. A local save is not
  graph visibility; inspect delivery separately. Withdraw with the ID and
  revision, without observation or visibility. Withdrawal needs no new consent.


## Live read and activation errors

An unresolved profile, a bounded empty search, absent permission, an old reference
and a service outage are different results. Do not report all of them as no path.
For an old reference or changed graph revision, search and read context again.
For `ACTIVATION_CHANGED`, inspect the current tracker revision. For
`SEND_APPROVAL_MISMATCH`, get the exact approved send details; do not invent a
receipt. For `OUTCOME_CONSENT_REQUIRED`, obtain the separate explicit consent
before shared capture. `GRAPH_MEMBER_SYNC_PENDING` means the shared layer has
undelivered changes; do not reuse an old shared answer.

## Prompt selection

`joey_make_intro` accepts one `requestId`, `pathRef` or `activationId`.
`joey_follow_up` and `joey_weekly_review` have no arguments. These prompts serve
clients with no installed skills and keep references as data. They do not grant
permission to send or to share private outcomes.
