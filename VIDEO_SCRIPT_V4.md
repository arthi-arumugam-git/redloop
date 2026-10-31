# RedLoop demo v4: hackathon-built work only (~3 min)

Why v4: the CV submit form says the 3-minute video must show only work built during the hackathon. Demo v3 opens on the offline showcase, which is pre-window code (commits through Oct 25 ET). v4 leads with work from Oct 26 ET onward. Every number below comes from a file in `results/` or a commit message; nothing new is claimed.

Pre-window pieces (sandbox tools, rule judge, check-suite, GitHub Action) may appear only as plumbing behind an in-window shot, with one spoken line: "The sandbox and test runner existed before the hackathon; everything you see running today was built this week."

| # | Time | Shot (in-window source) | Screen | Line |
|---|------|------|--------|------|
| 1 | 0:00-0:15 | Hook | Landing page `site/` (d2ae28a, Oct 29) | "Agents read untrusted email, docs and screenshots. One hidden instruction can leak a secret. RedLoop tests for that, and this week we pointed it at Muse Spark." |
| 2 | 0:15-0:50 | Muse Spark as target and judge (3d20145, b598701) | `results/MUSE_ASR.md` table | "65 frozen attacks against Muse Spark, with Muse Spark also judging. Zero breaches undefended, zero guarded, and the Muse judge agreed with our rule judge on all 111 completed runs. About $1.16 of target calls per sweep, $1.35 with the judge." |
| 3 | 0:50-1:20 | Live evolutionary search (492b603) | `results/MUSE_ATTACK_ASR.md` | "Then we let RedLoop mutate attacks live: 255 episodes, no breach. It did find a real bug, though: agents looping on document IDs." |
| 4 | 1:20-1:45 | The fix (5061624, f5707ed) | `results/MUSE_DOCS_VERIFY.md` before/after | "We added a list_docs tool. Same scenarios now finish in two tool calls, all green." |
| 5 | 1:45-2:10 | PixelInject (4ee1277) | `assets/pixelinject_demo.png`, scenario run | "New this week: injections hidden inside support-ticket screenshots." |
| 6 | 2:10-2:30 | Red vs green demo mode + ablation (9eef1a3, 80178d8) | Demo workflow run; ablation table | "Here is what a hole looks like: the unguarded demo agent goes red. Each guard layer alone keeps all 65 green." |
| 7 | 2:30-2:45 | Real third-party agent (b17b648, 1c3c05a) | Letta baseline 15/15 green | "It also tests agents we didn't write: a live Letta agent through an MCP mirror, 15 of 15 green." |
| 8 | 2:45-3:00 | Production + close (3453dab, 9ef5d12) | `redloop report` latency/cost table, ASR badge | "Retries on rate limits, infra errors marked unknown, never safe. RedLoop: find the hole, keep it closed." |

## Re-cut checklist (before Nov 5, 7:30 AM IST)
- [ ] Re-record narration from the Line column (`demo/narration.txt` is v3; write v4 alongside it).
- [ ] Build from `scripts/make_demo_video.py` with the shots above; drop the offline showcase opener.
- [ ] Keep it at or under 3:00.
- [ ] Upload, then swap the link in SUBMISSION_COPY.md and SUBMISSION_FIELDS.md.
