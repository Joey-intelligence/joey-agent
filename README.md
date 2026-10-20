# Joey for your AI agent

Joey finds paths to people for personal accounts and company workspaces. This
plugin connects your AI agent to live graph evidence and delivered reports.
Your agent proposes and prepares the next path action. It can send an approved
request, set an approved reminder and check progress through connected plugins.
Each message needs your approval of its exact recipient, channel and text.
Shared outcomes need separate consent from relationship and trust statements.

## What you need

- A Joey personal account or a company workspace account.
- One of these agents: Claude Code, Codex, Claude Desktop, claude.ai, Cursor or
  ChatGPT.
- For a send or progress check, a connected host plugin with the required
  account permission. Joey account connections and host plugin access are separate.
- For future reminders or repeated checks, a host scheduler. A scheduled
  progress check also needs access to Joey and the selected host plugins.

## What the plugin contains

- The Joey MCP server at `https://pouch.getjoey.io/api/customer/mcp`.
- Six skills:

| Skill | What it does |
| --- | --- |
| [joey](skills/joey/SKILL.md) | Finds paths, explains evidence and prepares the next action for the member's goal. |
| [joey-activate-path](skills/joey-activate-path/SKILL.md) | Prepares an introduction request for the next person on a path. Sends after your yes, then updates the stage. |
| [joey-path-follow-up](skills/joey-path-follow-up/SKILL.md) | Prepares first asks and follow-ups. Creates and verifies approved host reminders and repeated checks. |
| [joey-tracker-sync](skills/joey-tracker-sync/SKILL.md) | Checks relevant host messages and calendar events in the current task or an approved scheduled check. Proposes progress and the next action. |
| [joey-attest](skills/joey-attest/SKILL.md) | Records, corrects and withdraws relationship and trust statements after consent for this chat. |
| [joey-trust](skills/joey-trust/SKILL.md) | Shows relationship context, source attribution, conflicts and derived trust support for a person or agent. |

## How Joey continues a path

1. Connect Joey and give your goal. Your agent reads the current path and
   progress. It checks the available host tools and their account permissions.
2. Your agent prepares the next request in the same turn. It reuses a saved
   activation and keeps each intermediate step separate from the final target.
3. Review the actual recipient, channel, subject and full text. After your yes,
   your agent sends that version through your host plugin and checks the Joey
   progress record. Each later send needs a new exact approval.
4. Your agent offers an activation reminder if you defer the first request,
   or a progress check after a send. Approve its scope, time and time zone.
   Your agent checks for an existing task, creates or updates the approved
   host task, then verifies its state and schedule.
5. You can approve repeated checks through selected mail or calendar plugins.
   Your agent checks only the selected path evidence, proposes confirmed
   progress changes and prepares the next request. A stage change still needs
   your confirmation. A calendar date alone does not prove attendance.

Repeated checks stay quiet while progress is unchanged. They notify you of a
material change, required action, completion or failure. They end at their
agreed stop condition. A reminder supplies no send approval or mail-read
permission. If the host cannot run the required tools, your agent states that
limit before it claims a scheduled check.

## Sign in

The first time that your agent uses Joey, it opens a browser page.

1. Sign in to Joey.
2. Choose the workspace.
3. Approve the agent.

The grant gives access to the selected workspace. Trust permissions also give
access to the Joey trust network. The agent keeps the sign-in, so you never
copy a token. To remove the access, revoke the agent in Joey Settings.
Joey Settings also shows these install steps with copy buttons.

Trust reads need `trust:read`. Statement changes need `trust:write`. Existing
grants do not receive these permissions automatically. Reconnect Joey and select
them if needed.

The agent asks for consent before a new capture session in each chat.
Structured claims, relevant context, your name and dates go to the Joey trust
network. Source excerpts and chat references stay private to you. The session
lasts twelve hours. You can stop capture or withdraw saved statements. These are
agent submissions under reported member consent, not direct human signatures.
The skills act when the host loads or invokes them, including an approved host
task. The plugin has no connection hook or background listener. A connection
alone starts no contact or scheduled check. Trust support gives no permission
to act and predicts no intro outcome.

## Install

Menu names in the agents can change. If a step does not match, look for the
"MCP", "connector" or "skills" settings of your agent.

### Claude Code

```bash
claude plugin marketplace add Joey-intelligence/joey-agent
claude plugin install joey-agent@joey-agent
```

Start a new session. Run `/mcp`, select the Joey server, and sign in.

### Codex

