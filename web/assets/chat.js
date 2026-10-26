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
  const TEXT = {
    tooShort: 'Type at least 3 characters.',
    tooLong: 'Keep it under 500 characters.',
    network: 'Pakkam could not reach the server. Check your connection and ask again.',
    server: 'Something went wrong on the server. Ask again in a moment.',
    tooMany: 'Pakkam is getting a lot of questions. Wait a minute, then ask again.',
    timeout: 'Pakkam took too long to answer. Ask again in a moment.',
    offline: 'The live chat is offline right now. The answer server is not connected to this site.',
    waiting: 'Finding the pages, reading them and checking every sentence',
    chip: 'Show the source',
    sources: (n) => (n === 1 ? '1 source' : `${n} sources`),
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
  $('#side-close').addEventListener('click', () => setMenu(false));
  scrim.addEventListener('click', () => setMenu(false));

  /* ---------- sources panel ---------- */
  let open = null; // { chip, item }

  function closeSources(returnFocus) {
    if (!open) return;
    panel.hidden = true;
    open.item.querySelectorAll('.sent.lit').forEach((s) => s.classList.remove('lit'));
    open.item.querySelectorAll('[aria-expanded="true"]').forEach((b) => b.setAttribute('aria-expanded', 'false'));
    if (returnFocus) open.chip.focus({ preventScroll: true });
    open = null;
  }

  function sourceCard(c, current) {
    const li = el('li', `source${current ? ' current' : ''}`);
    const head = el('div', 'source-head');
    head.append(el('span', 'source-no', String(c.number)));
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
    open = { chip: opener, item };
    panelHeading.focus({ preventScroll: true });
    if (currentCard) currentCard.scrollIntoView({ block: 'nearest' });
  }

  $('#sources-close').addEventListener('click', () => closeSources(true));
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

  function renderAnswer(data) {
    const item = el('li', 'msg a');
    const body = el('div', 'a-body');
    setLang(body, data.language);

    if (data.refused || data.sentences.length === 0) {
      body.append(el('p', 'refusal', data.answer));
    } else {
      const byNumber = new Map(data.citations.map((c) => [c.number, c]));
      const para = el('p', 'sentences');
      data.sentences.forEach((sentence) => {
        const span = el('span', 'sent', sentence.text);
        span.dataset.cites = sentence.citations.join(' ');
        para.append(span);
        sentence.citations.forEach((n) => {
          const c = byNumber.get(n);
          if (!c) return;
          const chip = el('button', 'chip', String(n));
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
      });
      body.append(para);
    }

    const meta = el('div', 'a-meta');
    if (data.citations.length) {
      const button = el('button', 'sources-btn', TEXT.sources(data.citations.length));
      button.type = 'button';
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-controls', 'sources');
      button.addEventListener('click', () => {
        if (open && open.chip === button) closeSources(true);
        else openSources(data, null, button, item);
      });
      meta.append(button);
    }
    meta.append(listenButton(data));
    if (data.latency_ms) meta.append(el('span', 'a-time', TEXT.answeredIn(data.latency_ms)));
    const disclaimer = el('p', 'disclaimer', data.disclaimer);
    setLang(disclaimer, data.language);
    body.append(meta, disclaimer);

    item.append(avatar(), body);
    return item;
  }

  /* ---------- spoken answers (Gnani Timbre on the server; only after a tap) ---------- */
  let playing = null; // { audio, button, url }

  function stopPlaying() {
    if (!playing) return;
    playing.audio.pause();
    URL.revokeObjectURL(playing.url);
    playing.button.textContent = TEXT.listen;
    playing.button.setAttribute('aria-pressed', 'false');
    playing = null;
  }

  function spokenText(data) {
    if (data.refused || data.sentences.length === 0) return data.answer;
    return data.sentences.map((s) => s.text).join(' ');
  }

  async function listen(data, button) {
    if (playing && playing.button === button) return stopPlaying();
    stopPlaying();
    button.disabled = true;
    button.textContent = TEXT.listenLoading;
    try {
      const response = await fetch('/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: spokenText(data), language: data.language }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(typeof body.detail === 'string' ? body.detail : TEXT.listenFailed);
      }
      const url = URL.createObjectURL(await response.blob());
      const audio = new Audio(url);
      playing = { audio, button, url };
      audio.addEventListener('ended', stopPlaying);
      button.textContent = TEXT.listenStop;
      button.setAttribute('aria-pressed', 'true');
      await audio.play();
    } catch (error) {
      stopPlaying();
      button.textContent = TEXT.listen;
      showFormMsg(error instanceof TypeError ? TEXT.network : error.message);
    } finally {
      button.disabled = false;
    }
  }

  function listenButton(data) {
    const button = el('button', 'sources-btn listen-btn', TEXT.listen);
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
  const showFormMsg = (text) => { formMsg.textContent = text; };

  function autosize() {
    input.style.height = 'auto';
    input.style.height = `${input.scrollHeight}px`;
  }

  // One question and answer turn. `request` returns the fetch promise; `label` shows until the
  // server replies (for voice, the transcript then replaces it).
  async function runTurn(label, request) {
    if (busy) return;
    showFormMsg('');
    busy = true;
    send.disabled = true;
    form.setAttribute('aria-busy', 'true');
    welcome.hidden = true;
    closeSources(false);

    const questionItem = el('li', 'msg q');
    const bubble = el('p', null, label);
    questionItem.append(bubble);
    const pending = assistantItem('pending', [el('p', 'wait', TEXT.waiting), el('span', 'wait-bar')]);
    log.append(questionItem, pending);
    scrollToEnd();

    try {
      let response;
      try {
        response = await withTimeout(request(), ASK_TIMEOUT_MS);
      } catch (error) {
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
      pending.replaceWith(renderAnswer(data));
    } catch (error) {
      let message = error.message === 'timeout' ? TEXT.timeout : TEXT.network;
      if (error instanceof ServerError) {
        // 404/405: a static host (e.g. Vercel) with no answer server behind it.
        // 429: the server says whether to wait a minute or come back tomorrow.
        if (error.status === 429) message = error.detail || TEXT.tooMany;
        else if (error.status === 404 || error.status === 405) message = TEXT.offline;
        else if (error.detail && VOICE_ERRORS.has(error.status)) message = error.detail;
        else message = TEXT.server;
      }
      pending.replaceWith(assistantItem('', [el('p', 'error-msg', message)]));
      return error;
    } finally {
      busy = false;
      send.disabled = false;
      form.removeAttribute('aria-busy');
      scrollToEnd();
      input.focus({ preventScroll: true });
    }
  }

  function ask(raw) {
    const question = raw.trim();
    if (question.length < MIN_CHARS) return showFormMsg(TEXT.tooShort);
    if (question.length > MAX_CHARS) return showFormMsg(TEXT.tooLong);
    if (busy) return;
    input.value = '';
    autosize();
    return runTurn(question, () => fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    }));
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

  function setVoiceStatus(text, spoken = text) {
    voiceStatus.textContent = text;
    if (spoken !== null) voiceAnnounce.textContent = spoken;
  }

  // Worth sending the same clip again: the request never arrived, or the server failed.
  // Not for 4xx answers like "could not hear", where speaking again is the fix.
  const canRetry = (error) => !(error instanceof ServerError) || error.status >= 500;

  async function askVoice(audio, filename, language = voiceLanguage()) {
    retryButton.hidden = true;
    lastClip = { audio, filename, language };
    const body = new FormData();
    body.append('audio', audio, filename);
    body.append('language', language);
    setVoiceStatus(TEXT.sendingVoice);
    const slow = setTimeout(() => setVoiceStatus(TEXT.slowUpload), SLOW_UPLOAD_MS);
    const error = await runTurn(TEXT.voiceQuestion, () => fetch('/ask/voice', { method: 'POST', body }));
    clearTimeout(slow);
    if (error && canRetry(error)) {
      setVoiceStatus(TEXT.voiceFailed);
      retryButton.hidden = false;
    } else {
      setVoiceStatus('');
      lastClip = null;
    }
  }

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
    cancelButton.hidden = true;
    return recorder;
  }

  async function stopRecording() {
    if (!recording) return;
    const wav = await endRecording().stop();
    askVoice(wav, 'question.wav');
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
      const recorder = await window.PakkamRecorder.start();
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
    if (lastClip && !busy) askVoice(lastClip.audio, lastClip.filename, lastClip.language);
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
    if (file) askVoice(file, file.name);
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

  /* ---------- new conversation ---------- */
  document.querySelectorAll('[data-new-chat]').forEach((button) => {
    button.addEventListener('click', () => {
      if (busy) return;
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
        const li = el('li', null, scheme);
        li.append(el('span', 'scheme-docs', Array.from(langs).join(', ')));
        list.append(li);
      });
    } catch {
      list.textContent = '';
      list.append(el('li', 'scheme-note', TEXT.schemesFailed));
    }
  }
  loadSchemes();
})();
