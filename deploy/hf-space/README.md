---
title: Pakkam
emoji: 📄
colorFrom: purple
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Scheme answers in Tamil, Hindi, English or Tanglish, cited
---

# Pakkam

Ask about Indian government schemes in Tamil, Hindi, English or Tanglish. Every answer shows
the official document and page it comes from, and Pakkam says so when the documents do not
cover a question. The chat is at `/chat/`.

An independent student project, not an official service and not affiliated with any
government body. Answers are informational only: check the official source before you act.
Your question text is not stored by the app.

This free Space is Pakkam's **backup** answer server. The site (pakkam-alpha.vercel.app)
normally answers from a laptop with a GPU; when that is offline, the chat page sends questions
here instead (`web/assets/backup.js`). It runs on 2 CPU cores, so answers take up to a minute;
signed fact-card answers and repeated questions are instant.

Settings are copied from the laptop's `.env` by `deploy/hf-space/push.py`: API keys as Space
secrets, everything else as variables.
