# Copy to config.sh and edit. config.sh is gitignored: it holds LIVE LOCATORS,
# which rapp-hive/1 section 13 forbids in a shareable template ("excludes ...
# live channel locator"). Tracked code is the DOGG projection; this is the estate.
NAS_HOST=nas.example.lan         # NAS address or hostname
NAS_USER=admin                   # NAS ssh user (key auth; no passwords)
NAS_DATA=/share/CACHEDEV1_DATA   # NAS volume root
LAN_PREFIX=10.0.0.               # only these sources may POST to ingest.php
INGEST_URL="http://${NAS_HOST}/wifimon/ingest.php"
BASE_URL="http://${NAS_HOST}/wifimon"
TZ_NAME=UTC                      # PHP timezone; QNAP defaults to Asia/Taipei
