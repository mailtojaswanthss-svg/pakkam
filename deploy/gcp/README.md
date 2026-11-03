# Pakkam on Google Cloud (free trial)

One 8-core server in Mumbai (`e2-standard-8`, 32 GB, no GPU) runs the Pakkam backend behind
Caddy, which gives it a fixed HTTPS address (`https://<ip-with-dashes>.sslip.io`) with a free
certificate. The website on Vercel forwards its API paths there. The new-account free trial's
$300 credit covers about six weeks of this machine; check prices in the console.

## 1. One-time: Google Cloud account

1. Sign up at https://cloud.google.com/free (a card is needed to verify; the trial does not
   charge it unless you upgrade).
2. In the console, create a project (top bar, project picker, **New project**), e.g. `pakkam`.

## 2. On the laptop: pack Pakkam

In the project folder:

```powershell
git pull origin main
uv run --extra ingest --extra index --extra generate --extra gemini --extra api python deploy/gcp/bundle.py
```

This writes `pakkam-gcp.zip` (about 150 MB) with your `.env` settings and API keys inside.
Keep it private: upload it only to your own Cloud Shell. It is in `.gitignore`.

## 3. In Cloud Shell: create the server

1. Open https://console.cloud.google.com, select the project, click the **Cloud Shell** icon
   (`>_`, top right).
2. In Cloud Shell's menu (three dots), **Upload**, and pick `pakkam-gcp.zip`.
3. Run:

   ```bash
   gcloud config set project <your-project-id>
   unzip -oq pakkam-gcp.zip && bash pakkam/deploy.sh
   ```

   Answer `y` if asked to enable an API or authorise Cloud Shell. The first run takes 20-30
   minutes (server, Docker, PyTorch, both models). It ends with:

   ```
   Send this address to Claude: https://34-xx-xx-xx.sslip.io
   ```

If the machine type is refused for quota, run `MACHINE=e2-standard-4 bash pakkam/deploy.sh`.

## Updating

Repeat steps 2 and 3 (upload the new zip, then `unzip -oq pakkam-gcp.zip && bash pakkam/deploy.sh`):
it copies the new bundle and rebuilds; the server and its address stay the same.

## Looking at the server

```bash
gcloud compute ssh pakkam --zone asia-south1-a
sudo docker compose -f ~/pakkam/compose.yaml logs --tail 80 pakkam
```

To stop paying from the credit after judging: `gcloud compute instances stop pakkam --zone asia-south1-a`
(and `gcloud compute addresses delete pakkam-ip --region asia-south1` to release the address).
