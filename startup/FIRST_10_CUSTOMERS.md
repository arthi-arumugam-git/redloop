# First 10 Target Customers (US / remote, USD)
Research date: Oct 29, 2026 (web search + prior public knowledge). **No founder emails were verified.** "Unknown" = find via the company site / YC page / LinkedIn before sending; never guess an address. Verify each company is still active before outreach.

| # | Company | Who (public) | What the agent touches | Source | Email | Angle |
|---|---|---|---|---|---|---|
| 1 | AgentMail (SF, YC S25, $6M seed Mar 2026) | Haakam Aujla, CEO | Gives agents their own inboxes — every inbound email is untrusted input to a customer's agent | TechCrunch 2026-03-10; ycombinator.com/companies/agentmail | Unknown | "Your customers' agents read mail from strangers. Offer a tested 'injection-safe' reference config; we'll run RedLoop's email_exfil scenarios on your sample agent." Also a partner/co-marketing angle. |
| 2 | item (SF, YC F25) | Andres Santanilla CEO, Akshay Guthal CTO | Agentic CRM; agents send follow-ups and upsell emails autonomously | ycombinator.com/companies/item | Unknown | CRM-note exfiltration hit 100% ASR on unguarded mock agents; autonomous sends = unauthorized-send risk. Snapshot before enterprise deals. |
| 3 | Fixture (SF, tiny, ~$125K) | Founders unknown | AI-first CRM with API + MCP | linkedin.com/company/fixture-gtm | Unknown | Too small for $5K; pitch the $149 kit + free CI action. |
| 4 | Nex AI / WUPHF (SF, $3.5M seed) | Najmuzzaman Mohammad CEO | Context graph via MCP over contacts, deals, meetings, emails; open-source WUPHF | everydev.ai/developers/nex-crm | Unknown | Open-source to open-source: offer a PR adding a RedLoop CI gate to WUPHF; upsell Snapshot on Nex MCP tools. |
| 5 | Composio (SF) | Founders: check site | 100s of tool integrations for agents (Gmail, Slack, GitHub) | composio.dev (prior knowledge, verify) | Unknown | Tool results from their integrations are the injection surface; joint "poisoned tool result" benchmark. |
| 6 | Arcade.dev (SF) | Alex Salazar, CEO (verify) | Auth'd tool calling for agents | arcade.dev (verify) | Unknown | Their pitch is safe tool auth; RedLoop tests what happens after auth when the content is hostile. |
| 7 | Browserbase (SF) | Paul Klein IV, CEO (verify) | Headless browsers for agents; web pages = untrusted input | browserbase.com (verify) | Unknown | Visual/OCR injection scenarios; Full Assessment on a reference agent (Stagehand). |
| 8 | Lindy (SF/remote) | Flo Crivello, CEO (verify) | No-code agents over Gmail, calendar, CRM | lindy.ai (verify) | Unknown | Email→action agents are the textbook case; Snapshot on one template agent. |
| 9 | Letta (SF) | Charles Packer, Sarah Wooders (verify) | Stateful agents w/ memory; poisoned memory persists | letta.com (verify) | Unknown | Memory-tamper scenario; open-source collaboration first. |
| 10 | Smithery (MCP registry) | Founders: check site | Hosts/lists MCP servers | smithery.ai (verify) | Unknown | Offer RedLoop scan as a badge for listed servers; distribution play more than a sale. |

Priority for first 5 emails: #1, #2, #4, #8, #6 (clear email/CRM surface, funded, reachable via YC/X).
How to find emails legitimately: YC company page "contact", company site /security or /contact, founder's X bio, GitHub commit emails on public repos (only if publicly listed). If none, use the site contact form or X DM.
