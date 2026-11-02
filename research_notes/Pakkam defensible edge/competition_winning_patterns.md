# Competition Winning Patterns: Voice-AI Hackathons, Especially Gnani.ai's (research date 2 Nov 2026)

## Q1. Gnani.ai competitions 2025-2026: rules, judging, prizes, emphasis

### Takeaway
The 10 Nov 2026 deadline belongs to Gnani.ai's **Great Indian AI Internship Challenge (GIAIC) 2026**. It is open-brief, has **no published scoring rubric**, and runs two separate tracks.
- **Ten ₹50,000 category awards**, each judged on its own criterion: regional language, code-mixed speech, real-world usefulness, noisy telephony audio, best 60-second demo, crowd votes, and others.
- **Internship shortlist**, which starts with *verified organic engagement on a public LinkedIn/X demo post*.

Winners won't be known until after 10 Nov, so there are no past winners. GIAIC 2026 is the first edition I found.

### Cited Findings
- **Basics:** The challenge is for students enrolled at Indian colleges, aged 18 or over, working solo or in a team of two. The brief is open ("no set problem statement"). It ran 1 Oct 2026 to 10 Nov 2026, 11:59 PM IST, a 41-day window. The deadline is fixed with no extensions. Internships begin 1 Jan 2027. — [Gnani internship page](https://www.gnani.ai/internship); [Gnani blog](https://www.gnani.ai/resources/blogs/great-indian-ai-internship-challenge-2026)
- **Theme:** The stated theme is "Build Sovereign AI for India." The tagline is "Intelligence that truly listens." The blog has no founder quotes. — [Gnani blog](https://www.gnani.ai/resources/blogs/great-indian-ai-internship-challenge-2026)
- **Models:**
  - Entries must use and name Gnani models or APIs: Prisma v2.5 (STT), Timbre v2.5 (TTS, beta) and Evon v3.3 (30B MoE with about 3.5B active parameters, open weights, Apache 2.0, 128K context).
  - Evon is not on the API platform. You request the weights on Hugging Face and host it yourself.
  - The agent builder is out of scope.
  - Prisma is described as trained on 14M+ hours of telephonic audio, streaming in under 200 ms, covering 10+ Indian languages plus code-mixed speech.
  - Source: [Gnani internship page](https://www.gnani.ai/internship); [Gnani blog](https://www.gnani.ai/resources/blogs/great-indian-ai-internship-challenge-2026)
- **Submission:**
  - A demo video of the app working.
  - A written explanation: title, problem, target users, models/APIs used, and each member's contribution.
  - One nominated LinkedIn/X post per platform, carrying both #GnaniAI and #GreatIndianAIInternshipChallenge. Tagging Gnani alone doesn't count.
  - Source: [Gnani internship page](https://www.gnani.ai/internship)
- **Ten awards of ₹50,000 each:** No team can win more than one. Awards are judged separately from internship selection.
  1. Main Character: regional or low-resource language
  2. Mixed Vibes: best code-mixed voice experience. Hinglish, **Tanglish** and Benglish are named.
  3. Real Deal: most useful real-world problem solved
  4. Noise Canceller: best performance on noisy telephonic audio
  5. Two-Person Army
  6. Solo Ninja
  7. Jugaad Genius: most creative or unexpected use of the models
  8. Small Town, Big Build: best entry from a Tier 2/3 town
  9. Demo Day Drop: best 60-second demo video
  10. Crowd Favourite: public votes on LinkedIn/X
  - Source: [Gnani internship page](https://www.gnani.ai/internship)
- **Internship selection order:**
  1. Engagement check: verified reactions, comments and reshares on nominated posts, counted at the cutoff
  2. Eligibility check: genuine use of Gnani technology
  3. Shortlist: eligible projects with the *strongest verified engagement*
  4. Individual interviews
  5. Offers, based on skills, interview performance and fit
  - Source: [Gnani internship page](https://www.gnani.ai/internship)
- **Prohibited:**
  - Bought engagement, bots, paid promotion, engagement swaps, plagiarism, and **misleading demos**. Demos that fake results are specifically called out.
  - Real phone numbers, Aadhaar, PAN, account numbers or recorded calls. Use synthetic data only. The page notes that voice data is personal data under the DPDP Act.
  - Source: [Gnani internship page](https://www.gnani.ai/internship); [Gnani blog](https://www.gnani.ai/resources/blogs/great-indian-ai-internship-challenge-2026)
- **Gnani's own example ideas:**
  - a Kannada farmer helpline (Main Character, Real Deal)
  - a Hinglish kirana phone-order assistant (Mixed Vibes, Real Deal)
  - a noisy phone-call summariser tested on synthetic calls (Noise Canceller)
  - a Tamil voice tutor (Jugaad Genius)

  The users it mentions are enterprises, developers, creators, farmers, kirana stores and rural health workers. — [Gnani internship page](https://www.gnani.ai/internship)
- **Other Gnani-linked event:** The India Agentic AI Open Hackathon, co-hosted with Sarvam and NVIDIA. Applications closed 19 Jun 2026, with in-person finals in Bangalore on 24-25 Jul 2026. I found no results. — [search summary citing openhackathons.org](https://www.openhackathons.org/s/siteevent/a0CUP00004gn7e32AA/se000496) (not fetched directly)
- **Competing teams already build in public:** The dhwani-desk team (Kannada civic-complaint line) planned a "teaser post a week before the main demo" to "start building organic engagement." The issue closed on 1 Nov. — [dhwani-desk issue #20](https://github.com/Pranav-0710/dhwani-desk/issues/20)

### Inferences
- **Two games are being played at once.**
  - The internship shortlist is gated first by organic social engagement. If Pakkam hasn't posted yet, a public demo post in the next 1-2 days matters as much as any feature, because engagement is measured at cutoff.
  - The awards reward a *single sharp axis*. Each award is one dimension, and a team can win only one.
- **Award categories that best fit Pakkam's existing assets:**
  - **Mixed Vibes** (Tanglish is named explicitly)
  - **Real Deal** (welfare schemes for citizens)
  - **Demo Day Drop** (a 60-second video)
  - **Noise Canceller**, only if it can be shown credibly
  - Main Character is a weaker fit, because Tamil and Hindi are not low-resource and many teams pick Tamil or Kannada.
- **Honest demos are a stated rule.** The "misleading demos" ban means a scripted or mocked demo should be labelled as such. Pakkam's verified, cited facts suit this rule.

### Gaps
- No numeric rubric or judge names are published for GIAIC.
- No past winners: this appears to be the first edition.
- I found no LinkedIn or X posts from Gnani judges saying what they want. Search surfaced only staff profiles promoting the challenge.
- I didn't verify whether the Discord holds extra guidance. It is private and not searchable.

## Q2. Winning projects at comparable voice/Indic AI events: what they share

### Takeaway
Across ElevenLabs, Harvard Kennedy AI for Good and Bhashini-linked events, winners share three things:
- one memorable live or viral moment
- voice as the core interface, not an add-on
- a concrete task for a named user

A grounded, voice-first government-scheme assistant has already won a top prize (MEGHA, Harvard, Apr 2025), so the concept is validated. It is also crowded: I found **at least 5 other GIAIC entries on welfare schemes**, several of them in Tamil.

### Cited Findings
- **ElevenLabs Worldwide Hackathon:**
  - It ran 40 hours, with results posted 28 Feb 2025, and drew 300+ projects. Judges included the CEOs of ElevenLabs, Vercel, PostHog and Lovable, plus two a16z partners.
  - The global winner, **GibberLink**, showed two AI agents on a phone call detecting each other and switching to a faster audio protocol. It was "viral" and chosen unanimously: one clear wow moment.
  - Procuro, NY 2nd, was "built after a 1 a.m. pivot," and judges were "impressed by its live demo." The fal.ai prize went to Playcade because judges "enjoyed seeing it run live."
  - Source: [ElevenLabs blog](https://elevenlabs.io/blog/announcing-the-winners-of-the-elevenlabs-worldwide-hackathon)
- **ElevenLabs online winners:**
  - Hugo, a tour guide, was praised for feature depth and a personalised, location-aware experience.
  - Pep, a physical-therapy voice coach, won 2nd for its "potential to improve lives."
  - Many winners were voice agents that call people or businesses to finish a task (Dealwise, Procuro).
  - Source: [ElevenLabs blog](https://elevenlabs.io/blog/announcing-the-winners-of-the-elevenlabs-worldwide-hackathon)
- **MEGHA (Meghalaya E-Governance Human-centered Assistance):**
  - Won 1st Prize at the Kennedy AI for Good Hackathon, Harvard Kennedy School, reported 28 Apr 2025.
  - It is "a toll-free, voice-first solution designed to bridge information asymmetry and digital-literacy barriers," and it works on any basic phone. Answers are "grounded in verified official documents."
  - The team included serving IAS/IRS/IPS officers. No user metrics were reported, and the article gives no judges' reasons.
  - Source: [Free Press Journal](https://www.freepressjournal.in/india/ai-solution-for-india-wins-top-spot-at-harvards-hackathon)
- **MultiLipi:** It claims to have won BHASHINI LEAP Hackathon Problem Statement 2: converting spoken regional-dialect statements into structured FIR drafts in under 90 seconds. This is unverified vendor marketing. — [MultiLipi for Government](https://gov.multilipi.com/)
- **Bhashini challenges:**
  - The 2023 Grand Innovation Challenge included live speech-to-speech translation with a voice-quality bar (DMOS >4.2). Each team received ₹1 lakh to improve its prototype.
  - Bhasha Techathon (2024, with Google Cloud and MachineHack) included a voice-to-text task for railway complaints in 22 languages.
  - The 2026 VYOMA challenge targets offline, low-connectivity, voice-first multilingual solutions.
  - I found no winner lists.
  - Source: [IndiaAI article](https://indiaai.gov.in/article/the-meity-introduced-bhashini-grand-innovation-challenge); [AIM](https://analyticsindiamag.com/google-cloud-bhashini-and-machinehack-come-together-for-bhasha-techathon/); [NewsX VYOMA](https://www.newsx.com/tech-and-auto/bhashini-launches-vyoma-challenge-to-build-offline-ai-solutions-in-indian-languages-229600/)
- **Sarvam "BuildIn' Hours":** A 12-hour event with 6,272 applicants and 100 selected. Its tracks were Voice AI, Document Intelligence, Multilingual AI and AI Agents. I found no winners. — [Digital Terminal](https://digitalterminal.in/tech-companies/zo-house-bengaluru-hosts-sarvam-ai-hackathon)
- **Competing GIAIC entries on welfare schemes (public GitHub, Oct-Nov 2026):**
  - **Kural** (Tamil scheme helpline on Prisma, Evon and Timbre). It answers only from retrieved knowledge-base passages, with the source attached. Other features:
    - BM25 plus character n-gram retrieval tuned for Tamil morphology and Tanglish
    - escalation of unanswered questions to a human officer as a callback ticket
    - an ffmpeg denoise pipeline with a per-call SNR estimate, and a simulated 8 kHz μ-law noisy-phone mode
    - a Twilio phone line and PII redaction
    - a 60-second demo video in the repo
    - 20/20 top-1 retrieval on a 20-question benchmark (a small set)
    - Its noisy-phone CER is not reported.
    - Source: [Kural](https://github.com/Mirdumurugesan/kural)
  - **JanVaani:** Covers 19 schemes in 9 languages, with Hinglish treated as a first-class dialogue language. Other features:
    - a deterministic five-verdict eligibility engine (the LLM never decides)
    - an 8 kHz browser softphone with barge-in
    - a printable CSC Ready Slip PDF with a QR code
    - a live Vercel demo with a scripted 60-second Kolar farmer run
    - It shows **no source-document citations** and **no accuracy numbers**.
    - Source: [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani)
  - **Others in the same space:** Urimai (Tamil voice eligibility screening with three-valued rule logic), Thunai (Tamil voice scheme navigator), tn-schemematch (code-mixed Tamil-English TN schemes, verdicts from a rule engine only), and Anganwadi Akka (Tamil/Tanglish). Several of these use Whisper, Web Speech or Gemini rather than Gnani. — [search results listing repos](https://github.com/rgokulkrishna44-debug/urimai), [Thunai](https://github.com/murali18-a/Thunai), [tn-schemematch](https://github.com/kanishk5676/tn-schemematch), [magalir-voice-ai](https://github.com/Bhavesh-Ram-G-V/magalir-voice-ai)
  - **Other GIAIC entries:** Bolo (voice form-filling, "the model proposes and code decides," 26/26 live multilingual eval cases, includes a farmer-scheme form), dhwani-desk (Kannada civic line with supervisor takeover), KisanSetu (farmers), Savdhaan (scam-call shield), Maatu (Kannada-Telugu ride translation). — [Bolo](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon); [dhwani-desk](https://github.com/Pranav-0710/dhwani-desk); [KisanSetu](https://github.com/aniket25042005/kisan_setu_gnani_ai_challenge); [Savdhaan](https://github.com/tejaspatel2255/savdhaan-gnani)
- **Pakkam's own README** (as indexed): "Voice is tested on clean read speech only; real phone recordings and spoken Tanglish are untested." — [Pakkam repo](https://github.com/mailtojaswanthss-svg/pakkam)

### Inferences
- **The common stack has become baseline.** Several GIAIC peers already advertise "the LLM never decides," grounding plus escalation, and an 8 kHz phone simulation. These are table stakes, not differentiators.
- **Where Pakkam can still stand out:**
  - **Page-level citations to official PDFs.** Kural attaches a "source"; JanVaani has none.
  - **Human-signed facts.**
  - **Four languages including Tanglish.**
- **Pakkam's most exposed weakness is also the cheapest gap to close.** Spoken Tanglish is untested, but Tanglish is named in the Mixed Vibes award. A small measured spoken-Tanglish eval (synthetic voices or teammates reading) plus a demo moment would turn that weakness into an award claim.
- **A "wow" moment Pakkam could own:** a caller asks in spoken Tanglish, and the assistant answers in Tamil by voice while the screen shows the exact page of the official PDF, the highlighted line and the human verifier's signature. Then it refuses a question the PDFs don't cover. This matches the GibberLink/Procuro pattern (one clear live moment) and MEGHA's winning framing ("grounded in verified official documents").
- **Depth over breadth.** Hugo won partly on feature depth, but most winners and judge advice favour one complete path. Breadth (19 schemes, 9 languages) is already JanVaani's angle.

### Gaps
- No published winner lists for any Bhashini, Sarvam, AI4Bharat or IndiaAI voice track. I couldn't find primary results pages.
- The MultiLipi win is unverified.
- I couldn't confirm which GIAIC repos will actually be submitted, or their final state.

## Q3. What judges say they want, and why strong projects lose

### Takeaway
Judges consistently reward:
- one complete end-to-end path, demoed live
- a one-sentence identity a judge can repeat
- a specific user
- honest naming of weaknesses

Projects lose by:
- spreading across half-built features
- opening with context instead of the product
- vague users
- blurring what was built
- relying on slides

### Cited Findings
- **Scoring dynamics:**
  - Rubric categories (difficulty, originality, design, impact, sponsor API use) compress, so most teams land mid-range. Winners separate on factors the rubric doesn't name.
  - Judges rank projects against the others they've just seen, not against an ideal.
  - Narrow projects consistently scored higher.
  - Source: [Kurbaitaev, DEV, Jul 2026](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l)
- **Reasons projects lost ground:**
  - opening with market size or a personal story
  - showing many half-built paths
  - vague users ("Athletes" was not enough)
  - blurring which parts were built during the event ("Blur reads as hiding")
  - spending demo time on the stack
  - slide-heavy presentations

  Source: [Kurbaitaev, DEV](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l)
- **What raised scores:**
  - "A live demo removes doubt, and doubt is what a judge is actually managing under time pressure."
  - Rehearse the first 30 seconds.
  - Keep a 60-second backup recording.
  - Prepare an honest answer to "what breaks first?" Naming a known weakness raised scores.
  - "Pick the sentence you want a judge to repeat to another judge an hour later."
  - What did *not* move scores: polish beyond legibility, framework choice, team credentials.
  - Source: [Kurbaitaev, DEV](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l)
- **Cutting features:**
  - One winning team started with 7 features, shipped 2, and won. Their filter was whether a judge needed to see a feature to understand the solution.
  - One fully working core feature beats five half-working ones.
  - Final-stretch rule: no new features, only polish and demo prep.
  - Videos longer than 60-90 seconds are too long, because judges review 10-20 entries each.
  - Source: these are aggregated practitioner blogs, surfaced via search: [Reskilll SIH retrospective](https://blogs.reskilll.com/?p=449), [whereuelevate](https://whereuelevate.com/blogs/why-hackathon-projects-fail), [DoraHacks DEV](https://dev.to/dorahacks/what-does-a-good-hackathon-submission-look-like-5398). I didn't fetch each one individually; these are practitioner opinion.
- **Inaccessible source:** A JetBrains post, "How to win a hackathon: notes from the judging table" (Jun 2026), returned 403. Its content is unverified. — [JetBrains blog](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/)

### Inferences
- **The 60-second format raises the bar.** GIAIC has a dedicated "best 60-second demo" award, and judges skim many videos. Pakkam's video should open with the product sentence and the live voice moment in the first 10 seconds, not architecture.
- **Candidate one-liner:** "Ask about any government scheme in Tamil, Hindi, English or Tanglish, by voice, and Pakkam answers with the exact page of the official PDF, verified by a human — or says it doesn't know."
- **What to stop doing in the last 4 days:**
  - Freeze breadth: no new schemes or languages.
  - Spend the time on one flawless voice path, a measured eval number (spoken Tanglish and/or noisy 8 kHz), the 60-second video, and the public post.

### Gaps
- No Indian voice-AI judge (Gnani, Sarvam, Bhashini) is on record about their own criteria. The judge-behaviour evidence above comes from global or general hackathons.

## Q4. How winning teams answer "why not just use ChatGPT?"

### Takeaway
I found no transcript of a hackathon winner answering this. Practitioner and investor-style commentary converges on one answer: the value sits outside the model, in proprietary or verified data, workflow integration, trust, and distribution. The common test is "could a user get 80% of this by pasting into ChatGPT?"

### Cited Findings
- **The 80% test:** If a technical user could get 80% of the output by pasting your prompt into ChatGPT, you're a wrapper. — [search summary of wrapper-moat posts, e.g. Daily Success Snacks](https://dailysuccesssnacks.beehiiv.com/p/it-s-like-chatgpt-for-x-the-pitch-that-instantly-makes-investors-nervous); [maccelerator](https://maccelerator.la/en/blog/startup-strategy/why-ai-wrappers-don-t-have-moats/)
- **Where the moat sits:** Commonly cited moats are a data flywheel, workflow integration, distribution, brand and trust, and network effects. "The aggregated dataset is the product. The AI is just the interface." "Start with the problem. The model is a detail." — [hatchworks](https://hatchworks.com/blog/gen-ai/ai-wrapper-product-strategy/); [eka-blog "your moat is the database"](https://eka-blog.pages.dev/posts/your-moat-is-the-database)
- **A team without an answer:** One anecdote describes Series A prospects asking "why not just use Claude with a good prompt?" The team, which had no proprietary-data or workflow answer, pivoted. — [search summary; source blog not fetched](https://eka-blog.pages.dev/posts/your-moat-is-the-database)
- **What MEGHA claimed:** Its winning framing rested on "grounded in verified official documents," toll-free access, and working on any basic phone. These are access and trust arguments, not model arguments. — [Free Press Journal](https://www.freepressjournal.in/india/ai-solution-for-india-wins-top-spot-at-harvards-hackathon)
- **What GIAIC peers claim:**
  - "No LLM in the call path" (dhwani-desk)
  - "the model proposes and code decides" (Bolo)
  - "the LLM never decides eligibility" (JanVaani)
  - "refuses to guess... escalated" (Kural)
  - Source: [dhwani-desk](https://github.com/Pranav-0710/dhwani-desk); [Bolo](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon); [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani); [Kural](https://github.com/Mirdumurugesan/kural)

### Inferences
Pakkam's answer to "why not ChatGPT" should be concrete and demonstrable on screen.
1. **Access.** A voice-first, phone-shaped experience for people who don't type and won't install ChatGPT, and it handles spoken Tanglish. This is Gnani's telephony-trained STT angle.
2. **Trust.** Every answer carries a page citation to the official PDF plus a human signature. It refuses rather than hallucinates.
   - Best shown as a side-by-side: ChatGPT gives a confident wrong or outdated amount, while Pakkam shows the cited page. Only do this if a real, reproducible example exists, because faked comparisons breach the "misleading demos" rule.
3. **The asset is the verified corpus.** The signed fact store is the asset ChatGPT doesn't have. This is the "dataset is the product" moat.

Peers already claim "the LLM doesn't decide," so Pakkam's distinct claim is *verifiable provenance down to page and signer*.

### Gaps
- I found no primary-source example of an Indian hackathon judge asking this question, or of a winning team's verbatim answer.
- I found no evidence on how Gnani judges specifically weigh an "LLM-free" design against an LLM-grounded one.
