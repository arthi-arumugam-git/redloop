# RedLoop: 3-minute demo video script

Recorded once a real Llama endpoint is configured; every command below also runs fully offline on the mock targets.
One-command pipeline: `./scripts/showcase.sh` (or `make showcase`). Artifacts land in `build/showcase/`.

| Time | Screen | Voiceover (short) |
|------|--------|-------------------|
| 0:00–0:20 | README hero + architecture diagram | "Agents that read email, docs and tickets can be hijacked by text hidden in that content. RedLoop is an agent that red-teams your agents, then turns what it finds into a CI test." |
| 0:20–0:45 | `python3 -m redloop list` | "12 seeded scenarios across 7 mock tools: gmail, slack, github, x, calendar, docs, CRM. Each one has a policy: no exfiltration, no unauthorized send, no destructive action, no policy override." |
| 0:45–1:25 | `python3 -m redloop attack --all --agents naive,guarded,llama,llama-guarded` | "The attacker mutates injection payloads and keeps what the judge scores as violations. Here's a real Llama tool-calling agent, and the same agent with spotlighting and a tool allowlist." |
| 1:25–1:50 | `build/showcase/ASR.md` (report table) | "Attack success rate per scenario and per agent. On mocks, naive fails 65/65 and guarded 0/65. On live Muse Spark, even undefended Muse resisted every frozen payload: 0% ASR, guarded 0%." |
| 1:50–2:10 | Judge agreement output (rule judge vs Llama/LLM judge) | "We don't trust one judge. The LLM judge is calibrated against the rule judge; on live Muse Spark the Muse judge agrees with the rule judge on 100% of verdicts, 111 of 111." |
| 2:10–2:40 | `export-suite` then `check-suite` guarded (pass) and naive (exit 1) | "Every successful attack is frozen into a regression suite. Ship a prompt or model change and CI replays all of them: guarded passes, naive fails the build." |
| 2:40–3:00 | `action.yml` + green GitHub Actions run, Streamlit dashboard | "Drop it into any repo as a GitHub Action. RedLoop: find the hole, then make sure it stays closed." |

## Before recording
- Set `LLAMA_BASE_URL`, `LLAMA_API_KEY`, `LLAMA_MODEL` (and `JUDGE_*` for the LLM judge), then rerun with the llama agents so the table shows a real model.
- Live Muse numbers (Oct 26 2026 ~9:40 PM IST, API live): llama 0/56 red + 9 ERROR, llama-guarded 0/55 red + 10 ERROR, judge agreement 100% (111/111), ≈$2.70. Source: `results/MUSE_ASR.md`.
- Offline baseline (mock targets, this run): naive 65/65 frozen cases still succeed, guarded 0/65.
