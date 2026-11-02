# Put Pakkam on a phone line, then prove it

Pakkam stands out from ChatGPT, Claude, Gemini and Meta AI on two things. First, **it can be a Tamil-speaking phone number that works from any handset**. Second, **it can measurably show that every answer comes from a named page of an official document, signed by a person, or it says no.** Neither of these is about a better model. On a typed English question with web search, a general assistant will often give a similar answer, and the research found **no documented case of any of the four getting an Indian scheme amount wrong**. So "ChatGPT can do that too" is partly true for the web demo Pakkam has today. It stops being true once Pakkam is reached by a voice call from a feature phone, answers in Tamil or Tanglish over Gnani's 8 kHz speech stack, cites a G.O. page out loud, and refuses when the documents are silent.

The beneficiary evidence points to the same place. About **40% of Indian adults (46% in rural areas) cannot use the internet even though 86.5% can use a phone**. The documented harms are procedural: rejection SMSes nobody can decode, missed e-KYC deadlines, fake "₹1,000 stopped" forwards. Basic awareness that a scheme exists is less of a problem.

With about four days and one developer, the ranked plan is:

1. A call-in phone line on an Exotel or Twilio trial, piping 8 kHz audio through Gnani Prisma and Timbre into the existing FastAPI pipeline (about 1.5–2 days).
2. An "Is this forward true?" checker that tests viral claims against the official documents and the signed fact cards (about 0.5–1 day).
3. A rejection-SMS decoder with a document checklist (about 1 day).
4. A small head-to-head test running the same questions through the general assistants (about 0.5 day). This is the only direct, honest answer to the "ChatGPT can do that" objection.

Answer speed is the biggest risk to the phone line. Pakkam's own benchmark shows a **9.2 s median and 29.2 s p90** per answer, which is long dead air on a phone call.

## Beneficiaries lose benefits to procedure, not ignorance

