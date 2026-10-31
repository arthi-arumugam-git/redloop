# Gumroad listing: Agent Prompt-Injection Red-Team Kit

**Name:** Agent Prompt-Injection Red-Team Kit
**URL slug:** `agent-injection-kit`
**Price:** Starter **$49** · Pro **$149** (Gumroad "versions" on one product)
**Summary line (shown under the title):** Templates, a checklist and a report format to test whether a poisoned email, doc or tool result can make your AI agent leak data or take actions nobody asked for.

## Description (paste into Gumroad)
Your AI agent reads email, docs, tickets and tool results. Any of those can carry instructions from someone else. If the agent follows them, it can forward data out of your company, delete records or post to a public channel, and the chat transcript will look normal.

This kit is a way to test for that before your customers find out. It comes out of RedLoop, an open-source harness I built that ran a frozen 65-case attack suite against Meta's Muse Spark model (results are included in the Pro version).

**Starter ($49)**
- Pre-launch checklist: 11 controls for agents and MCP servers (tool allowlists, confirmation on sends and deletes, secret handling, outbound allowlists, audit logs, CI gate)
- Attack templates: 7 payload families (authority spoof, task continuation, hidden markup, MCP tool-result poisoning, urgency, encoding, screenshot/OCR) across 9 injection locations, plus a mutation guide
- A how-to README: run the payloads against a staging agent and judge by the action log, not by what the model says

**Pro ($149)**: everything in Starter, plus
- 13 scenario fixtures (JSON) for email, docs, CRM, calendar, Slack and GitHub exfiltration, deletion and tampering cases
- A fill-in red-team report template (attack success rate, findings, fixes, retest)
- GitHub Action + CI setup guide that fails a pull request when an old attack works again
- A real results file from the Muse Spark run, so you can see what a finished report looks like

Demo video: https://youtu.be/T6BolZX1AWM

Only test systems you own or have written permission to test.

## FAQ
**Who is this for?** Engineers and founders shipping an AI agent or MCP server that touches email, docs, CRM, chat or code, and security folks asked to review one.
**Do I need RedLoop to use it?** No. Starter is plain markdown you can apply to any stack. The Pro fixtures and GitHub Action plug into RedLoop (open source on GitHub), but the fixtures also work as written test specs for your own harness.
**Which models does it cover?** The tests check what the agent *does*, so they apply to any model. The included sample run used Meta Muse Spark.
**Is this a pentest?** No. It's the kit I use to start one. If you want me to run the tests on your agent and write the report, reply to the receipt email and ask about a scoped engagement.
**Format?** A ZIP of markdown files, JSON fixtures, a YAML action file and one PNG. No video course.
**Refunds?** Full refund within 14 days if it isn't useful to you. Reply to the receipt email.
**Updates?** You get any updated version of the files at no charge through your Gumroad library.
