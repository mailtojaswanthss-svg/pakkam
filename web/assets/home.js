/* Pakkam home page: the live demo. Plain JS; all text set with textContent. */
(() => {
  'use strict';

  // An example answer written by hand from the documents, labelled "Example answer" on the
  // page: it is not saved pipeline output. Its source slip is hidden until Jaswanth confirms
  // the page against the PDF (docs/review/hidden-items.md); add slipTitle/slipLine to show it.
  // The Hindi example is hidden for the same reason.
  const DEMOS = {
    tl: {
      lang: 'ta-Latn',
      question: 'PM kisan la varushathuku evlo panam kidaikum',
      read: 'Reading the page',
      answer: 'PM-KISAN la thagudhiyana vivasayigalukku varushathuku Rs.6000 kidaikum, moonu samamaana thavanaiyaa.',
    },
  };

  const win = document.getElementById('demo-window');
  if (!win) return;
  const q = document.getElementById('demo-q');
  const steps = Array.from(document.querySelectorAll('#demo-steps li'));
  const readStep = document.getElementById('demo-read');
  const answer = document.getElementById('demo-a-text');
  const slipTitle = document.getElementById('demo-slip-title');
  const slipLine = document.getElementById('demo-slip-line');
  const slip = win.querySelector('.demo-slip');
  const citeChip = win.querySelector('.chip-cite');
  const replay = document.getElementById('demo-replay');
  const tabs = Array.from(document.querySelectorAll('.demo-tab'));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  let timers = [];
  let current = 'tl';

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  function at(ms, fn) {
    timers.push(setTimeout(fn, ms));
  }

  function fill(demo) {
    q.textContent = demo.question;
    q.lang = demo.lang;
    readStep.textContent = demo.read;
    answer.textContent = demo.answer;
    answer.lang = demo.lang;
    const hasSlip = Boolean(demo.slipTitle);
    slip.hidden = !hasSlip;
    citeChip.hidden = !hasSlip;
    slipTitle.textContent = demo.slipTitle || '';
    slipLine.textContent = demo.slipLine || '';
    if (demo.slipLang) slipLine.lang = demo.slipLang;
  }

  function showFinal() {
    win.classList.add('show-q', 'show-a', 'finished');
    steps.forEach((s) => { s.classList.remove('active'); s.classList.add('done'); });
  }

  function play(key) {
    clearTimers();
    current = key;
    fill(DEMOS[key]);
    win.classList.remove('show-q', 'show-a', 'finished');
    steps.forEach((s) => s.classList.remove('active', 'done'));
    if (reduceMotion.matches) return showFinal();

    at(150, () => win.classList.add('show-q'));
    steps.forEach((step, i) => {
      at(700 + i * 900, () => step.classList.add('active'));
      at(700 + i * 900 + 800, () => { step.classList.remove('active'); step.classList.add('done'); });
    });
    at(700 + steps.length * 900 + 100, () => win.classList.add('show-a'));
    at(700 + steps.length * 900 + 600, () => win.classList.add('finished'));
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.setAttribute('aria-selected', String(t === tab)));
      play(tab.dataset.demo);
    });
  });
  replay.addEventListener('click', () => play(current));

  // Play once when the demo first scrolls into view.
  fill(DEMOS.tl);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        observer.disconnect();
        play(current);
      }
    }, { threshold: 0.4 });
    observer.observe(win);
  } else {
    showFinal();
  }
})();
