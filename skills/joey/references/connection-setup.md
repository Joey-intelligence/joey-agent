# Connect Joey

Use this guide for an install, reconnect or sign-in fault.

## Exact endpoints

| Purpose | URL |
| --- | --- |
| MCP server | `https://pouch.getjoey.io/api/customer/mcp` |
| OAuth discovery | `https://pouch.getjoey.io/.well-known/oauth-authorization-server` |
| Authorization endpoint | `https://pouch.getjoey.io/oauth/authorize` |

The authorization path has a slash between `oauth` and `authorize`.
Read live discovery. Copy its `authorization_endpoint` exactly. Do not derive
the path from the MCP URL or reconstruct it from words.

## Setup

1. Install the Joey plugin and its skills. Reuse the MCP server that the plugin
   adds. Do not add a duplicate connector. A host without plugin support uses
   one custom connector with the exact MCP server URL above.
2. Use the host MCP client's OAuth sign-in. The host owns dynamic client
   registration, the exact registered callback, state, PKCE and the token
   exchange. Do not construct an authorization URL, edit a popup URL or replace
   the host's state or PKCE verifier.
3. For a host that needs explicit OAuth fields, use the live discovery values.
   Verify the saved authorization endpoint before a fresh Connect action.
4. The member signs in, selects the workspace and approves the requested access.
   Do not approve new or broader access on the member's behalf.
5. Call `joey_whoami`. Confirm the returned identity, workspace and scopes.
   Report setup as complete only after that call succeeds. For a setup-only
   task, stop here. Do not start path work or request a new goal.

## A sign-in fault

A Connect card, connector spec or consent page does not prove a completed
connection. Do not claim that an unexposed request field or token exchange was
verified. Mark it as unknown.

Compare the popup's first URL path and parameter names with discovery. A staff
login page needs this route check. The last page alone does not show the cause.

Joey answers a wrong authorization path, such as `/oauthoauthorize`, with
HTTP 400 and the page "This is not a valid Joey authorization link". The page
gives the received path and the correct authorization endpoint. Correct the
saved endpoint from discovery, then use a fresh Connect action. An unknown or
malformed `client_id` shows an error on the consent page. A bad `code_challenge`,
`response_type` or `resource` returns to the host callback with an OAuth
`error`, such as `invalid_request`.

Do not infer that a request lacks `resource`, state or PKCE because the connector
tool omits that field from its spec. Use the actual request or server result.

Do not ask for tokens, authorization codes, client secrets, state values or a
PKCE verifier. Paths and parameter names suffice for the first route check.
Stop repeated sign-in attempts until the fault is known. After a correction,
use a fresh host Connect action. Keep its callback, state and PKCE intact.
