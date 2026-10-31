# Publish checklist (Arthi does the steps marked 🔒; nothing is published yet)

## Before Gumroad
- [x] Files ready: Starter = README.md, prelaunch_checklist.md, attack_templates.md. Pro adds report_template.md and pro/ (13 scenarios, action.yml, CI_SETUP.md, SCENARIOS.md, sample_results_MUSE_ASR.md, assets/pixelinject_demo.png)
- [x] Build the zips: `cd /workspace/money/meta/redloop/gumroad && ./build_zips.sh` → `dist/agent-injection-kit-starter.zip`, `dist/agent-injection-kit-pro.zip`
- [ ] 🔒 Confirm prices ($49 / $149) and the 14-day refund line in the FAQ
- [ ] 🔒 Confirm the RedLoop repo is **public** with a LICENSE (the Pro CI guide points to github.com/arthi-arumugam-git/redloop; the local checkout has no LICENSE file)
- [ ] 🔒 Cover image 1280×720: a real screenshot of results/MUSE_ASR.md or the PNG in assets/. No mockups.

## Gumroad steps
1. 🔒 Log in at gumroad.com → **Products → New product** → type **Digital product**.
2. Name: `Agent Prompt-Injection Red-Team Kit`. Price: `49`. Click **Next: Customize**.
3. **Description**: paste the "Description" section of LISTING.md. Add the FAQ under it (or use Gumroad's FAQ block if your editor shows one).
4. **Cover**: upload the cover image. **Thumbnail**: a square crop of it.
5. **Summary** ("You'll get…"): paste the summary line from LISTING.md.
6. **Versions** (Product → Content → "Add version" / "Variants"): `Starter` +$0, `Pro` +$100. Attach `dist/agent-injection-kit-starter.zip` to Starter and `dist/agent-injection-kit-pro.zip` to Pro.
7. **Settings**: URL slug `agent-injection-kit`. Turn **off** "Allow customers to pay what they want" for launch.
8. **Payout**: Settings → Payments: a bank or PayPal account must be connected, otherwise sales are held.
9. Click **Publish** 🔒, then open the public URL in a logged-out window and test-buy with a 100% discount code to confirm both zips download.
10. Put the product link in redloop README and in GUMROAD_PACK.md.

## After publish (needs Arthi's approval for each post)
- Posting the link on X/LinkedIn or the repo README is an external post: draft only until she approves.
