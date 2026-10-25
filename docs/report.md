# Pakkam: technical report

Citation-grounded answers about Indian government schemes, asked in Tamil, Hindi, English or
Tanglish, with a per-language evaluation.

> **Status of the numbers.** Every figure below comes from `python -m schemebot.evaluation`
> on 110 **draft** questions that no second person has checked yet. Retrieval is measured on
> all 110; answers only in an 8-question live test on Gemini's free tier (section 8), because
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
reads "रु.000". The guardrail's number check cannot catch this, because the wrong number is in
the cited passage.

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

Language detection missed 6 of the 28 Tanglish questions (e.g. "tamil pudhalvan scheme la
pasangalukku evlo panam" has one lexicon word in seven), so the gloss is not gated on it. It
is applied to any romanised question with words to gloss; none of the English questions has
any, so English is unchanged.

In the full evaluation (section 8) the gloss cut Tanglish false refusals from 57% to 29% and
left the other three groups exactly as they were. Per question, of the 21 answerable Tanglish
questions:

- **Without the gloss**, 9 passed the confidence check, all with a gold page in the top 5.
- **With it**, 15 passed: 13 with a gold page in the top 5 (6 of them newly rescued, each
  with the gold page ranked first), and **2 without one**. q039 (Magalir Urimai and
  government employees) and q040 (PM-KISAN yearly amount) were refused before, with the
  right page retrieved; now they pass with the wrong pages. That is the worst outcome: only
  the LLM's "not answerable" judgement and the guardrail stand between them and a wrong
  answer.
- Two questions that passed before are now refused (q042, and q103 at 0.349 against 0.35).

(After the PM-KISAN label fix in section 8, q040 turned out to have a page stating its answer in the top 5 after all, and the live test answered it correctly and refused q039.) So the gloss trades at most 2 risky passes for 4 more correctly grounded answers. The full-pipeline
run will show whether the LLM refuses q039 and q040; until then, this is the main open risk of
the change, and the remaining 29% is still the largest gap between groups.

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
development. On the free tier, rate-limited and overloaded calls are retried with backoff
for about three minutes, and calls that still fail are counted separately in the results.

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

110 questions in four groups (English, Tamil, Hindi, Tanglish), each about 21 answerable and
7 unanswerable. q001-q048 are the development set, drafted from the first 10 documents;
q049-q110 are held out: 12 facts from the 5 policy-note pairs and 4 topics the corpus does
not cover (crop insurance premium, voter ID, rooftop solar subsidy, duplicate Aadhaar), each
asked in all four groups and written after the Tanglish word list was fixed. Gold labels are
pages, listed in both language versions where both state the fact. All 110 are drafts.

Metrics (details in [evaluation.md](evaluation.md)): recall@1 and @5 and MRR of gold pages
among the 5 reranked passages; correct refusal (unanswerable questions refused) and false
refusal (answerable ones refused), where "refused" in a retrieval-only run means confidence
below 0.35; retrieval latency on a laptop RTX 4060 (8 GB).

### Results (retrieval only)

From [results.md](results.md), hybrid search, reranker and Tanglish gloss on:

| Group | Ans/Unans | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Retrieval p50 / p95 ms |
|---|---|---|---|---|---|---|---|
| English | 21/7 | 86% | 100% | 0.91 | 86% | 5% | 435 / 523 |
| Tamil | 20/7 | 100% | 100% | 1.00 | 86% | 0% | 459 / 543 |
| Hindi | 20/7 | 80% | 100% | 0.89 | 100% | 0% | 471 / 545 |
| Tanglish | 21/7 | 90% | 95% | 0.92 | 100% | 29% | 420 / 499 |
| **All** | 82/28 | 89% | 99% | 0.93 | 93% | 9% | 444 / 543 |

Development and held-out sets separately (all groups): recall@5 97% and 100%, false refusal
8% and 9%, correct refusal 83% and 100%. The held-out set is not harder for retrieval; its
unanswerable topics are further from the corpus than the development set's near misses.

### Ablations

Same 110 questions, one change at a time. These runs predate the PM-KISAN label fix below
(3 questions), so compare them with the first row, not with the results table above:

| Configuration | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Tanglish false refusal | p50 ms |
|---|---|---|---|---|---|---|---|
| **Full** (hybrid, rerank, gloss), before the label fix | 85% | 98% | 0.90 | 93% | 9% | 29% | 526 |
| No Tanglish gloss | 84% | 99% | 0.90 | 93% | 16% | 57% | 520 |
| No reranker | 68% | 94% | 0.79 | 0%* | 0%* | 0%* | 321 |
| Dense only (+ rerank, gloss) | 85% | 99% | 0.91 | 93% | 9% | 29% | 369 |
| Sparse only (+ rerank, gloss) | 67% | 74% | 0.70 | 93% | 27% | 33% | 491 |

\* Without the reranker there is no calibrated confidence: every question passes the
threshold, including all 28 unanswerable ones. Refusal then rests entirely on the LLM.

**What the ablations show.**

- **The reranker** is worth its 200 ms: recall@1 rises from 68% to 85%, and it is the only
  source of a usable refusal signal.
- **Dense search does the cross-language work.** Sparse search alone finds the gold page in
  the top 5 for only 30% of Hindi questions (100% with dense), because word-level weights
  cannot link a Hindi question to English or Tamil text. It does fine for English (100%).
- **Sparse adds nothing measurable here.** Dense-only matches hybrid (recall@5 99% against
  98%, MRR 0.91 against 0.90) and is faster. Hybrid stays the default because sparse
  matching should help with exact scheme names, G.O. numbers and amounts that 110 questions
  barely exercise; a larger verified set should decide. Latency differences between runs of
  about 50 ms are noise on this laptop.
- **The Tanglish gloss** halves Tanglish false refusals and changes nothing for the other
  groups.

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

All 8 sentences were judged faithful, no call failed, and every refusal came in the
question's language with the official website. Both near misses that passed the retrieval
check were refused by the model, and q039, the risk of the Tanglish gloss, was refused rather
than answered wrongly. End-to-end time was 13 to 52 seconds per answer on the free tier,
including retries; a paid tier should be much faster.

The live answers also exposed a **labelling gap**: q025 and q040 cited page 1 of the
PM-KISAN e-KYC note, which states "Rs 6,000/- per year in three equal instalments" but was
missing from the draft labels. The label was widened (3 questions) and retrieval re-run; q040
now counts as found, which is why Tanglish recall@5 is 95%, not 90%. q043 cited page 1 of the
Ujjwala procedure, not the labelled page 2; that label needs the same check.

Eight questions are a smoke test, not an evaluation: faithfulness and citation accuracy over
all 110 questions still need a paid key (Claude, or Gemini with billing).

### Error analysis

1. **Tanglish** remains the weakest group (section 5): 29% false refusal, and one question
   (q039) that passes the confidence check without its gold page (the model refused it).
2. **Near misses get through.** The two wrongly passed unanswerable questions are both near
   a covered topic: "When will the next PM-KISAN instalment be paid?" (0.44; the guidelines
   describe instalment periods but give no dates) and "How do I apply for a new ration card?"
   in Tamil (0.85; the Magalir Urimai G.O. discusses ration cards at length). The LLM has to
   refuse these.
3. **Hindi recall@1 is lowest (80%)** while recall@5 is 100%. Of the 4 top-1 misses, 1
   ranks the Hindi PM-KISAN e-KYC note above the English guidelines that actually answer the
   question (the reranker favours a passage in the question's own script); the other 3 put a
   nearby page of the right document first (page 473 for 474).
4. **Draft labels were incomplete four times**: the Magalir Urimai amount (also on the Tamil
   page 9), Pudhumai Penn and the women helpline (widened while writing the held-out set), and
   the PM-KISAN amount (found by the live answers). Labels need a second reader before the
   numbers mean much.
5. **OCR digit errors** (section 4) do not show in retrieval metrics at all; they will show in
   answer accuracy.

## 9. Limitations

- **Draft labels.** No question has been checked by a second person. One wrong draft label
  has already been found and fixed (section 8).
- **Answer quality on 8 questions only.** The live test passed, but faithfulness and citation
  accuracy over the full set need a paid key; the free-tier test used small Flash-Lite models,
  and one model both verified and judged.
- **OCR digits.** Wrong numbers in Tamil and Hindi OCR text pass the number check.
- **Near misses.** Questions next to a covered topic ("next PM-KISAN instalment date") get
  high retrieval confidence; only the LLM's "not answerable" judgement refuses them.
- **Tanglish detection.** The lexicon detector missed 6 of 28 Tanglish questions. The answer
  language follows detection, so those would be answered in English, and refusals shown in
  English.
- **Scope.** 18 documents from one state plus three central schemes; rules change, and
  answers reflect the documents' dates.
- **Not an official service.** It does not process applications or personal data.

## 10. Reproducing

```bash
uv sync --extra ingest --extra index --extra generate --extra api --extra eval
uv run python -m schemebot.ingest         # PDFs listed in data/sources.json
uv run python -m schemebot.index
uv run python -m schemebot.evaluation --retrieval-only     # writes docs/results.md
uv run pytest                              # 172 fast tests
```

## 11. Next steps

1. With a paid key (Claude, or Gemini with billing), run the full evaluation:
   `python -m schemebot.evaluation --workers 4`.
2. Have a Tamil and a Hindi speaker verify the 110 drafts; grow to about 200.
3. Re-OCR number-dense pages at a higher resolution, or prefer the English version of a
   paired document when numbers disagree.
4. Tune the refusal threshold on verified labels, per language if the data supports it.
