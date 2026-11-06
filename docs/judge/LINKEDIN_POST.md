# LinkedIn post: Pakkam (Gnani.ai Great Indian AI Internship Challenge 2026)

## Which video to post
| File | Length | Use it for |
|---|---|---|
| `pakkam-90s.mp4` | 1:15 | **The main LinkedIn post.** Opens on the forward ("Is it true?"), then Lakshmi's story: the forward, the 40-page order, asking Pakkam in Tamil, the page as proof, the honest refusal, the wider features. |
| `pakkam-60s.mp4` | 0:55 | Short sharing: Reels, X, WhatsApp status. |
| `pakkam-full.mp4` | 1:24 | For judges: adds the test results (39 of 40 refused, the one failure). |

Thumbnail: `linkedin-thumbnail.jpg`. No subtitles or captions: the narrator explains each scene, over soft original background music (generated, royalty-free).

Lakshmi is a fictional, illustrative character (the post text says so). Everything else is the real live site, recorded on 6 Nov 2026:
- the Tamil question is real speech, transcribed live by Gnani Prisma
- the answer (Rs.2.5 lakh income limit, G.O.(Ms) No.15, page 10) and the page shown are real
- the narration and Pakkam's Tamil answer are both Gnani Timbre; the narrator is pitched lower so the two are easy to tell apart

## Post text (copy everything between the lines)

---
A question she shouldn't have to struggle to ask.

Meet Lakshmi, a mother in Tamil Nadu (a fictional character, but her problem is real). A forward in the family group says Magalir Urimai is now Rs.2,000 a month. Is it true? Is she even eligible?

The answer exists. It's buried in a 40-page Government Order. She shouldn't need to understand a 40-page document to understand her rights.

So we built **Pakkam (பக்கம், "page" in Tamil)**.
🎙️ Ask by voice in Tamil, Tanglish, Hindi or English. Gnani Prisma listens, Gnani Timbre answers aloud.
📄 Every answer comes with the order number and page. One tap opens the original, with the line highlighted.
🙅 If the documents don't say it, Pakkam says so. It never guesses.
🔎 Rumour Shield checks WhatsApp forwards against the official order and flags scam tricks.

We tested it live on 194 real questions: 98% cite the correct page. Of 40 questions outside the documents, it correctly refused 39. The one failure is in our public report, and it showed us where to improve.

Speak. Hear. See the proof. Because everyone deserves to know.

Try it: https://pakkam-alpha.vercel.app
Code and test report: https://github.com/mailtojaswanthss-svg/pakkam

Built by Mohit K and me for the Great Indian AI Internship Challenge by Gnani.ai.

#GreatIndianAIInternshipChallenge #GnaniAI #AIForBharat #VoiceAI #TamilNadu #GovTech #ResponsibleAI
---

When posting, type "@" and pick **Gnani.ai** and **Mohit K** from the list so they are real tags.

## First comment (post right after the post goes live)
> 🎬 Full version for judges, with the test results: https://github.com/mailtojaswanthss-svg/pakkam/blob/main/docs/judge/pakkam-full.mp4
> 📊 How we tested, including the one miss: https://github.com/mailtojaswanthss-svg/pakkam/blob/main/docs/review/LIVE_BENCHMARK.md
> Pakkam is a student research prototype, not a government service. Always check the official source before you act.

## How to post (about 10 minutes)
1. **Laptop, 2 min.** Run `start_pakkam.ps1` and keep the backend and tunnel windows open, so people who click the link get live answers.
2. **LinkedIn, 5 min.** Start a post → media icon → `pakkam-90s.mp4` → Thumbnail: `linkedin-thumbnail.jpg`. Paste the post text, add the real @ tags, click **Post**.
3. **First comment, 1 min.** Paste the first comment above.
4. **Mohit, 2 min.** Repost with his own line.
5. **Afterwards.** Reply to every comment in the first 2 hours.

Best time: a weekday, 8–10 AM IST.

## Video script (90 s cut)
| Time | On screen | Narration |
|---|---|---|
| 0:00 | The family-group forward | Two thousand rupees a month? Share your OTP? Is it true? |
| 0:04 | Lakshmi at home with her phone | This is Lakshmi, a mother in Tamil Nadu. And this forward just landed in her family group. |
| 0:10 | Lakshmi among papers, then the real G.O.15 pages scrolling | …buried in a forty page Government Order… She shouldn't need to understand a forty page document to understand her rights. |
| 0:21 | Lakshmi speaking to the orb, then Pakkam's home ("Speak. Hear. See the proof.") | What if she could simply ask? That's why we built Pakkam. |
| 0:25 | Tap the orb, the Tamil question, the answer (Rs.2.5 lakh, G.O.15 page 10) spoken aloud, the original page opened | She taps the orb, and asks in her own words… |
| 0:48 | "When will the next PM-KISAN instalment come?" → Not in the documents | And when the documents don't say it, Pakkam won't guess. |
| 0:55 | Rumour Shield verdict, the scheme list, the language chips | Tamil, Tanglish, Hindi or English… |
| 1:03 | Lakshmi and her daughter, then the end card | Pakkam. Speak. Hear. See the proof. Because everyone deserves to know. |

The full cut replaces the short refusal line with: "We tested forty questions outside the documents. Pakkam correctly refused thirty nine. The one failure showed us where to improve. Lakshmi doesn't need an assistant with an answer for everything. She needs one that knows when it doesn't have one."

## Rebuilding the videos
```
python scripts/video/make_voice.py WORK      # Timbre narration via the live /speak (pitched lower) + Pakkam's Tamil voice
node   scripts/video/record_cards.js WORK    # opening and end cards
node   scripts/video/record_demo.js WORK     # the live site, Tamil speech fed into the fake microphone
python scripts/video/build_video.py WORK docs/judge   # illustrations + recording → three cuts
```
Lines are in `scripts/video/script.json`; illustrations in `scripts/video/art/` (Figma AI, faceless). `WORK` also needs `fakemic.wav` (the Tamil question with silence around it) and `go/p1,p2,p3,p10.png` (pages from the site's `/page?doc=kmut-go15-2023-ta&p=N`).
