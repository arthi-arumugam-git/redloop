# RedLoop — Company One-Pager
Founder: Arthi Arumugam · arthi1805@gmail.com · USD only · Goal: $35,000 collected by Dec 31, 2026
Repo: https://github.com/arthi-arumugam-git/redloop (MIT) · Demo: https://youtu.be/T6BolZX1AWM

## Problem
AI agents read email, docs, tickets, CRM notes and MCP tool results. Any of that text can carry instructions written by an outsider. If the agent follows them it forwards data, deletes records, or sends messages — and the chat transcript looks normal. Most teams test the model's replies, not the agent's actions.

## Product
RedLoop injects attack payloads into tool results, runs the agent, and scores attack success rate (ASR) from the action log (what the agent did, not what it said). Errors and timeouts count as UNKNOWN, never safe. A GitHub Action fails the build when ASR regresses.
- Open source harness (MIT): 13 scenarios, frozen suite, mutation search, rule + LLM judge.
- Kit (Gumroad): checklist, payload templates, report format.
- Service: we run it against your staging agent and hand you the report and the CI gate.

## ICP
US/remote AI startups (seed–Series B) shipping agents or MCP servers that touch email, docs, CRM, calendar, Slack or browsers. Buyer: CTO / founding engineer / head of security, usually triggered by an enterprise security questionnaire.

## Pricing (USD)
| Offer | Price | Scope |
|---|---|---|
| Kit Starter | $49 | Checklist, 7 payload families, README |
| Kit Pro | $149 | + Muse Spark results, report template, CI config |
| Snapshot | $2,000 / 5 business days | 1 agent, ≤5 tools, ASR report + top findings, 30-min readout |
| Full Assessment | $5,000 / 10 business days | 1–2 agents, ≤15 tools, custom scenarios, fix guidance, CI gate set up |
Payment 50% upfront / 50% on delivery (Stripe or Wise). Staging + test accounts only.

## Proof (measured, not claimed)
- Meta Muse Spark 1.3 (Oct 26, 2026): 65-case frozen suite, 0% ASR undefended and guarded; judge agreement 111/111.
- Offline mock agents without guards: 75–100% ASR per scenario; guarded (spotlighting + tool allowlist): 0%.
- No paying customers yet. Say so if asked.

## Path to $35K
Mix example: 4 Full ($20K) + 6 Snapshots ($12K) + ~25 kits (~$3K) = $35K. Kits are credibility; services are the money.

### 30 days (by Nov 28)
- Gumroad live; landing page live; 50 targeted emails sent (5/day weekdays).
- 1 Snapshot sold (can discount the first to $1,500 in exchange for a named case study).
### 60 days (by Dec 28)
- 3 Snapshots + 1 Full delivered; first case study published (with permission).
- Snapshot → Full upsell offered on every readout.
### 90 days (by Jan 27, 2027)
- Recurring: monthly retest + CI suite upkeep ($500–$1,000/mo) offered to every Full customer.
- Note: the $35K target falls at ~day 63; anything after Dec 31 counts toward 2027.

## Brand voice
Plain, specific, measurable. Say what was run, how many cases, what the number was. Never: "revolutionary", "next-gen", "unlock", "supercharge", "AI-powered security", invented stats, fake logos, fake testimonials. If the agent passed, say it passed.
