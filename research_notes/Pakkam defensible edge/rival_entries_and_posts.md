# Rival entries and posts: Gnani "Great Indian AI Internship Challenge 2026" (researched 2 Nov 2026)

What I could access:
- **GitHub (good access).** Public READMEs and docs came from raw.githubusercontent.com. About 320 candidate READMEs came from GitHub repo and code search. Of those, 223 mention Gnani, Prisma or Timbre, and 58 explicitly name the challenge or its hashtag. The GitHub REST metadata API (stars, created dates) was blocked for most repos in this session, so creation dates come only from search listings where shown.
- **LinkedIn (partial access).**
  - The hashtag feed (`/feed/hashtag/...`) returned HTTP 403.
  - Individual public post pages *did* open. Their JSON-LD gave the author, date, video length and reaction and comment counts.
  - Web search engines index almost none of the challenge posts. I could therefore reach only posts whose URLs were logged in entrants' repos, so the post sample below is small and **not representative**.
- **X (minimal access).**
  - x.com returned 402.
  - The fxtwitter mirror worked for public tweets.
  - One entrant's account (Dhwani Desk) is protected.
- I invented no posts or numbers. Repo claims are the authors' own README claims, and I did not run or verify any of them.

## 1. Contest mechanics that decide what "beating rivals" means

### Takeaway
Internship shortlisting is driven first by **verified engagement on the nominated LinkedIn/X post**, then by an eligibility check for genuine Gnani use, then by individual interviews. Prize money comes from 10 category awards worth ₹50,000 each, judged on category criteria. A rival map therefore has to cover both the builds and the posts.

