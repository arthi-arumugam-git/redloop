#!/usr/bin/env bash
# One-command Nebius x NVIDIA run: smoke test, then frozen suite + attack on Nemotron via Token Factory.
# Needs only NEBIUS_API_KEY (optional NEBIUS_MODEL / NEBIUS_BASE_URL). Never prints the key.
set -euo pipefail
: "${NEBIUS_API_KEY:?export NEBIUS_API_KEY first (https://tokenfactory.nebius.com/)}"
OUT=${OUT:-results/nebius}
mkdir -p "$OUT"
PY=${PYTHON:-python3}
echo "== smoke test (1 scenario, llama target -> Nebius Token Factory) =="
first=$($PY -m redloop list | awk 'NF{print $1; exit}')
$PY -m redloop run --scenario "$first" --agent llama --results "$OUT/smoke.jsonl" | tee "$OUT/smoke.txt"
echo "== attack sweep: llama vs llama-guarded =="
$PY -m redloop attack --all --agents llama,llama-guarded --results "$OUT/attack.jsonl"
$PY -m redloop report --results "$OUT/attack.jsonl" --out "$OUT/ASR.md"
echo "== frozen suite check =="
$PY -m redloop check-suite --suite results/regression_suite.json --agent llama-guarded | tee "$OUT/suite_guarded.txt" || true
$PY -m redloop check-suite --suite results/regression_suite.json --agent llama | tee "$OUT/suite_naive.txt" || true
echo "Artifacts in $OUT. Copy real numbers into NEBIUS_SUBMISSION.md (Results section)."
