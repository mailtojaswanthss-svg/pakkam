#!/usr/bin/env bash
# Builds Pakkam's Cloud Run image in Cloud Build and deploys it on an NVIDIA L4 GPU.
#
#   PROJECT_ID=my-project ./deploy/cloudrun/deploy.sh
#
# Run it from the project root, after the one-time setup in deploy/cloudrun/README.md
# (billing, APIs, the API-key secret). Everything else is an environment variable with a
# default below. Re-running it deploys a new revision of the same service.
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID to your Google Cloud project ID}"
REGION="${REGION:-asia-southeast1}"        # L4 GPUs without an invitation; see README
SERVICE="${SERVICE:-pakkam}"
REPOSITORY="${REPOSITORY:-pakkam}"
LLM_PROVIDER="${LLM_PROVIDER:-gemini}"     # gemini or claude
SECRET="${SECRET:-pakkam-${LLM_PROVIDER}-key}"
MAX_INSTANCES="${MAX_INSTANCES:-1}"        # each instance is one GPU, billed while it runs
MIN_INSTANCES="${MIN_INSTANCES:-0}"        # 0 scales to zero: nothing billed while idle

case "$LLM_PROVIDER" in
  gemini) KEY_VAR=SCHEMEBOT_GEMINI_API_KEY ;;
  claude) KEY_VAR=SCHEMEBOT_ANTHROPIC_API_KEY ;;
  *) echo "LLM_PROVIDER must be gemini or claude, not '$LLM_PROVIDER'" >&2; exit 1 ;;
esac

for file in data/index/meta.json data/sources.json data/contacts.json Dockerfile; do
  if [ ! -e "$file" ]; then
    echo "Missing $file. Run this from the project root after building the index" \
         "(uv run python -m schemebot.index)." >&2
    exit 1
  fi
done

TAG="$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:${TAG}"

echo "==> Artifact Registry repository ${REPOSITORY} in ${REGION}"
if ! gcloud artifacts repositories describe "$REPOSITORY" \
      --project "$PROJECT_ID" --location "$REGION" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPOSITORY" \
    --project "$PROJECT_ID" --location "$REGION" --repository-format docker \
    --description "Pakkam container images"
fi

echo "==> Building ${IMAGE} in Cloud Build (20-40 minutes the first time)"
gcloud builds submit . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --config deploy/cloudrun/cloudbuild.yaml \
  --substitutions "_IMAGE=${IMAGE}"

echo "==> Deploying ${SERVICE} to Cloud Run"
# --no-cpu-throttling: GPU services use instance-based billing.
# --concurrency 4: requests queue on one GPU anyway (the app serialises model use).
# Startup probe: loading both models takes about a minute; allow up to ~4.
gcloud run deploy "$SERVICE" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "$IMAGE" \
  --port 8000 \
  --cpu 8 \
  --memory 32Gi \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --no-gpu-zonal-redundancy \
  --no-cpu-throttling \
  --concurrency 4 \
  --min-instances "$MIN_INSTANCES" \
  --max-instances "$MAX_INSTANCES" \
  --timeout 300 \
  --startup-probe "httpGet.path=/health,httpGet.port=8000,initialDelaySeconds=20,periodSeconds=10,timeoutSeconds=5,failureThreshold=22" \
  --set-env-vars "SCHEMEBOT_LLM_PROVIDER=${LLM_PROVIDER}" \
  --set-secrets "${KEY_VAR}=${SECRET}:latest" \
  --allow-unauthenticated

URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$REGION" \
        --format 'value(status.url)')"
echo
echo "Deployed: ${URL}  (chat at ${URL}/chat/)"
echo "Check:    curl ${URL}/health"
