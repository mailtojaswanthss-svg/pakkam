# Step 2: reference study

Date: 26 Oct 2026. These are patterns only. Pakkam copies no layouts, copy, images, branding or code from these sites.

Most of the effort goes into three screens:
- **(H)** the home hero
- **(V)** the voice chat screen
- **(P)** the answer and proof card

## How this was gathered, and what was blocked

- Every page was read through a text fetch on 26 Oct 2026. The notes below describe only what those fetches returned. Where a page did not render or was blocked, I say so and do not guess.
- **No reference screenshots.** This container's network blocks those sites for the browser, so I could not take phone-width captures. The descriptions come from page text, not visual inspection. Where a note concerns visual layout, it is limited to what the text shows.
- **Blocked or unreadable:**
  - Mobbin: `/glossary` and `/explore` both failed to load, and the screen library appears to need an account.
  - Bhashini: robots.txt disallows fetching.
  - Apple HIG Privacy and Material 3: these pages need JavaScript, so only their metadata came back.
- **Substitute for Mobbin:** the public web.dev guide on permission prompts. It covers the one mobile pattern Pakkam needs most, which is asking for the mic.

## The 9 references

### 1. Sarvam AI (sarvam.ai)
- **Opening and close:** the hero opens on a positioning line ("AI for all from India") with Sign up and Contact Us, then a strip of 15 partner logos. The hero has no live demo.
- **Proof:** metrics such as "<100ms" median latency, each linked to a Trust Center. Language coverage is given per capability (TTS in 11 languages, STT in 12, translation in 23).
- **Ending:** a single-button closing band.

**Patterns**
1. **Every claim links to its evidence (P).** Each Sarvam number links to the page that backs it. Pakkam can do the same at sentence level: a result number links to `docs/results.md`, and an answer sentence links to its page. This fits Pakkam because "trust me" is exactly what its users have been burned by.
2. **Coverage stated per capability (V, H).** Sarvam lists voice-in, voice-out and translation languages separately. Pakkam should do the same honestly. Voice input may cover fewer languages than text: Tanglish is mapped to ta-IN and still untested in the voice thread. Say so next to the mic rather than in the fine print.
3. **What to avoid, a lesson rather than a pattern (H).** A hero with no product in it makes the visitor take the claim on faith. Pakkam's hero should show a real question and a real cited answer instead.

### 2. Gnani AI (gnani.ai and /resources/timbre-v3)
- **Opening:** the home hero is a brand line ("The Frontier AI Company") with "Book a Demo".
- **Try it:** the home page offers a "Talk to Our Voice Agent" form (pick a use case, give a phone number, get a call). The Timbre v3.0 page has a "Hear Timbre v3.0 / Tap the orb to hear it." control, a "Now playing" bar, voice cards ("Thirteen voices. Press any one."), and a code-switch "Play sample".
- **Partly rendered:** several Timbre page controls came back as unrendered template placeholders, so their exact behaviour is unknown.
- **Proof:** metrics, logos and named testimonials. The fetched copy is inconsistent in places: "sub 200ms" vs "<150 ms", and "250+" vs "200+" enterprises.

**Patterns**
1. **One big tap target that says what will happen (V).** "Tap the orb to hear it." is a single, obvious action with its instruction right beside it. For Pakkam: one large mic button with a plain label under it in the chosen language ("Tap and speak").
2. **A persistent "now playing" strip (P).** Playback state lives in one fixed place, not inside each item. For Pakkam: when the spoken answer plays, a slim bar shows "Playing answer" with a Stop button, so the user can always stop it.
3. **Mixed-language samples are featured, not hidden (H, V).** Code-switching gets its own sample. Tanglish is code-switching, so Pakkam's sample questions should include one spoken Tanglish example, but only after the 44% Tanglish false-refusal rate is checked for that question.
- **Caution:** the inconsistent numbers on the fetched pages show why every Pakkam number must come from one re-runnable source. Pakkam must not state anything about Gnani beyond "voice by Gnani's APIs".

### 3. Mobile patterns (Mobbin was blocked, so web.dev permission guidance stands in)
- **Gathered:** the web.dev permissions best-practices article, plus general patterns from voice chat products. I could not see Mobbin screens, so nothing here is claimed to come from Mobbin.

