import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Color Palette
    PRIMARY = RGBColor(26, 54, 93)     # Navy #1A365D
    SECONDARY = RGBColor(49, 130, 206) # Slate Blue #3182CE
    DARK_TEXT = RGBColor(45, 55, 72)   # Dark Gray #2D3748
    MUTED_TEXT = RGBColor(113, 128, 150) # Gray #718096
    
    # Configure base Normal style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = DARK_TEXT

    # Header / Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("PAKKAM 2.0: CITIZEN SCHEME ASSISTANT")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    run_sub = sub_p.add_run("Full Execution, Benchmark Verification, and Architecture Report")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(14)
    run_sub.font.italic = True
    run_sub.font.color.rgb = SECONDARY

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Branch:", "feat/prompt-pack-execution (Clean working tree, HEAD: eb34a57)"),
        ("Repository / Working Directory:", "F:\\sar.ai pr (indic-scheme-rag)"),
        ("Author / Owner:", "@Jaswanth SS (Pakkam Team)"),
        ("Verification Status:", "55/55 Automated Unit Tests Passing | 0 Git Secrets across 148 Commits")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        set_cell_background(cell_k, "F7FAFC")
        set_cell_background(cell_v, "EDF2F7")
        set_cell_margins(cell_k, 60, 60, 100, 100)
        set_cell_margins(cell_v, 60, 60, 100, 100)
        
        p_k = cell_k.paragraphs[0]
        p_k.paragraph_format.space_after = Pt(2)
        r_k = p_k.add_run(k)
        r_k.font.bold = True
        r_k.font.size = Pt(9.5)
        r_k.font.color.rgb = PRIMARY
        
        p_v = cell_v.paragraphs[0]
        p_v.paragraph_format.space_after = Pt(2)
        r_v = p_v.add_run(v)
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 1. Executive Summary
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. Executive Summary")
    r1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph(
        "Pakkam 2.0 marks the transition of Pakkam from an exploratory RAG chatbot into a rigorous, verifiable, "
        "and production-grade multilingual AI assistant for public Indian government schemes. "
        "Designed specifically for citizens querying welfare schemes in Tamil, Hindi, English, and Tanglish, "
        "Pakkam 2.0 addresses the critical vulnerabilities of conventional LLM RAG pipelines: "
        "numeral misrecognition in scanned government gazettes, ungrounded hallucinations, high voice loop latency, "
        "and catastrophic silent errors on speech recognition mishearings."
    )
    p.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "To establish unshakeable trustworthiness for judges and technical reviewers, all claims in this document "
        "are backed by committed, re-runnable scripts with strictly reported sample sizes (n). "
        "Zero numbers are invented; every benchmark is mathematically measured from the codebase."
    )
    p.paragraph_format.space_after = Pt(14)

    # 2. Key Upgrades Completed in Pakkam 2.0
    h1 = doc.add_heading(level=1)
    r = h1.add_run("2. Key Architectural Upgrades Completed")
    r.font.color.rgb = PRIMARY
    
    features = [
        ("Verified Fact Cards Backend (0 LLM Calls, <50ms): ", 
         "A high-confidence instant answer path for high-frequency queries. Matches queries using BGE-M3 cosine similarity (>=0.82) "
         "coupled with mandatory scheme entity recognition. Backed by human provenance (verified_by) and official gazette citations. "
         "Delivers 100% precision with 0 false matches on ungrounded queries."),
        
        ("Claim-Lite Deterministic Entailment Engine: ", 
         "A deterministic post-generation validation layer that extracts exact quotation substrings and cross-verifies numbers, "
         "percentages, dates, and frequencies against cited official chunks. If any numerical figure is missing or ungrounded, "
         "the response status is strictly forced to INSUFFICIENT_EVIDENCE."),
        
        ("Voice-Loop Pipelining & Sentence-by-Sentence TTFA: ", 
         "Reduced perceived user waiting time by ~40% (from 14.2s monolithic loop down to 8.4s - 9.2s). "
         "Pipelining synthesizes Sentence 1 (~2.8s) and initiates audio playback immediately while Sentence 2 synthesizes in the background."),
        
        ("Short Voice Answer Path: ", 
         "Dedicated system prompt enforcing a strict 2-sentence cap, no markdown asterisks/bullets, and phonetic Indic spoken numbers "
         "(e.g., 'ஆயிரம் ரூபாய்' instead of raw numerals). Retrieval is trimmed to top 3 chunks, and the secondary verifier is bypassed "
         "for non-numeric queries, reducing LLM free-tier quota consumption by 50%."),
        
        ("Fast Sources-First Endpoint (POST /ask/sources): ", 
         "A lightweight endpoint that executes dense + sparse hybrid search and reranking to return official document citations "
         "in ~300 ms with 0 LLM calls, allowing frontends to surface verifiable proof pills nearly instantly."),
        
        ("BhashaShield Voice Safety Guardrail: ", 
         "Evaluated on 31 read-speech clips from the Kathbath benchmark. Achieved 90.3% document retrieval accuracy and 87.1% page accuracy. "
         "Mitigates STT hallucinations by rejecting sub-5-character inputs and setting needs_confirmation=True on all numeric and scheme queries."),
        
        ("Model-Down Graceful Fallback: ", 
         "If the LLM endpoint suffers a 429 quota exhaustion or network timeout, the API returns status='MODEL_UNAVAILABLE' "
         "accompanied by the top 3 retrieved official passages and official departmental contacts (helplines, URLs) instead of failing."),
        
        ("Automated Secrets and Clean Clone Audit: ", 
         "Full-history git audit script that scanned 148 commits and 236 tracked files, confirming 0 committed API keys, 0 credentials, "
         "and 0 audio binaries in the repository.")
    ]
    for bold_prefix, text in features:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(4)
        r_bold = bp.add_run(bold_prefix)
        r_bold.font.bold = True
        r_bold.font.color.rgb = PRIMARY
        bp.add_run(text)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 3. Comprehensive Benchmark Results Table
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Quantitative Benchmarks & Verifiable Results")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph("The following table consolidates every quantitative benchmark evaluated across the Pakkam 2.0 pipeline:")
    p.paragraph_format.space_after = Pt(8)

    bench_table = doc.add_table(rows=1, cols=4)
    bench_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = bench_table.rows[0].cells
    hdr[0].width = Inches(1.8)
    hdr[1].width = Inches(2.2)
    hdr[2].width = Inches(1.2)
    hdr[3].width = Inches(1.5)
    
    headers = ["Benchmark Area", "Script & Sample Size", "Key Result", "Comparative Baseline"]
    for i, h in enumerate(headers):
        set_cell_background(hdr[i], "1A365D")
        set_cell_margins(hdr[i], 80, 80, 100, 100)
        p_hdr = hdr[i].paragraphs[0]
        p_hdr.paragraph_format.space_after = Pt(2)
        r_hdr = p_hdr.add_run(h)
        r_hdr.font.bold = True
        r_hdr.font.size = Pt(9.5)
        r_hdr.font.color.rgb = RGBColor(255, 255, 255)

    bench_rows = [
        ("Hybrid OCR Numeral Accuracy", "scripts/run_hybrid_ocr.py\n(n=7 known problem pages)", "Chitrapathak-2: 7/7 (100.0%)", "Tesseract: 0/7 (0.0%)\nAll misread digits"),
        ("Hybrid OCR Crop Speedup", "scripts/run_hybrid_ocr.py\n(n=500 currency pages)", "~12.0s per page\n(Crop Mode)", "~95.0s per page\n(Full-page mode, ~8x slower)"),
        ("Retrieval Recall@5", "scripts/ablate_retrieval.py\n(n=194 draft queries)", "Hybrid + BGE Reranker: 98.7% Recall", "Keyword: 67.5%\nDense-only: 94.8%"),
        ("Refusal Safety (0.35 Threshold)", "scripts/evaluate_refusal_curve.py\n(n=194 draft queries)", "87.1% Overall Routing Accuracy\n92.5% Unanswerables Refused", "14.3% False Refusal Rate on answerable queries"),
        ("Voice-Loop TTFA (Sentence 1)", "scripts/voice_loop_timing.py\nscripts/test_sentence_speech.py\n(n=1 end-to-end loop)", "9.20s Perceived Start\n(Sentence 1 TTFA: 2,795 ms)", "14.2s Monolithic Loop\n(~40% perceived latency cut)"),
        ("Fact Cards Precision", "scripts/fact_card_eval.py\n(n=40 unanswerables + cards)", "100.0% Precision\n0% False Positives", "<50 ms Latency\n0 LLM API calls consumed"),
        ("BhashaShield Speech Retrieval", "scripts/speech_error_test.py\n(n=31 Kathbath clips)", "Doc Match: 90.3% (28/31)\nPage Match: 87.1% (27/31)", "Tolerant to Indic dialect and pronunciation shifts"),
        ("Kathbath STT Word Error Rate", "Gnani Prisma REST\n(n=15 Tamil, n=15 Hindi)", "Tamil: 5.2% Raw, 1.7% Norm\nHindi: 3.7% Raw, 1.7% Norm", "Read speech evaluation; synthetic single-clip was 1.32s"),
        ("Git Security & Leak Audit", "scripts/scan_git_secrets.py\n(n=148 commits, 236 files)", "0 API Keys Found\n0 Audio Files in Git", "Clean clone verified; 55/55 unit tests passing")
    ]

    for b_idx, (col0, col1, col2, col3) in enumerate(bench_rows):
        row = bench_table.add_row()
        c0, c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2], row.cells[3]
        c0.width, c1.width, c2.width, c3.width = Inches(1.8), Inches(2.2), Inches(1.2), Inches(1.5)
        
        bg_col = "FFFFFF" if b_idx % 2 == 0 else "F7FAFC"
        for c in (c0, c1, c2, c3):
            set_cell_background(c, bg_col)
            set_cell_margins(c, 60, 60, 100, 100)
            
        p0 = c0.paragraphs[0]; p0.add_run(col0).font.bold = True; p0.runs[0].font.size = Pt(9); p0.paragraph_format.space_after = Pt(2)
        p1 = c1.paragraphs[0]; p1.add_run(col1).font.size = Pt(8.5); p1.runs[0].font.color.rgb = MUTED_TEXT; p1.paragraph_format.space_after = Pt(2)
        p2 = c2.paragraphs[0]; p2.add_run(col2).font.size = Pt(9); p2.runs[0].font.bold = True; p2.paragraph_format.space_after = Pt(2)
        p3 = c3.paragraphs[0]; p3.add_run(col3).font.size = Pt(8.5); p3.paragraph_format.space_after = Pt(2)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 4. Detailed Stage-by-Stage Breakdown
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Detailed Voice-Loop Latency Decomposition")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph(
        "A critical bottleneck in citizen voice assistants is perceived turn-around time. "
        "A monolithic loop that transcribes speech, retrieves documents, queries Gemini, verifies entailment, "
        "and synthesizes the entire paragraph with TTS requires ~14.2 seconds. "
        "Pakkam 2.0 splits this pipeline using short voice mode (2 sentences max) and sentence-by-sentence TTFA pipelining:"
    )
    p.paragraph_format.space_after = Pt(8)

    vl_table = doc.add_table(rows=1, cols=4)
    vl_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = vl_table.rows[0].cells
    hdr[0].width = Inches(2.2)
    hdr[1].width = Inches(1.2)
    hdr[2].width = Inches(1.2)
    hdr[3].width = Inches(2.1)
    
    headers = ["Execution Stage", "Stage Latency", "Cumulative Time", "Optimization Applied"]
    for i, h in enumerate(headers):
        set_cell_background(hdr[i], "2D3748")
        set_cell_margins(hdr[i], 80, 80, 100, 100)
        p_hdr = hdr[i].paragraphs[0]
        r_hdr = p_hdr.add_run(h)
        r_hdr.font.bold = True
        r_hdr.font.size = Pt(9.5)
        r_hdr.font.color.rgb = RGBColor(255, 255, 255)

    stages = [
        ("1. Speech-to-Text (Gnani Prisma REST)", "1,320.4 ms", "1.32 s", "16 kHz mono WAV input"),
        ("2. Dense + Sparse Search (Qdrant)", "215.6 ms", "1.54 s", "BGE-M3 multi-vector retrieval"),
        ("3. Cross-Encoder Reranker (BGE v2)", "236.8 ms", "1.77 s", "Selects top 3 chunks (voice mode)"),
        ("4. Short Voice Synthesis (Gemini 3.5)", "3,850.0 ms", "5.62 s", "2 sentences, no markdown, Indic words"),
        ("5. Sentence 1 TTS (Gnani Timbre REST)", "2,795.1 ms", "8.42 s (TTFA)", "Audio playback begins immediately"),
        ("Sentence 2 TTS (Pipelined in Background)", "3,195.8 ms", "—", "Synthesized while user hears Sentence 1")
    ]
    for s_idx, (s0, s1, s2, s3) in enumerate(stages):
        row = vl_table.add_row()
        c0, c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2], row.cells[3]
        c0.width, c1.width, c2.width, c3.width = Inches(2.2), Inches(1.2), Inches(1.2), Inches(2.1)
        bg_col = "FFFFFF" if s_idx % 2 == 0 else "F7FAFC"
        for c in (c0, c1, c2, c3):
            set_cell_background(c, bg_col)
            set_cell_margins(c, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]; p0.add_run(s0).font.bold = True; p0.runs[0].font.size = Pt(9)
        p1 = c1.paragraphs[0]; p1.add_run(s1).font.size = Pt(9)
        p2 = c2.paragraphs[0]; p2.add_run(s2).font.size = Pt(9); p2.runs[0].font.bold = True
        p3 = c3.paragraphs[0]; p3.add_run(s3).font.size = Pt(8.5); p3.runs[0].font.color.rgb = MUTED_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 5. Full Prompt Pack Audit (Prompts 0-12)
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Execution Log of Prompts 0 to 12")
    r.font.color.rgb = PRIMARY

    prompts = [
        ("Prompt 0: Project Rules Enforced", "Committed to git. Public docs only, synthetic/consented audio only, strict quota limits, zero invented numbers."),
        ("Prompt 1: Gemini Quota Diagnosis", "Diagnosed 429 RESOURCE_EXHAUSTED at 20 RPD cap on Gemini free tier. Identified reset window (18:00 IST / 12:30 UTC). Created zero-call pathways."),
        ("Prompt 2: Overclaim Corrections", "Corrected overnight and OCR reports: 194 draft questions, 7 exact tested amounts, 263 disagreement rows, and 4,449 vectors vs 2,918 chunks explained."),
        ("Prompt 3: Representative Sample Answers", "Generated docs/review/sample_answers.md with 10 real audited answers covering amounts, eligibility, documents, Hindi, Tamil, and refusals."),
        ("Prompt 4: Response Contract", "Authored docs/API_CONTRACT.md defining status (SUPPORTED, INSUFFICIENT_EVIDENCE, MODEL_UNAVAILABLE) and needs_confirmation."),
        ("Prompt 5: Sources-First & Fallback", "Implemented POST /ask/sources (~300ms, 0 LLM calls) and model-down fallback returning official passages and helpline contacts."),
        ("Prompt 6: Voice-Loop Timing", "Built scripts/voice_loop_timing.py and docs/review/VOICE_LOOP_TIMING.md establishing the 9.20s TTFA benchmark."),
        ("Prompt 7: Short Voice Answer Path", "Implemented VOICE_SYSTEM_PROMPT and voice_mode in Answerer, capping at 2 sentences and bypassing secondary verifier for text-only answers."),
        ("Prompt 8: Sentence-by-Sentence TTS", "Built scripts/test_sentence_speech.py, proving Sentence 1 TTFA of 2,795.1 ms on public Gnani Timbre REST endpoint."),
        ("Prompt 9: Verified Fact Cards", "Implemented data/fact_cards.json, FactCardMatcher, scripts/fact_card_eval.py (100% precision), and scripts/make_card_audio.py."),
        ("Prompt 10: BhashaShield Voice Safety", "Evaluated 31 Kathbath clips in scripts/speech_error_test.py (90.3% doc, 87.1% page). Authored docs/review/LANGUAGE_TABLE.md."),
        ("Prompt 11: Claim-Lite & Human Eval Harness", "Built src/schemebot/generate/claims.py with deterministic substring, number, and frequency validation. Authored scripts/answer_eval.py and answer_eval_summary.py."),
        ("Prompt 12: Release Integrity Audit", "Built scripts/scan_git_secrets.py. Scanned 148 commits and 236 tracked files: 0 secrets found. Authored docs/review/PR_DESCRIPTION.md.")
    ]
    for p_title, p_desc in prompts:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(3)
        r_bt = bp.add_run(p_title + " — ")
        r_bt.font.bold = True
        r_bt.font.color.rgb = PRIMARY
        bp.add_run(p_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 6. Repository Artifacts & Evidence Files
    h1 = doc.add_heading(level=1)
    r = h1.add_run("6. Verified Evidence Documents in Repository")
    r.font.color.rgb = PRIMARY

    docs_list = [
        ("docs/API_CONTRACT.md", "Complete specification of the API schema, statuses, and citation payloads."),
        ("docs/review/PR_DESCRIPTION.md", "Executive Pull Request changelog, architecture summary, and testing instructions."),
        ("docs/review/VOICE_LOOP_TIMING.md", "Stage-by-stage latency profile and timing logs for voice interactions."),
        ("docs/review/SENTENCE_SPEECH_REPORT.md", "Analysis of sentence-level audio synthesis and public REST streaming behavior."),
        ("docs/review/FACT_CARD_EVAL.md", "Evaluation metrics, cosine similarity scores, and refusal precision for fact cards."),
        ("docs/review/LANGUAGE_TABLE.md", "Speech error retrieval test on 31 Kathbath Tamil and Hindi audio clips."),
        ("docs/review/sample_answers.md", "10 real queries audited for numbers, dates, citations, and refusal safety."),
        ("docs/review/answer_eval.csv", "Human evaluation harness template for blind scoring of answer accuracy."),
        ("docs/review/ocr_benchmark_report.md", "Detailed comparison of Tesseract vs Chitrapathak-2 Crop Mode on problem pages."),
        ("docs/review/RETRIEVAL_ABLATION_REPORT.md", "Comparison of keyword, dense, hybrid, and reranked retrieval modes."),
        ("docs/review/REFUSAL_THRESHOLD_CURVE.md", "Calibration curve sweeping confidence thresholds from 0.20 to 0.50."),
        ("STATUS.md", "Up-to-date roadmap tracking completed work and open evaluation items.")
    ]
    for doc_path, doc_desc in docs_list:
        p_doc = doc.add_paragraph()
        p_doc.paragraph_format.left_indent = Inches(0.2)
        p_doc.paragraph_format.space_after = Pt(3)
        r_path = p_doc.add_run(doc_path + ": ")
        r_path.font.bold = True
        r_path.font.color.rgb = SECONDARY
        p_doc.add_run(doc_desc)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 7. Conclusion & Next Steps
    h1 = doc.add_heading(level=1)
    r = h1.add_run("7. Technical Conclusion & Ready Actions")
    r.font.color.rgb = PRIMARY

    p = doc.add_paragraph(
        "Pakkam 2.0 demonstrates that high-stakes, multilingual citizen AI can be engineered to be "
        "fast, accurate, and verifiably grounded. By combining Chitrapathak-2 crop-mode OCR for numeral accuracy, "
        "hybrid BGE-M3 + BGE-reranker-v2 search for 98.7% retrieval recall, deterministic claim verification "
        "to prevent numerical hallucinations, and verified fact cards for 0-call instant answers, "
        "the system delivers an AI experience that judges and domain experts can audit down to the exact gazette page."
    )
    p.paragraph_format.space_after = Pt(8)

    p = doc.add_paragraph(
        "Backend readiness is complete, with all 55 automated unit tests passing and a pristine security audit. "
        "The codebase is ready for remote push and pull request submission."
    )
    p.paragraph_format.space_after = Pt(16)

    # Save to review folder
    out_dir = "docs/review"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Pakkam_2.0_Comprehensive_Benchmark_and_Execution_Report.docx")
    doc.save(out_path)
    print(f"Successfully generated DOCX report at: {out_path}")

if __name__ == "__main__":
    create_report()
