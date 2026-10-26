# Pakkam: technical report

Citation-grounded answers about Indian government schemes, asked in Tamil, Hindi, English or
Tanglish, with a per-language evaluation.

> **Status of the numbers.** Every figure below comes from `python -m schemebot.evaluation`
> on 194 **draft** questions that no second person has checked yet. Retrieval is measured on
> all 194; answers only in an 8-question live test on Gemini's free tier (section 8), because
> the Claude account had no credit and Gemini's free tier allows 20 requests a day per model.
> Treat the numbers as development results.

## 1. Problem

Eligibility rules, amounts and documents for welfare schemes are written down, in government
orders, guidelines and departmental policy notes. They are long PDFs in formal English or
Tamil, many of them scans. The people they are for ask in their own words and language, often
mixing Tamil and English in Latin letters ("PM kisan la evlo panam kidaikum"). A general
chatbot answers fluently and without a source, and a wrong income limit or amount costs a
family money.

Goal: answer only from official documents, show the page every sentence comes from, refuse
when the documents do not answer the question, and measure all of that separately for each
of the four ways people ask.

## 2. System

```
PDFs ──► text layer or OCR (per page) ──► language ID ──► section-aware chunks
                                                              │
                                     bge-m3 dense + sparse vectors ──► Qdrant (local)
                                                              │
question ──► digit normalisation ──► hybrid search (top 20, RRF) ──► cross-encoder rerank (top 5)
                                                              │
                         best passage below 0.35? ──► refuse, no LLM call
                                                              │
                  Claude answers in the question's language, citing passages per sentence
                                                              │
       guardrail: cited passage was shown? numbers appear in it? second model agrees?
       failing sentences removed; nothing left ──► refuse with the official contact
```

| Stage | Choice | Why |
|---|---|---|
| Extraction | PyMuPDF text layer; Tesseract OCR per page when the text layer is broken | Half the pages are scans or use legacy Tamil fonts |
| Chunking | Section-aware, at most 1,000 characters, up to 250 characters of overlap | Keeps an eligibility list or table with its heading |
| Embedding | BAAI/bge-m3, dense and sparse | One model for all three scripts; sparse catches scheme names and numbers |
| Store | Qdrant, local mode | No server to run; 2,785 chunks fit easily |
| Fusion | Reciprocal rank fusion of dense and sparse | No score calibration needed |
| Reranker | BAAI/bge-reranker-v2-m3 (fp16) | Multilingual cross-encoder; its probability doubles as the refusal signal |
| Answers | Claude Opus 5.5 (default) or Gemini, structured JSON output | Per-sentence citations as data, not parsed prose |
| Verifier | Claude Haiku 5.5, or Gemini Flash-Lite | Cheap second opinion on each sentence |
| API | FastAPI, one worker, models loaded once | One GPU; requests are serialised |
| UI | Plain HTML, CSS and JavaScript (no build step) | Loads fast on a phone; light and dark themes |

## 3. Data

18 public PDFs, 2,688 pages: 3 central schemes (PM-KISAN, Atal Pension Yojana, Ujjwala), 2
Tamil Nadu government orders (Kalaignar Magalir Urimai Thittam, Chief Minister's Breakfast
Scheme) and 5 Tamil Nadu departmental policy notes for 2024-25. Seven pairs carry the same
content in two languages (the 5 policy notes in English and Tamil; the PM-KISAN e-KYC note and
the APY brochure in English and Hindi), which lets one fact be checked against both versions.
Sources, dates and licences are in [data_sources.md](data_sources.md).

| Document language | Documents | Pages | From the text layer | OCR | Chunks |
|---|---|---|---|---|---|
| English | 9 | 1,356 | 1,328 | 28 | 1,364 |
| Tamil | 7 | 1,327 | 7 | 1,320 | 1,407 |
| Hindi | 2 | 5 | 0 | 5 | 14 |
| **Total** | **18** | **2,688** | **1,335** | **1,353** | **2,785** |

Language is also detected per chunk (1,390 English, 1,382 Tamil, 13 Hindi), since Tamil
documents carry English pages, such as the KMUT G.O.'s English annexure.

Hindi coverage is thin: 2 documents, 5 pages, 14 chunks. Most Hindi questions are answered
from English or Tamil pages through cross-language retrieval, with the answer in Hindi.

## 4. Ingestion

All pages of the Hindi documents and all but 7 pages of the Tamil ones (the KMUT G.O.'s
English annexure) went through OCR. Their text layers looked fine to PyMuPDF but were
unusable: legacy Tamil fonts (TAU-Marutham and similar) map Tamil glyphs to
Latin code points, and broken Devanagari shaping puts the i-sign before its consonant
(`िृषि`). A page goes to OCR when any of these hold:

