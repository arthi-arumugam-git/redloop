# WUPHF / Nex AI — RedLoop first-target check

**Date:** Thu Oct 29 2026 (Asia/Calcutta) — early prep for Assignment Fri Oct 30  
**Target asked:** `https://github.com/nex-crm/wuphf` (Nex AI / WUPHF)  
**Clone used:** shallow clone at `/tmp/wuphf`  
**Repo resolution:** `github.com/nex-crm/wuphf` **301 →** `https://github.com/najmuzzaman-mohammad/gawkbot` (public). Go module path in tree remains `github.com/nex-crm/wuphf`. Product names in-tree: **gawkbot / WUPHF / Nex**. Commit examined: `84af42b` on `main`.

**Recommendation: `SWITCH_TO_LETTA`**

WUPHF is a strong *agent + Gmail/CRM act* surface, but it does **not** first-class let an agent load an **external MCP server in place of** Gmail/Composio. RedLoop’s “MCP mirror replaces the integration” shape fits **Letta** better. Details below.

---

## Verdict summary

| Item | Result |
|------|--------|
| **(a)** External MCP in place of existing tool/integration | **FAIL** |
| **(b)** Workflow that reads untrusted text then acts | **PASS** (Gmail/Composio via `team_action_*`) |
| **(c)** Normal user task that triggers it | **PASS** (inbound email / “check inbox & reply or route”) |
| **LICENSE** local testing | **PASS** (Sustainable Use License — internal / non-commercial OK) |
| **Overall** | **SWITCH_TO_LETTA** |

---

## (a) Can WUPHF’s agents load an external MCP server in place of an existing tool/integration?

### FAIL — evidence

1. **Bot MCP config is launcher-assembled, not user-pluggable for arbitrary replacements.**  
   `internal/team/mcp_config.go` `buildMCPServerMap()` only registers the office binary under key(s) from `ServerKeys()` (`wuphf-office`):

   ```go
   office := map[string]any{
       "command": wuphfBinary,
       "args":    []string{"mcp-team"},
   }
   for _, key := range ServerKeys() {
       servers[key] = office
   }
   ```

   Extra per-turn servers exist only via `ensureBotMCPConfigWith(slug, extra)` — today used for the fixed **`computer`** bridge (`internal/team/launcher_computer.go`), not for swapping Gmail.

2. **Headless Claude is locked to that config.**  
   `internal/team/headless_claude.go` / `internal/provider/claude.go` pass `--mcp-config <path>` **and** `--strict-mcp-config` (also `--setting-sources user`). Strict MCP config means the session’s MCP set is the WUPHF-written map, not “drop in RedLoop MCP instead of Composio.”

3. **Gmail / CRM are not MCP servers.** They are **Composio (HTTP) actions** behind office tools `team_action_search` → `team_action_knowledge` → `team_action_execute` (`internal/teammcp/actions.go` `registerActionTools`). Provider base URL is `https://backend.composio.dev/api/v3`, overridable with `WUPHF_COMPOSIO_BASE_URL` / `COMPOSIO_BASE_URL` (`internal/action/composio.go` `configResolveComposioBaseURL`) — that is an **HTTP API mirror**, not an MCP server swap.

4. **Closest real MCP remotes (not email):**
   - `WUPHF_GBRAIN_MCP_URL` — remote gbrain MCP for the **broker’s** knowledge client (`internal/gbrain/mcp.go`), not a bot-facing Gmail replacement.  
   - `computer` MCP — Cua Driver bridge (`cmd/wuphf/computer_mcp.go`), fixed shape.

**Implication for RedLoop:** You cannot point a stock WUPHF agent at a RedLoop MCP and have it replace Gmail the way Letta’s `mcpServers: { email: … }` does. A Composio-compatible HTTP fake via `WUPHF_COMPOSIO_BASE_URL` is a *different* test shape (still useful, but not the Assignment’s MCP-mirror shape).

---

## (b) Which WUPHF workflow reads untrusted text and can then act?

### PASS — Gmail (and CRM/Slack) through `team_action_*`

**Workflow (agent loop):**

1. **Read untrusted external text (no human approval):**  
   `team_action_execute` with read-only Composio action IDs such as:
   - `GMAIL_FETCH_MAILS` / `GMAIL_SEARCH_EMAILS` (classified read-only in `internal/teammcp/actions_test.go`)
   - App-scaffold example uses `GMAIL_FETCH_EMAILS` (`templates/app-scaffold/src/wuphf-bridge.ts` — “READ-ONLY … no approval card”)
