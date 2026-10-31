#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"; rm -rf dist; mkdir -p dist
python3 - <<'PY'
import zipfile,os
def mk(name,items):
    with zipfile.ZipFile(f'dist/{name}','w',zipfile.ZIP_DEFLATED) as z:
        for it in items:
            if os.path.isdir(it):
                for r,_,fs in os.walk(it):
                    for f in fs: z.write(os.path.join(r,f))
            else: z.write(it)
base=['README.md','prelaunch_checklist.md','attack_templates.md']
mk('agent-injection-kit-starter.zip',base)
mk('agent-injection-kit-pro.zip',base+['report_template.md','pro'])
PY
ls -la dist
