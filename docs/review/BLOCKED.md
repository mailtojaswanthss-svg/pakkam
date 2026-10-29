# Pakkam 2.0 - Blocked Items Tracker

This document records all tasks, assets, or decisions that require human action or external input.
Per Master Prompt 2 guidelines, engineering work continues autonomously on non-blocked items.

| ID | Item / Gate | Required From | Description | Status |
|---|---|---|---|---|
| BLK-01 | Held-out Question Evaluation | User | Creation of `.freeze` file in repository root (scheduled Mon 2 Nov) before running the 20-30 held-out questions. | Blocked on `.freeze` trigger |
| BLK-02 | Teammate 50 Verified Questions | Teammate | Ingestion of teammate's 50 verified questions into `data/eval/` for full answer evaluation batch. | Blocked on teammate data delivery |
| BLK-03 | Field Audio Recordings | User / Field | Collection and placement of 30 physical audio recordings into `data/voice/field_clips/` under user consent protocol. | Blocked on field recording collection |
| BLK-04 | Helpline Verification | User | Verification of 9 scheme helplines against official pages only in `docs/review/helpline_check.csv` (no phone calls required). | Blocked on official page check |
| BLK-05 | Answer-Level Human Grading | User | Hand-grading of ~60 answers (10 samples + ~30 verified + 20 held-out) in `docs/review/grading_sheet.csv`. | Blocked on human evaluator |
| BLK-06 | OCR Page Disagreement Review | User | Review of the 68 scanned/legacy Tamil PDF pages flagged with amount disagreements. | Blocked on human document review |
| BLK-07 | Remote Push / PR Creation | User | Explicit `PUSH_BRANCH_NOW: yes` decision to push feature branch to origin. | Gated on user decision |
| BLK-08 | Cloud Hosting / Phone Test | User | Real phone network and live server deployment test (Twilio/Exotel or physical SIP). | NOT PLANNED |
