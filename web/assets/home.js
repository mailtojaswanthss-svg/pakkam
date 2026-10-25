/* Pakkam home page: the live demo. Plain JS; all text set with textContent. */
(() => {
  'use strict';

  // Example answers built from the real documents (G.O. p9, e-KYC note p1, PM-KISAN p10),
  // chosen where the indexed text is clean so the real pipeline can give the same answer.
  const DEMOS = {
    ta: {
      lang: 'ta',
      question: 'மகளிர் உரிமைத் தொகை ஆண்டுக்கு எவ்வளவு?',
      read: 'Reading page 9 of G.O.(Ms) No.15',
      answer: 'கலைஞர் மகளிர் உரிமைத் திட்டத்தில் ஆண்டுக்கு 12 ஆயிரம் ரூபாய் உரிமைத் தொகை வழங்கப்படும்.',
      slipTitle: 'Kalaignar Magalir Urimai Thittam, page 9',
      slipLine: 'ஆண்டுக்கு 12 ஆயிரம் ரூபாய் உரிமைத்தொகை…',
      slipLang: 'ta',
    },
    hi: {
      lang: 'hi',
      question: 'पीएम किसान के लिए ई-केवाईसी कैसे करें?',
      read: 'Reading page 1 of the e-KYC note',
      answer: 'ई-केवाईसी ओटीपी से पीएम-किसान पोर्टल या मोबाइल ऐप पर हो सकता है, या कॉमन सर्विस सेंटर पर बायोमेट्रिक से।',
      slipTitle: 'PM-KISAN, page 1',
      slipLine: '(i) ओटीपी आधारित ई-केवाईसी (पीएम-किसान पोर्टल और मोबाइल ऐप पर उपलब्ध)…',
      slipLang: 'hi',
    },
    tl: {
      lang: 'ta-Latn',
      question: 'PM kisan la varushathuku evlo panam kidaikum',
      read: 'Reading page 10 of the PM-KISAN guidelines',
      answer: 'PM-KISAN la thagudhiyana vivasayigalukku varushathuku Rs.6000 kidaikum, moonu thavanaiyaa Rs.2000 aaga.',
      slipTitle: 'PM-KISAN, page 10',
      slipLine: 'The financial benefit of Rs.6000/- per year is to be released to the eligible farmers in three installments of Rs.2000/- each…',
      slipLang: 'en',
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
  const replay = document.getElementById('demo-replay');
  const tabs = Array.from(document.querySelectorAll('.demo-tab'));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  let timers = [];
  let current = 'ta';

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
    slipTitle.textContent = demo.slipTitle;
    slipLine.textContent = demo.slipLine;
    slipLine.lang = demo.slipLang;
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
  fill(DEMOS.ta);
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
