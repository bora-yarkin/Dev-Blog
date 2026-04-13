// SPDX-FileCopyrightText: 2026 Bora Yarkın
// SPDX-License-Identifier: GPL-3.0-only

(() => {
  const els = {
    form: document.querySelector("#setup-form"),
    status: document.querySelector("#setup-status"),
    submit: document.querySelector("#setup-submit"),
    themeToggle: document.querySelector("#theme-toggle"),
    data: document.querySelector("#setup-data")
  };

  const data = (() => {
    if (!els.data) return {};
    try {
      return JSON.parse(els.data.textContent || "{}");
    } catch (err) {
      return {};
    }
  })();

  const THEME_ICONS = {
    sun: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" stroke="currentColor" stroke-width="2" fill="none"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="3" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="21"/><line x1="3" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="21" y2="12"/><line x1="5.6" y1="5.6" x2="7.1" y2="7.1"/><line x1="16.9" y1="16.9" x2="18.4" y2="18.4"/><line x1="5.6" y1="18.4" x2="7.1" y2="16.9"/><line x1="16.9" y1="7.1" x2="18.4" y2="5.6"/></g></svg>',
    moon: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 14.5a8.5 8.5 0 1 1-10.5-10 6.5 6.5 0 1 0 10.5 10Z"/></svg>'
  };

  const setStatus = (msg, isError = false) => {
    if (!els.status) return;
    els.status.textContent = msg || "";
    els.status.style.color = isError ? "var(--accent)" : "inherit";
  };

  const getPreferredTheme = () => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    const desired = theme === "dark" ? "dark" : "light";
    document.documentElement.classList.remove("theme-light", "theme-dark");
    document.documentElement.classList.add(desired === "dark" ? "theme-dark" : "theme-light");
    document.documentElement.style.colorScheme = desired;
    localStorage.setItem("theme", desired);
    if (els.themeToggle) {
      els.themeToggle.innerHTML = desired === "dark" ? THEME_ICONS.moon : THEME_ICONS.sun;
      els.themeToggle.setAttribute("aria-pressed", desired === "dark");
    }
  };

  const bind = () => {
    if (els.themeToggle) {
      els.themeToggle.addEventListener("click", () => {
        const next = document.documentElement.classList.contains("theme-dark") ? "light" : "dark";
        applyTheme(next);
      });
    }
    if (els.form) {
      els.form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(els.form);
        setStatus("Saving setup…");
        if (els.submit) els.submit.disabled = true;
        try {
          const res = await fetch("/api/setup", { method: "POST", body: fd });
          const json = await res.json();
          if (!res.ok) throw new Error(json.error || "Save failed");
          setStatus("Setup saved. You can open the admin area to continue.");
        } catch (err) {
          setStatus(err.message || "Save failed", true);
        } finally {
          if (els.submit) els.submit.disabled = false;
        }
      });
    }
  };

  const init = () => {
    applyTheme(getPreferredTheme());
    bind();
  };

  document.addEventListener("DOMContentLoaded", init);
})();
