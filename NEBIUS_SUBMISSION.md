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

## Rules check (Oct 30 2026, 4:10 AM IST, from nebiusglobalaihackathon.devpost.com/rules)
- Deadline confirmed: Oct 30 10:00 AM PT = 10:30 PM IST. Drafts can be saved on Devpost before then.
- No clause bars the same project in another hackathon. Requirement: new, or significantly updated after Aug 26 2026 (RedLoop first commit Oct 25 2026, so it qualifies; say so in the "what was updated" field).
- Must make a runtime call to the Token Factory API with at least one NVIDIA open model (Nemotron). Key is still the only blocker.
- Required: working demo URL, public repo with detectable OSS license + README naming Nemotron/Token Factory use, YouTube video under 3 min, track pick, Nebius/NVIDIA feedback section.
- Track pick: Coding and Agentic Engineering (agent security testing tool) or Best Apps and Agents. One Overall OR one Track award, plus one Bonus.
- Easy extras: fill the feedback section (Most Valuable Feedback $100); Best Use of Tavily $3,000 needs a functional runtime Tavily API call (e.g. a web-search tool in a scenario). Tavily credits come with the Nebius Builder Program.
- Meta event page (Oct 30 4:05 AM IST) still links no Official Rules, so nothing published forbids cross-submission there either.

## Paste-ready extra fields (added Oct 30 5:10 AM IST)
**What was built or updated after Aug 26 2026:** Everything. The repo's first commit is Oct 25 2026 (36 commits so far): sandboxed mock tools for email, Slack, GitHub, X, calendar, docs and CRM; 13 seeded indirect-injection scenarios; the evolutionary attacker; the rule judge; the frozen regression suite and GitHub Action; an MCP mirror target; and the Nebius Token Factory target for Nemotron.

**Track:** Coding and Agentic Engineering (first choice).

**Nebius / NVIDIA feedback (fill only after the real run, from what actually happened):** time from signup to first working call; any OpenAI-compat differences hit (tool-calling format, streaming, rate limits); Nemotron tool-call reliability seen in results/nebius/; one concrete docs fix we'd want. Do not write this section before the run.

**Submit checklist (after key):** run `bash scripts/nebius_run.sh` -> paste ASR numbers from results/nebius/ into Results -> render video with scripts/make_demo_video.py and upload to YouTube (<3 min) -> confirm repo public with LICENSE and README naming Nemotron + Token Factory -> demo URL -> feedback -> submit before 10:30 PM IST.
