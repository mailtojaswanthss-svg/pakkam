/* Pakkam's living background ("pakkam" = page): page outlines, Tamil and Hindi letters, ₹,
   small glowing dots, faint circles and thin lines between nearby dots, drifting slowly upward.

   - Spread over the whole screen with a jittered grid (no clumps, no empty holes), with random
     size and opacity so it never looks regular. Items over the central text column are drawn
     much fainter, so text always stays readable.
   - Colours follow the theme. Density follows the screen and Settings > Background
     (minimal: none, balanced, ambient: more).
   - Cheap: device-pixel ratio capped at 2, about 30 frames a second, no objects created per
     frame, glow sprites drawn once, neighbour lines checked pair by pair with squared distances.
   - One still frame for "reduce animations"; paused when the tab or canvas is hidden. */
(() => {
  'use strict';

  const canvas = document.getElementById('bg-pages');
  if (!canvas || !canvas.getContext) return;
  canvas.setAttribute('aria-hidden', 'true');
  const ctx = canvas.getContext('2d');
  const root = document.documentElement;
  const LETTERS = ['ப', 'க', 'ம்', 'அ', 'இ', 'த', 'प', 'क', 'म', '₹', 'பக்கம்'];
  const KINDS = ['page', 'letter', 'dot', 'dot', 'dot', 'circle'];
  const reducedQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  const LINK = 170;            // px: dots closer than this get a faint line
  const LINK2 = LINK * LINK;

  let items = [];
  let dots = [];
  let width = 0;
  let height = 0;
  let ratio = 1;
  let colors = { line: '#cfe7ee', accent: '#a78bfa', cyan: '#39dde5' };
  let sprites = {};
  let last = 0;
  let frame = null;
  let visible = true;
  let columnLeft = 0;
  let columnRight = 0;

  const calm = () => reducedQuery.matches || root.classList.contains('calm');
  const mode = () => root.dataset.bg || 'balanced';

  function readColors() {
    const style = getComputedStyle(root);
    const pick = (name, fallback) => (style.getPropertyValue(name) || '').trim() || fallback;
    colors = { line: pick('--text-primary', '#cfe7ee'), accent: pick('--accent-2', '#a78bfa'), cyan: pick('--accent-cyan', '#39dde5') };
    sprites = { cyan: glowSprite(colors.cyan), accent: glowSprite(colors.accent) };
  }

  /** A soft round glow, drawn once and reused (no shadow-blur in the loop). */
  function glowSprite(color) {
    const size = 32;
    const sprite = document.createElement('canvas');
    sprite.width = size; sprite.height = size;
    const g = sprite.getContext('2d');
    const grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    grad.addColorStop(0, color);
    grad.addColorStop(0.25, color);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, size, size);
    return sprite;
  }

  function targetCount() {
    if (mode() === 'minimal') return 0;
    const base = width < 640 ? 10 : width < 1024 ? 18 : 40;
    return Math.round(base * (mode() === 'ambient' ? 1.6 : 1));
  }

  /** Reset one item in place (reused, never re-created while animating). */
  function place(item, x, y) {
    const kind = KINDS[Math.floor(Math.random() * KINDS.length)];
    const vary = 0.6 + Math.random() * 0.8;           // size ±40%
    item.kind = kind;
    item.x = x;
    item.y = y;
    item.size = kind === 'page' ? 34 * vary : kind === 'letter' ? 20 * vary : kind === 'circle' ? 26 * vary : 2.2 * vary;
    item.speed = 4 + Math.random() * 8;               // px per second
    item.angle = (Math.random() - 0.5) * 0.3;
    item.spin = (Math.random() - 0.5) * 0.02;
    item.alpha = (kind === 'dot' ? 0.5 : 0.08) * (0.5 + Math.random());   // opacity ±50%
    item.letter = LETTERS[Math.floor(Math.random() * LETTERS.length)];
    item.accent = Math.random() < 0.35;
    return item;
  }

  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    const column = Math.min(900, width * 0.72);
    columnLeft = (width - column) / 2;
    columnRight = columnLeft + column;
    // Jittered grid: one item per cell, at a random spot inside it.
    const count = targetCount();
    const cols = Math.max(1, Math.round(Math.sqrt((count * width) / Math.max(height, 1))));
    const rows = Math.max(1, Math.ceil(count / cols));
    const cw = width / cols;
    const ch = (height + 120) / rows;
    items = [];
    for (let i = 0; i < count; i += 1) {
      const c = i % cols;
      const r = Math.floor(i / cols);
      items.push(place({}, (c + 0.15 + Math.random() * 0.7) * cw, (r + 0.15 + Math.random() * 0.7) * ch - 60));
    }
    dots = items.filter((item) => item.kind === 'dot');
    readColors();
    draw();
  }

  /** Items over the central text column are drawn much fainter. */
  const fade = (x) => (x > columnLeft && x < columnRight ? 0.35 : 1);

  function drawPage(item) {
    const w = item.size;
    const h = item.size * 1.3;
    ctx.lineWidth = 1.1;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(-w / 2, -h / 2, w, h, 4);
    else ctx.rect(-w / 2, -h / 2, w, h);
    ctx.moveTo(w / 2 - 8, -h / 2);
    ctx.lineTo(w / 2, -h / 2 + 8);
    ctx.stroke();
    for (let i = 0; i < 4; i += 1) ctx.fillRect(-w / 2 + 6, -h / 2 + 11 + i * (h - 20) / 4, (w - 12) * (i === 3 ? 0.55 : 0.85), 1.3);
  }

  function drawLinks() {
    // Each pair once, squared distances only, nothing allocated (at most ~26 dots).
    ctx.lineWidth = 0.7;
    ctx.strokeStyle = colors.cyan;
    for (let i = 0; i < dots.length; i += 1) {
      const a = dots[i];
      for (let j = i + 1; j < dots.length; j += 1) {
        const b = dots[j];
        const dx = a.x - b.x;
        if (dx > LINK || dx < -LINK) continue;
        const dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 > LINK2) continue;
        ctx.globalAlpha = 0.12 * (1 - d2 / LINK2) * Math.min(fade(a.x), fade(b.x));
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    }
  }

  function draw() {
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    if (!items.length) return;
    drawLinks();
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      const alpha = item.alpha * fade(item.x);
      ctx.globalAlpha = alpha;
      if (item.kind === 'dot') {
        const sprite = item.accent ? sprites.accent : sprites.cyan;
        const s = item.size * 6;
        ctx.drawImage(sprite, item.x - s / 2, item.y - s / 2, s, s);
        continue;
      }
      ctx.save();
      ctx.translate(item.x, item.y);
      ctx.rotate(item.angle);
      const color = item.accent ? colors.accent : colors.line;
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      if (item.kind === 'page') drawPage(item);
      else if (item.kind === 'circle') { ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(0, 0, item.size, 0, Math.PI * 2); ctx.stroke(); }
      else {
        ctx.font = `600 ${item.size}px "Noto Sans Tamil", "Noto Sans Devanagari", system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(item.letter, 0, 0);
      }
      ctx.restore();
    }
    ctx.globalAlpha = 1;
  }

  function step(now) {
    frame = requestAnimationFrame(step);
    if (now - last < 33) return;  // about 30 frames a second
    const dt = Math.min((now - last) / 1000, 0.1);
    last = now;
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      item.y -= item.speed * dt;
      item.angle += item.spin * dt;
      if (item.y < -60) place(item, Math.random() * width, height + 40);
    }
    draw();
  }

  function start() {
    stop();
    readColors();
    if (items.length !== targetCount()) { resize(); } else draw();
    if (calm() || document.hidden || !visible || !items.length) return;
    last = performance.now();
    frame = requestAnimationFrame(step);
  }

  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = null;
  }

  // Parallax: on wide screens the pages drift a little against the scroll.
  let lastScroll = window.scrollY;
  window.addEventListener('scroll', () => {
    const delta = window.scrollY - lastScroll;
    lastScroll = window.scrollY;
    if (width < 900 || calm()) return;
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      item.y -= delta * 0.1;
      if (item.y < -60) place(item, Math.random() * width, height + 40);
      else if (item.y > height + 60) place(item, Math.random() * width, -40);
    }
    if (!frame) draw();
  }, { passive: true });

  window.addEventListener('resize', () => { resize(); start(); });
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; if (visible) start(); else stop(); }).observe(canvas);
  }
  if (reducedQuery.addEventListener) reducedQuery.addEventListener('change', start);
  // Theme, calm mode or background setting changed (app.js sets these on <html>).
  new MutationObserver(start).observe(root, { attributes: true, attributeFilter: ['data-theme', 'class', 'data-bg'] });
  window.PakkamBackground = {
    start, stop, isAnimating: () => Boolean(frame),
    stats: () => ({ count: items.length, xs: items.map((item) => Math.round(item.x)), colors: { ...colors } }),
  };
  // Start after the page has painted, so the background never delays the first view.
  const boot = () => { resize(); start(); };
  const later = () => (window.requestIdleCallback ? requestIdleCallback(boot, { timeout: 1500 }) : setTimeout(boot, 300));
  if (document.readyState === 'complete') later();
  else window.addEventListener('load', later, { once: true });
})();
