#!/usr/bin/env bash
# Runs on the Google Cloud server (started by deploy.sh): installs Docker once, then builds and
# starts Pakkam and Caddy. Safe to run again after uploading a new bundle.
#   bash vm-setup.sh <site-name>
set -euo pipefail
SITE="$1"
cd "$(dirname "$0")"
chmod 600 pakkam.env

if ! command -v docker >/dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sudo sh /tmp/get-docker.sh
fi

echo "Building Pakkam (the first time downloads PyTorch and both models: 10-20 minutes)..."
sudo SITE="$SITE" docker compose up -d --build

echo "Waiting for the models to load..."
for _ in $(seq 1 60); do
  if sudo docker compose exec -T pakkam python -c \
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=4)" \
      >/dev/null 2>&1; then
    echo "Pakkam is up: https://$SITE/chat/"
    exit 0
  fi
  sleep 10
done
echo "Pakkam did not answer within 10 minutes. Logs:  sudo docker compose -f ~/pakkam/compose.yaml logs --tail 80 pakkam"
exit 1
