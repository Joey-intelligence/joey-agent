# Trust context result

`joey_get_trust_context` takes `subjectId` and optional `task`. A success has
`{data}`. Input schema errors or service refusals have `isError`; do not present
them as an empty network or a successful result.

| Result | Use |
| --- | --- |
| `subject`, `origin`, `task` | The selected subject, the authenticated member and the requested task. |
| `support` | `HIGH`, `MEDIUM`, `LOW` or `UNKNOWN`. |
| `directStatements` | The member's direct claims about this subject. |
| `relationshipContext` | Relevant network claims, with context and source attribution. |
| `paths` | At most five paths, each with at most three links, support levels, reasons and statements. |
| `conflicts` | Contradictory claims. Show the difference rather than hide one. |
| `incomplete`, `incompleteReasons`, `limits` | The data, path or work limits that affect the result. |
| `rulesVersion`, `interpretation` | The rule version and the limits of the result. |

Each network statement includes its ID, revision, subject, object, claim type,
value, familiarity, purpose, context, issuer, dates, basis and proof type.
`basis: "THIRD_PARTY"` means the issuer reports another person's relationship
or trust. It does not make that person the issuer.

## Support rules

| Evidence | Maximum level |
| --- | --- |
| Explicit trust for the requested task | High |
| Explicit general trust | Medium |
| Very well familiarity | Medium |
| Somewhat familiarity | Low |
| A third-party report | Low |
| No positive familiarity or trust detail | Unknown |

A path takes the level of its weakest link. Paths rank by support, then fewer
links, then more recent evidence. Duplicate statements and cycles do not raise
support. Trust for an unrelated task does not raise the result. An agent
representation does not establish trust. Product trust does not transfer to
a specific agent.

The member's own distrust excludes affected positive paths. Other members'
negative claims remain visible as conflicts. They do not cancel every other
member's statements. A conflicting link has at most Low support.

A relationship absence removes acquaintance evidence. Explicit trust can still
apply to a person whom the member does not know personally. A third-party
distrust report can create a conflict, but it cannot become the member's own
distrust veto. Different members' trust opinions remain visible without a global
veto. The service checks the member's own distrust separately from its shared
scan limit.

Source excerpts and chat references are private to the author. They are not in
the network result. Member names and structured context are network data.
`AUTHENTICATED_ACCOUNT` identifies a Joey account. `MEMBER_PROVIDED_URI` does not
prove ownership of a person profile or agent.

## Errors

- Auth error or absent `trust:read`: reconnect Joey with that permission.
- `FORBIDDEN` or `NOT_FOUND`: stop. Do not probe other IDs.
- `RATE_LIMITED`: stop and tell the member to try later. Do not loop.
- Other error: give the code or short error text. Do not guess a trust result.
