# Speech Error & Language Table (BhashaShield)

Generated: 2026-10-28 17:27:44
Script: `scripts/speech_error_test.py`
Evaluation Set: Kathbath Read Speech Sample (Tamil n=15, Hindi n=15, Total n=31)

---

## 1. Summary Metrics

| Metric | Measured Value | Notes |
| :--- | :--- | :--- |
| **Total Audio Clips Tested** | **31** | 15 Tamil (`ta`), 15 Hindi (`hi`) |
| **STT WER (Tamil)** | **5.2% raw / 1.7% normalized** | Read speech, verified by `gnani_stt_eval.py` |
| **STT WER (Hindi)** | **3.7% raw / 1.7% normalized** | Read speech, verified by `gnani_stt_eval.py` |
| **Same Top Document Retrieval** | **28/31 (90.3%)** | Dense + sparse retrieval robustness |
| **Same Top Page Retrieval** | **27/31 (87.1%)** | Exact page match rate |
| **Number Survival Rate** | **0/0 (100.0%)** | Numerical digit retention |

---

## 2. Gnani Confidence Score Status
- **Public REST API Status**: The Gnani Prisma v2.5 REST API (`POST https://api.vachana.ai/stt/v3`) returns `{"success": true, "request_id": "...", "transcript": "..."}`.
- **Confidence Score**: Not returned in the public REST JSON response. BhashaShield relies on transcript length checks, digit verification, and scheme keyword matching.

---

## 3. BhashaShield Voice Confirmation Guardrails
1. **Empty / Noise Filter**: Transcripts < 5 characters return an immediate clarification message: *"Sorry, could not hear clearly. Please speak again or type your question."*
2. **Mandatory Confirmation Flag (`needs_confirmation=True`)**:
   - Triggers whenever a transcript contains digits/amounts or mentions a recognized government scheme.
   - The UI displays the recognized question text and prompts the citizen for confirmation before executing irrevocable actions.

---

## 4. Per-Clip Results Table

