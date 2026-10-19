# Joey for your AI agent

Joey finds warm introduction paths to the people that your company wants to
meet. This plugin connects your own AI agent to Joey. Your agent can then read
your paths, help you activate paths to get introductions, remind you to follow up, and keep your
path stages current. With your consent, it can also record relationship and
trust statements and read the context behind trust support.

## What you need

- A Joey account in a company workspace. Joey is invite only.
- One of these agents: Claude Code, Codex, Claude Desktop, claude.ai, Cursor or
  ChatGPT.

## What the plugin contains

- The Joey MCP server at `https://pouch.getjoey.io/api/customer/mcp`.
- Six skills:

| Skill | What it does |
| --- | --- |
| [joey](skills/joey/SKILL.md) | Uses the Joey tools: paths, reports, strength, saved targets, better paths, preferences, ICP and prospects. |
| [joey-activate-path](skills/joey-activate-path/SKILL.md) | Prepares an introduction request for the next person on a path. Sends after your yes, then updates the stage. |
| [joey-path-follow-up](skills/joey-path-follow-up/SKILL.md) | Finds active paths with no answer, updates their stage, and offers follow-ups and reminders. |
| [joey-tracker-sync](skills/joey-tracker-sync/SKILL.md) | Reads your email and calendar and proposes path stage updates for you to confirm. |
| [joey-attest](skills/joey-attest/SKILL.md) | Records, corrects and withdraws relationship and trust statements after consent for this chat. |
| [joey-trust](skills/joey-trust/SKILL.md) | Shows relationship context, source attribution, conflicts and derived trust support for a person or agent. |

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
The skills act only when the host loads or invokes them. They do not listen in
the background. Trust support gives no permission to act and predicts no intro
outcome.

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

## Safety

- Your agent sends an email only after you say yes to the exact text.
- Your agent sends email only through your own email tool.
- Your agent contacts nobody unless you ask.
- Your agent sets a reminder only after you agree.
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

Before release of version `1.1.0`, deploy the Pouch trust contract and verify its
permissions, source privacy and withdrawal. Release the plugin after that check.

## License

Proprietary. See [LICENSE](LICENSE).

Personal relationship answers use four strengths: weak, medium, strong, and very strong.
Joey shares old and new personal answers as attributed statements. Weak is positive; an explicit No is separate.
Source excerpts and chat references stay private to their author.
