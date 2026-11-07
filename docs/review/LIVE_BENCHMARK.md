# Live benchmark (2026-11-03)

Questions sent to `https://pakkam-alpha.vercel.app` one at a time, as a visitor would. Times are end to end
(network, tunnel, search, answer writing, checks). Answers come from Gemini (free plan).

| Language | Answered (covered questions) | Cited a correct page | Refused when not covered | Busy | Median | p90 |
|---|---|---|---|---|---|---|
| English | 97% (38/39) | 100% (38/38) | 100% (10/10) | 0 | 9.3 s | 28.6 s |
| Tamil | 92% (35/38) | 94% (33/35) | 100% (10/10) | 0 | 4.8 s | 30.1 s |
| Hindi | 84% (32/38) | 100% (32/32) | 90% (9/10) | 0 | 4.4 s | 7.9 s |
| **All** | 91% (105/115) | 98% (103/105) | 97% (29/30) | 0 | 4.8 s | 28.6 s |

## To look at

- `q029` (hi) **missed** unsupported number_not_in_source: अटल पेंशन योजना में कितनी पेंशन मिलती है?
- `q031` (hi) **missed** not_in_documents: उज्ज्वला योजना में गैस कनेक्शन के लिए कौन पात्र है?
- `q036` (hi) **answered_uncovered** : पीएम किसान की अगली किस्त कब आएगी?
- `q066` (ta) **missed** unsupported not_supported: முதலமைச்சரின் மருத்துவக் காப்பீட்டுத் திட்டத்தில் சேர குடும்ப ஆண்டு வருமான வரம்பு என்ன?
- `q122` (en) **missed** not_in_documents: How much subsidy does TAHDCO give on a self-employment project?
- `q146` (ta) **missed** unsupported number_not_in_source: பிற்படுத்தப்பட்டோருக்கு விலையில்லா வீட்டுமனை பெற ஆண்டு வருமான வரம்பு என்ன?
- `q147` (ta) **missed** not_in_documents: பிற்படுத்தப்பட்டோர் பள்ளி விடுதி மாணவர்களுக்கு மாத உணவுக் கட்டணம் எவ்வளவு?
- `q159` (hi) **missed** unsupported not_supported: तमिलनाडु की विधवा पुनर्विवाह सहायता योजना में उम्र की शर्तें क्या हैं?
- `q164` (hi) **missed** not_in_documents: टीएएचडीसीओ स्वरोजगार परियोजना पर कितनी सब्सिडी देता है?
- `q168` (hi) **missed** not_in_documents: पिछड़े वर्ग के स्कूल छात्रावास में छात्रों के लिए मासिक भोजन शुल्क कितना है?
- `q169` (hi) **missed** unsupported not_supported: पिछड़े वर्ग के छात्रावास के छात्रों को कितने सेट यूनिफॉर्म मिलते हैं?

Raw replies: `data/eval/live_benchmark.json`. Questions: `data/eval/questions.jsonl`
(the reference answers are drafts; correctness of wording is graded separately).
