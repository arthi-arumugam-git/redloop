# RedLoop: video script outline (~3 min, PR red to green)

Offline-first: every shot below runs on mock targets with no keys. Muse Spark shots are optional and only added once Meta Model API billing clears (currently 402 billing_not_configured).

| # | Time | Shot | Command / screen | Line |
|---|------|------|------------------|------|
| 1 | 0:00-0:20 | Hook | README hero, badge, flow diagram | "Agents read untrusted email, tickets and screenshots. One hidden instruction can leak a secret. RedLoop is a unit test for that." |
| 2 | 0:20-0:50 | Guarded vs unguarded | Actions: run "Demo - guarded (green) vs unguarded (red)" (workflow_dispatch); production guard untouched | "Same 65 attacks, two agents: our guarded agent, and an unguarded demo agent with no defenses." |
| 3 | 0:50-1:20 | CI goes red | Action log: `check-suite` exit 1, 65/65 cases succeed | "CI replays all 65 frozen attacks. The build fails, and it shows the ASR." |
| 4 | 1:20-1:45 | Evidence | Action log row: injected payload then `gmail.send_email` with the secret | "This is the exact payload, and the agent emailing the secret out." |
| 5 | 1:45-2:10 | Green + defense in depth | Guarded job green (0/65); then `check-suite --agent spotlight-only` / `allowlist-only` each 0/65 (ablation table) | "Guarded stays green at 0%. And either layer alone still blocks all 65, so one regression doesn't reopen the hole." |
| 6 | 2:10-2:30 | PixelInject | `assets/pixelinject_demo.png` + scenario run | "It also catches injections hidden in ticket screenshots." |
| 7 | 2:30-2:50 | Production | `python -m redloop report` (ASR + latency table), exit code 3 = UNKNOWN | "Seconds per run, and infra errors are UNKNOWN, never safe." |
| 8 | 2:50-3:00 | Close | Dashboard trend + badge | "RedLoop: find the hole, keep it closed." |

Post-billing add-on (do not show placeholders): Muse Spark judge verdict and tokens/USD columns from a real run.
