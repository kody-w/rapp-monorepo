Wi-Fi Monitor - NAS side
========================
index.php   dashboard (open @@BASE_URL@@/)
ingest.php  receiver; probes POST JSON here. LAN-only by source IP, no token.
api.php     feeds the dashboard
install.sh  probe installer:  curl -fsSL @@BASE_URL@@/install.sh | bash
data/       wifi-YYYY-MM-DD.jsonl, one line per sample per probe

Requires: QNAP Web Server enabled (Control Panel > Applications > Web Server).
Probes: any Mac ON WI-FI. A wired host cannot measure RF and is not a useful probe.
