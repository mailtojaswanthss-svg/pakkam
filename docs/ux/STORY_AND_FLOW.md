# Step 3: Pakkam's story and home page flow

Date: 26 Oct 2026. This is a plan. No code has changed.

Inputs: `UI_AUDIT.md`, `REFERENCES.md`, Jaswanth's rules from 26 Oct, and the weakness review (`STEP1_VERIFY.md`).

**Labels used below**
- **UNVERIFIED**: I could not check this fact against the repo text or the PDF. Do not publish it until it is checked.
- **(build after voice works end to end)**: depends on the voice thread's mic, STT, TTS and live test.
- **Tamil (needs native review)**: every Tamil line here is my draft.

---

## 0. Fact check for everything this page would show

**How I checked:** against the repo. That means `data/sources.json`, `docs/data_sources.md`, `docs/results.md`, and the page text extracted from each PDF in `docs/review/questions-review.csv`. The PDFs themselves are not in the repo, and this container cannot download them. So "verified" here means **verified in the repo's extracted text**.
- English text comes from the PDF text layer.
- Tamil and Hindi text is often OCR, which is known to misread numbers (a 1 can become a 4).

Before publishing, open each source page once and look at it with your own eyes. That step is not done.

| Fact | Status | Where it is |
|---|---|---|
| PM-KISAN: Rs.6,000 a year | **Verified** | Operational guidelines (English), p2: "an amount of Rs.6000/- per year". e-KYC note (English), p1: "Rs 6,000/- per year in three equal instalments" |
| PM-KISAN: Rs.2,000 each instalment, "page 10" | **UNVERIFIED** | The p10 text in the repo does not show it. Use "three equal instalments, e-KYC note p1" instead |
| Pudhumai Penn: Rs.1,000 a month | **Verified in English only** | SWWE policy note 2024-25 (English), p7: "Rs.1000/- per month to their bank account". Higher Education policy note (English), p6. The **Tamil** OCR text reads 4,000 (`report.md` §4). Never show this fact from a Tamil source |
| Atal Pension Yojana: join between 18 and 40 | **Verified** | APY brochure (English), p1: "If you are between 18 and 40 years of age" |
| Atal Pension Yojana: Rs.1,000 to Rs.5,000 a month after 60 | **UNVERIFIED** | The English p1 text in the repo does not show it. The Hindi OCR reads "रु.000" |
| Magalir Urimai: Rs.1,000 a month, Rs.12,000 a year, page 9 | **UNVERIFIED** | The Tamil pages are OCR, and the repo excerpt of p9 does not show the amount. The live test answered "Rs.12,000 a year" (`report.md` §8), but that is not a check against the page |
| Magalir Urimai G.O. is 43 pages (English pp 1-7, Tamil pp 8-43) | **Verified (repo metadata)** | `docs/data_sources.md`, row 1 |
| G.O.(Ms) No.15 dated 10 July 2023 | **Verified (repo metadata)** | `sources.json` (`doc_date` 2023-07-10), `data_sources.md` |
| Breakfast scheme: classes 1 to 5 in primary schools, G.O.(Ms) No.43 dated 27.07.2022, p1 | **Verified (Tamil OCR text)** | Repo text of p1: "1 முதல் 5-ஆம் வகுப்பு வரை பயிலும் மாணவ, மாணவியருக்கு", "அரசாணை (நிலை) எண்.43 நாள். 27.07.2022". It is OCR, so check the page by eye |
| 18 documents, 2,785 passages | **Verified** | `docs/results.md` |
| Per-language results | **Verified** | `docs/results.md`. Its header says the run was on "commit c050d23 (uncommitted changes)". Re-run on a clean commit before publishing |
| "Your question text is never logged" | **True, but incomplete** | `api/audit.py` stores only a hash. The voice clip goes to Gnani and the text goes to the LLM provider, so the copy must say so (see the call to action beat) |
| "Documents checked on <date>" | **Not used** | Not to be written until you confirm you did that check |

