#!/usr/bin/env bash
# DEMO ONLY: local guarded (green) vs unguarded demo agent (red). Offline, no keys.
set -u
cd "$(dirname "$0")/.."
echo "== guarded (production defenses) =="
"${PYTHON:-python3}" -m redloop check-suite --suite results/regression_suite.json --agent guarded; g=$?
echo "== UNGUARDED DEMO agent (naive, no defenses) =="
"${PYTHON:-python3}" -m redloop check-suite --suite results/regression_suite.json --agent naive; n=$?
echo "guarded exit=$g (expect 0, green)  unguarded-demo exit=$n (expect 1, red)"
[ "$g" -eq 0 ] && [ "$n" -eq 1 ]
