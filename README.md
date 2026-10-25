# RedLoop — agent that red-teams agents (Meta Global AI Dev Hackathon)
Run offline demo: `python3 -m app.redloop` -> findings.json
- app/sandbox.py: target agent + judge (secret leak, unsafe tool call)
- app/redloop.py: attacker loop (seed -> mutate via Muse Spark -> attack -> judge -> log)
- app/model.py: Meta Model API adapter (env META_BASE_URL, META_API_KEY, META_MODEL=muse-spark). Without key: offline stubs.
Meta stack notes: Muse Spark = attacker + judge; Muse Code agent for build; open-weights target via Baseten/Modal/Fireworks credits for "attack any model" comparison; SAM 3.1/Muse Image optional for multimodal (image-injection) attacks.
Next: LLM judge, attack-success leaderboard per target model, patch-suggestion step (attacker -> defender loop), web UI.
