# Joey for your AI agent

Joey finds warm introduction paths to the people that your company wants to
meet. This plugin connects your own AI agent to Joey. Your agent can then read
your paths, help you make introductions, remind you to follow up, and keep your
introduction tracker true.

## What you need

- A Joey account in a company workspace. Joey is invite only.
- One of these agents: Claude Code, Codex, Claude Desktop, claude.ai, Cursor or
  ChatGPT.

## What the plugin contains

- The Joey MCP server at `https://pouch.getjoey.io/api/customer/mcp`.
- Four skills:

| Skill | What it does |
| --- | --- |
| [joey](skills/joey/SKILL.md) | Uses the Joey tools: paths, reports, strength, saved targets, better paths, preferences, ICP and prospects. |
| [joey-make-intro](skills/joey-make-intro/SKILL.md) | Writes the intro email with you and sends it after your yes, then updates Joey. |
| [joey-intro-follow-up](skills/joey-intro-follow-up/SKILL.md) | Finds intros with no answer, updates their stage, and offers follow-ups and reminders. |
| [joey-tracker-sync](skills/joey-tracker-sync/SKILL.md) | Reads your email and calendar and proposes intro stage updates for you to confirm. |

## Sign in

The first time that your agent uses Joey, it opens a browser page.

1. Sign in to Joey.
2. Choose the workspace.
3. Approve the agent.

The agent gets access only to that workspace. The agent keeps the sign-in, so
you never copy a token. To remove the access, revoke the agent in Joey Settings.
Joey Settings also shows these install steps with copy buttons.

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
2. Get the four skill zips from the latest release of this repository, or build
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

For Claude Desktop and claude.ai, upload the new skill zips.

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

## License

Proprietary. See [LICENSE](LICENSE).
