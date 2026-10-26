#!/usr/bin/env bash
# One-command offline end-to-end pipeline for the demo video (same as `make showcase`).
set -euo pipefail
PY=${PYTHON:-python3}
D=${DEMO_DIR:-build/showcase}
rm -rf "$D" && mkdir -p "$D"
$PY -m redloop list
$PY -m redloop attack --all --agents naive,guarded --results "$D/attack.jsonl"
$PY -m redloop report --results "$D/attack.jsonl" --out "$D/ASR.md"
$PY -m redloop export-suite --results "$D/attack.jsonl" --out "$D/suite.json"
echo "== guarded agent vs frozen suite (expect PASS) =="
$PY -m redloop check-suite --suite "$D/suite.json" --agent guarded
echo "== naive agent vs frozen suite (expect FAIL, exit 1) =="
if $PY -m redloop check-suite --suite "$D/suite.json" --agent naive; then echo "unexpected: naive passed"; exit 1; fi
echo "Showcase artifacts in $D: attack.jsonl ASR.md suite.json"
