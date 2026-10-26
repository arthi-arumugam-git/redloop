# RedLoop: Startup track plan

Startup track is judged on **technical execution and whether it holds up in production** (event page, checked Oct 26 2026 2:10 PM IST). So the submission has to read as a product a team can adopt on Monday, not a research demo.

## What "holds up in production" means for RedLoop
| Judge question | Evidence we ship | Status |
| --- | --- | --- |
| Can a team drop it into CI? | `action.yml` GitHub Action + `check-suite` gate that fails the build on any regression | Done (06078f5) |
| Is the score reproducible? | Frozen attack suite (65 payloads, 13 scenarios incl. PixelInject), deterministic offline run, seedable | Done (3fda41e) |
| Does it work on a real Meta model? | `llama-guarded` target + Muse Spark target via Meta Model API, LLM judge on Muse Spark | Done. Muse API live as of Oct 26 ~9:40 PM IST. Live on the frozen 65-case suite (Muse Spark 1.3 as target and judge): undefended `llama` 0/56 completed cases red (ASR 0.0%, 9 ERROR = 8-turn budget exhausted on docs_* scenarios, counted UNKNOWN), `llama-guarded` 0/55 red (ASR 0.0%, 10 ERROR). Muse judge vs rule judge verdict agreement 100% (111/111). ~1.46M tokens, ≈$2.70 at list price. See `results/MUSE_ASR.md`. |
| Is the judge trustworthy? | `ChatLLMJudge` + `agreement()` vs rule judge, report agreement % in README | Code done; run on real model pending |
| Is it fast and cheap enough? | `report` prints a cost/latency table (runs, total/mean/p95 seconds, tokens, USD); every run row records `seconds` | Seconds done offline; tokens/USD N/A until a real model call |
| Does it fail safely? | Retries/backoff (429/5xx/resets, Retry-After, `REDLOOP_HTTP_ATTEMPTS`) and timeouts on model calls; errors recorded as `error` rows, non-zero exit | Done: retries (3453dab); `check-suite` exits 3 on infra errors (UNKNOWN), 1 on vulnerability |
| Can a customer see value in 3 minutes? | `make showcase` + DEMO_SCRIPT.md (naive 91% ASR to guarded 0%) | Done (bdec6b8) |

## Product framing for the writeup
- **Customer:** teams shipping tool-using agents (support, coding, ops) who need a prompt-injection regression test before every deploy.
- **Wedge:** free GitHub Action; paid hosted dashboard with trend history and new attack packs each week.
- **Why now:** agents now read untrusted tool output (email, web, tickets); one injected instruction can exfiltrate data or send mail.

## Next build steps (priority order)
1. ~~Cost and latency columns in `report`~~ seconds done; tokens/USD recorded per Muse call in `results/muse_live.jsonl`.
2. ~~Retry wrapper; distinct infra exit code~~ done (exit 3 = infra/UNKNOWN, 1 = vulnerable).
3. Run the suite on Muse Spark via Meta Model API as soon as kickoff grants access; publish before/after table.
4. ~~Install section at top of README~~ done (3-line install + flow diagram).