- too few characters, or replacement / private-use characters;
- letters under half of the text and alphanumerics under 80% (tables stay on the text layer);
- a legacy font name on the page;
- many words starting with an orphan combining mark;
- in Hindi, an i-sign share outside the 2-9% band of real Hindi;
- too many tokens that are not words.

OCR uses the document's own languages (`tam+eng`, `hin+eng`, `eng`), since mixing all three
made Tesseract confuse scripts, and its result replaces the text layer only when it reads at
least a quarter as much text. OCR output is cached by file hash, language and resolution, so
re-running ingestion skips OCR for pages already read.

**Known damage.** OCR misreads digits, and that matters most here: the Tamil higher-education
note reads "ரூ.4,000" where the English says Rs.1,000 for Pudhumai Penn, the Tamil health note
reads "ரூ.4,20,000" for the Rs.1,20,000 insurance income limit, and the Hindi APY brochure
reads "रु.000". In Tamil the error has a pattern: a leading 1 is read as 4 (Rs.1,000 as 4,000,
Rs.1,20,000 as 4,20,000, the hostel food charge Rs.1,400 as 4400), and the senior-citizen
helpline 14567 appears as 14167 in the body text under a correct heading. The guardrail's
number check cannot catch this, because the wrong number is in the cited passage.

## 5. Retrieval

Hybrid search takes the top 20 from dense and sparse search, fused with reciprocal rank
fusion. Tamil and Devanagari digits are mapped to ASCII on both sides. The cross-encoder then
rescores those candidates and keeps 5; its probability for the best passage is the
confidence, and below 0.35 the system refuses without calling the LLM.

### Tanglish gloss

On the development set, answerable Tanglish questions were refused 56% of the time against
0-11% for the other groups. The right page was retrieved (recall@5 100%), but the reranker
scored it low: 0.036 for "PM kisan la varushathuku evlo panam kidaikum", 0.97 for the same
question in English. A lower threshold for Tanglish would not work, since scores for
answerable and unanswerable Tanglish questions overlap (0.015-0.80 and 0.001-0.13).

The fix gives the reranker the question followed by an English gloss of its Tanglish words,
from a fixed list of 169 everyday words and 8 case endings (`retrieve/tanglish.py`):
"PM kisan la varushathuku evlo panam kidaikum (PM kisan in for year how much money will
get)". Scheme names are deliberately left out of the list so they still match the Tamil
documents. First-stage search keeps the question as typed.

The word list was written before the 62 held-out questions, so those test whether it
generalises. Three reranker inputs, same first-stage candidates, threshold 0.35 (Tanglish
questions only):

| Reranker reads | Dev: false refusal | Dev: correct refusal | Held-out: false refusal | Held-out: correct refusal |
|---|---|---|---|---|
| The question as typed | 56% (5/9) | 100% (3/3) | 58% (7/12) | 100% (4/4) |
| The English gloss only | 11% | **33%** | 33% | 100% |
| Question + gloss (chosen) | 22% | 100% | 33% | 100% |

Gloss alone let two of three unanswerable development questions through (e.g. "magalir urimai
thogai indha maasam eppo varum", when will this month's payment come, rose from 0.13 to above
the threshold), so the question is kept and the gloss appended. That choice was made on the
development set; on the held-out set both variants cut false refusals from 58% to 33% without
answering any unanswerable question.

Language detection missed 6 of the 28 Tanglish questions in the first two batches (e.g.
"tamil pudhalvan scheme la pasangalukku evlo panam" has one lexicon word in seven), so the
gloss is not gated on it. It is applied to any romanised question with words to gloss; none
of the English questions has any, so English is unchanged.

**Detection.** Language detection also decides the answer and refusal language, so it gained a
second signal: Tamil case and verb endings joined to a word (-ukku, -aanga, -radhu, -chu).
None of the 1,390 English chunks in the corpus trips it. It now finds 12 of 12 development,
14 of 16 first held-out and 20 of 21 fresh (second held-out batch) Tanglish questions.

**Effect on all 194 questions** (section 8), false refusal on answerable Tanglish questions:

| Batch | Without gloss | With gloss |
|---|---|---|
| Development (9) | 56% | 22% |
| Held-out 1 (12) | 58% | 33% |
| Held-out 2, written after both Tanglish changes (18) | 83% | 61% |
| **All Tanglish (39)** | **69%** | **44%** |

