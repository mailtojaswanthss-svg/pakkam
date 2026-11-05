/* Backup answer server. The site's API paths (/ask, /speak, ...) normally reach the laptop
   through Vercel. When that is offline (tunnel down, laptop asleep), the same request goes
   straight to the backup on Hugging Face Spaces: slower (CPU), but the site keeps answering.
   After one failure, requests go to the backup for a few minutes before the laptop is tried
   again. Load before every other script that calls fetch. */
(() => {
  'use strict';

  const BACKUP = 'https://jazz716-pakkam.hf.space';
  const API = /^\/(ask|sources|transcribe|speak|feedback|check-forward|page|checklist|officer-request|dashboard\/stats)(\/|\?|$)/;
  const RETRY_LAPTOP_MS = 3 * 60 * 1000;
  const realFetch = window.fetch.bind(window);
  let backupSince = 0;

  const usingBackup = () => backupSince > 0 && Date.now() - backupSince < RETRY_LAPTOP_MS;

  // The laptop is unreachable, not just answering with an error of its own: no connection,
  // a gateway or Cloudflare error, or Vercel's own "not found" page instead of the API's JSON.
  function offline(res) {
    if ([502, 504].includes(res.status) || (res.status >= 520 && res.status <= 530)) return true;
    if ([404, 405].includes(res.status)) {
      return !(res.headers.get('content-type') || '').includes('application/json');
    }
    return false;
  }

  function note(on) {
    document.documentElement.classList.toggle('on-backup', on);
    window.dispatchEvent(new CustomEvent('pakkam-backup', { detail: { on } }));
  }

  async function viaBackup(path, init) {
    const res = await realFetch(BACKUP + path, init);
    note(true);
    return res;
  }

  window.fetch = async (input, init) => {
    const path = typeof input === 'string' ? input : '';
    if (!API.test(path)) return realFetch(input, init);
    if (usingBackup()) return viaBackup(path, init);
    try {
      const res = await realFetch(path, init);
      if (!offline(res)) {
        if (backupSince) { backupSince = 0; note(false); }
        return res;
      }
    } catch (error) {
      if (error && error.name === 'AbortError') throw error;
    }
    backupSince = Date.now();
    return viaBackup(path, init);
  };

  window.PakkamBackup = {
    /** The address for an API path used outside fetch (page images, links). */
    url: (path) => (usingBackup() ? BACKUP + path : path),
    backupUrl: (path) => BACKUP + path,
    active: usingBackup,
  };
})();
