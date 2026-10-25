"""RedLoop dashboard skeleton.  Run:  streamlit run dashboard/app.py"""

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from redloop.dashboard_data import load_results, summarize  # noqa: E402

st.set_page_config(page_title="RedLoop", layout="wide")
st.title("RedLoop: indirect prompt injection red-team results")

path = st.sidebar.text_input("Results file", "results/results.jsonl")
rows = load_results(path)
if not rows:
    st.info(f"No results at {path}. Run `python -m redloop run --all --agent naive` "
            "or `python -m redloop attack --all` first.")
    st.stop()

agents = sorted({r["agent"] for r in rows})
picked = st.sidebar.multiselect("Agents", agents, default=agents)
modes = sorted({r.get("mode", "single") for r in rows})
mode = st.sidebar.multiselect("Mode", modes, default=modes)
rows = [r for r in rows if r["agent"] in picked and r.get("mode", "single") in mode]

summary = summarize(rows)
c1, c2, c3 = st.columns(3)
c1.metric("Runs", len(rows))
c2.metric("RED runs", sum(r.get("status") == "red" for r in rows))
c3.metric("Scenarios", len({r["scenario"] for r in rows}))

st.subheader("Attack success rate by scenario and agent")
st.dataframe(summary, width="stretch")

st.subheader("ASR per agent")
by_agent = {}
for item in summary:
    if item["asr"] is not None:
        by_agent.setdefault(item["agent"], []).append(item["asr"])
st.bar_chart({a: sum(v) / len(v) for a, v in by_agent.items()})

st.subheader("Inspect a run")
labels = [f"{r['status'].upper():7} {r['scenario']} / {r['agent']} / {r['run_id'][:8]}" for r in rows]
choice = st.selectbox("Run", range(len(rows)), format_func=lambda i: labels[i])
run = rows[choice]
st.code(run.get("payload", ""), language="text")
st.json({"violations": run.get("violations", []), "actions": run.get("actions", [])}, expanded=False)
