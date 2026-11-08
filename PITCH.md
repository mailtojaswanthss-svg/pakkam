# Pakkam · பக்கம் — Solution Pitch

**Ask about a government welfare scheme in your own language, by voice. Get the answer with the exact page of the official document as proof, or an honest "I don't know". No page, no answer.**

**The problem.** The real rules of welfare schemes (who can apply, how much, which documents) sit in long Government Orders in formal Tamil or official English that few families read. So people rely on WhatsApp forwards and middlemen, and miss benefits or fall for scams. When it is someone's ₹1,000 a month, a confident wrong answer is worse than no answer, and general chatbots answer anyway.

**Our solution.** Pakkam (Tamil for *page*) is a voice-first assistant that answers only from 18 official scheme documents. You speak naturally ("Magalir urimai ku income limit evlo?") and hear the answer: family income below ₹2.5 lakh, G.O.(Ms) No.15, page 10. One tap opens that page with the line highlighted: evidence you can show at a government counter.

**How it works.** Gnani Prisma speech to text → hybrid search (BGE-M3 + reranker) over the official PDFs → an answer where every sentence must cite a page and every number must appear on that page → if a check fails, Pakkam refuses and gives the official helpline → Gnani Timbre speaks the answer.

**What makes it different**
- **Proof, not prose:** the order number, page and exact line behind every sentence.
- **Knows when not to answer:** refuses honestly instead of guessing.
- **Human-checked facts:** 26 key answers checked by hand against the printed orders and signed.
- **Built for real moments:** Rumour Shield checks WhatsApp forwards and flags scam traps (fake links, OTP); "What can my family get?"; an appeal note quoting the exact rule after a rejection.
- **Voice that feels instant:** speaks "checking the government order…" while it verifies.

**Results (live site, 145 questions in Tamil, Hindi and English):** 98% of answers cite the correct government page; 29 of 30 out-of-scope questions honestly refused (the one miss is published in our report).

**Built on Gnani.ai:** Prisma v3.0 (speech to text, with scheme names as key terms and code-mixed speech) and Timbre (natural Tamil, Hindi and English speech).

**Impact and next steps.** Helps families, elderly people and the volunteers who assist them get the right rule with proof. Next: keep up to date with new Government Orders, answer broad questions ("schemes for unemployed youth") with proof for each scheme, and field-test with real voices on budget phones.

**Team:** Jaswanth S S (idea, AI, backend, frontend) · Mohit K (design, frontend)
**Links:** Live site https://pakkam-alpha.vercel.app · Code https://github.com/mailtojaswanthss-svg/pakkam · Demo video `docs/judge/pakkam-90s.mp4`

*Student research prototype for the Great Indian AI Internship Challenge 2026 by Gnani.ai. Not an official government service.*
