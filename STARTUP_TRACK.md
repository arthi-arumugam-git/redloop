# RedLoop: Startup track plan

Startup track is judged on **technical execution and whether it holds up in production** (event page, checked Oct 26 2026 2:10 PM IST). So the submission has to read as a product a team can adopt on Monday, not a research demo.

## What "holds up in production" means for RedLoop
| Judge question | Evidence we ship | Status |
| --- | --- | --- |
| Can a team drop it into CI? | `action.yml` GitHub Action + `check-suite` gate that fails the build on any regression | Done (06078f5) |
| Is the score reproducible? | Frozen attack suite (60 payloads), deterministic offline run, seedable | Done (3fda41e) |
| Does it work on a real Meta model? | `llama-guarded` target + Muse Spark target via Meta Model API, LLM judge on Muse Spark | Llama done; Muse Spark pending API key after kickoff |
| Is the judge trustworthy? | `ChatLLMJudge` + `agreement()` vs rule judge, report agreement % in README | Code done; run on real model pending |
| Is it fast and cheap enough? | Report wall-clock and token cost per suite run in `report` output | TODO |
| Does it fail safely? | Retries/backoff (429/5xx/resets, Retry-After, `REDLOOP_HTTP_ATTEMPTS`) and timeouts on model calls; errors recorded as `error` rows, non-zero exit | Done: retries (3453dab); `check-suite` exits 3 on infra errors (UNKNOWN), 1 on vulnerability |
| Can a customer see value in 3 minutes? | `make showcase` + DEMO_SCRIPT.md (naive 91% ASR to guarded 0%) | Done (bdec6b8) |

## Product framing for the writeup
- **Customer:** teams shipping tool-using agents (support, coding, ops) who need a prompt-injection regression test before every deploy.
- **Wedge:** free GitHub Action; paid hosted dashboard with trend history and new attack packs each week.
- **Why now:** agents now read untrusted tool output (email, web, tickets); one injected instruction can exfiltrate data or send mail.

## Next build steps (priority order)
1. Cost and latency columns in `report` (tokens, seconds, USD per run).
2. ~~Retry wrapper; distinct infra exit code~~ done (exit 3 = infra/UNKNOWN, 1 = vulnerable).
3. Run the suite on Muse Spark via Meta Model API as soon as kickoff grants access; publish before/after table.
4. ~~Install section at top of README~~ done (3-line install + flow diagram).

## Locked entry (Arthi approved Oct 26 2026, after gstack validation: ITERATE)
**RedLoop Cloud + one PixelInject scenario.** gstack priorities:
1. **Muse Spark as target, attacker and judge.** Judge errors or unparseable verdicts become UNKNOWN, never "safe". Needs Muse API access (kickoff ~9:30 PM IST Oct 26).
2. **Hosted dashboard + README badge** ("RedLoop ASR: 0%"). Today it's a local Streamlit app; hosting is TODO.
3. **PixelInject visual scenario:** stub at `redloop/scenarios/visual/pixelinject_stub.py`. It has `generate_image` (Muse Image) and `segment_regions` (SAM 3.1) hooks and skips when they're unset. Wire it after kickoff.
4. **Video (about 3 min), PR red to green:** (a) open a PR that weakens the guard; (b) the Action runs and `check-suite` exits 1, so the PR goes red with ASR shown; (c) show the injected payload and action log (the secret was emailed); (d) restore the guard, push, and it goes green at 0% ASR; (e) show the PixelInject screenshot attack and the Muse Spark judge verdict; (f) show the dashboard trend and badge.

Open: cost/latency columns in `report` (we can scaffold seconds offline; tokens and USD need real model calls).