The other groups are unchanged, and recall@5 is the same with and without the gloss (98%).
The gloss helps on every batch, but the fresh batch shows it is not enough: most of its
refused questions have the right page in the top 5 and their scores rise (0.02 to 0.12, say)
without reaching the threshold. Tanglish is still the largest gap between groups.

Two development questions show the gloss's risk: q039 and q040 were refused with the right
page retrieved, and with the gloss they pass the check. q040 turned out to have a page stating
its answer in the top 5 (a label gap, section 8) and was answered correctly in the live test;
q039 passes without its gold page and was correctly refused by the model.

## 6. Answers and guardrails

The passages go to Claude with their numbers; the reply is JSON with a list of sentences,
each listing the passages it relies on, or a "not answerable" flag. It answers in the
question's language (Tanglish answers in Tanglish). Then every sentence must pass, cheapest
first:

1. it cites at least one passage that was actually shown;
2. every number in it (amount, age, income, date) appears in a cited passage, after digit
   normalisation;
3. a second model (Claude Haiku 5.5) reads the sentence with its passages and agrees they
   state it.

Failing sentences are dropped; if none are left, the answer is a refusal. The checks fail
closed: a sentence the verifier does not confirm is dropped, and if the verifier cannot be
reached the whole answer is refused as unavailable. Refusals are written in
the question's language and point to the official website, and to a helpline only where a
document in the corpus states one (`data/contacts.json`).

**Provider.** Claude is the default. A Gemini client (`generate/gemini.py`) implements the
same interface: it requests JSON that follows the same schemas, and maps safety blocks to a
decline and API failures to "unavailable", so the pipeline, guardrail and evaluation run
unchanged. `SCHEMEBOT_LLM_PROVIDER` switches between them. The answer-quality numbers in
section 8 were measured with Gemini, because the Claude account had no credit during
development. On the free tier, rate-limited and overloaded calls were retried with backoff
for about three minutes (now `SCHEMEBOT_LLM_RETRIES=7`; the app default is 2 retries of at
most 60 s each, so a visitor is not kept waiting), and calls that still fail are counted separately in the results.

## 7. Service and interface

`POST /ask` returns cited sentences, citations with page ranges, excerpts and source URLs,
the refusal reason if any, the confidence and latency. The audit log keeps a hash of the
question, never its text. For a public demo `/ask` is rate limited per visitor (10 a minute)
and in total (500 a day), because each question can cost two LLM calls. Errors return a
generic message with a request ID.

The web UI, **Pakkam** ("page" in Tamil), has a home page that tells the story of one
forwarded WhatsApp message and a chat app where every sentence carries a numbered chip that
opens the cited passage and a link to the PDF at that page. It follows the system light or
dark setting, with a manual switch; the colour pairs used for text meet WCAG AA contrast in
both themes (lowest 5.5:1 in dark, 6.1:1 in light, checked by script).
Server text is inserted as text, never HTML.

## 8. Evaluation

### Question set

194 questions in four groups (English, Tamil, Hindi, Tanglish), each with 38-39 answerable
and 10 unanswerable, in three batches:

- **Development (q001-q048):** drafted from the first 10 documents; the Tanglish gloss was
  designed on these.
- **Held-out 1 (q049-q110):** 12 facts from the 5 policy-note pairs and 4 out-of-corpus
  topics, written after the gloss word list was fixed.
- **Held-out 2 (q111-q194):** 18 more facts (Atal Pension, Ujjwala, marriage assistance,
  free bus travel, hostels, health and higher-education schemes) and 3 out-of-corpus topics,
  written after both Tanglish changes.

Each fact is asked in all four groups. Gold labels are pages, listed in both language versions
where both state the fact. All 194 are drafts; `python -m schemebot.evaluation.review export`
writes a spreadsheet with each question beside its gold-page text for a native speaker to
check, and `import` marks the checked ones verified.

Metrics (details in [evaluation.md](evaluation.md)): recall@1 and @5 and MRR of gold pages
among the 5 reranked passages; correct refusal (unanswerable questions refused) and false
refusal (answerable ones refused), where "refused" in a retrieval-only run means confidence
below 0.35; retrieval latency on a laptop RTX 4060 (8 GB).

### Results (retrieval only)

From [results.md](results.md), hybrid search, reranker and Tanglish gloss on:

| Group | Ans/Unans | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Retrieval p50 / p95 ms |
|---|---|---|---|---|---|---|---|
| English | 39/10 | 85% | 100% | 0.91 | 90% | 5% | 495 / 921 |
| Tamil | 38/10 | 92% | 100% | 0.96 | 90% | 8% | 532 / 644 |
| Hindi | 38/10 | 79% | 100% | 0.88 | 100% | 8% | 578 / 691 |
| Tanglish | 39/10 | 82% | 92% | 0.87 | 100% | 44% | 525 / 775 |
| **All** | 154/40 | 84% | 98% | 0.90 | 95% | 16% | 533 / 720 |

