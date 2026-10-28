import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def create_report():
    doc = Document()
    
    # Page setup - 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    PRIMARY = RGBColor(26, 54, 93)     # Navy #1A365D
    SECONDARY = RGBColor(49, 130, 206) # Slate Blue #3182CE
    DARK_TEXT = RGBColor(45, 55, 72)   # Dark Gray #2D3748
    MUTED_TEXT = RGBColor(113, 128, 150) # Gray #718096
    WARNING_TEXT = RGBColor(197, 48, 48) # Red #C53030

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(10)
    font.color.rgb = DARK_TEXT

    # Header / Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run("PAKKAM 2.0: RESEARCH PROTOTYPE BENCHMARK REPORT")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(10)
    run_sub = sub_p.add_run("Evidence, Engineering Boundaries, and Known Limitations (Draft Questions Benchmark)")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = SECONDARY

    # Status Alert Box
    alert_table = doc.add_table(rows=1, cols=1)
    alert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_alert = alert_table.rows[0].cells[0]
    c_alert.width = Inches(6.5)
    set_cell_background(c_alert, "FFF5F5")
    set_cell_margins(c_alert, 70, 70, 100, 100)
    p_alert = c_alert.paragraphs[0]
    r_al_b = p_alert.add_run("STATUS: Research Prototype (Do Not Push to Git Remote)\n")
    r_al_b.font.bold = True
    r_al_b.font.size = Pt(9.5)
    r_al_b.font.color.rgb = WARNING_TEXT
    r_al_t = p_alert.add_run(
        "Evidence gathered to date is measured on draft questions and synthetic/read speech. "
        "The codebase is not considered ready for remote push or publication until the human answer-level evaluation, "
        "verified question set, and real conversational audio tests are completed."
    )
    r_al_t.font.size = Pt(8.5)
    r_al_t.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Working Branch:", "feat/prompt-pack-execution (Local only; unpushed)"),
        ("Corpus Under Test:", "18 PDFs, 2,688 pages, 4,449 chunks in Qdrant ('pakkam_chitra')"),
        ("Author / Contributor:", "@Jaswanth SS (Developer-authored draft benchmarks)"),
        ("Verification Status:", "55/55 Unit Tests Passing | Custom Regex Scan: 0 secrets | Real Clone: Pending")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.width = Inches(2.0)
        cell_v.width = Inches(4.5)
        set_cell_background(cell_k, "F7FAFC")
        set_cell_background(cell_v, "EDF2F7")
        set_cell_margins(cell_k, 40, 40, 70, 70)
        set_cell_margins(cell_v, 40, 40, 70, 70)
        
        p_k = cell_k.paragraphs[0]; p_k.paragraph_format.space_after = Pt(1)
        r_k = p_k.add_run(k); r_k.font.bold = True; r_k.font.size = Pt(8.5); r_k.font.color.rgb = PRIMARY
        
        p_v = cell_v.paragraphs[0]; p_v.paragraph_format.space_after = Pt(1)
        r_v = p_v.add_run(v); r_v.font.size = Pt(8.5); r_v.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. Executive Summary & Research Scope
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. Research Scope & Evaluation Context")
    r1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph(
        "Pakkam 2.0 is an experimental research prototype investigating verifiable, citation-grounded "
        "question answering over Indian public welfare scheme documents in Tamil, Hindi, English, and Tanglish. "
        "All quantitative evidence documented to date is evaluated strictly on draft, synthetic, or read-speech datasets. "
        "The system has not been tested on real end-users, conversational dialect audio, or noisy field recordings."
    )
    p.paragraph_format.space_after = Pt(4)
    
    p = doc.add_paragraph(
        "In compliance with project integrity rules, every reported number is accompanied by its source script, "
        "sample size (n), and evaluation constraints. No metrics are extrapolated beyond their tested boundaries."
    )
    p.paragraph_format.space_after = Pt(10)

    # 2. Key Upgrades Completed
    h1 = doc.add_heading(level=1)
    r = h1.add_run("2. Engineering Upgrades Completed")
    r.font.color.rgb = PRIMARY
    
    features = [
        ("Fact Cards Design Harness (2 Draft Cards): ", 
         "Implemented in data/fact_cards.json with matching via FactCardMatcher using BGE-M3 cosine similarity (>=0.82) "
         "plus mandatory scheme keyword identification. Both cards (KMUT and PM-KISAN) were authored as AI drafts during development. "
         "verified_by is set to null on both unverified cards. Under the load_verified_cards() filter, unverified cards are strictly dropped "
         "at startup and are NEVER served to users (verified by tests/test_fact_cards.py::test_load_verified_cards_filters_unverified). "
         "Evaluated on n=44 draft queries (4 positive, 40 unanswerables): 100% precision on this small sample, 0% false positives. "
         "Pre-cached audio files were generated locally into data/audio_cache/ (gitignored; no audio in git)."),
        
        ("Claim-Lite Quote and Number Checks (Not Entailment): ", 
         "Implemented in src/schemebot/generate/claims.py. Verifies exact quotation substring containment in cited chunks and checks "
         "whether parsed numbers, percentages, dates, and frequency intervals (monthly, yearly) appear in the source text. "
         "Forces status='INSUFFICIENT_EVIDENCE' if amounts mismatch. "
         "Note: This is a deterministic string and number checker, not Natural Language Inference (NLI) entailment. "
         "Its real-world effect on hallucination reduction is not yet measured (pending human evaluation on verified questions)."),
        
        ("Voice-Loop Latency Measurements (Measured Values Only): ", 
         "The previously reported voice stage table was composed of numbers stitched from separate scripts rather than measured "
         "simultaneously in one execution; that table has been removed. Individual measured component benchmarks are: "
         "STT latency on synthetic clip is 1,320.4 ms (scripts/gnani_smoke.py); first-stage search median is 215.6 ms and reranker median "
         "is 236.8 ms (scripts/ablate_retrieval.py, n=194); and Sentence 1 TTS TTFA is 2,795.1 ms (scripts/test_sentence_speech.py, n=3). "
         "Crucial limitation: The project target of 5.0 s end-to-end latency was NOT met. "
         "The 14.07 s sequential baseline was an estimated composite of medians from separate scripts and was not measured on the same run, "
         "so no percentage comparison is claimed."),
        
        ("Short Voice Answer Path: ", 
         "Added VOICE_SYSTEM_PROMPT enforcing a strict 2-sentence maximum, no markdown, and Indic spoken words for currency. "
         "Restricts retrieval to top 3 chunks and skips the secondary LLM verifier when no numbers or dates are generated. "
         "Theoretical quota benefit: up to 50% fewer calls on non-numeric questions, but actual savings across an operational query stream are not measured."),
        
        ("Fast Sources-First Endpoint (POST /ask/sources): ", 
         "Returns top 3 retrieved passages with official document title and page numbers in ~300 ms with 0 LLM calls."),
        
        ("BhashaShield Speech Retrieval Test (31 Clips): ", 
         "Evaluated on 31 clips: 15 Tamil read-speech clips, 15 Hindi read-speech clips from AI4Bharat Kathbath, and 1 synthetic boundary plumbing clip. "
         "Kathbath sentences are general news sentences, not scheme queries. 'Target document' and 'target page' are defined as the top chunk "
         "retrieved when querying the clean reference text. The test measures whether querying the STT transcript retrieves the same top document "
         "(90.3%, 28/31) and same top page (87.1%, 27/31) as the reference text. Tanglish and real conversational recordings are untested."),
        
        ("Model-Down Fallback: ", 
         "Returns top 3 retrieved passages and available contact information with status='MODEL_UNAVAILABLE' on LLM 429 quota exhaustion or timeouts."),
        
        ("Custom Secrets Audit: ", 
         "Custom regex scanner (scripts/scan_git_secrets.py) confirmed 0 keys and 0 audio files across 151 commits. "
         "Certified tools (gitleaks/trufflehog) are not installed on the system. Fresh clone verification is pending.")
    ]
    for bold_prefix, text in features:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(3)
        r_bold = bp.add_run(bold_prefix); r_bold.font.bold = True; r_bold.font.color.rgb = PRIMARY
        bp.add_run(text)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. Corpus Composition & OCR Disagreements
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Corpus Composition & OCR Disagreements")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph(
        "Explanation of 4,449 Points in Qdrant: In the collection 'pakkam_chitra', there are exactly 4,449 points, "
        "each holding 1 chunk (chunk_id) indexed across all 18 official policy documents (2,688 pages). "
        "The earlier mention of '2,918 chunks' was an outdated count from an intermediate indexing step. "
        "The final index contains 4,449 chunks."
    )
    p.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph(
        "Meaning of the 263 OCR Disagreement Rows: Each row in docs/review/ocr_disagreements.csv represents a single page where the set "
        "of numbers extracted by Tesseract differed from the set extracted by Chitrapathak-2 Crop Mode. "
        "For example, in Row 14 (tn-hedu-policy-note-2024-ta, page 33, Pudhumai Penn scheme): Tesseract extracted '4000' "
        "(reading 'ரூ.1,000' as 4000), while Chitrapathak-2 Crop Mode extracted '1000'. "
        "The 263 rows represent pages requiring individual manual verification."
    )
    p.paragraph_format.space_after = Pt(8)

    # 4. Quantitative Benchmarks Table
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Quantitative Benchmarks & Evaluation Scope")
    r.font.color.rgb = PRIMARY

    b_table = doc.add_table(rows=1, cols=4)
    b_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = b_table.rows[0].cells
    hdr[0].width, hdr[1].width, hdr[2].width, hdr[3].width = Inches(1.8), Inches(2.1), Inches(1.3), Inches(1.3)
    
    headers = ["Benchmark Area", "Script & Sample Size", "Result", "Baseline & Scope Notes"]
    for i, h in enumerate(headers):
        set_cell_background(hdr[i], "1A365D")
        set_cell_margins(hdr[i], 60, 60, 80, 80)
        p_hdr = hdr[i].paragraphs[0]
        r_hdr = p_hdr.add_run(h); r_hdr.font.bold = True; r_hdr.font.size = Pt(8.5); r_hdr.font.color.rgb = RGBColor(255, 255, 255)

    bench_rows = [
        ("Hybrid OCR Problem Pages", "scripts/run_hybrid_ocr.py\n(n=7 cherry-picked pages)", "Chitrapathak-2: 7/7 (100%)\nTesseract: 0/7 (0%)", "Selection bias: 7 pages chosen because Tesseract failed; not a corpus-wide sample."),
        ("OCR Crop Speedup", "scripts/run_hybrid_ocr.py\n(n=500 currency pages)", "~12.0s per page (Crop Mode)", "Full-page GPU was ~95s. Earlier 6-7 min/page was on GPU; difference with ~95s is unreconciled without log."),
        ("Retrieval Recall@5", "scripts/ablate_retrieval.py\n(n=194 draft queries)", "Hybrid + Reranker: 98.7%\nHybrid alone: 94.8%", "Evaluated on draft questions only; no blind held-out set."),
        ("Refusal Routing (0.35)", "scripts/evaluate_refusal_curve.py\n(n=194 draft queries)", "87.1% Overall Accuracy\n92.5% Unanswerables Refused", "14.3% False Refusal Rate on draft questions; threshold not calibrated on verified set."),
        ("Fact Cards Precision", "scripts/fact_card_eval.py\n(n=4 positive, 40 unanswerables)", "100.0% Precision (4/4)\n0 False Positives (0/40)", "Tested on 2 AI draft cards. Unverified cards filtered out (verified_by: null)."),
        ("Speech Error Retrieval", "scripts/speech_error_test.py\n(n=31 clips: 15 TA, 15 HI, 1 synth)", "Doc Match: 90.3% (28/31)\nPage Match: 87.1% (27/31)", "Read-speech news only. Measures match against clean reference retrieval. Tanglish/conversational untested."),
        ("STT Word Error Rate", "Gnani Prisma REST\n(n=15 Tamil, n=15 Hindi)", "Tamil: Raw 5.2% (Norm 1.7%)\nHindi: Raw 3.7% (Norm 1.7%)", "Clean read speech only. 'Norm' strips punctuation/spaces. Identical 1.7% is coincidental rounding (1.72% vs 1.68%)."),
        ("Custom Secrets Audit", "scripts/scan_git_secrets.py\n(n=151 commits, 239 files)", "0 Secrets Detected\n0 Audio Files in Git", "Custom Python regex scan. Gitleaks unavailable. Fresh clone test pending.")
    ]

    for b_idx, (c0, c1, c2, c3) in enumerate(bench_rows):
        row = b_table.add_row()
        cells = row.cells
        cells[0].width, cells[1].width, cells[2].width, cells[3].width = Inches(1.8), Inches(2.1), Inches(1.3), Inches(1.3)
        bg_col = "FFFFFF" if b_idx % 2 == 0 else "F7FAFC"
        for c in cells:
            set_cell_background(c, bg_col)
            set_cell_margins(c, 40, 40, 60, 60)
        cells[0].paragraphs[0].add_run(c0).font.bold = True; cells[0].paragraphs[0].runs[0].font.size = Pt(8)
        cells[1].paragraphs[0].add_run(c1).font.size = Pt(7.5); cells[1].paragraphs[0].runs[0].font.color.rgb = MUTED_TEXT
        cells[2].paragraphs[0].add_run(c2).font.size = Pt(8); cells[2].paragraphs[0].runs[0].font.bold = True
        cells[3].paragraphs[0].add_run(c3).font.size = Pt(7.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 5. Guardrail Mechanics & needs_confirmation Specification
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Confirmation Guardrail Mechanics & Proposal")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph()
    r_cur = p.add_run("Current Implementation: ")
    r_cur.font.bold = True
    p.add_run(
        "In src/schemebot/generate/answer.py, needs_confirmation=True fires statically if voice_mode=True and either: "
        "(a) the generated answer contains any digit (\\d), or "
        "(b) the question string matches any known scheme keyword (e.g. 'pm kisan', 'kmut', 'pudhumai penn'). "
        "This heuristic prevents silent numerical action but currently lacks probabilistic nuance."
    )
    p.paragraph_format.space_after = Pt(3)

    p_prop = doc.add_paragraph()
    r_pr = p_prop.add_run("Proposed Uncertainty-Based Rule (Not Yet Implemented): ")
    r_pr.font.bold = True
    p_prop.add_run(
        "Instead of firing on all numbers, trigger confirmation only under measured ambiguity: "
        "(1) Margin retrieval confidence where top chunk score is near threshold (0.35 <= score < 0.45); "
        "(2) STT transcript character count is dangerously short (<15 characters); or "
        "(3) Acoustic token confidence is below 0.70 (if/when supported by the STT provider). "
        "Status: Proposal only; no code changes made in this step."
    )
    p_prop.paragraph_format.space_after = Pt(8)

    # 6. Speech-to-Text Benchmark Details
    h1 = doc.add_heading(level=1)
    r = h1.add_run("6. STT Word Error Rate Details (Kathbath Read Speech)")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph(
        "Evaluated via scripts/gnani_stt_eval.py on clean read speech from AI4Bharat Kathbath (news text recordings):"
    )
    p.paragraph_format.space_after = Pt(3)

    stt_items = [
        ("Tamil (n=15 read clips): ", "Raw WER 5.2%, Normalized WER 1.7%, Median Latency 0.95s."),
        ("Hindi (n=15 read clips): ", "Raw WER 3.7%, Normalized WER 1.7%, Median Latency 0.92s."),
        ("Definition of 'Norm': ", "Normalized WER applies Unicode NFC normalization, lowercasing, punctuation removal (commas, periods, question marks, dashes), whitespace collapsing, and zero-width character removal."),
        ("Why 1.7% appears identical: ", "Across the 15 Tamil clips, raw WER of 5.2% reduced to 1.72% after stripping punctuation and whitespace. Across the 15 Hindi clips, raw WER of 3.7% reduced to 1.68%. Both round to 1.7% at one decimal place; they are not identical raw outputs.")
    ]
    for b_prefix, b_text in stt_items:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r_b = bp.add_run(b_prefix); r_b.font.bold = True; r_b.font.color.rgb = PRIMARY
        bp.add_run(b_text)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 7. Departmental Contacts & Helplines Audit
    h1 = doc.add_heading(level=1)
    r = h1.add_run("7. Departmental Helplines Audit (data/contacts.json)")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph("Audit of all 10 cataloged public schemes in data/contacts.json (no numbers added from memory):")
    p.paragraph_format.space_after = Pt(3)

    c_table = doc.add_table(rows=1, cols=4)
    c_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = c_table.rows[0].cells
    hdr[0].width, hdr[1].width, hdr[2].width, hdr[3].width = Inches(2.2), Inches(1.3), Inches(1.8), Inches(1.2)
    for i, h in enumerate(["Scheme Name", "Helpline Number", "Official Source URL / Citation", "Verification Status"]):
        set_cell_background(hdr[i], "1A365D")
        set_cell_margins(hdr[i], 50, 50, 70, 70)
        p_hdr = hdr[i].paragraphs[0]
        r_hdr = p_hdr.add_run(h); r_hdr.font.bold = True; r_hdr.font.size = Pt(8); r_hdr.font.color.rgb = RGBColor(255, 255, 255)

    schemes = [
        ("Atal Pension Yojana", "1800 1100 69", "apy-brochure-en:p1 / https://www.pfrda.org.in", "Found in brochure, current number to be confirmed by a person"),
        ("PM-KISAN", "None listed", "https://pmkisan.gov.in", "Unverified (helpline null)"),
        ("PM Ujjwala Yojana", "None listed", "https://www.pmuy.gov.in", "Unverified (helpline null)"),
        ("Kalaignar Magalir Urimai Thittam", "None listed", "https://kmut.tn.gov.in", "Unverified (helpline null)"),
        ("Chief Minister's Breakfast Scheme", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)"),
        ("TN Social Welfare Schemes", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)"),
        ("TN Health & Family Welfare", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)"),
        ("TN Higher Education Schemes", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)"),
        ("TN Adi Dravidar & Tribal Welfare", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)"),
        ("TN BC, MBC & Minorities Welfare", "None listed", "https://www.tn.gov.in", "Unverified (helpline null)")
    ]
    for s_idx, (sc0, sc1, sc2, sc3) in enumerate(schemes):
        row = c_table.add_row()
        cells = row.cells
        cells[0].width, cells[1].width, cells[2].width, cells[3].width = Inches(2.2), Inches(1.3), Inches(1.8), Inches(1.2)
        bg_col = "FFFFFF" if s_idx % 2 == 0 else "F7FAFC"
        for c in cells:
            set_cell_background(c, bg_col)
            set_cell_margins(c, 30, 30, 50, 50)
        cells[0].paragraphs[0].add_run(sc0).font.bold = True; cells[0].paragraphs[0].runs[0].font.size = Pt(7.5)
        cells[1].paragraphs[0].add_run(sc1).font.size = Pt(7.5)
        cells[2].paragraphs[0].add_run(sc2).font.size = Pt(7); cells[2].paragraphs[0].runs[0].font.color.rgb = MUTED_TEXT
        cells[3].paragraphs[0].add_run(sc3).font.size = Pt(7.5)
        if "Unverified" in sc3:
            cells[3].paragraphs[0].runs[0].font.color.rgb = WARNING_TEXT
        else:
            cells[3].paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 8. Quota Diagnostics & Sample Answers
    h1 = doc.add_heading(level=1)
    r = h1.add_run("8. Operational Notes: Quota Reset & Sample Answers")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph()
    r_q = p.add_run("Gemini Quota Reset Window: ")
    r_q.font.bold = True
    p.add_run(
        "The daily reset time for the Gemini Free Tier is unverified. "
        "There is no official SLA guaranteeing a specific reset hour."
    )
    p.paragraph_format.space_after = Pt(3)

    p_ans = doc.add_paragraph()
    r_an = p_ans.add_run("Sample Answers Status: ")
    r_an.font.bold = True
    p_ans.add_run(
        "The 10 sample queries compiled in docs/review/sample_answers.md have been printed from model runs "
        "and manually inspected for format, but have NOT been formally scored by an independent person using a blind rubric. "
        "Official human grading remains pending under Phase 0.3."
    )
    p_ans.paragraph_format.space_after = Pt(10)

    # 9. Conclusion & Release Gate Check
    h1 = doc.add_heading(level=1)
    r = h1.add_run("9. Release Gate Check & Conclusion")
    r.font.color.rgb = PRIMARY

    p_gate = doc.add_paragraph()
    r_gt = p_gate.add_run("BRANCH IS NOT READY FOR PUSH TO GITHUB REMOTE.\n")
    r_gt.font.bold = True
    r_gt.font.size = Pt(9.5)
    r_gt.font.color.rgb = WARNING_TEXT
    p_gate.add_run(
        "Under the strict Pakkam project rules, code must not be pushed or submitted until all claims are verified. "
        "The following gates remain unpassed:\n"
        "• Gate 0.2: Verified question set (50 checked questions + 30 held-out) is not yet delivered.\n"
        "• Gate 0.3: Blind human grading of answer_eval.csv is not yet completed.\n"
        "• Gate 1.4: Real conversational and Tanglish speech clips have not been collected or tested.\n"
        "• Gate 2.1: 263 OCR disagreement rows remain unreviewed.\n\n"
        "The codebase remains safe and functional locally on branch feat/prompt-pack-execution with all 55 unit tests passing. "
        "All updates in this document reflect the measured state and recorded limitations of the research prototype."
    )
    p_gate.paragraph_format.space_after = Pt(12)

    out_dir = "docs/review"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Pakkam_2.0_Comprehensive_Benchmark_and_Execution_Report.docx")
    doc.save(out_path)
    print(f"Successfully generated corrected DOCX report at: {out_path}")

if __name__ == "__main__":
    create_report()
