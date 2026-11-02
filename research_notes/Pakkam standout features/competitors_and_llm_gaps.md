# Competitors to Pakkam and Where General LLM Assistants Fall Short (India welfare-scheme access, as of Nov 2026)

Research date: 2026-11-02. Search was capped at about 18 tool calls. Most adoption numbers come from vendors or partners and have not been independently audited. Dates are noted wherever sources give them.

## Q1. What do existing products do (languages, channels, grounding/citations, accuracy evidence, adoption)?

### Takeaway
The field splits three ways:
- **Government portals and apps:** myScheme and UMANG. These are text-first and need a smartphone or web access.
- **Scheme-specific or state chatbots:** Kisan e-Mitra and Namma Arasu on WhatsApp. These cover one scheme or one menu of services.
- **Infrastructure and voice vendors:** Bhashini/VoicERA, Sarvam, Gnani. These sell building blocks or outbound calling rather than a citizen-facing Q&A product grounded in documents.

I found no competitor that publicly offers page-level citations to official scheme PDFs together with an explicit refusal policy and human-verified answer cards. Only Haqdarshak offers human accountability, through trained field agents, but it is not a self-serve voice line.

### Cited Findings

**Jugalbandi (AI4Bharat / Microsoft Research / OpenNyAI)**
- Launched in 2023 as a generative-AI WhatsApp chatbot. Users send text or voice messages. At launch it covered 10 of India's 22 official languages and 171 of roughly 20,000 government programmes. Models came from AI4Bharat and reasoning ran on Azure OpenAI. — [Microsoft Source Asia](https://news.microsoft.com/source/asia/features/with-help-from-next-generation-ai-indian-villagers-gain-easier-access-to-government-services/); [Business Standard / Reuters](https://business-standard.com/amp/technology/tech-news/microsoft-backed-group-aims-to-bridge-language-gap-with-ai-assistant-123052301059_1.html)
- Coverage at the time flagged the risk of incorrect information about benefits and procedures. It also flagged privacy concerns about plans to let the bot fill application forms. — [MediaNama 2023](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/)
- Thoughtworks describes v1 as covering more than 170 schemes and says it is now expanding to other sectors, which suggests a pivot towards a platform or framework. — [Thoughtworks](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/jugalbandi-building-ai-social-impact)
- A related MeitY/Bhashini WhatsApp bot built on ChatGPT models (2023) was fed about 170 schemes at more than 1,000 words each and tested in 12 languages. — [YourStory](https://yourstory.com/2023/02/meity-integrate-openai-chatgpt-whatsapp-farmer-govt-schemes); [MediaNama](https://www.medianama.com/2023/02/223-indian-govt-whatsapp-questions-chatgpt-bot/)

**Bhashini / VoicERA (MeitY)**
- Bhashini covers 36 text languages and 23 voice languages (Indian). It reports more than 800 government websites using it, more than 9 billion cumulative inferences and about 24 million inferences per day. These are self-reported figures. — [PIB doc Jan 2025](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/jan/doc2025116486101.pdf); [newkerala Oct 2026](https://www.newkerala.com/news/a/bhashini-deploys-real-time-multilingual-ai-translation-platform-international-931.htm)
- VoicERA is an open-source, end-to-end voice AI stack covering ASR, TTS, conversational AI and multilingual telephony on Bhashini. It was unveiled at the India AI Impact Summit in February 2026, aimed at helplines, grievance redressal, agriculture advisories and scheme discovery. Partners are EkStep, IIIT Bengaluru and AI4Bharat. No deployment numbers or language list were published. — [Angel One / news, 19 Feb 2026](https://www.angelone.in/news/economy/voicera-on-bhashini-govt-services-helpline-will-now-speak-in-your-language)
- NITI Aayog and Bhashini have partnered to expand voice-first AI across government services. — [Devdiscourse](https://www.devdiscourse.com/article/law-order/3963092-bhashini-and-niti-aayog-join-hands-for-multilingual-ai-governance)

**myScheme (NeGD / MeitY)**
- Launched on 4 July 2022 as a scheme marketplace for search and eligibility discovery. — [Digital India](https://www.digitalindia.gov.in/?p=6360)
- Vikaspedia lists 4,000+ schemes: 550+ central and 3,440+ state/UT. — [Vikaspedia](https://en.vikaspedia.in/viewcontent/e-governance/digital-india/myscheme-national-platform?lgn=en)
- A secondary 2026 guide says eligibility is checked through about 8 profile questions and that the site supports 8 Indian languages. This source is low reliability. — [RTI Wiki](https://righttoinformation.wiki/mygov-myscheme-citizen-services-india)
- A government OpenForge task (assigned 2025-09-23) is to build a LangChain-based myScheme chatbot with "multilingual context-aware Q&A … streaming and citations". This is a contributor task, not evidence of a live feature. — [OpenForge](https://openforge.gov.in/plugins/tracker/?aid=320621)

**UMANG (NeGD)**
- The pilot text chatbot reportedly had about 0.5 million users asking more than 1 million questions (undated, likely before 2025). Senseforth built the chatbot and voice assistant. — [IndiaAI](https://indiaai.gov.in/news/now-say-hey-umang-to-avail-government-services); [Voicebot.ai](https://voicebot.ai/conversational-ai-startup-senseforth-chosen-to-build-indian-governments-voice-assistant/)
- A January 2025 NeGD RFP for a new UMANG conversational chatbot and AI voice assistant scopes English, Hindi and Hinglish. — [NeGD RFP responses, Jan 2025](https://negd.gov.in/wp-content/uploads/2025/01/Response-to-Queries-against-UMANG-RFP-Conversational-Chatbot-and-AI-Based-Voice-Assistant_0.pdf)
- Sources disagree on UMANG's language count (12, 13 or 23 languages) and on its service count (1,200+ to 2,039). — [IMPRI](https://www.impriindia.com/insights/umang-unified-mobile-application/); [GKToday](https://www.gktoday.in/?p=165330)

**Haqdarshak (social enterprise, human-agent model)**
- Reports 6.68 million citizens reached from April 2015 to November 2024, including 1.47 million from December 2023 to November 2024. Also reports 6.38 million applications submitted and 6.06 million benefits delivered. These are self-reported. — [Haqdarshak Annual Impact Analysis 2025](https://haqdarshak.com/annual_impact_analysis_2025)
- The Yojana Card launched in May 2022. It is a QR-enabled card with free first-time scheme screening, aimed at exclusion, grievance and documentation gaps. A Mastercard prepaid variant was announced. — [MIT Solve](https://solve.mit.edu/solutions/70685); [ThePrint/ANI](https://theprint.in/ani-press-releases/haqdarshak-announces-its-financial-services-linked-yojana-card-at-its-debut-conference-amid-stalwarts-including-nandan-nilekani-dilip-asbe-and-abhishek-singh/1608388)
- A give.do profile gives a lower, undated figure: 28 lakh citizens and INR 4,200 crore unlocked. This conflicts with the impact report, probably because of the date. — [give.do](https://give.do/discover/17HE/haqdarshak/)

**Farmer.CHAT (Digital Green, built with Gooey.AI)**
- User counts vary by source: about 200k (early), 400k+ across five countries (AIKOSH), and more than 1 million (Rural 21, 2026). — [AIKOSH/IndiaAI](https://aikosh.indiaai.gov.in/home/use-cases/details/farmerchat_ai_powered_agricultural_advisory_at_scale.html); [Rural 21](https://www.rural21.com/english/news/detail/article/testing-ai-advisory-services-insights-from-farmerchat-in-india-and-kenya.html)
- Gooey.AI lists Hindi, Telugu, Bhojpuri, Amharic, Swahili and English. — [Gooey.AI](https://gooey.ai/farmer-chat)
- Digital Green's CTO acknowledged hallucinations even within the knowledge base. He also said off-the-shelf models handle Telugu and Swahili poorly and that "LLMs often claim support they don't deliver". — [Digital Green Ethiopia insight](https://www.digitalgreen.org/insights/breaking-language-barriers-ethiopia)
- In an IDinsight evaluation, 60% of users acted on the advice. That measures uptake, not factual accuracy. — [Rural 21](https://www.rural21.com/english/news/detail/article/testing-ai-advisory-services-insights-from-farmerchat-in-india-and-kenya.html)
- Farmer.CHAT is focused on agronomy advisory, not welfare-scheme entitlements.

**PM-KISAN Kisan e-Mitra (MoA&FW, with Wadhwani AI and Bhashini)**
- Launched in September 2023 in English, Hindi, Bengali, Odia and Tamil. — [News On AIR](https://newsonair.gov.in/union-minister-kailash-choudhary-launches-pm-kisan-ai-chatbot-kisan-e-mitra-in-new-delhi)
- Now covers 11 languages and 49 query categories, using Bhashini IndicTrans2, with a goal of all 22 languages. — [Wadhwani AI](https://www.wadhwaniai.org/?p=4132); [Apolitical](https://apolitical.co/en/navigator/case-studies/kisan-e-mitra-indias-voice-enabled-ai-support-for-farmers)
- Wadhwani AI reports more than 3 million grievances resolved for more than 290k farmers since the February 2024 upgrade, and 2.69 million queries in 186 days. These are partner figures. — [Wadhwani AI](https://www.wadhwaniai.org/?p=3443); [Wadhwani AI](https://www.wadhwaniai.org/empowering-millions-of-indian-farmers-with-instant-ai-chatbot-support/)
- It covers a single scheme (PM-KISAN status, payment, eligibility and registration) and is accessed through the PM-KISAN portal or app. — [PIB Aug 2025](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/aug/doc202581597201.pdf)

**Tamil Nadu: 1100 CM Helpline, KMUT channels, Namma Arasu**
- 1100 is the state-wide CM Helpline, an integrated public-grievance system. It handles grievances; it is not an information service. — [The News Minute](https://www.thenewsminute.com/article/tamil-nadu-cm-launches-helpline-no-1100-redressing-peoples-grievances-143392); [DT Next](https://www.dtnext.in/news/chennai/now-call-1100-to-access-integrated-public-grievance-cm-helpline-management-system)
- A KMUT (Magalir Urimai) grievance portal and helpline (044-25619208) are listed only by aggregators. I could not confirm them officially. A Magalir Urimai-specific helpline was not verified. — [egovtschemes](https://www.egovtschemes.com/?p=21067); [OneIndia](https://www.oneindia.com/chennai/kalaignar-scheme-have-queries-on-registration-application-status-of-magalir-urimai-thittam-helpli-3636215.html)
- **Namma Arasu** is a WhatsApp chatbot (+91 7845 252525) launched in January 2026 by TNeGA with Meta. It works in Tamil and English and covers 50–51 services across 16 departments, including welfare-scheme information, certificates and bill payments. It uses intent-based search. Tamil Nadu is the third state with such a bot, after Andhra Pradesh and Odisha. — [Storyboard18](https://www.storyboard18.com/social-media/tamil-nadu-launches-namma-arasu-whatsapp-chatbot-in-partnership-with-meta-87299.htm); [Elets eGov Jan 2026](https://egov.eletsonline.com/2026/01/tamil-nadu-launches-namma-arasu-whatsapp-chatbot-to-offer-50-government-services/)
- Other Tamil Nadu WhatsApp bots: Chennai Corporation civic services (August 2025) and NalamAI for outpatient appointments at government hospitals. — [The Week](https://www.theweek.in/wire-updates/national/2025/08/25/mes16-tn-citizen-services-gcc.html); [DT Next](https://www.dtnext.in/news/tamilnadu/tn-launches-nalamai-whatsapp-chatbot-to-book-op-appointments-at-govt-hospitals)
- WhatsApp has about 500 million users in India and is building state citizen-service bots with Odisha, Maharashtra, Andhra Pradesh and Tamil Nadu. — [Business Today Sep 2025](https://www.businesstoday.in/technology/news/story/whatsapp-expands-business-tools-in-india-with-payments-ai-support-and-citizen-services-495481-2025-09-24)

**Sarvam AI**
- In April 2025 the Government of India selected Sarvam to build India's sovereign LLM under the IndiaAI Mission. — [Sarvam blog](https://www.sarvam.ai/blogs/indias-sovereign-llm); [YourStory](https://yourstory.com/2025/04/india-taps-sarvam-build-sovereign-large-languag)
- Maharashtra approved Rs 11.26 crore over two years for Indus, voice citizen outreach and MahaAI speech tech, plus a pilot of the Samvaad TB-calling agent. Hosting would be on audited infrastructure in India. — [YourStory](https://yourstory.com/ai-story/maharashtra-approves-rs-11-26-crore-sarvam-ai-rollout)
- "Listen at Scale" (March 2026, with EkStep and AI4Bharat) replaces one-way IVR and SMS with two-way voice calls. The National Health Authority reportedly called 1.4 million+ seniors, with a 42% rise in daily Ayushman Vay Vandana enrolments. These figures are unverified. — [Storyboard18](https://www.storyboard18.com/digital/sarvam-ai-launches-listen-at-scale-with-ekstep-ai4bharat-to-expand-multilingual-voice-ai-across-india-91931.htm)
- Sarvam's developer docs include a sample "Government Scheme Agent" whose prompt says to redirect to a human helpline instead of guessing. — [Sarvam docs](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/use-cases/government-services.md)

**Gnani.ai**
- Gnani claims more than 200 enterprise clients, including government, and supports on-prem and air-gapped deployment. It raised $10M for "sovereign" voice agents. — [Inc42](https://inc42.com/buzz/gnani-ai-raises-10-mn-to-build-sovereign-ai-voice-agents/); [Gnani](https://gnani.ai/dev/about-us)
- Madhya Pradesh is exploring Gnani for citizen services. This is exploratory, not a deployment. — [AIM](https://analyticsindiamag.com/ai-news/madhya-pradesh-explores-ai-driven-governance-solutions-with-gnaniai)

### Inferences
- **Telephony is the frontier, but not yet a citizen information product.** Sarvam and VoicERA show that government is moving to voice calls in 2026. The documented uses are outbound campaigns (enrolment and TB calls) and helpline infrastructure, not an inbound "call and ask about any of my schemes, with a cited answer" service. Pakkam can occupy that position, though government-backed VoicERA deployments could close the gap quickly.
- **Tamil Nadu is the closest overlap, but the formats differ.** Namma Arasu is a Tamil/English WhatsApp menu-and-intent bot spanning many services. It is not voice-first, not Tanglish, and has no documented citation or refusal behaviour.
- **Kisan e-Mitra is the strongest precedent for a narrow, grounded government bot.** It is single-scheme and app or portal based.
- **Haqdarshak is the accountability benchmark.** It uses human agents and paid screening. Pakkam's human-signed fact cards borrow that trust model without the field-agent cost.

### Gaps
- I found no current status for Jugalbandi (2025–26) and no accuracy evaluation of it.
- I found no evidence that myScheme's chatbot is live, and no myScheme usage numbers.
- Namma Arasu: no usage figures, and no information on whether it answers free-form scheme-eligibility questions or uses an LLM.
- I could not verify the KMUT helpline officially. Tamil Nadu reportedly had a change of government in 2026; I did not verify this, and it could change scheme rules or names.
- I found no published accuracy or hallucination audit for any product in this list. The only accuracy-adjacent measures are self-reported resolutions or uptake.

## Q2. Documented gaps: hallucination, no citations, English bias, smartphone/internet need, accountability, telephony

### Takeaway
The documented gaps are:
- hallucination, admitted even by grounded deployments;
- English-source content and poor performance in low-resource languages;
- dependence on smartphones or WhatsApp in most products;
- privacy and accountability concerns.

No product found documents citations to source pages.

### Cited Findings
- **Hallucination and confidence:** commentary on the 2023 government ChatGPT/WhatsApp scheme bot warned that ChatGPT gives fictional information confidently as fact, cannot fact-check, and cannot access real-time information. — [Policy Circle](https://www.policycircle.org/society/chatgpt-for-farmers-under-digital-india/)
- **Hallucination despite grounding:** Farmer.CHAT's CTO reports hallucinations even within the knowledge base. — [Digital Green](https://www.digitalgreen.org/insights/breaking-language-barriers-ethiopia)
- **English source content:** scheme information on government websites is usually written in English, and Jugalbandi had to translate it. — [Business Standard/Reuters](https://business-standard.com/amp/technology/tech-news/microsoft-backed-group-aims-to-bridge-language-gap-with-ai-assistant-123052301059_1.html)
- **Speech recognition for low-resource languages:** off-the-shelf ASR performed poorly for Farmer.CHAT, which forced a custom transcription pipeline. — [iMerit](https://imerit.ai/?p=35917)
- **Voice and Indic queries in grounded bots:** in CataractBot, a deployed expert-in-the-loop health bot in India, 18.64% of Indic-language queries and 26.74% of audio queries got "I don't know" answers because of speech and translation limits. — [arXiv 2409.10354](https://arxiv.org/pdf/2409.10354)
- **Privacy:** Jugalbandi's plan to have the bot fill forms raised concerns about sharing personal information through the bot. — [MediaNama](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/)
- **Why WhatsApp:** Jugalbandi chose WhatsApp because government websites are hard to navigate for rural users with little digital education. Even so, this still assumes a smartphone and data. — [Microsoft Source](https://news.microsoft.com/source/asia/features/with-help-from-next-generation-ai-indian-villagers-gain-easier-access-to-government-services/)
- **Grievance vs. information:** Tamil Nadu's 1100 is a grievance channel, not an information service. — [The News Minute](https://www.thenewsminute.com/article/tamil-nadu-cm-launches-helpline-no-1100-redressing-peoples-grievances-143392)

### Inferences
- **No product found offers verifiable page-level citations to the official scheme document.** Its absence from every product description I found is a strong signal, but not proof.
- **Feature-phone and IVR access for information remains thin.** Pakkam's phone channel addresses the smartphone gap, but VoicERA targets the same space.

### Gaps
- I found no systematic study of citizens receiving wrong scheme information from a government chatbot.
- I found no Indian data on feature-phone vs. smartphone share among scheme beneficiaries.

## Q3. What can and can't ChatGPT, Claude, Gemini and Meta AI do for this use case?

### Takeaway
General assistants are widely used in India; Meta AI reports India as its largest market. Their documented limits are:
- uneven Indic voice support (Meta AI voice: English, Hindi, Bengali);
- no phone-call access for feature phones;
- no guarantee of grounding in official documents;
- known worse performance in Hindi than English on factual domains;
- government restrictions on use because of data confidentiality.

### Cited Findings
- Meta has said India is Meta AI's largest market by usage. — [DT Next / IANS](https://www.dtnext.in/lifestyle/technology/india-becomes-largest-market-for-meta-ai-usage-mark-zuckerberg-797637)
- Meta AI added Hindi and romanised Hindi text in July 2024. — [Inc42](https://inc42.com/buzz/meta-ai-expands-language-support-with-hindi-and-hindi-romanised-script)
- A later rollout (Muse Spark, date unclear) added voice for India in English, Hindi and Bengali. I found no Tamil voice support for Meta AI. — [pc-tablet](https://pc-tablet.com/?p=191242)
- **Data sovereignty:** on 29 January 2025 the Finance Ministry's Department of Expenditure told staff not to use AI tools such as ChatGPT and DeepSeek on office devices, citing the confidentiality of government data. — [Business Today](https://www.businesstoday.in/technology/news/story/govt-employees-asked-to-stop-using-ai-tools-like-chatgpt-deepseek-on-official-devices-heres-why-463483-2025-02-05); [Deccan Herald](https://www.deccanherald.com/india/finance-ministry-asks-employees-to-avoid-ai-tools-like-chatgpt-deepseek-3390249)
- Government is backing sovereign or in-country alternatives: the Sarvam sovereign LLM (IndiaAI), Maharashtra's Sarvam hosting on audited Indian infrastructure, and Gnani's air-gapped option. — [Sarvam](https://www.sarvam.ai/blogs/indias-sovereign-llm); [YourStory](https://yourstory.com/ai-story/maharashtra-approves-rs-11-26-crore-sarvam-ai-rollout); [Inc42](https://inc42.com/buzz/gnani-ai-raises-10-mn-to-build-sovereign-ai-voice-agents/)
- **Hindi factual accuracy:** GPT-3.5 gave contradictory, incomplete or inappropriate health answers in Hindi about 45% of the time, its worst language and worse than English. This is an older model. — [Scientific American](https://www.scientificamerican.com/article/chatbots-medical-questions-language/)
- **Cross-language consistency:** LLM answers differ across languages for the same health question. — [arXiv 2501.14719](https://arxiv.org/html/2501.14719v1)
- **Trust despite errors:** in a 2025 study, users kept trusting ChatGPT after noticing it gave false information about Indian politicians. — [Big Data & Society 2025](https://journals.sagepub.com/doi/10.1177/20539517241306345)
- **Government-affairs QA (non-India):** many of 15 LLMs tested showed low accuracy and reliability under minor input variations. — [ACM, MSGA](https://dl.acm.org/doi/10.1145/3716854)

### Inferences (structural; not from a single source)
- **Answers are not tied to a fixed document.** General assistants answer from training data or open web search. They cannot guarantee that an amount, such as ₹1,000 per month for KMUT or ₹6,000 per year for PM-KISAN, comes from the current official PDF. Web-search citations point to whatever pages rank, often aggregator sites like those that dominated this research, not official documents with page numbers.
- **Stale information.** Scheme rules change, for example after a state change of government, and training cutoffs lag behind.
- **No accountability.** No named official or human signs an answer, and terms of service disclaim accuracy.
- **No phone line.** None of the four, as far as found, offers a toll-free voice number reachable from a feature phone. WhatsApp-based Meta AI still needs a smartphone and data.
- **Tanglish and Tamil voice are unproven.** No evidence found of Tamil or code-mixed Tamil-English voice quality evaluations for these assistants.

### Gaps
- I found no documented, dated example of ChatGPT, Gemini, Claude or Meta AI giving a specific wrong amount or eligibility rule for an Indian scheme. Only general hallucination commentary exists. This is a good candidate for Pakkam to produce its own test set.
- I did not verify current ChatGPT, Gemini or Claude voice language lists for Tamil or Hindi. These were not searched within the call budget.
- I did not locate the IndiaAI Mission or MeitY data-localisation guidance text (for example the DPDP Act rules or the 2024 MeitY AI advisory) within the budget.

## Q4. Studies and evaluations of LLM accuracy on Indian government scheme questions or Indic languages

### Takeaway
I found no benchmark specifically for Indian welfare-scheme QA. That absence is itself a positioning opportunity. Adjacent Indian benchmarks (tax law, financial regulation, health) show substantial error rates and weaker Indic performance.

### Cited Findings
- **LE-BTL (IIT Kharagpur and Taxmann, 2025):** the first benchmark of 12 LLMs on Indian tax law (Income Tax, GST, FEMA). — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5941734)
- **IndiaFinBench (2026):** 406 expert QA items from SEBI and RBI documents. Zero-shot accuracy ranged from 70.4% (Gemma 4 E4B) to 89.7% (Gemini 2.5 Flash), so even the best model got about 1 in 10 wrong on Indian regulatory text. — [arXiv 2604.19298](https://arxiv.org/abs/2604.19298)
- **HEALTH-PARIKSHA:** evaluated 24 models on 750 real user questions in 5 languages. Instruction-tuned Indic models do not always perform well on Indic queries. — [arXiv 2410.13671](https://arxiv.org/pdf/2410.13671)
- **CataractBot:** 84.52% of medical answers were rated accurate and complete with expert-in-the-loop, but there were high "I don't know" rates for Indic and audio queries. — [arXiv 2409.10354](https://arxiv.org/pdf/2409.10354)
- **"LLMs Humanize Technology"** uses a farmer and central-scheme voice-bot example. It notes that accuracy is likely lower for low-resource languages and needs quantified evaluation. — [arXiv 2305.05576](https://arxiv.org/pdf/2305.05576)
- **English dominance in evaluations:** 95% of 519 health LLM evaluations (2022–2024) were in English. — [PMC systematic review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11795331/)

### Inferences
- **On a credible error range:** even on well-documented Indian regulatory text, top models miss about 10% of questions. For benefit amounts and eligibility, a 10% error rate is unacceptable, which supports Pakkam's refuse-when-unsupported design.
- **On publishing an evaluation:** Pakkam could differentiate by publishing its own small evaluation of the 18 schemes in Tamil, Hindi, English and Tanglish, comparing itself with general assistants.

### Gaps
- I found no welfare-scheme QA dataset.
- I found no Tamil or Tanglish voice ASR benchmark comparing Sarvam, Bhashini and the big-tech assistants.
- I did not find benchmarks such as MILU or IndicGenBench within the budget; a follow-up search is worthwhile.
