# Pakkam web UI audit (Step 1)

Date: 26 Oct 2026. Branch `claude/project-thread-i98lxh` at commit 35ba419. No code was changed.

## How I tested

- I ran the real FastAPI app (`create_app`), which serves the real `web/` folder, at 390 x 844 (phone, touch) and 1440 x 900 (desktop) in Chromium.
- This container has no built index and no LLM key, so `/ask` was answered by a **stub**. It waits 2.5 s, then either returns the Tamil example answer already used on the home page (G.O.(Ms) No.15, page 9) or a refusal built from the real refusal and disclaimer texts in `messages.py`. A network error was forced by blocking `/ask`. The layouts are real. The answer content is not a live model answer.
- Fonts: Baloo 2, Baloo Thambi 2, Hind and Hind Madurai all loaded. Tamil and Devanagari render correctly.
- Screenshots are in `audit-shots/`: `phone-` and `desktop-` versions of `home-top`, `home-full`, `chat-welcome`, `chat-loading`, `chat-answer`, `chat-sources`, `chat-refusal`, `chat-error`, plus `phone-chat-menu`.

## What already works (keep it)

- A calm, warm visual identity: ledger-paper background, violet accent, rounded Indian type. Nothing looks like a stock AI landing page.
- All server text goes in with `textContent`. Enter never sends during Tamil or Hindi IME composition.
- Reduced motion is respected. The theme follows the system setting. Focus moves to the sources panel and back.
- Citation chips get a larger invisible tap area on touch screens.
- The honesty pieces exist: refusals, the disclaimer, "Measured, not claimed", and the photo credits.
- The results numbers match `docs/results.md`. 151 of 154 is 98% recall@5, 18 documents and 2,785 passages.

## Top 10 UX problems, by impact on the demo and on real users

**1. Voice is missing from the story and from the screen.** The home page says "Ask in Tamil, Hindi, English or Tanglish" but never "speak". The chat composer has only a text box and a send arrow, and there is no place for a mic in the layout (`phone-chat-welcome.png`). For a voice challenge, the first 5 seconds of the video show a typing product. *(The voice thread is adding the mic and `/ask/voice`. This audit covers how it should sit, not building it.)*

**2. All the interface text is in English only.** The welcome headline, placeholder, loading line, errors, "1 source", "Open the official PDF at page 9", the menu, and the whole home page are English. Only the answer and disclaimer follow the user's language (`phone-chat-refusal.png`). A user who is not comfortable in English can get an answer but cannot find their way to it.

**3. The proof, which is Pakkam's main difference, reads like a footnote.** The citation is a small "1" chip after the sentence, and a separate "1 source" pill does the same job. Nothing says "this came from page 9 of the government order" until you tap. In the sources sheet the title wraps to "page / 9" and the quoted passage ends in "…" (`phone-chat-sources.png`). Non-technical users will not know the chip is tappable, and judges watching a 60-second video will not see the proof.

**4. On a phone, visitors read for a long time before they feel the product.** The hero copy and buttons fill the first screen. The forward-and-answer picture starts below the fold, and the live demo is about 2.5 screens down. There is no tappable sample question near the top. The full page is about 5,800 px tall (about 7 screens), and the forwarded message appears twice (hero and story tile) (`phone-home-full.png`).

**5. There is no language choice, and the language chips look tappable but are not.** The language is detected silently. Voice input needs a language chosen before recording, and a wrong guess shows as a wrong transcript. Meanwhile the four pill chips in the hero and the menu look like buttons but do nothing.

**6. The waiting state does not reflect real latency.** It shows one fixed English line and an indeterminate bar (`phone-chat-loading.png`). It has no "this is taking longer than usual" after a few seconds, no cancel, and no sign of which stage is running. With STT, retrieval, the LLM and TTS together, real waits will be much longer than the 2.5 s stub, and a silent bar on a slow phone looks frozen.

**7. The "I don't know" answer is honest but leaves people stuck.** It says to check "the scheme's official website" without naming or linking it, and it does not list what Pakkam *does* cover. It sits in a grey quote-style box that looks similar to an answer, and it shows "Answered in 2.5 s", which reads oddly on a refusal (`phone-chat-refusal.png`). This is the moment that builds trust, and it is underplayed.

**8. Errors lose the question and offer no retry.** On a network failure the input is already cleared, there is no "Try again" button, and the message is English only (`phone-chat-error.png`). For voice this will be worse: re-recording is more effort than re-typing.

**9. The disclaimer is hidden on phones until after the first answer.** `.composer-hint` is set to `display: none` below 640 px, so the "information, not official advice" line is missing on the screen most users and the video will show. It only appears under answers and inside the menu.

**10. Smaller phone and accessibility issues.**
- The sources bottom sheet has no backdrop or drag handle. It covers the composer and looks like part of the page.
- `aria-live="polite"` on the whole conversation log makes screen readers read each full answer plus its meta and disclaimer, with no short "Answer ready" cue.
- The suggestion cards push the composer to the very bottom edge of the phone screen. Four of the six cards show at 390 px.
- On the home page the dark-mode toggle takes nav space on phones, beside the main call to action.

## A risk that is not a UI problem but will show in the demo

Tanglish has a **44% false-refusal rate** in `docs/results.md` (draft questions, retrieval-only run). A Tanglish voice question in the video has close to a coin-flip chance of being refused. Pick demo questions that the eval shows are answered, or fix this first (the report suggests transliterating Tanglish to Tamil script before reranking).

## Notes for the next steps

- The voice thread ("Add Gnani voice to Pakkam") owns the mic button, `/ask/voice` and the language picker. Steps 3 and 4 will specify how they should look and behave so the two threads don't build the same thing twice.
- Every number on the site already traces to `docs/results.md`. Keep it that way, and label them "draft questions, not yet native-speaker verified" (the current footnote says "draft" but not who has checked them).
