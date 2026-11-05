#!/usr/bin/env bash
# Run in Google Cloud Shell, next to pakkam-gcp.zip (see deploy/gcp/README.md):
#   unzip -oq pakkam-gcp.zip && bash pakkam/deploy.sh
# Creates (once) a fixed address, a firewall rule for HTTPS and the server, copies Pakkam to it
# and starts it. Running it again only uploads and restarts. Settings can be changed with
# environment variables, e.g. MACHINE=e2-standard-4 bash pakkam/deploy.sh
set -euo pipefail

NAME=${NAME:-pakkam}
ZONE=${ZONE:-asia-south1-a}          # Mumbai
REGION=${ZONE%-*}
MACHINE=${MACHINE:-e2-standard-8}    # 8 cores, 32 GB
HERE="$(cd "$(dirname "$0")" && pwd)"

PROJECT=$(gcloud config get-value project 2>/dev/null || true)
if [ -z "$PROJECT" ]; then
  echo "No project selected. Run: gcloud config set project <your-project-id>" >&2
  exit 1
fi
echo "Project $PROJECT, zone $ZONE, machine $MACHINE"

gcloud services enable compute.googleapis.com

if ! gcloud compute addresses describe "$NAME-ip" --region "$REGION" >/dev/null 2>&1; then
  gcloud compute addresses create "$NAME-ip" --region "$REGION"
fi
IP=$(gcloud compute addresses describe "$NAME-ip" --region "$REGION" --format='value(address)')
SITE="${IP//./-}.sslip.io"

if ! gcloud compute firewall-rules describe "$NAME-web" >/dev/null 2>&1; then
  gcloud compute firewall-rules create "$NAME-web" --allow tcp:80,tcp:443 --target-tags "$NAME"
fi

if ! gcloud compute instances describe "$NAME" --zone "$ZONE" >/dev/null 2>&1; then
  gcloud compute instances create "$NAME" --zone "$ZONE" --machine-type "$MACHINE" \
    --image-family debian-12 --image-project debian-cloud \
    --boot-disk-size 50GB --boot-disk-type pd-balanced \
    --address "$IP" --tags "$NAME"
  echo "Waiting for the server to boot..."
  sleep 40
fi

echo "Copying Pakkam to the server..."
for attempt in 1 2 3 4 5; do
  if gcloud compute scp --zone "$ZONE" --recurse --quiet "$HERE" "$NAME":~/ ; then break; fi
  [ "$attempt" = 5 ] && { echo "Could not copy to the server." >&2; exit 1; }
  sleep 15
done

gcloud compute ssh "$NAME" --zone "$ZONE" --quiet --command "bash ~/pakkam/vm-setup.sh $SITE"

echo
echo "Pakkam:  https://$SITE/"
echo "Send this address to Claude: https://$SITE"
