// Records the Pakkam demo from the live site, the way a visitor would use it.
//
//   node scripts/video/record_demo.js OUT_DIR
//
// Needs OUT_DIR/durations.json and OUT_DIR/fakemic.wav (see make_voice.py). Writes
// OUT_DIR/main.webm (one continuous take of the site), OUT_DIR/marks.json (when each scene
// starts, in seconds) and OUT_DIR/answers.json (the answer texts shown on screen).
// The Tamil question is real speech played into Chromium's fake microphone, so Gnani Prisma
// transcribes it live. Scenes wait for their narration, so the edit never has to stretch.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.resolve(process.argv[2]);
const SCRIPT = JSON.parse(fs.readFileSync(path.join(__dirname, 'script.json'), 'utf8'));
const D = JSON.parse(fs.readFileSync(path.join(OUT, 'durations.json'), 'utf8'));
const SITE = SCRIPT.site;
const W = 1536;
const H = 864;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const CURSOR = () => {
  const add = () => {
    if (document.getElementById('__cur')) return;
    const style = document.createElement('style');
    style.textContent = '@keyframes __rip{from{transform:scale(.4);opacity:1}to{transform:scale(1.7);opacity:0}}';
    document.head.appendChild(style);
    const c = document.createElement('div');
    c.id = '__cur';
    c.style.cssText = 'position:fixed;z-index:2147483647;left:-40px;top:-40px;width:26px;height:26px;pointer-events:none;filter:drop-shadow(0 2px 4px rgba(0,0,0,.5))';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 2.5l15.5 9.8-6.8 1.4-3.7 6.8z" fill="#fff" stroke="#0b1020" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(c);
    document.addEventListener('mousemove', (e) => { c.style.left = `${e.clientX - 3}px`; c.style.top = `${e.clientY - 2}px`; }, true);
    document.addEventListener('mousedown', (e) => {
      const r = document.createElement('div');
      r.style.cssText = `position:fixed;z-index:2147483646;left:${e.clientX - 20}px;top:${e.clientY - 20}px;width:40px;height:40px;border-radius:50%;border:3px solid #42DDEB;pointer-events:none;animation:__rip .65s ease-out forwards`;
      document.documentElement.appendChild(r);
      setTimeout(() => r.remove(), 700);
    }, true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
};

(async () => {
  const browser = await chromium.launch({
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', `--use-file-for-fake-audio-capture=${path.join(OUT, 'fakemic.wav')}`, '--autoplay-policy=no-user-gesture-required'],
  });
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
    permissions: ['microphone'],
    recordVideo: { dir: OUT, size: { width: W, height: H } },
  });
  const t0 = Date.now();
  const marks = {};
  const answers = {};
  const mark = (name) => { marks[name] = (Date.now() - t0) / 1000; console.log(name, marks[name].toFixed(2)); };
  const page = await context.newPage();
  await page.addInitScript(() => { try { localStorage.setItem('pakkam_theme', 'dark'); localStorage.setItem('pakkam_lang', 'en-IN'); } catch (_) {} });
  await page.addInitScript(CURSOR);
  let mx = W / 2;
  let my = H / 2;
  const moveTo = async (locator, dx = 0.5, dy = 0.5) => {
    await locator.scrollIntoViewIfNeeded().catch(() => {});
    const b = await locator.boundingBox();
    const x = b.x + b.width * dx;
    const y = b.y + b.height * dy;
    const steps = Math.max(12, Math.round(Math.hypot(x - mx, y - my) / 22));
    await page.mouse.move(x, y, { steps });
    mx = x; my = y;
  };
  const click = async (locator) => { await moveTo(locator); await sleep(180); await page.mouse.down(); await sleep(70); await page.mouse.up(); await sleep(250); };
  const holdUntil = async (start, seconds) => { const left = start + seconds - (Date.now() - t0) / 1000; if (left > 0) await sleep(left * 1000); };
  const aiCount = () => page.evaluate(() => document.querySelectorAll('#chat-messages .chat-bubble.ai').length);
  const waitAnswer = async (before, timeout = 90000) => {
    const end = Date.now() + timeout;
    let last = '';
    let stableSince = 0;
    while (Date.now() < end) {
      const state = await page.evaluate(() => {
        const all = document.querySelectorAll('#chat-messages .chat-bubble.ai');
        const b = all[all.length - 1];
        return { n: all.length, text: b ? b.innerText : '', done: Boolean(b && (b.querySelector('.source-pill') || /NOT IN THE DOCUMENTS|could not find|couldn't find/i.test(b.innerText))) };
      });
      if (state.n > before && state.done) {
        if (state.text === last) { if (Date.now() - stableSince > 1200) return state.text; } else { last = state.text; stableSince = Date.now(); }
      }
      await sleep(250);
    }
    throw new Error('answer did not arrive');
  };
  const ask = async (question, key) => {
    const input = page.locator('#chat-input');
    await click(input);
    await input.pressSequentially(question, { delay: 45 });
    await sleep(300);
    const before = await aiCount();
    await page.keyboard.press('Enter');
    mark(`${key}_sent`);
    answers[key] = await waitAnswer(before);
    mark(`${key}_answer`);
  };

  // Load once and let the home intro finish off camera time (cut in the edit).
  await page.goto(SITE, { waitUntil: 'networkidle' });
  await sleep(3500);
  mark('ready');

  // s02: Rumour Shield
  await click(page.locator('.nav-item[data-nav="shield"]'));
  await sleep(900);
  mark('s02');
  await sleep(500);
  await click(page.locator('#shield-input'));
  await page.locator('#shield-input').fill(SCRIPT.forward);
  await sleep(1200);
  await click(page.locator('#shield-check'));
  await page.waitForSelector('.shield-verdict-card', { timeout: 120000 });
  mark('s02_verdict');
  await sleep(1500);
  await page.mouse.wheel(0, 380);
  await sleep(1800);
  await page.mouse.wheel(0, 320);
  await holdUntil(marks.s02, D.s02_shield + 1.2);
  mark('s02_end');

  // s03: home
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(400);
  await click(page.locator('.nav-item[data-nav="home"]'));
  await sleep(600);
  mark('s03');
  await holdUntil(marks.s03, Math.max(D.s03_home + 1.2, 5));
  mark('s03_end');

  // s04: voice question in Tamil, on the Ask page
  await click(page.locator('#cta-ask-pakkam'));
  await sleep(1000);
  mark('s04');
  await click(page.locator('#voice-lang-chips button', { hasText: 'தமிழ்' }));
  await holdUntil(marks.s04, D.s04_voice + 0.3);
  const before = await aiCount();
  await click(page.locator('#assistant-mic-orb'));
  mark('s04_mic');
  answers.s04 = await waitAnswer(before, 120000);
  mark('s04_answer');
  await sleep(1000 * (D.s04_voice_b + 9));
  mark('s04_end');

  // s05: open the proof
  mark('s05');
  const pill = page.locator('#chat-messages .chat-bubble.ai').last().locator('.source-pill').first();
  await click(pill);
  await sleep(2500);
  await holdUntil(marks.s05, D.s05_proof + 1.5);
  await page.keyboard.press('Escape');
  await sleep(600);
  mark('s05_end');

  // s06: three more languages, typed
  await click(page.locator('#voice-lang-chips button', { hasText: 'English' }));
  mark('s06');
  await ask('PM Kisan la varushathuku evlo?', 'tanglish');
  await sleep(2500);
  await ask('अटल पेंशन किसे मिलती है?', 'hindi');
  await sleep(2500);
  await ask('Who gets free breakfast at school?', 'english');
  await sleep(2500);
  mark('s06_end');

  // s07: honest refusal
  mark('s07');
  await ask('When will the next PM-KISAN installment come?', 'refusal');
  await sleep(1000 * (D.s07_refusal + 1.5));
  mark('s07_end');

  // s08: under the hood
  await click(page.locator('.nav-item[data-nav="about"]'));
  await sleep(900);
  await click(page.locator('#tab-how'));
  await sleep(500);
  await page.evaluate(() => document.querySelector('.pipeline').scrollIntoView({ behavior: 'smooth', block: 'center' }));
  await sleep(1100);
  mark('s08');
  await holdUntil(marks.s08, D.s08_how + 1.2);
  mark('s08_end');

  // s09: tested, honestly
  await page.evaluate(() => document.querySelector('.about-tablist').scrollIntoView({ behavior: 'smooth', block: 'start' }));
  await sleep(900);
  await click(page.locator('#tab-tested'));
  mark('s09');
  await sleep(1800);
  await page.evaluate(() => document.querySelector('.test-method').scrollIntoView({ behavior: 'smooth', block: 'center' }));
  await holdUntil(marks.s09, D.s09_numbers + 1.5);
  mark('s09_end');

  const video = page.video();
  await context.close();
  await browser.close();
  fs.renameSync(await video.path(), path.join(OUT, 'main.webm'));
  fs.writeFileSync(path.join(OUT, 'marks.json'), JSON.stringify(marks, null, 2));
  fs.writeFileSync(path.join(OUT, 'answers.json'), JSON.stringify(answers, null, 2));
  console.log('done');
})().catch((e) => { console.error(e); process.exit(1); });
