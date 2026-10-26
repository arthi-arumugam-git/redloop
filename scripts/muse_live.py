"""Live Muse Spark run: frozen suite x {llama, llama-guarded}, Muse as target and judge.
Records tokens/USD per call. Never prints the API key."""
from __future__ import annotations
import json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from redloop.regressions import load_suite
from redloop.runner import run_scenario, load_scenario
from redloop.targets.llama_agent import LlamaAgent
from redloop.judge.llm_judge import ChatLLMJudge, agreement, JudgeError
from redloop.policy import Policy
from redloop.judge import judge as rule_judge

PIN = float(os.environ.get("MUSE_USD_PER_MTOK_IN", "0") or 0)
POUT = float(os.environ.get("MUSE_USD_PER_MTOK_OUT", "0") or 0)
FATAL = threading.Event(); FATAL_MSG = []

def usage_of(c):
    u = (c or {}).get("usage") or {}
    pt, ct = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
    cost = u.get("cost") or u.get("total_cost")
    usd = float(cost) if cost is not None else ((pt*PIN + ct*POUT)/1e6 if (PIN or POUT) else None)
    return pt, ct, usd

class Meter:
    def __init__(self): self.calls = []
    def wrap(self, fn):
        def inner(*a, **k):
            if FATAL.is_set(): raise RuntimeError("aborted: fatal HTTP status earlier")
            try: c = fn(*a, **k)
            except Exception as e:
                for code in ("401", "402", "403"):
                    if f"HTTP {code}" in str(e): FATAL.set(); FATAL_MSG.append(str(e))
                raise
            pt, ct, usd = usage_of(c); self.calls.append({"prompt_tokens": pt, "completion_tokens": ct, "usd": usd})
            return c
        return inner

def tot(calls):
    usd = [c["usd"] for c in calls if c["usd"] is not None]
    return {"calls": len(calls), "prompt_tokens": sum(c["prompt_tokens"] for c in calls),
            "completion_tokens": sum(c["completion_tokens"] for c in calls),
            "tokens": sum(c["prompt_tokens"]+c["completion_tokens"] for c in calls),
            "usd": round(sum(usd), 6) if usd else None}

def one(case, agent_name):
    if FATAL.is_set(): return None
    ag = LlamaAgent(defended=agent_name == "llama-guarded", timeout=120.0)
    tm = Meter(); ag._request = tm.wrap(ag._request)
    row = run_scenario(case["scenario"], ag, case["payload"], results_path=None)
    t = tot(tm.calls)
    row.update({"target_model": "muse-spark", "target_calls": tm.calls, "tokens": t["tokens"], "usd": t["usd"]})
    pol = load_scenario(case["scenario"])["policy"]
    jm = Meter(); j = ChatLLMJudge(timeout=120.0); j._request = jm.wrap(j._http)
    if row["status"] in ("red", "green"):
        try:
            llm = j.score(row["actions"], pol)
            rule = rule_judge(row["actions"], pol)
            ag_ = agreement(rule, llm)
            row["llm_judge"] = {"status": "red" if llm else "green", "agreement": ag_, "calls": jm.calls}
        except Exception as e:
            row["llm_judge"] = {"status": "error", "error": str(e)[:200], "calls": jm.calls}
    jt = tot(jm.calls); row["judge_tokens"] = jt["tokens"]; row["judge_usd"] = jt["usd"]
    print(f"{agent_name:14} {case['scenario']:32} {row['status']:7} judge={row.get('llm_judge',{}).get('status')} tok={row['tokens']}", flush=True)
    return row

def main():
    suite = load_suite("results/regression_suite.json")
    agents = sys.argv[1:] or ["llama", "llama-guarded"]
    jobs = [(c, a) for a in agents for c in suite["cases"]]
    with ThreadPoolExecutor(int(os.environ.get("MUSE_PAR", "6"))) as ex:
        rows = [r for r in ex.map(lambda x: one(*x), jobs) if r]
    out = Path("results/muse_live.jsonl")
    with out.open("w") as f:
        for r in rows: f.write(json.dumps(r, default=str) + "\n")
    if FATAL.is_set(): print("FATAL:", FATAL_MSG[0]); sys.exit(4)
main()
