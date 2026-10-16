# Joey MCP tool reference

The Joey customer MCP is at `https://pouch.getjoey.io/api/customer/mcp`. Each
tool acts for one member in one workspace. The member chose the workspace when
the member approved the agent.

The input schema that the server sends is the authority. If this page and the
schema do not agree, follow the schema. [tools.json](tools.json) lists the
tool names, scopes and prompts.

Each result has the form `{data}`. An error has a stable code. See
[Errors](#errors).

## Scopes

| Scope | Who | Tools |
| --- | --- | --- |
| `workspace:read` | All members | All read tools |
| `intros:write` | All members | All write tools, except `joey_update_icp` |
| `icp:write` | Workspace admins only | `joey_update_icp` |

A member who is not an admin does not see `joey_update_icp`.

## Read tools

### joey_whoami

- Input: none.
- Result: the member (name, email), the workspace (id, name), the member role
  (admin or member), and the granted scopes.
- Call it first in each session.

### joey_list_paths

- Input:
  - `status` (optional): filter by request status.
  - `introStage` (optional): one of the [intro stages](#intro-stages).
  - `savedOnly` (optional): `true` gives only saved targets.
  - `query` (optional): a part of a target name or a company name.
  - `limit`: the number of rows on one page.
  - `cursor` (optional): the cursor from the last page.
- Result: one row for each path request, and the cursor of the next page. Each
  row has the `requestId`, the target, the target company, the hops, the
  strength, the intro stage and a saved flag.

### joey_get_path_report

- Input: `requestId`.
- Result: the report. It has one or more paths. Each path has a `pathKey`,
  people, hops and a summary. Each hop has:
  - the two people,
  - a strength word,
  - a basis: Public source, Inferred or User-confirmed,
  - an explanation,
  - the evidence: the source kind, the date and what the source records.

  The result also gives the intro stage and the person to ask.

### joey_get_intro_draft

- Input: `requestId`, `pathKey` (optional; path 1 if you do not give it).
- Result: `{to, subject, body, introducer}`.
  - `to` is the email address of the person to write to. It can be empty.
  - `introducer` is the person who makes the introduction. For a REACH_OUT,
    the next person on the path is the target. Then the email goes to the
    target and no introducer makes an introduction.
- Joey writes the draft with AI from the hop evidence. The server limits the
  number of new drafts for each member in one hour.

### joey_get_intro_tracker

- Input:
  - `stage` (optional): one of the [intro stages](#intro-stages).
  - `staleDays` (optional): give only intros with no change for this number of
    days.
- Result: one row for each intro, and the counters. Each row has the
  `requestId`, the target, the introducer, the stage, the date of each stage,
  the last note, and the stop state. The counters are paths discovered, intros
  requested, intros made and meetings.

### joey_list_path_preferences

- Input: none.
- Result: the saved preferences of the member (`preferenceId`, chip, text,
  date). A member can save at most 10.

### joey_get_icp

- Input: none.
- Result: the ICP of the workspace: `description` (free text), `roles`,
  `industries`, `countries`, `employeeRanges`, and its `version`.

### joey_list_prospects

- Input: none or filters from the schema.
- Result: the prospects of the workspace. Saved targets show here with high
  priority.

## Write tools

### joey_request_path

- Input: `targetName`, `targetCompany` (optional), `linkedinUrl` (optional),
  `note` (optional), `idempotencyKey`.
- Result: the new path request. Joey researches the path. The path shows in
  `joey_list_paths` when Joey delivers it.
- The workspace has a weekly limit of new paths.

### joey_save_target

- Input: `requestId`.
- Result: the prospect. The target becomes a prospect with high priority.

### joey_find_better_path

- Input: `requestId`, `preference`, `savePreference`, `idempotencyKey`.
  - `preference` has a `chip`, a `text`, or both.
  - `chip` is one of the [preference chips](#preference-chips), or `null`.
  - `text` is the member's own words, at most 280 characters.
  - `savePreference`: `true` saves the preference for future searches.
    `false` uses it only for this search.
- Result: the new better-path round. A request has at most one open round.

### joey_set_intro_stage

- Input: `requestId`, `stage`, `note` (optional).
- Result: the intro after the change.
- A stopped intro takes no change.

### joey_stop_intro

- Input: `requestId`, `reason` (optional).
- Result: the stopped intro. A stop is final.

### joey_rate_familiarity

- Input: `requestId`, `personKey`, `level`.
  - `level` is one of `VERY_WELL`, `SOMEWHAT`, `NOT_WELL`.
- Result: the rating.
- The answer is not private to the member. Joey uses it to rank paths. The member
  controls this with the switch "Share my ratings with the Joey graph" in Joey
  Settings. With OPEN (the default), other Joey users can see the member as a
  possible introducer to this person. With NOBODY, Joey uses the answer only to
  rank the paths of the member.

### joey_delete_path_preference

- Input: `preferenceId`.
- Result: no data.

### joey_update_icp

- Input: `expectedVersion`, `description`, `roles`, `industries`, `countries`,
  `employeeRanges`.
- Result: the new ICP and its new version.
- Only an admin with the `icp:write` scope can call it. Read the ICP first and
  send its version as `expectedVersion`. If another person changed the ICP
  after your read, the call fails with a version conflict.

## Values

### Intro stages

| Stage | Meaning |
| --- | --- |
| `PATH_FOUND` | Joey delivered the path. Nobody asked for the intro yet. |
| `INTRO_REQUESTED` | The member asked the introducer for the intro (or wrote to the target for a REACH_OUT). |
| `INTRODUCED` | The introducer made the introduction. |
| `MEETING_SET` | The member and the target set a meeting. |
| `MET` | The member and the target met. |

A stop (`joey_stop_intro`) ends the intro at any stage.

### Strength words

Each hop has one strength word. The word comes from the Joey graph.

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

### Familiarity levels

| Level | Words in the Joey app |
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
| Not found or forbidden | The path is not in this workspace, or the member has no access. Do not retry. |
| Rate limit | Stop. Tell the member to try again later. Do not loop. |
| Version conflict (ICP) | Read the ICP again. Show the new version to the member before a new change. |
| `INTRO_STOPPED` | The intro is stopped. Tell the member. Do not change it. |
| Weekly limit | Tell the member that the workspace reached its weekly limit of new paths. |
| Other code | Tell the member the code in plain words. Do not guess a cause. |

## Server prompts

Clients without skills can use these prompts. The skills in this plugin do the
same work.

| Prompt | Arguments | Same as |
| --- | --- | --- |
| `joey_make_intro` | `requestId` | the `joey-make-intro` skill |
| `joey_follow_up` | none | the `joey-intro-follow-up` skill |
| `joey_weekly_review` | none | the `joey` skill and the `joey-intro-follow-up` skill |
