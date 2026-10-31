# NEBIUS — BLOCKED on NEBIUS_API_KEY
Deadline: **Fri Oct 30, 10:30 PM IST** (10:00 AM PT). Requirement: run on Nebius Token Factory + at least one NVIDIA open model.
Status (Oct 28, 3:40 PM IST): code is ready (`resolve_llama_env()` maps NEBIUS_API_KEY → Token Factory + Nemotron). **There is no key on the box. None has been invented.**

## Arthi action
1. Sign up at https://tokenfactory.nebius.com/ (a card may be needed; check for hackathon credits).
2. Create an API key → paste it into chat (it'll be used as an env var only, never committed).

## What runs when the key arrives (cd /workspace/money/meta/redloop)
- [ ] `export NEBIUS_API_KEY=...` (optional: `NEBIUS_MODEL=nvidia/nemotron-3-super-120b-a12b`; the default is NVIDIA-Nemotron-3-Nano-30B-A3B)
- [ ] `bash scripts/nebius_run.sh` → smoke test, attack sweep llama vs llama-guarded, ASR report, frozen-suite check
- [ ] If the model ID or base URL 404s: verify on the Token Factory model list; try `NEBIUS_BASE_URL=https://api.tokenfactory.us-central1.nebius.com/v1`
- [ ] Artifacts: results/nebius/{smoke.txt, attack.jsonl, ASR.md, suite_guarded.txt, suite_naive.txt}
- [ ] Paste the real numbers into NEBIUS_SUBMISSION.md (Results)
- [ ] Re-render the demo (scripts/make_demo_video.py) with the Nebius run → YouTube Unlisted/Public
- [ ] Devpost: repo, video, description ("red-team CI for open-model agents on Nebius")
- [ ] Check the Meta hackathon cross-submission rules first
Time needed after the key arrives: ~2–3 h. The key must arrive by **Oct 30, ~6 PM IST**.
