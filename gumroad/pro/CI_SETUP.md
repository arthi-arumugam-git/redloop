# CI setup: fail the build when a prompt-injection attack starts working again
Uses the RedLoop GitHub Action (`action.yml`, copied here from github.com/arthi-arumugam-git/redloop).

1. Freeze a regression suite from your red-team run:
   `python -m redloop export-suite --out results/regression_suite.json`
2. Commit `results/regression_suite.json`.
3. Add `.github/workflows/redloop.yml`:
```yaml
name: prompt-injection-regression
on: [pull_request]
jobs:
  redloop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: arthi-arumugam-git/redloop@main
        with:
          agent: guarded
          suite: results/regression_suite.json
```
4. The job fails if any frozen attack succeeds against the agent. An errored case counts as UNKNOWN, not as a pass.

`agent` options in the stock harness: `naive`, `guarded`, `llama`, `llama-guarded`. To test your own agent, add an adapter in `redloop/agents/` (see the repo README).
