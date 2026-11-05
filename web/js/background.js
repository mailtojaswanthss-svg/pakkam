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
    colors = { line: pick('--text-primary', '#cfe7ee'), accent: pick('--raw-purple', '#a970ff') };
  }

  function makeItem(randomY) {
    const page = Math.random() < 0.6;
    const size = page ? 46 + Math.random() * 54 : 18 + Math.random() * 26;
    return {
      page,
      size,
      x: Math.random() * width,
      y: randomY ? Math.random() * height : height + size * 2,
      speed: 6 + Math.random() * 10,        // px per second
      drift: (Math.random() - 0.5) * 6,
      angle: (Math.random() - 0.5) * 0.5,
      spin: (Math.random() - 0.5) * 0.05,
      alpha: 0.05 + Math.random() * 0.07,
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
    const count = Math.round(Math.min(18, Math.max(8, (width * height) / 90000)));
    items = Array.from({ length: count }, () => makeItem(true));
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

  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  if (reducedQuery.addEventListener) reducedQuery.addEventListener('change', start);
  // Theme or calm-mode changes (app.js sets data-theme and the "calm" class on <html>).
  new MutationObserver(start).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
  window.PakkamBackground = { start, stop, isAnimating: () => Boolean(frame) };
  resize();
  start();
})();