## Locked entry (Arthi approved Oct 26 2026, after gstack validation: ITERATE)
**RedLoop Cloud + one PixelInject scenario.** gstack priorities:
1. **Muse Spark as target, attacker and judge.** Judge errors or unparseable verdicts become UNKNOWN, never "safe". Needs Muse API access (kickoff ~9:30 PM IST Oct 26).
2. **Hosted dashboard + README badge** ("RedLoop ASR: 0%"). Today it's a local Streamlit app; hosting is TODO.
3. **PixelInject visual scenario:** real offline scenario `pixelinject_ticket_screenshot` (injection in the ticket screenshot's `ocr_text` leaf, read via `tickets.read_attachment`; naive emails the secret, guarded stays green) plus an offline Pillow PNG (`assets/pixelinject_demo.png`, `python -m redloop.scenarios.visual.pixelinject_stub`). Muse Image (`generate_image`) and SAM (`segment_regions`) hooks are optional polish after kickoff.
4. **Video (about 3 min), PR red to green:** (a) open a PR that weakens the guard; (b) the Action runs and `check-suite` exits 1, so the PR goes red with ASR shown; (c) show the injected payload and action log (the secret was emailed); (d) restore the guard, push, and it goes green at 0% ASR; (e) show the PixelInject screenshot attack and the Muse Spark judge verdict; (f) show the dashboard trend and badge.

## Muse status (Oct 26 2026)
Muse Spark API is **live** as of Oct 26 2026 ~9:40 PM IST. Live on the frozen 65-case suite (Muse Spark 1.3 as target and judge): undefended `llama` 0/56 completed cases red (ASR 0.0%, 9 ERROR = 8-turn budget exhausted on docs_* scenarios, counted UNKNOWN), `llama-guarded` 0/55 red (ASR 0.0%, 10 ERROR). Muse judge vs rule judge verdict agreement 100% (111/111). ~1.46M tokens, ≈$2.70 at list price. See `results/MUSE_ASR.md`.

Offline polish shipped: seconds/latency columns in `report`; `python -m redloop badge` (offline SVG + README snippet, `assets/redloop-asr-badge.svg`); `check-suite` exit codes 0/1/3 covered by tests; `VIDEO_SCRIPT.md` outline.

Next: live `attack --all --agents llama,llama-guarded` (Muse as attacker target) to find payloads that beat undefended Muse, since the frozen suite (mined against the mock naive agent) does not; raise max_turns for docs_* scenarios; host dashboard/badge.

## Ablation note (Oct 26 2026, 6:10 PM IST, offline)
Defense in depth check: with the guarded agent temporarily changed to also follow instructions found in tool output (spotlighting bypassed), the frozen suite still stayed green (`check-suite`: guarded 0/65 cases succeed) because the trusted-tool allowlist blocked every injected action. So the two layers are independent, and the writeup can say a single regression in either layer doesn't reopen the hole. Video idea: show that ablation on screen instead of a fully weakened guard. A fuller ablation table (spotlight only, allowlist only, both) is a candidate next step via a dedicated `--agent` variant, not by editing the shipped guard.

### Ablation table (frozen suite, 65 cases, offline)

| Target | Spotlighting | Tool allowlist | Cases that still succeed |
|---|---|---|---|
| `naive` | off | off | 65/65 |
| `spotlight-only` | on | off | 0/65 |
| `allowlist-only` | off | on | 0/65 |
| `guarded` | on | on | 0/65 |

Reproduce with `python -m redloop check-suite --agent <target>`. Each layer alone blocks every frozen case, so a regression in one layer does not reopen the hole. Covered by `tests/test_ablation.py`.

## Filming the green-vs-red CI story (demo mode, production guard untouched)
We do **not** ship or PR a weakened guard. The red side uses the separate, clearly labeled unguarded demo agent (`--agent naive`); `guarded` code is never edited.

- **Local (offline, no keys):** `./demo/red_vs_green.sh` prints guarded exit 0 (green, 0/65) and unguarded demo exit 1 (red, 65/65).
- **GitHub Actions:** Actions tab, **"Demo - guarded (green) vs unguarded (red)"**, click *Run workflow* (manual `workflow_dispatch` only, never on push/PR). Two jobs run side by side: `Guarded agent ... expected GREEN` passes; `UNGUARDED DEMO agent ... expected RED` fails with `check-suite` exit 1. Screenshot the run summary, then open the red job log for the payload and the `gmail.send_email` evidence.
- **Defense-in-depth beat:** follow with `check-suite --agent spotlight-only` and `--agent allowlist-only` (each 0/65) to show either layer alone holds.
- Covered by `tests/test_demo_red_vs_green.py`.