The people Pakkam serves can mostly make calls but cannot do much online. The NSSO CAMS survey (2022–23) found **86.5% of adults can use a mobile phone but only 59.8% can use the internet (53.6% rural)**. Only **43.4% can send an email** and only **30% can search, email and bank online** ([ThePrint](https://theprint.in/india/50-of-indias-internet-users-dont-know-how-to-send-email-a-third-know-online-banking-govt-survey/2308129)). Tamil Nadu women are ahead on phones: **74.6% of women aged 15–49 use their own mobile, against 53.9% nationally** ([Rajya Sabha PQ 259](https://rsdebate.nic.in/bitstream/123456789/740019/1/PQ_259_03022023_S22_p18_p20.pdf)). NFHS-6, however, names Tamil Nadu as a state where women's phone ownership runs ahead of their internet use ([The News Minute](https://www.thenewsminute.com/news/womens-internet-use-nearly-doubles-but-access-gaps-remain)). GSMA puts Indian women's mobile internet use at about **39%** ([Dawn, citing GSMA 2025](https://www.dawn.com/news/amp/1911146)). For KMUT's target users, a website or chat app leaves out a large group that a phone call reaches.

The failures cluster after enrolment. KMUT received **1.63 crore applications** in 2023 ([News Today](https://newstodaynet.com/2023/08/22/1-63-cr-applications-received-for-magalir-urimai-thogai-scheme/)). The opposition claimed about **57 lakh were rejected "with no clarification"**; that is a political figure, not an official tally ([DT Next](https://www.dtnext.in/amp/story/news/tamilnadu/provide-rs-1000-monthly-dole-to-all-women-in-tn-ramadoss-738117)). **9.24 lakh women appealed** ([inkl/The Hindu](https://inkl.com/news/9-24-lakh-women-file-appeals-against-their-rejection-from-kalaignar-magalir-urimai-thittam)) and **1.48 lakh appeals were accepted** ([DT Next](https://www.dtnext.in/amp/story/news/tamilnadu/148l-appeals-accepted-under-kalaignar-mahalir-urimai-thittam-informs-udhayanidhi-792266)). The appeal window was 30 days from the rejection SMS, and the appeal portal crashed on its first morning ([DT Next](https://www.dtnext.in/news/tamilnadu/kmut-website-reportedly-crashes-on-day-one-of-appeal-737308)). Two years later the problem had not gone away: on day one of the 2025 "Ungaludan Stalin" camps in Chennai, **7,518 of 10,949 petitions were KMUT applications from women left out** ([DT Next](https://www.dtnext.in/amp/story/news/chennai/almost-11000-applications-submitted-at-ungaludan-stalin-camp-held-in-7-places-840232)).

PM-KISAN shows the same pattern. After e-KYC and Aadhaar seeding became mandatory, Punjab's beneficiaries fell from **17.59 lakh to 7.97 lakh** ([Rajya Sabha PQ 265](https://rsdebate.nic.in/bitstream/123456789/749525/1/PQ_265_26072024_S49_p40_p45.pdf)). Dvara Research's grievance analysis found:

- **About 72% of complaints were application or document problems.**
- **32% were about centres being too far or officials being unavailable.**
- **13% were about repeat visits.**
- About half of those with DBT problems had payments stop "without clear communication" ([ThePrint](https://theprint.in/india/despite-direct-benefit-transfers-welfare-schemes-beneficiaries-still-floundering-claims-study/983113)).

Getting help also costs money. A certificate that costs Rs 20 at a public e-Sevai centre can cost **Rs 200 at a private one** ([Citizen Matters](https://citizenmatters.in/e-sevai-centres-chennai-data-security-certificates-governance/)).

Misinformation is the third barrier, and it is specific. Newschecker Tamil has debunked recycled KMUT application dates, "scheme stopped for 80 lakh women" claims, and fake court cases ([Newschecker](https://newschecker.in/ta/fact-check-ta/magalir-urimai-thogai-stopped)). PIB has flagged a fake ₹4,000 PM-KISAN "Raksha Bandhan instalment" ([CareerIndia](https://www.careerindia.com/features/pm-kisan-4000-raksha-bandhan-grant-fact-check-viral-ai-videos-fake-claims-011-64505.html)). The Agriculture Ministry warns that registration happens only via pmkisan.gov.in, a CSC or the tehsil office ([Free Press Journal](https://www.freepressjournal.in/business/ministry-of-agriculture-warns-about-fraudulent-messages-under-the-guise-of-pradhan-mantri-kisan-samman-nidhi-scheme)).

These are the jobs a feature has to do: decode a status, check a forward, list the documents before a trip. Saying "here is what KMUT is" does not address them. Ujjwala is the exception. Its refill drop-off (**1.66 crore one-refill beneficiaries in FY 2023-24**) is mostly about affordability, which information cannot fix ([The South First](https://thesouthfirst.com/news/rising-dropout-rate-in-pradhan-mantri-ujjwala-yojana-a-growing-concern/)).

## Competitors cover channels or schemes, never cited pages

The field has three kinds of competitor, and none combines voice, Tamil, citations and refusals:

- **Government portals.** myScheme lists 4,000+ schemes but is a text eligibility search; its chatbot with citations exists only as an open contributor task, not a live feature ([Vikaspedia](https://en.vikaspedia.in/viewcontent/e-governance/digital-india/myscheme-national-platform?lgn=en); [OpenForge](https://openforge.gov.in/plugins/tracker/?aid=320621)).
- **Narrow chatbots.** Kisan e-Mitra is the best grounded precedent. It covers 11 languages, including Tamil, but only one scheme, and lives inside the PM-KISAN portal ([Wadhwani AI](https://www.wadhwaniai.org/?p=4132)). Tamil Nadu's **Namma Arasu** (January 2026, TNeGA with Meta) is the closest local overlap. It is a Tamil/English WhatsApp intent bot across about 50 services, with no documented voice, Tanglish, citations or refusal behaviour ([Elets eGov](https://egov.eletsonline.com/2026/01/tamil-nadu-launches-namma-arasu-whatsapp-chatbot-to-offer-50-government-services/)).
- **Voice infrastructure.** Sarvam's "Listen at Scale" and MeitY's open-source **VoicERA** (February 2026) aim squarely at government helplines and scheme discovery ([Storyboard18](https://www.storyboard18.com/digital/sarvam-ai-launches-listen-at-scale-with-ekstep-ai4bharat-to-expand-multilingual-voice-ai-across-india-91931.htm); [Angel One](https://www.angelone.in/news/economy/voicera-on-bhashini-govt-services-helpline-will-now-speak-in-your-language)). Their documented uses are outbound campaigns and helpline plumbing, not an inbound line that answers any scheme question with a cited source.

Tamil Nadu's **1100** helpline handles grievances, not information ([The News Minute](https://www.thenewsminute.com/article/tamil-nadu-cm-launches-helpline-no-1100-redressing-peoples-grievances-143392)). Haqdarshak is the accountability benchmark: humans screen people for schemes, reaching **6.68 million citizens** (self-reported). It is not a self-serve line ([Haqdarshak](https://haqdarshak.com/annual_impact_analysis_2025)).

Grounded systems still make mistakes. Farmer.CHAT's CTO admits hallucinations happen even within its knowledge base ([Digital Green](https://www.digitalgreen.org/insights/breaking-language-barriers-ethiopia)). CataractBot returned "I don't know" on **26.74% of audio queries** because of speech and translation limits ([arXiv 2409.10354](https://arxiv.org/pdf/2409.10354)).

No product found publishes page-level citations to official scheme PDFs, and none publishes an accuracy audit. Pakkam already has both. Its final live benchmark on 60 questions, run through the website, gave:

| Measure | Result |
|---|---|
| Covered questions answered | **81%** |
| Answers that cited a correct page | **97%** |
| Out-of-scope questions refused | **92%** |
| Weakest spots | Hindi refusals 2 of 3; Tanglish answer rate 67% |

Source: [LIVE_BENCHMARK.md](../docs/review/LIVE_BENCHMARK.md). Those numbers are an asset only if Pakkam shows them to the judges.

## What ChatGPT can do too, and what it structurally cannot

Take the worry head on: much of Pakkam's current web demo can be copied. ChatGPT, Gemini and Claude can answer "how much is Magalir Urimai Thogai?" in English and in Tamil text. With web search they attach links. A custom GPT loaded with the same 18 PDFs and told to refuse when unsure would get partway to Pakkam in an afternoon.

The research found **no dated example** of these assistants giving a wrong Indian scheme amount. The evidence against them is indirect:

- On Indian SEBI/RBI regulatory text, the best model tested still missed **about 1 in 10** questions ([IndiaFinBench, arXiv 2604.19298](https://arxiv.org/abs/2604.19298)).
- GPT-3.5 gave contradictory or incomplete Hindi health answers **about 45% of the time**, worse than in English ([Scientific American](https://www.scientificamerican.com/article/chatbots-medical-questions-language/)).
- Answers drift across languages for the same question ([arXiv 2501.14719](https://arxiv.org/html/2501.14719v1)).
- Users keep trusting ChatGPT after catching it in errors about Indian topics ([Big Data & Society](https://journals.sagepub.com/doi/10.1177/20539517241306345)).

Saying "LLMs hallucinate" on stage without Pakkam's own comparison is an assertion, not evidence.

The differences that hold up are structural:

- **Reach.** Meta AI is the assistant most likely to reach Pakkam's users, since India is its largest market ([DT Next](https://www.dtnext.in/lifestyle/technology/india-becomes-largest-market-for-meta-ai-usage-mark-zuckerberg-797637)). Its voice in India covers English, Hindi and Bengali, and **no Tamil voice was found** ([pc-tablet](https://pc-tablet.com/?p=191242)). It also needs a smartphone and data. The research found no Indian phone number for any of the four assistants. Before saying "none exists" on stage, check this live, because OpenAI has run a US phone line.
- **What an answer is tied to.** A general assistant answers from training data or from whatever web pages rank, which are often the aggregator sites that dominated this research. It cannot promise that "₹1,000" comes from page 11 of the current G.O. Pakkam does this by design, and its refusal rate is measured.
- **Accountability.** No person signs a ChatGPT answer, and its terms disclaim accuracy. Pakkam's signed fact cards copy the trust model of Haqdarshak's human agents without the cost of field staff.
- **Sovereignty.** The Finance Ministry told staff in January 2025 not to use ChatGPT or DeepSeek on office devices ([Business Today](https://www.businesstoday.in/technology/news/story/govt-employees-asked-to-stop-using-ai-tools-like-chatgpt-deepseek-on-official-devices-heres-why-463483-2025-02-05)). Gnani offers on-prem and air-gapped deployment ([Inc42](https://inc42.com/buzz/gnani-ai-raises-10-mn-to-build-sovereign-ai-voice-agents/)), which a state department could actually adopt.

The honest conclusion is that Pakkam's edge does not come from the model. It comes from the curated, OCR-corrected corpus, the signed cards, a measured refusal policy, and a channel that general assistants do not offer. Features should make those visible.

## Gnani's stack fits a phone line almost exactly

Gnani's public API at `api.vachana.ai` offers:

- **Prisma STT** over REST, WebSocket and batch, in 10 languages including **`ta-IN` with Tamil-script output**, and `indic-auto` language detection in v3.0. Hinglish is accepted under `en-IN`. **Tanglish is not documented** ([Gnani STT languages](https://docs.gnani.ai/api/STT/languages.md)).
- **Timbre TTS** with SSML and text normalisation ([HF gnani-ai/vachana](https://huggingface.co/gnani-ai/vachana)).
- **Voice cloning.**
- The **Inya** no-code agent builder.

The detail that matters most is that **Prisma accepts 8 kHz audio** ([Pipecat Gnani STT](https://docs.pipecat.ai/api-reference/server/services/stt/gnani)), the rate that Exotel's Voicebot and Twilio Media Streams deliver. Gnani claims about **200 ms P95 streaming STT latency**; that is a vendor claim ([Gnani docs](https://docs.gnani.ai/api/introduction/introduction.md)).

The pieces worth showing judges are:

- 8 kHz phone audio in Tamil.
- `indic-auto` switching between Tamil, Hindi and English mid-call.
- SSML-slowed, paused TTS for elderly callers.
- Tanglish, shown only after testing it on real phone audio, since Pakkam's Tanglish answer rate is already the weakest at 67%.

Do not rebuild the pipeline inside Inya. It would duplicate the backend's retrieval and verification, and its only documented telephony is importing Twilio numbers ([Gnani Import Number](https://docs.gnani.ai/M16x_Import_Number.md)). Avoid voice cloning in a welfare context; it invites impersonation questions. The Tamil voice list for TTS was not confirmed, so check the available-voices page first.

Telephony choices for a four-day build:

- **Exotel.** Its trial gives a real Indian ExoPhone in minutes **without KYC**. Calls only reach whitelisted numbers and the trial lasts about 7 days (some pages say 15). Production numbers need KYC, which takes 2–3 business days ([Exotel trial](https://developer.exotel.com/docs/getting-started/trial-account); [Exotel KYC](https://developer.exotel.com/docs/faqs/account-setup)).
- **Twilio.** Its trial is the fastest fallback, but Indian callers would dial a foreign number, the trial is capped at 75 voice minutes, and only verified callers can get through ([Twilio trials](https://www.twilio.com/docs/usage/trials); [Twilio India](https://www.twilio.com/en-us/guidelines/in/voice)).
- **Pipecat.** It ships Exotel and Twilio serializers and a Gnani STT service ([Pipecat Exotel guide](https://docs.pipecat.ai/pipecat/telephony/exotel-websockets.md)), which plausibly cuts the integration to about a day.

There is precedent that a phone number reaches people an app does not. ARMMAN's government-run **Kilkari** voice service has passed **11 million subscribers** ([ARMMAN](https://armman.org/armmans-vision-for-kilkari-and-mobile-academy/)). Gram Vaani's IVR reached about **100,000 monthly users** in poorly literate communities ([MIT Solve](https://solve.mit.edu/solutions/7355)).

## Ranked features for the last four days

Features are ranked by how far they move Pakkam from "a chatbot" to "something ChatGPT is not", weighed against effort for one developer on the existing FastAPI backend. Effort figures are engineering estimates, not sourced numbers.

| Rank | Feature | Why it differentiates (evidence) | Effort | Main risks |
|---|---|---|---|---|
| 1 | **Call-in phone line.** Exotel trial ExoPhone (Twilio fallback) → FastAPI `/ws/call` → Gnani Prisma 8 kHz → existing answer and verifier → Timbre TTS. The answer speaks the source ("G.O. 15, page 11") and a signed card's reviewer. | No general assistant offers an Indian phone line or Tamil voice on Meta AI. Serves the 40% offline (CAMS) and the Kilkari/Gram Vaani precedent. It is the most "Gnani" demo possible. | 1.5–2 days (about 1 with Pipecat) | **Latency:** 9.2 s median and 29.2 s p90 on free Gemini ([LIVE_BENCHMARK](../docs/review/LIVE_BENCHMARK.md)). Mitigate with a spoken holding line, an instant path for fact cards that skips the LLM, and a paid model tier for demo day. **Budget:** the self-imposed cap of 200 LLM calls per day (`SCHEMEBOT_MAX_DAILY_LLM_CALLS`, `config.py`), at about 2–3 calls per answer, allows roughly 70–100 answers a day, and the free Gemini tier has its own daily limits, so raise both for judging. Exotel streaming may need to be switched on by support; only whitelisted callers on trial; mu-law conversion for Twilio. |
| 2 | **"Is this forward true?" checker** (text, voice, and a phone menu option). Extract the claimed amount, date or "stopped" status, compare it with corpus and card values, and return a cited verdict plus "never share an OTP; only gov.in/nic.in". | Recurring, documented KMUT and PM-KISAN fakes (Newschecker, PIB). Official guidance matches the guardrail. ChatGPT would cite aggregator pages; Pakkam cites the G.O. | 0.5–1 day | Some forwards ("scheme stopped") depend on news after the PDFs were published. The checker must answer "the documents do not say this; check the official site", not "false". |
| 3 | **Rejection-SMS decoder and pre-visit checklist.** The user reads or pastes the SMS; Pakkam explains the reason, the documents to fix, the 30-day window and the public e-Sevai fee. | 72% of grievances are about documents; 13% are repeat visits (Dvara). There were 9.24 lakh KMUT appeals. Private centres charge 10x. | About 1 day | The 18 PDFs do not contain official rejection-reason codes. Sources disagree on where to appeal (the RDO or e-Sevai). Refuse anything not covered. |
| 4 | **Head-to-head test.** Put 20–30 of the existing benchmark questions (Tamil, Hindi, Tanglish, out-of-scope) to ChatGPT, Gemini and Meta AI by hand. Score the correct amount, whether an official page is cited, and whether it refused. | The only honest rebuttal to "ChatGPT can do that". No welfare-scheme QA benchmark exists, so Pakkam would be first. | 0.5 day | The general assistants may score well on amounts. Publish the result anyway; the differences in citations, refusals and channel will still show. |
| 5 | **Elderly mode on the phone line.** DTMF "press 1 to repeat, 2 for slower", SSML pauses, and a short-answer-first format. | Older women have lower documentation rates (Haqdarshak). Gnani TTS supports SSML. | 0.5 day after #1 | Exotel trial applets may limit DTMF inside the Voicebot flow. |
| 6 | **Missed-call callback.** The caller rings, the line hangs up, and Pakkam calls back, so the caller pays nothing. | Removes the cost of a call for the poorest users. | 0.5 day after #1 | This is an inferred Exotel flow with no official document. Trial outbound calls only reach whitelisted numbers. |
| 7 | **WhatsApp voice notes** (Cloud API test number). | Low added differentiation: Meta AI and Namma Arasu already live on WhatsApp. | About 1 day | Only 5 recipients, a token that expires every 24 h, and conflicting reports on whether the test number accepts inbound messages ([WANotifier](https://help.wanotifier.com/en/article/test-phone-number-limitations-kt0ly2/)). |
| 8 | **Voice eligibility interview** that sends a checklist by SMS. | Help with applying raises uptake more than information alone (Delhi pension RCT, secondary summary). | 1–2 days | Too large for the remaining time; it competes with #1. |

The sequence that fits is:

- **Day 1:** sign up for the Exotel and Twilio trials, and request streaming enablement. Build the phone WebSocket bridge and get a Tamil question answered end to end.
- **Day 2:** add the holding audio, the instant fact-card path, the spoken citation and the DTMF repeat option.
- **Day 3:** build the forward-checker and the SMS decoder as answer modes that both the web and phone channels use.
- **Day 4:** run the head-to-head test, re-run the 60-question benchmark through the phone path, and record the demo.

STATUS.md lists a demo-video delivery date of 3 November. Confirm whether the competition accepts a later cut, because these features otherwise miss the video.

**One-line pitch for the top pick:** *"Dial Pakkam from any phone, ask in Tamil, and hear the answer with the government page it came from, or an honest 'that isn't in the official documents.' ChatGPT has no number to call."*

## Conclusion

The worry is right about today's web demo and wrong about what Pakkam can become in four days. General assistants are good enough at typed questions that "we answer welfare questions with AI" is not a differentiator. Judges at a voice-AI competition will reward the thing Gnani's stack enables and ChatGPT's product does not: a Tamil phone line with measured faithfulness to the source documents. The second insight is that Pakkam's strongest evidence is something it already has and is not showing: a 97% correct-page rate and a 92% refusal rate on its own benchmark, in a field where no competitor publishes any accuracy audit.

Two things remain unknown: whether Gnani's STT handles Tanglish on 8 kHz phone audio, and how general assistants actually score on these 18 schemes. Both are measurable in under a day. Measuring them, rather than claiming them, is what makes the pitch credible.
