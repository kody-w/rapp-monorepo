#!/bin/bash
# Drive the NAS installer lab from this Mac.
# Why the NAS and not here: exec-proof says prove an installer on a machine that
# did NOT build it. The NAS is x86_64 Linux, always on, and reaches pypi.org
# directly - no MS pip proxy, unlike Docker on this Mac. That makes it the
# closest thing to what a stranger actually runs.
#   usage: nas-lab.sh <installer-url|path> [label]
#          nas-lab.sh --results            # list past runs
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"
. "$R/config.sh"   # live locators live here, never in the tracked code
NAS="$NAS_USER@$NAS_HOST"
if [ "${1:-}" = "--results" ]; then
  ssh -o BatchMode=yes $NAS 'for d in $NAS_DATA/rapp-lab/results/*/; do
      echo "== $(basename $d)"; grep -hE "^(PASS|FAIL|RESULT)" $d/../../last-run.log 2>/dev/null
      python3 -c "import json,sys;d=json.load(open(\"$d/summary.json\"));print(\"   \",d[\"pass\"],\"pass\",d[\"fail\"],\"fail  sha\",d[\"sha\"])" 2>/dev/null
    done'; exit 0
fi
SRC="${1:?usage: nas-lab.sh <installer-url|path> [label]}"
LABEL="${2:-run}"
# A local file has to be shipped over first; a URL the NAS fetches itself.
if [ -f "$SRC" ]; then
  scp -o BatchMode=yes -q "$SRC" $NAS:$NAS_DATA/rapp-lab/_incoming.sh
  SRC=$NAS_DATA/rapp-lab/_incoming.sh
fi
ssh -o BatchMode=yes $NAS "cd $NAS_DATA/rapp-lab && ./lab.sh '$SRC' '$LABEL'"
