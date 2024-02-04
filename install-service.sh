#! /usr/bin/env bash
set -euo pipefail
set -x

SERVICE_CONF_PATH=/etc/systemd/system/auto-connect-midi.service

poetry install
venvDir=$(poetry env info | grep '^Path' | head -n 1 | awk '{print $2}')
sudo ln -fs "$venvDir/bin/auto-connect-midi" /usr/local/bin/auto-connect-midi
sudo cp ./auto-connect-midi.service "$SERVICE_CONF_PATH"
sudo sed -i 's/User=unset/User='"$(whoami)"'/g' "$SERVICE_CONF_PATH"
sudo systemctl daemon-reload
sudo systemctl restart auto-connect-midi
systemctl status auto-connect-midi

