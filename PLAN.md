# RedLoop — plan (Meta Global AI Developer Hackathon)
Dates: kickoff Oct 26 12:00 PM ET -> submissions Nov 4 9:00 PM ET. Track: Indie, theme "Push the Frontier".

## Product
RedLoop is an agent that red-teams other agents. It automates indirect prompt injection (IPI) testing: seed attacks are
planted in tool outputs/documents, mutated by an attacker model, run against a sandboxed target agent, and judged for
secret leakage or unsafe tool calls. Every run produces a reproducible findings.json and attack-success metrics.

## Architecture
- app/sandbox.py — target agent + rule-based judge (secret leak, unsafe tool call)
- app/redloop.py — attacker loop: seed -> mutate -> attack -> judge -> log
- app/model.py — Meta Model API adapter (META_BASE_URL, META_API_KEY, META_MODEL=muse-spark); offline stubs without key

## Muse stack notes
- Muse Spark: attacker (mutation) + LLM judge
- Muse Code agent: build assistance
- Open-weights targets via Baseten/Modal/Fireworks credits for "attack any model" comparisons
- SAM 3.1 / Muse Image (optional): multimodal image-borne injection attacks

## Milestones
D1 API access + rules; D2-3 attacker loop on live Muse Spark; D4-5 LLM judge + IPI corpus; D6-7 multi-model leaderboard;
D8 defender/patch-suggestion loop + web UI; D9 video/writeup; D10 buffer, submit.
