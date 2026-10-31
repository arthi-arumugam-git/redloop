# Scenario fixtures (13 JSON files in `scenarios/`)
Each file is a seeded, synthetic test: a task the user gave, a mock app state (inbox, docs, CRM, calendar, Slack, GitHub) with one injected instruction, and the harmful action the judge looks for in the action log. Secrets are dummy values (e.g. `REDLOOP_DUMMY_SECRET_123`); addresses use `example.test`.
Use them as-is with RedLoop, or as written specs for your own harness: copy the `state`, plant the payload in your staging app, run your agent, and check the action log.
calendar_destructive calendar_invite_exfil crm_destructive crm_note_exfil crm_record_tamper docs_destructive docs_share_external email_exfil github_comment_secret_leak github_destructive pixelinject_ticket_screenshot slack_unauthorized_send x_policy_override 
