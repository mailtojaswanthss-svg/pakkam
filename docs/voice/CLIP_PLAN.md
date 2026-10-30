# Pakkam 2.0 Field Audio Collection & Benchmark Plan

## 1. Purpose & Protocol
This plan outlines the protocol for collecting and evaluating **30 synthetic speech prompts** across Tamil, Tanglish, Hindi, and English.
These clips evaluate Gnani Prisma STT word error rate (WER) and end-to-end voice retrieval performance under real acoustic conditions (smartphone microphone, outdoor ambient noise, conversational cadence).

### Privacy & Ethics Protocol
- **Synthetic Prompts Only**: All audio recordings speak strictly synthetic or standardized public scheme questions. Zero personal citizen situations or personal identifiable information (PII) may be spoken.
- **Git Hygiene**: No raw `.wav` or `.mp3` files are ever committed to git. All recordings live under `data/voice/field_clips/` which is strictly `.gitignore`d.
- **Informed Consent**: Every volunteer speaker reads and signs/consents to the following text prior to recording:
  > *"I consent to my voice recording being used exclusively for evaluating the research prototype speech-recognition model for public government scheme information retrieval. My name and identity will not be published or linked to the recording, and no audio will be shared publicly or stored in public source code repositories."*

---

## 2. File Naming & Organization
Each audio file is recorded as 16 kHz mono WAV (or converted via `ffmpeg`) with the canonical name:
```
clip_{id:02d}_{lang}_{speaker_id}.wav
```
Example: `clip_01_ta_spk01.wav`, `clip_11_ta_latn_spk02.wav`.

All clips are stored in:
`data/voice/field_clips/`

---

## 3. Metadata Table Specification (`docs/voice/field_clips_metadata.csv`)
The companion file `docs/voice/field_clips_metadata.csv` maps every clip to its ground-truth reference text:

| Column | Description |
|---|---|
| `clip_id` | Identifier matching filename (e.g. `clip_01`) |
| `language` | Language code: `ta`, `ta-Latn`, `hi`, `en` |
| `speaker_id` | Anonymized speaker ID (e.g. `spk01`) |
| `environment` | Acoustic environment: `quiet_room`, `street_ambient`, `canteen` |
| `reference_text` | Exact ground-truth transcript spoken |
| `target_scheme` | Expected scheme: `APY`, `PM-KISAN`, `PMUY`, `KMUT`, `CMBS` |

---

## 4. The 30 Standardized Synthetic Prompts

### Tamil (Script: தமிழ், 8 Prompts)
1. `clip_01_ta`: அடல் பென்ஷன் திட்டத்தில் சேர வயது வரம்பு என்ன? (APY)
2. `clip_02_ta`: பிஎம் கிசான் திட்டத்தில் ஆண்டுக்கு எவ்வளவு உதவித்தொகை கிடைக்கும்? (PM-KISAN)
3. `clip_03_ta`: மகளிர் உரிமைத் திட்டத்திற்கு யார் விண்ணப்பிக்கலாம்? (KMUT)
4. `clip_04_ta`: உஜ்வாலா திட்டத்தில் இலவச கேஸ் இணைப்பு எப்படி பெறுவது? (PMUY)
5. `clip_05_ta`: முதலமைச்சரின் காலை உணவுத் திட்டம் எந்த வகுப்புகளுக்கு செயல்படுத்தப்படுகிறது? (CMBS)
6. `clip_06_ta`: விவசாயிகளுக்கு ஆண்டுக்கு ஆறாயிரம் ரூபாய் தரும் திட்டம் எது? (PM-KISAN)
7. `clip_07_ta`: கலைஞர் மகளிர் உரிமைத் தொகை வங்கி கணக்கில் எப்போது வரும்? (KMUT)
8. `clip_08_ta`: அறுபது வயதுக்கு மேல் மாதாந்திர பென்ஷன் தரும் திட்ட விவரம் சொல்லுங்கள். (APY)

### Tanglish (Tamil in Latin script, 8 Prompts)
9. `clip_09_ta_latn`: Atal Pension Yojana-la seruradhukku enna age limit? (APY)
10. `clip_10_ta_latn`: PM-KISAN thittathula varushathuku evlo kaasu varum? (PM-KISAN)
11. `clip_11_ta_latn`: Magalir Urimai Thogai eppo bank account-la kedaikkum? (KMUT)
12. `clip_12_ta_latn`: Ujjwala yojana-la free gas connection epdi apply panradhu? (PMUY)
13. `clip_13_ta_latn`: Government school pasangalukku breakfast scheme irukka? (CMBS)
14. `clip_14_ta_latn`: 60 age ku mela monthly pension varra scheme sollu. (APY)
15. `clip_15_ta_latn`: Enakku 2 ekar boomi irukku PM kisan apply panna mudiyuma? (PM-KISAN)
16. `clip_16_ta_latn`: Ration card irukura ponnukku 1000 rubai kedaikuma? (KMUT)

### Hindi (Script: देवनागरी, 7 Prompts)
17. `clip_17_hi`: अटल पेंशन योजना में न्यूनतम और अधिकतम आयु सीमा क्या है? (APY)
18. `clip_18_hi`: पीएम किसान सम्मान निधि में किसानों को साल में कितने पैसे मिलते हैं? (PM-KISAN)
19. `clip_19_hi`: प्रधानमंत्री उज्ज्वला योजना में मुफ्त गैस सिलेंडर कैसे प्राप्त करें? (PMUY)
20. `clip_20_hi`: अटल पेंशन योजना में साठ साल के बाद कितनी पेंशन मिलती है? (APY)
21. `clip_21_hi`: क्या दो हेक्टेयर से कम भूमि वाले किसान पीएम किसान के पात्र हैं? (PM-KISAN)
22. `clip_22_hi`: उज्ज्वला योजना के तहत पहला गैस चूल्हा मुफ्त मिलता है क्या? (PMUY)
23. `clip_23_hi`: पेंशन के लिए बैंक खाते में ऑटो डेबिट कैसे चालू करें? (APY)

### English (7 Prompts)
24. `clip_24_en`: What is the entry age limit for Atal Pension Yojana? (APY)
25. `clip_25_en`: How much financial assistance is provided annually under PM-KISAN? (PM-KISAN)
26. `clip_26_en`: Who is eligible for the Kalaignar Magalir Urimai scheme in Tamil Nadu? (KMUT)
27. `clip_27_en`: What are the documents required for Pradhan Mantri Ujjwala Yojana? (PMUY)
28. `clip_28_en`: Which classes of students are covered under Chief Minister Breakfast Scheme? (CMBS)
29. `clip_29_en`: Is there a monthly pension guaranteed after 60 years of age in APY? (APY)
30. `clip_30_en`: Can income tax payers apply for Kalaignar Magalir Urimai Thittam? (KMUT)
