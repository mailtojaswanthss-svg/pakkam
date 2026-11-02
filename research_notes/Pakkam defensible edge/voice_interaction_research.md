# Evidence-Backed Voice Interaction Designs for Low-Literacy, Elderly and Rural Users (Pakkam)

Research date: 2026-11-02. Scope: HCI4D / ICTD / global-health evidence relevant to a Tamil/Tanglish/Hindi welfare-scheme voice assistant (Pakkam) built on Gnani.ai STT/TTS plus a grounded-answer backend. About 17 searches and fetches. Many findings come from search-result summaries of primary papers, not full-text reads, so effect sizes marked "per summary" should be checked against the PDF before they are quoted publicly.

## 1. HCI4D findings on voice UIs for low-literacy users (voice forums, peer voices, repetition, dialect, narrative)

### Takeaway
The strongest behavioural evidence says **peer-recorded voices drive more engagement than expert voices, even when users say they prefer experts** (Patel et al., ICTD 2012). Spoken dialog is faster and needs less help than text for low-literate users, but **task completion is lower than for richer multimodal UIs** (Medhi et al., CHI 2009 / ToCHI 2011). Combining audio with visuals can confuse this population (Medhi & Prasad, WWW 2007). Community-run voice forums (CGNet Swara, Sangeet Swara, Mobile Vaani) show that low-literate users will record, moderate and use audio content at scale.

