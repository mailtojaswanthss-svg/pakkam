/* Pakkam chat app. Plain JS, no build step. All server text is inserted with textContent. */
(() => {
  'use strict';

  const MIN_CHARS = 3;
  const MAX_CHARS = 500;
  const MAX_VOICE_SECONDS = 30;
  // Give up on an answer after 2 minutes, so the page never waits forever.
  const ASK_TIMEOUT_MS = 120000;
  // Voice errors whose server message is written for the user (bad file, nothing heard, STT down).
  const VOICE_ERRORS = new Set([400, 413, 415, 422, 502, 503]);
  // After this long, say so: "This is taking longer than usual."
  const SLOW_ANSWER_S = 20;
  const TEXT = {
    tooShort: 'Type at least 3 characters.',
    tooLong: 'Keep it under 500 characters.',
    network: 'Pakkam could not reach the server. Check your connection and ask again.',
    server: 'Something went wrong on the server. Ask again in a moment.',
    tooMany: 'Pakkam is getting a lot of questions. Wait a minute, then ask again.',
    timeout: 'Pakkam took too long to answer. Ask again in a moment.',
    offline: 'The live chat is offline right now. The answer server is not connected to this site.',
    waiting: 'Searching the official documents',
    found: (doc, page) => `Found in ${doc}, page ${page}. Writing the answer`,
    slowAnswer: 'This is taking longer than usual.',
    stop: 'Stop',
    talk: {
      idle: 'Tap the mic and ask your question',
      listening: 'Listening… stop talking when you are done',
      thinking: 'Finding the answer in the official documents…',
      speaking: 'Speaking… tap the mic to interrupt',
    },
    talkNoSpeech: 'Pakkam did not hear anything. Tap the mic and try again.',
    talkFailed: 'That did not work. Tap the mic and ask again.',
    talkLangLabel: 'I will speak in',
    call: (number) => `Call ${number}`,
    stopped: 'Stopped. Ask again when you are ready.',
    chip: 'Show the source',
    answeredIn: (ms) => `Answered in ${(ms / 1000).toFixed(1)} s`,
    openPdf: (page) => `Open the official PDF at page ${page}`,
    passage: 'Cited passage',
    voiceQuestion: 'Voice question',
    listen: 'Listen',
    listenLoading: 'Getting audio',
    listenStop: 'Stop',
    listenFailed: 'Pakkam could not read this answer aloud.',
    heard: 'Pakkam heard:',
    recording: (s, max) => `● 0:${String(s).padStart(2, '0')} / 0:${max}`,
    recordingSpoken: (s, max) => `Recording, ${s} of ${max} seconds. Tap the mic again to send.`,
    fewSecondsLeft: (s, max) => `● 0:${String(s).padStart(2, '0')} / 0:${max}, 5 seconds left`,
    micStart: 'Ask by voice',
    micStop: 'Stop and send',
    micBlocked: 'Pakkam could not use the microphone. Allow it in the browser, or upload a recording.',
    micOff: 'Mic is off. Type instead, or turn on the microphone in your browser settings.',
    cancelled: 'Recording cancelled.',
    sendingVoice: 'Sending your voice…',
    slowUpload: 'Slow connection, still sending…',
    voiceFailed: 'Your recording is kept. Tap Send again when the connection is back.',
    schemesFailed: 'The document list could not load. Each answer still links its own source.',
  };
  // Refusal card text. Tamil needs native review; other languages fall back to English.
  const REFUSAL_TEXT = {
    en: { title: 'Not in the documents Pakkam has', official: 'Ask on the official website', schemes: 'What Pakkam can read' },
    ta: { title: 'Pakkam-இடம் உள்ள ஆவணங்களில் இது இல்லை', official: 'அதிகாரப்பூர்வ இணையதளத்தில் கேளுங்கள்', schemes: 'Pakkam படிக்கக்கூடியவை' },
    hi: { title: 'यह Pakkam के दस्तावेज़ों में नहीं है', official: 'आधिकारिक वेबसाइट पर पूछें', schemes: 'Pakkam क्या पढ़ सकता है' },
  };
  // Words around an answer, in its language. Tamil and Hindi need native review.
  const UI = {
    en: {
      followUps: ['Who can get it?', 'How much money?', 'What documents are needed?', 'How do I apply?'],
      more: 'Ask more about this scheme', useful: 'Was this useful?', yes: 'Useful', no: 'Not useful', thanks: 'Thank you.',
      whichScheme: 'Which scheme do you mean?', busy: 'Pakkam cannot write the answer right now. This is what the official documents say:',
      tryAgain: 'Try again', page: 'page', disclaimer: 'Information only. Check the official source.',
      sections: { amount: 'How much', eligibility: 'Who can get it', documents: 'Documents needed', apply: 'How to apply' },
      about: (s) => `What is ${s} and who can get it?`, pickFor: 'Or pick who it is for:',
      audiences: [['Women', 'schemes for women'], ['Students', 'schemes for students'], ['Farmers', 'schemes for farmers'], ['Elderly', 'pension schemes for elderly'], ['Families', 'schemes for poor families'], ['Health', 'schemes for health treatment']],
    },
    'ta-Latn': {
      followUps: ['Yaarukku kidaikum?', 'Evlo panam kidaikum?', 'Enna documents venum?', 'Eppadi apply panradhu?'],
      more: 'Ask more about this scheme', useful: 'Useful-aa irundhadha?', yes: 'Useful', no: 'Not useful', thanks: 'Nandri.',
      whichScheme: 'Endha scheme pathi kekkureenga?', busy: 'Ippo answer ezhudha mudiyala. Official documents la idhu irukku:',
      tryAgain: 'Marubadi try pannunga', page: 'page', disclaimer: 'Information only. Check the official source.',
      sections: { amount: 'Evlo kidaikum', eligibility: 'Yaarukku kidaikum', documents: 'Thevaiyana documents', apply: 'Eppadi apply panradhu' },
      about: (s) => `${s} enna, yaarukku kidaikum?`, pickFor: 'Illa yaarukku-nu choose pannunga:',
      audiences: [['Pengal', 'pengalukku enna scheme irukku'], ['Students', 'students-ku enna scheme irukku'], ['Vivasayigal', 'vivasayigalukku enna scheme irukku'], ['Periyavanga', 'pension scheme enna irukku'], ['Kudumbam', 'ezhai kudumbathukku enna scheme irukku'], ['Health', 'maruthuva scheme enna irukku']],
    },
    ta: {
      followUps: ['யாருக்கு கிடைக்கும்?', 'எவ்வளவு பணம்?', 'என்ன ஆவணங்கள் தேவை?', 'எப்படி விண்ணப்பிப்பது?'],
      more: 'இந்தத் திட்டம் பற்றி மேலும் கேளுங்கள்', useful: 'இது உதவியதா?', yes: 'உதவியது', no: 'உதவவில்லை', thanks: 'நன்றி.',
      whichScheme: 'எந்தத் திட்டத்தைக் குறிப்பிடுகிறீர்கள்?', busy: 'இப்போது பதில் எழுத முடியவில்லை. அதிகாரப்பூர்வ ஆவணங்களில் உள்ளது:',
      tryAgain: 'மீண்டும் முயற்சிக்கவும்', page: 'பக்கம்', disclaimer: 'தகவலுக்கு மட்டும். அதிகாரப்பூர்வ ஆதாரத்தைச் சரிபார்க்கவும்.',
      sections: { amount: 'எவ்வளவு கிடைக்கும்', eligibility: 'யாருக்குக் கிடைக்கும்', documents: 'தேவையான ஆவணங்கள்', apply: 'விண்ணப்பிக்கும் முறை' },
      about: (s) => `${s} என்றால் என்ன, யாருக்குக் கிடைக்கும்?`, pickFor: 'அல்லது யாருக்கு என்று தேர்ந்தெடுங்கள்:',
      audiences: [['பெண்கள்', 'பெண்களுக்கு என்ன திட்டங்கள் உள்ளன?'], ['மாணவர்கள்', 'மாணவர்களுக்கு என்ன திட்டங்கள் உள்ளன?'], ['விவசாயிகள்', 'விவசாயிகளுக்கு என்ன திட்டங்கள் உள்ளன?'], ['முதியோர்', 'முதியோர் ஓய்வூதியத் திட்டங்கள் என்ன?'], ['குடும்பங்கள்', 'ஏழைக் குடும்பங்களுக்கு என்ன திட்டங்கள் உள்ளன?'], ['மருத்துவம்', 'மருத்துவத் திட்டங்கள் என்ன உள்ளன?']],
    },
    hi: {
      followUps: ['किसे मिलता है?', 'कितना पैसा मिलता है?', 'कौन से दस्तावेज़ चाहिए?', 'आवेदन कैसे करें?'],
      more: 'इस योजना के बारे में और पूछें', useful: 'क्या यह उपयोगी था?', yes: 'उपयोगी', no: 'उपयोगी नहीं', thanks: 'धन्यवाद।',
      whichScheme: 'आप किस योजना के बारे में पूछ रहे हैं?', busy: 'अभी उत्तर नहीं लिखा जा सका। आधिकारिक दस्तावेज़ों में यह लिखा है:',
      tryAgain: 'फिर से कोशिश करें', page: 'पेज', disclaimer: 'केवल जानकारी के लिए। आधिकारिक स्रोत देखें।',
      sections: { amount: 'कितना मिलता है', eligibility: 'किसे मिलता है', documents: 'ज़रूरी दस्तावेज़', apply: 'आवेदन कैसे करें' },
      about: (s) => `${s} क्या है और किसे मिलती है?`, pickFor: 'या चुनें कि किसके लिए:',
      audiences: [['महिलाएँ', 'महिलाओं के लिए कौन सी योजनाएँ हैं?'], ['छात्र', 'छात्रों के लिए कौन सी योजनाएँ हैं?'], ['किसान', 'किसानों के लिए कौन सी योजनाएँ हैं?'], ['बुज़ुर्ग', 'बुज़ुर्गों के लिए पेंशन योजनाएँ कौन सी हैं?'], ['परिवार', 'गरीब परिवारों के लिए कौन सी योजनाएँ हैं?'], ['स्वास्थ्य', 'इलाज के लिए कौन सी योजनाएँ हैं?']],
    },
  };
  const LANG_NAME = { en: 'English', ta: 'தமிழ்', hi: 'हिन्दी', 'ta-Latn': 'Tanglish' };
  const LANG_ATTR = new Set(['en', 'ta', 'hi', 'ta-Latn']);
  const AVATAR = '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="3" width="19" height="26" rx="2.5"/><path d="M9 10h11M9 15h11M9 20h7"/><circle cx="24" cy="23" r="6"/></svg>';

  const $ = (selector, root = document) => root.querySelector(selector);
  const app = $('#app');
  const form = $('#ask');
  const input = $('#q');
  const send = $('#send');
  const log = $('#log');
  const thread = $('#thread');
  const welcome = $('#welcome');
  const formMsg = $('#form-msg');
  const panel = $('#sources');
  const sheetScrim = $('#sheet-scrim');
  const panelHeading = $('#sources-h');
  const sourceList = $('#source-list');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  class ServerError extends Error {
    constructor(status, detail = null) {
      super(`HTTP ${status}`);
      this.status = status;
      this.detail = detail;
    }
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }
  const setLang = (node, lang) => { if (LANG_ATTR.has(lang)) node.lang = lang; };
  const safeUrl = (url) => (/^https?:\/\//i.test(url) ? url : null);
  // Rejects with Error('timeout') if the promise has not settled after ms.
  function withTimeout(promise, ms) {
    let timer;
    const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), ms); });
    return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
  }
  const pagesText = (c) => (c.page_start === c.page_end ? `page ${c.page_start}` : `pages ${c.page_start} to ${c.page_end}`);
  const pageShort = (c) => (c.page_start === c.page_end ? `p.\u00a0${c.page_start}` : `pp.\u00a0${c.page_start}-${c.page_end}`);
  // "From: <document> · page N", in the answer's language. Tamil needs native review.
  function sourceLineText(c, lang) {
    const pages = c.page_start === c.page_end ? String(c.page_start) : `${c.page_start}-${c.page_end}`;
    if (lang === 'ta') return `ஆதாரம்: ${c.document} · பக்கம்\u00a0${pages}`;
    return `From: ${c.document} · ${c.page_start === c.page_end ? 'page' : 'pages'}\u00a0${pages}`;
  }
  const scrollToEnd = () => thread.scrollTo({ top: thread.scrollHeight, behavior: reduceMotion.matches ? 'auto' : 'smooth' });

  /* ---------- greeting in four scripts ---------- */
  const greetings = Array.from(document.querySelectorAll('.greeting span'));
  let greetIndex = 0;
  setInterval(() => {
    if (reduceMotion.matches || document.hidden || welcome.hidden) return;
    greetings[greetIndex].classList.remove('on');
    greetIndex = (greetIndex + 1) % greetings.length;
    greetings[greetIndex].classList.add('on');
  }, 2400);

  /* ---------- sidebar drawer (phones) ---------- */
  const scrim = $('#scrim');
  const sideOpen = $('#side-open');
  function setMenu(open) {
    app.classList.toggle('menu-open', open);
    scrim.hidden = !open;
    sideOpen.setAttribute('aria-expanded', String(open));
    if (open) $('#side-close').focus();
    else sideOpen.focus({ preventScroll: true });
  }
  sideOpen.addEventListener('click', () => setMenu(true));

  // "What Pakkam can read": the scheme list lives in the sidebar (a drawer on phones).
  const schemesHeading = $('#schemes-h');
  function showSchemes() {
    if (matchMedia('(max-width: 860px)').matches) setMenu(true);
    schemesHeading.scrollIntoView({ block: 'start', behavior: reduceMotion.matches ? 'auto' : 'smooth' });
    schemesHeading.focus({ preventScroll: true });
  }
  $('#side-close').addEventListener('click', () => setMenu(false));
  scrim.addEventListener('click', () => setMenu(false));

  /* ---------- sources panel ---------- */
  let open = null; // { chip, item }

  function closeSources(returnFocus) {
    if (!open) return;
    panel.hidden = true;
    sheetScrim.hidden = true;
    open.item.querySelectorAll('.sent.lit').forEach((s) => s.classList.remove('lit'));
    open.item.querySelectorAll('[aria-expanded="true"]').forEach((b) => b.setAttribute('aria-expanded', 'false'));
    if (returnFocus) open.chip.focus({ preventScroll: true });
    open = null;
  }

  function sourceCard(c, current) {
    const li = el('li', `source${current ? ' current' : ''}`);
    const head = el('div', 'source-head');
    head.append(el('span', 'source-no', pageShort(c)));
    const meta = el('div');
    meta.append(el('p', 'source-title', `${c.scheme}, ${pagesText(c)}`));
    const lang = LANG_NAME[c.language];
    meta.append(el('p', 'source-doc', lang ? `${c.document} (${lang})` : c.document));
    head.append(meta);
    const passage = el('blockquote', 'source-text', c.excerpt);
    passage.tabIndex = 0;
    passage.setAttribute('aria-label', TEXT.passage);
    setLang(passage, c.language);
    li.append(head, passage);
    const url = safeUrl(c.source_url);
    if (url) {
      const link = el('a', 'source-link', TEXT.openPdf(c.page_start));
      link.href = `${url}#page=${c.page_start}`;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      li.append(link);
    }
    return li;
  }

  function openSources(data, number, opener, item) {
    closeSources(false);
    sourceList.textContent = '';
    let currentCard = null;
    data.citations.forEach((c) => {
      const card = sourceCard(c, c.number === number);
      if (c.number === number) currentCard = card;
      sourceList.append(card);
    });
    if (number != null) {
      item.querySelectorAll('.sent').forEach((s) => {
        if (s.dataset.cites.split(' ').includes(String(number))) s.classList.add('lit');
      });
    }
    opener.setAttribute('aria-expanded', 'true');
    panel.hidden = false;
    sheetScrim.hidden = false;
    open = { chip: opener, item };
    panelHeading.focus({ preventScroll: true });
    if (currentCard) currentCard.scrollIntoView({ block: 'nearest' });
  }

  $('#sources-close').addEventListener('click', () => closeSources(true));
  sheetScrim.addEventListener('click', () => closeSources(true));
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (app.classList.contains('menu-open')) setMenu(false);
    else if (open) closeSources(true);
  });

  /* ---------- rendering ---------- */
  function avatar() {
    const span = el('span', 'avatar');
    span.innerHTML = AVATAR; // static markup, never server data
    return span;
  }

  const uiText = (lang) => UI[lang] || UI.en;
  const SECTION_ORDER = ['amount', 'eligibility', 'documents', 'apply', 'other'];
  const SECTION_ICON = { amount: '₹', eligibility: '👤', documents: '📄', apply: '📝' };

  // Buttons that ask the next natural question about the same scheme. They send the scheme
  // along (follow_up), so "How do I apply?" is read as "how do I apply for <scheme>?".
  // Each chip is first checked against the documents (search only, no LLM) and dropped if
  // they cannot answer it, so a chip never leads to "not in the documents".
  function followUpChips(data, question) {
    const scheme = data.scheme;
    if (!scheme) return null;
    const words = uiText(data.language);
    const row = el('div', 'follow-ups');
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', words.more);
    words.followUps.forEach((text) => {
      const chip = el('button', 'follow-up', text);
      chip.type = 'button';
      setLang(chip, data.language);
      chip.addEventListener('click', () => ask(text, { followUp: { question, scheme } }));
      chip.classList.add('checking');
      row.append(chip);
      fetch('/ask/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, follow_up: { question, scheme } }),
      }).then((res) => (res.ok ? res.json() : null)).then((found) => {
        if (found && found.answerable === false) chip.remove();
        else chip.classList.remove('checking');
        if (!row.children.length) row.remove();
      }).catch(() => chip.classList.remove('checking'));
    });
    return row;
  }

  // Was this answer useful? Only the status, language and timings are sent, never the text.
  function feedbackRow(data) {
    const words = uiText(data.language);
    const row = el('div', 'feedback');
    const label = el('span', 'feedback-label', words.useful);
    setLang(label, data.language);
    row.append(label);
    [['up', '👍', words.yes], ['down', '👎', words.no]].forEach(([thumbs, icon, name]) => {
      const button = el('button', 'feedback-btn', icon);
      button.type = 'button';
      button.setAttribute('aria-label', name);
      button.addEventListener('click', () => {
        row.querySelectorAll('button').forEach((b) => { b.disabled = true; });
        button.classList.add('chosen');
        fetch('/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: data.status || 'SUPPORTED', thumbs, language: data.language, timings_ms: data.timings_ms || {} }),
        }).catch(() => {});
        label.textContent = words.thanks;
      });
      row.append(button);
    });
    return row;
  }

  // "Did you mean A or B?": each scheme is a button that asks the same question about it.
  // A broad question ("a scheme for farmers?") gets the matching schemes as buttons; with no
  // group named, also the groups to narrow by.
  function clarifyCard(data, question) {
    const words = uiText(data.language);
    const discovery = data.path === 'discovery';
    const card = el('div', 'clarify');
    const title = el('p', 'clarify-title', discovery ? data.answer : words.whichScheme);
    setLang(title, data.language);
    card.append(title);
    const actions = el('div', 'clarify-actions');
    data.candidate_schemes.forEach((scheme) => {
      const button = el('button', 'clarify-btn', scheme);
      button.type = 'button';
      button.addEventListener('click', () => (discovery
        ? ask(words.about(scheme), { followUp: { question, scheme } })
        : ask(question, { followUp: { question, scheme }, label: `${question} (${scheme})` })));
      actions.append(button);
    });
    card.append(actions);
    if (discovery && data.candidate_schemes.length > 4) {
      const pick = el('p', 'clarify-title clarify-sub', words.pickFor);
      setLang(pick, data.language);
      const groups = el('div', 'follow-ups');
      words.audiences.forEach(([label, q]) => {
        const chip = el('button', 'follow-up', label);
        chip.type = 'button';
        setLang(chip, data.language);
        chip.addEventListener('click', () => ask(q));
        groups.append(chip);
      });
      card.append(pick, groups);
    }
    return card;
  }

  // The answer writer is busy or down: show what the documents say instead of a bare error.
  function busyCard(data, question) {
    const words = uiText(data.language);
    const card = el('div', 'busy');
    const title = el('p', 'busy-title', words.busy);
    setLang(title, data.language);
    card.append(title);
    const list = el('ul', 'busy-passages');
    data.passages.forEach((p) => {
      const li = el('li');
      const head = el('p', 'busy-doc', `${p.document} · ${words.page} ${p.page}`);
      const text = el('blockquote', 'busy-text', p.text.length > 280 ? `${p.text.slice(0, 277)}…` : p.text);
      li.append(head, text);
      const url = safeUrl(p.source_url);
      if (url) {
        const link = el('a', 'source-link', TEXT.openPdf(p.page));
        link.href = `${url}#page=${p.page}`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        li.append(link);
      }
      list.append(li);
    });
    card.append(list);
    const again = el('button', 'refusal-schemes', words.tryAgain);
    again.type = 'button';
    again.addEventListener('click', () => ask(question));
    card.append(again);
    return card;
  }

  function renderAnswer(data, question) {
    const item = el('li', 'msg a');
    const body = el('div', 'a-body');
    setLang(body, data.language);
    const words = uiText(data.language);

    if (data.confirmation_text) {
      const confirm = el('p', 'confirm', data.confirmation_text);
      setLang(confirm, data.language);
      body.append(confirm);
    }

    const clarify = data.status === 'needs_clarification' && data.candidate_schemes && data.candidate_schemes.length;
    const busy = data.refused && data.passages && data.passages.length;
    const refused = !clarify && (data.refused || data.sentences.length === 0);
    if (clarify) {
      body.append(clarifyCard(data, question));
    } else if (busy) {
      body.append(busyCard(data, question));
    } else if (refused) {
      body.append(refusalCard(data));
    } else {
      const byNumber = new Map(data.citations.map((c) => [c.number, c]));
      const addSentence = (para, sentence) => {
        const span = el('span', 'sent', sentence.text);
        span.dataset.cites = sentence.citations.join(' ');
        para.append(span);
        sentence.citations.forEach((n) => {
          const c = byNumber.get(n);
          if (!c) return;
          const chip = el('button', 'chip', pageShort(c));
          chip.type = 'button';
          chip.title = TEXT.chip;
          chip.setAttribute('aria-label', `${TEXT.chip}: ${c.scheme}, ${pagesText(c)}`);
          chip.setAttribute('aria-expanded', 'false');
          chip.setAttribute('aria-controls', 'sources');
          chip.addEventListener('click', () => {
            if (open && open.chip === chip) closeSources(true);
            else openSources(data, n, chip, item);
          });
          para.append(chip);
        });
        para.append(' ');
      };
      // Grouped under "How much", "Who can get it", ... when the answer covers those parts.
      const titled = data.sentences.some((s) => s.section && s.section !== 'other');
      if (titled) {
        const groups = el('div', 'a-sections');
        SECTION_ORDER.forEach((section) => {
          const inSection = data.sentences.filter((s) => (s.section || 'other') === section);
          if (!inSection.length) return;
          const block = el('section', `a-section a-section-${section}`);
          if (section !== 'other') {
            const head = el('h3', 'a-section-h', words.sections[section]);
            head.prepend(el('span', 'a-section-icon', SECTION_ICON[section]));
            block.append(head);
          }
          const para = el('p', 'sentences');
          inSection.forEach((sentence) => addSentence(para, sentence));
          block.append(para);
          groups.append(block);
        });
        body.append(groups);
      } else {
        const para = el('p', 'sentences');
        data.sentences.forEach((sentence) => addSentence(para, sentence));
        body.append(para);
      }

      // The proof, visible without a tap: one line per cited document page.
      const cited = new Set(data.sentences.flatMap((sentence) => sentence.citations));
      const lines = el('ul', 'source-lines');
      data.citations.filter((c) => cited.has(c.number)).forEach((c) => {
        const line = el('button', 'source-line', sourceLineText(c, data.language));
        line.type = 'button';
        setLang(line, data.language);
        line.setAttribute('aria-expanded', 'false');
        line.setAttribute('aria-controls', 'sources');
        line.addEventListener('click', () => {
          if (open && open.chip === line) closeSources(true);
          else openSources(data, c.number, line, item);
        });
        const li = el('li');
        li.append(line);
        lines.append(li);
      });
      if (lines.children.length) body.append(lines);
    }

    const meta = el('div', 'a-meta');
    if (!clarify && !busy) meta.append(listenButton(data));
    if (data.latency_ms && !refused && !clarify) meta.append(el('span', 'a-time', TEXT.answeredIn(data.latency_ms)));
    if (!refused && !clarify) meta.append(feedbackRow(data));
    body.append(meta);

    if (!refused && !clarify) {
      const more = followUpChips(data, question);
      if (more) body.append(more);
    }
    const disclaimer = el('p', 'disclaimer', data.disclaimer || words.disclaimer);
    setLang(disclaimer, data.language);
    body.append(disclaimer);

    item.append(avatar(), body);
    return item;
  }

  function refusalCard(data) {
    const words = REFUSAL_TEXT[data.language] || REFUSAL_TEXT.en;
    const card = el('div', 'refusal');
    if (data.refusal_reason !== 'service_unavailable') {
      const title = el('p', 'refusal-title', words.title);
      setLang(title, data.language);
      card.append(title);
    }
    card.append(el('p', 'refusal-text', data.answer));
    const actions = el('div', 'refusal-actions');
    const helpline = data.contact && data.contact.helpline;
    if (helpline) {
      const call = el('a', 'refusal-link refusal-call', TEXT.call(helpline));
      call.href = `tel:${helpline.replace(/[^\d+]/g, '')}`;
      actions.append(call);
    }
    const url = data.contact ? safeUrl(data.contact.website) : null;
    if (url) {
      const link = el('a', 'refusal-link', words.official);
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.append(el('span', 'refusal-host', new URL(url).host));
      actions.append(link);
    }
    if (data.refusal_reason !== 'service_unavailable') {
      const schemes = el('button', 'refusal-schemes', words.schemes);
      schemes.type = 'button';
      schemes.addEventListener('click', showSchemes);
      actions.append(schemes);
    }
    if (actions.children.length) card.append(actions);
    return card;
  }

  /* ---------- spoken answers (Sentence-by-sentence queued playback via Gnani Timbre) ---------- */
  let playing = null; // { audio, button, abortCtrl, urls: [] }

  function stopPlaying() {
    if (!playing) return;
    if (playing.abortCtrl) {
      playing.abortCtrl.abort();
    }
    if (playing.audio) {
      playing.audio.pause();
    }
    if (playing.urls) {
      playing.urls.forEach((u) => URL.revokeObjectURL(u));
    }
    playing.button.textContent = TEXT.listen;
    playing.button.setAttribute('aria-pressed', 'false');
    playing = null;
  }

  function getSentencesToSpeak(data) {
    const first = data.confirmation_text ? [data.confirmation_text] : [];
    if (data.refused || !data.sentences || data.sentences.length === 0) {
      return [...first, data.answer];
    }
    return [...first, ...data.sentences.map((s) => s.text.trim()).filter(Boolean)];
  }

  // Called once when an answer has been read out to the end (not when stopped).
  let onSpokenEnd = null;

  async function fetchSentenceAudio(text, language, signal) {
    const response = await fetch('/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
      signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(typeof body.detail === 'string' ? body.detail : TEXT.listenFailed);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }

  // `quiet`: started automatically after a voice question, so a failure (e.g. spoken answers
  // not set up on this server) just leaves the Listen button, with no error message.
  async function listen(data, button, quiet = false) {
    if (playing && playing.button === button) {
      stopPlaying();
      return;
    }
    stopPlaying();
    button.disabled = true;
    button.textContent = TEXT.listenLoading;

    const abortCtrl = new AbortController();
    const urls = [];
    const state = { audio: null, button, abortCtrl, urls, failed: false };
    playing = state;

    const sentences = getSentencesToSpeak(data);
    if (sentences.length === 0) {
      stopPlaying();
      button.disabled = false;
      return;
    }

    try {
      // Pipelining: fetch sentence 1 first to minimize Time-to-First-Audio (TTFA)
      const firstUrl = await fetchSentenceAudio(sentences[0], data.language, abortCtrl.signal);
      urls.push(firstUrl);

      if (playing !== state) return; // stopped while downloading

      button.disabled = false;
      button.textContent = TEXT.listenStop;
      button.setAttribute('aria-pressed', 'true');

      // Play queue sequentially
      let currentIdx = 0;
      const playNext = async () => {
        if (playing !== state || currentIdx >= sentences.length) {
          stopPlaying();
          return;
        }

        const url = urls[currentIdx];
        const audio = new Audio(url);
        state.audio = audio;

        // Prefetch next sentence while current sentence is playing
        if (currentIdx + 1 < sentences.length && urls.length <= currentIdx + 1) {
          fetchSentenceAudio(sentences[currentIdx + 1], data.language, abortCtrl.signal)
            .then((nextUrl) => {
              if (playing === state) urls.push(nextUrl);
            })
            .catch(() => { state.failed = true; });
        }

        audio.addEventListener('ended', async () => {
          currentIdx++;
          if (currentIdx < sentences.length) {
            // Wait for next sentence if it is still fetching
            // Wait for the next sentence, unless its audio could not be fetched.
            while (urls.length <= currentIdx && playing === state && !state.failed) {
              await new Promise((r) => setTimeout(r, 100));
            }
            if (urls.length <= currentIdx) {
              stopPlaying();
              return;
            }
            playNext();
          } else {
            stopPlaying();
            const next = onSpokenEnd;
            onSpokenEnd = null;
            if (next) next();
          }
        });

        await audio.play();
      };

      await playNext();
    } catch (error) {
      if (error.name === 'AbortError') {
        return; // Normal cancellation
      }
      stopPlaying();
      button.textContent = TEXT.listen;
      if (!quiet) showFormMsg(error instanceof TypeError ? TEXT.network : error.message);
    } finally {
      if (playing === state && !state.audio) {
        button.disabled = false;
      }
    }
  }

  function listenButton(data) {
    const button = el('button', 'listen-btn', TEXT.listen);
    button.type = 'button';
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => listen(data, button));
    return button;
  }

  function assistantItem(className, content) {
    const item = el('li', `msg a ${className}`);
    const body = el('div', 'a-body');
    content.forEach((node) => body.append(node));
    item.append(avatar(), body);
    return item;
  }

  /* ---------- asking ---------- */
  let busy = false;
  let current = null; // { controller } for the turn in progress, so it can be stopped
  // The last answered scheme. A short follow-up ("how do I apply?") is sent with it so the
  // server reads it as a question about that scheme. Kept only in this page, never stored.
  let lastTurn = null; // { question, scheme }
  const showFormMsg = (text) => { formMsg.textContent = text; };

  function autosize() {
    input.style.height = 'auto';
    input.style.height = `${input.scrollHeight}px`;
  }

  // Short questions that only make sense after the previous answer, in the four languages.
  const FOLLOW_UP_CUE = /\b(apply|eligib|documents?|how much|amount|when|where|who|evlo|evvalavu|eppadi|eppo|yaar|enna|venum|kaise|kitna|kab|kaun)\b|விண்ணப்ப|ஆவண|எவ்வளவு|யார்|எப்படி|எப்போது|आवेदन|दस्तावेज़|कितना|कौन|कैसे|कब/i;
  function followUpFor(question) {
    if (!lastTurn) return null;
    const words = question.trim().split(/\s+/).length;
    return words <= 6 && FOLLOW_UP_CUE.test(question) ? lastTurn : null;
  }

  // Show the pages a question matched while its answer is still being written.
  function previewSources(question, followUp, view, signal) {
    fetch('/ask/sources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, follow_up: followUp }),
      signal,
    }).then(async (res) => {
      if (!res.ok) return;
      const found = await res.json();
      if (!found.passages || !found.passages.length || !view.pending.isConnected) return;
      const first = found.passages[0];
      view.stage = TEXT.found(first.document, first.page);
      view.update();
      view.preview.textContent = '';
      view.preview.append(el('blockquote', 'source-preview-snippet', first.text.length > 160 ? `${first.text.slice(0, 157)}…` : first.text));
      view.preview.hidden = false;
      scrollToEnd();
    }).catch(() => {});
  }

  function stopCurrent() {
    if (current) current.controller.abort();
  }

  // One question and answer turn. `request(bubble, hooks)` returns the fetch promise; `label`
  // shows in the question bubble until it is replaced (for voice, by what Pakkam heard).
  // Resolves to { data, item } on an answer, { error } on a failure, {} when stopped.
  async function runTurn(label, request, question = null, followUp = null) {
    if (busy) return {};
    showFormMsg('');
    busy = true;
    send.disabled = true;
    form.setAttribute('aria-busy', 'true');
    welcome.hidden = true;
    closeSources(false);
    const controller = new AbortController();
    current = { controller };

    const questionItem = el('li', 'msg q');
    const bubble = el('p', null, label);
    questionItem.append(bubble);
    const waitMsg = el('p', 'wait');
    const waitBar = el('span', 'wait-bar');
    const preview = el('div', 'source-preview-box');
    preview.hidden = true;
    const stop = el('button', 'stop-btn', TEXT.stop);
    stop.type = 'button';
    stop.addEventListener('click', stopCurrent);
    const pending = assistantItem('pending', [waitMsg, waitBar, preview, stop]);
    log.append(questionItem, pending);
    scrollToEnd();

    // Real progress only: what was found, and how long it has taken. No pretend steps.
    const started = Date.now();
    const view = {
      pending,
      preview,
      stage: TEXT.waiting,
      update() {
        const seconds = Math.floor((Date.now() - started) / 1000);
        const slow = seconds >= SLOW_ANSWER_S ? ` ${TEXT.slowAnswer}` : '';
        waitMsg.textContent = seconds >= 2 ? `${this.stage} · ${seconds} s${slow}` : this.stage;
      },
    };
    view.update();
    const ticker = setInterval(() => view.update(), 1000);
    const hooks = {
      signal: controller.signal,
      preview: (text, fu) => previewSources(text, fu, view, controller.signal),
    };
    if (question) hooks.preview(question, followUp);

    try {
      let response;
      try {
        response = await withTimeout(request(bubble, hooks), ASK_TIMEOUT_MS);
      } catch (error) {
        if (error.name === 'AbortError') throw error;
        throw new Error(error.message === 'timeout' ? 'timeout' : 'network');
      }
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new ServerError(response.status, typeof body.detail === 'string' ? body.detail : null);
      }
      const data = await response.json();
      if (data.transcript) {
        bubble.textContent = '';
        bubble.append(el('span', 'heard', TEXT.heard), data.transcript);
      }
      setLang(bubble, data.language);
      const asked = question || hooks.asked || data.transcript || bubble.textContent;
      const item = renderAnswer(data, asked);
      pending.replaceWith(item);
      if (!data.refused && data.scheme) {
        lastTurn = { question: asked, scheme: data.scheme };
      }
      return { data, item };
    } catch (error) {
      if (error.name === 'AbortError') {
        pending.replaceWith(assistantItem('', [el('p', 'wait', TEXT.stopped)]));
        return {};
      }
      let message = error.message === 'timeout' ? TEXT.timeout : TEXT.network;
      if (error instanceof ServerError) {
        // 404/405: a static host (e.g. Vercel) with no answer server behind it; 502/504: the
        // host is there but the answer server behind it is not reachable.
        // 429: the server says whether to wait a minute or come back tomorrow.
        if (error.status === 429) message = error.detail || TEXT.tooMany;
        // 520-530: Cloudflare's tunnel is up on their side but the laptop behind it is not.
        else if (([404, 405, 502, 504].includes(error.status) || (error.status >= 520 && error.status <= 530)) && !error.detail) message = TEXT.offline;
        else if (error.detail && VOICE_ERRORS.has(error.status)) message = error.detail;
        else message = TEXT.server;
      }
      pending.replaceWith(assistantItem('', [el('p', 'error-msg', message)]));
      return { error };
    } finally {
      clearInterval(ticker);
      current = null;
      busy = false;
      send.disabled = false;
      form.removeAttribute('aria-busy');
      scrollToEnd();
      input.focus({ preventScroll: true });
    }
  }

  const askBody = (question, followUp, voiceMode = false) => JSON.stringify({
    question,
    ...(voiceMode ? { voice_mode: true } : {}),
    ...(followUp ? { follow_up: followUp } : {}),
  });

  // `options.followUp` comes from a follow-up chip or a "did you mean" button; a typed short
  // follow-up gets the previous scheme automatically (followUpFor).
  function ask(raw, options = {}) {
    const question = raw.trim();
    if (question.length < MIN_CHARS) return showFormMsg(TEXT.tooShort);
    if (question.length > MAX_CHARS) return showFormMsg(TEXT.tooLong);
    if (busy) return;
    input.value = '';
    autosize();
    stopPlaying();
    const followUp = options.followUp || followUpFor(question);
    return runTurn(options.label || question, (bubble, hooks) => fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: askBody(question, followUp),
      signal: hooks.signal,
    }), question, followUp);
  }

  /* ---------- asking by voice (Gnani speech to text on the server) ---------- */
  const SLOW_UPLOAD_MS = 5000;
  const WARN_AT_SECONDS = MAX_VOICE_SECONDS - 5;
  const ANNOUNCE_EVERY_SECONDS = 10;
  const mic = $('#mic');
  const upload = $('#upload');
  const voiceStatus = $('#voice-status');
  const voiceAnnounce = $('#voice-announce');
  const cancelButton = $('#voice-cancel');
  const retryButton = $('#voice-retry');
  const typeInstead = $('#type-instead');
  let recording = null; // { recorder, timer }
  let lastClip = null; // { audio, filename, language }, kept until it is sent without a network error

  const voiceLanguage = () => $('input[name="voice-lang"]:checked').value;

  // The voice language sits folded next to the mic: "Voice: தமிழ்". It only tells speech
  // recognition what to listen for; typed questions are detected by themselves.
  const voicePick = $('#voice-lang-pick');
  function showVoiceLang() {
    const checked = $('input[name="voice-lang"]:checked');
    const now = $('#voice-lang-now');
    now.textContent = checked.nextElementSibling.textContent.replace(/\s*\(.*\)$/, '');
    now.lang = checked.value;
  }
  document.querySelectorAll('input[name="voice-lang"]').forEach((radio) => {
    radio.addEventListener('change', () => { showVoiceLang(); voicePick.open = false; });
  });
  showVoiceLang();

  function setVoiceStatus(text, spoken = text) {
    voiceStatus.textContent = text;
    if (spoken !== null) voiceAnnounce.textContent = spoken;
  }

  // Worth sending the same clip again: the request never arrived, or the server failed.
  // Not for 4xx answers like "could not hear", where speaking again is the fix.
  const canRetry = (error) => !(error instanceof ServerError) || error.status >= 500;

  // Two steps, so "Pakkam heard: ..." shows as soon as speech to text is done, while the
  // answer is still being written: /transcribe (1 Gnani call), then /ask with that text, in
  // voice mode (a short answer that reads well aloud), and the answer is then spoken.
  // Once the transcript is known, Send again resends only the text, with no new Gnani call.
  async function askVoice(clip) {
    retryButton.hidden = true;
    lastClip = clip;
    stopPlaying();
    setVoiceStatus(TEXT.sendingVoice);
    const slow = setTimeout(() => setVoiceStatus(TEXT.slowUpload), SLOW_UPLOAD_MS);
    const result = await runTurn(TEXT.voiceQuestion, async (bubble, hooks) => {
      if (!clip.transcript) {
        const body = new FormData();
        body.append('audio', clip.audio, clip.filename);
        body.append('language', clip.language);
        const heard = await fetch('/transcribe', { method: 'POST', body, signal: hooks.signal });
        if (!heard.ok) return heard; // runTurn shows the server's message
        clip.transcript = (await heard.json()).transcript;
      }
      clearTimeout(slow);
      setVoiceStatus('');
      bubble.textContent = '';
      bubble.append(el('span', 'heard', TEXT.heard), clip.transcript);
      hooks.asked = clip.transcript;
      const followUp = followUpFor(clip.transcript);
      hooks.preview(clip.transcript, followUp);
      return fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: askBody(clip.transcript, followUp, true),
        signal: hooks.signal,
      });
    });
    clearTimeout(slow);
    if (result.error && canRetry(result.error)) {
      setVoiceStatus(TEXT.voiceFailed);
      retryButton.hidden = false;
      return result;
    }
    setVoiceStatus('');
    lastClip = null;
    // Asked by voice, answered by voice: read the answer out. Listen stays as Stop/replay.
    const button = result.item && result.item.querySelector('.listen-btn');
    if (button) listen(result.data, button, true);
    return { ...result, transcript: clip.transcript };
  }

  const newClip = (audio, filename) => ({ audio, filename, language: voiceLanguage(), transcript: null });

  function showRecording(seconds) {
    const text = seconds >= WARN_AT_SECONDS
      ? TEXT.fewSecondsLeft(seconds, MAX_VOICE_SECONDS)
      : TEXT.recording(seconds, MAX_VOICE_SECONDS);
    // Screen readers hear the time every 10 seconds and the warning once, not every tick.
    let spoken = null;
    if (seconds === WARN_AT_SECONDS) spoken = text;
    else if (seconds % ANNOUNCE_EVERY_SECONDS === 0) spoken = TEXT.recordingSpoken(seconds, MAX_VOICE_SECONDS);
    setVoiceStatus(text, spoken);
  }

  function endRecording() {
    const { recorder, timer } = recording;
    recording = null;
    clearInterval(timer);
    mic.setAttribute('aria-pressed', 'false');
    mic.setAttribute('aria-label', TEXT.micStart);
    mic.style.setProperty('--level', '0');
    cancelButton.hidden = true;
    return recorder;
  }

  async function stopRecording() {
    if (!recording) return;
    const wav = await endRecording().stop();
    askVoice(newClip(wav, 'question.wav'));
  }

  function cancelRecording() {
    if (!recording) return;
    endRecording().cancel();
    setVoiceStatus(TEXT.cancelled);
    mic.focus();
  }

  async function micIsDenied() {
    try {
      const status = await navigator.permissions.query({ name: 'microphone' });
      return status.state === 'denied';
    } catch {
      return false; // Firefox and older Safari cannot query the microphone permission.
    }
  }

  function showMicOff() {
    mic.classList.add('mic-off');
    setVoiceStatus(TEXT.micOff);
    typeInstead.hidden = false;
  }

  async function startRecording() {
    if (busy) return;
    showFormMsg('');
    stopPlaying();
    typeInstead.hidden = true;
    retryButton.hidden = true;
    try {
      const recorder = await window.PakkamRecorder.start({
        onLevel: (level) => mic.style.setProperty('--level', level.toFixed(2)),
        onSilence: (heard) => { if (heard) stopRecording(); },
      });
      const startedAt = Date.now();
      let shown = -1;
      const timer = setInterval(() => {
        const seconds = Math.floor((Date.now() - startedAt) / 1000);
        if (seconds >= MAX_VOICE_SECONDS) stopRecording();
        else if (seconds !== shown) showRecording((shown = seconds));
      }, 250);
      recording = { recorder, timer };
      mic.classList.remove('mic-off');
      mic.setAttribute('aria-pressed', 'true');
      mic.setAttribute('aria-label', TEXT.micStop);
      cancelButton.hidden = false;
      showRecording((shown = 0));
    } catch {
      if (await micIsDenied()) showMicOff();
      else showFormMsg(TEXT.micBlocked);
    }
  }

  if (window.PakkamRecorder && window.PakkamRecorder.supported) {
    mic.addEventListener('click', () => (recording ? stopRecording() : startRecording()));
    micIsDenied().then((denied) => { if (denied) showMicOff(); });
  } else {
    mic.hidden = true;
  }
  cancelButton.addEventListener('click', cancelRecording);
  retryButton.addEventListener('click', () => {
    if (lastClip && !busy) askVoice(lastClip);
  });
  typeInstead.addEventListener('click', () => {
    typeInstead.hidden = true;
    setVoiceStatus('');
    input.focus();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && recording) cancelRecording();
  });
  upload.addEventListener('change', () => {
    const file = upload.files[0];
    upload.value = '';
    if (file) askVoice(newClip(file, file.name));
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    ask(input.value);
  });
  input.addEventListener('keydown', (event) => {
    // Enter sends, Shift+Enter adds a line. Never send mid-composition (Tamil/Hindi IMEs).
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  input.addEventListener('input', () => {
    autosize();
    if (formMsg.textContent) showFormMsg('');
  });
  document.querySelectorAll('[data-q]').forEach((button) => {
    button.addEventListener('click', () => ask($('.suggest-q', button).textContent));
  });

  /* ---------- talk mode: a whole conversation by voice ---------- */
  // Speak, hear the answer, and Pakkam listens again for a follow-up: no reading or typing.
  // The chat log underneath keeps the written answers and their sources.
  const talk = $('#talk');
  const talkMic = $('#talk-mic');
  const talkState = $('#talk-state');
  const talkRing = $('#talk-ring');
  const talkHeard = $('#talk-heard');
  const talkAnswer = $('#talk-answer');
  const talkActions = $('#talk-actions');
  const talkLang = $('#talk-lang');
  const FOLLOW_UP_LISTEN_MS = 6000;
  let talkOn = false;
  let talkPhase = 'idle';
  let talkRec = null; // { recorder, cap }

  function setTalk(phase, text) {
    talkPhase = phase;
    talk.dataset.phase = phase;
    talkState.textContent = text || TEXT.talk[phase];
  }

  function openTalk() {
    if (!window.PakkamRecorder || !window.PakkamRecorder.supported) return showFormMsg(TEXT.micBlocked);
    talkOn = true;
    talk.hidden = false;
    renderTalkLangs();
    setTalk('idle');
    talkMic.focus();
  }

  // The same four choices as under the question box, so the language can change mid-talk.
  function renderTalkLangs() {
    talkLang.textContent = '';
    talkLang.append(el('span', null, TEXT.talkLangLabel));
    document.querySelectorAll('input[name="voice-lang"]').forEach((radio) => {
      const button = el('button', 'talk-lang-btn', radio.nextElementSibling.textContent.replace(/\s*\(.*\)$/, ''));
      button.type = 'button';
      button.setAttribute('aria-pressed', String(radio.checked));
      button.addEventListener('click', () => { radio.checked = true; renderTalkLangs(); showVoiceLang(); });
      talkLang.append(button);
    });
  }

  function closeTalk() {
    talkOn = false;
    onSpokenEnd = null;
    stopTalkRecording(true);
    stopPlaying();
    talk.hidden = true;
    mic.focus({ preventScroll: true });
  }

  function stopTalkRecording(cancel, message) {
    if (!talkRec) return null;
    clearTimeout(talkRec.cap);
    const { recorder } = talkRec;
    talkRec = null;
    talkRing.style.setProperty('--level', '0');
    if (cancel) {
      recorder.cancel();
      if (talkOn) setTalk('idle', message);
      return null;
    }
    return recorder;
  }

  // `followUp`: started by itself after an answer, so give up quietly if nobody speaks.
  async function talkListen(followUp = false) {
    if (busy || talkRec || !talkOn) return;
    onSpokenEnd = null;
    stopPlaying();
    try {
      const recorder = await window.PakkamRecorder.start({
        onLevel: (level) => talkRing.style.setProperty('--level', level.toFixed(2)),
        onSilence: (heard) => {
          if (heard) finishTalkRecording();
          else stopTalkRecording(true, followUp ? TEXT.talk.idle : TEXT.talkNoSpeech);
        },
        noSpeechMs: followUp ? FOLLOW_UP_LISTEN_MS : 10000,
      });
      talkRec = { recorder, cap: setTimeout(finishTalkRecording, MAX_VOICE_SECONDS * 1000) };
      setTalk('listening');
    } catch {
      setTalk('idle', TEXT.micBlocked);
    }
  }

  function showTalkResult(result, question) {
    const data = result.data;
    talkHeard.textContent = question ? `${TEXT.heard} ${question}` : '';
    const spoken = getSentencesToSpeak(data).join(' ').replace(/\s*\[\d+\]/g, '');
    talkAnswer.textContent = spoken;
    setLang(talkAnswer, data.language);
    talkActions.textContent = '';
    const scheme = data.citations && data.citations.length ? data.citations[0].scheme : null;
    if (scheme && !data.refused) {
      uiText(data.language).followUps.forEach((text) => {
        const chip = el('button', 'follow-up', text);
        chip.type = 'button';
        setLang(chip, data.language);
        chip.addEventListener('click', () => talkAsk(text, { question: question || text, scheme }));
        talkActions.append(chip);
      });
    }
    // Read out (askVoice/talkAsk started it); then listen for a follow-up by itself.
    if (playing) {
      setTalk('speaking');
      onSpokenEnd = () => { if (talkOn) talkListen(true); };
    } else {
      setTalk('idle');
    }
  }

  async function finishTalkRecording() {
    const recorder = stopTalkRecording(false);
    if (!recorder) return;
    setTalk('thinking');
    talkHeard.textContent = '';
    talkAnswer.textContent = '';
    talkActions.textContent = '';
    const result = await askVoice(newClip(await recorder.stop(), 'question.wav'));
    if (!talkOn) return;
    if (!result || !result.data) return setTalk('idle', TEXT.talkFailed);
    showTalkResult(result, result.transcript);
  }

  // A follow-up chip in talk mode: ask it, and read the answer out.
  async function talkAsk(text, followUp) {
    if (busy) return;
    stopPlaying();
    setTalk('thinking');
    const result = await ask(text, { followUp });
    if (!talkOn || !result || !result.data) return setTalk('idle', TEXT.talkFailed);
    const button = result.item && result.item.querySelector('.listen-btn');
    if (button) listen(result.data, button, true);
    showTalkResult(result, text);
  }

  talkMic.addEventListener('click', () => {
    if (talkPhase === 'listening') finishTalkRecording();
    else if (talkPhase !== 'thinking') talkListen(); // also interrupts Pakkam while it speaks
  });
  $('#talk-close').addEventListener('click', closeTalk);
  document.querySelectorAll('[data-talk]').forEach((button) => button.addEventListener('click', openTalk));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && talkOn) closeTalk();
  });

  /* ---------- new conversation ---------- */
  document.querySelectorAll('[data-new-chat]').forEach((button) => {
    button.addEventListener('click', () => {
      stopCurrent();
      lastTurn = null;
      stopPlaying();
      cancelRecording();
      lastClip = null;
      retryButton.hidden = true;
      setVoiceStatus('');
      closeSources(false);
      log.textContent = '';
      welcome.hidden = false;
      showFormMsg('');
      input.value = '';
      autosize();
      if (app.classList.contains('menu-open')) setMenu(false);
      thread.scrollTo({ top: 0 });
      input.focus();
    });
  });

  /* ---------- the schemes list ---------- */
  async function loadSchemes() {
    const list = $('#scheme-list');
    try {
      const response = await fetch('/sources');
      if (!response.ok) throw new Error(String(response.status));
      const docs = await response.json();
      const schemes = new Map();
      docs.forEach((doc) => {
        if (!schemes.has(doc.scheme)) schemes.set(doc.scheme, new Set());
        schemes.get(doc.scheme).add(LANG_NAME[doc.language] || doc.language);
      });
      list.textContent = '';
      schemes.forEach((langs, scheme) => {
        const li = el('li');
        const button = el('button', 'scheme-ask', scheme);
        button.type = 'button';
        button.title = `Ask about ${scheme}`;
        button.addEventListener('click', () => {
          if (app.classList.contains('menu-open')) setMenu(false);
          ask(`What is ${scheme} and who can get it?`);
        });
        li.append(button, el('span', 'scheme-docs', Array.from(langs).join(', ')));
        list.append(li);
      });
    } catch {
      list.textContent = '';
      list.append(el('li', 'scheme-note', TEXT.schemesFailed));
    }
  }
  loadSchemes();

  // chat/?q=... (from the home page) asks that question straight away.
  const fromLink = new URLSearchParams(location.search).get('q');
  if (fromLink) {
    history.replaceState(null, '', location.pathname);
    ask(fromLink);
  }
})();
