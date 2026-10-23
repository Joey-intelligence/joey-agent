# Report a problem to the Joey team

`joey_report_bug` sends one report to the Joey team. Use a new UUID as
`idempotencyKey` for each report. Use the same key only for an exact retry.

## Mechanical failures

Report these automatically, with `trigger: automatic` and no question to the
member:

- `INTERNAL`, or an error code that the [tool reference](tools.md) does not
  list.
- A timeout or a transport error of the Joey server that repeats after one
  retry.
- A Joey tool or a result field that this skill names, but that the server
  does not have.
- A result that does not match the shape in the tool reference.

These are not bugs: `NOT_IN_GRAPH`, `AMBIGUOUS`, `IDENTITY_UNRESOLVED`,
`NO_PERMISSION`, `FORBIDDEN`, `RATE_LIMITED`, an empty bounded search, and an
`INVALID_INPUT` refusal of your own input. An error of the host or its proxy is
not a Joey bug.

1. Continue the member's task as far as possible.
2. Call `joey_report_bug` with `trigger: automatic`, a `severity`, a one-line
   `title` and a `description`. Also give `toolName`, `errorCode`, `host` and
   `pluginVersion`, the installed release in [the update check](updates.md).
   Use `blocking` when the task cannot continue. Otherwise use `wrong`.
3. Tell the member in one line, for example: "Joey had an internal error in
   the path search. I reported it to the Joey team."
4. Send one report for each failure. The status `DUPLICATE` tells you that the
   team already has a report of this failure.

## Problems that the member reports

When the member says that Joey is wrong or broken:

1. Write the report: a title, what happened, the steps, what the member
   expected and a severity.
2. Show the exact report text to the member.
3. Call `joey_report_bug` with `trigger: member` only after an explicit "yes"
   for that text.
4. Give the member the `reportId`.

To attach screenshots or files, the member can use **Report a bug** under
Settings in the Joey web app.

## Content rules

- Write tool names, error codes and ids. Do not write the names, emails or
  profile URLs of people unless the member approves that exact text.
- Do not include report text, message text, calendar text, tokens, keys or
  passwords.
- A refusal of `joey_report_bug` does not stop the task. Do not retry it in a
  loop.
