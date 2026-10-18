# Joey MCP tool reference

The Joey customer MCP is at `https://pouch.getjoey.io/api/customer/mcp`. Each
tool acts for one member in one workspace. The member chose the workspace when
the member approved the agent.

The input schema that the server sends is the authority. If this page and the
schema do not agree, follow the schema. [tools.json](tools.json) lists the
tool names, scopes, arguments and prompts.

Each result has the form `{data}`. A service error has a stable `code`. Input
errors can have `isError` and text without a service code. See
[Errors](#errors).

## Scopes

| Scope | Who | Tools |
| --- | --- | --- |
| `workspace:read` | All members | Workspace read tools |
| `intros:write` | All members | Introduction and target write tools |
| `icp:write` | Workspace admins only | `joey_update_icp` |
| `trust:read` | Members with this permission | Trust subject lookup, own statements and trust context |
| `trust:write` | Members with this permission | Capture sessions, subjects, statements and withdrawal |

A member who is not an admin does not see `joey_update_icp`.

## Read tools

### joey_whoami

- Input: none.
- Result: `user` (`id`, `name`, `email`), `workspace` (`id`, `name`), `role`
  (`ADMIN` or `MEMBER`), `scopes`, and `client` (the name of this agent).
- Call it first in each session.

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
  - `requestId`: from `joey_list_paths`.
  - `pathKey` (optional): the path. Path 1 if you do not give it.
  - `regenerate` (optional): `true` makes a new draft in place of the saved
    one.
- Result: `{pathKey, to, mode, viaTeammate, subject, body, contextChips,
  gmailUrl, cached}`.
  - `to` is the person to write to: `name` and `email`. The `email` can be
    `null`.
  - `mode` is `ASK_INTRO` (the person introduces the member to the target) or
    `REACH_OUT` (the person is the target).
  - `viaTeammate` is `true` when the member is not on the path. Then the email
    goes to the first person on the path, a teammate of the member.
  - `gmailUrl` opens a Gmail compose window in the member's account with this
    recipient, subject and body.
- Joey writes the draft with AI from the hop evidence. The server limits the
  number of new drafts for each member in one hour. A saved draft
  (`cached: true`) does not count.

### joey_get_intro_tracker

- Input:
  - `stage` (optional): one of the [intro stages](#intro-stages), or `STOPPED`.
  - `staleDays` (optional): only the open intros (not `MET`, not stopped) with
    no change for at least this number of days.
- Result: `{counters, openCount, rows}`.
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
  capacity}`. Joey researches the path. The path shows in `joey_list_paths`
  when Joey delivers it. `capacity` gives the open requests and the paths of
  this week, with their limits.
- If the workspace asked for this target before, the member joins that request.

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
  - `requestId`: from `joey_list_paths`.
  - `stage`: one of the [intro stages](#intro-stages).
  - `pathKey` (optional): the path that the intro uses. If you do not give it,
    the intro keeps its path (path 1 for a new intro). Do not give it with
    `PATH_FOUND`.
- Result: `{requestId, intro}`.
- The tracker shows that this agent made the change. A stopped intro takes no
  change (`INTRO_STOPPED`).
- Joey keeps no note with a stage. Tell the member the reason in your answer.

### joey_stop_intro

- Input:
  - `requestId`: from `joey_list_paths`.
- Result: `{requestId, intro}`.
- A stop is final. Only a requested intro can stop (`INTRO_NOT_STARTED`).

### joey_rate_familiarity

- Input:
  - `requestId`: from `joey_list_paths`.
  - `pathKey` (optional): the path. Path 1 if you do not give it.
  - `rating`: `VERY_WELL`, `SOMEWHAT` or `NOT_WELL`, or `null` to remove the
    answer.
- Result: `{pathKey, person, rating}`. The tool rates the next person after the
  member on the path: the `rate` person of `joey_get_path_report`.
- The answer is not private to the member. Joey uses it to rank paths. The member
  controls this with the switch "Share my ratings with the Joey graph" in Joey
  Settings. With OPEN (the default), other Joey users can see the member as a
  possible introducer to this person. With NOBODY, Joey uses the answer only to
  rank the paths of the member.

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
| `VERY_WELL` | Very well |
| `SOMEWHAT` | Somewhat |
| `NOT_WELL` | Not well |

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
| `OPEN_CAPACITY_REACHED` or `QUOTA_OPEN_REACHED` | The workspace has the most open searches that it can have. Tell the member. |
| `RATING_NOT_ALLOWED` | This path has no person that the member can rate. Do not retry. |
| `TARGET_COMPANY_REQUIRED` | Joey does not know the company of the target, so it cannot save the target. |
| `INVALID_TARGET_URL` | Ask the member for a LinkedIn person or company URL. Do not guess one. |
| `IDEMPOTENCY_CONFLICT` | The key was used for another request. Make a new key. |
| Other code | Tell the member the code in plain words. Do not guess a cause. |

## Server prompts

Clients without skills can use these prompts. The skills in this plugin do the
same work.

| Prompt | Arguments | Same as |
| --- | --- | --- |
| `joey_make_intro` | `requestId` | the `joey-make-intro` skill |
| `joey_follow_up` | none | the `joey-intro-follow-up` skill |
| `joey_weekly_review` | none | the `joey` skill and the `joey-intro-follow-up` skill |

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
  - `identityUri` (optional): a public HTTPS identity URL without credentials, query or fragment.
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
- Result: statement IDs, revisions and status. Each claim has `subjectId`,
  `objectId` (or `representedTeam` for an agent), `claimType`, `value`, optional
  `familiarity`, `purpose`, public `context`, private `sourceExcerpt` and private
  `sourceReference`. A correction also needs `id` and `expectedRevision`.
  Types are `RELATIONSHIP`, `TRUST` and `REPRESENTS`. The server supplies the
  issuer. Do not submit tool results, quoted examples, secrets or whole reports.

### joey_list_attestations

- Input:
  - `subjectId` (optional): a subject filter.
  - `cursor` (optional): the previous `nextCursor`.
  - `limit` (optional): 1 to 50.
- Result: `{statements, nextCursor}` for this member only. This author-only result
  includes private source excerpts. Do not share those fields.

### joey_withdraw_attestations

- Input:
  - `sessionId` (optional): withdraw all current statements from this session and stop it.
  - `statements` (optional): selected records, each with `id` and `expectedRevision`.
- Result: `{withdrawn}`. Supply exactly one selection. Withdrawal works after
  capture ends. The next context query excludes withdrawn records.

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
