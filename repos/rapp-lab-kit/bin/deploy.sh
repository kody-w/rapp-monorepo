#!/bin/bash
# Project this repo onto the NAS, then VERIFY the projection.
#
# The repo is authority; the NAS is a channel. rapp-hive/1 section 9: a mirror
# "never becomes authority by availability or timestamp". So this is one-way -
# it never reads NAS state back into the repo - and it ends by comparing
# hashes, which is the honest version of a projection receipt: if the NAS does
# not byte-match the repo, the deploy FAILS rather than reporting success.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
. "$R/config.sh"
NAS="$NAS_USER@$NAS_HOST"
ssh_() { ssh -o BatchMode=yes -o StrictHostKeyChecking=no "$NAS" "$@"; }

"$R/bin/build-installer.sh" >/dev/null

STAGE=$(mktemp -d); trap 'rm -rf "$STAGE"' EXIT
cp -R "$R/nas/." "$STAGE/"
# Render live locators into the deployed artifacts only.
for f in $(find "$STAGE" -type f); do
  sed -i '' -e "s|@@INGEST_URL@@|$INGEST_URL|g" -e "s|@@BASE_URL@@|$BASE_URL|g" "$f" 2>/dev/null || \
  sed -i -e "s|@@INGEST_URL@@|$INGEST_URL|g" -e "s|@@BASE_URL@@|$BASE_URL|g" "$f"
done
printf '%s' "$LAN_PREFIX" > "$STAGE/web/wifimon/lan-prefix.txt"
printf '%s' "$TZ_NAME"    > "$STAGE/web/wifimon/timezone.txt"

ssh_ "mkdir -p '$NAS_DATA/rapp-lab/results' '$NAS_DATA/Web/wifimon/data'"
scp -o BatchMode=yes -q "$STAGE/rapp-lab/lab.sh" "$NAS:$NAS_DATA/rapp-lab/lab.sh"
ssh_ "chmod +x '$NAS_DATA/rapp-lab/lab.sh'"
for f in "$STAGE"/web/wifimon/*; do
  scp -o BatchMode=yes -q "$f" "$NAS:$NAS_DATA/Web/wifimon/$(basename "$f")"
done

echo "verifying projection:"
fail=0
check() { # local-file remote-path
  l=$(shasum -a 256 "$1" | cut -d' ' -f1)
  r=$(ssh_ "sha256sum '$2' 2>/dev/null | cut -d' ' -f1")
  if [ "$l" = "$r" ]; then printf '  ok    %s\n' "$(basename "$2")"
  else printf '  DIFF  %s  (repo %s / nas %s)\n' "$(basename "$2")" "${l:0:8}" "${r:0:8}"; fail=1; fi
}
check "$STAGE/rapp-lab/lab.sh" "$NAS_DATA/rapp-lab/lab.sh"
for f in "$STAGE"/web/wifimon/*; do check "$f" "$NAS_DATA/Web/wifimon/$(basename "$f")"; done
[ $fail -eq 0 ] || { echo "PROJECTION FAILED - NAS does not match repo"; exit 1; }

echo "live checks:"
code=$(curl -s -o /dev/null -w '%{http_code}' -m 10 "$BASE_URL/")
echo "  dashboard  HTTP $code"
# Probe the endpoint WITHOUT writing a data row: a health check that pollutes
# the dataset is a bad health check. These two paths prove PHP is executing and
# the guards are live.
m405=$(curl -s -o /dev/null -w '%{http_code}' -m 10 "$INGEST_URL")
m400=$(curl -s -o /dev/null -w '%{http_code}' -m 10 -X POST --data 'not-json' "$INGEST_URL")
echo "  ingest     GET=$m405 (want 405)  bad-json=$m400 (want 400)"
[ "$m405" = "405" ] && [ "$m400" = "400" ] || { echo "INGEST GUARDS FAILED"; exit 1; }
echo "PROJECTION OK"
