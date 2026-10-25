# Pakkam frontend plan (v2)

Two pages instead of one:

| URL | Page | Job |
|---|---|---|
| `/` | Home | Tell the story of the project and make people feel why it matters; send them to the chat |
| `/chat/` | Chat app | The product: a full-screen chat where citizens ask and get cited answers |

## What we took from the references

- **sarvam.ai**: show the product working instead of describing it (live-looking demo
  panels with process steps and language chips); calm, light canvas; pill buttons; a small
  Indian ornament as a motif.
- **olakrutrim.com**: a small badge above the headline; a strip of real impact numbers; a
  case study of a public, multilingual assistant (Kumbh Sahayak).
- Avoided on purpose: one word of the headline in a different style, gradient washes as
  decoration, identical card grids (all listed as generated-page tells).

## Type: warmer and adaptive

Two families by Indian foundries, each covering Latin, Devanagari and Tamil, so all three
scripts read as one voice:

- **Display: Baloo 2** (Latin, Devanagari) + **Baloo Thambi 2** (Tamil), Ek Type. Rounded
  and warm: a public service for people, not a cloud console. Weights 600 and 800.
- **Body: Hind** (Latin, Devanagari) + **Hind Madurai** (Tamil), Indian Type Foundry.
  Highly readable at small sizes. Weights 400, 500, 600.

Fluid type scale (one ratio at 375 px, a larger one at 1440 px, everything in between via
`clamp`), so text adapts to the screen instead of jumping at breakpoints:

| Token | 375 px | 1440 px | Use |
|---|---|---|---|
| `--step--1` | 13 px | 14 px | captions, credits |
| `--step-0` | 16 px | 18 px | body |
| `--step-1` | 19 px | 22 px | lead text, card titles |
| `--step-2` | 23 px | 30 px | section titles (small) |
| `--step-3` | 28 px | 40 px | section titles |
| `--step-4` | 34 px | 56 px | page titles |
| `--step-5` | 40 px | 76 px | home hero |

Tamil and Devanagari get line-height 1.7, Latin 1.5.

## Colour

Kept the identity (ledger paper and rubber-stamp violet) and added one warm note from the
photos, used only in illustrations and highlights, never on controls:

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#EEF1EA` | page background (ledger paper; never pure white) |
| `--panel` | `#FBFCF9` | cards, chat surface |
| `--ink` | `#1B2130` | text |
| `--ink-2` | `#4A5366` | secondary text |
| `--line` | `#D3D9CD` | dividers |
| `--border` | `#7D8A78` | interactive borders (3:1) |
| `--stamp` | `#5A36A3` | the accent: primary buttons, citations, focus |
| `--marigold` | `#E3A33B` | warm highlight in illustrations only |

## Spacing: no big gaps, no cramming

- One 4 px based scale: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- Sections: `padding-block: clamp(48px, 7vw, 96px)`; never `min-height: 70vh` blocks.
- Content width 1200 px; text blocks capped at 60-68 characters.
- Inside cards: 24 px (16 px on phones). Grid gaps: 16 px on phones, 24 px on desktop.
- The old six tall story chapters (72 vh each, mostly empty) are replaced by a dense story
  bento and an animated demo.

## Home page sections

1. **Nav**: Pakkam mark; Story, How it works, Results; "Open Pakkam" pill.
2. **Hero**: badge ("Student research project, Tamil Nadu"); headline "Somewhere in a
   government order, there is a line about you."; sub; "Ask Pakkam" and "See how it works".
   Right: the phone photo in an arched frame (an arch like a temple doorway is the shared
   motif), with a floating forwarded message and a floating answer slip ("page 9,
   ₹12,000 a year") that tell the whole story in one picture.
3. **Language strip**: the four ways to ask, in their own scripts.
4. **The story (bento)**: the forward; the 43-page order (files photo); so people guess;
   the honest no. Dense tiles, different sizes, no empty chapters.
5. **Live demo** (Sarvam pattern): a Tamil question, then the real pipeline steps
   (finding the pages, reading page 9, checking every sentence), then the cited answer
   with its source slip. Plays when scrolled into view; "Play again" button.
6. **Who it's for**: three photos (farmers, students, elders), each with real facts from
   our documents (PM-KISAN ₹6,000 a year; Pudhumai Penn ₹1,000 a month; Atal Pension
   ₹1,000 to ₹5,000 a month after 60).
7. **How it works**: three numbered steps (a real sequence).
8. **Measured, not claimed** (Krutrim pattern): 18 official documents, 2,785 passages,
   4 language groups, right page in the top 5 for 36 of 36 test questions, labelled as a
   development test on draft questions.
9. **Final call to action** band: "Ask your first question".
10. **Footer**: disclaimer, photo credits, sources.

## Chat page

- Full-height app shell (`100dvh`). Desktop: left sidebar (new conversation, languages,
  schemes covered, links), conversation in the centre (max 760 px), composer pinned at the
  bottom, and a right **sources panel** that opens when a citation is tapped. Phones:
  sidebar becomes a drawer, sources become a bottom sheet.
- Welcome state: greeting in four scripts, "What would you like to know about a scheme?",
  and suggestion cards (topic + question in its language).
- Assistant messages: Pakkam's stamp avatar, the answer with citation chips, a small
  meta line (answered in N seconds), disclaimer. Refusals get a distinct calm style with
  the official contact.
- Waiting state: "Finding the pages, reading them, checking every sentence" with an
  indeterminate indicator; no fake step-by-step progress.
- Composer: large rounded box, send button, Enter to send (Shift+Enter for a new line,
  never during IME composition), hint "Answers come from official documents only".

## Engineering

Plain HTML/CSS/JS, no build step, served by FastAPI. Shared `tokens.css`; `home.css` +
`home.js`; `chat.css` + `chat.js`. Photos are local WebP, lazy-loaded below the fold,
credited in the footer and `web/assets/img/CREDITS.md`. All server text inserted with
`textContent`. Reduced motion honoured. Copy gate before showing anyone.
