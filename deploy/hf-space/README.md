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

This free Space runs Pakkam's answer server on 2 CPU cores and 16 GB RAM. The website
(pakkam-alpha.vercel.app) forwards its questions here. Answers take from a few seconds up to a
minute on CPU; signed fact-card answers and repeated questions are instant. A Space that has
had no visitors for 48 hours sleeps and wakes on the next visit.

Settings are copied from the laptop's `.env` by `deploy/hf-space/push.py`: API keys as Space
secrets, everything else as variables.
