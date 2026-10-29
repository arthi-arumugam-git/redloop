#!/usr/bin/env bash
# Drive one Letta Code agent through the RedLoop email mirror, one case per
# fresh conversation, then score. Sends are recording stubs; nothing is mailed.
#
# One-time setup (inside `letta`, on the agent you will test):
#   /mcp add --transport stdio email --cwd /ABS/PATH/redloop python3 -m redloop.mcp_target --run-dir /ABS/PATH/redloop-private/letta-email serve
#   (absolute paths only: Letta stores the command verbatim and does not expand $VARS or ~)
#
# Usage: LETTA_AGENT_ID=agent-... RUN_DIR=~/redloop-private/letta-email scripts/letta_mcp_run.sh
set -euo pipefail

: "${LETTA_AGENT_ID:?set LETTA_AGENT_ID to the agent with the email MCP attached}"
RUN_DIR="${RUN_DIR:-$HOME/redloop-private/letta-email}"
PY="${PYTHON:-python3}"
M=("$PY" -m redloop.mcp_target --run-dir "$RUN_DIR")
TASK="$("$PY" -c 'from redloop.mcp_target.core import load_config; print(load_config("letta_email")["task"])')"

case "$RUN_DIR" in "$(pwd)"/*) echo "RUN_DIR must live outside the repo" >&2; exit 2;; esac
mkdir -p "$RUN_DIR/transcripts"
[ -f "$RUN_DIR/cases.json" ] || "${M[@]}" cases >/dev/null

# Control first; the core-memory payload last so it cannot leak into other cases.
mapfile -t CASES < <("$PY" -c 'import json,sys; c=list(json.load(open(sys.argv[1]))); c.sort(key=lambda k:(k!="control", k=="hw05_letta_memory")); print("\n".join(c))' "$RUN_DIR/cases.json")

for case_id in "${CASES[@]}"; do
  "${M[@]}" set-case "$case_id"
  echo "== $case_id"
  # --yolo: no approval prompts, so we measure the model's decision, not the gate.
  letta -p "$TASK" --agent "$LETTA_AGENT_ID" --new --yolo --output-format json \
    > "$RUN_DIR/transcripts/$case_id.json" 2> "$RUN_DIR/transcripts/$case_id.err" \
    || echo "   letta exited $? (see transcripts/$case_id.err)"
done

"${M[@]}" score
