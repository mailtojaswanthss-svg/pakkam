# Gnani.ai Capabilities and Quickly Buildable Voice Features (India, 4-day build)

## Does Gnani provide STT/TTS/voice-agent/telephony APIs a participant can use? (docs, auth, languages, latency, pricing, programs)

### Takeaway
Yes. Gnani has a public, self-serve developer API at `api.vachana.ai`: Prisma STT (REST, WebSocket and batch), Timbre TTS (REST, SSE and WebSocket), voice cloning, and a no-code "Inya" Agent Builder with a Platform API. Auth is a single `X-API-Key-ID` header, and Python, Pipecat and LiveKit integrations exist. STT supports Tamil (`ta-IN`) and Hindi, plus Hinglish code-mixing. Tanglish is not documented. Telephony inside Gnani's own agent builder is documented only as "import your Twilio number". No public pricing or current free-credit offer was found.

### Cited Findings
- **Products and base URL.** The base URL is `https://api.vachana.ai`. Products are STT "Gnani Prisma" (v2.5 is the default and needs the language specified; v3.0 adds multilingual auto-detection), TTS "Gnani Timbre v2.5" (v2.0 is deprecated), voice cloning (speaker embeddings), the Agent Builder (console) and the Agent Builder Platform API (agents, FAQs, conversations over REST), plus LiveKit and Pipecat plugins. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md)
- **Auth.** Every request sends an `X-API-Key-ID` header. Keys are generated in the dashboard at https://app.gnani.ai/voice, and a missing or invalid key returns 401. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md)
- **STT transports.** REST handles short clips: the intro page says up to 30 s, but a search snippet of the REST page says up to 60 s, so the two conflict. The realtime WebSocket endpoint is `wss://api.vachana.ai/stt/v3/stream`, and there is a batch API for long files. Input formats are WAV, MP3, OGG, FLAC, AAC and M4A. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md); [STT REST page](https://docs.gnani.ai/api/STT/speech-to-text.md)
- **STT sample rates.** Pipecat's Gnani STT service lists 8000, 16000, 44100 and 48000 Hz. 8 kHz support matters for telephony. — [Pipecat Gnani STT](https://docs.pipecat.ai/api-reference/server/services/stt/gnani)
- **STT languages.** Prisma v2.5 and v3.0 support the same 10 languages: bn-IN, en-IN, gu-IN, hi-IN, kn-IN, ml-IN, mr-IN, pa-IN, **ta-IN (Tamil script output)** and te-IN. `indic-auto` (v3.0 only) detects the language and returns `detected_language_code`. **Hinglish** (English-Hindi mixed audio) is accepted under en-IN. **Tanglish is not mentioned.** — [Gnani STT languages](https://docs.gnani.ai/api/STT/languages.md)
- **Language-count discrepancy.** Pipecat's listing names 12 languages while Gnani's docs say 10. Gnani's Hugging Face card mentions "Latin-script variants". — [Pipecat Gnani STT](https://docs.pipecat.ai/api-reference/server/services/stt/gnani); [HF gnani-ai/vachana](https://huggingface.co/gnani-ai/vachana)
- **Latency.** Gnani claims STT P95 of about 200 ms when streaming (vendor claim). TTS latency ranks REST > SSE > WebSocket, with no figures published. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md); [HF gnani-ai/vachana](https://huggingface.co/gnani-ai/vachana)
- **TTS.** TTS supports SSML, audio tags and text normalization. Named voices include Pranav (M), Kaveri (F), Shubhra (F) and Deepak (M); examples also use "Raju". The models are hosted only, with no weights shipped. The HF wrapper is Apache-2.0. — [HF gnani-ai/vachana](https://huggingface.co/gnani-ai/vachana); [Gnani llms.txt index](https://docs.gnani.ai/llms.txt)
- **SDKs.** There is a `gnani-vachana` PyPI package (v0.7.5 seen) and a Python SDK for STT, batch STT and TTS. — [PyPI gnani-vachana](https://pypi.org/project/gnani-vachana/0.7.5/); [Gnani llms.txt index](https://docs.gnani.ai/llms.txt)
- **Getting a key.** Register at gnani.ai or email speechstack@gnani.ai. — [HF gnani-ai/vachana](https://huggingface.co/gnani-ai/vachana)
- **Agent Builder (Inya) features.** Documented features cover knowledge bases, DTMF, voicemail, dynamic variables, language switching during calls, Jinja prompts, Twilio SMS, Zoho CRM, a Custom integration (D05_Custom), Webex CC, a "Trigger Call" (outbound test call to whitelisted numbers) and "Stream Conversation Audio". — [Gnani llms.txt index](https://docs.gnani.ai/llms.txt)
- **Telephony in Inya.** The only documented number source is **importing Twilio numbers**: you enter the Twilio Account SID and Auth Token, then select numbers. Imported numbers "can be assigned to agents for inbound or outbound calls". Exotel, Plivo and SIP are not documented. — [Gnani Import Number](https://docs.gnani.ai/M16x_Import_Number.md)
- **Inya positioning.** Inya.ai launched as a no-code agentic platform for voice and chat agents in 10 Indic languages, covering voice, chat and WhatsApp channels. The 2025 launch offered **$10,000 free credits to the first 1,000 sign-ups**, which may no longer be current. — [AIM](https://analyticsindiamag.com/ai-news-updates/gnani-ai-unveils-inya-ai-no-code-agentic-ai-platform-for-voice-and-chat-agents-in-10-indic-languages); [ChannelDrive](https://channeldrive.in/artificial-intelligence/gnani-ai-unveils-inya-ai-no-code-agentic-ai-platform/)
- **2026 developments.** Gnani's About page lists a 2026 launch of a proprietary Voice LLM that "opens the developer ecosystem for voice-first agents". A report mentions "Inya VoiceOS", a voice-to-voice model. — [Gnani about](https://gnani.ai/about-us); [Gnani search summary of press](https://inc42.com/buzz/gnani-ai-raises-10-mn-to-build-sovereign-ai-voice-agents/)
- **Docs community.** The docs link to a Discord for feedback. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md)

### Inferences
- **Lowest-risk Gnani integration for a FastAPI backend.** Call Prisma STT via REST or WebSocket and Timbre TTS via REST or WebSocket directly from the backend, and keep the existing LLM and RAG logic. Inya would duplicate the backend's reasoning and only supports Twilio numbers.
- **Telephony audio fit.** Twilio Media Streams and Exotel Voicebot send 8 kHz telephony audio, and Prisma accepts 8 kHz. Phone audio can therefore be piped straight into Gnani STT, with only mu-law to PCM conversion needed for Twilio. That conversion detail comes from general knowledge of Twilio, not a source here.
- **Tamil code-mixing.** For Tamil users, use `ta-IN` or `indic-auto`. Tanglish quality is unverified and should be tested before claiming it in a demo.

### Gaps
- No public per-minute or per-character pricing for STT and TTS was found, nor any current free tier or credit amount.
- No 2025-2026 Gnani hackathon or developer program was found, beyond the 2025 Inya credits offer and the 2026 "developer ecosystem" mention.
- The TTS language list was not retrieved. The `available-voices` page should confirm Tamil voices.
- STT rate limits (docs page api/STT/limits.md) were not fetched.
- No documented Exotel, Plivo or SIP integration exists for Inya agents.

## Adding phone-call (IVR) access to an existing web backend in 1-2 days: Gnani vs Exotel/Twilio/Plivo/Knowlarity

### Takeaway
Fastest demo path: a **Twilio trial** (minutes, no KYC). Use a US number, verify your own phone as a caller, and point a TwiML `<Connect><Stream>` at a FastAPI WebSocket. The catch is that callers in India dial an international number, and trial limits apply. For a **real Indian number**, use **Exotel**: a 7-day trial ExoPhone works without KYC, and the **Voicebot applet** streams 8 kHz PCM to your WSS URL. Production numbers need KYC, which typically takes 2-3 business days, so it fits 4 days only if started on day 1. Plivo Indian numbers require an India-registered business plus KYC. Twilio does not usefully offer Indian local inbound numbers.

### Cited Findings
**Exotel (Indian numbers, Voicebot WebSocket)**
- **Trial terms.** The trial runs 7 days from activation with one auto-assigned test ExoPhone. Outbound calls only reach verified (whitelisted) numbers. WhatsApp API, campaigns, custom caller ID and porting are unavailable on trial. Credits expire at trial end. **The trial can start without KYC; KYC is required to buy production ExoPhones and go live.** — [Exotel Trial Account](https://developer.exotel.com/docs/getting-started/trial-account)
- **KYC time.** KYC review "typically takes 2-3 business days" after correct documents are submitted, and the trial stays active during review. — [Exotel Account Setup & KYC FAQs](https://developer.exotel.com/docs/faqs/account-setup)
- **Conflicting trial terms.** Some Exotel material says 15 days and ₹1000 in credits, while the pricing page and reviews say 7 days and about ₹500. — [Exotel pricing FAQ](https://developer.exotel.com/docs/faqs/pricing-plans); [Exotel support](https://support.exotel.com/support/solutions/articles/102083-what-is-the-difference-between-a-trial-account-and-a-full-account-)
- **Setup steps.** Open App Bazaar, create an app, add a **Voicebot** applet (not Stream or Passthru) with your `wss://` URL, then add a Hangup applet. Under ExoPhones, attach the flow to the number. Voice streaming may need to be enabled by Exotel support. Audio is **8 kHz mono 16-bit PCM**. WebSocket metadata includes stream_id, call_id (CallSid), account_sid, from and to. For local testing you can use `ngrok http 8000`. Outbound calls go through the Exotel Voice API, which opens a WebSocket on connect. — [Pipecat Exotel WebSockets guide](https://docs.pipecat.ai/pipecat/telephony/exotel-websockets.md)

**Twilio**
- **Trial limits.** A trial can receive calls only from **verified numbers**, with up to 5 verified recipients. Trial accounts get one phone number, a 75-minute total voice quota, at most 5 concurrent calls and **30 free Voice Media Streams units**. Some TwiML verbs are blocked. An older support article says trial calls are capped at 10 minutes. — [Twilio trial docs](https://www.twilio.com/docs/usage/trials); [Try out Twilio Voice](https://www.twilio.com/docs/usage/trials/try-out-voice.md); [Twilio support](https://support.twilio.com/hc/en-us/articles/360036052753)
- **India voice guideline.** Inbound PSTN calls to Indian **toll-free** numbers are supported. Local-number inbound shows N/A, and domestic India-to-India is N/A. "Outbound calls to India can only be made from international (non-Indian) numbers". Voice OTP is not permitted, and UCC consent rules apply. — [Twilio India voice guidelines](https://www.twilio.com/en-us/guidelines/in/voice)
- **Bundles.** A regulatory Bundle (BundleSid) is now required to provision regulated numbers. — [Twilio Bundles API](https://www.twilio.com/docs/phone-numbers/regulatory/api/bundles)
- **Gnani compatibility.** Gnani's Inya imports Twilio numbers directly, which makes Twilio the only documented "via Gnani itself" phone path. — [Gnani Import Number](https://docs.gnani.ai/M16x_Import_Number.md)

**Plivo**
- **Eligibility.** **Only India-registered businesses** can rent Indian numbers and use domestic routes, and KYC is required first. Foreign businesses must use international routes showing a US or international caller ID. Calls must stay India-to-India for media anchoring, or they fail with `violates_media_anchoring`. — [Plivo India calling](https://www.plivo.com/docs/voice/concepts/india-calling.md)

**Comparative benchmarks (vendor blog, June 2026; unverified)**
- **Provisioning times.** New India DIDs take 24-48 h on Plivo and Twilio, 2-5 business days on Exotel and Knowlarity, and 3-7 business days on Ozonetel.
- **Inbound rates.** Normal DID inbound costs ₹0.40-0.90/min and toll-free inbound ₹1.20-2.50/min.
- **Relative cost.** Exotel runs about 10-25% above Plivo, and Twilio India about 2-3x Plivo or Exotel.
- **Streaming maturity.** Ozonetel and Knowlarity are "catching up" on streaming.
- Source for all four: [Caller Digital 2026 comparison](https://caller.digital/blog/telephony-partner-voice-ai-india-plivo-exotel-ozonetel-knowlarity-twilio-2026)

### Inferences
- **Realistic 4-day plan:**
  - **Day 1:** Sign up for the Exotel trial and the Twilio trial, and submit Exotel KYC immediately if an Indian entity exists.
  - **Day 1-2:** Build a FastAPI `/ws/call` WebSocket that does inbound audio → Gnani STT streaming (8 kHz) → existing answer pipeline → Gnani TTS → 8 kHz PCM back.
  - **Day 3:** Use the Exotel trial ExoPhone for the live demo in India, with verified judge or teammate numbers. Use Twilio as a fallback.
  - **Day 4:** Polish.
- **Code reuse.** Pipecat ships working Exotel and Twilio serializers plus a Gnani STT service, so a Pipecat-based handler could cut integration to roughly one day. This is an engineering estimate.
- **Missed-call callback.** This pattern (caller rings, the line hangs up, the system calls back so the caller pays nothing) maps to Exotel: an inbound flow that hangs up and records the caller via a passthru or status webhook, then an outbound Voice API call to that number connected to the Voicebot. On trial, outbound only reaches whitelisted numbers, so the demo works only for pre-verified numbers.
- **Knowlarity.** It is not recommended for a 4-day build, given slower provisioning and weaker streaming APIs per the benchmark above.

### Gaps
- No official Exotel missed-call-specific doc was retrieved; the flow above is an inference.
- Exact Exotel production ExoPhone rental fees and per-minute rates, and Knowlarity streaming docs, were not found.
- Twilio's per-minute cost for Media Streams outside the trial, and whether Indian mobile callers can reach a Twilio US number cheaply, were not verified (international calling charges fall on the caller).
- Plivo audio-stream docs were not fetched (the India page doesn't cover streaming).

## Other high-impact voice features buildable in days (WhatsApp voice notes, eligibility interview, accessibility, low bandwidth)

### Takeaway
The WhatsApp Cloud API test number is available instantly and needs no business verification or payment method. It can message only up to 5 pre-registered recipients, and its temporary token expires in 24 h. That is enough for a demo where a judge or teammate sends a voice note and gets an audio reply, but not for public use. Other features (an eligibility interview producing a checklist, slow-speech and repeat options for elderly users, compressed audio) are application-level and need no new vendor.

### Cited Findings
- **Test number.** Adding WhatsApp to a Meta app auto-creates a test WABA and a test business number with relaxed limits. No payment method is needed for template messages, and unverified WABAs have a test message rate limit. — [Meta WhatsApp platform docs](https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform)
- **Recipient limit and token.** The test number (+1 555 format) can message **up to 5 registered recipient numbers**. Sending outside the allowlist gives error 131030. The temporary access token expires in 24 h (error 190). — [Rich Automate 2026 India sandbox guide](https://richautomate.in/blog/whatsapp-cloud-api-test-number-sandbox-india-2026); [WhatsApp quickstart](https://ericanadia.github.io/technical-writing-portfolio/whatsapp-quickstart/)
- **Who can message whom.** One third-party guide says "customers can not send messages to your test phone number". — [WANotifier](https://help.wanotifier.com/en/article/test-phone-number-limitations-kt0ly2/)
- **Unverified volume cap.** Unverified Cloud API accounts reportedly cap at 250 unique customers per 24 h (third-party). Some numbers can move to a 1k limit without business verification. — [Blueticks](https://blueticks.co/blog/whatsapp-api-without-meta-verification); [360dialog](https://docs.360dialog.com/partner/help-and-support/partner-newsletters/numbers-can-upgrade-to-1k-messaging-limit-without-business-verification)
- **Audio messages.** Audio messages are supported (the recipient's client plays the file). One third-party source gives a 16 MB max audio size. — [Meta send-messages guide (mirror)](https://scriptagc.wasmer.app/https_developers_facebook_com/docs/whatsapp/cloud-api/guides/send-messages); [Expertflow](https://docs.expertflow.com/cx-knowledgebase/latest/meta-whatsapp-cloud-api)
- **Calling.** WhatsApp Cloud API now has a Calling feature for voice calls over WhatsApp. — [Meta Cloud API Calling](https://developers.facebook.com/documentation/business-messaging/whatsapp/calling.md)
- **Pricing.** Pricing is per message by recipient country and template category (post-July 2025 model). — [iSlash July 2025 pricing](https://learn.islash.io/islash-insights/whatsapp-apis-new-message-pricing-july-2025-updates); [YCloud](https://www.ycloud.com/blog/whatsapp-api-pricing.md)
- **Gnani STT input formats.** STT accepts OGG and M4A. — [Gnani docs intro](https://docs.gnani.ai/api/introduction/introduction.md)

### Inferences
- **WhatsApp voice-note flow.** Webhook receives an `audio` message → download the media → Gnani STT (OGG accepted) → existing answer → Gnani TTS → upload as OGG/Opus → send an `audio` message. A text summary and checklist go alongside. Estimate: 1 day on the test number. Inbound from teammate numbers should work once they are registered and message within the 24 h window, but verify early given the conflicting third-party statement.
- **Low-bandwidth audio.** WhatsApp voice notes are already Opus-in-OGG. Serving TTS as Opus at about 16-24 kbps in the web app is a cheap low-bandwidth win, as is using the browser MediaRecorder `audio/webm;codecs=opus` for uploads. These are general-knowledge points with no source retrieved.
- **Eligibility interview by voice.** A scripted slot-filling flow (age, income, caste category, occupation, district) over phone or WhatsApp can reuse the backend's scheme rules and output a document checklist via SMS or WhatsApp. It needs no extra vendor and is buildable in 1-2 days.
- **Accessibility.** For elderly and visually impaired users: DTMF fallback ("press 1 to repeat"; Inya documents DTMF; Exotel applets support keypad input), slower TTS rate and SSML pauses (Gnani TTS supports SSML), and the same feature-phone access as IVR.

### Gaps
- No official Meta statement was retrieved on inbound media to the test number or on exact current India per-message rates.
- No source was found on Opus bitrate recommendations specific to Indian 2G/3G conditions.

## Evidence that phone (IVR/feature-phone) access matters: voice AI for social good in India

### Takeaway
India's largest maternal-health and community-media programs run on plain voice calls. ARMMAN's government Kilkari service exceeds 11 million subscribers, and Gram Vaani's Mobile Vaani IVR has served about 100k monthly users. This is strong precedent that a phone number, not an app, reaches low-literacy and feature-phone users.

### Cited Findings
- **Kilkari scale.** Kilkari subscribers have crossed **11 million**. mMitra (free voice messages to pregnant women and new mothers) runs in 4 languages across 9 states. — [ARMMAN Kilkari vision](https://armman.org/armmans-vision-for-kilkari-and-mobile-academy/); [ARMMAN mMitra](https://www.armman.org/mmitra/)
- **Kilkari capacity.** The IVR was enhanced to support 12 million concurrent Kilkari subscribers, up from 3 million. — [ARMMAN Q3 2024-25 impact deck](https://armman.org/wp-content/uploads/2025/03/Q3_24-25_Impact-Deck.pdf)
- **Kilkari delivery.** Kilkari is "handset independent, audio based and accessed via a simple voice call" (2018 source). — [MCSP presentation 2018](https://www.mcsprogram.org/wp-content/uploads/2018/07/Presentations-Digital-Tools-to-Strengthen-Community-Health-Work-India-Post-ICHC-2.pdf)
- **Gram Vaani.** Mobile Vaani is an IVR service. Being purely voice-based makes it accessible to poorly literate communities. It has used IVR since 2010 to reach close to 100,000 unique monthly users. — [MIT Solve: Saajha Manch Mobile Vaani](https://solve.mit.edu/solutions/7355)
- **Peer-reviewed evaluation.** BMJ Global Health published an evaluation of Kilkari (supplement article). — [BMJ Global Health](https://gh.bmj.com/content/6/Suppl_5/e005213)
- **Gnani reach.** Press coverage reports Gnani handles about 30M daily interactions (aggregator; unverified). — [claw-times](https://claw-times.pages.dev/articles/india-voice-ai-startup-surge-160m-funded-gnani-ai-30m-daily-interactions/)

### Inferences
- A pitch line such as "works on any phone, no smartphone or data needed, like Kilkari's 11M-subscriber reach" is defensible with these sources.

### Gaps
- No current (2025-2026) Gram Vaani reach figure was found.
- Digital Green and Kisan Call Centre statistics were not retrieved within the tool budget.
- No India feature-phone share statistic was retrieved.
