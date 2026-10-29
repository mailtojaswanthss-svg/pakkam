# Pakkam 2.0 - Blocked Items Tracker

This document records all tasks, assets, or decisions that require human action or external input.
Per Master Prompt 2 guidelines, engineering work continues autonomously on non-blocked items.

| ID | Item / Gate | Required From | Description | Status |
|---|---|---|---|---|
| BLK-01 | Held-out Question Evaluation | User | Creation of `.freeze` file in repository root (scheduled Mon 2 Nov) before running the 20-30 held-out questions. | Blocked on `.freeze` trigger |
| BLK-02 | Teammate 50 Verified Questions | Teammate | Ingestion of teammate's 50 verified questions into `data/eval/` for full answer evaluation batch. | Blocked on teammate data delivery |
| BLK-03 | Field Audio Recordings | User / Field | Collection and placement of 30 physical audio recordings into `data/voice/field_clips/` under user consent protocol. | Blocked on field recording collection |
| BLK-04 | Helpline Human Verification | User | Manual human telephone verification and URL citation recording for the 9 scheme helplines in `docs/review/helpline_check.csv`. | Blocked on human phone verification |
| BLK-05 | Answer-Level Human Grading | User | Completion of manual hand-grading sheet (`docs/review/grading_sheet.csv`) for answer factuality and attribution. | Blocked on human evaluator |
| BLK-06 | OCR Page Disagreement Review | User | Review of the 68 scanned/legacy Tamil PDF pages flagged with amount disagreements. | Blocked on human document review |
| BLK-07 | Remote Push / PR Creation | User | Explicit `PUSH_BRANCH_NOW: yes` decision to push feature branch to origin. | Gated on user decision |
| BLK-08 | Cloud Hosting / Phone Test | User | Real phone network and live server deployment test (Twilio/Exotel or physical SIP). | Gated on infrastructure |