### Cited Findings
- **Peer vs expert voice (strongest single finding for Pakkam).** Patel, Savani, Dave, Shah, Klemmer and Parikh, "Power to the Peers", ICTD 2012 (also ITID 2013). 305 Gujarat farmers got 7 agricultural tips by automated call over two weeks. Each tip was recorded by both university scientists and peer farmers, with identical content. Farmers called the follow-up number **significantly more often when a peer recorded the preview**. In interviews, a majority still *said* they preferred scientists, which the authors read as a socially desirable answer. — [Stanford HCI](https://hci.stanford.edu/publications/paper.php?id=195); [PDF](https://cs.stanford.edu/~neilp/pubs/ictd2012_patel.pdf); [FAO AIMS summary](https://aims.fao.org/es/news/do-indian-farmers-over-value-institutionally-recognized-authorities-relative-peer-so)
- **Spoken dialog vs text vs multimedia (Medhi, Gautama, Toyama, CHI 2009; 58 subjects in India).** Non-text designs were strongly preferred over text. Spoken dialog was faster and needed less assistance, but task completion was higher for the rich multimedia UI. — [MSR PDF](https://microsoft.com/en-us/research/wp-content/uploads/2016/02/medhi_chi2009.pdf)
- **ToCHI 2011 (Medhi, Patnaik, Brunskill et al.).** The text interface was unusable without literacy. Only **72% of spoken-dialogue subjects finished the task**, though they were quicker and needed less help. The graphical UI reached full completion in that comparison (per summary). — [MSR PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ToCHI2711_Medhi.pdf)
- **Voice annotation and modality (Medhi & Prasad, WWW 2007; 200 illiterate subjects).** Health symptoms were shown as text, drawings, photos, animation or video, each with and without voice. **Voice annotation generally sped up comprehension**, but bimodal audio-visual information could confuse the target population. — [WWW 2007 PDF](https://www.www2007.cpsc.ucalgary.ca/papers/paper764.pdf)
- **Text-free UI work (Medhi, Sagar, Toyama).** Results confirmed the need for semi-abstract graphics plus voice feedback. — [UW course copy](https://courses.cs.washington.edu/courses/cse490d/09au/papers/Text-FreeUI.pdf)
- **Community-moderated voice forum (Sangeet Swara, Vashistha et al.).** Low-income, low-literate users moderated audio content themselves without outside support. Community moderation was **98% accurate in categorisation and agreed with expert moderators in 90% of judgments** (per summary). — [CACM "Internet of the Orals"](https://cacm.acm.org/research/the-internet-of-the-orals); [Vashistha dissertation, UW 2019](https://digital.lib.washington.edu/researchworks/handle/1773/44769)
- **Overview chapter.** Vashistha and Raza (2021) review two decades of voice interfaces for underserved communities. — [PDF](https://aghaaliraza.com/publications/2021--DevEnggBook--Voice_Interfaces_for_Underserved_Communities.pdf)
- **CGNet Swara (Mudliar, Donner, Thies, ICTD 2012).** Analysis of 1,000+ recordings from a voice forum for citizen journalism in rural Chhattisgarh, studied as a grievance-reporting channel together with its links to mainstream media. Follow-ups: Marathe et al., ICTD 2015, "Revisiting CGNet Swara and Its Impact", and a 2016 comparison with the state-run Madhya Pradesh CM Helpline. — [ICTD12 PDF](https://billthies.net/assets/pdf/swara-ictd12.pdf); [ICTD16 PDF](https://billthies.net/assets/pdf/ictd16-swara.pdf)
- **Interface design matters for success rates.** In voice-based automated surveys among low-literate users in Lahore, task success ranged from **0 to 75%** depending on interface design (Raza et al., 2016). — [PDF](https://www.aghaaliraza.com/publications/2016--DEV--Real-time_Automated_Surveys_among_Low-literate_Masses_using_Voice-based_Telephone_Services.pdf)
- **Teach-back (clinical literature, not HCI4D).** A 2016 JBI systematic review found positive but not always significant effects. In an ED RCT with low-health-literacy patients, teach-back did **not** improve general comprehension of diagnoses, but it **significantly improved comprehension of self-care, follow-up and medication**. Reviews note gains are harder to detect in people with low literacy. — [PMC review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12680514/); [Fed Pract](https://www.mdedge.com/fedprac/article/202182/health-policy/use-and-effectiveness-teach-back-method-patient-education-and/page/0/3)

### Inferences
- For Pakkam, a "peer voice" layer (short clips from real beneficiaries describing how they claimed a scheme) is directly supported by Patel 2012. It is likely to raise engagement more than an official-sounding TTS voice.
- Teach-back works best for **action steps** (documents, office, dates), not abstract eligibility rules. Pakkam should confirm the next action ("so tomorrow you will take your Aadhaar and ration card to the VAO office?"), not quiz policy details.
- Spoken dialog alone leaves about 28% of users unable to finish (Medhi ToCHI). A minimal visual anchor such as one icon or photo per document, *shown sequentially rather than at the same time as speech* (WWW 2007), could raise completion. Keep it optional because of the confusion risk.
- A voice-forum or peer-moderation model is credible. Sangeet Swara shows low-literate communities can moderate content.

### Gaps
- No found study quantifies the effect of **repetition** or **local dialect vs standard language** on comprehension in IVR. Both are widely recommended, but I found no effect size.
- No found RCT of "someone like me" narrative audio specifically for welfare uptake. Patel 2012 is the closest evidence, but it is about agriculture.
- Exact statistics from Patel 2012 (effect size, p-values) were not verified from the full text.

## 2. Trust and comprehension: official document vs local/peer voice vs human in the loop; "show your source"

### Takeaway
Behavioural evidence favours **peer voices for engagement**, while stated trust favours authorities (Patel 2012). Evidence from welfare access shows that **information alone does not help illiterate people; hands-on human help (form filling, accompaniment) does** (Gupta, Delhi RCT 2015). No rigorous study was found on "show the source" for low-literacy voice users. That is a genuine research gap, and Pakkam could lead on it.

### Cited Findings
- **Welfare-specific RCT (Sarika Gupta, Harvard; Delhi slums, summer 2015; >1,200 women eligible for the widow pension but not enrolled; 75 slums; 4 arms).**
  - Information only: no significant average effect. It raised applications by **14 pp for literate women and had no effect on illiterate women**.
  - Information plus form filling: +6 pp, about 40% over control, with **equal effect for literate and illiterate women, closing the gap**. It helped women with fewer political connections more.
  - Information plus form filling plus accompaniment to the MLA's office: +11 pp, about 70% over control. It helped low-autonomy women most (+16 pp).
  - Author's conclusion: transaction costs, not just information, keep eligible people out.
  - — [Ideas for India, 14 May 2018](https://www.ideasforindia.in/topics/poverty-inequality/who-does-not-get-caught-by-social-safety-nets)
- **Peer vs authority.** Users said they preferred scientists but acted on peers (see section 1). — [Patel et al. 2012](https://hci.stanford.edu/publications/paper.php?id=195)
- **Channel trust in India.** An IIIT-Delhi usability study found participants trusted a web interface more than a human or an IVR. This compares channels, not voice types. — [IIIT-D repository](https://repository.iiitd.edu.in/jspui/handle/123456789/13)
- **Synthetic vs human voice.** A South African blind randomised listening test (65 participants; Afrikaans, isiZulu, Sepedi; healthcare prompts) treats trust and authenticity of TTS vs human prompts as open questions. A 2022 non-low-literate study (n=118) found TTS was rated more eerie than recorded human voice, but **similar on likeability and trust**. — [DHASA journal](https://upjournals.up.ac.za/index.php/dhasa/article/download/6721/5077/27310); [Macquarie](https://researchers.mq.edu.au/en/publications/is-natural-necessary-human-voice-versus-synthetic-voice-for-intel/)
- **Generative AI for schemes, prior art.** Jugalbandi (Microsoft, AI4Bharat, OpenNyAI; 2023) is a WhatsApp voice/text bot for government schemes, piloted in Biwan, Haryana. It covered 10 languages and 171 of about 20,000 schemes by mid-2023. Microsoft acknowledged that "sometimes these models do make errors". MediaNama flagged stale scheme information as a risk. Gram Vaani community volunteers were evaluating it for Mobile Vaani. **No controlled accuracy or user outcome data was found.** — [Microsoft Source](https://news.microsoft.com/source/asia/features/with-help-from-next-generation-ai-indian-villagers-gain-easier-access-to-government-services/); [MediaNama](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/)
- **Human intermediaries for schemes.** Haqdarshak trains women "Haqdarshikas". About 1,000 active agents gathered more than 100,000 applications, but LEAD cautions that not all applications led to benefits. An RCT (Banerjee, Bussell, Gupta, Hanna, Olken) is registered (AEA RCT registry 3114, 2018) and has replication data, but I did not find published results. The LEAD/Krea impact evaluation in Chhattisgarh (1,618 Haqdarshika interviews, 12,676 citizen/SHG surveys) is listed as underway. — [AEA registry](https://www.socialscienceregistry.org/trials/3114); [LEAD note](https://ifmrlead.org/wp-content/uploads/2021/12/Innovations-for-SHGs_Chhattisgarh.pdf)

### Inferences
- The Delhi RCT is the most important evidence for Pakkam's product thesis. **A Q&A bot is the "information only" arm, which did nothing for illiterate women.** Pakkam's edge should be the voice equivalent of form-filling and accompaniment:
  - spoken document checklists
  - pre-filled application summaries the user can show at the office
  - a "walk me through the office visit" mode
  - hand-off to a human helper (Haqdarshak-style)
- "Show your source" for low-literacy users can be done by voice: play a short clip naming the document, issuing department, date and clause ("Tamil Nadu government order, March 2025, says..."). Pair it with a peer clip for motivation. Dual sourcing (authority for truth, peer for action) reconciles the stated vs revealed preference gap in Patel 2012. This is an inference, not a tested result.
- Staleness is a known failure mode (MediaNama on Jugalbandi). Speaking a "last verified on" date is cheap and builds trust.

### Gaps
- No peer-reviewed study found that tests whether citing an official document aloud increases trust or comprehension among low-literacy users.
- No India-specific controlled comparison of TTS vs human-recorded voice for trust was found.
- Haqdarshak RCT results were not found (they may exist in a working paper that did not surface).

## 3. Group and shared-phone use (family phone, SHG meetings, speakerphone, call-back)

### Takeaway
Shared and borrowed phones are the norm for many rural Indian women, often under family supervision. In Kilkari, **husbands frequently listened to messages meant for women who did not own phones**. Designs must assume multiple listeners and low privacy. SHGs are a proven distribution channel for voice services (Mobile Vaani evaluation, Haqdarshak), but I found no controlled study of speakerphone group sessions.

### Cited Findings
- 47% of Indian women who access a phone borrow rather than own it, vs 16% of men (Harvard Kennedy School study). Women preferred, or were expected, to use phones in front of family. Some had to share passcodes. — [LEAD/IFMR blog](https://ifmrlead.org/whose-phone-is-it-anyway-how-women-users-navigate-shared-access-privacy-and-leisure-in-india/); [Down To Earth](https://www.downtoearth.org.in/amp/story/science-technology/many-indian-women-denied-mobile-phones-to-keep-them-pure--62024)
- Women often use a common household phone managed by the male head of household, or borrow from community contacts (Dvara Research review). Shared-device workarounds include deleting call logs and timing usage (citing Sambasivan et al., 2018). — [LEAD/IFMR](https://ifmrlead.org/whose-phone-is-it-anyway-how-women-users-navigate-shared-access-privacy-and-leisure-in-india/)
- **Kilkari qualitative finding.** Women who owned and controlled their phones were the actual listeners. Among women without their own phones, husbands often listened. — [BMJ Global Health supplement](https://gh.bmj.com/content/6/Suppl_5/e005512.abstract)
- **Mobile Vaani health evaluation.** A quasi-experimental before-and-after study among SHG members measured knowledge of maternal and child nutrition, family planning and diarrhoea. Only 23% of women interviewed had heard of Mobile Vaani, which shows reach limits even with SHG distribution. — [PMC9558784](https://pmc.ncbi.nlm.nih.gov/articles/PMC9558784)
- **Grievance baseline (Gram Vaani and IIT Delhi).** Awareness of government grievance systems was low (37%) and use was low (51%) among beneficiaries. The pilot used community-reporter volunteers across 4 districts (ICTD 2017). — [IIT-D PDF](https://www.cse.iitd.ac.in/~aseth/improving-grievance-redressal.pdf)

### Inferences
- Pakkam should support a **"family mode / speaker mode"** in which the assistant expects several voices and summarises for "everyone listening". It should also support a **private-callback mode**: the woman requests a call-back at a time she picks, with a neutral caller ID and no sensitive content in the opening sentence.
- An **SHG meeting mode** fits the evidence on intermediaries. One facilitator phone on speaker runs a 5-minute scheme briefing and a group checklist ("who here has a ration card?"). Diarization could log per-person follow-ups. This is untested.
- Gendered access means scheme information for women (widow pension, maternity benefit) may reach husbands first. Include a short "this benefit is for her; she must apply herself" line.

### Gaps
- The full text of Sambasivan et al. (CHI 2018, shared phones / privacy) was not retrieved.
- No evaluated study of speakerphone group IVR sessions or SHG-meeting voice tools was found.

## 4. Proactive voice (outbound calls and reminders): Kilkari, mMitra, PxD, ARMMAN

### Takeaway
Outbound voice at national scale produces **small but real behavioural effects**:
- Kilkari: +2.8% immunisation at 10 weeks and more reversible contraception, but no change in the primary breastfeeding outcome.
- mMitra: improved knowledge, practices and birth weight in a pseudo-RCT.
- PxD meta-analysis: +11.3% lime adoption.

**Targeted human follow-up calls chosen by ML** (ARMMAN restless bandits) cut engagement drop-off by about 32%. The lesson for Pakkam: reminders work modestly, and targeting the right people for a human touch works better.

### Cited Findings
- **Kilkari RCT (Madhya Pradesh, 2018 to early 2020; n=5,095 pregnant women; up to 72 messages).** About 65% of the intervention arm listened to at least 50% of content. The primary outcome (exclusive breastfeeding) showed no significant change. Immunisation at 10 weeks was 2.8% higher (RR 1.03, 95% CI 1.00–1.06, p=0.048), and use of modern reversible contraception rose. Kilkari did not close equity gaps by wealth or education. It was cost-effective. BMJ Global Health 2022 describes it as the first RCT of a direct-to-beneficiary mobile programme at scale. — [PMC9288869](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9288869/); [BMJ GH](https://gh.bmj.com/content/6/Suppl_5/e008838.full)
- **mMitra (ARMMAN, Mumbai, 2015–2017; pseudo-randomised, single-blind; 1,516 intervention, 500 control).** Two voice messages a week from pregnancy to the infant's first birthday. Improved maternal health practices, infant-care knowledge and birth weight. Caveats: not fully randomised, and the team reported difficulty measuring hard outcomes. — [JMIR mHealth 2019](https://mhealth.jmir.org/2019/8/e14668); [BMC Public Health](https://bmcpublichealth.biomedcentral.com/track/pdf/10.1186/s12889-020-08965-2)
- **ARMMAN and Google Research restless multi-armed bandits (AAAI 2022; about 23,000 beneficiaries; 7 weeks).** ML-selected human service calls gave the largest, statistically significant reduction in cumulative engagement drops: **32% vs standard of care** (Google blog figure). The NGO deployed it weekly. A later paper notes about 38% of mothers stop listening. — [AAAI 2022](https://ojs.aaai.org/index.php/AAAI/article/view/21460); [Google Research blog](https://blog.research.google/2022/08/using-ml-to-boost-engagement-with.html?m=1); [AAAI 2023](https://ojs.aaai.org/index.php/AAAI/article/view/26672)
- **Listenership ≠ knowledge.** A 2024 arXiv paper (Harvard/Google with ARMMAN) notes that no correlation had been shown between listenership and knowledge gains, and runs knowledge surveys. Its results were not retrieved. — [arXiv 2407.11973](https://www.arxiv.org/pdf/2407.11973)
- **PxD.**
  - A meta-analysis of 6 studies (Kenya/Rwanda) found +11.3% agricultural lime adoption from advisory SMS. Four of the six studies were run by PxD.
  - An Odisha (Ama Krushi) RCT reports higher production and profits and less crop loss (Cole et al., 2025 working paper, not checked).
  - Cole et al. (2020, Gujarat cotton): weekly push calls plus visual aids raised fertiliser use.
  - GiveWell rates the evidence as moderate quality with wide confidence intervals, a "modest update".
  - — [PxD@10](https://precisiondev.org/pxd10-a-decade-of-evidence-driven-impact/); [GiveWell](https://www.givewell.org/node/3479); [PxD 2024 Annual Report](https://precisiondev.org/wp-content/uploads/2025/05/2024-PxD-Annual-Report_270525.pdf)

### Inferences
- For welfare schemes, a proactive call is best for **deadline- and event-triggered nudges**: application windows, eKYC deadlines, instalment credited or missed, renewal due. It is weaker as generic content.
- An "ARMMAN-lite" approach fits in a 2-3 day build: score users at risk of dropping off (for example, started an application but no follow-up in X days) and route only them to a human volunteer call-back. A full RMAB is not needed for a demo; a heuristic is enough.
- Kilkari's flat equity results warn that outbound voice alone does not reach the most marginalised. Combining it with human help (section 2) is the evidence-based fix.

### Gaps
- No found RCT of outbound voice reminders for **welfare scheme enrolment** specifically (as opposed to health or agriculture).
- Immunisation-reminder RCTs outside Kilkari/mMitra were not retrieved in this pass.

## 5. Emerging voice capabilities (2025-2026) and ethical guidance

### Takeaway
Regulators treat emotion inference from voice as high risk. The EU AI Act **bans emotion recognition from biometric data (including voice) in workplaces and education** from 2 Feb 2025, with medical and safety exceptions only. Text-only sentiment analysis falls outside the ban. For Pakkam, frustration or confusion detection is best framed as conversational repair signals (repeats, long silences, "puriyala" / "samajh nahi aaya"), not emotion inference. I did not find authoritative sources on Indian voice-cloning consent rules or on Gnani-specific capabilities.

### Cited Findings
- EU AI Act Art. 5(1)(f): workplace and education emotion recognition from biometric data is prohibited from 2 Feb 2025. The Commission's draft guidelines give voice-based anger tracking of call-centre staff as an example. The exception covers medical and safety uses only, and general wellbeing is not covered. Text sentiment is out of scope. Rules for other high-risk emotion-recognition systems apply from 2 Dec 2027 (as reported). — [Lewis Silkin, Feb 2025](https://www.lewissilkin.com/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011); [CX Today](https://www.cxtoday.com/contact-center/contact-center-emotion-ai-eu-rules/)
- Jugalbandi shows the 2023 baseline architecture: Indic STT (AI4Bharat) plus an LLM plus TTS over WhatsApp voice notes for schemes. Pakkam's core Q&A is therefore not novel by itself. — [Microsoft Source](https://news.microsoft.com/source/asia/features/with-help-from-next-generation-ai-indian-villagers-gain-easier-access-to-government-services/); [Thoughtworks](https://www.thoughtworks.com/en-ca/clients/jugalbandi)

### Inferences
- **Consent-based voice cloning of a trusted local person** (an SHG leader or a beneficiary who agrees, with recorded consent and a spoken disclosure such as "this is an AI voice of Selvi akka, used with her permission") is a possible way to combine Patel's peer-voice effect with scalable TTS. It carries ethical risk (impersonation, deepfake norms). It needs explicit consent, revocability and disclosure. No evidence was found on how low-literate users perceive cloned voices.
- **Two-party listening** (the assistant listens on speaker while the user talks to an office clerk or a CSC operator, then explains what was said or flags missing documents) is novel and buildable. It raises consent issues for the third party, so it should announce itself and be opt-in.
- **Diarization** is useful for family and SHG mode: it tracks who asked what and can give per-person checklists.
- **Code-mixed speech** (Tanglish/Hinglish) is table stakes. Gnani's code-mix accuracy was not verified here.

### Gaps
- Gnani.ai's actual 2025-26 features (diarization, emotion, cloning, streaming) were not verified. Check vendor docs.
- India's DPDP Act 2023 / DPDP Rules 2025 as they apply to voice data, and MeitY guidance on synthetic media or deepfake labelling, were not retrieved.
- No HCI4D study was found on low-literate users' reactions to AI-cloned or synthetic peer voices.

## 6. Concrete ideas ranked by evidence strength × novelty (2-3 day build on existing STT + TTS + grounded backend)

### Takeaway
Ideas built on the *action* gap (Delhi RCT) and *peer voice* (Patel 2012) have the strongest evidence and are clearly different from Jugalbandi-style Q&A. Ideas using emerging capabilities (two-party listening, consented voice cloning) are the most novel but the least evidenced.

### Cited Findings (evidence anchor per idea; see sections above for details)
1. **"Kaagaz Checklist + Office Walkthrough" (voice equivalent of form-filling and accompaniment).**
   - What it does: after eligibility, Pakkam speaks one document at a time, asks "do you have it? say yes/no", builds a spoken and shareable checklist, then rehearses the office visit (where, whom to meet, what to say).
   - Evidence: **strong**. Form help closed the literate/illiterate gap, and accompaniment had the largest effect. — [Gupta, Ideas for India 2018](https://www.ideasforindia.in/topics/poverty-inequality/who-does-not-get-caught-by-social-safety-nets)
   - Novelty: medium-high.
2. **"Someone Like Me" peer clips.**
   - What it does: plays a 20-second recorded testimonial from a real local beneficiary of the same scheme (matched by district or occupation) before or after the official answer.
   - Evidence: **strong (behavioural)**. — [Patel et al. ICTD 2012](https://hci.stanford.edu/publications/paper.php?id=195)
   - Novelty: high for welfare bots.
3. **Action teach-back.**
   - What it does: at the end of a session the assistant asks the user to say the next step back. It repairs gaps with a re-explanation, not a repeat.
   - Evidence: **moderate**. Improves self-care and action comprehension even in low-health-literacy patients. — [Fed Pract RCT summary](https://www.mdedge.com/fedprac/article/202182/health-policy/use-and-effectiveness-teach-back-method-patient-education-and/page/0/3)
   - Novelty: medium.
4. **Spoken source and "last verified" stamp.**
   - What it does: every grounded answer ends with "this is from <department> <GO number/date>; checked on <date>". The user can say "send this to my son" to forward the source.
   - Evidence: **weak or indirect** (stale-information risk, authority preference). — [MediaNama](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/)
   - Novelty: medium. This is also a research opportunity.
5. **Deadline-triggered outbound call-back plus risk-targeted human follow-up.**
   - Evidence: **moderate-strong** for reminders (Kilkari +2.8% immunisation, PxD +11.3% adoption) and **strong** for ML-targeted human calls (ARMMAN −32% drop-off). — [Kilkari](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9288869/); [AAAI 2022](https://ojs.aaai.org/index.php/AAAI/article/view/21460)
   - Novelty: medium for welfare.
6. **Family/SHG speaker mode with diarization.**
   - What it does: multi-listener summaries, per-person checklists, and a facilitator script for SHG meetings.
   - Evidence: **moderate (contextual)** for shared phones and the SHG channel; untested as a design. — [LEAD](https://ifmrlead.org/whose-phone-is-it-anyway-how-women-users-navigate-shared-access-privacy-and-leisure-in-india/); [Kilkari qual](https://gh.bmj.com/content/6/Suppl_5/e005512.abstract)
   - Novelty: high.
7. **Private call-back for women** (user-chosen time, discreet opening line).
   - Evidence: **moderate (contextual)**: 47% of women borrow phones, and husbands listen to Kilkari. — [LEAD](https://ifmrlead.org/whose-phone-is-it-anyway-how-women-users-navigate-shared-access-privacy-and-leisure-in-india/)
   - Novelty: medium.
8. **Confusion-repair loop** (detects repeats, silence or "puriyala", then slows down, simplifies, or offers a human).
   - Evidence: **indirect**. Spoken dialog completion was only 72%. — [Medhi ToCHI 2011](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ToCHI2711_Medhi.pdf)
   - Uses conversational signals, not biometric emotion recognition, to stay clear of EU-style restrictions. — [Lewis Silkin](https://www.lewissilkin.com/insights/2025/02/17/understanding-the-eu-ai-acts-prohibited-practices-key-workplace-and-advertising-102k011)
   - Novelty: medium.
9. **"Office companion" two-party listening** (opt-in, announced; explains what the clerk said and flags missing documents).
   - Evidence: **none direct**. It is extrapolated from the accompaniment effect in the Delhi RCT.
   - Novelty: very high. Ethics risk: third-party consent.
10. **Consented cloned local voice** (an SHG leader's voice with disclosure).
    - Evidence: **none direct** (peer effect plus unclear TTS trust effects). — [Patel 2012](https://hci.stanford.edu/publications/paper.php?id=195); [Macquarie TTS trust](https://researchers.mq.edu.au/en/publications/is-natural-necessary-human-voice-versus-synthetic-voice-for-intel/)
    - Novelty: very high. Highest ethics risk.
11. **Peer-moderated voice Q&A board per scheme** (users record tips; community upvotes).
    - Evidence: **moderate**. Sangeet Swara moderation was 98% accurate; CGNet Swara shows sustained use. — [CACM](https://cacm.acm.org/research/the-internet-of-the-orals)
    - Novelty: low-medium (well-known pattern). It takes more than 3 days to seed with content.

### Inferences
- The best demo combination for a 2-3 day build is idea 1 plus idea 2 plus idea 3 (checklist → peer clip → teach-back), with idea 4 woven in. Each step maps to a specific cited finding, which makes for a defensible pitch: "Q&A bots are the information-only arm that the Delhi RCT showed does nothing for illiterate women; Pakkam is the form-help and accompaniment arm, in voice."
- Ideas 9 and 10 are the "wow" differentiators but should be shown as consented, disclosed prototypes.

### Gaps
- None of the ranked ideas has been tested as a voice-only intervention for welfare schemes. Effect sizes are borrowed from adjacent domains (health, agriculture, in-person assistance).
- Elderly-specific voice UI evidence (pace, hearing loss, TTS speed) for India was not found in this pass.