By batch (all groups):

| Batch | Answerable / unanswerable (n) | Recall@1 | Recall@5 | Correct refusal | False refusal |
|---|---|---|---|---|---|
| Development | 36 / 12 | 89% | 97% | 83% | 8% |
| Held-out 1 | 46 / 16 | 89% | 100% | 100% | 9% |
| Held-out 2 | 72 / 12 | 79% | 97% | 100% | 25% |

Recall@5 means a gold page was among the 5 retrieved passages; it does not measure whether
the written answer is correct. One person wrote every question and the system, and the
threshold was chosen on the first 110 questions, so held-out 2 is the only batch untouched by
any tuning.

Retrieval holds up on the fresh batch (recall@5 97%), but its false refusals are higher:
Tanglish (61%) and several Ujjwala and marriage-assistance questions in Tamil and Hindi score
just under the threshold with the right page found. The unanswerable questions of the later
batches are further from the corpus than the development set's near misses, so correct
refusal there is easier.

**The threshold.** Choosing it on the first 110 questions and testing on held-out 2 shows no
better operating point: at 0.2, false refusals fall (tuning 9% to 6%, test 25% to 18%) but
correct refusals fall too (tuning 93% to 79%). The retrieval threshold mainly saves an LLM
call; the model's own "not answerable" judgement refused every near miss in the live test
below, so a lower threshold may pay off once answer quality can be measured on all 194
questions. It stays at 0.35 until then.

### Ablations

Same 194 questions, one change at a time:

| Configuration | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Tanglish false refusal | p50 ms |
|---|---|---|---|---|---|---|---|
| **Full** (hybrid, rerank, gloss) | 84% | 98% | 0.90 | 95% | 16% | 44% | 533 |
| No Tanglish gloss | 84% | 98% | 0.90 | 95% | 23% | 69% | 521 |
| No reranker | 68% | 94% | 0.78 | 0%* | 0%* | 0%* | 280 |
| Dense only (+ rerank, gloss) | 84% | 99% | 0.91 | 95% | 16% | 44% | 366 |
| Sparse only (+ rerank, gloss) | 66% | 72% | 0.68 | 95% | 36% | 49% | 509 |

\* Without the reranker there is no calibrated confidence: every question passes the
threshold, including all 40 unanswerable ones. Refusal then rests entirely on the LLM.

**What the ablations show.**

- **The reranker** is worth its 250 ms: recall@1 rises from 68% to 84%, and it is the only
  source of a usable refusal signal.
- **Dense search does the cross-language work.** Sparse search alone finds the gold page in
  the top 5 for 29% of Hindi questions and 76% of Tamil ones (100% for both with dense),
  because word-level weights cannot link a question to a page in another language or a
  differently worded OCR page. It does fine for English (97%).
- **Sparse adds nothing measurable here.** Dense-only matches hybrid (recall@5 99% against
  98%, MRR 0.91 against 0.90) and is faster. Hybrid stays the default because sparse
  matching should help with exact scheme names, G.O. numbers and amounts that this question
  set barely exercises; a larger verified set should decide. Latency differences of about
  50 ms between runs are noise on this laptop.
- **The Tanglish gloss** cuts Tanglish false refusals from 69% to 44% and changes nothing for
  the other groups.

### Live answers (Gemini, 8 questions)

Gemini's free tier allows 20 requests a day per model. Gemini 3.6 Flash ran out after a few
questions of the full run, 3.8 Flash was overloaded, and Gemini 4 Argon has no free quota. So
answers were checked live on 8 chosen questions, with Gemini 3.5 Flash-Lite answering and 3.1
Flash-Lite verifying and judging, through the same pipeline and guardrail:

| Question | Group | Outcome |
|---|---|---|
| q001 Who can apply for Magalir Urimai? | English | Answered, 3 sentences, all faithful, all cite gold pages |
| q016 Magalir Urimai yearly amount | Tamil | Answered in Tamil: Rs.12,000 a year; faithful, gold page |
| q025 PM-KISAN yearly amount | Hindi | Answered in Hindi: Rs.6,000 in three instalments; faithful |
| q043 Ujjwala documents | Tanglish | Answered in Tanglish, 2 sentences, faithful |
| q040 PM-KISAN yearly amount | Tanglish | Answered in Tanglish: Rs.6,000 in three instalments; faithful |
| q039 Magalir Urimai and government jobs | Tanglish | Refused; its gold page was not retrieved, so refusing was right |
| q011 Next PM-KISAN instalment date | English | Refused, pointing to the PM-KISAN website: correct |
| q023 New ration card | Tamil | Refused in Tamil, pointing to the KMUT website: correct |

