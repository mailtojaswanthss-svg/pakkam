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

This free Space runs on CPU, so the first question after a quiet spell waits a minute or two
while the models load, and answers take several seconds.

Settings (Space → Settings → Variables and secrets):

- secret `SCHEMEBOT_GEMINI_API_KEY`: the Gemini API key (or `SCHEMEBOT_ANTHROPIC_API_KEY`)
- variable `SCHEMEBOT_LLM_PROVIDER`: `gemini` or `claude`
