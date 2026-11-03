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
  // Shown while answers come from the slower backup server (assets/backup.js).
  window.addEventListener('pakkam-backup', (event) => {
    let pill = document.getElementById('backup-note');
    if (!pill) {
      pill = document.createElement('p');
      pill.id = 'backup-note';
      pill.className = 'backup-note';
      pill.setAttribute('role', 'status');
      pill.textContent = 'Using the backup server: answers can take up to a minute. · மாற்று சர்வர்: பதில் வர ஒரு நிமிடம் ஆகலாம்.';
      document.body.append(pill);
    }
    pill.hidden = !event.detail.on;
  });
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
    if (document.getElementById('proof')) closeProof();
    else if (document.getElementById('shield')) closeShield();
    else if (app.classList.contains('menu-open')) setMenu(false);
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

  /* ---------- proof card ("show the officer") ---------- */
  // The government's own page, the cited lines marked, who checked the fact and the next
  // steps from the answer: something to hold up at the counter, not a paragraph a model wrote.
  const PROOF = {
    en: { show: 'Show proof', title: 'Official proof', page: 'page', dated: 'dated',
      checked: (who, on) => `✔ Checked against the printed page by ${who}${on ? ` on ${on}` : ''}`,
      fromDoc: 'Quoted from the official document. The highlighted lines are what the answer is based on.',
      next: 'Your next steps', read: 'Read aloud', share: 'Share', open: 'Open official PDF', close: 'Close',
      noImage: 'The page image is not available here. Open the official PDF instead.',
      says: (doc, page) => `${doc}, page ${page} says:` },
    ta: { show: 'ஆதாரம் காட்டு', title: 'அதிகாரப்பூர்வ ஆதாரம்', page: 'பக்கம்', dated: 'நாள்',
      checked: (who, on) => `✔ அச்சிட்ட பக்கத்துடன் சரிபார்த்தவர்: ${who}${on ? `, ${on}` : ''}`,
      fromDoc: 'அதிகாரப்பூர்வ ஆவணத்திலிருந்து. மஞ்சள் வரிகளின் அடிப்படையில் பதில் தரப்பட்டது.',
      next: 'அடுத்து செய்ய வேண்டியவை', read: 'படித்துக் காட்டு', share: 'பகிர்', open: 'அதிகாரப்பூர்வ PDF', close: 'மூடு',
      noImage: 'பக்கப் படம் இங்கு கிடைக்கவில்லை. அதிகாரப்பூர்வ PDF-ஐத் திறக்கவும்.',
      says: (doc, page) => `${doc}, பக்கம் ${page} சொல்வது:` },
    'ta-Latn': { show: 'Proof kaattu', title: 'Official proof', page: 'page', dated: 'date',
      checked: (who, on) => `✔ Print page-oda check pannavar: ${who}${on ? `, ${on}` : ''}`,
      fromDoc: 'Official document-la irundhu. Highlight panna lines-a vechu dhaan badhil.',
      next: 'Adutha step', read: 'Padichu kaattu', share: 'Share', open: 'Official PDF', close: 'Close',
      noImage: 'Page image inga illa. Official PDF-a open pannunga.',
      says: (doc, page) => `${doc}, page ${page} solradhu:` },
    hi: { show: 'प्रमाण दिखाएँ', title: 'आधिकारिक प्रमाण', page: 'पेज', dated: 'दिनांक',
      checked: (who, on) => `✔ छपे पेज से जाँचा: ${who}${on ? `, ${on}` : ''}`,
      fromDoc: 'आधिकारिक दस्तावेज़ से। हाइलाइट की गई पंक्तियों पर उत्तर आधारित है।',
      next: 'आगे क्या करें', read: 'सुनाएँ', share: 'साझा करें', open: 'आधिकारिक PDF', close: 'बंद करें',
      noImage: 'पेज की छवि यहाँ उपलब्ध नहीं है। आधिकारिक PDF खोलें।',
      says: (doc, page) => `${doc}, पेज ${page} में लिखा है:` },
  };
  const proofText = (lang) => PROOF[lang] || PROOF.en;
  let proofAudio = null;

  function closeProof() {
    const sheet = document.getElementById('proof');
    if (sheet) sheet.remove();
    if (proofAudio) { proofAudio.pause(); proofAudio = null; }
    if (!document.getElementById('shield')) document.body.classList.remove('proof-open');
  }

  // The forward checker sits under a proof card opened from it, so it closes separately.
  function closeShield() {
    closeProof();
    const sheet = document.getElementById('shield');
    if (sheet) sheet.remove();
    document.body.classList.remove('proof-open');
  }

  function openProof(data, number, opener) {
    closeProof();
    const words = proofText(data.language);
    const cited = new Set(data.sentences.flatMap((s) => s.citations));
    const citations = data.citations.filter((c) => cited.has(c.number));
    if (!citations.length) return;
    let current = citations.find((c) => c.number === number) || citations[0];

    const sheet = el('div', 'proof');
    sheet.id = 'proof';
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'true');
    setLang(sheet, data.language);
    const box = el('div', 'proof-box');
    const head = el('div', 'proof-head');
    const heading = el('h2', 'proof-title', words.title);
    heading.id = 'proof-title';
    sheet.setAttribute('aria-labelledby', 'proof-title');
    const close = el('button', 'proof-close', '✕');
    close.type = 'button';
    close.setAttribute('aria-label', words.close);
    close.addEventListener('click', () => { closeProof(); if (opener) opener.focus(); });
    head.append(heading, close);

    const body = el('div', 'proof-body');
    const tabs = el('div', 'proof-tabs');
    const render = () => {
      body.textContent = '';
      const c = current;
      const doc = el('p', 'proof-doc', c.document);
      const meta = el('p', 'proof-meta', `${words.page} ${c.page_start}${c.document_date ? ` · ${words.dated} ${c.document_date}` : ''}`);
      body.append(doc, meta);
      body.append(el('p', c.checked_by ? 'proof-checked' : 'proof-note',
        c.checked_by ? words.checked(c.checked_by, c.checked_on) : words.fromDoc));
      const figure = el('figure', 'proof-page');
      const img = document.createElement('img');
      img.alt = `${c.document}, ${words.page} ${c.page_start}`;
      img.loading = 'eager';
      const mark = (c.excerpt || '').slice(0, 600);
      const pagePath = `/page?doc=${encodeURIComponent(c.doc_id)}&p=${c.page_start}&mark=${encodeURIComponent(mark)}`;
      const backup = window.PakkamBackup;
      img.src = backup ? backup.url(pagePath) : pagePath;
      img.addEventListener('error', () => {
        // The laptop may be offline: try the backup server once before giving up.
        if (backup && !img.src.startsWith(backup.backupUrl(''))) { img.src = backup.backupUrl(pagePath); zoom.href = img.src; return; }
        figure.replaceChildren(el('p', 'proof-note', words.noImage));
      });
      // Tap for the full-size page, readable across a counter.
      const zoom = el('a', 'proof-zoom');
      zoom.href = img.src;
      zoom.target = '_blank';
      zoom.rel = 'noopener';
      zoom.append(img);
      figure.append(zoom);
      body.append(figure);
      const steps = data.sentences.filter((s) => s.section === 'documents' || s.section === 'apply');
      if (steps.length) {
        body.append(el('h3', 'proof-next', words.next));
        const list = el('ol', 'proof-steps');
        steps.forEach((s) => list.append(el('li', null, s.text)));
        body.append(list);
      }
      tabs.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.n) === c.number)));
    };
    if (citations.length > 1) {
      citations.forEach((c) => {
        const tab = el('button', 'proof-tab', pageShort(c));
        tab.type = 'button';
        tab.dataset.n = String(c.number);
        tab.addEventListener('click', () => { current = c; render(); });
        tabs.append(tab);
      });
    }

    const actions = el('div', 'proof-actions');
    const read = el('button', 'proof-btn', `🔊 ${words.read}`);
    read.type = 'button';
    read.addEventListener('click', async () => {
      if (proofAudio) { proofAudio.pause(); proofAudio = null; return; }
      const first = data.sentences.find((s) => s.citations.includes(current.number)) || data.sentences[0];
      const text = `${words.says(current.document, current.page_start)} ${first ? first.text : ''}`;
      try {
        read.disabled = true;
        const url = await fetchSentenceAudio(text, data.language);
        proofAudio = new Audio(url);
        proofAudio.addEventListener('ended', () => { proofAudio = null; });
        await proofAudio.play();
      } catch { /* the page itself is the proof; audio is a bonus */ } finally { read.disabled = false; }
    });
    actions.append(read);
    const remind = el('button', 'proof-btn', `📅 ${REMIND[data.language] || REMIND.en}`);
    remind.type = 'button';
    remind.addEventListener('click', () => {
      const steps = data.sentences.filter((s) => s.section === 'documents' || s.section === 'apply').map((s) => s.text);
      const first = data.sentences.find((s) => s.citations.includes(current.number)) || data.sentences[0];
      downloadReminder(`Pakkam: ${current.scheme || current.document}`, [first ? first.text : '', ...steps, words.says(current.document, current.page_start), safeUrl(current.source_url) ? `${current.source_url}#page=${current.page_start}` : ''].filter(Boolean).join('\n'));
    });
    actions.append(remind);
    const pdf = safeUrl(current.source_url);
    if (navigator.share) {
      const share = el('button', 'proof-btn', `↗ ${words.share}`);
      share.type = 'button';
      share.addEventListener('click', () => {
        const first = data.sentences.find((s) => s.citations.includes(current.number)) || data.sentences[0];
        const link = safeUrl(current.source_url);
        navigator.share({
          title: words.title,
          text: `${first ? first.text : ''}\n${words.says(current.document, current.page_start)}${current.checked_by ? `\n${words.checked(current.checked_by, current.checked_on)}` : ''}`,
          ...(link ? { url: `${link}#page=${current.page_start}` } : {}),
        }).catch(() => {});
      });
      actions.append(share);
    }
    if (pdf) {
      const open = el('a', 'proof-btn', words.open);
      open.href = `${pdf}#page=${current.page_start}`;
      open.target = '_blank';
      open.rel = 'noopener noreferrer';
      actions.append(open);
    }

    box.append(head, tabs, body, actions);
    sheet.append(box);
    sheet.addEventListener('click', (event) => { if (event.target === sheet) closeProof(); });
    document.body.append(sheet);
    document.body.classList.add('proof-open');
    render();
    close.focus();
  }

  /* ---------- rumour shield ("is this forward true?") ---------- */
  // Each claim in a forward checked against the official documents, with the page as proof,
  // plus warning signs found by fixed rules (links, OTP, money, ID numbers, urgency).
  const SHIELD = {
    en: {
      title: 'Is this forward true?', placeholder: 'Paste the WhatsApp message here, or tap the mic and read it out.',
      check: 'Check it', checking: 'Checking each claim against the government orders…', speak: 'Read it out', stop: 'Stop',
      overall: { wrong: '❌ This forward is wrong', partly_wrong: '⚠️ Partly wrong', looks_right: '✅ Matches the official documents',
        not_in_documents: '⚠️ Not in any official document. Be careful.', no_claims: 'No scheme claim found in this message.' },
      verdict: { supported: '✅ True', contradicted: '❌ Wrong', not_in_documents: '⚠️ Not in the documents' },
      signs: { unofficial_link: 'The link is not a government website (.gov.in). Do not open it or enter details.',
        official_link: 'The link is a government website (.gov.in).',
        otp: 'It asks for an OTP. Government schemes never ask for your OTP. Never share it.',
        payment: 'It asks for money. Applying for these schemes does not need payment to anyone in a message.',
        personal_data: 'It asks for Aadhaar or bank details. Do not send them to unknown people.',
        urgency: '"Today only" pressure is a common trick. Check first.' },
      warnings: 'Warning signs', proof: 'Show proof', share: 'Send the correction on WhatsApp', listen: 'Read the result',
      correction: 'Fact-check by Pakkam (from the official government documents):', failed: 'Pakkam could not check this now. Try again in a minute.' },
    ta: {
      title: 'இந்த வாட்ஸ்அப் செய்தி உண்மையா?', placeholder: 'வாட்ஸ்அப் செய்தியை இங்கே ஒட்டுங்கள், அல்லது மைக்கைத் தொட்டு படியுங்கள்.',
      check: 'சரிபார்', checking: 'ஒவ்வொரு கூற்றும் அரசாணையுடன் சரிபார்க்கப்படுகிறது…', speak: 'படித்துச் சொல்', stop: 'நிறுத்து',
      overall: { wrong: '❌ இந்தச் செய்தி தவறு', partly_wrong: '⚠️ ஓரளவு தவறு', looks_right: '✅ அதிகாரப்பூர்வ ஆவணங்களுடன் பொருந்துகிறது',
        not_in_documents: '⚠️ எந்த அதிகாரப்பூர்வ ஆவணத்திலும் இல்லை. கவனம்.', no_claims: 'இந்தச் செய்தியில் திட்டம் பற்றிய கூற்று இல்லை.' },
      verdict: { supported: '✅ உண்மை', contradicted: '❌ தவறு', not_in_documents: '⚠️ ஆவணங்களில் இல்லை' },
      signs: { unofficial_link: 'இந்த இணைப்பு அரசு இணையதளம் (.gov.in) அல்ல. திறக்க வேண்டாம், விவரங்களைக் கொடுக்க வேண்டாம்.',
        official_link: 'இந்த இணைப்பு அரசு இணையதளம் (.gov.in).',
        otp: 'OTP கேட்கிறது. அரசுத் திட்டங்கள் ஒருபோதும் OTP கேட்பதில்லை. பகிர வேண்டாம்.',
        payment: 'பணம் கேட்கிறது. இந்தத் திட்டங்களுக்கு செய்தி மூலம் யாருக்கும் பணம் கட்டத் தேவையில்லை.',
        personal_data: 'ஆதார் அல்லது வங்கி விவரங்களைக் கேட்கிறது. தெரியாதவர்களுக்கு அனுப்ப வேண்டாம்.',
        urgency: '"இன்று மட்டும்" என்ற அவசரம் ஒரு வழக்கமான ஏமாற்று. முதலில் சரிபாருங்கள்.' },
      warnings: 'எச்சரிக்கை அறிகுறிகள்', proof: 'ஆதாரம் காட்டு', share: 'திருத்தத்தை வாட்ஸ்அப்பில் அனுப்பு', listen: 'முடிவைப் படித்துக் காட்டு',
      correction: 'பக்கம் சரிபார்ப்பு (அதிகாரப்பூர்வ அரசு ஆவணங்களிலிருந்து):', failed: 'இப்போது சரிபார்க்க முடியவில்லை. ஒரு நிமிடம் கழித்து முயற்சிக்கவும்.' },
    hi: {
      title: 'क्या यह व्हाट्सऐप संदेश सच है?', placeholder: 'व्हाट्सऐप संदेश यहाँ चिपकाएँ, या माइक दबाकर पढ़ें।',
      check: 'जाँचें', checking: 'हर दावे को सरकारी आदेश से जाँचा जा रहा है…', speak: 'पढ़कर सुनाएँ', stop: 'रोकें',
      overall: { wrong: '❌ यह संदेश गलत है', partly_wrong: '⚠️ आंशिक रूप से गलत', looks_right: '✅ आधिकारिक दस्तावेज़ों से मेल खाता है',
        not_in_documents: '⚠️ किसी आधिकारिक दस्तावेज़ में नहीं। सावधान रहें।', no_claims: 'इस संदेश में योजना का कोई दावा नहीं मिला।' },
      verdict: { supported: '✅ सही', contradicted: '❌ गलत', not_in_documents: '⚠️ दस्तावेज़ों में नहीं' },
      signs: { unofficial_link: 'यह लिंक सरकारी वेबसाइट (.gov.in) नहीं है। इसे न खोलें।',
        official_link: 'यह लिंक सरकारी वेबसाइट (.gov.in) है।',
        otp: 'यह OTP माँगता है। सरकारी योजनाएँ कभी OTP नहीं माँगतीं। इसे साझा न करें।',
        payment: 'यह पैसे माँगता है। इन योजनाओं के लिए संदेश से किसी को भुगतान नहीं करना होता।',
        personal_data: 'यह आधार या बैंक विवरण माँगता है। अनजान लोगों को न भेजें।',
        urgency: '"आज ही" का दबाव एक आम चाल है। पहले जाँचें।' },
      warnings: 'चेतावनी के संकेत', proof: 'प्रमाण दिखाएँ', share: 'सुधार व्हाट्सऐप पर भेजें', listen: 'नतीजा सुनाएँ',
      correction: 'पक्कम द्वारा जाँच (आधिकारिक सरकारी दस्तावेज़ों से):', failed: 'अभी जाँच नहीं हो सकी। एक मिनट बाद कोशिश करें।' },
  };
  SHIELD['ta-Latn'] = { ...SHIELD.en,
    title: 'Indha WhatsApp forward unmaiya?', check: 'Check pannu', checking: 'Ovvoru claim-um G.O. kooda check aagudhu…',
    overall: { ...SHIELD.en.overall, wrong: '❌ Indha forward thappu', partly_wrong: '⚠️ Konjam thappu', looks_right: '✅ Official documents kooda sariya irukku' },
    verdict: { supported: '✅ Unmai', contradicted: '❌ Thappu', not_in_documents: '⚠️ Documents-la illa' },
    share: 'Correction-a WhatsApp-la anuppu' };
  const shieldText = (lang) => SHIELD[lang] || SHIELD.en;
  const pageLabel = (c) => `${c.document}, ${proofText('en').page} ${c.page_start}`;

  function shieldResult(result, ui, box) {
    const lang = (result.claims.find((c) => c.answer && c.answer.language) || {}).answer?.language || ui;
    const words = shieldText(lang);
    const out = el('div', 'shield-result');
    setLang(out, lang);
    out.append(el('p', `shield-overall shield-${result.overall}`, words.overall[result.overall] || result.overall));
    const lines = [words.correction];
    result.claims.forEach((c) => {
      const card = el('div', `shield-claim shield-${c.verdict}`);
      card.append(el('p', 'shield-verdict', words.verdict[c.verdict] || c.verdict));
      card.append(el('p', 'shield-claim-text', `“${c.claim}”`));
      card.append(el('p', 'shield-why', c.explanation));
      const cites = (c.answer && c.answer.citations) || [];
      if (cites.length && c.answer.sentences.length) {
        const proof = el('button', 'proof-open-btn', `📄 ${words.proof}`);
        proof.type = 'button';
        proof.addEventListener('click', () => openProof(c.answer, null, proof));
        card.append(proof);
        lines.push(`${words.verdict[c.verdict]}: "${c.claim}". ${c.explanation} (${pageLabel(cites[0])})`);
      } else {
        lines.push(`${words.verdict[c.verdict]}: "${c.claim}".`);
      }
      out.append(card);
    });
    const signs = (result.scam_signs || []).filter((s) => s !== 'official_link');
    if (signs.length) {
      const warn = el('div', 'shield-warn');
      warn.append(el('p', 'shield-warn-title', `🚨 ${words.warnings}`));
      const list = el('ul');
      signs.forEach((s) => { list.append(el('li', null, words.signs[s])); lines.push(`🚨 ${words.signs[s]}`); });
      warn.append(list);
      out.append(warn);
    }
    const actions = el('div', 'proof-actions');
    const text = `${lines.join('\n')}\n${location.origin}/chat/`;
    const wa = el('a', 'proof-btn shield-wa', `💬 ${words.share}`);
    wa.href = `https://wa.me/?text=${encodeURIComponent(text)}`;
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    const listenBtn = el('button', 'proof-btn', `🔊 ${words.listen}`);
    listenBtn.type = 'button';
    listenBtn.addEventListener('click', async () => {
      if (proofAudio) { proofAudio.pause(); proofAudio = null; return; }
      const spoken = [words.overall[result.overall], ...result.claims.map((c) => `${words.verdict[c.verdict].replace(/^\S+\s/, '')}. ${c.explanation}`)].join(' ');
      try {
        listenBtn.disabled = true;
        proofAudio = new Audio(await fetchSentenceAudio(spoken.slice(0, 900), lang));
        proofAudio.addEventListener('ended', () => { proofAudio = null; });
        await proofAudio.play();
      } catch { /* the written result stands on its own */ } finally { listenBtn.disabled = false; }
    });
    actions.append(listenBtn, wa);
    out.append(actions);
    box.replaceChildren(out);
    out.scrollIntoView({ block: 'start' });
  }

  function openShield() {
    closeShield();
    const ui = voiceLanguage();
    const words = shieldText(ui);
    const sheet = el('div', 'proof');
    sheet.id = 'shield';
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'true');
    sheet.setAttribute('aria-labelledby', 'shield-title');
    setLang(sheet, ui);
    const box = el('div', 'proof-box');
    const head = el('div', 'proof-head');
    const heading = el('h2', 'proof-title', `🛡️ ${words.title}`);
    heading.id = 'shield-title';
    const close = el('button', 'proof-close', '✕');
    close.type = 'button';
    close.setAttribute('aria-label', 'Close');
    close.addEventListener('click', closeShield);
    head.append(heading, close);
    const body = el('div', 'proof-body');
    const input = document.createElement('textarea');
    input.className = 'shield-input';
    input.rows = 5;
    input.maxLength = 1500;
    input.placeholder = words.placeholder;
    const row = el('div', 'proof-actions shield-row');
    const mic = el('button', 'proof-btn', `🎤 ${words.speak}`);
    mic.type = 'button';
    const check = el('button', 'proof-btn shield-check', words.check);
    check.type = 'button';
    const status = el('p', 'proof-note shield-status');
    status.setAttribute('aria-live', 'polite');
    const results = el('div');
    row.append(mic, check);
    body.append(input, row, status, results);
    box.append(head, body);
    sheet.append(box);
    sheet.addEventListener('click', (event) => { if (event.target === sheet) closeShield(); });
    document.body.append(sheet);
    document.body.classList.add('proof-open');
    input.focus();

    let rec = null;
    mic.addEventListener('click', async () => {
      if (rec) {
        const recorder = rec; rec = null;
        mic.textContent = `🎤 ${words.speak}`;
        status.textContent = words.checking;
        try {
          const form = new FormData();
          form.append('audio', await recorder.stop(), 'forward.wav');
          form.append('language', voiceLanguage());
          const heard = await fetch('/transcribe', { method: 'POST', body: form });
          if (!heard.ok) throw new Error('stt');
          input.value = (await heard.json()).transcript;
          status.textContent = '';
        } catch { status.textContent = words.failed; }
        return;
      }
      if (!window.PakkamRecorder || !window.PakkamRecorder.supported) { status.textContent = TEXT.micBlocked; return; }
      try {
        rec = await window.PakkamRecorder.start({});
        mic.textContent = `⏹ ${words.stop}`;
      } catch { status.textContent = TEXT.micBlocked; }
    });
    check.addEventListener('click', async () => {
      const message = input.value.trim();
      if (message.length < 10) { input.focus(); return; }
      check.disabled = true;
      status.textContent = words.checking;
      try {
        const res = await fetch('/check-forward', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }),
        });
        if (!res.ok) throw new Error(String(res.status));
        status.textContent = '';
        shieldResult(await res.json(), ui, results);
      } catch { status.textContent = words.failed; } finally { check.disabled = false; }
    });
  }
  document.querySelectorAll('[data-forward]').forEach((b) => b.addEventListener('click', openShield));

  // Easy mode (for elderly people, and a volunteer helping someone): bigger text and buttons,
  // every answer read aloud, slower speech. Remembered on this phone only.
  let easyMode = false;
  const easyToggle = document.getElementById('easy-mode');
  function setEasy(on) {
    easyMode = on;
    document.body.classList.toggle('easy', on);
    if (easyToggle) easyToggle.setAttribute('aria-pressed', String(on));
    try { localStorage.setItem('pakkam-easy', on ? '1' : '0'); } catch { /* private mode */ }
  }
  if (easyToggle) easyToggle.addEventListener('click', () => setEasy(!easyMode));
  try { if (localStorage.getItem('pakkam-easy') === '1') setEasy(true); } catch { /* private mode */ }

  // Phone-call mode: every recording is turned into phone-line audio before it is sent.
  const phoneToggle = document.getElementById('phone-mode');
  if (phoneToggle && window.PakkamRecorder) {
    phoneToggle.addEventListener('click', () => {
      const on = phoneToggle.getAttribute('aria-pressed') !== 'true';
      window.PakkamRecorder.phoneMode = on;
      phoneToggle.setAttribute('aria-pressed', String(on));
      document.body.classList.toggle('phone-mode-on', on);
    });
  }

  // "Remind me": a calendar event 3 days ahead with the answer, next steps and the page link.
  // It stays on the person's phone; nothing is stored on the server.
  const REMIND = { en: 'Remind me', ta: 'நினைவூட்டு', 'ta-Latn': 'Remind pannu', hi: 'याद दिलाएँ' };
  function downloadReminder(title, details) {
    const start = new Date(Date.now() + 3 * 86400000);
    start.setHours(10, 0, 0, 0);
    const stamp = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    const esc = (t) => t.replace(/\\/g, '\\\\').replace(/[,;]/g, (m) => `\\${m}`).replace(/\n/g, '\\n');
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Pakkam//EN', 'BEGIN:VEVENT',
      `UID:${Date.now()}@pakkam`, `DTSTAMP:${stamp(new Date())}`, `DTSTART:${stamp(start)}`,
      `DTEND:${stamp(new Date(start.getTime() + 1800000))}`, `SUMMARY:${esc(title)}`, `DESCRIPTION:${esc(details)}`,
      'BEGIN:VALARM', 'TRIGGER:-PT30M', 'ACTION:DISPLAY', `DESCRIPTION:${esc(title)}`, 'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    link.download = 'pakkam-reminder.ics';
    document.body.append(link);
    link.click();
    link.remove();
  }

  /* ---------- visit checklist ---------- */
  // What to carry and how to apply, before going to the e-Sevai centre or ration shop: the
  // answer's own documents/apply sentences plus the scheme's signed cards, each with its page.
  const CHECK = {
    en: { button: 'Visit checklist', title: 'Before you go', hint: 'Tick each item as you get it ready.', read: 'Read aloud', share: 'Share', print: 'Print',
      empty: 'The official documents in Pakkam do not list the papers for this scheme. Ask at your e-Sevai centre.' },
    ta: { button: 'செல்லும் முன் பட்டியல்', title: 'செல்லும் முன்', hint: 'ஒவ்வொன்றும் தயாரானதும் குறியிடுங்கள்.', read: 'படித்துக் காட்டு', share: 'பகிர்', print: 'அச்சிடு',
      empty: 'இந்தத் திட்டத்துக்கான ஆவணங்கள் பக்கத்தில் உள்ள அதிகாரப்பூர்வ ஆவணங்களில் இல்லை. இ-சேவை மையத்தில் கேளுங்கள்.' },
    hi: { button: 'जाने से पहले सूची', title: 'जाने से पहले', hint: 'हर चीज़ तैयार होने पर टिक करें।', read: 'सुनाएँ', share: 'साझा करें', print: 'प्रिंट',
      empty: 'पक्कम के आधिकारिक दस्तावेज़ों में इस योजना के कागज़ों की सूची नहीं है। ई-सेवा केंद्र पर पूछें।' },
  };
  CHECK['ta-Latn'] = { ...CHECK.en, button: 'Pogum munnadi list', title: 'Pogum munnadi', hint: 'Ready aana tick pannunga.' };
  const checkText = (lang) => CHECK[lang] || CHECK.en;

  async function openChecklist(data, scheme, opener) {
    closeProof();
    const words = checkText(data.language);
    const items = [];
    const seen = new Set();
    const add = (text, citation) => {
      const key = text.trim();
      if (!key || seen.has(key)) return;
      seen.add(key);
      items.push({ text: key, citation });
    };
    data.sentences.filter((s) => s.section === 'documents' || s.section === 'apply').forEach((s) => {
      add(s.text, data.citations.find((c) => s.citations.includes(c.number)));
    });
    try {
      const res = await fetch(`/checklist?scheme=${encodeURIComponent(scheme)}&lang=${encodeURIComponent(data.language)}`);
      if (res.ok) (await res.json()).items.forEach((i) => add(i.text, i.citation));
    } catch { /* the answer's own steps still show */ }

    const sheet = el('div', 'proof');
    sheet.id = 'proof';
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'true');
    sheet.setAttribute('aria-labelledby', 'check-title');
    setLang(sheet, data.language);
    const box = el('div', 'proof-box');
    const head = el('div', 'proof-head');
    const heading = el('h2', 'proof-title', `🧾 ${words.title}: ${scheme}`);
    heading.id = 'check-title';
    const close = el('button', 'proof-close', '✕');
    close.type = 'button';
    close.setAttribute('aria-label', 'Close');
    close.addEventListener('click', () => { closeProof(); if (opener) opener.focus(); });
    head.append(heading, close);
    const body = el('div', 'proof-body');
    if (!items.length) {
      body.append(el('p', 'proof-note', words.empty));
    } else {
      body.append(el('p', 'proof-note', words.hint));
      const list = el('ul', 'check-list');
      items.forEach((item, i) => {
        const li = el('li', 'check-item');
        const box2 = document.createElement('input');
        box2.type = 'checkbox';
        box2.id = `check-${i}`;
        const label = el('label', null, item.text);
        label.htmlFor = box2.id;
        li.append(box2, label);
        if (item.citation) {
          const page = el('button', 'chip', pageShort(item.citation));
          page.type = 'button';
          page.title = item.citation.document;
          page.addEventListener('click', () => openProof({ language: data.language, citations: [{ ...item.citation, number: 1 }], sentences: [{ text: item.text, citations: [1], section: 'documents' }] }, 1, page));
          li.append(page);
        }
        list.append(li);
      });
      body.append(list);
    }
    const actions = el('div', 'proof-actions');
    const read = el('button', 'proof-btn', `🔊 ${words.read}`);
    read.type = 'button';
    read.addEventListener('click', async () => {
      if (proofAudio) { proofAudio.pause(); proofAudio = null; return; }
      try {
        read.disabled = true;
        proofAudio = new Audio(await fetchSentenceAudio(items.map((i) => i.text).join(' ').slice(0, 900) || words.empty, data.language));
        if (easyMode) proofAudio.playbackRate = 0.85;
        proofAudio.addEventListener('ended', () => { proofAudio = null; });
        await proofAudio.play();
      } catch { /* written list stands */ } finally { read.disabled = false; }
    });
    const shareText = `${words.title}: ${scheme}\n${items.map((i) => `☐ ${i.text}${i.citation ? ` (${i.citation.document}, p.${i.citation.page_start})` : ''}`).join('\n')}`;
    const wa = el('a', 'proof-btn shield-wa', `💬 ${words.share}`);
    wa.href = `https://wa.me/?text=${encodeURIComponent(shareText)}`;
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    const print = el('button', 'proof-btn', `🖨 ${words.print}`);
    print.type = 'button';
    print.addEventListener('click', () => window.print());
    actions.append(read, wa, print);
    box.append(head, body, actions);
    sheet.append(box);
    sheet.addEventListener('click', (event) => { if (event.target === sheet) closeProof(); });
    document.body.append(sheet);
    document.body.classList.add('proof-open');
    close.focus();
  }

  function checklistButton(data) {
    const button = el('button', 'proof-open-btn', `🧾 ${checkText(data.language).button}`);
    button.type = 'button';
    setLang(button, data.language);
    button.addEventListener('click', () => openChecklist(data, data.scheme, button));
    return button;
  }

  /* ---------- rejected? from the rule to an appeal note ---------- */
  // The person gives the scheme and the rejection reason. Pakkam asks the documents what the
  // rule says (a normal cited answer), then fills a fixed appeal template with that rule and
  // its page. The note is never written by a model: only the cited official sentences go in.
  const APPEAL = {
    en: { start: 'My application was rejected', title: 'Application rejected?', scheme: 'Scheme', reason: 'Reason given in the rejection message',
      situation: 'Your situation (optional), e.g. "we only have a two-wheeler"', go: 'Find the rule', working: 'Finding the rule in the government order…',
      rule: 'What the rule says', note: 'Draft appeal note (edit before you use it)', copy: 'Copy', share: 'Share', print: 'Print',
      noRule: 'The official documents in Pakkam do not cover this reason. You can ask an officer.',
      disclaimer: 'This is a draft to help you, not legal advice. Check every detail and ask at your e-Sevai centre how and by when to submit an appeal.',
      ask: (scheme, reason) => `Under ${scheme}, is this a reason not to be eligible: ${reason}? What does the rule say?`,
      template: (t) => `To\nThe officer concerned, ${t.scheme}\n\nSubject: Request to reconsider my application\n\nMy application under ${t.scheme} (Application No: __________) was rejected for this reason: "${t.reason}".\n${t.situation ? `My situation: ${t.situation}\n` : ''}\nThe government rule says (${t.document}, page ${t.page}):\n"${t.rule}"\n\nI request you to reconsider my application in the light of this rule.\n\nName: __________        Family card No: __________\nPhone: __________       Date: __________\nSignature: __________` },
    ta: { start: 'என் விண்ணப்பம் நிராகரிக்கப்பட்டது', title: 'விண்ணப்பம் நிராகரிக்கப்பட்டதா?', scheme: 'திட்டம்', reason: 'நிராகரிப்புச் செய்தியில் சொன்ன காரணம்',
      situation: 'உங்கள் நிலைமை (விருப்பம்), எ.கா. "எங்களிடம் இரு சக்கர வாகனம் மட்டுமே உள்ளது"', go: 'விதியைக் கண்டுபிடி', working: 'அரசாணையில் விதி தேடப்படுகிறது…',
      rule: 'விதி சொல்வது', note: 'மேல்முறையீட்டுக் கடித வரைவு (பயன்படுத்தும் முன் திருத்துங்கள்)', copy: 'நகலெடு', share: 'பகிர்', print: 'அச்சிடு',
      noRule: 'இந்தக் காரணம் பக்கத்தில் உள்ள அதிகாரப்பூர்வ ஆவணங்களில் இல்லை. அதிகாரியிடம் கேட்கலாம்.',
      disclaimer: 'இது உதவிக்கான வரைவு மட்டுமே, சட்ட ஆலோசனை அல்ல. ஒவ்வொரு விவரத்தையும் சரிபார்த்து, மேல்முறையீட்டை எப்படி, எப்போதுக்குள் தர வேண்டும் என்று இ-சேவை மையத்தில் கேளுங்கள்.',
      ask: (scheme, reason) => `${scheme} திட்டத்தில், இது தகுதியின்மைக்கான காரணமா: ${reason}? விதி என்ன சொல்கிறது?`,
      template: (t) => `பெறுநர்\nசம்பந்தப்பட்ட அலுவலர், ${t.scheme}\n\nபொருள்: எனது விண்ணப்பத்தை மறுபரிசீலனை செய்யக் கோருதல்\n\n${t.scheme} திட்டத்தின் கீழ் எனது விண்ணப்பம் (விண்ணப்ப எண்: __________) "${t.reason}" என்ற காரணத்தால் நிராகரிக்கப்பட்டது.\n${t.situation ? `எனது நிலைமை: ${t.situation}\n` : ''}\nஅரசு விதி (${t.document}, பக்கம் ${t.page}) கூறுவது:\n"${t.rule}"\n\nஇந்த விதியின் அடிப்படையில் எனது விண்ணப்பத்தை மறுபரிசீலனை செய்யுமாறு கேட்டுக்கொள்கிறேன்.\n\nபெயர்: __________        குடும்ப அட்டை எண்: __________\nதொலைபேசி: __________       தேதி: __________\nகையொப்பம்: __________` },
  };
  APPEAL['ta-Latn'] = APPEAL.en;
  APPEAL.hi = { ...APPEAL.en };
  const APPEAL_SCHEMES = ['Kalaignar Magalir Urimai Thittam', 'PM-KISAN', 'Pudhumai Penn Scheme', 'Pradhan Mantri Ujjwala Yojana', 'Atal Pension Yojana'];

  function openAppeal() {
    closeShield();
    const ui = voiceLanguage() === 'ta' ? 'ta' : 'en';
    const words = APPEAL[ui];
    const sheet = el('div', 'proof');
    sheet.id = 'shield';
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'true');
    sheet.setAttribute('aria-labelledby', 'appeal-title');
    setLang(sheet, ui);
    const box = el('div', 'proof-box');
    const head = el('div', 'proof-head');
    const heading = el('h2', 'proof-title', `📝 ${words.title}`);
    heading.id = 'appeal-title';
    const close = el('button', 'proof-close', '✕');
    close.type = 'button';
    close.setAttribute('aria-label', 'Close');
    close.addEventListener('click', closeShield);
    head.append(heading, close);
    const body = el('div', 'proof-body');
    const form = el('form', 'officer-form appeal-form');
    const schemeLabel = el('label', 'appeal-label', words.scheme);
    const scheme = document.createElement('select');
    scheme.className = 'officer-contact';
    APPEAL_SCHEMES.forEach((name) => { const o = el('option', null, name); o.value = name; scheme.append(o); });
    schemeLabel.append(scheme);
    const reason = document.createElement('textarea');
    reason.className = 'shield-input';
    reason.rows = 2;
    reason.maxLength = 300;
    reason.placeholder = words.reason;
    reason.required = true;
    const situation = document.createElement('textarea');
    situation.className = 'shield-input';
    situation.rows = 2;
    situation.maxLength = 300;
    situation.placeholder = words.situation;
    const go = el('button', 'proof-btn shield-check', words.go);
    go.type = 'submit';
    const status = el('p', 'proof-note');
    status.setAttribute('aria-live', 'polite');
    const result = el('div');
    form.append(schemeLabel, reason, situation, go, status);
    body.append(form, result);
    box.append(head, body);
    sheet.append(box);
    sheet.addEventListener('click', (event) => { if (event.target === sheet) closeShield(); });
    document.body.append(sheet);
    document.body.classList.add('proof-open');
    reason.focus();

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const why = reason.value.trim();
      if (why.length < 3) return;
      go.disabled = true;
      status.textContent = words.working;
      try {
        const res = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: words.ask(scheme.value, why).slice(0, 500), follow_up: { question: why, scheme: scheme.value } }),
        });
        if (!res.ok) throw new Error(String(res.status));
        const data = await res.json();
        status.textContent = '';
        result.textContent = '';
        if (data.refused || !data.sentences.length) {
          result.append(el('p', 'proof-note', words.noRule));
          result.append(officerForm({ ...data, question: `${scheme.value}: ${why}` }));
          return;
        }
        const c = data.citations.find((x) => data.sentences.some((s) => s.citations.includes(x.number))) || data.citations[0];
        result.append(el('h3', 'proof-next', words.rule));
        const rule = el('div', 'appeal-rule');
        data.sentences.forEach((s) => rule.append(el('p', null, s.text)));
        result.append(rule);
        const proof = el('button', 'proof-open-btn', `📄 ${proofText(data.language).show}`);
        proof.type = 'button';
        proof.addEventListener('click', () => openProof(data, null, proof));
        result.append(proof);
        result.append(el('h3', 'proof-next', words.note));
        const note = document.createElement('textarea');
        note.className = 'shield-input appeal-note';
        note.rows = 14;
        note.value = words.template({ scheme: scheme.value, reason: why, situation: situation.value.trim(), document: c.document, page: c.page_start,
          rule: data.sentences.map((s) => s.text).join(' ') });
        result.append(note);
        result.append(el('p', 'proof-note', words.disclaimer));
        const actions = el('div', 'proof-actions');
        const copy = el('button', 'proof-btn', `📋 ${words.copy}`);
        copy.type = 'button';
        copy.addEventListener('click', () => { navigator.clipboard && navigator.clipboard.writeText(note.value).catch(() => {}); });
        const wa = el('a', 'proof-btn shield-wa', `💬 ${words.share}`);
        wa.target = '_blank';
        wa.rel = 'noopener noreferrer';
        const syncLink = () => { wa.href = `https://wa.me/?text=${encodeURIComponent(note.value)}`; };
        syncLink();
        note.addEventListener('input', syncLink);
        const print = el('button', 'proof-btn', `🖨 ${words.print}`);
        print.type = 'button';
        print.addEventListener('click', () => window.print());
        actions.append(copy, wa, print, checklistButton({ ...data, scheme: scheme.value }));
        result.append(actions);
      } catch {
        status.textContent = (SHIELD[ui] || SHIELD.en).failed;
      } finally { go.disabled = false; }
    });
  }
  document.querySelectorAll('[data-appeal]').forEach((b) => b.addEventListener('click', openAppeal));

  function proofButton(data) {
    const words = proofText(data.language);
    const button = el('button', 'proof-open-btn', `📄 ${words.show}`);
    button.type = 'button';
    setLang(button, data.language);
    button.addEventListener('click', () => openProof(data, null, button));
    return button;
  }

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
  // "What can I get?": signed amounts per scheme, and the yearly total of the fixed ones.
  const FACTS_TEXT = {
    en: { total: (n, k) => `You may be eligible for up to ₹${n} a year from ${k} scheme${k > 1 ? 's' : ''}, if you meet each scheme's conditions.`, ask: 'Ask more' },
    ta: { total: (n, k) => `ஒவ்வொரு திட்டத்தின் நிபந்தனைகளும் பொருந்தினால், ${k} திட்டங்களிலிருந்து ஆண்டுக்கு ₹${n} வரை கிடைக்கலாம்.`, ask: 'மேலும் கேள்' },
    'ta-Latn': { total: (n, k) => `Ovvoru scheme-oda conditions porundhina, ${k} scheme-la irundhu varushathukku ₹${n} varai kidaikalam.`, ask: 'Innum kelu' },
    hi: { total: (n, k) => `हर योजना की शर्तें पूरी होने पर, ${k} योजनाओं से साल में ₹${n} तक मिल सकता है।`, ask: 'और पूछें' },
  };

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
    const facts = discovery ? (data.scheme_facts || []).filter((f) => f.amount || f.who) : [];
    if (facts.length) {
      const words2 = FACTS_TEXT[data.language] || FACTS_TEXT.en;
      const total = facts.reduce((sum, f) => sum + (f.yearly_amount || 0), 0);
      const counted = facts.filter((f) => f.yearly_amount).length;
      if (total > 0) {
        const sum = el('p', 'facts-total', words2.total(total.toLocaleString('en-IN'), counted));
        setLang(sum, data.language);
        card.append(sum);
      }
      const list = el('div', 'facts-list');
      facts.forEach((f) => {
        const item = el('div', 'facts-item');
        item.append(el('p', 'facts-scheme', f.scheme));
        if (f.amount) item.append(el('p', 'facts-line', `₹ ${f.amount}`));
        if (f.who) item.append(el('p', 'facts-line', `👤 ${f.who}`));
        const cites = [f.amount_citation, f.who_citation].filter(Boolean).map((c, i) => ({ ...c, number: i + 1 }));
        const lines = [f.amount, f.who].filter(Boolean);
        const proofData = {
          language: data.language,
          citations: cites,
          sentences: lines.map((text, i) => ({ text, citations: [i + 1], section: i === 0 && f.amount ? 'amount' : 'eligibility' })),
        };
        const row = el('div', 'facts-actions');
        const proof = el('button', 'proof-open-btn', `📄 ${proofText(data.language).show}`);
        proof.type = 'button';
        proof.addEventListener('click', () => openProof(proofData, null, proof));
        const more = el('button', 'follow-up', words2.ask);
        more.type = 'button';
        more.addEventListener('click', () => ask(words.about(f.scheme), { followUp: { question, scheme: f.scheme } }));
        row.append(proof, more);
        item.append(row);
        list.append(item);
      });
      card.append(list);
    }
    data.candidate_schemes.filter((scheme) => !facts.some((f) => f.scheme === scheme)).forEach((scheme) => {
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
    if (!refused && !clarify && data.citations && data.citations.length) meta.append(proofButton(data));
    if (!refused && !clarify && data.scheme) meta.append(checklistButton(data));
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

  // When the documents cannot answer: leave the question for an officer to follow up.
  const OFFICER = {
    en: { ask: 'Ask an officer', intro: 'Pakkam will pass your question to the scheme help desk. Do not write Aadhaar or bank numbers.',
      contact: 'Phone number for the call back (optional)', send: 'Send to an officer', sent: (t) => `Sent. Your reference is ${t}. Keep it to follow up.`, failed: 'Could not send now. Try again later.' },
    ta: { ask: 'அதிகாரியிடம் கேள்', intro: 'உங்கள் கேள்வி திட்ட உதவி மையத்துக்கு அனுப்பப்படும். ஆதார், வங்கி எண்களை எழுத வேண்டாம்.',
      contact: 'திரும்ப அழைக்க தொலைபேசி எண் (விருப்பம்)', send: 'அதிகாரிக்கு அனுப்பு', sent: (t) => `அனுப்பப்பட்டது. உங்கள் குறிப்பு எண் ${t}.`, failed: 'இப்போது அனுப்ப முடியவில்லை. பின்னர் முயற்சிக்கவும்.' },
    'ta-Latn': { ask: 'Officer-kitta kelu', intro: 'Unga kelvi scheme help desk-ku pogum. Aadhaar, bank number ezhudha vendaam.',
      contact: 'Call back-ku phone number (optional)', send: 'Officer-ku anuppu', sent: (t) => `Anuppiyaachu. Unga reference ${t}.`, failed: 'Ippo anuppa mudiyala. Apram try pannunga.' },
    hi: { ask: 'अधिकारी से पूछें', intro: 'आपका सवाल योजना हेल्प डेस्क को भेजा जाएगा। आधार या बैंक नंबर न लिखें।',
      contact: 'वापस कॉल के लिए फ़ोन नंबर (वैकल्पिक)', send: 'अधिकारी को भेजें', sent: (t) => `भेज दिया। आपका संदर्भ ${t} है।`, failed: 'अभी नहीं भेज सके। बाद में कोशिश करें।' },
  };

  function officerForm(data) {
    const words = OFFICER[data.language] || OFFICER.en;
    const form = el('form', 'officer-form');
    setLang(form, data.language);
    form.append(el('p', 'officer-intro', words.intro));
    const question = document.createElement('textarea');
    question.className = 'shield-input';
    question.rows = 2;
    question.maxLength = 500;
    question.value = data.question || lastAsked || '';
    const phone = document.createElement('input');
    phone.type = 'tel';
    phone.className = 'officer-contact';
    phone.placeholder = words.contact;
    phone.maxLength = 40;
    const send = el('button', 'proof-btn shield-check', words.send);
    send.type = 'submit';
    const status = el('p', 'proof-note');
    status.setAttribute('aria-live', 'polite');
    form.append(question, phone, send, status);
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      send.disabled = true;
      try {
        const res = await fetch('/officer-request', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: question.value, scheme: (data.contact && data.contact.scheme) || null, language: data.language, contact: phone.value || null }),
        });
        const body = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(typeof body.detail === 'string' ? body.detail : words.failed);
        status.textContent = words.sent(body.ticket);
        question.disabled = true;
        phone.disabled = true;
      } catch (error) {
        status.textContent = error.message || words.failed;
        send.disabled = false;
      }
    });
    return form;
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
    if (data.refusal_reason !== 'service_unavailable' && data.refusal_reason !== 'pii_detected') {
      const officer = el('button', 'refusal-link', `🙋 ${(OFFICER[data.language] || OFFICER.en).ask}`);
      officer.type = 'button';
      officer.addEventListener('click', () => { officer.disabled = true; card.append(officerForm(data)); });
      actions.append(officer);
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

  // Spoken last, after the answer: where it comes from, so the source is heard, not only seen.
  const SOURCE_SPOKEN = {
    en: (c) => `Source: ${c.document}, page ${c.page_start}.`,
    ta: (c) => `ஆதாரம்: ${c.document}, பக்கம் ${c.page_start}.`,
    'ta-Latn': (c) => `ஆதாரம்: ${c.document}, பக்கம் ${c.page_start}.`,
    hi: (c) => `स्रोत: ${c.document}, पेज ${c.page_start}.`,
  };

  function getSentencesToSpeak(data) {
    const first = data.confirmation_text ? [data.confirmation_text] : [];
    if (data.refused || !data.sentences || data.sentences.length === 0) {
      return [...first, data.answer];
    }
    const said = [...first, ...data.sentences.map((s) => s.text.trim()).filter(Boolean)];
    const cited = data.citations && data.citations.find((c) => data.sentences.some((s) => s.citations.includes(c.number)));
    if (cited) said.push((SOURCE_SPOKEN[data.language] || SOURCE_SPOKEN.en)(cited));
    return said;
  }

  // Said the moment a Talk-mode question is sent, so there is no silence while Pakkam reads
  // the documents. Fetched once per language when Talk mode opens, then played instantly.
  const FILLER = {
    ta: 'ஒரு நிமிடம், அரசாணையில் பார்க்கிறேன்.',
    'ta-Latn': 'ஒரு நிமிடம், அரசாணையில் பார்க்கிறேன்.',
    hi: 'एक पल, सरकारी आदेश में देख रहा हूँ।',
    en: 'One moment, checking the government order.',
  };
  const fillerUrls = {};
  function prefetchFiller(lang) {
    if (fillerUrls[lang] || !FILLER[lang]) return;
    fillerUrls[lang] = fetchSentenceAudio(FILLER[lang], lang === 'ta-Latn' ? 'ta' : lang).catch(() => {
      delete fillerUrls[lang];
      return null;
    });
  }
  async function playFiller(lang) {
    prefetchFiller(lang); // a language picked mid-talk is ready from the next question
    try {
      const url = await fillerUrls[lang];
      if (url) await new Audio(url).play();
    } catch { /* the answer still comes; the filler is only comfort */ }
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
        if (easyMode) audio.playbackRate = 0.85; // slower for elderly listeners, same pitch
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
  let lastAsked = '';
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
      lastAsked = asked;
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
    const turn = runTurn(options.label || question, (bubble, hooks) => fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: askBody(question, followUp),
      signal: hooks.signal,
    }), question, followUp);
    // Easy mode reads every answer aloud, so nobody has to read the screen.
    if (easyMode && !talkOn) {
      turn.then((result) => {
        const button = result && result.item && result.item.querySelector('.listen-btn');
        if (button) listen(result.data, button, true);
      });
    }
    return turn;
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
    prefetchFiller(voiceLanguage());
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
    playFiller(voiceLanguage());
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
