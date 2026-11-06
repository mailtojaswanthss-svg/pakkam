/* A small spotlight tour: dims the page, rings one element and explains it in a card with
   Back / Next / Skip. Each step can prepare the page first (open a page, ask a sample question).
   Keyboard: Enter or → next, ← back, Escape ends. */

export function runTour(steps, labels) {
  let index = 0;
  let ended = false;
  const spot = document.createElement('div');
  spot.className = 'tour-spot';
  const card = document.createElement('div');
  card.className = 'tour-card';
  card.setAttribute('role', 'dialog');
  card.setAttribute('aria-live', 'polite');
  document.body.append(spot, card);
  document.body.classList.add('touring');

  function end() {
    if (ended) return;
    ended = true;
    spot.remove();
    card.remove();
    document.body.classList.remove('touring');
    window.removeEventListener('resize', place);
    document.removeEventListener('keydown', onKey, true);
    steps[index]?.leave?.();
  }

  function place() {
    const step = steps[index];
    const target = step && document.querySelector(step.target);
    if (!target) { spot.style.opacity = '0'; card.classList.add('centered'); return; }
    target.scrollIntoView({ block: 'center', behavior: 'instant' });
    const box = target.getBoundingClientRect();
    const pad = 8;
    spot.style.opacity = '1';
    Object.assign(spot.style, { left: `${box.left - pad}px`, top: `${box.top - pad}px`, width: `${box.width + pad * 2}px`, height: `${box.height + pad * 2}px` });
    card.classList.remove('centered');
    const below = box.bottom + 16 + card.offsetHeight < window.innerHeight;
    const top = below ? box.bottom + 16 : Math.max(12, box.top - card.offsetHeight - 16);
    const left = Math.min(window.innerWidth - card.offsetWidth - 12, Math.max(12, box.left + box.width / 2 - card.offsetWidth / 2));
    Object.assign(card.style, { top: `${top}px`, left: `${left}px` });
  }

  async function show(next) {
    steps[index]?.leave?.();
    index = next;
    if (index >= steps.length) { end(); return; }
    const step = steps[index];
    card.innerHTML = '';
    const count = document.createElement('p');
    count.className = 'tour-count';
    count.textContent = labels.count.replace('{n}', index + 1).replace('{total}', steps.length);
    const title = document.createElement('h3');
    title.textContent = step.title;
    const body = document.createElement('p');
    body.textContent = step.body;
    const actions = document.createElement('div');
    actions.className = 'tour-actions';
    const skip = button(labels.skip, 'text-link', end);
    const back = button(labels.back, 'chip-btn', () => show(index - 1));
    back.disabled = index === 0;
    const go = button(index === steps.length - 1 ? labels.done : labels.next, 'cta-button', () => show(index + 1));
    actions.append(skip, back, go);
    card.append(count, title, body, actions);
    if (step.enter) { card.classList.add('busy'); try { await step.enter(); } catch (_) { /* keep going */ } card.classList.remove('busy'); }
    if (ended) return;
    place();
    go.focus({ preventScroll: true });
    setTimeout(() => { if (!ended) place(); }, 450);  // again once smooth scrolling has settled
  }

  function button(text, className, onClick) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = className;
    b.textContent = text;
    b.addEventListener('click', onClick);
    return b;
  }

  function onKey(event) {
    if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); end(); }
    else if (event.key === 'ArrowRight') show(index + 1);
    else if (event.key === 'ArrowLeft' && index > 0) show(index - 1);
  }

  window.addEventListener('resize', place);
  document.addEventListener('keydown', onKey, true);
  show(0);
  return { end };
}
