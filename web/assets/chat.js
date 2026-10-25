/* Pakkam chat app. Plain JS, no build step. All server text is inserted with textContent. */
(() => {
  'use strict';

  const MIN_CHARS = 3;
  const MAX_CHARS = 500;
  const TEXT = {
    tooShort: 'Type at least 3 characters.',
    tooLong: 'Keep it under 500 characters.',
    network: 'Pakkam could not reach the server. Check your connection and ask again.',
    server: 'Something went wrong on the server. Ask again in a moment.',
    waiting: 'Finding the pages, reading them and checking every sentence',
    chip: 'Show the source',
    sources: (n) => (n === 1 ? '1 source' : `${n} sources`),
    answeredIn: (ms) => `Answered in ${(ms / 1000).toFixed(1)} s`,
    openPdf: (page) => `Open the official PDF at page ${page}`,
    passage: 'Cited passage',
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

  class ServerError extends Error {}

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }
  const setLang = (node, lang) => { if (LANG_ATTR.has(lang)) node.lang = lang; };
  const safeUrl = (url) => (/^https?:\/\//i.test(url) ? url : null);
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
    if (data.latency_ms) meta.append(el('span', 'a-time', TEXT.answeredIn(data.latency_ms)));
    const disclaimer = el('p', 'disclaimer', data.disclaimer);
    setLang(disclaimer, data.language);
    body.append(meta, disclaimer);

    item.append(avatar(), body);
    return item;
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

  async function ask(raw) {
    const question = raw.trim();
    if (question.length < MIN_CHARS) return showFormMsg(TEXT.tooShort);
    if (question.length > MAX_CHARS) return showFormMsg(TEXT.tooLong);
    if (busy) return;

    showFormMsg('');
    busy = true;
    send.disabled = true;
    form.setAttribute('aria-busy', 'true');
    welcome.hidden = true;
    closeSources(false);

    const questionItem = el('li', 'msg q');
    const bubble = el('p', null, question);
    questionItem.append(bubble);
    const pending = assistantItem('pending', [el('p', 'wait', TEXT.waiting), el('span', 'wait-bar')]);
    log.append(questionItem, pending);
    scrollToEnd();
    input.value = '';
    autosize();

    try {
      let response;
      try {
        response = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question }),
        });
      } catch {
        throw new Error('network');
      }
      if (!response.ok) throw new ServerError(String(response.status));
      const data = await response.json();
      setLang(bubble, data.language);
      pending.replaceWith(renderAnswer(data));
    } catch (error) {
      const message = error instanceof ServerError ? TEXT.server : TEXT.network;
      pending.replaceWith(assistantItem('', [el('p', 'error-msg', message)]));
    } finally {
      busy = false;
      send.disabled = false;
      form.removeAttribute('aria-busy');
      scrollToEnd();
      input.focus({ preventScroll: true });
    }
  }

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
