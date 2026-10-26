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
| Does it fail safely? | Retries/backoff and timeouts on model calls, partial results saved, non-zero exit on infra error (distinct from red finding) | TODO |
| Can a customer see value in 3 minutes? | `make showcase` + DEMO_SCRIPT.md (naive 91% ASR to guarded 0%) | Done (bdec6b8) |

## Product framing for the writeup
- **Customer:** teams shipping tool-using agents (support, coding, ops) who need a prompt-injection regression test before every deploy.
- **Wedge:** free GitHub Action; paid hosted dashboard with trend history and new attack packs each week.
- **Why now:** agents now read untrusted tool output (email, web, tickets); one injected instruction can exfiltrate data or send mail.

## Next build steps (priority order)
1. Cost and latency columns in `report` (tokens, seconds, USD per run).
2. Retry/timeout wrapper on model calls; exit code 2 for infra errors vs 1 for red findings.
3. Run the suite on Muse Spark via Meta Model API as soon as kickoff grants access; publish before/after table.
4. Short "Deploy in 5 minutes" section at the top of README.
