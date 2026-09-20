#!/bin/bash
# Wi-Fi monitor probe installer - self-contained, safe to re-run.
set -e
D="$HOME/.rapp-tests/wifi"; mkdir -p "$D/spool"
INGEST="${WIFIMON_INGEST:-@@INGEST_URL@@}"
NAME=$(scutil --get ComputerName 2>/dev/null || hostname)

IF=$(route -n get default 2>/dev/null | awk '/interface:/{print $2}')
if networksetup -getairportnetwork "$IF" >/dev/null 2>&1; then
  echo "[ok] $NAME routes over $IF (Wi-Fi) - valid probe vantage point"
else
  echo "[!!] $NAME routes over $IF, which is NOT Wi-Fi."
  echo "     A wired host cannot see RF signal, channel or airtime."
  echo "     Continuing anyway - it will still track mesh + internet health."
fi

echo "@@COLLECT_B64@@" | base64 -d > "$D/collect.py"
cat > "$D/collect.sh" <<'SH'
#!/bin/bash
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
exec /usr/bin/python3 "$HOME/.rapp-tests/wifi/collect.py" "$HOME/.rapp-tests/wifi/spool" "unused"
SH
chmod +x "$D/collect.sh" "$D/collect.py"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$HOME/Library/LaunchAgents/com.kody.wifimon.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.kody.wifimon</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$D/collect.sh</string></array>
  <key>EnvironmentVariables</key><dict><key>WIFIMON_INGEST</key><string>$INGEST</string></dict>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$D/monitor.log</string>
  <key>StandardErrorPath</key><string>$D/monitor.err</string>
  <key>ProcessType</key><string>Background</string><key>LowPriorityIO</key><true/>
</dict></plist>
PL
launchctl bootout gui/$(id -u)/com.kody.wifimon 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/com.kody.wifimon.plist"
echo "[ok] installed + scheduled every 5 min on $NAME"
echo "[..] running one sample now..."
WIFIMON_INGEST="$INGEST" "$D/collect.sh" || true
echo "[ok] done. logs: $D/monitor.log"