### Cited Findings
- **Internship selection order:**
  1. Engagement check, counting verified reactions, comments and reshares on nominated posts at the closing cutoff.
  2. Eligibility check for genuine use of Gnani AI technology.
  3. Shortlisting of the projects with the strongest verified engagement.
  4. Individual interviews.
  5. Written offers.
  — [Gnani internship page](https://www.gnani.ai/internship)
- **Ten awards of ₹50,000 each.** No one can win more than one:
  - Main Character (regional or low-resource language)
  - Mixed Vibes (code-mixed: Hinglish, Tanglish, Benglish)
  - Real Deal (most useful real-world problem)
  - Noise Canceller (noisy telephonic audio)
  - Two-Person Army
  - Solo Ninja
  - Jugaad Genius
  - Small Town, Big Build
  - Demo Day Drop (best **60-second** demo video)
  - Crowd Favourite (public votes on LinkedIn and X)

  — [Gnani internship page](https://www.gnani.ai/internship)
- **Post rules:**
  - Show a video of the working app.
  - Say which Gnani technology was used.
  - Tag Gnani AI.
  - Include #GreatIndianAIInternshipChallenge and #GnaniAI.
  - Nominate one post per platform.
  - The post must be live before you submit.

  — [Gnani internship page](https://www.gnani.ai/internship)
- **Not allowed:** bought engagement, bots, paid promotion, engagement swaps, plagiarism and **misleading demos**. Synthetic data only. — [Gnani internship page](https://www.gnani.ai/internship)
- **Models:**
  - Prisma v2.5 STT: trained on telephonic audio, handles Hinglish, Tanglish and Benglish.
  - Timbre v2.5 TTS: beta.
  - Evon v3.3: open weights on Hugging Face only, not on the API platform.
  - The site header already lists Prisma v3.0.

  — [Gnani internship page](https://www.gnani.ai/internship)
- **Engagement baseline.** Gnani's own launch post (1 Oct 2026, 49 s video) had 171 reactions and 8 comments when fetched. — [Gnani AI LinkedIn post](https://www.linkedin.com/posts/gnani-ai_gnaniai-greatindianaiinternshipchallenge-activity-7511341641274884096-dHzG)

### Inferences
- The post is part of the scoring, not decoration. A technically superior entry with a weak post may not be shortlisted for interviews, though it can still win an award.
- "Misleading demos" is a disqualification ground. Live, unedited proof on screen is defensively useful as well as persuasive.
- Pakkam fits Real Deal, Main Character (Tamil) and Mixed Vibes (Tanglish). Kural explicitly targets the same set plus Noise Canceller, Solo Ninja, Small Town and Demo Day Drop (see section 2).

### Gaps
- The judging rubric weights inside each award are not published.
- Whether "verified engagement" weights comments over likes is not stated.

## 2. Rival builds in Pakkam's space (welfare schemes, citizen services, Tamil/Indic voice, helplines)

### Takeaway
The only rival that overlaps Pakkam head-on is **Kural**: Tamil/Tanglish scheme Q&A on Prisma, Evon and Timbre, with sources, refusal plus escalation, a Twilio phone line and a published noise benchmark. Other scheme entries are **eligibility screeners or form-fillers** that use rule engines (JanVaani, Sarkari Saathi, Bolo), or they are not Gnani entries at all (Urimai, Thunai, Udhavi/tn-schemematch, Anganwadi Akka). **No rival shows page-level citations to official PDFs, human-signed fact cards, or a measured refusal rate.**

### Cited Findings

**Kural (குரல்)** by Mirdula M (solo), Sri Ramakrishna Engineering College, Coimbatore. Repo created 5 Oct 2026.
- **What it is:** a Tamil-first voice helpline for government schemes, on Prisma v2.5 (ta-IN, ITN, scheme-name word boosting), Evon v3.3 (grounded answers from retrieved passages only, with citations) and Timbre v2.5 (Tamil voice "Trisha"; 8 kHz WAV for phone). — [Kural README](https://github.com/Mirdumurugesan/kural)
- **Channels:** web mic plus a **Twilio phone line** (language menu 1 Tamil / 2 English / 3 Hindi). Out-of-scope questions produce a **callback ticket for a human officer**. There is an admin dashboard for "knowledge gaps". — [Kural README](https://github.com/Mirdumurugesan/kural)
- **Noise handling:**
  - ffmpeg denoise chain and a per-call SNR estimate.
  - A UI "phone-line mode" degrades the judge's own voice to 8 kHz μ-law plus noise.
  - Claimed benchmark from 5 Oct: CER after denoise of 0.8% at 20 dB, 3.0% at 10 dB, 1.2% at 5 dB and 6.5% at 0 dB, on **6 synthetic Timbre-spoken questions**, with the right scheme retrieved 24/24.
  - The README itself admits denoise is worse at 10 dB (1.2% raw vs 3.0%).

  — [Kural BENCHMARKS.md](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md)
- **Retrieval and refusal claims:**
  - Retrieval top-1 is **20/20** on a 20-question set (Tamil, Tanglish, code-mixed, English).
  - Only 2 of 3 off-topic questions were rejected by retrieval. The third is left to an Evon NO_ANSWER rule.
  - **The refusal test is 3 questions, and no refusal rate is reported.**
  - The knowledge base is "compiled from public scheme information" in Markdown, with "verify amounts... against the linked official sources". Citations point to KB passages, not to pages of official PDFs.

  — [Kural BENCHMARKS.md](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md); [Kural README](https://github.com/Mirdumurugesan/kural)
- **Engineering claims:** PII redaction, extractive fallback when Evon is down, credit budget guard, TTS cache, 34 tests, CI, Docker, Prometheus. Evon needs self-hosting on a GPU. Until then Kural "answers extractively". — [Kural README](https://github.com/Mirdumurugesan/kural)
- **Post plan (drafts in the repo, not verified as published):**
  - Weekly build-in-public posts: announcement, a "Tamil broke my search engine 😅" technical insight, a noise benchmark clip, then a final 60 s native video.
  - Final-week checklist: "✅ Answers only from verified sources, with citations ✅ Doesn't guess: escalates to a human".
  - Closing ask: "a 👍 helps it reach the right people".
  - An X thread.

  — [Kural SOCIAL_POSTS.md](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/SOCIAL_POSTS.md)
- **Targeted awards (from its submission kit):** "Main Character (Tamil) · Mixed Vibes (Tanglish) · Real Deal · Noise Canceller · Solo Ninja · Small Town, Big Build (Coimbatore) · Demo Day Drop... lead with the Tamil-on-noisy-phone story." Kural has a 60 s demo video file in the repo. — [Kural SUBMISSION.md](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/SUBMISSION.md); [Kural README](https://github.com/Mirdumurugesan/kural)

**JanVaani** (amantebriwal4321). Repo created 20 Oct 2026.
- **What it is:** a voice desk for welfare **forms**.
  - 9 languages including Tamil; Hinglish is first-class.
  - **19 schemes decided by a deterministic rule engine.** "The language model never decides eligibility."
  - Verdicts: qualify / likely / need one answer / not for you / not enough facts.

  — [JanVaani README](https://github.com/amantebriwal4321/janvaani-gnani)
- **Channels and output:**
  - Browser softphone at 8 kHz with barge-in.
  - Twilio and Exotel adapters exist but no funded number.
  - Output is a printable **CSC Ready Slip PDF with QR** and SMS-style text.

  — [JanVaani README](https://github.com/amantebriwal4321/janvaani-gnani)
- **Models:** Prisma realtime WebSocket (8 kHz, scheme/district bias list), Timbre (`timbre-v3.0`, voice Shivani). The LLM is optional, on Groq `gpt-oss-20b` (not Evon). The README does not mention any citations to documents. Its 19 schemes are central schemes plus Gruha Lakshmi (Karnataka), Ladki Bahin (Maharashtra), Rythu Bharosa (Telangana) and Lakshmir Bhandar (West Bengal). **None is a TN state scheme.** — [JanVaani README](https://github.com/amantebriwal4321/janvaani-gnani)
- **Demo and post:** an in-app "Play 60-second demo" with a scripted Kolar household. Its own "not in repo" list includes an unverified `indic-auto` live check. No post link was found. — [JanVaani README](https://github.com/amantebriwal4321/janvaani-gnani)

**Sarkari Saathi** by Sahil Pathak.
- **What it is:** Marathi, Hindi or English voice eligibility for **13 schemes** (central plus Maharashtra).
  - "The LLM listens, the code decides."
  - Each rule records the page it was checked against and the date (checked 19 Oct 2026).
  - Results are "eligible / likely / no / needs more info".
  - About 3 s per turn. 54 tests.
  - Live link on Render.
  - Prisma v2.5 REST, Timbre v3.0, and **Gemini Flash-Lite** in place of Evon on the public link.

  — [Sarkari Saathi README](https://github.com/sahil454521/sarkari-saathi)
- **LinkedIn post (20 Oct 2026):**
  - Native video of **1 min 18 s**.
  - Hook: "आप बोलिए, फ़ॉर्म अपने-आप भरेगा। / Speak, and the form fills itself in."
  - Discloses the persona's "synthetic ElevenLabs voice".
  - **10 reactions, 1 comment** when fetched.

  — [Sahil Pathak LinkedIn post](https://www.linkedin.com/feed/update/urn:li:activity:7518269164248289280/)
- **X thread (22 Oct 2026):** 0 likes, 0 reposts, 1 reply, 12 views. — [X via fxtwitter](https://x.com/Sahilpathak2105/status/2113327134072795560)

**Bolo** by Satyabrata Mishra. Repo created 3 Oct 2026.
- **What it is:** a voice form-filler in 11 languages including Tamil.
  - Code validates every field.
  - Each field links to its recording ("recording behind every field").
  - Demo forms include "Farmer support enrolment".
  - Gemini stands in for Evon.
- **Status:** the README lists the demo video and LinkedIn post as "Coming soon".

— [Bolo README](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon)

**Dhwani Desk** by Jey Pranav and Lakshmi Narasimma K G (team of two). Repo created 9 Oct 2026.
- **What it is:** a Kannada civic-complaint helpline on Prisma (kn-IN, 8 kHz) and Timbre.
  - Decisions come from a local fine-tuned "Laya" model, with no LLM in the call path.
  - Hazard escalation to a human, and a supervisor console.

  — [Dhwani Desk README](https://github.com/Pranav-0710/dhwani-desk)
- **LinkedIn post (1 Nov 2026):**
  - Native video of **49 s**.
  - Hook: "If you live in a Kannada-speaking town, try reporting an overflowing drain... Hold music, forms in English, nobody picks up. 📞"
  - Demo beat: "a live wire sparking... puts an officer on the line".
  - **10 reactions, 6 comments.** The author has 791 followers.
  - One comment asks technical questions (how Laya was fine-tuned, how urgency is decided).

  — [Jey Pranav LinkedIn post](https://www.linkedin.com/posts/jey-pranav-783761278_greatindianaiinternshipchallenge-gnaniai-ugcPost-7522648733591842817-UTNQ)
- **X:** the account is protected, so engagement was not visible. — [Dhwani CONTRIBUTIONS.md](https://raw.githubusercontent.com/Pranav-0710/dhwani-desk/main/docs/CONTRIBUTIONS.md)

**Other Gnani-built civic and welfare entries (README claims only):**
- **Adhikar:** schemes plus grievances, 5 schemes, web plus WhatsApp. **Only STT is built; TTS, KB, backend, frontend and WhatsApp are "Not started".** — [Adhikar README](https://github.com/0Curious0/adhikar)
- **Kaagaz Saathi:** a voice-first *document pre-check* for scheme applications (name mismatches, expired income certificates). — [Kaagaz Saathi README](https://github.com/Abhinavsharma005/Kaagaz-Saathi)
- **Artha-Suraksha:** 8 kHz MFI, PMFBY and grievance copilot. Claims "P95 ~622 ms" and a noise stress-test workbench. — [Artha-Suraksha README](https://github.com/Daniishhhhh/artha-suraksha)
- **SHRAVAN:** a civic issue reporter in Hindi and English. Reports stay local and are not delivered to any authority. — [SHRAVAN README](https://github.com/saisasidharpaluri/shravan)
- **Kisan Saathi:** "source-grounded" farmer advisory on WhatsApp and web in Telugu, Hindi and English, using Prisma v3.0. — [Kisan Saathi README](https://github.com/itsakhilesh7/KIsan-Saathi)
- **JeevanRaksha AI:** a disaster-relief voice intake MVP. — [JeevanRaksha README](https://github.com/aasutoshsony/jeevanraksha-ai)
- **JANAVAANI AI:** document Q&A over uploaded notices in English and Telugu, "shows supporting evidence". The README does not mention Gnani in the opening lines I read. — [JANAVAANI AI README](https://github.com/ShyamSampath-git/Janavaani-ai)

**Tamil scheme repos that are probably *not* Gnani entries** (no Gnani models in the README):
- **Urimai:** Tamil voice-note eligibility screening, 10 schemes, three-valued logic, browser speech or Whisper. Its Tamil audio testing is dated 24 Aug 2026, which is before the contest. — [Urimai README](https://github.com/rgokulkrishna44-debug/urimai)
- **Thunai:** a missed-call IVR plus WhatsApp, 50 schemes (26 TN), JsonLogic. It uses Twilio and Bhashini and lists "themes" and SDGs, so it is likely a different hackathon. — [Thunai README](https://github.com/murali18-a/Thunai)
- **Udhavi (tn-schemematch):** 54 schemes (28 TN), a rule engine, a helper or caseload dashboard, printable sheets, about 370 tests, Chrome speech and an optional Claude model. — [tn-schemematch README](https://github.com/kanishk5676/tn-schemematch)
- **Anganwadi Akka:** Gemini 1.5 Flash plus Web Speech, with no grounding. — [magalir-voice-ai README](https://github.com/Bhavesh-Ram-G-V/magalir-voice-ai)

**Pakkam's visibility:** Pakkam's own repo (`mailtojaswanthss-svg/pakkam`) came up in the same GitHub search, so rivals can see it. — GitHub search results (this session)

### Inferences
- Kural is the main threat on every axis Pakkam cares about. It is Tamil-first, grounded, refuses and escalates, has a phone line, and has a benchmark with numbers. Its weak points, from its own docs, are:
  - The evaluation sets are tiny: 6 noise clips, 20 retrieval questions, 3 off-topic questions.
  - Citations point to a hand-compiled Markdown KB, not to official PDFs with page numbers.
  - No refusal rate is reported.
  - No human-verified facts.
  - Evon may not be live, so the README says answers may be extractive.
- The other scheme entries chose eligibility screening by rule engine plus form filling. Pakkam's grounded document Q&A with refusals is a different product, and it is uncrowded among Gnani-built entries.
- No Gnani entry found covers **TN state schemes** in Tamil except Kural. Kural's KB scope (number of schemes) was not stated in the README sections I read.

### Gaps
- I could not confirm whether Kural, JanVaani or Bolo have published their LinkedIn/X posts, or what engagement those posts have.
- I could not read Kural's KB scheme list or its citation UI.
- Star, fork and creation metadata were blocked for most repos.
- Entrants without public GitHub repos are invisible to this method.

## 3. Patterns: baseline claims, rare claims, what nobody shows, how posts are pitched

### Takeaway
The baseline Gnani-entry pitch is: "voice-first, Indic plus code-mixed, the LLM doesn't decide (rules decide), synthetic data, Prisma plus Timbre". Rare: phone-line demos, noise benchmarks with numbers, and refusal or escalation. **Nobody shows** page-cited answers from official documents, a refusal-rate metric on a sizeable set, human sign-off on facts, or a misinformation or rumour check. Posts that could be checked are 49 s to 1 min 25 s native videos with problem-first hooks, and they earn only about 7 to 35 reactions.

### Cited Findings
- **"The LLM never decides" is the dominant safety claim among scheme builds.**
  - JanVaani: "The language model never decides eligibility" — [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani)
  - Sarkari Saathi: "the LLM listens, the code decides" — [Sarkari Saathi](https://github.com/sahil454521/sarkari-saathi)
  - Bolo: "model proposes and code decides" — [Bolo](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon)
  - Dhwani Desk: "no LLM in the call path" — [Dhwani Desk](https://github.com/Pranav-0710/dhwani-desk)
- **Telephony realism is usually simulated:**
  - JanVaani runs a browser softphone at 8 kHz, with no funded number. — [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani)
  - Kural uses Twilio plus a phone-line simulator. — [Kural](https://github.com/Mirdumurugesan/kural)
- **Noise numbers:** only Kural (CER at 4 SNR levels on 6 clips) and Artha-Suraksha (a latency claim) publish numbers in their READMEs. — [Kural BENCHMARKS](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md); [Artha-Suraksha](https://github.com/Daniishhhhh/artha-suraksha)
- **Many entries swap Evon for another LLM:**
  - Gemini — [Sarkari Saathi](https://github.com/sahil454521/sarkari-saathi); [Bolo](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon)
  - Groq — [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani)
  - Mock Evon — [MetalliSense Kural](https://github.com/NethraVenkat/MetalliSense-Gnani)
- **Post engagement observed (all I could verify):**

  | Project | Date | Video | Reactions | Comments | Source |
  |---|---|---|---|---|---|
  | Voice Khata | 2 Oct | text only | 35 | 2 | [Vinodkumar Kadli](https://www.linkedin.com/posts/vinodkumar-kadli-b40b91293_gnaniai-greatindianaiinternshipchallenge-activity-7511708832922955776-2zcw) |
  | IndicVoiceCare | 3 Oct | 1 min 25 s | 14 | 1 | [venkata sai kowshik boddu](https://www.linkedin.com/posts/venkata-sai-kowshik-boddu_gnaniai-greatindianaiinternshipchallenge-activity-7512093942717509632-0fsm) |
  | Sarkari Saathi | 20 Oct | 1 min 18 s | 10 | 1 | [Sahil Pathak](https://www.linkedin.com/feed/update/urn:li:activity:7518269164248289280/) |
  | Anchor (Hinglish companion) | 26 Oct | 1 min 1 s | 7 | 0 | [Khushi Gupta](https://www.linkedin.com/posts/khushi-gupta-411019382_greatindianaiinternshipchallenge-gnaniai-ugcPost-7520408871471874048-cWs5) |
  | Dhwani Desk | 1 Nov | 49 s | 10 | 6 | [Jey Pranav](https://www.linkedin.com/posts/jey-pranav-783761278_greatindianaiinternshipchallenge-gnaniai-ugcPost-7522648733591842817-UTNQ) |
  | Gnani AI official launch post (for scale) | — | — | 171 | 8 | [Gnani AI](https://www.linkedin.com/posts/gnani-ai_gnaniai-greatindianaiinternshipchallenge-activity-7511341641274884096-dHzG) |

- **Hooks used:**
  - Sarkari Saathi opens with a native-language one-liner plus an English gloss.
  - Dhwani Desk and Voice Khata open with a relatable civic or shop pain.
  - IndicVoiceCare uses a generic "🚀 Excited to share", and its demo is an off-platform link.
  - Kural's drafts use a weekly build-in-public cadence and a "👍 helps it reach the right people" ask.

  — sources as in the table above; [Kural SOCIAL_POSTS](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/SOCIAL_POSTS.md)
- **Some entrants plan staged posts:**
  - Kaam ka Parcha planned a launch around 15 Oct, a build story around 22 Oct, a Jugaad post around 29 Oct and a final demo around 3 Nov, with "no engagement-exchange requests". — [kaam-ka-parcha posts.md (via GitHub code search)](https://github.com/HarshdipSaha/kaam-ka-parcha)
  - Dhwani logged a teaser plus a demo post on the same day (1 Nov). — [Dhwani CONTRIBUTIONS.md](https://raw.githubusercontent.com/Pranav-0710/dhwani-desk/main/docs/CONTRIBUTIONS.md)

### Inferences
- The engagement bar among visible entrants is low (about 10 reactions), so a post with more than 50 genuine reactions and real comment threads would likely be top tier. This is unverified: the sample has 5 posts.
- Dhwani's post drew the most comments by showing a concrete high-stakes moment (the live wire triggering an officer handoff) and by its technical depth. Comments asked "how". Showing one striking moment seems to pull more discussion than listing features.
- Videos over 60 s miss the Demo Day Drop format (best 60-second demo). Sarkari Saathi (1 min 18 s) and IndicVoiceCare (1 min 25 s) overshoot it.

### Gaps
- There was no access to LinkedIn hashtag-wide results, so I cannot rank all entrants by engagement.
- X engagement was visible only for Sarkari Saathi (12 views).

## 4. How Pakkam can demonstrably exceed each common rival claim

### Takeaway
Pakkam should win on **measured, on-screen proof** where rivals only assert: a larger evaluation set, page-level PDF evidence, a refusal rate, and human sign-off. On telephony and noise, where Kural is ahead, Pakkam needs at least one measured noisy-audio result, or it should concede that award and avoid competing on it.

### Cited Findings (rival claim → evidence basis)
- **"Answers only from verified sources, with citations" (Kural).** The citations are to a Markdown KB, and the README says to verify against official sources. — [Kural README](https://github.com/Mirdumurugesan/kural)
- **"Doesn't guess: escalates to a human" (Kural).** It was tested on 3 off-topic questions, and no rate is given. — [Kural BENCHMARKS](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md)
- **"20/20 retrieval top-1" (Kural).** That is n=20, and it measures retrieval only, not answer correctness. — [Kural BENCHMARKS](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md)
- **"Works on noisy 8 kHz phone audio: 0.8% to 6.5% CER" (Kural).** This was measured on 6 synthetic TTS clips. — [Kural BENCHMARKS](https://raw.githubusercontent.com/Mirdumurugesan/kural/main/docs/BENCHMARKS.md)
- **"Rule engine decides, LLM never does".** Each rule is checked against the scheme page with a date. — [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani); [Sarkari Saathi](https://github.com/sahil454521/sarkari-saathi)
- **"Recording behind every field" (Bolo) and "Printable slip with QR" (JanVaani).** — [Bolo](https://github.com/satyabrata-mishra/Gnani-AI-Hackathon); [JanVaani](https://github.com/amantebriwal4321/janvaani-gnani)

### Inferences (proposed ways to exceed; these are recommendations, not findings)
- **Citations.** Show the cited PDF page opening on screen, with the passage highlighted, for a Tamil voice question in the video. Say "97% correct-page citations on 60 questions". That is 3x Kural's question count and measures the *answer's page*, not just retrieval. Link the live benchmark page in the post.
- **Refusals.** Report "92% correct refusals" with the size of the refusal set, versus Kural's unreported rate on 3 questions. On camera, ask one tempting unsupported question (for example a rumoured new amount) and show Pakkam refusing and saying where to check.
- **Trust in facts.** The 22 human-signed fact cards have no equivalent in any rival. Show the signer and date on a card. This answers the "verify against official sources" caveat that rivals leave to the user.
- **Rumour checker.** No entry found does misinformation checking. A 5-second beat in the demo ("WhatsApp forward says ₹X; Pakkam: not in G.O., here is page N") is unique. Real Deal judges and Crowd voters may find it relatable.
- **Rule engines vs grounding.** Do not compete on eligibility screening, where JanVaani, Sarkari Saathi and Udhavi are deeper. Position Pakkam as "answers *what the document says*, page-cited". Rule-engine rivals cite a scheme webpage at best.
- **Noise and telephony (Kural's lead).** If the team claims Noise Canceller at all, publish a noisy-audio result with more clips than Kural's 6, for example Prisma transcripts of real-recorded Tamil and Tanglish questions with added noise, measured by end-to-end correct-page rate rather than CER. Otherwise state honestly that Pakkam is web plus Talk mode, and lead with Real Deal or Mixed Vibes. Only one award can be won anyway.
- **Tanglish and Hindi.** Show a Tanglish question and an English or Hindi question in the same demo, each answered from the same page. Report the per-language split of the 60-question benchmark if one exists, since Kural splits its 20 by language.
- **Posts.**
  - Keep the main video at 60 s or less.
  - Open with a native-language hook plus an English gloss (the Sarkari Saathi pattern).
  - Include one dramatic proof moment: the refusal or rumour catch (the Dhwani pattern).
  - Put the numbers in the first 3 lines of the post.
  - Invite technical questions so the comment threads are genuine.
  - Avoid any engagement-exchange asks, which are banned.

### Gaps
- Kural's final published post, its video, its engagement, and whether its Evon was live at demo time are unknown.
- No information was found on how judges weigh benchmark rigour against polish.
