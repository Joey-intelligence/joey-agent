# Statement API

The server's input schema is the authority. A success has `{data}`. A service
refusal has `isError` and a stable code. Input errors can have `isError` and text
without a service code. Never treat an error as a save receipt.

## Sessions

- `joey_whoami`: no input. Returns the member, workspace and granted scopes.
- `joey_begin_attestation_session`: `chatKey` (UUID), `consentVersion`
  (`joey.trust.chat.v1`), `consentResponse` (the explicit response, at most 1,000
  characters). Returns `id`, `memberSubjectId`, `startedAt`, `expiresAt` and
  `proofType: "AGENT_SUBMITTED_MEMBER_REPORTED_CONSENT"`.
- `joey_end_attestation_session`: `sessionId`. Returns `{sessionId, ended}`.

The session belongs to one member, workspace and agent grant. It is not a token.
Do not reuse it in another chat or with another grant.

## Subjects

- `joey_resolve_trust_subject`: `query`, optional `kind` and `limit` (1 to 50).
  Returns `{subjects, incomplete}`.
- `joey_register_trust_subject`: `sessionId`, new UUID `idempotencyKey`, `kind`,
  `label`, optional `identityUri`. For a name-only record that the member already
  owns, also send `subjectId` and `expectedRevision`.

Kinds are `PERSON`, `AGENT_PRODUCT` and `AGENT_INSTANCE`. An identity URL must be
public HTTPS with no credentials or fragment.
A canonical Facebook profile URL can contain its numeric `id` query. Other query parameters are not permitted.
Each subject returns `id`,
`kind`, `label`, `identityUri`, `identityStatus`, `identityBasis` and `revision`.
`AUTHENTICATED_ACCOUNT` identifies a Joey account. `MEMBER_PROVIDED_URI` is a
member's locator claim. `MEMBER_NAMED` has no clear identity yet.

## Statements

`joey_put_attestations` takes `sessionId`, a new UUID `idempotencyKey`, and
`statements` (1 to 25). Each statement has:

| Field | Value |
| --- | --- |
| `subjectId` | The person or agent that the claim describes. |
| `objectId` | The other subject. Omit only for a represented team. |
| `representedTeam` | A team name for `REPRESENTS`; omit `objectId` then. |
| `claimType` | `RELATIONSHIP`, `TRUST` or `REPRESENTS`. |
| `value` | `KNOWS`, `DOES_NOT_KNOW`, `TRUST`, `DISTRUST` or `REPRESENTS`, as the claim type requires. |
| `familiarity` | Optional `weak`, `medium`, `strong` or `very_strong`; only for `KNOWS`. |
| `purpose` | `general` or the stated task; at most 160 characters. |
| `context` | Network context; at most 1,000 characters. |
| `sourceExcerpt` | Exact relevant member words; at most 1,000 characters; private to the author. |
| `sourceReference` | A message reference; at most 300 characters; private to the author. |
| `id`, `expectedRevision` | Both required for a correction; omit both for a new claim. |

A relationship needs two people. A trust claim starts at a person. A
representation starts at an agent and names a person or team. The receipt lists
`statements`, each with `id`, `revision`, `status` and `graphDelivery`.

`graphDelivery` has `state`, `revision`, `deliveredRevision` and `disposition`.
The delivery revision differs from the statement revision. Identity resolution
can send an existing statement without a content correction. States are:

- `PENDING`: the local save is complete; graph delivery is not confirmed.
- `SYNCED`: the graph confirmed the current delivery revision. Check
  `disposition` for `ACTIVE` or `WITHDRAWN`. Delivery alone does not prove
  visibility. Check `visibility`; a member must confirm a public graph profile
  before their edge can appear. Do not create an account node or merge namesakes.
- `WITHHELD`: an unresolved identity prevents an active graph claim.

The initial receipt remains a record of that write. To check later delivery,
read the current record. Graph claims keep the member, purpose, context, proof
type and revisions. They contain no private source excerpt or chat reference.
They remain separate from public research facts.

`joey_list_attestations` takes optional `subjectId`, `cursor` and `limit` (1 to
50). It returns the author's records and `nextCursor`. This author-only result
includes private source fields. Do not pass them to another tool or message.

`joey_withdraw_attestations` takes exactly one of:

- `sessionId` for all current statements and shared outcomes from that session.
- `statements`, each with `id` and `expectedRevision`, for selected records.

It returns `{withdrawn, graphDelivery}`. New graph removals are `PENDING`; a
repeat with no change is `UNCHANGED`. It needs `trust:write`, but no active
capture session. Read the author's record for the current graph delivery state
only when `trust:read` is available.

## Refusals and uncertain responses

- Auth error or missing scope: reconnect Joey with the required permission.
- `CAPTURE_SESSION_INACTIVE`: stop capture. Ask for new chat consent before a
  new session. Existing records remain available for inspection or withdrawal.
- `ATTESTATION_CHANGED` or `SUBJECT_CHANGED`: read the current record before a
  new change. Do not overwrite it from an old result.
- `SUBJECT_EXISTS`: resolve the identity and select the existing record.
- `SUBJECT_IDENTITY_FIXED`: do not change that identity. Ask the member to select
  the correct subject instead.
- `FORBIDDEN` or `NOT_FOUND`: stop. Do not probe other IDs.
- `RATE_LIMITED`: stop and tell the member to try later. Do not loop.
- `IDEMPOTENCY_CONFLICT`: the key has other content. Check the earlier receipt
  before a new set. Do not create another copy of an uncertain write.
- `TRUST_CONFLICT`: read current records before another write.
- An uncertain transport response: retry the exact same input and key while the
  session is active. After expiry, inspect the author's records before a new
  submission.

Weak is a positive relationship strength. `DOES_NOT_KNOW` has no familiarity.
The service preserves old uncertain answers as `UNSURE`. Do not invent a Yes or No for them.
An agent must not submit `UNSURE` as a new captured statement.
