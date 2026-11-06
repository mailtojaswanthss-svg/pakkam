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
  // Serve the front end from this checkout (main), so the video shows the latest copy even before
  // the laptop redeploys Vercel. Every API call still goes to the live backend.
  const WEB = path.join(__dirname, '..', '..', 'web');
  await page.route(/\/(index\.html)?(\?.*)?$|\/js\/[a-z]+\.js|\/Styles\/[A-Za-z]+\.css/, async (route) => {
    const u = new URL(route.request().url());
    if (u.origin !== new URL(SITE).origin) return route.continue();
    const rel = u.pathname === '/' ? 'index.html' : u.pathname.slice(1);
    const file = path.join(WEB, rel);
    if (!fs.existsSync(file)) return route.continue();
    const type = rel.endsWith('.js') ? 'text/javascript' : rel.endsWith('.css') ? 'text/css' : 'text/html';
    return route.fulfill({ status: 200, contentType: `${type}; charset=utf-8`, body: fs.readFileSync(file) });
  });
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

  const navTo = async (key) => { await click(page.locator(`[data-nav="${key}"]`).filter({ visible: true }).first()); await sleep(900); };
  const smoothTo = (selector, block = 'center') => page.evaluate(([sel, blk]) => document.querySelector(sel)?.scrollIntoView({ behavior: 'smooth', block: blk }), [selector, block]);

  // Set up off camera: Tamil as the spoken language, then back to Home (cut in the edit).
  await page.goto(SITE, { waitUntil: 'networkidle' });
  await sleep(2500);
  await navTo('settings');
  await click(page.locator('.settings-voice-chips button', { hasText: 'தமிழ்' }));
  await navTo('home');
  await sleep(1500);
  mark('ready');

  // Lakshmi story. l3: Pakkam's home page (the reveal)
  mark('l3');
  await sleep(1000 * (D.l3_intro + 1.5));
  mark('l3_end');

  // l4: she taps the orb and asks in Tamil; the answer comes with the order and page; she opens it
  mark('l4');
  await holdUntil(marks.l4, D.l4_ask + 0.4);
  await click(page.locator('#hero-orb-trigger'));
  mark('l4_mic');
  await page.waitForFunction(() => { const c = document.getElementById('home-answer'); return c && !c.hidden && c.querySelector('.proof-btn'); }, null, { timeout: 120000 });
  mark('l4_answer');
  await sleep(600);
  await smoothTo('#home-convo', 'center');
  await sleep(1000 * (D.l4_ask_b + D.tamil_answer + 1.0));
  mark('l4_proof');
  await click(page.locator('#home-answer .proof-btn').first());
  await sleep(1000 * (D.l4_ask_c + 2.4));
  await page.keyboard.press('Escape');
  await sleep(500);
  mark('l4_end');

  // l5: the honest refusal, typed on the Ask page
  await page.evaluate(() => window.scrollTo({ top: 0 }));
  await click(page.locator('#cta-ask-pakkam'));
  await sleep(900);
  mark('l5');
  await ask('When will the next PM-KISAN installment come?', 'refusal');
  await sleep(1000 * (D.l5_refusal_short + 2.0));
  mark('l5_end');

  // l5b: the honest test numbers on About > Tested
  await navTo('about');
  await click(page.locator('#tab-tested'));
  mark('l5b');
  await sleep(6000);
  mark('l5b_end');

  // l6: the bigger picture: Rumour Shield, schemes, languages
  await page.evaluate(() => window.scrollTo({ top: 0 }));
  await navTo('shield');
  mark('l6_shield');
  await click(page.locator('#shield-input'));
  await page.locator('#shield-input').fill(SCRIPT.forward);
  await sleep(600);
  await click(page.locator('#shield-check'));
  await page.waitForSelector('.shield-verdict-card', { timeout: 120000 });
  mark('l6_verdict');
  await sleep(800);
  await smoothTo('.shield-signs');
  await sleep(2600);
  mark('l6_verdict_end');
  await page.evaluate(() => window.scrollTo({ top: 0 }));
  await navTo('schemes');
  mark('l6_schemes');
  await sleep(1200);
  await smoothTo('#scheme-filters', 'start');
  await sleep(2400);
  mark('l6_schemes_end');
  await page.evaluate(() => window.scrollTo({ top: 0 }));
  await navTo('settings');
  mark('l6_lang');
  await sleep(800);
  for (const label of ['English', 'हिन्दी', 'தமிழ்']) {
    const chip = page.locator('.settings-voice-chips button', { hasText: label }).first();
    if (await chip.count()) { await click(chip); await sleep(700); }
  }
  mark('l6_lang_end');

  const video = page.video();
  await context.close();
  await browser.close();
  fs.renameSync(await video.path(), path.join(OUT, 'main.webm'));
  fs.writeFileSync(path.join(OUT, 'marks.json'), JSON.stringify(marks, null, 2));
  fs.writeFileSync(path.join(OUT, 'answers.json'), JSON.stringify(answers, null, 2));
  console.log('done');
})().catch((e) => { console.error(e); process.exit(1); });