**Effect on the page**
- The **Magalir Urimai** amount (the forward story) stays as the *question* the page asks. Its *answer* is only shown once you have checked G.O. page 9.
- The demo proof uses a **verified** fact: PM-KISAN, or the breakfast scheme.
- The current home page shows two UNVERIFIED facts: Atal Pension ₹1,000-5,000 and Magalir Urimai "page 9, ₹12,000". These must be fixed or checked before the video. This is listed in Step 4.

---

## 1. The story

**One sentence**

> Pakkam lets you ask about a government scheme in your own language, by voice or text, and shows you the exact page of the official document behind every sentence, or says honestly that the documents don't cover it.

**Three lines (for the video and the post)**

> A forwarded message says there's money for you. Is it real?
> Ask Pakkam in Tamil, Hindi, English or Tanglish, and see the official page each answer comes from.
> When the documents don't say, Pakkam says so, and tells you where to ask.

Tanglish speech input is still untested (voice thread, `stt.py` maps Tanglish to ta-IN). Until it works, the video should *type* Tanglish, or show Tamil or English by voice.

---

## 2. Home page, beat by beat

Seven beats plus a footer, much shorter than today's page (about 5,800 px on a phone).
- **Target:** 4 to 5 phone screens.
- **Motion:** every beat uses only reveal-on-scroll (see section 4).
- **Order:** the hero carries the sample question, so a visitor feels the product before reading anything.

### Beat 0: Hero (carries "Ask by voice", build after voice works end to end)

| | English | Tamil (needs native review) |
|---|---|---|
| Badge | Student project · not a government service | மாணவர் திட்டம் · அரசு சேவை அல்ல |
| Headline | Somewhere in a government order, there is a line about you. | அரசாணையில் எங்கோ ஒரு வரி உங்களைப் பற்றி இருக்கிறது. |
| Supporting line | Ask in your own language. See the page your answer comes from. | உங்கள் மொழியில் கேளுங்கள். பதில் எந்தப் பக்கத்திலிருந்து வருகிறது என்று பாருங்கள். |
| Primary button | Ask by voice *(build after voice works end to end; until then: "Ask Pakkam")* | குரலில் கேளுங்கள் |
| Secondary | or type your question | அல்லது தட்டச்சு செய்யுங்கள் |

*(I kept the current headline. It is the strongest line on the site.)*

- **Visual:** the product, not a stock photo (Linear pattern). A real answer card sits under the buttons: the question, one cited sentence, and the page slip. The photo moves to the "who it's for" area or is dropped.
- **Interaction:** the tappable sample question (section 3).

**Phone layout (390 px)**
```
┌──────────────────────────────┐
│ ▣ Pakkam              [Ask]  │
│ ● Student project · not a    │
│   government service         │
│ Somewhere in a government    │
│ order, there is a line       │
│ about you.                   │
│ Ask in your own language.    │
│ See the page your answer     │
│ comes from.                  │
│ [ 🎙  Ask by voice         ] │  ← full width, 56 px tall
│   or type your question      │
│ ┌──────────────────────────┐ │
│ │ Try: முதலமைச்சரின் காலை    │ │  ← sample chip (tap)
│ │ உணவுத் திட்டம் எந்த       │ │
│ │ வகுப்பு மாணவர்களுக்கு? ▶  │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘  first screen ends here
```
- Fixed order: the badge, then the headline (3-4 lines at about 34 px), the supporting line, one full-width primary button, a text link, then the sample chip.
- The theme toggle moves out of the phone nav, leaving only the logo and "Ask".
- Desktop: the copy and buttons on the left, the answer card on the right.

### Beat 1: Problem, the forward

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | A message says there's money for you. Is it real? | உங்களுக்குப் பணம் கிடைக்கும் என்று ஒரு செய்தி வருகிறது. அது உண்மையா? |
| Supporting line | It doesn't say who qualifies, how much, or where the rule is written. | யாருக்குக் கிடைக்கும், எவ்வளவு, எந்த விதியில் உள்ளது என்று அது சொல்வதில்லை. |

