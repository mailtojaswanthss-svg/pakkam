/* Pakkam theme: follows the system setting until the visitor picks one.
   Loaded without defer in <head>, so the first paint is already in the right theme. */
(() => {
  'use strict';

  const KEY = 'pakkam-theme';
  const THEMES = new Set(['light', 'dark']);
  const root = document.documentElement;
  const systemDark = matchMedia('(prefers-color-scheme: dark)');

  function readChoice() {
    try {
      const value = localStorage.getItem(KEY);
      return THEMES.has(value) ? value : null;
    } catch {
      return null; // storage blocked (private window): follow the system setting
    }
  }

  function saveChoice(theme) {
    try {
      localStorage.setItem(KEY, theme);
    } catch {
      // storage blocked: the choice still holds until the page is closed
    }
  }

  const activeTheme = () => root.dataset.theme || (systemDark.matches ? 'dark' : 'light');

  function sync() {
    const theme = activeTheme();
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta && meta.dataset[theme]) meta.content = meta.dataset[theme];
    document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    });
  }

  function apply(theme) {
    if (theme) root.dataset.theme = theme;
    else delete root.dataset.theme;
    sync();
  }

  apply(readChoice());
  systemDark.addEventListener('change', () => { if (!root.dataset.theme) sync(); });

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
      button.hidden = false;
      button.addEventListener('click', () => {
        const next = activeTheme() === 'dark' ? 'light' : 'dark';
        saveChoice(next);
        apply(next);
      });
    });
    sync();
  });
})();
