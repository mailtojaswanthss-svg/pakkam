/* Floating pages behind Pakkam ("pakkam" = page): faint page outlines and letters drifting
   slowly upward. Colours follow the theme; one still frame when the viewer asks for less motion
   (system setting or Settings > Reduce animations); pauses when the tab is hidden. */
(() => {
  'use strict';

  const canvas = document.getElementById('bg-pages');
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  const LETTERS = ['ப', 'க', 'ம்', 'அ', 'இ', 'a', '₹', 'பக்கம்'];
  const reducedQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  let items = [];
  let lanes = [];      // x centres the items keep to: the side margins on wide screens
  let nextLane = 0;
  let width = 0;
  let height = 0;
  let ratio = 1;
  let colors = { line: 'rgba(160,220,230,1)', accent: 'rgba(170,130,255,1)' };
  let last = 0;
  let frame = null;

  const calm = () => reducedQuery.matches || document.documentElement.classList.contains('calm');

  function readColors() {
    const style = getComputedStyle(document.documentElement);
    const pick = (name, fallback) => (style.getPropertyValue(name) || '').trim() || fallback;
    colors = { line: pick('--text-primary', '#cfe7ee'), accent: pick('--accent-2', '#c4a5ff') };
  }

  function laneX() {
    const x = lanes[nextLane % lanes.length];
    nextLane += 1;
    return x + (Math.random() - 0.5) * 16;
  }

  function makeItem(randomY) {
    const page = Math.random() < 0.6;
    const size = page ? 40 + Math.random() * 40 : 18 + Math.random() * 20;
    return {
      page,
      size,
      x: laneX(),
      y: randomY ? Math.random() * height : height + size * 2,
      speed: 6 + Math.random() * 10,        // px per second
      drift: 0,
      angle: (Math.random() - 0.5) * 0.24,
      spin: (Math.random() - 0.5) * 0.02,
      alpha: 0.045 + Math.random() * 0.04,
      letter: LETTERS[Math.floor(Math.random() * LETTERS.length)],
      accent: Math.random() < 0.3,
    };
  }

  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    // Even lanes in the side margins, outside the ~1100px content column; spread across the
    // page only when the margins are too narrow (phones, small laptops), and fewer items there.
    const margin = (width - 1120) / 2;
    if (margin >= 110) {
      const perSide = margin >= 260 ? 2 : 1;
      lanes = [];
      for (let i = 0; i < perSide; i += 1) {
        const x = (margin * (i + 0.5)) / perSide;
        lanes.push(x, width - x);
      }
    } else {
      const n = width < 640 ? 3 : 5;
      lanes = Array.from({ length: n }, (_, i) => (width * (i + 0.5)) / n);
    }
    nextLane = 0;
    const count = width < 640 ? 6 : Math.min(14, lanes.length * 3);
    items = Array.from({ length: count }, (_, i) => {
      const item = makeItem(false);
      item.y = ((i + Math.random() * 0.5) / count) * (height + 200);  // evenly spaced from the start
      return item;
    });
    readColors();
    draw();
  }

  function drawPage(item) {
    const w = item.size;
    const h = item.size * 1.3;
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = item.accent ? colors.accent : colors.line;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(-w / 2, -h / 2, w, h, 5);
    else ctx.rect(-w / 2, -h / 2, w, h);
    ctx.stroke();
    // folded corner and text lines
    ctx.beginPath();
    ctx.moveTo(w / 2 - 10, -h / 2);
    ctx.lineTo(w / 2, -h / 2 + 10);
    ctx.stroke();
    ctx.fillStyle = ctx.strokeStyle;
    for (let i = 0; i < 5; i += 1) {
      const lineWidth = (w - 16) * (i === 4 ? 0.55 : 0.9 - (i % 2) * 0.15);
      ctx.fillRect(-w / 2 + 8, -h / 2 + 14 + i * (h - 24) / 5, lineWidth, 1.6);
    }
  }

  function draw() {
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    items.forEach((item) => {
      ctx.save();
      ctx.globalAlpha = item.alpha;
      ctx.translate(item.x, item.y);
      ctx.rotate(item.angle);
      if (item.page) drawPage(item);
      else {
        ctx.fillStyle = item.accent ? colors.accent : colors.line;
        ctx.font = `600 ${item.size}px "Noto Sans Tamil", system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(item.letter, 0, 0);
      }
      ctx.restore();
    });
  }

  function step(now) {
    frame = requestAnimationFrame(step);
    if (now - last < 33) return;  // about 30 frames a second is plenty for slow drift
    const dt = Math.min((now - last) / 1000, 0.1);
    last = now;
    items.forEach((item, index) => {
      item.y -= item.speed * dt;
      item.x += item.drift * dt;
      item.angle += item.spin * dt;
      if (item.y < -item.size * 2) items[index] = makeItem(false);
    });
    draw();
  }

  function start() {
    stop();
    readColors();
    draw();
    if (calm() || document.hidden) return;
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
    items.forEach((item, index) => {
      item.y -= delta * 0.12;
      if (item.y < -item.size * 2) items[index] = makeItem(false);
      else if (item.y > height + item.size * 2) { const fresh = makeItem(false); fresh.y = -fresh.size; items[index] = fresh; }
    });
    if (!frame) draw();
  }, { passive: true });
  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  if (reducedQuery.addEventListener) reducedQuery.addEventListener('change', start);
  // Theme or calm-mode changes (app.js sets data-theme and the "calm" class on <html>).
  new MutationObserver(start).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
  window.PakkamBackground = { start, stop, isAnimating: () => Boolean(frame) };
  resize();
  start();
})();
