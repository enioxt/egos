#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
SERVICE_NAME="oracle-instance-launcher.service"
TARGET="/etc/systemd/system/$SERVICE_NAME"
TMP_FILE="$(mktemp)"

sed "s|__PROJECT_ROOT__|$ROOT|g" "$ROOT/$SERVICE_NAME" > "$TMP_FILE"
sudo mv "$TMP_FILE" "$TARGET"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo "Installed $SERVICE_NAME at $TARGET"
echo "Start with: sudo systemctl start $SERVICE_NAME"