All 8 sentences were judged faithful. This is model-judged: the same Flash-Lite model ran
the in-pipeline support check and the judging, so it is not an independent judge, and no
person checked the verdicts. No call failed, and every refusal came in the
question's language with the official website. Both near misses that passed the retrieval
check were refused by the model, and q039, the risk of the Tanglish gloss, was refused rather
than answered wrongly. End-to-end time was 13 to 52 seconds per answer on the free tier,
including retries; a paid tier should be much faster.

The live answers also exposed a **labelling gap**: q025 and q040 cited page 1 of the
PM-KISAN e-KYC note, which states "Rs 6,000/- per year in three equal instalments" but was
missing from the draft labels. The label was widened (3 questions), so q040 now counts as
found. q043 cited page 1 of the Ujjwala procedure, not the labelled page 2; page 1 does not
list the documents, so that label stands and the citation was to a neighbouring passage.

Eight questions are a smoke test, not an evaluation: faithfulness and citation accuracy over
all 194 questions still need a paid key (Claude, or Gemini with billing).

### Error analysis

1. **Tanglish** remains the weakest group (section 5): 44% false refusal (61% on the fresh
   batch), mostly with the right page retrieved but scored under the threshold.
2. **Near misses get through.** The two wrongly passed unanswerable questions are both near
   a covered topic: "When will the next PM-KISAN instalment be paid?" (0.44; the guidelines
   describe instalment periods but give no dates) and "How do I apply for a new ration card?"
   in Tamil (0.85; the Magalir Urimai G.O. discusses ration cards at length). The LLM has to
   refuse these.
3. **Hindi recall@1 is lowest (79%)** while recall@5 is 100%: the reranker sometimes favours
   a passage in the question's own script (the Hindi PM-KISAN e-KYC note over the English
   guidelines), or puts a nearby page of the right document first (page 473 for 474).
4. **Draft labels were incomplete ten times.** The Magalir Urimai amount, Pudhumai Penn,
   the women helpline, the PM-KISAN amount (found by the live answers), four facts found by an
   audit that searches for pages stating a fact's numbers outside its labels (the senior and
   child helplines, the 3,600-unit rule, the transgender self-employment grant), and two
   Tamil pages the retriever found with high confidence (TAHDCO subsidy, hostel uniforms).
   Every one made the system look worse than it was. Labels need a second reader before the
   numbers mean much.
5. **OCR digit errors** (section 4) do not show in retrieval metrics at all; they will show in
   answer accuracy.

## 9. Limitations

- **Draft labels.** No question has been checked by a second person; ten incomplete labels
  have already been found and fixed (section 8). The review sheet makes checking quick.
- **Answer quality on 8 questions only.** The live test passed, but faithfulness and citation
  accuracy over all 194 questions need a paid key (Claude, or Gemini with billing); the
  free-tier test used small Flash-Lite models, and one model both verified and judged.
- **OCR digits.** Wrong numbers in Tamil and Hindi OCR text pass the number check.
- **Tanglish.** 44% of answerable Tanglish questions are still refused; detection misses 3
  of 49 Tanglish questions, whose answers and refusals would come back in English.
- **Near misses.** Questions next to a covered topic ("next PM-KISAN instalment date") get
  high retrieval confidence; only the LLM's "not answerable" judgement refuses them.
- **Scope.** 18 documents from one state plus three central schemes; rules change, and
  answers reflect the documents' dates.
- **Not an official service.** It does not process applications or personal data.

## 10. Reproducing

```bash
uv sync --extra ingest --extra index --extra generate --extra api --extra eval
uv run python -m schemebot.ingest         # PDFs listed in data/sources.json
uv run python -m schemebot.index
uv run python -m schemebot.evaluation --retrieval-only     # writes docs/results.md
uv run pytest                              # 190 fast tests (pytest -m models: 10 more)
```

## 11. Next steps

1. With a paid key (Claude, or Gemini with billing), run the full evaluation:
   `python -m schemebot.evaluation --workers 4`, and re-check the threshold with answer
   quality in view.
2. Have Tamil and Hindi speakers verify the 194 drafts with the review sheet.
3. Tanglish: transliterate to Tamil script before reranking, or fine-tune the reranker on
   Tanglish question-passage pairs, and test on a fresh batch.
4. Re-OCR number-dense Tamil pages at a higher resolution, or prefer the English version of a
   paired document when numbers disagree.
