// SPDX-FileCopyrightText: 2026 Bora Yarkın
// SPDX-License-Identifier: GPL-3.0-only

(() => {
  const state = {
    data: null,
    lang: localStorage.getItem("admin-lang") || "en",
    section: "home",
    dirty: false
  };

  const sections = [
    { id: "home", label: "Home" },
    { id: "projects", label: "Projects" },
    { id: "experience", label: "Experience" },
    { id: "skills", label: "Skills" },
    { id: "contact", label: "Contact" },
    { id: "blog", label: "Blog" },
    { id: "account", label: "Account" }
  ];
  const LANGS = ["en", "tr"];
  const THEME_ICONS = {
    sun: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" stroke="currentColor" stroke-width="2" fill="none"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="3" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="21"/><line x1="3" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="21" y2="12"/><line x1="5.6" y1="5.6" x2="7.1" y2="7.1"/><line x1="16.9" y1="16.9" x2="18.4" y2="18.4"/><line x1="5.6" y1="18.4" x2="7.1" y2="16.9"/><line x1="16.9" y1="7.1" x2="18.4" y2="5.6"/></g></svg>',
    moon: '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 14.5a8.5 8.5 0 1 1-10.5-10 6.5 6.5 0 1 0 10.5 10Z"/></svg>'
  };

  const els = {
    brand: document.querySelector("#brand"),
    reload: document.querySelector("#reload-data"),
    importFile: document.querySelector("#import-file"),
    download: document.querySelector("#download-json"),
    saveDb: document.querySelector("#save-db"),
    status: document.querySelector("#status-line"),
    panel: document.querySelector("#panel"),
    hero: document.querySelector(".hero"),
    themeToggle: document.querySelector("#theme-toggle")
  };

  const setStatus = (msg, isError = false) => {
    if (els.status) {
      els.status.textContent = msg || "";
      els.status.style.color = isError ? "var(--accent)" : "inherit";
    }
  };

  const markDirty = (msg) => {
    state.dirty = true;
    setStatus(msg || "Unsaved changes");
  };

  const apiFetch = async (url, opts = {}) => {
    const res = await fetch(url, { credentials: "include", ...opts });
    if (res.status === 401) {
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
    return res;
  };

  const defaultTranslation = () => ({
    nav: { items: [], cvLabel: "" },
    heroLinks: [],
    contactLinks: [],
    hero: { kicker: "", line: "", body1: "", body2: "", bodies: [] },
    work: { title: "", sub: "", workLinkLabel: "", items: [] },
    experience: { title: "", sub: "", items: [] },
    skills: { title: "", sub: "", education: { title: "", meta: "" }, groups: [] },
    contact: { title: "", sub: "", line1: "" },
    blogCopy: { title: "", sub: "", empty: "", draftLabel: "", publishedLabel: "", backToList: "" }
  });

  const ensureTranslationShape = (t) => {
    if (!t) return;
    t.nav = t.nav || { items: [], cvLabel: "" };
    t.nav.items = Array.isArray(t.nav.items) ? t.nav.items : [];
    t.heroLinks = Array.isArray(t.heroLinks) ? t.heroLinks : [];
    t.contactLinks = Array.isArray(t.contactLinks) ? t.contactLinks : [];
    t.hero = t.hero || { kicker: "", line: "", body1: "", body2: "", bodies: [] };
    t.hero.bodies = Array.isArray(t.hero.bodies) ? t.hero.bodies : [];
    if ((!t.hero.bodies || !t.hero.bodies.length) && (t.hero.body1 || t.hero.body2)) {
      const bodies = [];
      if (t.hero.body1) bodies.push(t.hero.body1);
      if (t.hero.body2) bodies.push(t.hero.body2);
      t.hero.bodies = bodies;
    }
    t.work = t.work || { title: "", sub: "", workLinkLabel: "", items: [] };
    t.work.items = Array.isArray(t.work.items) ? t.work.items : [];
    t.experience = t.experience || { title: "", sub: "", items: [] };
    t.experience.items = Array.isArray(t.experience.items) ? t.experience.items : [];
    t.skills = t.skills || { title: "", sub: "", education: { title: "", meta: "" }, groups: [] };
    t.skills.education = t.skills.education || { title: "", meta: "" };
    t.skills.groups = Array.isArray(t.skills.groups) ? t.skills.groups : [];
    t.contact = t.contact || { title: "", sub: "", line1: "" };
    t.blogCopy = t.blogCopy || { title: "", sub: "", empty: "", draftLabel: "", publishedLabel: "", backToList: "" };
  };

  const ensureDataShape = () => {
    state.data = state.data || {};
    state.data.site = state.data.site || { brand: "", cvPath: "", cvPathTr: "", email: "", profilePicture: "", favicon: "", siteUrl: "" };
    state.data.site.profilePicture = state.data.site.profilePicture || "";
    state.data.site.favicon = state.data.site.favicon || "";
    state.data.site.siteUrl = state.data.site.siteUrl || "";
    state.data.translations = state.data.translations || {};
    LANGS.forEach((code) => {
      if (!state.data.translations[code]) state.data.translations[code] = defaultTranslation();
      ensureTranslationShape(state.data.translations[code]);
    });
    state.data.blogPosts = Array.isArray(state.data.blogPosts) ? state.data.blogPosts : [];
  };

  const getLanguages = () => LANGS;

  const parseLines = (value) => (value || "").split("\n").map((v) => v.trim()).filter(Boolean);

  const createField = (label, value, onInput, opts = {}) => {
    const row = document.createElement("div");
    row.className = "field-row";
    const lbl = document.createElement("div");
    lbl.className = "field-label";
    lbl.textContent = label;
    const inputWrap = document.createElement("div");
    inputWrap.className = "field-input";
    const input = opts.multiline || opts.type === "textarea" ? document.createElement("textarea") : document.createElement("input");
    input.type = opts.type || "text";
    input.value = value ?? "";
    input.placeholder = opts.placeholder || "";
    if (opts.rows) input.rows = opts.rows;
    input.addEventListener("input", (e) => onInput(e.target.value));
    inputWrap.appendChild(input);
    row.append(lbl, inputWrap);
    return row;
  };

  const createTextListField = (label, arr, onChange) => {
    return createField(label, (arr || []).join("\n"), (val) => onChange(parseLines(val)), { multiline: true, rows: 4 });
  };

  const createUploadField = (label, accept, onChange) => {
    const row = document.createElement("div");
    row.className = "field-row";
    const lbl = document.createElement("div");
    lbl.className = "field-label";
    lbl.textContent = label;
    const inputWrap = document.createElement("div");
    inputWrap.className = "field-input";
    const input = document.createElement("input");
    input.type = "file";
    input.accept = accept;
    input.addEventListener("change", (e) => {
      const file = e.target.files?.[0];
      if (file) onChange(file);
    });
    inputWrap.appendChild(input);
    row.append(lbl, inputWrap);
    return row;
  };

  const createButton = (label, className, onClick) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = className;
    btn.textContent = label;
    btn.addEventListener("click", (e) => {
      if (btn) animateClick(btn);
      onClick(e);
    });
    return btn;
  };

  const animateClick = (el) => {
    if (!el) return;
    el.classList.remove("click-active");
    void el.offsetWidth; // force reflow
    el.classList.add("click-active");
    setTimeout(() => el.classList.remove("click-active"), 220);
  };

  const animatePanel = () => {
    if (!els.panel) return;
    els.panel.classList.remove("slide-in");
    void els.panel.offsetWidth;
    els.panel.classList.add("slide-in");
  };

  const createWysiwyg = (label, value, onInput) => {
    const row = document.createElement("div");
    row.className = "field-row";
    const lbl = document.createElement("div");
    lbl.className = "field-label";
    lbl.textContent = label;
    const wrap = document.createElement("div");
    wrap.className = "field-input";
    const bar = document.createElement("div");
    bar.className = "wysiwyg-toolbar";
    const area = document.createElement("div");
    area.className = "wysiwyg-area";
    area.contentEditable = "true";
    area.innerHTML = value || "";
    const cmds = [
      { t: "B", c: "bold" },
      { t: "I", c: "italic" },
      { t: "U", c: "underline" },
      { t: "H2", c: "formatBlock", v: "h2" },
      { t: "H3", c: "formatBlock", v: "h3" },
      { t: "P", c: "formatBlock", v: "p" },
      { t: "UL", c: "insertUnorderedList" },
      { t: "OL", c: "insertOrderedList" },
      { t: "Link", c: "createLink" },
      { t: "Clear", c: "removeFormat" }
    ];
    cmds.forEach(({ t, c, v }) => {
      const b = createButton(t, "wys-btn", () => {
        area.focus();
        if (c === "createLink") {
          const url = prompt("Link URL", "https://");
          if (!url) return;
          document.execCommand(c, false, url);
        } else if (c === "formatBlock") {
          document.execCommand(c, false, v);
        } else {
          document.execCommand(c, false, null);
        }
        area.dispatchEvent(new Event("input"));
      });
      bar.appendChild(b);
    });
    area.addEventListener("input", () => onInput(area.innerHTML));
    wrap.append(bar, area);
    row.append(lbl, wrap);
    return row;
  };

  const syncHeroBodies = () => {
    if (!state.data || !state.data.translations) return;
    Object.values(state.data.translations).forEach((t) => {
      ensureTranslationShape(t);
      const bodies = Array.isArray(t.hero.bodies) ? t.hero.bodies : [];
      t.hero.body1 = bodies[0] || "";
      t.hero.body2 = bodies[1] || "";
    });
  };

  const getPreferredTheme = () => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    const desired = theme === "dark" ? "dark" : "light";
    document.documentElement.classList.remove("theme-light", "theme-dark");
    document.documentElement.classList.add(desired === "dark" ? "theme-dark" : "theme-light");
    document.documentElement.style.colorScheme = desired;
    localStorage.setItem("theme", desired);
    if (els.themeToggle) {
      els.themeToggle.innerHTML = desired === "dark" ? THEME_ICONS.moon : THEME_ICONS.sun;
      els.themeToggle.setAttribute("aria-label", desired === "dark" ? "Switch to light mode" : "Switch to dark mode");
    }
  };

  const uploadCv = async (lang, file) => {
    if (!file) return;
    setStatus(`Uploading CV (${lang.toUpperCase()}) …`);
    const fd = new FormData();
    fd.append("lang", lang);
    fd.append("file", file);
    try {
      const res = await apiFetch("/api/upload-cv", { method: "POST", body: fd });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || `Upload failed (${lang})`);
      state.data.site = state.data.site || {};
      if (lang === "en") state.data.site.cvPath = json.path || state.data.site.cvPath;
      else state.data.site.cvPathTr = json.path || state.data.site.cvPathTr;
      setStatus(`Uploaded CV (${lang.toUpperCase()})`);
    } catch (err) {
      console.error(err);
      setStatus(err.message || "Upload failed", true);
    }
  };

  const renderTabs = () => {
    const holder = document.querySelector(".main-tabs");
    if (!holder) return;
    holder.innerHTML = "";
    sections.forEach((sec) => {
      const btn = createButton(sec.label, `nav-cv tab ${state.section === sec.id ? "active" : ""}`, () => {
        state.section = sec.id;
        renderTabs();
        renderLangTabs();
        renderPanel();
        animatePanel();
      });
      btn.setAttribute("data-tab", sec.id);
      holder.appendChild(btn);
    });
  };

  const renderLangTabs = () => {
    const holder = document.querySelector(".lang-tabs");
    if (!holder || !state.data) return;
    const langs = getLanguages();
    holder.innerHTML = "";
    langs.forEach((code) => {
      const btn = createButton(code.toUpperCase(), `nav-cv tab ${state.lang === code ? "active" : ""}`, () => {
        state.lang = code;
        localStorage.setItem("admin-lang", code);
        renderLangTabs();
        renderPanel();
        animatePanel();
      });
      holder.appendChild(btn);
    });
  };

  const renderList = (items, renderItem, addLabel, onAdd) => {
    const frag = document.createDocumentFragment();
    items.forEach((item, idx) => {
      const block = document.createElement("details");
      block.className = "line-item";
      block.open = false;
      const summary = document.createElement("summary");
      summary.className = "item-head";
      const title = document.createElement("div");
      title.className = "item-title";
      title.textContent = renderItem.title(item, idx);
      const actions = document.createElement("div");
      actions.className = "list-actions";
      const edit = createButton("Edit", "edit-btn", () => {
        const bodyEl = block.querySelector(".item-body");
        if (!bodyEl) return;
        const isOpen = block.classList.contains("is-open");
        if (isOpen) {
          const closing = () => {
            bodyEl.removeEventListener("transitionend", closing);
            block.classList.remove("is-open");
            block.open = false;
            bodyEl.style.maxHeight = "";
          };
          bodyEl.style.maxHeight = `${bodyEl.scrollHeight}px`;
          void bodyEl.offsetHeight;
          requestAnimationFrame(() => {
            bodyEl.style.maxHeight = "0px";
          });
          bodyEl.addEventListener("transitionend", closing);
        } else {
          const opened = () => {
            bodyEl.removeEventListener("transitionend", opened);
            // keep height set so closing animates smoothly next time
          };
          block.classList.add("is-open");
          block.open = true;
          // measure natural height even after previous transitions
          bodyEl.style.maxHeight = "none";
          const fullHeight = bodyEl.scrollHeight;
          bodyEl.style.maxHeight = "0px";
          void bodyEl.offsetHeight;
          bodyEl.style.maxHeight = `${fullHeight}px`;
          bodyEl.addEventListener("transitionend", opened);
        }
        animateClick(block);
      });
      const del = createButton("Remove", "lang-toggle", () => {
        renderItem.onRemove(idx);
        markDirty("Removed item");
        renderPanel();
      });
      actions.append(edit, del);
      summary.addEventListener("click", (e) => {
        if (!e.target.closest(".edit-btn")) {
          e.preventDefault();
        }
      });
      summary.append(title, actions);
      block.appendChild(summary);
      const bodyWrap = document.createElement("div");
      bodyWrap.className = "item-body";
      renderItem.body(item, idx, bodyWrap);
      block.appendChild(bodyWrap);
      frag.appendChild(block);
    });
    const add = createButton(addLabel, "nav-cv", () => {
      onAdd();
      markDirty(addLabel);
      animateClick(add);
      renderPanel();
    });
    frag.appendChild(add);
    return frag;
  };

  const renderAccount = (panel) => {
    const wrapper = document.createElement("div");
    wrapper.className = "line-item";
    wrapper.style.padding = "16px";
    const title = document.createElement("div");
    title.className = "admin-section-title";
    title.textContent = "Account";
    title.style.marginTop = "0";
    wrapper.appendChild(title);

    const cardTitle = document.createElement("div");
    cardTitle.className = "item-title";
    cardTitle.textContent = "Change password";
    cardTitle.style.margin = "6px 0 12px";
    wrapper.appendChild(cardTitle);

    const pwdState = { current: "", next: "", confirm: "" };
    wrapper.append(
      createField("Current password", "", (v) => (pwdState.current = v), { type: "password" }),
      createField("New password", "", (v) => (pwdState.next = v), {
        type: "password",
        placeholder: "At least 8 characters"
      }),
      createField("Confirm new password", "", (v) => (pwdState.confirm = v), { type: "password" })
    );

    const actions = document.createElement("div");
    actions.className = "list-actions";
    actions.style.justifyContent = "flex-end";
    actions.style.marginTop = "10px";

    const resetBtn = createButton("Clear", "lang-toggle", () => {
      pwdState.current = "";
      pwdState.next = "";
      pwdState.confirm = "";
      wrapper.querySelectorAll("input").forEach((input) => (input.value = ""));
      setStatus("Cleared password fields");
    });

    const submitBtn = createButton("Update password", "nav-cv", async () => {
      if (!pwdState.current || !pwdState.next || !pwdState.confirm) {
        setStatus("Please fill all password fields", true);
        return;
      }
      if (pwdState.next !== pwdState.confirm) {
        setStatus("New password and confirmation must match", true);
        return;
      }
      if (pwdState.next.length < 8) {
        setStatus("New password must be at least 8 characters", true);
        return;
      }
      setStatus("Updating password …");
      try {
        const res = await apiFetch("/api/change-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_password: pwdState.current,
            new_password: pwdState.next,
            confirm_password: pwdState.confirm
          })
        });
        const json = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(json.error || `Status ${res.status}`);
        setStatus("Password updated");
        resetBtn.click();
      } catch (err) {
        console.error(err);
        setStatus(err.message || "Password update failed", true);
      }
    });

    actions.append(resetBtn, submitBtn);
    wrapper.append(actions);
    panel.append(wrapper);
  };

  const renderHome = (panel, t, site) => {
    const sectionLabel = (text) => {
      const lbl = document.createElement("div");
      lbl.className = "admin-section-title";
      lbl.textContent = text;
      panel.appendChild(lbl);
    };

    sectionLabel("Site basics");
    panel.append(
      createField("Brand", site.brand || "", (v) => {
        site.brand = v;
        if (els.brand) els.brand.textContent = `${v || "Admin"} · Admin`;
        markDirty();
      }),
      createField("Email", site.email || "", (v) => {
        site.email = v;
        markDirty();
      }),
      createField("Site URL (canonical)", site.siteUrl || "", (v) => {
        site.siteUrl = v;
        markDirty("Updated site URL");
      }),
      createField("CV path (EN)", site.cvPath || "", (v) => {
        site.cvPath = v;
        markDirty();
      }),
      createField("CV path (TR)", site.cvPathTr || "", (v) => {
        site.cvPathTr = v;
        markDirty();
      }),
      createField("Nav CV Label", t.nav.cvLabel || "", (v) => {
        t.nav.cvLabel = v;
        markDirty();
      })
    );

    sectionLabel("Navigation");
    const navList = renderList(
      t.nav.items,
      {
        title: (item, idx) => item.label || `Link ${idx + 1}`,
        onRemove: (idx) => t.nav.items.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Label", item.label || "", (v) => {
              item.label = v;
              markDirty();
            }),
            createField("Href", item.href || "", (v) => {
              item.href = v;
              markDirty();
            })
          );
        }
      },
      "Add nav link",
      () => t.nav.items.push({ href: "#", label: "New" })
    );
    panel.append(navList);

    sectionLabel("Uploads");
    panel.append(
      createUploadField("CV (English)", "application/pdf", (file) => uploadCv("en", file)),
      createUploadField("CV (Turkish)", "application/pdf", (file) => uploadCv("tr", file))
    );

    sectionLabel("Hero");
    panel.append(
      createField("Hero kicker", t.hero.kicker || "", (v) => {
        t.hero.kicker = v;
        markDirty();
      }),
      createWysiwyg("Hero line (HTML)", t.hero.line || "", (v) => {
        t.hero.line = v;
        markDirty();
      })
    );

    const heroBodies = renderList(
      t.hero.bodies,
      {
        title: (_item, idx) => `Body ${idx + 1}`,
        onRemove: (idx) => t.hero.bodies.splice(idx, 1),
        body: (_item, idx, body) => {
          body.append(
            createWysiwyg("Body (HTML)", t.hero.bodies[idx] || "", (v) => {
              t.hero.bodies[idx] = v;
              // keep legacy fields in sync for compatibility
              t.hero.body1 = t.hero.bodies[0] || "";
              t.hero.body2 = t.hero.bodies[1] || "";
              markDirty();
            })
          );
        }
      },
      "Add hero body",
      () => {
        t.hero.bodies.push("");
        markDirty();
      }
    );
    panel.append(heroBodies);

    sectionLabel("Hero links");
    const heroLinks = renderList(
      t.heroLinks,
      {
        title: (item, idx) => item.label || `Link ${idx + 1}`,
        onRemove: (idx) => t.heroLinks.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Id", item.id || "", (v) => {
              item.id = v;
              markDirty();
            }),
            createField("Label", item.label || "", (v) => {
              item.label = v;
              markDirty();
            }),
            createField("URL", item.url || "", (v) => {
              item.url = v;
              markDirty();
            }),
            createField("Icon", item.icon || "", (v) => {
              item.icon = v;
              markDirty();
            }),
            createField("Download (true/false)", item.download ? "true" : "false", (v) => {
              item.download = v === "true";
              markDirty();
            })
          );
        }
      },
      "Add hero link",
      () => t.heroLinks.push({ id: "link", label: "New link", url: "#", icon: "", download: false })
    );
    panel.append(heroLinks);

    sectionLabel("Footer / contact links");
    const footerLinks = renderList(
      t.contactLinks,
      {
        title: (item, idx) => item.label || `Footer link ${idx + 1}`,
        onRemove: (idx) => t.contactLinks.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Label", item.label || "", (v) => {
              item.label = v;
              markDirty();
            }),
            createField("URL", item.url || "", (v) => {
              item.url = v;
              markDirty();
            }),
            createField("Icon", item.icon || "", (v) => {
              item.icon = v;
              markDirty();
            })
          );
        }
      },
      "Add footer link",
      () => t.contactLinks.push({ label: "New link", url: "#", icon: "" })
    );
    panel.append(footerLinks);
  };

  const renderProjects = (panel, t) => {
    panel.append(
      createField("Projects title", t.work.title || "", (v) => {
        t.work.title = v;
        markDirty();
      }),
      createField("Projects subtitle", t.work.sub || "", (v) => {
        t.work.sub = v;
        markDirty();
      }),
      createField("Project link label", t.work.workLinkLabel || "", (v) => {
        t.work.workLinkLabel = v;
        markDirty();
      })
    );

    const list = renderList(
      t.work.items,
      {
        title: (item, idx) => item.title || `Project ${idx + 1}`,
        onRemove: (idx) => t.work.items.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Title", item.title || "", (v) => {
              item.title = v;
              markDirty();
            }),
            createField("Meta", item.meta || "", (v) => {
              item.meta = v;
              markDirty();
            }),
            createField("Brief", item.brief || "", (v) => {
              item.brief = v;
              markDirty();
            }, { multiline: true, rows: 3 }),
            createField("Detail", item.detail || "", (v) => {
              item.detail = v;
              markDirty();
            }, { multiline: true, rows: 4 }),
            createTextListField("Tags", item.tags || [], (v) => {
              item.tags = v;
              markDirty();
            }),
            createField("Link", item.link || "", (v) => {
              item.link = v;
              markDirty();
            })
          );
        }
      },
      "Add project",
      () =>
        t.work.items.push({
          title: "New project",
          meta: "",
          brief: "",
          detail: "",
          tags: [],
          link: ""
        })
    );
    panel.append(list);
  };

  const renderExperience = (panel, t) => {
    panel.append(
      createField("Experience title", t.experience.title || "", (v) => {
        t.experience.title = v;
        markDirty();
      }),
      createField("Experience subtitle", t.experience.sub || "", (v) => {
        t.experience.sub = v;
        markDirty();
      })
    );
    const list = renderList(
      t.experience.items,
      {
        title: (item, idx) => item.company || `Role ${idx + 1}`,
        onRemove: (idx) => t.experience.items.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Company", item.company || "", (v) => {
              item.company = v;
              markDirty();
            }),
            createField("Role", item.role || "", (v) => {
              item.role = v;
              markDirty();
            }),
            createField("Date", item.date || "", (v) => {
              item.date = v;
              markDirty();
            }),
            createField("Description", item.desc || "", (v) => {
              item.desc = v;
              markDirty();
            }, { multiline: true, rows: 3 }),
            createTextListField("Bullets", item.bullets || [], (v) => {
              item.bullets = v;
              markDirty();
            })
          );
        }
      },
      "Add experience",
      () => t.experience.items.push({ company: "Company", role: "", date: "", desc: "", bullets: [] })
    );
    panel.append(list);
  };

  const renderSkills = (panel, t) => {
    panel.append(
      createField("Skills title", t.skills.title || "", (v) => {
        t.skills.title = v;
        markDirty();
      }),
      createField("Skills subtitle", t.skills.sub || "", (v) => {
        t.skills.sub = v;
        markDirty();
      }),
      createField("Education title", t.skills.education.title || "", (v) => {
        t.skills.education.title = v;
        markDirty();
      }),
      createField("Education meta", t.skills.education.meta || "", (v) => {
        t.skills.education.meta = v;
        markDirty();
      })
    );
    const list = renderList(
      t.skills.groups,
      {
        title: (item, idx) => item.label || `Group ${idx + 1}`,
        onRemove: (idx) => t.skills.groups.splice(idx, 1),
        body: (item, idx, body) => {
          body.append(
            createField("Label", item.label || "", (v) => {
              item.label = v;
              markDirty();
            }),
            createField("Text", item.text || "", (v) => {
              item.text = v;
              markDirty();
            }, { multiline: true, rows: 3 })
          );
        }
      },
      "Add group",
      () => t.skills.groups.push({ label: "New group", text: "" })
    );
    panel.append(list);
  };

  const renderContact = (panel, t, site) => {
    panel.append(
      createField("Contact title", t.contact.title || "", (v) => {
        t.contact.title = v;
        markDirty();
      }),
      createField("Contact subtitle", t.contact.sub || "", (v) => {
        t.contact.sub = v;
        markDirty();
      }),
      createField("Line", t.contact.line1 || "", (v) => {
        t.contact.line1 = v;
        markDirty();
      }, { multiline: true, rows: 3 }),
      createField("Email", site.email || "", (v) => {
        site.email = v;
        markDirty();
      })
    );
  };

  const renderBlog = (panel, t) => {
    panel.append(
      createField("Blog title", t.blogCopy.title || "", (v) => {
        t.blogCopy.title = v;
        markDirty();
      }),
      createField("Blog subtitle", t.blogCopy.sub || "", (v) => {
        t.blogCopy.sub = v;
        markDirty();
      }),
      createField("Empty label", t.blogCopy.empty || "", (v) => {
        t.blogCopy.empty = v;
        markDirty();
      }),
      createField("Draft label", t.blogCopy.draftLabel || "", (v) => {
        t.blogCopy.draftLabel = v;
        markDirty();
      }),
      createField("Published label", t.blogCopy.publishedLabel || "", (v) => {
        t.blogCopy.publishedLabel = v;
        markDirty();
      }),
      createField("Back to list", t.blogCopy.backToList || "", (v) => {
        t.blogCopy.backToList = v;
        markDirty();
      })
    );

    const posts = renderList(
      state.data.blogPosts,
      {
        title: (item, idx) => item.slug || item.id || `Post ${idx + 1}`,
        onRemove: (idx) => state.data.blogPosts.splice(idx, 1),
        body: (item, idx, body) => {
          item.id = item.id || `post-${Date.now()}`;
          item.slug = item.slug || item.id;
          item.tags = Array.isArray(item.tags) ? item.tags : [];
          item.lang = item.lang || {};
          getLanguages().forEach((code) => {
            if (!item.lang[code]) item.lang[code] = { title: "", summary: "", body: "" };
          });
          body.append(
            createField("Id", item.id, (v) => {
              item.id = v;
              markDirty();
            }),
            createField("Slug", item.slug, (v) => {
              item.slug = v;
              markDirty();
            }),
            createField("Date (YYYY-MM-DD)", item.date || "", (v) => {
              item.date = v;
              markDirty();
            }),
            createTextListField("Tags", item.tags, (v) => {
              item.tags = v;
              markDirty();
            }),
            createField("Published (true/false)", item.published ? "true" : "false", (v) => {
              item.published = v === "true";
              markDirty();
            })
          );
          const langWrap = document.createElement("div");
          langWrap.className = "lang-subwrap";
          Object.keys(item.lang).forEach((code) => {
            const langBlock = document.createElement("div");
            langBlock.className = "line-item nested";
            const title = document.createElement("div");
            title.className = "item-title";
            title.textContent = code.toUpperCase();
            langBlock.appendChild(title);
            langBlock.appendChild(
              createField("Title", item.lang[code].title || "", (v) => {
                item.lang[code].title = v;
                markDirty();
              })
            );
            langBlock.appendChild(
              createField("Summary", item.lang[code].summary || "", (v) => {
                item.lang[code].summary = v;
                markDirty();
              }, { multiline: true, rows: 3 })
            );
            langBlock.appendChild(
              createWysiwyg("Body", item.lang[code].body || "", (v) => {
                item.lang[code].body = v;
                markDirty();
              })
            );
            langWrap.appendChild(langBlock);
          });
          body.appendChild(langWrap);
        }
      },
      "Add post",
      () => {
        const langObj = {};
        getLanguages().forEach((code) => {
          langObj[code] = { title: "", summary: "", body: "" };
        });
        state.data.blogPosts.push({
          id: `post-${Date.now()}`,
          slug: "",
          published: false,
          tags: [],
          date: "",
          lang: langObj
        });
      }
    );
    // Mark blog items for longer animation
    posts.querySelectorAll && posts.querySelectorAll(".line-item").forEach((el) => el.classList.add("blog-item"));
    panel.append(posts);
  };

  const renderPanel = () => {
    if (!state.data || !els.panel) return;
    const panel = els.panel;
    panel.innerHTML = "";
    const t = state.data.translations[state.lang] || defaultTranslation();
    ensureTranslationShape(t);
    const site = state.data.site;
    if (state.section === "home") renderHome(panel, t, site);
    if (state.section === "projects") renderProjects(panel, t);
    if (state.section === "experience") renderExperience(panel, t);
    if (state.section === "skills") renderSkills(panel, t);
    if (state.section === "contact") renderContact(panel, t, site);
    if (state.section === "blog") renderBlog(panel, t);
    if (state.section === "account") renderAccount(panel);
  };

  const bootstrapEmpty = () => {
    state.data = { site: { brand: "", cvPath: "", cvPathTr: "", email: "" }, translations: { en: defaultTranslation(), tr: defaultTranslation() }, blogPosts: [] };
    ensureDataShape();
    renderTabs();
    renderLangTabs();
    renderPanel();
  };

  const loadFromServer = async () => {
    setStatus("Loading content …");
    try {
      const res = await apiFetch("/api/content", { cache: "no-cache" });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      state.data = json;
      ensureDataShape();
      if (!getLanguages().includes(state.lang)) state.lang = getLanguages()[0] || "en";
      if (els.brand) els.brand.textContent = `${state.data.site.brand || "Admin"} · Admin`;
      renderTabs();
      renderLangTabs();
      renderPanel();
      state.dirty = false;
      setStatus("Loaded");
    } catch (err) {
      console.error(err);
      setStatus(`Load failed: ${err.message}`);
      bootstrapEmpty();
    }
  };

  const importFromFile = (file) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(reader.result);
        state.data = parsed;
        ensureDataShape();
        renderTabs();
        renderLangTabs();
        renderPanel();
        markDirty("Imported JSON");
      } catch (err) {
        setStatus(`Import failed: ${err.message}`);
      }
    };
    reader.readAsText(file);
  };

  const saveToDatabase = async () => {
    if (!state.data) return;
    syncHeroBodies();
    setStatus("Saving to SQLite …");
    try {
      const res = await apiFetch("/api/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state.data)
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      state.dirty = false;
      setStatus("Saved to SQLite");
    } catch (err) {
      console.error(err);
      setStatus(`Save failed: ${err.message}`);
    }
  };

  const exportJson = async () => {
    if (!state.data) return;
    syncHeroBodies();
    setStatus("Exporting JSON …");
    try {
      const res = await apiFetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: state.data })
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "content.json";
      a.click();
      URL.revokeObjectURL(url);
      state.dirty = false;
      setStatus("Exported content.json");
    } catch (err) {
      console.error(err);
      setStatus(`Export failed: ${err.message}`);
    }
  };

  const bind = () => {
    if (els.reload) els.reload.onclick = () => loadFromServer();
    if (els.importFile) {
      els.importFile.addEventListener("change", (e) => {
        const file = e.target.files?.[0];
        if (file) importFromFile(file);
      });
    }
    if (els.download) els.download.onclick = exportJson;
    if (els.saveDb) els.saveDb.onclick = saveToDatabase;
    if (els.themeToggle) {
      els.themeToggle.onclick = () => {
        const next = document.documentElement.classList.contains("theme-dark") ? "light" : "dark";
        applyTheme(next);
      };
    }
  };

  const init = () => {
    applyTheme(getPreferredTheme());
    bind();
    bootstrapEmpty();
    loadFromServer();
    animatePanel();
  };

  document.addEventListener("DOMContentLoaded", init);
})();