- **Visual:** one chat-style bubble, labelled "Forwarded many times", reading "₹1,000 every month for women. Apply fast!".
- **Labelling:** under the bubble, in small text: "An example message, written for this page." It is a made-up forward, so say so.
- **Fallback:** if Magalir Urimai page 9 is not checked before the video, use a PM-KISAN forward instead ("₹6,000 a year for farmers. Apply fast!"). Its answer is verified.
- **Phone:** the bubble is full width, slightly tilted (2°, no animation), with the headline under it.

### Beat 2: Stakes

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | A wrong guess costs real money. | தவறான ஊகத்தால் உண்மையான பணம் இழக்கப்படுகிறது. |
| Supporting line | The rules sit in long official documents, often scanned, in formal language, rarely in the words people speak. | விதிகள் நீண்ட அரசு ஆவணங்களில் உள்ளன. பல ஸ்கேன் செய்யப்பட்டவை, அலுவல் மொழியில் உள்ளவை, மக்கள் பேசும் மொழியில் அல்ல. |

- **Visual:** one large number with its label: **43 pages**, "the government order behind that message: 7 in English, 36 in Tamil". This is verified from `data_sources.md` (pp 1-7 English, pp 8-43 Tamil).
- **What it must not do:** no claims about how many people miss out. There is no source for that.
- **Phone:** the number at about 56 px, the label under it, then two short lines of text.

### Beat 3: Turn, ask the way you speak

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | Just ask, the way you'd ask at home. | வீட்டில் கேட்பது போலவே கேளுங்கள். |
| Supporting line | Speak or type in Tamil, Hindi or English. Type in Tanglish. *(After the Tanglish voice test passes: "Speak or type in Tamil, Hindi, English or Tanglish.")* | தமிழ், இந்தி அல்லது ஆங்கிலத்தில் பேசுங்கள் அல்லது தட்டச்சு செய்யுங்கள். தங்கிலீஷில் தட்டச்சு செய்யுங்கள். |

- **Visual:** four language buttons that actually switch the interface language. These are real buttons, not decorative pills (audit problem 5).
- **Voice visual:** under them, a static drawing of the mic button with "Tap and speak" *(build after voice works end to end)*.
- **Phone:** the language buttons in a 2 × 2 grid, each at least 48 px tall.

### Beat 4: Proof, every sentence has a page

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | Every sentence shows its page. | ஒவ்வொரு வாக்கியத்துக்கும் அதன் பக்கம் உண்டு. |
| Supporting line | Tap the page to read the exact line in the official document. | பக்கத்தைத் தொட்டால், அதிகாரப்பூர்வ ஆவணத்தில் உள்ள அதே வரியைப் படிக்கலாம். |

- **Visual:** the answer and proof card, using **verified** content only:
  - Answer: PM-KISAN gives ₹6,000 a year in three equal instalments.
  - Slip: "PM-KISAN · e-KYC note (English) · page 1" and the quoted line "Rs 6,000/- per year in three equal instalments".
  - Link: "Open the official PDF at page 1".
  - Once Magalir Urimai page 9 is checked, this card can answer Beat 1's forward instead. That is the stronger story.
- **Card layout:** the slip shows exactly two facts, the amount and the page (Stripe pattern), plus the document date where `sources.json` has one. For PM-KISAN: "13 Nov 2023".
- **Interaction:** tap the "page 1" chip to expand the quoted line. Under reduced motion it simply appears.
- **Phone:** the card is full width. The page chip is a real button at least 44 px tall, labelled "page 1", not just "1".
- **Answer text:** this beat's answer must be copied from a real saved pipeline output, not written by hand.

