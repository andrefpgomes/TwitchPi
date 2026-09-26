#!/bin/bash
set -euo pipefail
BASE="/opt/twitch-pi"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute: sudo bash update.sh"
  exit 1
fi

if [ ! -d "$BASE" ]; then
  echo "ERRO: instalação TwitchPi não encontrada em $BASE"
  exit 1
fi

echo "A instalar update TwitchPi..."

cp -f update/server.py "$BASE/server.py"
mkdir -p "$BASE/web"
cp -f update/web/index.html "$BASE/web/index.html"
cp -f update/web/app.js "$BASE/web/app.js"
cp -f update/web/style.css "$BASE/web/style.css"
chmod 755 "$BASE/server.py"

systemctl daemon-reload
systemctl restart twitch-pi.service

echo
echo "========================================"
echo " TwitchPi - UPDATE INSTALADO COM SUCESSO"
echo "========================================"
echo
systemctl --no-pager --full status twitch-pi.service