**Patterns**
1. **Ask for the mic only after the user taps the mic, with a short explanation first (V).** web.dev: "Ask for permission after a user interaction." and "Only when users react affirmatively to such a pre-prompt should you trigger the browser's permission prompt." For Pakkam: the first mic tap shows one line ("Pakkam needs your microphone to hear your question. Nothing is recorded until you tap.") with Allow and Type instead. The browser prompt comes only after that.
2. **A denied mic is a guide, not a dead end (V).** web.dev: "detect that they blocked access using the Permissions API and offer a guide on how to change their settings." For Pakkam: if access is blocked, the mic turns into a "Type instead" path plus a two-step "turn the mic back on" hint for Chrome on Android.
3. **The recording state is unmistakable (V).** This is a general pattern, not from a specific source. While recording: a red dot, a running timer, the button changes to Stop, and a cancel option. Pakkam needs this because users must know when they are being heard.

### 4. Linear (linear.app), storytelling
- **Opening:** the hero has a short headline and subhead, with a product UI mockup (sidebar, an issue, an activity feed) directly under it.
- **Body:** each later section pairs one capability with one mockup: intake, planning, agents, review.
- **Proof:** named customer quotes and a changelog.
- **Ending:** "Built for the future. Available today." with four CTAs.

**Patterns**
1. **The product itself is the hero image (H).** Pakkam's hero should show a real chat card (a question, a cited sentence, a "page 9" slip) instead of a stock photo with floating labels. The person in the photo can stay further down.
2. **One section, one claim, one picture (H, story).** Each beat in STORY_AND_FLOW.md gets one sentence of claim and one visual, no more.
3. **"Recent changes" as proof of a living project (results).** A dated "what changed" list is honest proof for a student project: "26 Oct: voice input added". It shows progress without inventing user numbers.

### 5. Stripe (stripe.com), storytelling and proof
- **Opening:** a one-line value headline. A legal qualifier ("Stripe is not a bank…") sits right below it, not in the footer.
- **Proof:** a "backbone" band of four large stats with exact labels, then case studies with two concrete numbers each.
- **Ending:** "Ready to get started?" with two CTAs.

**Patterns**
1. **The qualifier sits next to the claim, in the hero (H).** Stripe puts its "not a bank" line in the hero. Pakkam should put "Independent student project. Not a government service. Check the official source." in the hero and in the chat itself, not only in the footer.
2. **Stat tiles with exact labels, few of them (results).** Four numbers with plain labels. Pakkam's per-language results can follow this, with each tile labelled "draft questions, not yet native-speaker verified".
3. **A two-number example card (P).** Each Stripe case shows exactly two concrete facts. A Pakkam proof card can do the same: the amount and the page ("₹12,000 a year · page 9 of G.O.(Ms) No.15").

### 6. Apple product page (apple.com/airpods-pro), storytelling
- **Opening:** the product name, then one bold claim ("The world's best in-ear Active Noise Cancellation."), a short subhead with a footnote marker, and one Buy button.
- **Body:** short sentence-case headings that end in periods, and big numeric callouts.
- **Qualifiers:** "Up to", "compared with", and numbered footnotes that name test methods and dates.

**Patterns**
1. **Footnote markers on claims, with the method at the end (H, results).** This fits Pakkam well. A result number carries a small marker that leads to "how this was measured: 194 draft questions, retrieval-only run, 26 Oct 2026".
2. **Short headings that end in a period (tone).** "It checks, or it stops." Pakkam already does this; keep it.
3. **One action in the hero (H).** Apple shows one button. Pakkam currently shows two buttons plus four pills. Make it one primary action, "Ask by voice", and one text link.

### 7. The Pudding ("Sizing chaos", pudding.cool/2026/02/womens-sizing), scroll-driven and editorial
- **Opening:** a headline, then "meet your typical tween": a composite character introduced before any data.
- **Body:** each lowercase chapter heading makes one claim, then one chart proves it. A concrete object (a dress form, a size chart) carries the argument. Sources are linked inline, and there is a Methodology section with dates and caveats.
- **Ending:** the conclusion ends on a question ("…why can't we make them better?"), followed by methodology.

**Patterns**
1. **Start with one person and one object, not statistics (H, story).** For Pakkam the object is the forwarded WhatsApp message. The reader meets it first, then learns what the real document says.
2. **Claim, then proof, step by step (story).** Each scroll step reveals one piece: the forward, the 43-page order, the line on page 9. Use simple reveal-on-scroll, with no animation when reduced motion is on.
3. **Methodology as a real section with dates and caveats (results).** Pakkam's results section ends with "How we measured" (script name, run date, draft status). This makes "Measured, not claimed" concrete.

