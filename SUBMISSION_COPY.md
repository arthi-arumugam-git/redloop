# RedLoop — paste-ready submission copy (draft)

Char limits are not yet published (Official Rules still unlinked on the event page as of Oct 27 2026, 4:10 PM IST). Each block below is sized to fit common Devpost-style limits; trim to the real limits once the form is visible.

## Name
RedLoop

## Tagline (under 140 chars)
An agent that red-teams your agents: it attacks tool-using AI agents with prompt injections and gates CI on what gets through.

## Short description (under 300 chars)
RedLoop drops a tool-using agent into sandboxed email, Slack, GitHub, X, calendar, docs, CRM and screenshot-OCR scenarios, mutates indirect prompt injections against it, judges every outbound action, and freezes past breaches into a CI regression gate. Runs live on Muse Spark via the Meta Model API.

## Long description
**Problem.** Agents that read email, docs and tickets and then call tools can be steered by text hidden in that content (indirect prompt injection). Teams ship these agents with no repeatable way to prove a fix stays fixed.

**What RedLoop does.**
- 13 seeded sandbox scenarios across email, Slack, GitHub, X, calendar, docs, CRM and a screenshot-OCR support-ticket case.
- An evolutionary attacker that mutates injected payloads and keeps the strongest candidates, with a fresh sandbox per trial.
- A rule judge that scores only successful outbound actions (exfiltration, unauthorized send, destructive action, policy override), so refusals, blocked attempts and failed calls never count as breaches.
- A frozen regression suite plus a GitHub Action that fails CI if an attack that used to be blocked gets through again.

**Built with Meta models.** Muse Spark through the Meta Model API is the live target agent (unguarded and guarded variants).

**Results so far (all in `results/`).**
- Frozen 65-case suite, offline ablation: naive agent breached 65/65; spotlight-only, allowlist-only and fully guarded agents 0/65.
- Live Muse Spark: 0/56 (unguarded) and 0/55 (guarded) breaches on the frozen suite, about $1.16 per 65-run sweep, mean latency 8–10 s per scenario.
- Live evolutionary search on Muse Spark: 0/128 and 0/127 breaches over 255 episodes.
- The live runs exposed a real reliability bug (the agent looped guessing document IDs); adding a `docs.list_docs` tool fixed it, and the docs scenarios now finish in 2 tool actions.

**Why it matters for production.** The same harness that finds a breach turns it into a permanent CI check, so agent security becomes a regression test instead of a one-off audit.

## Links
- Repo: https://github.com/arthi-arumugam-git/redloop
- Demo video: TBD (3 minutes)

## Demo video
https://youtu.be/T6BolZX1AWM (Unlisted, uploaded Oct 27 2026)
