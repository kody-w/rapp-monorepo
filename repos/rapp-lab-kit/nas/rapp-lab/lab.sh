#!/bin/bash
# RAPP brainstem installer lab - runs on the NAS, NOT on a build machine.
# That is the whole point: exec-proof doctrine says an installer must be proven
# on a clean environment that did not build it. This box is x86_64 Linux,
# always on, and reaches pypi.org directly (no corporate pip proxy), so it
# tests the installer the way a stranger actually gets it.
#
# usage: lab.sh <installer-url | /path/to/install.sh> [label]
set -u
# Self-locate: this script lives at <VOL>/rapp-lab/lab.sh, so the volume root
# is two levels up. No hardcoded QNAP path - works on any volume name.
ROOT="$(cd "$(dirname "$0")" && pwd)"
VOL="$(dirname "$ROOT")"
CS="$VOL/.qpkg/container-station"
export DOCKER_HOST=unix:///var/run/system-docker.sock
DOCKER=$CS/bin/docker
SRC="${1:?usage: lab.sh <url|path> [label]}"
LABEL="${2:-$(date +%H%M%S)}"
RUN="$ROOT/results/$(date +%Y-%m-%d)_${LABEL}"
mkdir -p "$RUN"

# Resolve the installer to a local file so every image tests the SAME bytes.
if [ -f "$SRC" ]; then cp "$SRC" "$RUN/install.sh"
else curl -fsSL --max-time 60 "$SRC" -o "$RUN/install.sh" || { echo "FATAL: could not fetch $SRC"; exit 1; }; fi
SHA=$(sha256sum "$RUN/install.sh" | cut -c1-16)
echo "installer: $SRC"
echo "sha256:    $SHA  ($(wc -l < "$RUN/install.sh") lines)"
echo "results:   $RUN"
echo

# PIP_INDEX_URL is deliberately NOT set: this NAS reaches pypi.org directly.
# Export PIP_INDEX_URL before calling if you need to mirror the Mac's proxy.
run() {
  name=$1; img=$2; pre=$3
  $DOCKER run --rm -e DEBIAN_FRONTEND=noninteractive \
    ${PIP_INDEX_URL:+-e PIP_INDEX_URL=$PIP_INDEX_URL} \
    -v "$RUN/install.sh":/install.sh:ro "$img" bash -c '
      export HOME=/root
      apt-get update -qq >/dev/null 2>&1
      apt-get install -y -qq curl sudo ca-certificates '"$pre"' >/dev/null 2>&1
      s=$(date +%s)
      bash /install.sh --no-launch >/tmp/o 2>&1
      echo "EXIT=$? TOTAL=$(( $(date +%s) - s ))s"
      grep -E "✗|Try:|ERROR|error:" /tmp/o | sed "s/\x1b\[[0-9;]*m//g" | head -15
      PORT=7071 timeout 25 ~/.brainstem/venv/bin/python \
        ~/.brainstem/src/rapp_brainstem/brainstem.py >/tmp/s 2>&1 &
      sleep 12
      echo "SERVER: $(curl -s --max-time 4 localhost:7071/version)"
      echo "--- install tail ---"; tail -20 /tmp/o | sed "s/\x1b\[[0-9;]*m//g"
    ' > "$RUN/$name.log" 2>&1
}

run ubuntu2404-bare      ubuntu:24.04 ""             &
run ubuntu2404-py-novenv ubuntu:24.04 "git python3"  &
run debian12             debian:12    ""             &
wait

pass=0; fail=0
{ echo "{"; echo "  \"installer\": \"$SRC\", \"sha\": \"$SHA\", \"ts\": \"$(date -Iseconds)\","; echo "  \"cases\": ["; } > "$RUN/summary.json"
first=1
for f in "$RUN"/*.log; do
  n=$(basename "$f" .log)
  t=$(grep -o 'TOTAL=[0-9]*s' "$f" | head -1)
  if grep -q 'EXIT=0' "$f" && grep -q 'SERVER: {"version"' "$f"; then
    echo "PASS  $n  $t"; ok=true; pass=$((pass+1))
  else
    echo "FAIL  $n  $t   -> $f"; ok=false; fail=$((fail+1))
  fi
  [ $first -eq 0 ] && echo "," >> "$RUN/summary.json"; first=0
  printf '    {"case":"%s","pass":%s,"time":"%s"}' "$n" "$ok" "${t#TOTAL=}" >> "$RUN/summary.json"
done
{ echo; echo "  ],"; echo "  \"pass\": $pass, \"fail\": $fail"; echo "}"; } >> "$RUN/summary.json"
echo
echo "RESULT: $pass passed, $fail failed  ($RUN/summary.json)"
[ $fail -eq 0 ]
