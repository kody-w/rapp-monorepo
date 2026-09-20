#!/bin/bash
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
exec /usr/bin/python3 "$HOME/.rapp-tests/wifi/collect.py" "$HOME/.rapp-tests/wifi/spool" "unused"
