# LinkedIn post: Pakkam (Gnani.ai Great Indian AI Internship Challenge 2026)

## Which video to post
| File | Length | Use it for |
|---|---|---|
| `pakkam-90s.mp4` | 1:22 | **The main post.** It has the hook, Rumour Shield, the Tamil voice question, the proof page, the honest refusal and the numbers. |
| `pakkam-60s.mp4` | 0:55 | Reels, X, a WhatsApp status, or the challenge form if it asks for 60 s or less |
| `pakkam-full.mp4` | 2:00 | The full demo, adding the four languages and the "under the hood" view. Link it in the first comment, or use it if the form asks for 2–3 minutes. |

Each video has a matching `.srt` file (English captions). Captions are already burned into the video. Uploading the `.srt` as well makes the captions searchable and lets viewers turn them off.
Thumbnail: `linkedin-thumbnail.jpg`.

Everything in the video is the real live site, recorded on 6 Nov 2026:
- the Tamil question is real speech, transcribed by Gnani Prisma
- the narration and the Tamil answer are spoken by Gnani Timbre

## Post text (copy everything between the lines)

---
A WhatsApp forward said Magalir Urimai is now Rs.2,000 a month. "Register today only. Share your OTP."

It isn't true. The official Government Order says Rs.1,000. But how would my grandfather know that?

So we built **Pakkam (பக்கம், "page" in Tamil)**: ask about a government welfare scheme in your own language, by voice, and get the answer **with its proof**, the exact page of the official document.

🔎 Paste a forward into Rumour Shield: every claim is checked against the Government Order, and scam tricks (short links, OTP requests, fake deadlines) are flagged.
🎙️ Speak in Tamil, Tanglish, Hindi or English. Gnani Prisma listens, Gnani Timbre answers out loud.
📄 Every sentence points to a page. One tap opens it, with the line highlighted.
🙅 If the documents don't say it, Pakkam says so. It never guesses.

Tested live on 194 real questions:
✅ 98% of answers cite the correct page
✅ 39 of 40 out-of-scope questions honestly refused (the one miss is in our public report)

உங்கள் மொழியில் கேளுங்கள். ஆதாரத்துடன் பதில் பெறுங்கள்.
(Ask in your language. Get the answer with its proof.)

Try it: https://pakkam-alpha.vercel.app
Code and test report: https://github.com/mailtojaswanthss-svg/pakkam

Built by Mohit K and me for the Great Indian AI Internship Challenge by Gnani.ai. Video narrated by Gnani Timbre.

#GreatIndianAIInternshipChallenge #GnaniAI #AIForBharat #VoiceAI #TamilNadu #GovTech #ResponsibleAI
---

When posting, type "@" and pick **Gnani.ai** and **Mohit K** from the list so they are real tags. A plain-text "@" does not notify anyone.

## First comment (post it right after the post goes live)
> 🎬 Full 2-minute demo (four languages and how it works under the hood): [attach pakkam-full.mp4 or a link to it]
> 📊 How we tested, including the one miss: https://github.com/mailtojaswanthss-svg/pakkam/blob/main/docs/review/LIVE_BENCHMARK.md
> Pakkam is a student research prototype, not a government service. Always check the official source before you act.

## How to post (about 10 minutes)
1. **Laptop, 2 min.** Run `start_pakkam.ps1` and keep the backend and tunnel windows open, so people who click the link get live answers.
2. **LinkedIn, 5 min.**
   1. Click **Start a post**, then the media icon, and choose `pakkam-90s.mp4`.
   2. In the video settings: **Thumbnail** → upload `linkedin-thumbnail.jpg`; **Captions** → upload `pakkam-90s.srt`.
   3. Paste the post text and add the real @ tags (Gnani.ai, Mohit K). Click **Post**.
3. **First comment, 1 min.** Paste the first comment above.
4. **Mohit, 2 min.** Repost with his own line (for example "Proud to have built the design and frontend of Pakkam with Jaswanth").
5. **Afterwards.** Reply to every comment in the first 2 hours. Early replies help the post reach more people.

Best time to post: a weekday between 8 and 10 AM IST.

## Video script (what each scene shows and says)
| Time (90 s cut) | On screen | Narration (Gnani Timbre) |
|---|---|---|
| 0:00 | A family-group forward: "Rs.2,000 … share OTP", then "Is it true?" | Forwards like this reach families across Tamil Nadu every day. But is it true? |
| 0:07 | Rumour Shield: "This forward is wrong", the claims checked against G.O.15, the warning signs | Pakkam's Rumour Shield checks it against the official Government Order. The amount is false, and it flags the scam tricks. |
| 0:14 | Home: "Tap. Ask. See the proof." | This is Pakkam. Ask in your language, and get the answer with its proof. |
| 0:20 | The orb listens to a Tamil question, Prisma's transcript appears, the Tamil answer with its source | Just tap the orb and ask, here in Tamil. Gnani Prisma turns the voice into text… *(then Pakkam answers aloud in Tamil, subtitled)* |
| 0:46 | The proof viewer: G.O.(Ms) No.15, page 3, checked against the printed page | Every answer shows its source. One tap opens the exact page… |
| 0:56 | "When will the next PM-KISAN instalment come?" → Not in the documents, plus the helpline | And when the documents don't say it, Pakkam says so. It never guesses. |
| 1:04 | Tested, honestly: 194 / 98% / 39 of 40, and the method | We tested it live on 194 real questions… |
| 1:16 | End card: Tap. Ask. See the proof. · the link · Jaswanth S S & Mohit K | Pakkam. Tap. Ask. See the proof. |

## Rebuilding the videos
```
python scripts/video/make_voice.py WORK      # Gnani Timbre narration, via the live /speak
node   scripts/video/record_cards.js WORK    # opening and end cards
node   scripts/video/record_demo.js WORK     # the live site, with Tamil speech fed into the fake microphone
python scripts/video/build_video.py WORK docs/judge   # three cuts plus .srt files
```
The narration lines are in `scripts/video/script.json`. `record_demo.js` needs `WORK/fakemic.wav` (the Tamil question with 0.5 s of silence before it and 4 s after) and `WORK/tamil_answer.wav`, both made with `/speak`.
