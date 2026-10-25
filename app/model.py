"""Model adapter. Fill in Meta Model API endpoint/auth after kickoff (env: META_API_KEY, META_BASE_URL, META_MODEL)."""
import json, os, urllib.request
def chat(messages, model=None):
    base, key = os.environ.get("META_BASE_URL"), os.environ.get("META_API_KEY")
    if not (base and key):
        return {"role": "assistant", "content": "[stub] " + messages[-1]["content"][:80]}
    body = json.dumps({"model": model or os.environ.get("META_MODEL", "muse-spark"), "messages": messages}).encode()
    req = urllib.request.Request(f"{base}/chat/completions", body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)["choices"][0]["message"]