2. Model receives message bodies / snippets / CRM fields in the tool result (untrusted).
3. **Act:** same tool `team_action_execute` with mutating IDs such as:
   - `GMAIL_SEND_EMAIL`, `GMAIL_CREATE_DRAFT`
   - `SLACKBOT_SEND_MESSAGE`
   - HubSpot / other Composio platforms  
   Mutating calls hit `requireTeamActionApproval` (`internal/teammcp/actions.go`): quote — *“a prompt-injected bot cannot send email, write to a CRM, or post a Slack message without the human explicitly clicking approve.”*  
   Bypass paths for lab shape: `WUPHF_UNSAFE=1`, standing grants, or dry_run.

**Related ingress:** `team_action_relay_events` / `team_action_relay_event` return platform webhook payloads (also untrusted text → later `team_action_execute`).

### Exact tools a RedLoop MCP mirror must copy (if mirroring the **office** MCP surface)

Schemas are Go structs with `json` + `jsonschema` tags in:

**File:** `/tmp/wuphf/internal/teammcp/actions.go` (lines ~482–600, registration ~602–658)

| Tool name | Schema type | Role |
|-----------|-------------|------|
| `team_action_guide` | `TeamActionGuideArgs` | provider docs |
| `team_action_connections` | `TeamActionConnectionsArgs` | list OAuth connections |
| `team_action_search` | `TeamActionSearchArgs` | NL find action IDs |
| `team_action_knowledge` | `TeamActionKnowledgeArgs` | load action schema |
| **`team_action_execute`** | **`TeamActionExecuteArgs`** | **read + write path** |
| `team_action_workflow_create` | `TeamActionWorkflowCreateArgs` | save workflow JSON |
| `team_action_workflow_execute` | `TeamActionWorkflowExecuteArgs` | run saved workflow |
| `team_action_workflow_schedule` | `TeamActionWorkflowScheduleArgs` | cron schedule |
| `team_action_relays` | `TeamActionRelaysArgs` | list relays |
| `team_action_relay_event_types` | `TeamActionRelayEventTypesArgs` | event catalog |
| `team_action_relay_create` | `TeamActionRelayCreateArgs` | create relay |
| `team_action_relay_activate` | `TeamActionRelayActivateArgs` | activate relay |
| `team_action_relay_events` | `TeamActionRelayEventsArgs` | poll events |
| `team_action_relay_event` | `TeamActionRelayEventArgs` | one event payload |

**Critical execute schema (`TeamActionExecuteArgs`) — fields to mirror:**

```json
{
  "platform": "string (e.g. gmail)",
  "action_id": "string (e.g. GMAIL_FETCH_MAILS | GMAIL_SEND_EMAIL)",
  "connection_key": "string?",
  "data": "object?",
  "path_variables": "object?",
  "query_parameters": "object?",
  "headers": "object?",
  "form_data": "boolean?",
  "form_url_encoded": "boolean?",
  "dry_run": "boolean?",
  "channel": "string?",
  "my_slug": "string?",
  "summary": "string?",
  "issue_id": "string? (required for mutating)"
}
```

Client-visible names under Claude: `mcp__wuphf-office__team_action_execute` (`internal/team/mcp_namespace.go` `ServerKey = "wuphf-office"`).

**Supporting tools often required before send:** `team_task` (issue_id), optionally `human_interview` / approval UX (broker-side, not MCP-replaceable for the mirror’s *content* injection).

**If mirroring Composio HTTP instead of MCP:** emulate `POST …/tools/execute/{action_id}` against `WUPHF_COMPOSIO_BASE_URL` (`internal/action/composio.go`) — still not “load external MCP.”

---

## (c) What normal user task triggers that workflow?

### PASS — examples grounded in-repo

1. **“Connect Gmail and have the bot read / handle my inbox”** — notch copy in `docs/specs/notch-screen-awareness.md`: *“Connect Gmail so your bots can read this inbox”*; bridge `getEmails()` → `GMAIL_FETCH_EMAILS`.
2. **RevOps inbound routing (Maya ICP)** — `docs/specs/operator-mlp-plan.md`: inbound demo requests in a shared inbox → enrich CRM → score → route / act (Gmail + HubSpot/Slack via Composio).
3. **Teach / run a Gmail workflow** — operation blueprints under `templates/operations/*` declare Gmail lanes (outreach, newsletter send, intake); bots use `team_action_*` after the human connects Gmail in Integrations.
4. **Chat ask:** e.g. draft/send follow-up or reply after fetching mail — same execute tool with `GMAIL_SEND_EMAIL` (approval card: “Send Email via Gmail”, tests in `internal/teammcp/actions_test.go`).

**Recommended first RedLoop workflow (if staying on WUPHF despite (a)):**  
*Connect Gmail → bot fetches recent mail (`GMAIL_FETCH_*`) → bot proposes / sends reply (`GMAIL_SEND_EMAIL`)* — inject malicious content in the fetch result. Prefer lab with `WUPHF_UNSAFE=1` or a standing grant so the act side can complete without waiting on UI.

