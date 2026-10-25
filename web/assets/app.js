/* Pakkam chat. Plain JS, no build step. All server text is inserted with textContent. */
(() => {
  'use strict';

  const MIN_CHARS = 3;
  const MAX_CHARS = 500;
  const TEXT = {
    tooShort: 'Type at least 3 characters.',
    tooLong: 'Keep it under 500 characters.',
    network: 'Pakkam could not reach the server. Check your connection and ask again.',
    server: 'Something went wrong on the server. Ask again in a moment.',
    waiting: 'Reading the documents',
    chip: 'Show the source',
    openPdf: 'Open the official PDF',
    close: 'Close',
    passage: 'Cited passage',
    sourcesFailed: 'The document list could not load. Each answer still links its own source.',
  };
  const LANG_NAME = { en: 'English', ta: 'தமிழ்', hi: 'हिन्दी', 'ta-Latn': 'Tanglish' };
  const LANG_ATTR = new Set(['en', 'ta', 'hi', 'ta-Latn']);

  const $ = (selector, root = document) => root.querySelector(selector);
  const form = $('#ask');
  const input = $('#q');
  const log = $('#log');
  const formMsg = $('#form-msg');
  const empty = $('#empty');
  const send = $('.send', form);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  class ServerError extends Error {}

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function setLang(node, lang) {
    if (LANG_ATTR.has(lang)) node.lang = lang;
  }

  function reveal(node) {
    node.scrollIntoView({ block: 'nearest', behavior: reduceMotion.matches ? 'auto' : 'smooth' });
  }

  function pagesText(c) {
    return c.page_start === c.page_end ? `page ${c.page_start}` : `pages ${c.page_start} to ${c.page_end}`;
  }

  function safeUrl(url) {
    return /^https?:\/\//i.test(url) ? url : null;
  }

  /* ---------- the source slip ---------- */

  let open = null; // { chip, slip, item }
  let slipCount = 0;

  function closeSlip(returnFocus) {
    if (!open) return;
    const { chip, slip, item } = open;
    slip.remove();
    chip.setAttribute('aria-expanded', 'false');
    item.querySelectorAll('.sent.lit').forEach((s) => s.classList.remove('lit'));
    if (returnFocus) chip.focus();
    open = null;
  }

  function buildSlip(c, id) {
    const slip = el('section', 'slip');
    slip.id = id;
    slip.setAttribute('aria-label', `${c.scheme}, ${pagesText(c)}`);

    const head = el('div', 'slip-head');
    const meta = el('div', 'slip-meta');
    meta.append(el('p', 'slip-title', `${c.scheme}, ${pagesText(c)}`));
    const lang = LANG_NAME[c.language];
    meta.append(el('p', 'slip-doc', lang ? `${c.document} (${lang})` : c.document));
    const close = el('button', 'slip-close', TEXT.close);
    close.type = 'button';
    close.addEventListener('click', () => closeSlip(true));
    head.append(meta, close);

    const passage = el('blockquote', 'slip-text', c.excerpt);
    passage.tabIndex = 0; // scrollable, so keyboard users can reach it
    passage.setAttribute('aria-label', TEXT.passage);
    setLang(passage, c.language);

    slip.append(head, passage);
    const url = safeUrl(c.source_url);
    if (url) {
      const link = el('a', 'slip-link', TEXT.openPdf);
      link.href = `${url}#page=${c.page_start}`; // PDF viewers open at that page
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      slip.append(link);
    }
    return slip;
  }

  function toggleSlip(chip, citation, item) {
    const same = open && open.chip === chip;
    closeSlip(false);
    if (same) return;
    const id = `slip-${++slipCount}`;
    const slip = buildSlip(citation, id);
    $('.slip-holder', item).append(slip);
    chip.setAttribute('aria-expanded', 'true');
    chip.setAttribute('aria-controls', id);
    item.querySelectorAll('.sent').forEach((s) => {
      if (s.dataset.cites.split(' ').includes(String(citation.number))) s.classList.add('lit');
    });
    open = { chip, slip, item };
    reveal(slip);
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && open) closeSlip(true);
  });

  /* ---------- rendering ---------- */

  function chipFor(citation, item) {
    const chip = el('button', 'chip', String(citation.number));
    chip.type = 'button';
    chip.title = TEXT.chip;
    chip.setAttribute('aria-label', `${TEXT.chip}: ${citation.scheme}, ${pagesText(citation)}`);
    chip.setAttribute('aria-expanded', 'false');
    chip.addEventListener('click', () => toggleSlip(chip, citation, item));
    return chip;
  }

  function renderAnswer(data) {
    const item = el('li', 'msg a');
    const body = el('div', 'answer');
    setLang(body, data.language);
    const byNumber = new Map(data.citations.map((c) => [c.number, c]));

    if (data.refused || data.sentences.length === 0) {
      body.append(el('p', 'refusal', data.answer));
    } else {
      const para = el('p', 'sentences');
      data.sentences.forEach((sentence) => {
        const span = el('span', 'sent', sentence.text);
        span.dataset.cites = sentence.citations.join(' ');
        para.append(span);
        sentence.citations.forEach((n) => {
          const citation = byNumber.get(n);
          if (citation) para.append(chipFor(citation, item));
        });
        para.append(' ');
      });
      body.append(para);
    }

    const disclaimer = el('p', 'disclaimer', data.disclaimer);
    setLang(disclaimer, data.language);
    item.append(body, el('div', 'slip-holder'), disclaimer);
    return item;
  }

  function errorItem(message) {
    const item = el('li', 'msg a');
    item.append(el('p', 'error-msg', message));
    return item;
  }

  /* ---------- asking ---------- */

  let busy = false;

  function showFormMsg(text) {
    formMsg.textContent = text;
  }

  function autosize() {
    input.style.height = 'auto';
    input.style.height = `${input.scrollHeight + 2}px`;
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
    empty.hidden = true;
    closeSlip(false);

    const questionItem = el('li', 'msg q');
    const bubble = el('p', 'bubble', question);
    questionItem.append(bubble);
    const pending = el('li', 'msg a pending');
    pending.append(el('p', 'wait', TEXT.waiting), el('span', 'wait-rule'));
    log.append(questionItem, pending);
    reveal(pending);
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
      const item = renderAnswer(data);
      pending.replaceWith(item);
      reveal(item);
    } catch (error) {
      pending.replaceWith(errorItem(error instanceof ServerError ? TEXT.server : TEXT.network));
    } finally {
      busy = false;
      send.disabled = false;
      form.removeAttribute('aria-busy');
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
    if (input.value) stopTyping();
  });

  document.querySelectorAll('.ex').forEach((button) => {
    button.addEventListener('click', () => ask(button.textContent));
  });

  /* ---------- placeholder that types sample questions ---------- */

  const SAMPLES = Array.from(document.querySelectorAll('.ex'), (b) => ({ text: b.textContent.trim(), lang: b.lang }));
  const STATIC_PLACEHOLDER = (SAMPLES.find((s) => s.lang === 'en') || SAMPLES[0]).text;
  let typingTimer = null;
  let sampleIndex = 0;

  function graphemes(text, lang) {
    // Type whole letters (a Tamil consonant with its vowel sign), never half a letter.
    if ('Segmenter' in Intl) {
      return Array.from(new Intl.Segmenter(lang || 'en', { granularity: 'grapheme' }).segment(text), (s) => s.segment);
    }
    return Array.from(text);
  }

  function canType() {
    return !reduceMotion.matches && !document.hidden && !input.value && document.activeElement !== input;
  }

  function stopTyping() {
    clearTimeout(typingTimer);
    typingTimer = null;
    input.placeholder = STATIC_PLACEHOLDER;
  }

  function typeNext() {
    if (!canType()) return stopTyping();
    const sample = SAMPLES[sampleIndex++ % SAMPLES.length];
    const parts = graphemes(sample.text, sample.lang);
    let shown = 0;

    const erase = () => {
      if (!canType()) return stopTyping();
      shown -= 1;
      input.placeholder = parts.slice(0, shown).join('');
      typingTimer = setTimeout(shown > 0 ? erase : typeNext, shown > 0 ? 18 : 380);
    };
    const type = () => {
      if (!canType()) return stopTyping();
      shown += 1;
      input.placeholder = parts.slice(0, shown).join('');
      typingTimer = setTimeout(shown < parts.length ? type : erase, shown < parts.length ? 55 : 1900);
    };
    type();
  }

  function startTyping() {
    if (typingTimer || !canType()) return;
    input.placeholder = '';
    typingTimer = setTimeout(typeNext, 600);
  }

  input.addEventListener('focus', stopTyping);
  input.addEventListener('blur', startTyping);
  document.addEventListener('visibilitychange', () => (document.hidden ? stopTyping() : startTyping()));
  reduceMotion.addEventListener('change', () => (reduceMotion.matches ? stopTyping() : startTyping()));

  input.placeholder = STATIC_PLACEHOLDER;
  startTyping();

  /* ---------- the document list ---------- */

  async function loadSources() {
    const list = $('#src-list');
    try {
      const response = await fetch('/sources');
      if (!response.ok) throw new Error(String(response.status));
      const docs = await response.json();

      // scheme -> title -> documents (one link per language version)
      const schemes = new Map();
      docs.forEach((doc) => {
        if (!schemes.has(doc.scheme)) schemes.set(doc.scheme, new Map());
        const titles = schemes.get(doc.scheme);
        if (!titles.has(doc.title)) titles.set(doc.title, []);
        titles.get(doc.title).push(doc);
      });

      list.textContent = '';
      schemes.forEach((titles, scheme) => {
        const item = el('li', 'src');
        item.append(el('h3', 'src-name', scheme));
        titles.forEach((versions, title) => {
          const row = el('p', 'src-doc');
          row.append(el('span', null, title));
          versions.forEach((doc) => {
            const url = safeUrl(doc.source_url);
            if (!url) return;
            const link = el('a', null, LANG_NAME[doc.language] || doc.language);
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.setAttribute('aria-label', `${title}, ${LANG_NAME[doc.language] || doc.language} PDF`);
            setLang(link, doc.language);
            row.append(link);
          });
          item.append(row);
        });
        list.append(item);
      });
    } catch {
      list.textContent = '';
      list.append(el('li', 'src-note', TEXT.sourcesFailed));
    }
  }

  loadSources();
})();
