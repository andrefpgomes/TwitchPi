#!/bin/bash
set -euo pipefail

REPO="https://github.com/andrefpgomes/TwitchPi.git"
BASE="/opt/twitch-pi"
SERVICE="twitch-pi.service"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute: sudo bash install.sh"
  exit 1
fi

echo "== TwitchPi: instalação/atualização pelo GitHub =="

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3

if ! command -v chromium >/dev/null 2>&1 && ! command -v chromium-browser >/dev/null 2>&1; then
  echo "Chromium não encontrado. A instalar..."
  apt-get install -y chromium || true
fi

mkdir -p "$BASE"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --depth 1 "$REPO" "$TMP/repo"

# Preserva dados locais: config.env, state.json e perfil Chromium.
cp -f "$TMP/repo/server.py" "$BASE/server.py"
mkdir -p "$BASE/web"
cp -f "$TMP/repo/web/index.html" "$BASE/web/index.html"
cp -f "$TMP/repo/web/app.js" "$BASE/web/app.js"
cp -f "$TMP/repo/web/style.css" "$BASE/web/style.css"

if [ ! -f "$BASE/state.json" ]; then
  printf '{"channel":"","status":"stopped","favorites":[]}' > "$BASE/state.json"
fi

cat > "/etc/systemd/system/$SERVICE" <<EOF
[Unit]
Description=TwitchPi Web Controller
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$BASE
Environment=PORT=8765
Environment=STATE_FILE=$BASE/state.json
Environment=TWITCH_PROFILE=/root/.config/twitch-pi-chromium
ExecStart=/usr/bin/python3 $BASE/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

chmod 755 "$BASE/server.py"
systemctl daemon-reload
systemctl enable --now "$SERVICE"

sleep 1
systemctl --no-pager --full status "$SERVICE" || true

echo
echo "TwitchPi instalado/atualizado em $BASE"
echo "Interface: http://$(hostname -I | awk '{print $1}'):8765"