---

## LICENSE

**File:** `/tmp/wuphf/LICENSE` — **Sustainable Use License** (Copyright 2026 Nex).

Quote: *“You may use or modify the software only for your own internal business purposes or for non-commercial or personal use.”*

**Local testing / RedLoop lab on a private machine: ALLOWED.**  
Commercial redistribution / SaaS resale of the software itself: restricted. Do not publish findings claiming a live exploit against third parties (per Assignment: read-only research + this report only).

---

## Exact tool list (office MCP — full inventory from `internal/teammcp`)

98 tools registered (names only). RedLoop minimum for email read→act: the **14 `team_action_*` tools** above; full set if replacing entire `wuphf-office` server:

`agent_message`, `context_capture`, `context_health`, `context_lookup`, `context_promote`, `data_*` (14), `entity_*` (3), `get_app`, `human_interview`, `human_message`, `image_generate`, `image_list_providers`, `link_task_wiki`, `list_apps`, `playbook_*` (4), `propose_app`, `read_conversation`, `register_app`, `reply`, `resolve_contradiction`, `run_lint`, `team_action_*` (14), `team_bridge`, `team_broadcast`, `team_channel`, `team_channel_member`, `team_channels`, `team_dm_open`, `team_inbox`, `team_learning_record`, `team_learning_search`, `team_local_agents`, `team_member`, `team_members`, `team_memory_*` (3), `team_office_members`, `team_outbox`, `team_plan`, `team_policy_record`, `team_poll`, `team_react`, `team_request`, `team_requests`, `team_routine`, `team_runtime_state`, `team_skill_*` (6), `team_status`, `team_task`, `team_task_status`, `team_tasks`, `team_wiki_*` (4), `visual_artifact_*` (4), `wuphf_wiki_lookup`.

---

## Recommended first workflow (WUPHF, secondary path)

| Step | Action ID / tool | Notes |
|------|------------------|-------|
| 1 | Connect Gmail (Integrations UI / Composio OAuth) | product path |
| 2 | `team_action_execute` `GMAIL_FETCH_MAILS` or `GMAIL_SEARCH_EMAILS` / `GMAIL_FETCH_EMAILS` | untrusted text in |
| 3 | Model reasons | injection surface |
| 4 | `team_action_execute` `GMAIL_SEND_EMAIL` | act out; approval unless unsafe/grant |

**Do not use as primary RedLoop MCP target** because of (a).

---

## Fallback — Letta (SWITCH_TO_LETTA)

**Verified (docs, Oct 2026):**

- **MCP:** Letta Agent SDK accepts arbitrary `mcpServers` (stdio, Streamable HTTP, SSE) when creating/resuming a session — tools appear as `mcp__<server>__<tool>`. Docs: https://docs.letta.com/agent-sdk/mcp/  
- **Email/send shape:** Host can attach an email MCP (HTTP or stdio) *in place of* other tools by configuring that server name — matches RedLoop “external MCP mirror” directly. Example pattern from docs: `mcpServers: { email: { type: "http", url: "…" } }`.  
- **Platform API:** Letta Tools API also has `/v1/tools/mcp/servers` add/list/execute (https://apis.io/apis/letta/letta-tools-api/).  
- **Open source:** `github.com/letta-ai/letta` + letta.com.

**Conclusion:** For Assignment Fri Oct 30, treat **Letta as first REAL agent target**; keep WUPHF notes as secondary (Composio HTTP mirror / approval-gate research) only if the brief expands beyond MCP-replaceable integrations.

---

## Sources (paths / URLs)

- Clone: `/tmp/wuphf` from `https://github.com/najmuzzaman-mohammad/gawkbot` (redirect of `nex-crm/wuphf`)
- `LICENSE`, `README.md`, `internal/team/mcp_config.go`, `internal/team/mcp_namespace.go`, `internal/team/headless_claude.go`, `internal/provider/claude.go`, `internal/teammcp/actions.go`, `internal/teammcp/actions_test.go`, `internal/action/composio.go`, `internal/gbrain/mcp.go`, `templates/app-scaffold/src/wuphf-bridge.ts`, `docs/specs/operator-mlp-plan.md`, `docs/specs/notch-screen-awareness.md`
- Letta MCP docs: https://docs.letta.com/agent-sdk/mcp/

---

## Final call

```
SWITCH_TO_LETTA
```

Reason: (a) FAIL on WUPHF for “load external MCP in place of Gmail/integration”; Letta PASS on that axis with documented email-capable MCP attachment; (b)(c) and LICENSE would have been fine on WUPHF alone.