```bash
codex plugin marketplace add Joey-intelligence/joey-agent
codex plugin add joey-agent@joey-agent
```

The plugin contains the Joey server with OAuth sign-in. If the Joey tools do not
show in Codex, add the server and sign in with these commands:

```bash
codex mcp add joey --url https://pouch.getjoey.io/api/customer/mcp
codex mcp login joey
```

### Claude Desktop and claude.ai

1. Add Joey as a custom connector with the URL
   `https://pouch.getjoey.io/api/customer/mcp`. Then connect and sign in.
2. Get the six skill zips from the latest release of this repository, or build
   them (see [Development](#development)).
3. Upload each zip as a skill in the Skills settings.

### Cursor

Add the server to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "joey": {
      "url": "https://pouch.getjoey.io/api/customer/mcp"
    }
  }
}
```

Cursor opens the sign-in page when it connects. If your Cursor version supports
Agent Skills, copy the folders in `skills/` to its skills folder.

### ChatGPT

Add Joey as a connector with the URL `https://pouch.getjoey.io/api/customer/mcp`
and OAuth sign-in. Connectors with write tools need the developer mode of
ChatGPT.

### Agents without skills

The Joey server also gives instructions and three prompts: `joey_make_intro`,
`joey_follow_up` and `joey_weekly_review`. Agents without skills can use them.
These prompts start manual tasks. A prompt name alone creates no schedule.
The installed skills supply the host reminder and repeated-check procedure.

## Safety

- Your agent sends only after your yes to the exact recipient, channel and text.
- Your agent uses an available host message tool through your account.
- A failed send changes no progress. A sent message creates no graph edge.
- A calendar entry alone does not prove a completed meeting.
- Your agent contacts nobody unless you ask.
- Your agent sets a reminder or repeated check only after you approve its scope
  and schedule. Each send still needs its own exact approval.
- Path reports are confidential to your workspace. Your agent quotes only the
  parts that you need.

## Update

```bash
# Claude Code
claude plugin marketplace update joey-agent
claude plugin update joey-agent@joey-agent

# Codex
codex plugin marketplace upgrade joey-agent
codex plugin add joey-agent@joey-agent
```

Each skill checks the latest stable release when it runs. With a saved check date,
it checks at most once a week. Without a saved date, it checks once per chat. It reports a
new version but does not install it. No check runs while the skill is inactive.

For Claude Desktop and claude.ai, upload the new skill zips. Remove the old
`joey-make-intro` and `joey-intro-follow-up` skills after you install their
replacements.

## Development

Read [AGENTS.md](AGENTS.md) for the repository rules.

Run the tests (standard library only):

```bash
python3 -I -m unittest discover -s tests -v
```

GitHub Actions runs the package tests and ZIP build for pull requests and
`main`. See [the CI workflow](.github/workflows/checks.yml).

Use [the path action cases](tests/fixtures/path-action-skill-cases.json) for a
separate skill behavior check. Give each case and the current skills to an
independent agent with simulated tools. Compare its actions with the case
checks. Do not send real messages or create real tasks for these cases.
Package tests alone do not prove skill behavior or future host execution.

Build the skill zips in `dist/`:

```bash
python3 -I scripts/build_skill_zips.py
```

Check the Claude Code plugin:

```bash
claude plugin validate .
```

For a new version, change the version in the four manifests and add an entry to
[CHANGELOG.md](CHANGELOG.md) in the same commit. Attach the zips to the release.

Before a release, verify confirmed profile identity, scopes, source privacy,
outcome consent and withdrawal. A release with a changed MCP contract needs
the matching Joey OS and Pouch release first. Version `1.3.0` uses the existing
MCP contract. Test host send receipts and approved task execution separately;
local tests do not prove live availability.

## License

Proprietary. See [LICENSE](LICENSE).

Personal relationship answers use four strengths: weak, medium, strong, and very strong.
Joey shares old and new personal answers as attributed statements. Weak is positive; an explicit No is separate.
Source excerpts and chat references stay private to their author.

Live graph reads need no delivered report. An empty report list does not show
graph absence. Shared member edges need a confirmed public profile and the
required trust permission. A local save, graph delivery and graph visibility
are separate states. SYNCED delivery alone does not prove visibility.

Confirmed outcomes keep their event source separate from public research and
member statements. A reply, accepted introduction or completed meeting can add
an interaction edge after explicit outcome consent and identity checks. It
creates no familiarity level, general trust or permission to contact anyone.
Private source excerpts and references stay with their author.