### Beat 5: Honesty, "I don't know"

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | When the documents don't say, Pakkam says so. | ஆவணங்களில் இல்லையென்றால், Pakkam அதை நேரடியாகச் சொல்லும். |
| Supporting line | No guessing. You get the official place to ask instead. | ஊகம் இல்லை. எங்கே கேட்கலாம் என்ற அதிகாரப்பூர்வ இடத்தைக் காட்டும். |

- **Visual:** a refusal card in its own calm style, with no red. It shows:
  - the question "When is the next PM-KISAN instalment?" (q011, refused correctly in the live test, `report.md` §8)
  - the refusal text
  - a link to the official website
  - a small "What Pakkam can read" link that opens the list of 18 documents
- **Phone:** the card is full width. The link is a 44 px button.

### Beat 6: Numbers, measured not claimed

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | Measured, not claimed. | சொல்லவில்லை, அளந்து காட்டுகிறோம். |
| Supporting line | Results from our evaluation script, per language. Draft questions, not yet native-speaker verified. | எங்கள் மதிப்பீட்டுக் கருவியின் முடிவுகள், மொழி வாரியாக. கேள்விகள் வரைவு நிலையில் உள்ளன; தாய்மொழி பேசுபவர்கள் இன்னும் சரிபார்க்கவில்லை. |

**Visual:** a small table with one row per language, using counts as "n of N" (not percentages alone), from `docs/results.md`:

| | Right page in top 5 | Correctly said "I don't know" | Wrongly refused |
|---|---|---|---|
| Tamil | 38 of 38 | 9 of 10 | 3 of 38 |
| Hindi | 38 of 38 | 10 of 10 | 3 of 38 |
| English | 39 of 39 | 9 of 10 | 2 of 39 |
| Tanglish | 36 of 39 | 10 of 10 | 17 of 39 |

- **How the counts were derived:** from the percentages and the Ans/Unans counts in `results.md`, for example Tanglish false refusal 44% of 39 = 17. The site should not hand-type them. A small step in the evaluation script should write a JSON file, which the page reads. *(That is a Step 4 task.)*
- **The Tanglish row shows the weak number.** Hiding it would undercut the "measured, not claimed" promise.
- **Footnote:** "How we measured: 194 draft questions written by the author, retrieval-only run of `python -m schemebot.evaluation`, run date from `results.md`. Answer quality was checked on 8 questions only." The Apple and Pudding methodology patterns apply here.
- **Phone:** one row per language as a card with three lines. No wide table on phones.

### Beat 7: Call to action

| | English | Tamil (needs native review) |
|---|---|---|
| Headline | Try it with your own question. | உங்கள் சொந்தக் கேள்வியுடன் முயற்சி செய்யுங்கள். |
| Supporting line | Free, no sign-up. A student project, not a government service. Check the official source before you act. | இலவசம், பதிவு தேவையில்லை. இது மாணவர் திட்டம், அரசு சேவை அல்ல. செயல்படும் முன் அதிகாரப்பூர்வ ஆதாரத்தைச் சரிபார்க்கவும். |
| Privacy line | Pakkam doesn't store your question. To answer it, your voice goes to a speech service and your text to an AI service. | Pakkam உங்கள் கேள்வியைச் சேமிப்பதில்லை. பதில் தர, உங்கள் குரல் ஒரு பேச்சு சேவைக்கும், உரை ஒரு AI சேவைக்கும் அனுப்பப்படுகிறது. |
| Button | Ask by voice *(after voice works; until then "Ask Pakkam")* | குரலில் கேளுங்கள் |

- **Phone:** a full-width band with the button at full width.
- **Footer (unchanged in spirit):** the full disclaimer, photo credits, and a link to the list of documents. Nothing in it implies a link to any government body, Gnani or Sarvam. Voice credit: "Speech by Gnani's public APIs", only once voice is live, and nothing more.

---

## 3. The tappable sample question (near the top)

