# RedLoop: Nebius x NVIDIA Global AI Hackathon, paste-ready Devpost copy (draft)

Deadline: Fri Oct 30, 10:00 AM PT = **Oct 30, 10:30 PM IST**. Requirement: runs on Nebius Token Factory / AI Cloud and uses at least one NVIDIA open model.

## Run (once NEBIUS_API_KEY exists, ~20-40 min)
```
export NEBIUS_API_KEY=...            # from https://tokenfactory.nebius.com/
bash scripts/nebius_run.sh           # smoke test, attack sweep, frozen-suite check -> results/nebius/
```

## Name
RedLoop

## Tagline
Red-team CI for open-model agents: attack Nemotron-powered tool agents with prompt injections on Nebius, then gate every deploy on what got through.

## Description
**Problem.** Agents built on open models read email, docs and tickets and then call tools. Text hidden in that content (indirect prompt injection) can steer them into leaking secrets or taking destructive actions, and teams have no repeatable way to prove a fix stays fixed.

**What RedLoop does.**
- 13 seeded sandbox scenarios across email, Slack, GitHub, X, calendar, docs, CRM and a screenshot-OCR ticket.
- An evolutionary attacker that mutates injected payloads, with a fresh sandbox per trial.
- A rule judge that counts only successful outbound actions (exfiltration, unauthorized send, destructive action, policy override).
- A frozen regression suite plus a GitHub Action that fails CI when a previously blocked attack gets through again.

**Built on Nebius + NVIDIA.** The target agent is NVIDIA Nemotron served by Nebius Token Factory through its OpenAI-compatible API. Setting `NEBIUS_API_KEY` is the only config needed.

**Results on Nemotron (fill from results/nebius/ only, never estimate).**
- Attack sweep ASR, unguarded vs guarded: TBD
- Frozen suite, unguarded vs guarded: TBD
- Offline reference (already verified): naive agent 65/65 breached, guarded 0/65.

## Links
- Repo: https://github.com/arthi-arumugam-git/redloop
- Video: re-render with Nemotron run via scripts/make_demo_video.py; fallback https://youtu.be/T6BolZX1AWM

## Open question
Check whether Meta and Nebius rules allow the same project in both; if not, frame the Nebius entry as the Nemotron/Token Factory port.
