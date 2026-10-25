# Pakkam: design package

> **Superseded in part by [frontend-plan.md](frontend-plan.md) (v2):** the site is now a home
> page (`/`) plus a chat app (`/chat/`), with Baloo + Hind type and Unsplash photos. The
> premise, palette roles, story facts and copy rules below still apply.

The single source for the web UI. Every viewer-facing line below ships verbatim.

## 1. Premise

**Pakkam** is Tamil for *page*. Government schemes live in long official documents; people
ask in their own language. Pakkam answers in that language and every answer shows the page
it came from. If the documents don't say, it says so and points to the official contact.
The page number is the product: the signature element, the interactive moment and the copy
all serve it.

Pakkam is an independent student project. It never imitates an official site: no
government emblem, no tricolour, no seals that read as authority.

## 2. Palette

Drawn from Indian office paperwork: ruled ledger paper, carbon-ink text, rubber-stamp violet.

```css
:root{
  --canvas:#EBEFE6;        /* ledger paper, a pale green-grey; never pure white */
  --panel:#F7F9F3;         /* raised paper: the chat sheet, slips */
  --rule:#C9D2C2;          /* ruled lines, dividers (decorative only) */
  --border:#7D8A78;        /* interactive borders, 3:1 on canvas */
  --ink:#1A2230;           /* primary text, carbon blue-black */
  --ink-2:#465063;         /* secondary text */
  --stamp:#5A36A3;         /* accent: send button, citation chips, focus */
  --stamp-hover:#47288A;
  --stamp-muted:rgba(90,54,163,.14); /* chip fill, highlight wash */
  --tape:#9E2F3A;          /* errors only */
}
```

Contrast, computed (WCAG): `--ink` on `--canvas` 13.7:1, `--ink-2` on `--canvas` 7.0:1,
`--stamp` on `--panel` 7.95:1, white on `--stamp` 8.4:1, `--tape` on `--panel` 6.8:1,
`--border` on `--canvas` 3.1:1 (interactive borders need 3:1).

## 3. Type

One family across three scripts, so Tamil, Hindi and English read as one voice: **Anek**
by Ek Type (Anek Latin, Anek Tamil, Anek Devanagari; variable width and weight).

- Display: Anek Latin 700, width 112 (wide) for the wordmark and the intro headline.
- Body and UI: Anek Latin / Tamil / Devanagari 400 and 600, width 100.
- Page references use tabular figures (`font-variant-numeric: tabular-nums`), no monospace.

Body lines stay under 70 characters; Tamil and Devanagari get line-height 1.75 (their
vowel signs need the room), Latin 1.55.

## 4. Layout

```
┌────────────────────────────────────────────────────────────┐
│ Pakkam                              About · Sources        │  nav
├────────────────────────────────────────────────────────────┤
│  Ask about a government scheme   │  [page illustration:    │  intro
│  in your own words.              │   ruled sheet, one line │
│  sub + language line             │   highlighted, a line   │
│                                  │   drawn to an answer]   │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────── chat sheet (ruled paper) ─────────────┐ │  chat
│  │ example questions (4 scripts)                          │ │
│  │ Q bubble (right)                                       │ │
│  │ Answer (left), citation chips [1] [2]                  │ │
│  │   └─ source slip unfolds: scheme · doc · page · text   │ │
│  │ [ question input ......................... ] [Ask]    │ │
│  └────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  How an answer is made (3 numbered steps: a real sequence) │
├────────────────────────────────────────────────────────────┤
│  What the documents cover (scheme list from /sources)      │
├────────────────────────────────────────────────────────────┤
│  footer: disclaimer, not affiliated, source list           │
└────────────────────────────────────────────────────────────┘
```

Left-aligned text throughout. On phones the illustration drops below the headline at
reduced height and the chat sheet goes full width.

## 5. Signature element and the one interactive moment

**The source slip.** Each answer sentence ends in stamp chips (`1`, `2`). Tapping a chip
unfolds a slip under the answer, like a page pulled from a file: scheme name, document,
page, the cited passage (scrollable), and a link to the official PDF. The chip and the slip
share the stamp violet; the matching sentence gets a soft violet wash while its slip is
open. Keyboard: chips are buttons, `Esc` closes the slip.

## 6. Motion

One orchestrated load moment, then only motion that answers the visitor:

- Intro illustration: the ruled sheet's highlighted line draws in, then a connector line
  draws from it to an answer card (SVG stroke-dashoffset, ~1.4 s, once).
- The input's placeholder types a sample question in Tamil, then Hindi, English and
  Tanglish, cycling while the input is empty and unfocused; stops on focus.
- Chat: new messages ease in (opacity + 8px rise, 220 ms); the slip unfolds by height and
  opacity (240 ms). While waiting: "Reading the documents" with a slow pulsing rule.
- Reduced motion: no typing cycle (a static placeholder), illustration drawn, instant slips.

Easing tokens: `--ease-out: cubic-bezier(.22,.8,.24,1)`, `--ease-in-out: cubic-bezier(.65,0,.35,1)`.

## 7. Copy (verbatim)

- `<title>`: Pakkam: scheme answers with the page they come from
- Nav: **Pakkam** · About · Sources
- Intro headline: Ask about a government scheme in your own words.
- Intro sub: Tamil, Hindi, English or Tanglish. Every answer shows the official document
  and page it comes from. If the documents don't say, Pakkam tells you.
