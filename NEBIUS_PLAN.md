# RedLoop on Nebius Token Factory (Nebius x NVIDIA Global AI Hackathon)

- Hackathon: https://nebiusglobalaihackathon.devpost.com/ ($50K; 1st $20K). Arthi registered Oct 21.
- Deadline: Fri Oct 30, 10:00 AM PT = **Oct 30, 10:30 PM IST**.
- Requirement (Devpost checklist mail, Oct 27): runs on Nebius Token Factory or Nebius AI Cloud AND uses at least one NVIDIA open model.

## Why RedLoop fits with no code change
RedLoop's target agent already talks to any OpenAI-compatible `/chat/completions` endpoint via env vars
(`redloop/targets/env.py`, `llama_agent.py`). Nebius Token Factory is OpenAI-compatible.

```
export LLAMA_BASE_URL=https://api.tokenfactory.nebius.com/v1
export LLAMA_API_KEY=$NEBIUS_API_KEY
export LLAMA_MODEL=nvidia/nemotron-3-super-120b-a12b   # or nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B (cheap)
```
(us-central1 models may need https://api.tokenfactory.us-central1.nebius.com/v1 — verify on first call.)

## One-env-var setup (added Oct 27, 11:10 PM IST)
`export NEBIUS_API_KEY=...` is now enough: `resolve_llama_env()` maps it to Token Factory
(`https://api.tokenfactory.nebius.com/v1`) and `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` by default.
Override with `NEBIUS_BASE_URL` / `NEBIUS_MODEL` (e.g. `nvidia/nemotron-3-super-120b-a12b`). Model IDs unverified until first live call.

## Steps once a key exists
1. Smoke test one scenario against Nemotron Nano, then Super (tool calling must work).
2. Run naive vs guarded attack suite; save results/NEBIUS_NEMOTRON.md (real numbers only).
3. Re-render demo video with Nebius/Nemotron run; upload YouTube Unlisted.
4. Devpost submission: repo link, video, description framed as "red-team CI for open-model agents on Nebius".

## Blocker
No Nebius API key on the box. Arthi must create a Token Factory account at https://tokenfactory.nebius.com/
(billing may require a card; hackathon credits exist) and paste the key into chat.
Check Meta hackathon rules for cross-submission before submitting the same project to both.