### 8. myScheme (myscheme.gov.in), Indian government service
- **Opening:** the hero is "Find schemes based on categories" with Categories, States/UTs and Ministries tabs.
- **How a citizen starts:** a three-step "Enter Details / Search / Select & Apply" flow.
- **Language:** a "Change language" icon in the header.
- **Missing:** the fetched page mentions no chatbot or voice.
- **Ending:** "Last Updated On" and a version number in the footer.

**Patterns**
1. **"Last updated" shown openly (P, results).** A date on the data tells people how fresh it is. Pakkam's proof card can show the document date ("G.O. dated 10 July 2023"), which is already in `sources.json`, and the site can show "documents checked on 25 Oct 2026".
2. **A three-step "how it works" (H).** Pakkam already has this. Keep it short and put it below the demo, not above it.
3. **The gap is the point (H).** myScheme asks you to browse categories and fill details. Pakkam's difference is "just ask, in your words, by voice". Say this without naming or criticising any government site, and without implying any link to one.

### 9. Kisan e-Mitra (PM-KISAN chatbot, as described by Wadhwani AI), Indian voice and government chatbot
- **What the article says:** it is on the PM-KISAN website and app. Farmers can type, tap an FAQ, or use voice "in their preferred language", across 11 languages.
- **How it answers:** intent detection, then retrieval, then an LLM, with templates. The most common questions are surfaced as clickable FAQs.
- **Not described:** the article does not say whether answers are spoken back or how escalation works.

**Patterns**
1. **Three ways in, side by side: speak, type, or tap a common question (V).** This matches Pakkam's users. The voice screen should offer the mic first, a text box second, and two or three tappable common questions in the chosen language.
2. **Frequent questions come from real usage (V).** Pakkam has no usage data and must not invent any. So the sample questions should come from the eval set questions that the script shows are answered correctly, and be labelled as examples.
3. **Language picked first (V).** "Preferred language" comes first. Pakkam's voice screen should start with a language picker (தமிழ் / हिन्दी / English / Tanglish) that also switches the interface text.

## What this means for the three screens

**(H) Home hero**
- Show the product itself: a real question and a cited answer card. *(Linear, Sarvam lesson)*
- One primary action, "Ask by voice", plus one sample question visitors can tap and play right there. *(Apple, Gnani)*
- The disclaimer sits in the hero. *(Stripe)*
- Open with the forwarded message as the story's object. *(Pudding)*

**(V) Voice chat screen**
- Language first, which also switches the interface. *(Kisan e-Mitra)*
- One big mic with its instruction under it. *(Gnani)*
- A pre-prompt before the browser asks for the mic, and a denied-mic guide. *(web.dev)*
- A clear recording state with a timer.
- Speak, type or tap, side by side. *(Kisan e-Mitra)*

**(P) Answer and proof card**
- Each sentence links to its page. *(Sarvam)*
- Two concrete facts on the slip: the amount and the page. *(Stripe)*
- The document date. *(myScheme)*
- A fixed "Playing answer / Stop" strip. *(Gnani)*

Steps 3 and 4 will turn these into STORY_AND_FLOW.md and UX_RECOMMENDATIONS.md. Anything touching the composer or mic code will be written as a spec for the voice thread, not built here.

## Sources (fetched 26 Oct 2026)
- [sarvam.ai](https://www.sarvam.ai/)
- [gnani.ai](https://www.gnani.ai/)
- [gnani.ai/resources/timbre-v3](https://www.gnani.ai/resources/timbre-v3)
- [mobbin.com](https://mobbin.com/) (home only; glossary and explore failed)
- [web.dev permissions best practices](https://web.dev/articles/permissions-best-practices)
- [linear.app](https://linear.app/)
- [stripe.com](https://stripe.com/)
- [apple.com/airpods-pro](https://www.apple.com/airpods-pro/)
- [pudding.cool "Sizing chaos"](https://pudding.cool/2026/02/womens-sizing)
- [myscheme.gov.in](https://www.myscheme.gov.in/)
- [Wadhwani AI on Kisan e-Mitra](https://www.wadhwaniai.org/empowering-millions-of-indian-farmers-with-instant-ai-chatbot-support/)
- Blocked: [bhashini.gov.in](https://bhashini.gov.in/) (robots); Apple HIG and Material 3 (JavaScript-only)
