#!/bin/bash
set -euo pipefail

REPO="https://github.com/andrefpgomes/TwitchPi.git"
BASE="/opt/twitch-pi"
SERVICE="twitch-pi.service"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute: sudo bash update-from-github.sh"
  exit 1
fi

[ -d "$BASE" ] || { echo "ERRO: TwitchPi não está instalado em $BASE. Use install.sh."; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "A procurar a versão mais recente no GitHub..."
git clone --depth 1 "$REPO" "$TMP/repo"

# Faz backup apenas dos ficheiros da aplicação antes da substituição.
BACKUP="$BASE/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp -a "$BASE/server.py" "$BACKUP/server.py" 2>/dev/null || true
cp -a "$BASE/web" "$BACKUP/web" 2>/dev/null || true

cp -f "$TMP/repo/server.py" "$BASE/server.py"
mkdir -p "$BASE/web"
cp -f "$TMP/repo/web/index.html" "$BASE/web/index.html"
cp -f "$TMP/repo/web/app.js" "$BASE/web/app.js"
cp -f "$TMP/repo/web/style.css" "$BASE/web/style.css"

# Atualiza também a unidade systemd, caso tenha mudado no repositório.
if [ -f "$TMP/repo/twitch-pi.service" ]; then
  cp -f "$TMP/repo/twitch-pi.service" "/etc/systemd/system/$SERVICE"
fi

chmod 755 "$BASE/server.py"
systemctl daemon-reload
systemctl enable "$SERVICE" >/dev/null 2>&1 || true
systemctl restart "$SERVICE"

echo
echo "========================================"
echo " TwitchPi atualizado pelo GitHub"
echo "========================================"
echo "Backup: $BACKUP"
echo
systemctl --no-pager --full status "$SERVICE"
