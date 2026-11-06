/* One set of line icons (24px grid, drawn with currentColor) used everywhere instead of emoji,
   so buttons look the same on every phone. decorate() swaps a leading emoji in a label for
   the matching icon, so translated texts can keep their emoji as a simple marker. */

export const ICONS = {
  mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>',
  speaker: '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
  stop: '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/>',
  page: '<path d="M7 3.5h7l4 4v13H7z"/><path d="M14 3.5v4h4M9.5 12h6M9.5 15.5h4"/>',
  clipboard: '<rect x="5.5" y="4.5" width="13" height="16" rx="2"/><path d="M9 4.5V3.5h6v1M9 10h6M9 13.5h6M9 17h3.5"/>',
  share: '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/><path d="m8.7 10.8 6.6-4M8.7 13.2l6.6 4"/>',
  repeat: '<path d="M4 12a8 8 0 0 1 13.7-5.6L20 8.5M20 4v4.5h-4.5"/><path d="M20 12a8 8 0 0 1-13.7 5.6L4 15.5M4 20v-4.5h4.5"/>',
  note: '<path d="M5 4.5h14v15H5z"/><path d="M8.5 9h7M8.5 12.5h7M8.5 16h4"/>',
  simple: '<path d="M4.5 6.5h15a1 1 0 0 1 1 1V15a1 1 0 0 1-1 1H10l-4.5 3.5V16h-1a1 1 0 0 1-1-1V7.5a1 1 0 0 1 1-1Z"/><path d="M8.5 11.25h7"/>',
  print: '<path d="M7 9V3.5h10V9"/><rect x="4" y="9" width="16" height="7.5" rx="1.5"/><path d="M7 14h10v6.5H7z"/>',
  person: '<circle cx="12" cy="8" r="3.5"/><path d="M5 20.5c.8-4 3.6-6.5 7-6.5s6.2 2.5 7 6.5"/>',
  thumbUp: '<path d="M7.5 10.5v9h-3v-9zM7.5 10.5 11 3.5c1.6 0 2.5 1.1 2.2 2.7l-.6 3.3H18a2 2 0 0 1 2 2.3l-1.1 6a2 2 0 0 1-2 1.7H7.5"/>',
  thumbDown: '<path d="M7.5 13.5v-9h-3v9zM7.5 13.5l3.5 7c1.6 0 2.5-1.1 2.2-2.7l-.6-3.3H18a2 2 0 0 0 2-2.3l-1.1-6a2 2 0 0 0-2-1.7H7.5"/>',
  phone: '<path d="M6.6 3.5h2.6l1.4 4-2 1.5a11 11 0 0 0 6.4 6.4l1.5-2 4 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2Z"/>',
  shield: '<path d="M12 3.5 19 6v5.5c0 4.3-2.9 7.7-7 9-4.1-1.3-7-4.7-7-9V6z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
  rupee: '<path d="M7 4.5h10M7 9h10M9.5 4.5c3.5 0 5 1.7 5 4.5s-2 4.5-5.5 4.5H7.5l7 7"/>',
  leaf: '<path d="M12 21V10"/><path d="M12 13c-4 0-6-2.5-6-6 3.5 0 6 2 6 6Z"/><path d="M12 11c0-4 2.5-6.5 6-6.5 0 3.8-2.4 6.5-6 6.5Z"/>',
  flame: '<path d="M12 21c-3.6 0-6-2.4-6-5.6 0-3.4 2.6-5 3.6-8.4 1.6 1.4 2.4 3 2.4 4.6 1-.8 1.6-2 1.8-3.4 2.2 1.8 4.2 4.2 4.2 7.2C18 18.6 15.6 21 12 21Z"/>',
  ban: '<circle cx="12" cy="12" r="8.5"/><path d="m6 6 12 12"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  github: '<path d="M9 19c-4 1.3-4-2-5.5-2.5M14.5 21v-3.4a3 3 0 0 0-.8-2.3c2.7-.3 5.5-1.3 5.5-6a4.7 4.7 0 0 0-1.3-3.2 4.3 4.3 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.6 11.6 0 0 0-6 0C6 2.6 5 2.9 5 2.9a4.3 4.3 0 0 0-.1 3.2A4.7 4.7 0 0 0 3.6 9.3c0 4.7 2.8 5.7 5.5 6a3 3 0 0 0-.8 2.3V21"/>',
  linkedin: '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 10.5V16M8 7.5v.01M11.5 16v-3.2c0-1.4 1-2.3 2.2-2.3s2 .9 2 2.3V16M11.5 10.5V16"/>',
  mail: '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="m4 7 8 6 8-6"/>',
  lock: '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
  warn: '<path d="M12 4 21 19.5H3z"/><path d="M12 10v4.5M12 17.2v.01"/>',
  x: '<path d="m6.5 6.5 11 11M17.5 6.5l-11 11"/>',
  help: '<circle cx="12" cy="12" r="8.5"/><path d="M9.7 9.5a2.4 2.4 0 0 1 4.6.9c0 1.6-2.3 2-2.3 3.4M12 16.8v.01"/>',
  bulb: '<path d="M9 17.5h6M10 20.5h4M12 3.5a6 6 0 0 0-3.6 10.8c.6.5 1 1.2 1 2V17.5h5.2v-1.2c0-.8.4-1.5 1-2A6 6 0 0 0 12 3.5Z"/>',
  sparkle: '<path d="M12 3.5 13.8 10 20.5 12l-6.7 2L12 20.5 10.2 14 3.5 12l6.7-2z"/>',
};

const EMOJI = {
  '🎙️': 'mic', '🎙': 'mic', '🎤': 'mic', '🔊': 'speaker', '⏹': 'stop', '⏹️': 'stop', '📄': 'page', '📋': 'clipboard',
  '📤': 'share', '🔁': 'repeat', '📝': 'note', '🗣️': 'simple', '🗣': 'simple', '🖨️': 'print', '🖨': 'print',
  '👤': 'person', '👍': 'thumbUp', '👎': 'thumbDown', '📞': 'phone', '🛡️': 'shield', '🛡': 'shield', '💰': 'rupee',
  '🌾': 'leaf', '🔥': 'flame', '🙅': 'ban', '✓': 'check', '✅': 'check', '❌': 'x', '⚠️': 'warn', '⚠': 'warn',
  '🤔': 'help', '❓': 'help', '💡': 'bulb',
};
const LEADING = /^(\p{Extended_Pictographic}️?|⏹️?)\s*/u;

export function iconSvg(name, className = 'ui-icon') {
  const body = ICONS[name];
  if (!body) return '';
  return `<svg class="${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;
}

/** Split "📄 See the page" into ['page', 'See the page']; [null, text] when there is no known emoji. */
export function splitIcon(text) {
  const m = String(text ?? '').match(LEADING);
  if (!m) return [null, String(text ?? '')];
  const name = EMOJI[m[1]] || EMOJI[m[1].replace('️', '')];
  return name ? [name, text.slice(m[0].length)] : [null, String(text)];
}

/** Put the label's icon (if any) and its text into node. Returns true when an icon was used. */
export function decorate(node, text) {
  const [name, rest] = splitIcon(text);
  if (!name) { node.textContent = text; return false; }
  node.innerHTML = iconSvg(name);
  if (rest) {
    const span = document.createElement('span');
    span.textContent = rest;
    node.append(span);
  }
  return true;
}