- **Where:** the last item on the first phone screen, in Beat 0.
- **What it shows:** "Try:" and a real question. Tapping ▶ shows a **saved real answer** inline, right under it: the answer sentence and its page chip.
- **Why a saved answer:** live answers took 13 to 52 s on the free tier (`report.md` §8). A live call in the hero would look broken.
- **Labelling:** the saved answer is marked "A saved answer from <run date>. Ask your own for a live one." Every word of it comes from a real pipeline output, saved as a JSON file in the repo, never retyped.

**Which question**
- **Tamil (default):** q019, "முதலமைச்சரின் காலை உணவுத் திட்டம் எந்த வகுப்பு மாணவர்களுக்கு?"
  - The fact (classes 1 to 5, G.O.(Ms) No.43, p1) is verified in the repo's OCR text.
  - It still needs one live run to capture the answer, and a look at the PDF page.
- **English alternative:** q004, "How much money does a farmer get every year under PM-KISAN?" The fact is verified, and it needs one live run.
- **Tanglish is not in the hero.** q040 ("PM kisan la varushathuku evlo panam kidaikum") was answered correctly in the 8-question live test. But that run has no saved output in the repo, and its label is still a draft. So the eval does not yet show it answered correctly. If you re-run it, save the output and confirm it, and it can become a second chip.

**Behaviour**
- **Tap:** the chip turns into the answer card. "Ask your own" focuses the voice or text entry.
- **Reduced motion:** the card simply appears.
- **No JavaScript:** the chip is a link to `/chat/?q=…`.

---

## 4. Motion and visual direction

**Motion: reveal-on-scroll only**
- Each beat fades in and rises 12 px once, when 20% of it is visible (IntersectionObserver), over 250 ms with ease-out.
- No parallax, scroll-jacking, looping animation or counters rolling up.
- **Reduced motion:** under `prefers-reduced-motion: reduce` everything is visible from the start, with no transitions. Content is visible by default, so the page still works if JavaScript fails or is late.

**Performance on cheap phones**
- No new libraries and no video.
- The hero has no image above the fold (the answer card is HTML).
- Photos stay WebP, lazy-loaded below the fold.
- Target under 300 KB for the first screen before fonts.

**Fonts**
- Keep Baloo 2 and Baloo Thambi 2 for headings, and Hind and Hind Madurai for body text. Add Hind for Devanagari (already in the family).
- Keep `display=swap`.
- Tamil and Devanagari use line-height 1.7 (already in `tokens.css`). Tamil headlines get about 10% smaller sizes than English, because Tamil words are longer and wrap badly at 34 px.

**Visual**
- Keep the ledger-paper background and stamp violet.
- The proof slip is the one place with a strong visual: a paper-like card with a violet page chip.
- Refusals use a calm neutral card with a dashed border, not red. Red is only for real errors.

**Accessibility**
- WCAG AA contrast and 44 px touch targets.
- Every interactive item is a real `<button>` or `<a>`.
- Server text is always inserted with `textContent`.
- Each beat is a `section` with a heading.

---

## 5. Tone guide

**The voice:** a helpful older cousin who works near the taluk office. Warm, plain, respectful. Never a brochure, never a government notice.

**Do**
- Use short sentences (under 15 words where possible) and everyday words. Say "money", not "financial assistance"; "who can get it", not "eligibility criteria".
- Say what Pakkam does and doesn't do: "Pakkam reads 18 documents. If yours isn't one, it will say so."
- Put the source and the limit next to the claim, not in the footer.
- Address the reader as "you". In Tamil use the respectful "நீங்கள்" forms. In Hindi use "आप".
- In Tamil, prefer spoken-standard words over formal ones (needs native review).

**Don't**
- Don't sell. No "revolutionary", "powerful", "instantly", "100% accurate", "trusted by".
- Don't sound official. No "Hon'ble", no seals, no tricolour, no "Government of…" phrasing, nothing that looks like a government portal.
- Don't invent people, quotes, user counts or results. Opinions are labelled as opinions.
- Don't blame people for not knowing ("simply", "just read the order").
- Don't promise outcomes. Never write "you will get". Write "the document says".