| File | Lang | WER | Reference Excerpt | Transcript Excerpt | Top Ref Target | Top Trans Target | Match? |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| `kathbath_ta_01.wav` | ta | 0.00 | திரையரங்கில் வைத்து கேமரா மூலம் இந்த இரு படங்களும்... | திரையரங்கில் வைத்து கேமரா மூலம் இந்த இரு படங்களும்... | `tn-hedu-policy-note-2024-ta:p102` | `tn-hedu-policy-note-2024-ta:p102` | ✅ |
| `kathbath_ta_02.wav` | ta | 0.00 | கணவன் மனைவி உறவில் விரிசல் வராமல் இருக்க மனைவியை ர... | கணவன் மனைவி உறவில் விரிசல் வராமல் இருக்க மனைவியை ர... | `tn-swwe-policy-note-2024-en:p47` | `tn-swwe-policy-note-2024-en:p47` | ✅ |
| `kathbath_ta_03.wav` | ta | 0.00 | ராயல் கடற்படை ஆய்வுக் கப்பலில் இளம் நேஷனல் ஸ்பிண்ட... | ராயல் கடற்படை ஆய்வுக் கப்பலில் இளம் நேஷனல் ஸ்பிண்ட... | `tn-hfw-policy-note-2024-en:p629` | `tn-hfw-policy-note-2024-en:p629` | ✅ |
| `kathbath_ta_04.wav` | ta | 0.08 | ரிச்சி இதற்காக பல ஆண்டுகள் ஜப்பானிலே வாழ்ந்து ஜப்ப... | ரிச்சி இதற்காக பல ஆண்டுகள் ஜப்பானிலே வாழ்ந்து ஜப்ப... | `tn-adtw-policy-note-2024-ta:p123` | `tn-hedu-policy-note-2024-ta:p107` | ❌ Diff |
| `kathbath_ta_05.wav` | ta | 0.00 | யுத்த காலத்தில் மனித உரிமை மீறப்பட்டதென்ற சர்வதேச ... | யுத்த காலத்தில் மனித உரிமை மீறப்பட்டதென்ற சர்வதேச ... | `tn-swwe-policy-note-2024-ta:p234` | `tn-swwe-policy-note-2024-ta:p234` | ✅ |
| `kathbath_ta_06.wav` | ta | 0.00 | கர்நாடகாவில் நடைபெற்று வரும் இடைத்தேர்தல் வாக்கு எ... | கர்நாடகாவில் நடைபெற்று வரும் இடைத்தேர்தல் வாக்கு எ... | `tn-hfw-policy-note-2024-en:p302` | `tn-hfw-policy-note-2024-en:p302` | ✅ |
| `kathbath_ta_07.wav` | ta | 0.08 | கிழக்கு மாகாணத்தின் ஆட்சி அதிகாரத்தை தமிழ்த் தேசிய... | கிழக்கு மாகாணத்தின் ஆட்சி அதிகாரத்தை தமிழ் தேசியக்... | `tn-hfw-policy-note-2024-en:p202` | `tn-hfw-policy-note-2024-en:p202` | ✅ |
| `kathbath_ta_08.wav` | ta | 0.12 | மூன்று இலங்கைத் தமிழர்களுக்கு ஆயுள் தண்டனை விதித்த... | மூன்று இலங்கை தமிழர்களுக்கு ஆயுள் தண்டனை விதித்த இ... | `tn-hfw-policy-note-2024-en:p283` | `tn-hfw-policy-note-2024-ta:p252` | ❌ Diff |
| `kathbath_ta_09.wav` | ta | 0.07 | திமுக தலைவர் கருணாநிதியின் மறைவிற்கு இரங்கல் தெரிவ... | திமுக தலைவர் கருணாநிதியின் மறைவிற்கு இரங்கல் தெரிவ... | `tn-bcmbc-policy-note-2024-ta:p106` | `tn-bcmbc-policy-note-2024-ta:p106` | ✅ |
| `kathbath_ta_10.wav` | ta | 0.17 | வரும் உள்ளாட்சி தேர்தல் பிரச்சாரங்களை முடித்தவுடன்... | வரும் உள்ளாட்சி தேர்தல் பிரச்சாரங்களை முடித்தவுடன்... | `cmbfs-go43-2022-ta:p4` | `cmbfs-go43-2022-ta:p4` | ✅ |
| `kathbath_ta_11.wav` | ta | 0.10 | பாரஸைட் படத்திற்காக சிறந்த இயக்குநர் விருதை தட்டிச... | பாரசைட் படத்திற்காக சிறந்த இயக்குநர் விருதை தட்டிச... | `tn-hfw-policy-note-2024-ta:p175` | `tn-hfw-policy-note-2024-ta:p175` | ✅ |
| `kathbath_ta_12.wav` | ta | 0.07 | அமெரிக்காவின் முன்னணி நிறுவனமான ஜெனரல் மோட்டார்ஸ் ... | அமெரிக்காவின் முன்னணி நிறுவனமான ஜெனரல் மோட்டார்ஸ் ... | `tn-hfw-policy-note-2024-ta:p542` | `tn-hedu-policy-note-2024-ta:p20` | ❌ Diff |
| `kathbath_ta_13.wav` | ta | 0.00 | ஜல்லிக்கட்டு நடத்திட அனுமதி பெற்றுத் தந்த முதலமைச்... | ஜல்லிக்கட்டு நடத்திட அனுமதி பெற்றுத் தந்த முதலமைச்... | `tn-bcmbc-policy-note-2024-ta:p105` | `tn-bcmbc-policy-note-2024-ta:p105` | ✅ |
| `kathbath_ta_14.wav` | ta | 0.00 | அப்பகுதி மக்கள் எந்த நேரமும் இங்கு வந்து தண்ணீர் ப... | அப்பகுதி மக்கள் எந்த நேரமும் இங்கு வந்து தண்ணீர் ப... | `tn-hfw-policy-note-2024-ta:p353` | `tn-hfw-policy-note-2024-ta:p353` | ✅ |
| `kathbath_ta_15.wav` | ta | 0.09 | இந்நிலையில் திங்கள்கிழமை வீட்டில் யாரும் இல்லாத நே... | இந்நிலையில் திங்கட்கிழமை வீட்டில் யாரும் இல்லாத நே... | `tn-hedu-policy-note-2024-ta:p121` | `tn-hedu-policy-note-2024-ta:p121` | ✅ |
| `kathbath_hi_01.wav` | hi | 0.00 | हमने ओबीसी तबके के बच्चों के लिए उच्च शिक्षा में आ... | हमने ओबीसी तबके के बच्चों के लिए उच्च शिक्षा में आ... | `tn-bcmbc-policy-note-2024-en:p13` | `tn-bcmbc-policy-note-2024-en:p13` | ✅ |
| `kathbath_hi_02.wav` | hi | 0.17 | उसको छोड़कर लोग इस प्रकार के मुद्दो पर चर्चा कर रह... | उसको छोड़कर लोग इस प्रकार के मुद्दों पर चर्चा कर र... | `tn-hedu-policy-note-2024-ta:p95` | `tn-hedu-policy-note-2024-ta:p95` | ✅ |
| `kathbath_hi_03.wav` | hi | 0.10 | उन्होंने कहा कि अतिथि अध्यापको को हटाना न्यायसंगत ... | उन्होंने कहा कि अतिथि अध्यापकों को हटाना न्यायसंगत... | `tn-bcmbc-policy-note-2024-ta:p15` | `tn-bcmbc-policy-note-2024-ta:p15` | ✅ |
| `kathbath_hi_04.wav` | hi | 0.00 | चीन में मोबाइल फोन की लत एक युवती को बड़ी मुश्किल ... | चीन में मोबाइल फोन की लत एक युवती को बड़ी मुश्किल ... | `tn-hedu-policy-note-2024-ta:p120` | `tn-hedu-policy-note-2024-ta:p120` | ✅ |
| `kathbath_hi_05.wav` | hi | 0.00 | मगर साथ में मनपसंद साथी हो तो मेहनत भी रास आती है | मगर साथ में मनपसंद साथी हो तो मेहनत भी रास आती है | `tn-bcmbc-policy-note-2024-en:p4` | `tn-bcmbc-policy-note-2024-en:p4` | ✅ |
| `kathbath_hi_06.wav` | hi | 0.00 | यह स्पष्ट नहीं है कि अन्नाद्रमुक कितने सीटों पर चु... | यह स्पष्ट नहीं है कि अन्नाद्रमुक कितने सीटों पर चु... | `tn-hfw-policy-note-2024-en:p210` | `tn-hfw-policy-note-2024-en:p210` | ✅ |
| `kathbath_hi_07.wav` | hi | 0.00 | ऐसे में फिल्म रिलीज के लिए अवसर बहुत सीमित हो जाते... | ऐसे में फिल्म रिलीज के लिए अवसर बहुत सीमित हो जाते... | `tn-adtw-policy-note-2024-ta:p155` | `tn-adtw-policy-note-2024-ta:p155` | ✅ |
| `kathbath_hi_08.wav` | hi | 0.13 | वैल कुछ फैंस का कहना है रणबीर कपूर नहीं चाहते थे क... | वेल कुछ फैंस का कहना है रणबीर कपूर नहीं चाहते थे क... | `tn-hfw-policy-note-2024-ta:p49` | `tn-hfw-policy-note-2024-ta:p49` | ✅ |
| `kathbath_hi_09.wav` | hi | 0.00 | वे जॉन अब्राहम निर्मित बनाना का निर्देशन कर रहे है... | वे जॉन अब्राहम निर्मित बनाना का निर्देशन कर रहे है... | `tn-adtw-policy-note-2024-ta:p59` | `tn-adtw-policy-note-2024-ta:p59` | ✅ |
| `kathbath_hi_10.wav` | hi | 0.07 | हम तैयार किए गए चीबरेक्स प्राप्त करेंगे और उन्हें ... | हम तैयार किए गए चीब्रेक्स प्राप्त करेंगे और उन्हें... | `tn-hfw-policy-note-2024-en:p465` | `tn-hfw-policy-note-2024-en:p465` | ✅ |
| `kathbath_hi_11.wav` | hi | 0.00 | कुंभ में बारिश ने तीर्थयात्रियों को किया हलकान | कुंभ में बारिश ने तीर्थयात्रियों को किया हलकान | `tn-hfw-policy-note-2024-en:p389` | `tn-hfw-policy-note-2024-en:p389` | ✅ |
| `kathbath_hi_12.wav` | hi | 0.08 | पार्टी के तीन सचिवों ने अपने पदों से इस्तीफा दे दि... | पार्टी के 3 सचिवों ने अपने पदों से इस्तीफा दे दिया... | `cmbfs-go43-2022-ta:p17` | `cmbfs-go43-2022-ta:p8` | ⚠️ Doc only |
| `kathbath_hi_13.wav` | hi | 0.00 | अब फाइनल बोर्ड परीक्षाओं के लिए भी छात्रों ने कमर ... | अब फाइनल बोर्ड परीक्षाओं के लिए भी छात्रों ने कमर ... | `tn-adtw-policy-note-2024-en:p139` | `tn-adtw-policy-note-2024-en:p139` | ✅ |
| `kathbath_hi_14.wav` | hi | 0.00 | मुझे मालूम हुआ है कि उन्हें हटा दिया गया है | मुझे मालूम हुआ है कि उन्हें हटा दिया गया है | `tn-hedu-policy-note-2024-ta:p120` | `tn-hedu-policy-note-2024-ta:p120` | ✅ |
| `kathbath_hi_15.wav` | hi | 0.00 | ये तो पिछले दरवाजे से आए कुछ लोगों की साजिश है | ये तो पिछले दरवाजे से आए कुछ लोगों की साजिश है | `tn-swwe-policy-note-2024-en:p248` | `tn-swwe-policy-note-2024-en:p248` | ✅ |
| `synthetic_smoke_ta.wav` | ta | 0.00 | வணக்கம் இது ஒரு சோதனை ஒலி | வணக்கம் இது ஒரு சோதனை ஒலி | `tn-hfw-policy-note-2024-ta:p224` | `tn-hfw-policy-note-2024-ta:p224` | ✅ |
