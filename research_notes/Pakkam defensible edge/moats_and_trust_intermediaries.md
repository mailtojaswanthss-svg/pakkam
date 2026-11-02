# Durable advantages ("moats") of small mission-driven voice/AI services for low-income and low-literacy users versus big general AI assistants

Research date: 2026-11-02. About 17 tool calls. Most sources are organisation reports, peer-reviewed or arXiv papers, and launch coverage. Where a figure is self-reported by the organisation, it is labelled as such.

## Q1. Which services for underserved users kept winning despite big-tech alternatives, and what was their moat?

### Takeaway
None of the durable cases rests on a technology advantage. The ones that lasted rest on one of four things:
- a paid or embedded human network (Haqdarshak's agents, Digital Green's extension workers, ARMMAN's link to the health system);
- government adoption that made the service the official channel (Kilkari through MoHFW);
- a channel that needs no smartphone (IVR in Mobile Vaani and Kilkari);
- outcome evidence from RCTs that wins funders and government contracts (PxD, ARMMAN, Digital Green).

Note that rigorous evidence of *outcomes* is often weaker than evidence of *reach*, even for the best-known services.

### Cited Findings

**Haqdarshak (welfare-scheme access through women agents; founded 2016)**
- Haqdarshak reports reaching over 6.3 million citizens, unlocking $2.1 billion in government benefits, and training over 25,000 women field agents. Acumen's 2024 case study repeats these figures, but they are company-reported — [Acumen case study](https://acumen.org/case-studies/haqdarshak/)
- Screening and eligibility checks are free. Citizens can pay an agent "a small fee to apply on their behalf." Haqdarshak also sells a SaaS platform to corporate partners for their informal workers. The fee amount and the margins are not disclosed — [Acumen](https://acumen.org/case-studies/haqdarshak/)
- Why the service needs humans: many citizens don't know the schemes exist, agents go door-to-door, and most beneficiaries lack the documents an application needs, so hands-on help is part of the product. The scheme database covers over 7,500 schemes in 13 languages — [Acumen](https://acumen.org/case-studies/haqdarshak/)
- Haqdarshak's original agents were men. An Omidyar Network Lean Data study found a stronger impact from women agents, because women often cannot leave the village and have few local jobs, so the company shifted to women agents (over 60% of agents were women in 2022) — [Acumen](https://acumen.org/case-studies/haqdarshak/)
- 2020 agent survey (self-reported): 90% of agents said they had improved family income, and 94% of women agents said they received more respect. Haqdarshak's own site reports about 7,000 women trained, of whom about 3,000 are consistently active, earning around INR 3,300 a month. Note how far this is from the "25,000 trained" headline — [Acumen](https://acumen.org/case-studies/haqdarshak/); [Haqdarshak site via search](https://haqdarshak.com/?p=6929)
- An IFMR LEAD study of SHG women in Chhattisgarh found that 67% (n=2,302) had used the app to enrol themselves, their families or neighbours in 139 schemes. The study raises questions about the sustainability of the model and about framing these women as entrepreneurs — [IFMR LEAD PDF](https://ifmrlead.org/wp-content/uploads/2021/12/Innovations-for-SHGs_Chhattisgarh.pdf)
- July 2024: a Mastercard Center for Inclusive Growth partnership aims to strengthen 1,000 women agents serving 500,000 micro and small enterprises. This is evidence of B2B and CSR funding of the agent channel — [Mastercard press release](https://www.mastercard.com/news/ap/en-in/newsroom/press-releases/en-in/2024/july/haqdarshak-and-mastercard-center-for-inclusive-growth-collaborate-to-empower-500-000-small-businesses-and-agri-entrepreneurs)

**ARMMAN mMitra and Kilkari (maternal voice calls)**
- Kilkari impact RCT in four districts of Madhya Pradesh (2018–2020, about 5,095 women):
  - No significant effect on the primary outcome, exclusive breastfeeding.
  - Higher use of modern reversible contraception.
  - Immunisation at 10 weeks about 2.8 percentage points higher, with no difference on most other outcomes.
  - Where women did not own a phone, husbands often took the calls instead.

  — [BMJ Global Health supplement](https://gh.bmj.com/content/6/Suppl_5/e008838.full); [ClinicalTrials.gov NCT03576157](https://clinicaltrials.gov/study/NCT03576157)
- Engagement RCT (Nov 2022–Feb 2023): ARMMAN used AI (a restless multi-armed bandit model, with Google DeepMind and IIT Madras) to decide which women got a live human service call. It reports up to 32% fewer drop-offs among high-risk women — [ARMMAN mMitra](https://www.armman.org/mmitra/)
- A 2025 RCT (over 34,000 beneficiaries) reports that AI-targeted *human* calls improved health behaviours, such as iron and calcium intake after delivery, and not just listenership — [arXiv 2507.20755](https://arxiv.org/pdf/2507.20755)
- Google DeepMind supports AI models for Kilkari pro bono. Rollout depends on MoHFW approval, so the government gate controls deployment — [ARMMAN](https://www.armman.org/mmitra/)

**Digital Green (video extension, then Farmer.CHAT)**
- Early RCT evidence for video extension: about 10x more cost-effective per adoption ($35 down to $3.50). In Bihar the videos cost INR 96 (US$1.60) per farmer, and the added profit was about 16x the added cost — [J-PAL evaluation](https://www.povertyactionlab.org/evaluation/evaluation-digital-greens-agricultural-extension-program-india?lang=id); [Digital Green](https://digitalgreen.org/?p=1973)
- Farmer.CHAT is built for extension agents, not for farmers directly: over 4,500 extension agents in Kenya and India were using it by 1 January 2024. Digital Green and OpenAI estimate it could cut extension cost 100x, from $35 to $0.35 per farmer. This is an unverified early estimate — [OpenAI customer story](https://openai.com/index/digital-green)
- Digital Green reported FY23 cost per farmer reached of $5.00 and cost per adoption of $6.50, across its whole programme — [Digital Green 2023 Annual Report](https://digitalgreen.org/wp-content/uploads/2024/03/2023-Annual-Report.pdf)
- Note that Digital Green builds Farmer.CHAT *on* OpenAI models, so its moat is the channel and the content, not the model.

**Precision Development (PxD)**
- Krishi Tarang in Gujarat (cotton and cumin, about 1,200 farmers): about $100 a year in added net income per farmer, at under $10 a year in cost, a benefit-cost ratio of about 10:1. Yields rose 8.6% for cotton and 28% for cumin — [PxD Krishi Tarang](https://precisiondev.org/project/krishi-tarang-gujarat/)
- PxD reports an average cost of $0.94 per user per year in 2024. GiveWell's preliminary estimate is about $1.80 per household reached per year — [PxD 2024 Annual Report](https://precisiondev.org/wp-content/uploads/2025/05/2024-PxD-Annual-Report_270525.pdf); [EA Forum/GiveWell](https://forum.effectivealtruism.org/topics/precision-development)
- PxD's model scales through government partners, and it runs a public registry of A/B experiments. The registry is the evidence engine behind its funding — [PxD registry](https://registry.precisiondev.org/registry_entry/cumin-experiment/)

**Gram Vaani Mobile Vaani (IVR community media)**
- Mobile Vaani works over IVR, so users need no data plan or smartphone. It runs on community-contributed audio and local volunteer clubs. Gram Vaani reports use in more than 80 districts across 10 states — [arXiv 2104.07901](https://arxiv.org/pdf/2104.07901); [ITU WSIS 2024](https://itu.int/net4/wsis/stocktaking/Prizes/2024/Details/16110584768637945)
- Gram Vaani's co-founder writes that after a decade, "the ideal [financial sustainability] model still remains elusive." The community-content moat has not turned into a self-sustaining business — [Seth, arXiv 1907.06360](https://arxiv.org/pdf/1907.06360.pdf)
- GSMA (2024) cites Mobile Vaani as a case study in language and humanitarian action — [GSMA M4D](https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2024/04/Language-and-Digital-Humanitarian-Action_CaseStudies_MobileVaani_R.pdf)

**Karya (paid data work)**
- Karya is a nonprofit that pays rural workers (it states a $5 hourly minimum), gives them de facto ownership of the data they create, and passes resale proceeds back to them. It reports about 30,000–35,000 workers across 22–24 states, and the figures vary by source — [Karya impact](https://www.karya.in/impact); [Yahoo/Time-derived coverage](https://tech.yahoo.com/ai/articles/workers-behind-ai-rarely-see-104446022.html)
- Its core platform will stay open source, so any moat is the worker network and the local-language data supply, not the software — [Karya](https://www.karya.in/impact)

### Inferences
- In every case that lasted, the hard-to-copy asset was **people plus institutional embedding**: Haqdarshak's agent network and document handling, ARMMAN's link to the health system, Digital Green's extension agents, PxD's government contracts. Features, models and apps were not the asset. Digital Green and Jugalbandi both run on OpenAI/Azure models, which shows that the model is a commodity input.
- **Last-mile completion** (documents, form filling, follow-up) is where Haqdarshak earns its fee. An answer engine on its own (eligibility information) is the part big assistants copy most easily.
- **Outcome evidence** (RCTs, the PxD registry, ARMMAN's RCTs) acts as a funding and government-procurement moat. Big tech assistants do not run outcome RCTs on welfare uptake.
- Mobile Vaani shows that community content and an IVR channel can build loyalty without building a sustainable business, which is a warning for any voice-only model.

### Gaps
- I found nothing current on CGNet Swara, Awaaz.De, Simprints, SEWA's digital tools or Khushi Baby's own platform within the call budget.
- I found no independent evaluation of Haqdarshak application *success rates* (approval as opposed to application).
- I could not confirm Kilkari's current national scale (reported in the millions) from a primary source in this pass.

## Q2. Do trust intermediaries drive adoption more than direct-to-citizen apps in India, and what happens when AI tools are built for the intermediary?

### Takeaway
HCI4D research since 2010 shows that intermediated use is the norm, not the exception, among low-literacy users in India. The strongest recent AI deployments (ASHABot, Farmer.CHAT, Haqdarshak's app) are built for the intermediary. ASHABot shows that intermediaries want a private, accurate, government-endorsed tool and trust it more when it says "I don't know." The weak link is unpaid expert reviewers.

### Cited Findings
- Sambasivan, Cutrell, Toyama and Nardi (CHI 2010, Best of CHI honorable mention) studied two Bangalore slums. Digitally skilled people routinely give others access to technology (they describe proximate enabling, proximate translation and surrogate use), which lets people who are non-literate or lack skills or money still benefit — [Microsoft Research](https://microsoft.com/en-us/research/?p=159423); [Sambasivan dissertation, UC Irvine](https://escholarship.org/content/qt6r24q4cb/qt6r24q4cb.pdf?t=ozq64x)
- Parikh and Ghosh (IEEE Pervasive Computing) argue that designs must serve both the primary user (the intermediary) and the secondary user (the beneficiary). Ghosh (CHI 2016) extends the finding to India and Ghana — [search result index](https://core.ac.uk/download/232196189.pdf)
- **ASHABot** (Khushi Baby with Microsoft Research, CHI 2025) ran with 20 ASHAs and 15 ANMs in Salumbar, Rajasthan, over 107 days (May–August 2024), on WhatsApp with Hindi voice and text — [arXiv 2409.10913](https://arxiv.org/html/2409.10913v3)
  - ASHAs sent 1,761 messages: 1,040 were taps on suggested "related questions," 470 were audio and 251 were typed. About 91.5% were clinical.
  - The bot answered "I don't know" to 16.4% of questions and forwarded 264 clinical questions to ANMs.
  - Expert-rated accuracy was 85% or higher in every evaluation (87.88% against doctor ground truth). In the pilot, 273 of 374 answers were accurate and complete, 9 inaccurate and 75 "I don't know."
  - 95.7% of ASHA poll responses rated the bot helpful.
  - Trust rose when the bot admitted it did not know. One ASHA linked her trust to the government's role in onboarding: "whatever the government says is correct."
  - It worked as a private channel for sensitive questions. One ASHA said: "I cannot openly ask the Doctor sir about white discharge."
  - An ANM said Google "does not give me a short answer," meaning web search results were too long and unfocused.
  - The weak point was ANM reviewers: they received 6,915 prompts but produced only 19 consensus answers, often after the ASHA had already found an answer. They had no incentive, feared exposure ("Everyone will know that I don't know"), and the authors call the expert-in-the-loop model's sustainability an open question.
- A later news report puts ASHABot at 869 ASHAs onboarded and about 24,000 messages since early 2024 in Udaipur district. This is a secondary source — [Rasonly](https://rasonly.com/current-affairs/ai-enabled-asha-bot-empowering-rural-healthcare-in-udaipur)
- ARMMAN's best 2025 result came from AI deciding *which women get a human call*, not from AI replacing the human — [arXiv 2507.20755](https://arxiv.org/pdf/2507.20755)
- Farmer.CHAT's users are extension agents (over 4,500 by January 2024), not farmers directly — [OpenAI](https://openai.com/index/digital-green)
- Haqdarshak's IFMR study: SHG women used the app for themselves *and their neighbours*, which is the intermediary pattern — [IFMR LEAD](https://ifmrlead.org/wp-content/uploads/2021/12/Innovations-for-SHGs_Chhattisgarh.pdf)
- Kilkari: on shared household phones, husbands often answered the calls, so direct-to-citizen voice reached the intended woman unreliably — [BMJ GH](https://gh.bmj.com/content/6/Suppl_5/e008838.full)

### Inferences
- For Pakkam, a tool aimed at the intermediary — e-Sevai operators, SHG leaders, anganwadi workers or Haqdarshak-style agents in Tamil Nadu — matches the strongest evidence. Page-cited answers suit intermediaries, because they must justify advice to the beneficiary and the official. An honest "I don't know" with escalation builds trust, as ASHABot found.
- Human-signed facts are valuable but are also the bottleneck that breaks first. ASHABot's ANM loop collapsed without incentives, so Pakkam's sign-off process needs a paid or institutionally mandated reviewer, and must stay small (18 PDFs) to be sustainable.
- Government endorsement is itself a trust signal for intermediaries ("whatever the government says is correct"). A tie to the Tamil Nadu government or a district office may be worth more than any feature.

### Gaps
- I found no India RCT comparing an intermediary-delivered welfare tool with a direct-to-citizen welfare app head-to-head.
- I found no Tamil Nadu-specific evidence on e-Sevai operators using AI tools.

## Q3. Data moats versus distribution moats in AI (VC commentary), applied to public-interest AI

### Takeaway
The best-known VC position (a16z, 2019, repeated in 2025–26 commentary) is that data alone is rarely a moat. Defensibility comes from verticalisation, go-to-market and distribution, and trust. Proprietary data counts only when it is scarce or when the company is a trusted custodian. For public-interest AI, "verified, signed, cited" data is a trust moat more than a data moat.

### Cited Findings
- Martin Casado and Peter Lauten, "The Empty Promise of Data Moats" (a16z, 9 May 2019) — [a16z](https://a16z.com/the-empty-promise-of-data-moats/)
  - "defensibility is not inherent to data itself"
  - "There generally isn't an inherent network effect that comes from merely having more data"
  - data is "like a commodity," and its scale effects can reverse
  - what is defensible instead: verticalising (domain understanding built into the product), winning the go-to-market race, and team
  - the exception: data can be defensible when sources are scarce, when customers won't share data with multiple vendors, or when the company is a **trustworthy data custodian**
- 2025–26 secondary summaries of a16z roundtables and podcasts ("Why AI Moats Still Matter," December 2025) say moats have shifted from the technology stack (models, data) to the commercial stack (workflow integration, brand, go-to-market). These are secondary summaries, not a16z's own text — [StartupHub summary](https://www.startuphub.ai/news/why-ai-moats-still-matter-and-how-theyve-changed); [rosetta.to a16z](https://rosetta.to/u/a16z/why-ai-moats-still-matter-and-how-they-ve-changed)
- Commentary on a 2026 Andreessen piece, "the AI moat is not the model." This is secondary — [the-ai-corner](https://www.the-ai-corner.com/p/marc-andreessen-ai-moat-not-the-model-2026?r=1krivi)

### Inferences
- Pakkam's 18 official PDFs are public, so any assistant can ingest them. The corpus itself is *not* a moat. What could be defensible:
  - the human-signed verification layer (accountability for being right, the "trustworthy custodian" exception);
  - workflow embedding with intermediaries (go-to-market and distribution);
  - outcome data on which answers led to successful applications, which only arises from being in the workflow.
- Applied to public-interest AI, the distribution moat means institutional distribution (government, SHG federations, NGOs), not consumer marketing.

### Gaps
- I did not retrieve the primary texts of the Sequoia or NFX AI-defensibility essays. Their positions are not verified here.

## Q4. Has a big general assistant been tried for welfare, health or agriculture information in India and been outperformed by a specialised tool?

### Takeaway
I found no clean head-to-head study in which a specialised Indian welfare tool beat ChatGPT, Gemini or Meta AI. There is evidence that general models are less accurate in Indic languages and specialist domains. The bigger strategic fact is that big tech is not losing: Meta is becoming the government's WhatsApp channel itself (Andhra Pradesh, Maharashtra, Gujarat, 2025–26), and the Microsoft/AI4Bharat Jugalbandi pattern uses general models underneath.

### Cited Findings
- BhashaBench V1 (2025, English and Hindi across agriculture, legal, finance and Ayurveda): GPT-4o scores 76.49% in Legal but only 59.74% in Ayurveda, and the authors describe large domain- and language-specific gaps — [arXiv 2510.25409](https://arxiv.org/html/2510.25409v2)
- Factual-accuracy study (2025): models hallucinate more when responding in low-resource Indic languages than in English — [arXiv 2504.20022](https://arxiv.org/html/2504.20022v2)
- Health-myth study of GPT-3.5, GPT-4 Turbo and GPT-4o in Hindi, Malayalam, Marathi, Tamil and Telugu reports language-dependent safety asymmetries. I did not obtain the headline numbers — [arXiv 2511.01360](https://arxiv.org/html/2511.01360v1)
- Jugalbandi (Microsoft, AI4Bharat, OpenNyAI, May 2023) is a WhatsApp bot covering up to 171 government programmes, with AI4Bharat speech and Azure OpenAI reasoning — [Microsoft News](https://news.microsoft.com/en-in/features/with-help-from-next-generation-ai-indian-villagers-gain-easier-access-to-government-services/)
  - AI4Bharat's Pratyush Kumar: "sometimes these models do make errors."
  - Thoughtworks, which built it, warned that inaccurate information could seriously hurt people's ability to access schemes.
  - I found no independent outcome or adoption evaluation — [Thoughtworks](https://www.thoughtworks.com/insights/articles/ai-impact-what-enterprise-leaders-learn-jugalbandi); [MediaNama](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/)
- Meta's government WhatsApp deals (Llama-powered) — [MediaNama Apr 2025](https://www.medianama.com/2025/04/223-meta-whatsapp-llama-ai-e-governance-india/); [Business Today May 2026](https://businesstoday.in/technology/news/story/gujarat-govt-taps-meta-for-ai-led-governance-push-digital-citizen-services-on-whatsapp-533293-2026-05-26); [IBTimes Maharashtra](https://www.ibtimes.co.in/maharashtra-govt-partners-meta-whatsapp-based-citizen-services-880162)
  - Andhra Pradesh "Mana Mitra" (from January 2025): the state reports over 5.1 million transactions and more than 2.5 million citizens reached by March 2025.
  - Gujarat (May 2026): about 20 services planned, including certificates, ration card updates and grievances, with voice support for rural users.
  - Maharashtra: also announced.
- ASHABot users found Google too long and unfocused for their needs — [arXiv 2409.10913](https://arxiv.org/html/2409.10913v3)
- Survey context: Statista reports that about 80% of rural respondents did not believe most forwarded WhatsApp messages. The date and method are unverified — [Statista](https://www.statista.com/chart/amp/17644/rural-indians-trust-in-forwarded-whatsapp-messages)

### Inferences
- Tamil Nadu could sign a similar Meta/WhatsApp e-governance deal. A Pakkam pitched as a better general scheme Q&A for citizens would then compete directly with the government's own channel. Directions that survive this would complement it:
  - an intermediary tool, plus outcome evidence;
  - a verified and accountable answer layer (cited page plus human sign-off) that a government or Meta channel could license or link to;
  - completing applications and following up, where Haqdarshak earns its fee.
- Lower general-model accuracy in Indic languages narrows as models improve, so it is not a durable moat. The durable parts are accountability (named human sign-off, page citations) and institutional trust.

### Gaps
- I found no documented case of ChatGPT, Gemini or Meta AI being formally piloted for Indian welfare information and then withdrawn or beaten in an evaluation.
- I did not obtain results from the Telugu maternal-health comparison of ChatGPT-4o, Gemini and Perplexity (NIT Warangal) or from agriculture bots such as Kisan e-Mitra or Krishi Sathi.
- Mana Mitra figures come from the state government, with no independent evaluation.
