# Deploying Pakkam on Google Cloud Run

This puts the whole app (home page, chat, API) on a public `https://…run.app` address, running
on one NVIDIA L4 GPU that scales to zero when nobody is using it.

**What is in the image.** The code, the web pages, PyTorch with CUDA, both models (bge-m3
and the reranker) and the search index with the source list and contacts. About 13 GB. The
API key is not in it; Cloud Run reads it from Secret Manager at start.

**What it costs.** GPU services are billed for every second an instance runs (CPU, memory and
the L4), with no per-request fee. With the defaults (`MIN_INSTANCES=0`, `MAX_INSTANCES=1`)
nothing is billed while idle, and at most one GPU runs at a time. Check current prices on the
[Cloud Run pricing page](https://cloud.google.com/run/pricing) before deploying, and set a
budget alert in Billing. Cloud Build and Artifact Registry storage (about 13 GB per image
kept) cost a little extra.

**The trade-off of scaling to zero.** The first question after a quiet spell waits for an
instance to start and load both models: about a minute. Open the site a couple of minutes
before a demo, or deploy with `MIN_INSTANCES=1` for the length of the demo (then it is billed
all the time).

## 1. One-time setup

You need a Google Cloud project with billing turned on, and the
[gcloud CLI](https://cloud.google.com/sdk/docs/install) (or use Cloud Shell in the browser,
which has it). Run these in Git Bash or Cloud Shell, from the project root.

```bash
gcloud auth login
export PROJECT_ID=your-project-id          # from the Cloud Console project picker
gcloud config set project "$PROJECT_ID"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com
```

**The API key, as a secret.** Use a paid key: Gemini's free tier allows about 20 requests a
day per model, and Google may use free-tier prompts to improve its products. Create the
secret by pasting the key when asked, so it never lands in your shell history:

```bash
read -rsp "Paste the Gemini API key, then press Enter: " KEY; echo
printf '%s' "$KEY" | gcloud secrets create pakkam-gemini-key --data-file=-
unset KEY
```

For Claude instead, name it `pakkam-claude-key` and deploy with `LLM_PROVIDER=claude`.

**Let Cloud Run read the secret.** Cloud Run runs as the project's default compute service
account:

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format 'value(projectNumber)')
gcloud secrets add-iam-policy-binding pakkam-gemini-key \
  --member "serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role roles/secretmanager.secretAccessor
```

**GPU quota.** Each project gets a small automatic L4 quota per region on its first GPU
deployment; one instance is all this needs. If the deploy reports a quota error, request an
increase for Cloud Run L4 GPUs (without zonal redundancy) in IAM & Admin → Quotas.

## 2. Deploy

The index must exist locally (`data/index/`), since it is copied into the image. Then:

```bash
PROJECT_ID=your-project-id ./deploy/cloudrun/deploy.sh
```

The script:
1. creates the Artifact Registry repository `pakkam` (first run only);
2. uploads the project (about 25 MB; `.gcloudignore` keeps out raw PDFs, logs and `.env`)
   and builds the `cloudrun` image in Cloud Build: 20-40 minutes the first time;
3. deploys the service with 1 L4 GPU, 8 CPUs, 32 GiB of memory, a health check that waits for
   the models to load, and the API key from Secret Manager;
4. prints the address.

Settings you can change on the command line:

| Variable | Default | Meaning |
|---|---|---|
| `REGION` | `asia-southeast1` (Singapore) | Where it runs. L4 is also offered in Mumbai (`asia-south1`), by invitation only |
| `LLM_PROVIDER` | `gemini` | `gemini` or `claude` |
| `SECRET` | `pakkam-<provider>-key` | The Secret Manager secret holding the key |
| `MIN_INSTANCES` | `0` | `1` keeps it warm (billed all the time) |
| `MAX_INSTANCES` | `1` | More instances means more GPUs and more cost |
| `SERVICE`, `REPOSITORY` | `pakkam` | Names of the service and image repository |

## 3. Check it

```bash
URL=$(gcloud run services describe pakkam --region asia-southeast1 --format 'value(status.url)')
curl "$URL/health"                         # {"status":"ok"} once the models are loaded
curl -X POST "$URL/ask" -H "Content-Type: application/json" \
  -d '{"question": "What is the age limit to join Atal Pension Yojana?"}'
```

Then open `$URL/chat/` in a browser. Logs are under Cloud Run → pakkam → Logs. The audit log
the app writes inside the container is lost when an instance stops; use Cloud Logging for a
lasting record.

## 4. Update, pause, remove

- **New version:** commit, then run `deploy.sh` again; Cloud Run switches to the new revision
  once its health check passes.
- **Pause:** `gcloud run services update pakkam --region asia-southeast1 --max-instances 0`
  stops it serving (and billing) without deleting it.
- **Remove everything:**

  ```bash
  gcloud run services delete pakkam --region asia-southeast1
  gcloud artifacts repositories delete pakkam --location asia-southeast1
  gcloud secrets delete pakkam-gemini-key
  ```

## Notes

- **Rate limits** (10 questions a minute per visitor, 500 a day in total) are kept in memory
  per instance, which is exact with one instance.
- **Visitor addresses.** The image trusts `X-Forwarded-For` because only Google's front end can
  reach a Cloud Run container; the rate limit needs the real address.
- **If the build fails on `--region`** (regional Cloud Build not available for this machine
  type in your region), remove the `--region` line from the `gcloud builds submit` call.
- **This has not been deployed yet.** The script, Cloud Build file and Dockerfile target are
  written against current `gcloud` documentation but have not been run; expect to fix small
  things on the first deploy.