- Intro language row: four file-folder tabs on one shelf line: தமிழ் / हिन्दी / English /
  Tanglish (a list, not a middle-dot string)
- Chat empty state: Try one of these, or type your own question.
- Example questions: மகளிர் உரிமைத் தொகை பெற யார் தகுதியானவர்? / पीएम किसान में साल में कितना
  पैसा मिलता है? / What is the age limit for Atal Pension Yojana? / ujjwala gas connection
  ku enna documents venum
- Input label (visually hidden): Your question
- Placeholder cycle: the four example questions, typed a whole letter at a time; with
  reduced motion or while focused, the English example as a static placeholder
- Send button: Ask
- Waiting: Reading the documents
- Answer footer: chip tooltip "Show the source"; slip link "Open the official PDF" (opens
  the PDF at the cited page); slip button "Close"
- Slip header: {scheme}, page {n} (or "pages {a} to {b}"), then "{document title}
  ({language})"
- Document list while loading: Loading the document list
- Document list failure: The document list could not load. Each answer still links its own
  source.
- Refusal: the backend's localized text, shown as is (it already names the contact).
- Validation (too short): Type at least 3 characters.
- Validation (too long): Keep it under 500 characters.
- Network error: Pakkam could not reach the server. Check your connection and ask again.
- Server error: Something went wrong on the server. Ask again in a moment.
- How it works heading: How an answer is made
  1. **It finds the pages.** Your question is matched against 18 official documents in
     Tamil, Hindi and English, whatever language you asked in.
  2. **It answers from those pages only.** Each sentence cites the page it uses. Numbers
     are copied from the document, not worked out.
  3. **It checks, or it stops.** Sentences the pages don't back are removed. If nothing is
     left, you get the official contact instead of a guess.
- Sources heading: What the documents cover
- Sources sub: Official public documents from Tamil Nadu and central government websites.
- Footer: Pakkam is an independent student project. It is not an official service and is
  not affiliated with any government body. Answers are for information only: check the
  official source before you act on them.

## 7b. The story (scroll chapters)

The page tells why Pakkam exists before it asks anything of the visitor. Told in the second
person so the reader is the person in it; no invented characters or testimonials. Grounded
in what is reported about scheme access (people unsure if they are eligible or how to
apply; official language that confuses; fake scheme forwards; middlemen asking fees). Every
number is from our own documents: the Magalir Urimai G.O. is 43 pages, and its Tamil
page 9 states ஆண்டுக்கு 12 ஆயிரம் ரூபாய் (₹12,000 a year).

Hero (replaces the earlier headline):
- Headline: Somewhere in a government order, there is a line about you.
- Sub: Pakkam finds it. Ask in Tamil, Hindi, English or Tanglish, and see the exact page
  your answer comes from.
- Button: Ask a question

Chapters, each paired with one scene of the sticky illustration:

| # | Heading (verbatim) | Body (verbatim) | Scene |
|---|---|---|---|
| 1 | It starts with a forward. | “₹1,000 every month for women. Apply fast!” Is it real? Is it meant for you? The message doesn't say. | A forwarded message bubble |
| 2 | The real answer is on paper. | It sits in a 43-page government order, written in formal Tamil and official English. Few people have the time to read it. | The bubble shrinks away; pages fan out; a counter rolls to 43 |
| 3 | So people guess. | Or they pay someone who says they know. Or they never apply at all. | Pages dim; three dashed paths lead off to "guess", "pay someone", "give up" |
| 4 | Pakkam reads the pages for you. | Ask the way you would ask at home, in Tamil, Hindi, English or Tanglish. | Pages square up; a Tamil question appears; a scan line reads the top page |
| 5 | Then it shows you the line. | Page 9 of the order: ₹12,000 a year for women who head their families and meet its conditions. The government's own words, so you can check them yourself. | One line lights up; a slip lifts out: "page 9", the Tamil line, "₹12,000 a year" |
| 6 | And when the pages don't say, it tells you. | No guessing. You get the official website or helpline instead. | A blank page: "Not in the documents", and an "Official contact" pill |

Chat heading (now visible): Your question, in your own words.

Mechanics: chapters scroll normally; an IntersectionObserver sets the active scene on the
sticky stage (fully reversible on scroll-up). Scene changes are transform and opacity
transitions only; the scan line loops only while scene 4 is active; the counter rolls only
on entering scene 2. Desktop: chapters left, stage sticky right, inactive chapters dimmed.
Phones: stage sticky at the top half, chapters scroll beneath as paper cards. Reduced
motion: scenes switch instantly, the counter shows 43, no scan loop. The stage is
decorative (`aria-hidden`); the chapters carry the story for screen readers.

## 8. Engineering list

Plain HTML/CSS/vanilla JS in `web/` (index.html + assets/), served by FastAPI's
`app.frontend()`; no build step. Semantic landmarks, skip link, `aria-live="polite"` on the
conversation, `lang` attributes set per message from the API's language, focus-visible in
stamp violet, 44px touch targets on coarse pointers, `overflow-x: clip` on html and body,
reduced motion honoured live, inline SVG favicon, `og:` tags marked `<!-- DEPLOY STEP -->`.
The answer text from the API is inserted with `textContent`, never `innerHTML`.

## 9. Copy gate

Every line above ships verbatim. Before anyone sees the page: zero em dashes, zero stock
words (leverage, seamless, empower, unlock, robust, actionable, data-driven, solutions),
and the body-copy sweep for AI tells.
