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

## Real-agent result (Letta, Oct 29 2026)

RedLoop ran 15 email-borne injection cases (5 frozen + 10 hand-written, incl. hidden HTML, spoofed tool results, memory-write bait, multilingual) against a live Letta agent wired to an email MCP server (list/read/send). Control run worked end to end. Result: 15/15 green, 0 breaks, 0 errors; every case reached the agent. A null result is still a result: it shows the harness can drive a real agent through real tool calls and score it, and it sets the baseline for the next targets. Raw output: `letta-email/summary.json` (private run dir).

## Links
- Repo: https://github.com/arthi-arumugam-git/redloop
- Demo video: https://github.com/arthi-arumugam-git/redloop/releases/download/demo-v4/redloop_demo_v4.mp4 (1:49, narrated, hackathon-window work only; YouTube unlisted link to replace this once Google verify clears)

## Demo video
https://github.com/arthi-arumugam-git/redloop/releases/download/demo-v4/redloop_demo_v4.mp4 (v4, 1:49, hackathon-window work only). Do NOT use the old Oct 27 YouTube link youtu.be/T6BolZX1AWM: it opens on pre-window offline code. Swap to a YouTube unlisted upload of v4 once Google verify clears.

## Built during the hackathon (required disclosure, Startups track)
Build window opened Oct 26 2026 (ET). Commit times from `git log`, converted to ET (UTC-4). The Startups track allows existing code if the new work is clearly stated; the demo video must show only hackathon-built work.

**Existing before the window (commits through Oct 25 ET, 2ea5314..bdec6b8):** sandbox mock tools (gmail, slack, github, x, calendar, docs, CRM), naive and guarded targets, policy schema, rule judge, 12 seeded injection scenarios, offline evolutionary attacker, OpenAI-compatible LLM judge, Markdown report, frozen regression suite (export-suite / check-suite), the reusable GitHub Action, and the offline showcase script.

**Built during the window (Oct 26 ET onward, 21357a4..):**
- Muse Spark integration through the Meta Model API (`META_`/`MUSE_API_KEY`, api.meta.ai/v1) as both target agent and judge.
- Live Muse Spark runs: frozen 65-case suite (0/56 unguarded, 0/55 guarded, about $1.16 per sweep) and live evolutionary search (255 episodes, 0 breaches).
- `docs.list_docs` tool, which fixed the doc-ID looping bug the live runs exposed.
- PixelInject screenshot-OCR support-ticket scenario and tickets tools (suite 60 to 65 cases).
- Defense-in-depth ablation targets (spotlight-only, allowlist-only).
- Production hardening: retry and backoff on 429/5xx with Retry-After; check-suite exit code 3 for infra errors.
- Latency and cost columns in the report, SVG ASR badge, demo mode workflow.
- MCP mirror target and the live Letta real-agent baseline (15/15 green).
- Narrated demo video, landing page, MIT license.

**Video check before submit:** done. Demo v4 (1:49, `make_demo_v4.py`) shows only hackathon-window work (Muse Spark live runs, PixelInject, list_docs fix, Letta run); it is the release asset linked above. Re-checked Nov 1 2026, 1:10 PM IST: release asset and public repo both return HTTP 200.

## Form answers (Cerebral Valley submit form, fields in CV_SUBMIT_FORM.md)

**Team Name:** RedLoop

**Track:** Startups Track

**Problem statement:** Push the Frontier

**Most Viral Track X post link:** paste the URL of the X post from X_VIRAL_POST.md once Arthi posts it (engagement counts until Nov 8 EOD).

**Describe your use of Meta products:**
Muse Spark, called through the Meta Model API (api.meta.ai/v1), is the live target agent in RedLoop's sandbox, in an unguarded and a guarded variant, and it can also serve as the judge model. We ran the frozen 65-case regression suite against it (0/56 unguarded and 0/55 guarded breaches, about $1.16 per sweep, mean latency 8 to 10 s per scenario) and a live evolutionary attack search (255 episodes, 0 breaches). Those live runs exposed a real reliability bug, the agent looping while guessing document IDs, which we fixed by adding a docs.list_docs tool.

**Why are Meta's models important to your solution?**
RedLoop is only useful if it tests the agents teams actually ship, and teams building on Meta models need a way to prove their agent resists indirect prompt injection before and after every change. Muse Spark is cheap and fast enough (about $1.16 for a full 65-case sweep) to run the whole suite in CI on every pull request, which is what turns a one-off red-team exercise into a regression test.

**How likely are you to build with Meta Model API?** Very likely

**Overall opinion of Meta Model API?** Very favorable

**Consent to promote materials:** Yes
