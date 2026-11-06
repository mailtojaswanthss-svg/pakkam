/* Pakkam's background: a calm, composed scene instead of random particles.

   - A few decorative pieces of "paperwork" (a government order with a seal circle, an
     application form with boxes, a page of text lines) placed at fixed anchor points in the
     side areas. They carry no readable words, numbers or emblems, so nothing could pass for a
     real document.
   - 5 on desktop (7 with Settings > Background > Ambient), at most 2 on phones, none with
     Minimal. Never drawn behind the headline, the orb or any control: anchors that would
     overlap them are skipped.
   - 8-12 tiny specks at seeded positions that twinkle slowly.
   - Each document is drawn once to a sprite; the loop only moves sprites (about 30 fps).
     Paused when the tab or canvas is hidden; one still frame for "reduce animations". */
(() => {
  'use strict';

  const canvas = document.getElementById('bg-pages');
  if (!canvas || !canvas.getContext) return;
  canvas.setAttribute('aria-hidden', 'true');
  const ctx = canvas.getContext('2d');
  const root = document.documentElement;
  const reducedQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  // Anchor points in % of the viewport: [x, y, template, size, tilt in degrees]
  const DESKTOP = [
    [7, 20, 'order', 92, -8], [5, 72, 'form', 84, 6], [93, 24, 'text', 88, 7],
    [95, 62, 'order', 76, -5], [84, 90, 'form', 80, 10],
  ];
  const AMBIENT_EXTRA = [[16, 47, 'text', 70, 9], [88, 44, 'form', 66, -9]];
  const PHONE = [[4, 34, 'text', 64, -8], [96, 66, 'order', 60, 7]];
  const KEEP_CLEAR = '.page-section.active h1, .page-section.active .hero-title, #hero-orb-assembly, #assistant-orb-assembly, .page-section.active button, .page-section.active a, .page-section.active input, .page-section.active textarea, .navbar-capsule, .tab-bar';

  let width = 0;
  let height = 0;
  let ratio = 1;
  let docs = [];
  let specks = [];
  let sprites = {};
  let colors = {};
  let frame = null;
  let last = 0;
  let born = 0;
  let visible = true;

  const calm = () => reducedQuery.matches || root.classList.contains('calm');
  const mode = () => root.dataset.bg || 'balanced';

  /** Small seeded random numbers, so the specks sit in the same places on every visit. */
  function seeded(seed) {
    let t = seed >>> 0;
    return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
  }

  function readColors() {
    const style = getComputedStyle(root);
    const pick = (name, fallback) => (style.getPropertyValue(name) || '').trim() || fallback;
    colors = { ink: pick('--text-primary', '#f5f3ff'), accent: pick('--accent-2', '#a855f7'), cyan: pick('--accent-cyan', '#42ddeb'), dark: root.dataset.theme !== 'light' };
  }

  /** Draw one decorative document into its own small canvas (done once per theme). */
  function makeSprite(template) {
    const w = 120;
    const h = 156;
    const s = 2;  // drawn at 2x for crisp edges
    const c = document.createElement('canvas');
    c.width = (w + 8) * s; c.height = (h + 8) * s;
    const g = c.getContext('2d');
    g.scale(s, s);
    g.translate(4, 4);
    g.lineJoin = 'round';
    g.lineCap = 'round';
    // the sheet: soft fill, outline, folded corner
    g.fillStyle = colors.dark ? 'rgba(255,255,255,0.035)' : 'rgba(255,255,255,0.65)';
    g.strokeStyle = colors.ink;
    g.lineWidth = 1.3;
    g.beginPath();
    g.moveTo(8, 0); g.lineTo(w - 22, 0); g.lineTo(w, 22); g.lineTo(w, h - 8);
    g.quadraticCurveTo(w, h, w - 8, h); g.lineTo(8, h); g.quadraticCurveTo(0, h, 0, h - 8);
    g.lineTo(0, 8); g.quadraticCurveTo(0, 0, 8, 0);
    g.fill(); g.stroke();
    g.beginPath(); g.moveTo(w - 22, 0); g.lineTo(w - 22, 22); g.lineTo(w, 22); g.stroke();
    const line = (x, y, len, alpha = 1) => { g.globalAlpha = alpha; g.fillRect(x, y, len, 2.2); g.globalAlpha = 1; };
    g.fillStyle = colors.ink;
    if (template === 'order') {
      // a seal circle at the top, a title bar, text lines, a signature curve
      g.strokeStyle = colors.accent;
      g.beginPath(); g.arc(w / 2, 26, 12, 0, Math.PI * 2); g.stroke();
      g.beginPath(); g.arc(w / 2, 26, 7.5, 0, Math.PI * 2); g.stroke();
      g.fillStyle = colors.accent; line(w / 2 - 26, 46, 52, 0.9);
      g.fillStyle = colors.ink;
      for (let i = 0; i < 7; i += 1) line(14, 60 + i * 10, (w - 28) * (i === 6 ? 0.5 : 0.92 - (i % 3) * 0.08), 0.7);
      g.strokeStyle = colors.cyan;
      g.beginPath(); g.moveTo(w - 52, h - 18); g.bezierCurveTo(w - 44, h - 30, w - 34, h - 8, w - 22, h - 22); g.stroke();
    } else if (template === 'form') {
      // a header, labelled boxes and two tick boxes
      g.fillStyle = colors.accent; line(14, 16, 56, 0.9);
      g.fillStyle = colors.ink;
      g.strokeStyle = colors.ink;
      for (let i = 0; i < 4; i += 1) {
        line(14, 34 + i * 24, 30, 0.6);
        g.globalAlpha = 0.7; g.strokeRect(14, 39 + i * 24, w - 28, 10); g.globalAlpha = 1;
      }
      g.strokeStyle = colors.cyan;
      g.strokeRect(14, h - 30, 9, 9);
      g.beginPath(); g.moveTo(16, h - 26); g.lineTo(18.5, h - 23); g.lineTo(22, h - 29); g.stroke();
      g.fillStyle = colors.ink; line(28, h - 27, 40, 0.6);
    } else {
      // a page of text lines in two paragraphs
      g.fillStyle = colors.accent; line(14, 18, 64, 0.9);
      g.fillStyle = colors.ink;
      for (let i = 0; i < 5; i += 1) line(14, 34 + i * 10, (w - 28) * (i === 4 ? 0.6 : 0.9 - (i % 2) * 0.1), 0.7);
      for (let i = 0; i < 5; i += 1) line(14, 92 + i * 10, (w - 28) * (i === 4 ? 0.45 : 0.88 - (i % 2) * 0.12), 0.7);
    }
    return c;
  }

  function buildSprites() {
    readColors();
    sprites = { order: makeSprite('order'), form: makeSprite('form'), text: makeSprite('text') };
  }

  /** Rectangles of things the documents must never sit behind. */
  function clearZones() {
    return [...document.querySelectorAll(KEEP_CLEAR)]
      .map((n) => n.getBoundingClientRect())
      .filter((r) => r.width && r.height && r.bottom > 0 && r.top < height);
  }

  function layout() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    const phone = width < 640;
    let anchors = mode() === 'minimal' ? [] : phone ? PHONE : DESKTOP.concat(mode() === 'ambient' ? AMBIENT_EXTRA : []);
    const zones = clearZones();
    const scale = phone ? 0.8 : Math.min(1.15, Math.max(0.75, width / 1400));
    docs = [];
    anchors.forEach(([px, py, template, size, tilt], index) => {
      const w = size * scale;
      const h = w * 1.3;
      // Try the anchor, then small nudges towards the nearest side edge and up or down; skip it only
      // if every spot would sit behind text or a control.
      const out = px < 50 ? -1 : 1;
      const tries = [[0, 0], [out * 24, 0], [0, -48], [0, 48], [out * 24, -48], [out * 24, 48], [out * 40, 0]];
      for (const [dx, dy] of tries) {
        const x = (px / 100) * width + dx;
        const y = (py / 100) * height + dy;
        const box = { left: x - w / 2 - 10, right: x + w / 2 + 10, top: y - h / 2 - 12, bottom: y + h / 2 + 12 };
        const blocked = zones.some((r) => r.left < box.right && r.right > box.left && r.top < box.bottom && r.bottom > box.top);
        if (blocked) continue;
        docs.push({ x, y, w, h, template, tilt: (tilt * Math.PI) / 180, phase: index * 1.7, period: 20 + (index % 3) * 5 });
        break;
      }
    });
    if (phone) docs = docs.slice(0, 2);
    const rand = seeded(1729);
    const count = mode() === 'minimal' ? 0 : phone ? 4 : mode() === 'ambient' ? 12 : 9;
    specks = Array.from({ length: count }, (_, i) => ({ x: rand() * width, y: rand() * height, r: 1 + rand() * 1.4, phase: rand() * 6.28, cyan: i % 3 !== 0 }));
    draw(performance.now());
  }

  function draw(now) {
    if (!sprites.order) return;  // not started yet (resize or page change before boot)
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const t = calm() ? 0 : now / 1000;
    const fadeIn = calm() ? 1 : Math.min(1, (now - born) / 1200);
    const docAlpha = (colors.dark ? 0.2 : 0.32) * fadeIn;
    for (let i = 0; i < docs.length; i += 1) {
      const d = docs[i];
      const wave = Math.sin((t / d.period) * Math.PI * 2 + d.phase);
      ctx.save();
      ctx.globalAlpha = docAlpha;
      ctx.translate(d.x, d.y + wave * 8);
      ctx.rotate(d.tilt + wave * 0.026);
      ctx.drawImage(sprites[d.template], -d.w / 2, -d.h / 2, d.w * (128 / 120), d.h * (164 / 156));
      ctx.restore();
    }
    for (let i = 0; i < specks.length; i += 1) {
      const p = specks[i];
      ctx.globalAlpha = (0.25 + 0.35 * (0.5 + 0.5 * Math.sin(t * 0.6 + p.phase))) * fadeIn;
      ctx.fillStyle = p.cyan ? colors.cyan : colors.accent;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function step(now) {
    frame = requestAnimationFrame(step);
    if (now - last < 33) return;  // about 30 frames a second
    last = now;
    draw(now);
  }

  function start() {
    stop();
    draw(performance.now());
    if (calm() || document.hidden || !visible || (!docs.length && !specks.length)) return;
    last = performance.now();
    frame = requestAnimationFrame(step);
  }

  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = null;
  }

  function refresh() { buildSprites(); layout(); start(); }

  let booted = false;
  const whenBooted = (fn) => () => { if (booted) fn(); };
  window.addEventListener('resize', whenBooted(() => { layout(); start(); }));
  document.addEventListener('visibilitychange', whenBooted(() => (document.hidden ? stop() : start())));
  document.addEventListener('pakkam:page', whenBooted(() => { layout(); start(); }));  // a different page has different controls
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; if (!booted) return; if (visible) start(); else stop(); }).observe(canvas);
  }
  if (reducedQuery.addEventListener) reducedQuery.addEventListener('change', whenBooted(start));
  new MutationObserver(whenBooted(refresh)).observe(root, { attributes: true, attributeFilter: ['data-theme', 'data-bg'] });
  new MutationObserver(whenBooted(start)).observe(root, { attributes: true, attributeFilter: ['class'] });
  window.PakkamBackground = {
    start, stop, isAnimating: () => Boolean(frame),
    stats: () => ({ count: docs.length + specks.length, docs: docs.map((d) => ({ x: Math.round(d.x), y: Math.round(d.y), w: Math.round(d.w), h: Math.round(d.h), template: d.template })), specks: specks.length, xs: docs.map((d) => Math.round(d.x)), colors: { line: colors.ink } }),
  };

  // Start after the page has painted, so the background never delays the first view.
  const boot = () => {
    born = performance.now();
    booted = true;
    refresh();
    // Text can change size once the web fonts arrive: place the documents again then.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { layout(); start(); });
  };
  const later = () => (window.requestIdleCallback ? requestIdleCallback(boot, { timeout: 1500 }) : setTimeout(boot, 300));
  if (document.readyState === 'complete') later();
  else window.addEventListener('load', later, { once: true });
})();
