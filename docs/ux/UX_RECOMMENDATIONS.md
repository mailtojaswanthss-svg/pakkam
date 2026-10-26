# Step 4: UX recommendations

Date: 26 Oct 2026. This is a plan. No code has changed. Building waits for Jaswanth's go-ahead.

Inputs: `UI_AUDIT.md`, `REFERENCES.md`, `STORY_AND_FLOW.md`, the weakness review (`STEP1_VERIFY.md`), Jaswanth's submission checklist, and the voice branch `claude/project-thread-fpld2g` (read at 0b898fc).

**Rules this plan follows**
- **Build scope** is audit #1, #3, #6, #9 and a better refusal screen, about 10 hours.
- **Mic and composer** belong to the voice thread. Here they appear only as notes for that thread (section 6).
- **Facts:** Magalir Urimai 12,000 / page 9, Atal Pension 1,000-5,000 and PM-KISAN page 10 stay **UNVERIFIED** and appear on no hero or demo list until Jaswanth confirms them from the PDFs.
- **Language:** every Tamil string is marked **needs native review**.

---

## 1. Main problems from the audit (and what is in scope)

| # | Problem | In build scope? |
|---|---|---|
| 1 | Voice is missing from the story and the screen | **Yes.** Home page parts here. Mic and composer go to the voice thread as notes |
| 2 | Interface text is English only | Partly. Only the key Tamil strings in section 7, and they ride on the tasks below |
| 3 | The proof (the source page) reads like a footnote | **Yes** |
| 4 | Phone visitors read long before they feel the product | Only the hero sample card (T7). The full page rewrite is cut |
| 5 | No language choice; the pills look tappable | Voice thread (its "I will speak in" picker) |
| 6 | The waiting state hides real latency | **Yes** |
| 7 | "I don't know" leaves people stuck | **Yes** (the better refusal screen) |
| 8 | Errors lose the question and offer no retry | Rides on #6 (keep the question, Retry button) |
| 9 | Disclaimer hidden on phones | **Yes** |
| 10 | Small phone and accessibility issues | Only the sources-sheet backdrop (rides on #3) |

**Already found in Step 3:** the live home page shows two UNVERIFIED facts:
- the hero slip "page 9, ஆண்டுக்கு 12 ஆயிரம் ரூபாய்" (also in the `home.js` Tamil demo)
- the Atal Pension "₹1,000 to ₹5,000 a month after 60" card

Task T0 removes them.

---

## 2. Ranked improvements

The ranking is by impact on the 60-second video and on a first-time phone user. Effort: S is under 1 hour, M is 1-3 hours, L is over 3 hours. "Hours" are my estimates, not measured.

| Rank | What | Why | Effort | Fixes | Owner |
|---|---|---|---|---|---|
| 1 | **T0. Remove UNVERIFIED facts from the site.** Drop the hero "page 9 / 12 ஆயிரம்" slip and the Tamil Magalir Urimai demo tab. Drop the Atal Pension amount and keep only "join between 18 and 40" (verified, brochure p1). Label every remaining hand-written demo answer "Example answer". | Every number on screen must be checkable, and judges may open the PDF | S (0.5 h) | Step 3 fact check | This thread |
| 2 | **T1. Proof you can see.** The citation chip shows "p. 9" (the page number) instead of "1". Under each answer, an always-visible source line: "From: G.O.(Ms) No.15 · page 9 · 10 Jul 2023". Tapping it opens the slip with the quoted line and "Open the official PDF at page N". The phone sheet gets a backdrop and a drag-handle bar. | Pakkam's whole difference has to be visible in a 2-second glance in the video | M (3.5 h) | #3, #10 | This thread |
| 3 | **T2. Honest waiting state.** Show an elapsed timer ("Working on it · 0:08"). After 15 s add "This is taking longer than usual. The free answer service can be slow." Add a Cancel button (AbortController). On failure, put the question back in the box and show a Retry button. No fake step-by-step progress, because the server does not report stages. | Real waits are 13-52 s (`report.md` §8); a silent bar looks frozen | M (2.5 h) | #6, #8 | This thread (chat.js shared with voice; see section 4) |
| 4 | **T3. Better "I don't know".** A calm card with a dashed border, no red and no "Answered in". The refusal text, then the scheme's **official website as a real link** when one is known, then a "What Pakkam can read" button that opens the scheme list. | The honest refusal is the trust moment; today it is a dead end | M (2 h, including a small API field) | #7 | This thread |
| 5 | **T4. Disclaimer on phones.** Show the composer hint at 640 px and below as one short line: "Information only, not official advice. Check the official source." Add the same line, in English, under the hero buttons. | It has to be on screen in every frame of the video | S (0.5 h) | #9 | This thread |
| 6 | **T5. Home hero for voice** *(build after voice works end to end)*. The primary button becomes "Ask by voice" and opens `/chat/` with the mic ready. The secondary is "or type your question". | The video's first 5 seconds must say "speak" | S (1 h) | #1 | This thread, after voice is live |
| 7 | **T6. Mic and composer spec** (notes only, section 6). A large mic, the one-line pre-prompt shown once, the recording timer, cancel, "didn't catch that", and playing the answer with Stop. | The voice screen is what judges see most | none here | #1, #5 | Voice thread |
| 8 | **T7. Hero sample answer card.** One question chip with an answer card (see section 3 for which answer). | Visitors feel the product before reading | S (1 h) | #4 | This thread |
| 9 | Key Tamil interface strings (section 7), wired in only where T1-T4 already touch the text | Non-English users can follow the key moments | S (rides on T1-T4) | #2 | This thread, plus a Tamil reviewer |
| 10 | Full home page rewrite to the 7 beats in STORY_AND_FLOW.md | The story arc | L (6-8 h) | #4 | **Cut**, later |
| 11 | Full interface translation (Tamil, Hindi, Tanglish) with a language switch | Users not comfortable in English | L | #2 | **Cut**, later |
| 12 | Per-language results read from a JSON file the evaluation script writes | No hand-typed numbers | M | Step 3 | **Cut**; for now copy exactly from a clean `results.md` re-run |

**Build total in this thread:** T0 0.5 + T1 3.5 + T2 2.5 + T3 2 + T4 0.5 + T5 1 + T7 1 = **about 11 hours**. That is just over the 10-hour budget, so the cut list (section 5) applies from the start: T7 waits until the hero answer has been captured from a real run.

---

## 3. The home page sample answer: which it is

- **Today:** there is **no real saved answer** in the repo. The `home.js` demo answers are hand-written from the documents. So until a real one is captured, the hero card and the demo are labelled **"Example answer"**.
- **Plan:** replace it with a **real saved answer and its source page**:
  1. Run the real pipeline once on q019 ("முதலமைச்சரின் காலை உணவுத் திட்டம் எந்த வகுப்பு மாணவர்களுக்கு?"). Its fact, classes 1 to 5 per G.O.(Ms) No.43 page 1, is verified in the repo's OCR text. Or run q004 (PM-KISAN ₹6,000 a year), which is verified in the English text layer.
  2. Save the full JSON response in the repo, with the run date.
  3. Jaswanth opens that PDF page once and confirms it.
  4. Then the label becomes **"Saved answer from <date>, source: <document>, page N"**.

  Section 3 of STORY_AND_FLOW.md said the same, with a slightly different label.
- **Never on a hero or demo list until Jaswanth confirms them:** Magalir Urimai 12,000 / page 9, Atal Pension 1,000-5,000, PM-KISAN page 10.
- **No Tanglish sample** until a saved run shows that exact question answered correctly.

---

## 4. Demo-ready subset (2-3 days, two people)

The teammate's skills are **UNKNOWN**. The teammate's tasks below need no coding. Where a task could be code or non-code, it is marked "either, if HTML/CSS skills are confirmed".

The voice thread owns `web/assets/chat.js`, `chat.css` and `web/chat/index.html` changes for the mic and composer. To avoid conflicts, T1-T4 start **after the voice branch is merged into main** (or are built on top of it), and touch only the rendering and refusal code, not the composer.

### Day 1
| Person | Task | Hours |
|---|---|---|
| Jaswanth | T0 remove UNVERIFIED facts; T4 disclaimer on phones | 1 |
| Jaswanth | T1 proof you can see (chip label, source line, phone backdrop) | 3.5 |
| Teammate | Open every source page used on the site or in the demo questions and confirm or correct each number (starting with the three UNVERIFIED ones). Write the result in `docs/review/`. | 2-3 |
| Teammate | Native review of the Tamil strings in section 7 and in STORY_AND_FLOW.md (UNKNOWN whether the teammate reads Tamil; if not, find a reviewer) | 1-2 |

### Day 2
| Person | Task | Hours |
|---|---|---|
| Jaswanth | T2 honest waiting state (timer, slow note, cancel, keep question, retry) | 2.5 |
| Jaswanth | T3 better refusal (API `contact` field plus test, card, scheme list button) | 2 |
| Teammate | Write the video script (60 s) from the three-line story; pick 3 demo questions whose facts were confirmed on Day 1 (one Tamil, one English or Hindi, one refusal) | 2 |
| Teammate | **English subtitles** for every Tamil, Hindi and Tanglish line in the video (draft them from the script, then fix the timing after recording) | 2 |

### Day 3 (only if voice works end to end by then)
| Person | Task | Hours |
|---|---|---|
| Jaswanth | T5 hero "Ask by voice"; T7 hero card, once a real answer is saved | 2 |
| Jaswanth | Run the existing tests, ruff and mypy; check 390 px and desktop screenshots against the audit | 1 |
| Teammate | 3-person check: each person does one spoken question, finds the source page, reacts to a refusal. Note where they hesitate (either person, no code) | 1.5 |
| Both | Record the fallback demo, then the 60-second video with subtitles | 2 |

**Done means:**
- The mic is visible (voice thread).
- Every answer shows its page without a tap.
- The wait shows a timer and never looks frozen.
- The disclaimer is on every phone screen.
- The refusal links the official site.
- No UNVERIFIED number is anywhere on the site or in the video.

---

## 5. Cut list (in the order Jaswanth set)

If time runs short, cut in this order:
1. **#9, T4** disclaimer on phones. **Fallback:** the per-answer disclaimer already shows after each answer. Make sure the video shows one answer.
2. **#6, T2** honest waiting state. **Fallback:** edit the video to skip the wait, and say "the wait is cut" in the subtitles. Don't hide that the wait exists.
3. **T7** hero sample card. The hero stays as is, minus the T0 facts.
4. **T5** hero "Ask by voice". The hero stays "Ask Pakkam" until voice is live.
5. **T3's scheme list button.** Keep the official link.

**Never cut:** T0 (unverified facts) and T1 (visible proof), since these carry the honesty story. Also never cut the English subtitles.

**Already cut (later, after the deadline):** the full 7-beat home page, the full interface translation, generated results JSON, public hosting, and the dark-mode toggle changes.

---

## 6. Notes for the voice thread (mic and composer; not built here)

I'm sending these to the "Add Gnani voice to Pakkam" thread. The voice branch already has a mic icon button, an upload button, an "I will speak in" picker, a 30 s auto-stop with a text timer, and a mic-blocked message. These notes are about how they look and behave for the video.

1. **A big mic, first.** On phones, show the mic as the main control: a round button at least 64 px, centred above the text box, with the label "Tap and speak" under it. The text box and upload stay below as "or type". On desktop it can stay inline.
2. **The language picker comes before the mic.** Show it as four buttons (தமிழ் / हिन्दी / English / Tanglish) rather than a select. Mark Tanglish "(being tested)" until the clip test says it works.
3. **Mic pre-prompt: once only, one line.** On the first mic tap, before the browser prompt, show: "Pakkam needs your microphone to hear your question. [Allow] [Type instead]". Remember it in `localStorage` (wrapped in try/catch) so it never shows again. Tamil string in section 7.
4. **Permission denied.** Use the Permissions API to detect "denied". Then the mic becomes "Mic is off. Type instead, or turn on the microphone in your browser settings", with "type instead" focusing the box. Don't show the pre-prompt again.
5. **Recording state.** Show a red dot, a big running timer "0:07 / 0:30", and the button turning into a square Stop. Add a Cancel (✕) next to it that discards the clip. Show a gentle "5 seconds left" at 0:25.
   - The brief said 60 s, but the voice branch caps clips at **30 s** (`SCHEMEBOT_STT_MAX_SECONDS`), because Gnani's docs say both 30 and 60. The timer must show the server's cap, so 30.
6. **After Stop.** Show "Sending your voice…", then "Pakkam heard: <transcript>" as soon as it is known.
   - Today `/ask/voice` returns the transcript only together with the answer. Returning it first (a separate STT call, or streaming) would let the user see it 13-50 s sooner. That is the voice thread's call.
7. **"Didn't catch that."** On an empty or very short transcript, or STT "nothing heard", show "Pakkam didn't catch that. Try again, a little closer to the phone." with the mic ready again. Don't send an empty question to `/ask`.
8. **Slow network.** If the upload takes over 5 s, show "Slow connection, still sending…". On failure, keep the recording in memory and offer "Send again", so the user doesn't have to speak again.
9. **Playing the answer (after TTS exists).** A fixed slim bar shows "Playing answer" with Stop (and Play again after it ends). It never autoplays without the user having tapped the mic in that turn. It stops when a new question starts.
10. **Accessibility.** The mic is a real `<button>` with `aria-pressed`. The timer is announced at most every 10 s (polite). The recording can be started and stopped with the keyboard (Space/Enter). All status text is inserted with `textContent`.

---

## 7. Key Tamil interface strings (all **needs native review**)

These are the first ones only: the mic label, recording state, errors and refusal. They are my drafts.

| Key | English | Tamil (needs native review) |
|---|---|---|
| micLabel | Tap and speak | தொட்டுப் பேசுங்கள் |
| micStop | Stop and send | நிறுத்தி அனுப்புங்கள் |
| prePrompt | Pakkam needs your microphone to hear your question. | உங்கள் கேள்வியைக் கேட்க Pakkam-க்கு மைக் அனுமதி தேவை. |
| allow / typeInstead | Allow / Type instead | அனுமதி / தட்டச்சு செய்யுங்கள் |
| recording | Recording 0:07 of 0:30 | பதிவாகிறது 0:07 / 0:30 |
| timeAlmostUp | 5 seconds left | இன்னும் 5 விநாடிகள் |
| sending | Sending your voice… | உங்கள் குரல் அனுப்பப்படுகிறது… |
| heard | Pakkam heard: | Pakkam கேட்டது: |
| didntCatch | Pakkam didn't catch that. Try again, a little closer to the phone. | Pakkam-க்குச் சரியாகக் கேட்கவில்லை. போனுக்கு அருகில் வைத்து மீண்டும் பேசுங்கள். |
| micDenied | Mic is off. Type instead, or turn on the microphone in your browser settings. | மைக் அணைக்கப்பட்டுள்ளது. தட்டச்சு செய்யுங்கள், அல்லது உலாவி அமைப்பில் மைக்கை இயக்குங்கள். |
| working | Working on it · 0:08 | பதில் தயாராகிறது · 0:08 |
| slow | This is taking longer than usual. | வழக்கத்தைவிட நேரம் ஆகிறது. |
| cancel / retry | Cancel / Try again | ரத்து / மீண்டும் முயலுங்கள் |
| network | Pakkam could not reach the server. Check your connection and try again. | சர்வரை அடைய முடியவில்லை. இணைப்பைச் சரிபார்த்து மீண்டும் முயலுங்கள். |
| refusalTitle | Not in the documents Pakkam has | Pakkam-இடம் உள்ள ஆவணங்களில் இது இல்லை |
| officialLink | Ask on the official website | அதிகாரப்பூர்வ இணையதளத்தில் கேளுங்கள் |
| whatICanRead | What Pakkam can read | Pakkam படிக்கக்கூடியவை |
| sourceLine | From: <document> · page N | ஆதாரம்: <ஆவணம்> · பக்கம் N |
| disclaimerShort | Information only, not official advice. Check the official source. | தகவலுக்கு மட்டும்; அதிகாரப்பூர்வ ஆலோசனை அல்ல. அதிகாரப்பூர்வ ஆதாரத்தைச் சரிபார்க்கவும். |

**Which language the interface uses:** the voice picker's language when set, otherwise the answer's language. English stays the fallback.

---

## 8. Wireframe: the ideal phone voice chat screen (390 px)

Three states of the same screen. All facts shown are verified (see STORY_AND_FLOW.md §0). The answer text is a placeholder for a real saved output.

```
A. Ready                          B. Recording                      C. Answer with proof
┌────────────────────────────┐   ┌────────────────────────────┐   ┌────────────────────────────┐
│ ☰   ▣ Pakkam            +  │   │ ☰   ▣ Pakkam            +  │   │ ☰   ▣ Pakkam            +  │
├────────────────────────────┤   ├────────────────────────────┤   ├────────────────────────────┤
│ I will speak in:           │   │                            │   │        ┌─────────────────┐ │
│ [தமிழ்][हिन्दी][English]    │   │                            │   │        │Pakkam heard:    │ │
│ [Tanglish (being tested)]  │   │                            │   │        │PM kisan la evlo │ │
│                            │   │          ● 0:07 / 0:30     │   │        │panam kidaikum   │ │
│  Try: How much money does  │   │                            │   │        └─────────────────┘ │
│  a farmer get under        │   │        ┌──────────┐        │   │ ▣ PM-KISAN gives ₹6,000 a  │
│  PM-KISAN?             ▶   │   │        │    ■     │  ✕     │   │   year in three equal      │
│                            │   │        │  (stop)  │ cancel │   │   instalments. [p. 1]      │
│                            │   │        └──────────┘        │   │   ┌──────────────────────┐ │
│                            │   │     Stop and send          │   │   │From: e-KYC note (EN) │ │
│         ┌──────────┐       │   │                            │   │   │· page 1 · 13 Nov 2023│ │
│         │    🎙    │       │   │                            │   │   │"Rs 6,000/- per year  │ │
│         └──────────┘       │   │                            │   │   │in three equal        │ │
│       Tap and speak        │   │                            │   │   │instalments" ▸ Open PDF│ │
│ ┌────────────────────────┐ │   │                            │   │   └──────────────────────┘ │
│ │ or type your question ⏎│ │   │                            │   │ ┌────────────────────────┐ │
│ └────────────────────────┘ │   │                            │   │ │▶ Playing answer  ■ Stop│ │
│ Information only, not      │   │ Information only, not      │   │ └────────────────────────┘ │
│ official advice. Check the │   │ official advice. Check the │   │ Information only, not      │
│ official source.           │   │ official source.           │   │ official advice. Check the │
└────────────────────────────┘   └────────────────────────────┘   │ official source.           │
                                                                   └────────────────────────────┘
```
The "Playing answer" bar in C needs TTS, which is not built yet. Its absence breaks nothing.

```
D. Waiting (honest)               E. Refusal ("I don't know")       F. Didn't catch / mic off
┌────────────────────────────┐   ┌────────────────────────────┐   ┌────────────────────────────┐
│        ┌─────────────────┐ │   │        ┌─────────────────┐ │   │                            │
│        │Pakkam heard:    │ │   │        │When is the next │ │   │ ┌────────────────────────┐ │
│        │…                │ │   │        │PM-KISAN         │ │   │ │Pakkam didn't catch     │ │
│        └─────────────────┘ │   │        │instalment?      │ │   │ │that. Try again, a      │ │
│ ▣ Working on it · 0:18     │   │        └─────────────────┘ │   │ │little closer to the    │ │
│   ━━━━━━━━━━━━━━━━━━━━━    │   │ ▣ ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │   │ │phone.  [🎙 Try again]  │ │
│   This is taking longer    │   │   Not in the documents     │   │ └────────────────────────┘ │
│   than usual. The free     │   │   Pakkam has               │   │                            │
│   answer service can be    │   │   I couldn't find this in  │   │ ┌────────────────────────┐ │
│   slow.                    │   │   the official scheme      │   │ │Mic is off. Type        │ │
│   [Cancel]                 │   │   documents I have…        │   │ │instead, or turn on the │ │
│                            │   │   [Ask on the official     │   │ │microphone in your      │ │
│                            │   │    website ↗ pmkisan.gov.in]│   │ │browser settings.       │ │
│                            │   │   [What Pakkam can read]   │   │ │[Type instead]          │ │
│                            │   │ └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │   │ └────────────────────────┘ │
└────────────────────────────┘   └────────────────────────────┘   └────────────────────────────┘
```

**Wireframe notes**
- **State A, sample chip:** uses English q004, because its fact is verified. A Tamil chip (q019) can replace it after the saved run (section 3). Tanglish is shown only in the picker, marked "(being tested)".
- **State C, transcript bubble:** it is Tanglish because it shows what a user might say; it is not a promise that this question works. For the video, use a question from the Day 1 confirmed list.
- **State E, refusal:** q011 was refused correctly in the live test (`report.md` §8). pmkisan.gov.in comes from `data/contacts.json`.
- **Every state:** the disclaimer line stays on screen.

---

## 9. Voice details (summary for the voice thread)

| Situation | Behaviour |
|---|---|
| First mic tap | The one-line pre-prompt, shown once (§6.3) |
| Permission denied | The "Mic is off…" card with Type instead (§6.4) |
| Recording | Red dot, a visible timer counting to the **server cap (30 s today)**, Stop and Cancel. Auto-stop and send at the cap (§6.5) |
| Slow network | "Slow connection, still sending…" after 5 s. Keep the clip and offer "Send again" (§6.8) |
| Nothing heard | "Pakkam didn't catch that. Try again…" with the mic ready (§6.7) |
| Answer playback | A fixed "Playing answer" bar with Stop. No autoplay without a tap. Stops on a new question (§6.9) |
| Daily Gnani cap reached | The existing 503 message ("you can still type") shown in the voice area, with Type instead focused |

---

## 10. What I need from you

1. **Go-ahead to build T0-T4** in this thread, after the voice branch merges or on top of it. Which of those two?
2. **Confirm the three UNVERIFIED facts** from the PDFs whenever you can (Day 1 teammate task).
3. **Teammate skills:** can they do HTML and CSS? Do they read Tamil? Both are UNKNOWN. The split above assumes no to both.
