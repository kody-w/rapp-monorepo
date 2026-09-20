#!/bin/bash
# Regenerate the probe installer by embedding collect.py. The installer is a
# BUILD ARTIFACT of collect.py - never hand-edit nas/web/wifimon/install.sh.
set -eu
R="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$R" <<'PY'
import base64, sys, os
R = sys.argv[1]
b64 = base64.b64encode(open(f"{R}/probe/collect.py","rb").read()).decode()
tmpl = open(f"{R}/probe/installer.tmpl.sh").read()
out = tmpl.replace("@@COLLECT_B64@@", b64)
open(f"{R}/nas/web/wifimon/install.sh","w").write(out)
print("built nas/web/wifimon/install.sh (%d bytes)" % len(out))
PY
bash -n "$R/nas/web/wifimon/install.sh" && echo "syntax OK"
