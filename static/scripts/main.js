// SPDX-FileCopyrightText: 2026 Bora Yarkın
// SPDX-License-Identifier: GPL-3.0-only

(() => {
  const ICONS = {
    download:
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a1 1 0 0 1 1 1v10.59l2.29-2.3a1 1 0 1 1 1.42 1.42l-4 4a1 1 0 0 1-1.42 0l-4-4a1 1 0 0 1 1.42-1.42L11 14.59V4a1 1 0 0 1 1-1Zm-6 16a1 1 0 1 1 0-2h12a1 1 0 1 1 0 2H6Z"/></svg>',
    mail:
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 5h17a1.5 1.5 0 0 1 1.5 1.5v11A1.5 1.5 0 0 1 20.5 19h-17A1.5 1.5 0 0 1 2 17.5v-11A1.5 1.5 0 0 1 3.5 5Zm0 2v.27l8 5.03 8-5.03V7h-16Zm16 8.5v-6.4l-7.48 4.7a1 1 0 0 1-1.04 0L3.5 9.1v6.4h16Z"/></svg>',
    linkedin:
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.43c0-1.29-.02-2.96-1.8-2.96-1.8 0-2.07 1.4-2.07 2.86v5.53H9.48V9h3.4v1.56h.05c.47-.89 1.63-1.83 3.35-1.83 3.58 0 4.24 2.35 4.24 5.4v6.32ZM5.34 7.43a2.06 2.06 0 1 1 0-4.11 2.06 2.06 0 0 1 0 4.11ZM7.12 20.45H3.56V9h3.56v11.45ZM22.23 0H1.77C.8 0 0 .78 0 1.73v20.54C0 23.22.8 24 1.77 24h20.46c.97 0 1.77-.78 1.77-1.73V1.73C24 .78 23.2 0 22.23 0Z"/></svg>',
    github:
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .5C5.73.5.5 5.74.5 12.02c0 5.1 3.29 9.43 7.86 10.96.58.11.79-.25.79-.56 0-.28-.01-1.02-.02-2-3.2.69-3.88-1.54-3.88-1.54-.53-1.36-1.3-1.72-1.3-1.72-1.06-.73.08-.72.08-.72 1.17.08 1.78 1.2 1.78 1.2 1.04 1.79 2.74 1.27 3.41.97.11-.75.41-1.27.74-1.56-2.55-.29-5.23-1.28-5.23-5.69 0-1.26.45-2.29 1.19-3.09-.12-.29-.52-1.45.11-3.02 0 0 .97-.31 3.18 1.18a11.05 11.05 0 0 1 5.8 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.57.23 2.73.11 3.02.74.8 1.19 1.83 1.19 3.09 0 4.43-2.68 5.39-5.24 5.67.42.36.8 1.08.8 2.18 0 1.57-.02 2.84-.02 3.22 0 .31.21.68.8.56A10.53 10.53 0 0 0 23.5 12C23.5 5.74 18.27.5 12 .5Z"/></svg>',
    instagram:
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7Zm5 3.8A4.2 4.2 0 1 1 7.8 12 4.2 4.2 0 0 1 12 7.8Zm0 2A2.2 2.2 0 1 0 14.2 12 2.2 2.2 0 0 0 12 9.8Zm5.25-4.05a1.15 1.15 0 1 1-1.15 1.15 1.15 1.15 0 0 1 1.15-1.15Z"/></svg>'
  };

  const BLOG_PAGE_SIZE = 4;
  const normalizeAssetPath = (path) => {
    if (!path) return "";
    const trimmed = path.trim();
    if (/^https?:\/\//i.test(trimmed)) return trimmed;
    if (trimmed.startsWith("/assets/") || trimmed.startsWith("/uploads/")) return trimmed;
    if (trimmed.startsWith("/")) return trimmed;
    if (trimmed.startsWith("assets/") || trimmed.startsWith("uploads/")) return `/${trimmed}`;
    return `/assets/${trimmed}`;
  };
  const initialLang = document.documentElement.lang || localStorage.getItem("lang") || "en";
  const state = {
    data: null,
    lang: initialLang,
    view: "site",
    currentPost: null,
    blogPage: 1,
    lastBlogScroll: 0
  };

  const selectors = {
    brand: "#brand",
    navLinks: "#nav-links",
    navCv: ".nav-cv",
    heroLinks: "#hero-links",
    contactEmail: "#contact-email",
    contactSocial: "#contact-social",
    workList: "#work-list",
    timeline: "#timeline",
    skillsList: "#skills-list",
    education: "#education",
    year: "#year",
    footerName: "#footer-name",
    langToggle: ".lang-toggle",
    themeToggle: ".theme-toggle",
    blogTitle: "#blog-title",
    blogSub: "#blog-sub",
    blogList: "#blog-list",
    blogEmpty: "#blog-empty",
    blogArticleWrap: "#blog-article-wrap",
    blogArticle: "#blog-article",
    blogBack: "#blog-back",
    blogBackBottom: "#blog-back-bottom",
    siteView: "#site-view",
    blogView: "#blog-view",
    blogPager: "#blog-pager",
    blogListWrap: ".blog-list-wrap",
    blogPageLabel: "#page-label",
    blogPagePrev: "#page-prev",
    blogPageNext: "#page-next",
    blogLoader: "#blog-loader"
  };

  const els = Object.fromEntries(Object.entries(selectors).map(([key, sel]) => [key, document.querySelector(sel)]));
  const pageEl = document.querySelector(".page");
  let langReadyForEffect = false;

  const stripTags = (value) => {
    if (!value) return "";
    const temp = document.createElement("div");
    temp.innerHTML = value;
    return temp.textContent || temp.innerText || "";
  };

  const setText = (selector, value, isHtml = false) => {
    const el = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!el || value === undefined || value === null) return;
    if (isHtml) el.innerHTML = value;
    else el.textContent = value;
  };

  const getPreferredTheme = () => {
    const stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    const root = document.documentElement;
    const desired = theme === "dark" ? "dark" : "light";
    root.classList.remove("theme-light", "theme-dark");
    root.classList.add(desired === "dark" ? "theme-dark" : "theme-light");
    root.style.colorScheme = desired;
    localStorage.setItem("theme", desired);
    if (els.themeToggle) {
      const sunIcon =
        '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" stroke="currentColor" stroke-width="2" fill="none"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="3" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="21"/><line x1="3" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="21" y2="12"/><line x1="5.6" y1="5.6" x2="7.1" y2="7.1"/><line x1="16.9" y1="16.9" x2="18.4" y2="18.4"/><line x1="5.6" y1="18.4" x2="7.1" y2="16.9"/><line x1="16.9" y1="7.1" x2="18.4" y2="5.6"/></g></svg>';
      const moonIcon = '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 14.5a8.5 8.5 0 1 1-10.5-10 6.5 6.5 0 1 0 10.5 10Z"/></svg>';
      els.themeToggle.innerHTML = desired === "dark" ? moonIcon : sunIcon;
      els.themeToggle.setAttribute("aria-pressed", desired === "dark");
    }
  };

  const getIcon = (id) => ICONS[id] || "";

  const loadContent = async () => {
    if (window.__CONTENT__) return window.__CONTENT__;
    const sources = ["/api/content", "/assets/content.json", "/assets/demo/demo.json"];
    let lastError = null;
    for (const url of sources) {
      try {
        const res = await fetch(url, { cache: "no-cache" });
        if (res.ok) return res.json();
        lastError = new Error(`Content fetch failed from ${url}: ${res.status}`);
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError || new Error("Content fetch failed");
  };

  const getCvPath = (lang) => {
    const site = state.data?.site || {};
    const raw =
      lang === "tr"
        ? site.cvPathTr || site.cvTr || site.cvPath
        : site.cvPath || site.cvPathTr || site.cvTr;
    if (!raw) return "";
    if (/^https?:\/\//i.test(raw.trim())) return raw.trim();
    return `/cv/${lang}`;
  };

  const showCvModal = () => {
    const cvEn = getCvPath("en");
    const cvTr = getCvPath("tr");
    if (!cvEn && !cvTr) {
      alert(state.lang === "tr" ? "CV bulunamadı, lütfen PDF yükleyin." : "No CV found. Please upload a PDF first.");
      return;
    }
    const copy =
      state.lang === "tr"
        ? {
            title: "CV indir",
            desc: "İndirmek için dil seç.",
            en: "İngilizce",
            tr: "Türkçe",
            cancel: "İptal"
          }
        : {
            title: "Download CV",
            desc: "Choose a language to download.",
            en: "English",
            tr: "Türkçe",
            cancel: "Cancel"
          };
    const existing = document.querySelector(".modal-overlay");
    if (existing) {
      existing.hidden = false;
      requestAnimationFrame(() => {
        existing.classList.add("show");
        const existingBox = existing.querySelector(".modal");
        if (existingBox) existingBox.classList.add("show");
      });
      return;
    }
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    const box = document.createElement("div");
    box.className = "modal";
    box.innerHTML = `
      <h3>${copy.title}</h3>
      <p class="muted">${copy.desc}</p>
      <div class="modal-actions">
        ${cvEn ? `<a class="lang-toggle" href="${cvEn}" download>${copy.en}</a>` : ""}
        ${cvTr ? `<a class="lang-toggle" href="${cvTr}" download>${copy.tr}</a>` : ""}
        <button type="button" class="lang-toggle" data-close="true">${copy.cancel}</button>
      </div>
    `;
    overlay.appendChild(box);
    const closeOverlay = () => {
      overlay.classList.remove("show");
      box.classList.remove("show");
      setTimeout(() => {
        overlay.remove();
      }, 180);
    };
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay || e.target.closest("[data-close='true']")) {
        closeOverlay();
      }
    });
    document.body.appendChild(overlay);
    requestAnimationFrame(() => {
      overlay.classList.add("show");
      box.classList.add("show");
    });
  };

  const renderNav = (items, cvLabel) => {
    if (!els.navLinks) return;
    els.navLinks.innerHTML = items.map((item) => `<a href="${item.href}">${item.label}</a>`).join("");
    if (els.navCv) els.navCv.textContent = cvLabel || "";

    els.navLinks.querySelectorAll("a").forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        const href = anchor.getAttribute("href") || "";
        if (href.startsWith("/blog")) {
          e.preventDefault();
          navigate("/blog");
          return;
        }
        if (href.startsWith("#")) {
          e.preventDefault();
          navigateToSection(href);
        }
      });
    });
  };

  const renderHeroLinks = (links, cvPath) => {
    if (!els.heroLinks) return;
    els.heroLinks.innerHTML = links
      .map((link) => {
        const href = link.id === "cv" ? cvPath : link.url;
        const downloadAttr = link.download ? " download" : "";
        const relAttr = link.download ? "" : ' rel="noopener noreferrer"';
        const targetAttr = link.download ? "" : ' target="_blank"';
        const iconPart = link.icon ? `${getIcon(link.icon)}` : "";
        return `<a href="${href}"${downloadAttr}${relAttr}${targetAttr}><span class="symbol">${iconPart}</span><span class="link-label">${link.label}</span></a>`;
      })
      .join("");
  };

  const renderHeroBodies = (hero) => {
    const wrap = document.querySelector("#hero-body-wrap");
    if (!wrap || !hero) return;
    const bodies = Array.isArray(hero.bodies) && hero.bodies.length
      ? hero.bodies
      : [hero.body1, hero.body2].filter(Boolean);
    wrap.innerHTML = "";
    bodies.forEach((body, idx) => {
      const p = document.createElement("p");
      p.className = "hero-body";
      p.setAttribute("data-hero-body", String(idx + 1));
      p.innerHTML = body || "";
      wrap.appendChild(p);
    });
  };

  const renderWork = (items, linkLabel) => {
    if (!els.workList) return;
    els.workList.innerHTML = "";
    items.forEach((item) => {
      const article = document.createElement("article");
      article.className = "work-item";
      article.innerHTML = `
        <div class="work-header">
          <div class="work-title">${item.title}</div>
          <div class="work-meta">${item.meta}</div>
        </div>
        <div class="work-brief">${item.brief}</div>
        <div class="work-details">
          <p>${item.detail}</p>
          <div class="work-tags">${item.tags.map((t) => `<span>${t}</span>`).join("")}</div>
          ${item.link ? `<a class="work-link" href="${item.link}" target="_blank" rel="noopener noreferrer"><span>↗</span> ${linkLabel}</a>` : ""}
        </div>
      `;
      els.workList.appendChild(article);
    });
  };

  const renderExperience = (items) => {
    if (!els.timeline) return;
    els.timeline.innerHTML = "";
    items.forEach((item) => {
      const wrap = document.createElement("div");
      wrap.className = "timeline-item";
      wrap.innerHTML = `
        <div class="timeline-title">${item.company}</div>
        <div class="timeline-role">${item.role}</div>
        <div class="timeline-date">${item.date}</div>
        <div class="timeline-details">
          <div class="timeline-desc">${item.desc}</div>
          <ul class="timeline-points">
            ${item.bullets.map((b) => `<li>${b}</li>`).join("")}
          </ul>
        </div>
      `;
      els.timeline.appendChild(wrap);
    });
  };

  const renderSkills = (skills) => {
    if (!els.skillsList || !els.education) return;
    els.education.innerHTML = `
      <div class="edu-item">
        <div class="edu-title">${skills.education.title}</div>
        <div class="edu-meta">${skills.education.meta}</div>
      </div>
    `;
    els.skillsList.innerHTML = "";
    skills.groups.forEach((group) => {
      const block = document.createElement("div");
      block.className = "skills-group";
      block.innerHTML = `
        <div class="skills-label">${group.label}</div>
        <div class="skills-text">${group.text}</div>
      `;
      els.skillsList.appendChild(block);
    });
  };

  const renderContact = (contact, site, heroLinks, contactLinks) => {
    setText("[data-i18n='contactTitle']", contact.title);
    setText("[data-i18n='contactSub']", contact.sub);
    setText("[data-i18n='contactLine1']", contact.line1);

    if (els.contactEmail) {
      els.contactEmail.textContent = site.email;
      els.contactEmail.setAttribute("href", `mailto:${site.email}`);
    }
    if (els.contactSocial) {
      const socials = contactLinks && contactLinks.length ? contactLinks : heroLinks.filter((l) => l.id !== "cv" && l.id !== "email");
      els.contactSocial.innerHTML = socials
        .map((s) => `<a href="${s.url}" target="_blank" rel="noopener noreferrer"><span class="symbol">${getIcon(s.icon)}</span><span class="link-label">${s.label}</span></a>`)
        .join("");
    }
  };

  const applyLanguage = (lang) => {
    if (!state.data) return;
    if (langReadyForEffect) {
      triggerLangTransition();
    } else {
      langReadyForEffect = true;
    }
    const locale = state.data.translations[lang] ? lang : "en";
    state.lang = locale;
    document.documentElement.lang = locale;
    localStorage.setItem("lang", locale);
    const data = state.data.translations[locale];
    const site = state.data.site;

    setText("[data-i18n='heroKicker']", data.hero.kicker);
    setText("[data-i18n='heroLine']", data.hero.line, true);
    renderHeroBodies(data.hero);
    setText("[data-i18n='workTitle']", data.work.title);
    setText("[data-i18n='workSub']", data.work.sub);
    setText("[data-i18n='expTitle']", data.experience.title);
    setText("[data-i18n='expSub']", data.experience.sub);
    setText("[data-i18n='skillsTitle']", data.skills.title);
    setText("[data-i18n='skillsSub']", data.skills.sub);
    setText("[data-i18n='contactTitle']", data.contact.title);
    setText("[data-i18n='contactSub']", data.contact.sub);
    setText("[data-i18n='contactLine1']", data.contact.line1);

    if (els.brand) els.brand.textContent = site.brand;
    if (els.footerName) els.footerName.textContent = site.brand;
    if (els.navCv) els.navCv.setAttribute("href", "#");

    renderNav(data.nav.items, data.nav.cvLabel);
    renderHeroLinks(data.heroLinks || [], getCvPath(locale));
    renderWork(data.work.items, data.work?.workLinkLabel || "");
    renderExperience(data.experience.items);
    renderSkills(data.skills);
    renderContact(data.contact, site, data.heroLinks || [], data.contactLinks || []);
    renderBlogCopy(data.blogCopy);
    state.blogPage = 1;
    renderBlogList();

    if (state.view === "site") {
      document.title = getSiteTitle();
    } else if (state.view === "blog" && data.blogCopy && data.blogCopy.title) {
      document.title = `${data.blogCopy.title} · ${site.brand || "CV + Blog"}`;
    } else if (state.view === "blog-post" && state.currentPost) {
      const langData = state.currentPost.lang[locale] || state.currentPost.lang.en || {};
      document.title = `${langData.title} · ${site.brand || "CV + Blog"}`;
    }

    if (els.langToggle) {
      els.langToggle.textContent = locale === "en" ? "TR" : "EN";
      els.langToggle.setAttribute("aria-pressed", locale !== "en");
    }
  };

  const renderBlogCopy = (copy) => {
    if (!copy) return;
    setText(els.blogTitle, copy.title);
    setText(els.blogSub, copy.sub);
  };

  const getPublishedPosts = () => {
    if (!state.data) return [];
    return (state.data.blogPosts || []).filter((p) => p.published);
  };

  const filterPosts = () => {
    return getPublishedPosts();
  };

  const triggerLangTransition = () => {
    if (!pageEl) return;
    const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;
    pageEl.classList.remove("lang-switching");
    void pageEl.offsetWidth; // force reflow
    pageEl.classList.add("lang-switching");
    setTimeout(() => pageEl.classList.remove("lang-switching"), 240);
  };

  const renderBlogList = () => {
    if (!els.blogList || !state.data) return;
    const copy = state.data.translations[state.lang]?.blogCopy;
    const posts = filterPosts();
    const total = posts.length;
    const start = 0;
    const visible = posts.slice(0, state.blogPage * BLOG_PAGE_SIZE);

    els.blogList.innerHTML = "";
    setText(els.blogEmpty, copy?.empty || "", false);

    if (!visible.length) {
      if (els.blogEmpty) els.blogEmpty.hidden = false;
      if (els.blogPager) els.blogPager.hidden = true;
      if (els.blogLoader) els.blogLoader.hidden = true;
      return;
    }
    if (els.blogEmpty) els.blogEmpty.hidden = true;

    visible.forEach((post) => {
      const langData = post.lang[state.lang] || post.lang.en || {};
      const item = document.createElement("article");
      item.className = "work-item fade-in";
      item.innerHTML = `
        <div class="work-header">
          <div class="work-title">${langData.title}</div>
          <div class="work-meta">${formatDate(post.date)}</div>
        </div>
        <div class="work-brief">${langData.summary || ""}</div>
        <div class="work-details">
          <div class="work-tags">
            ${(post.tags || []).map((t) => `<span class="pill">${t}</span>`).join("")}
          </div>
        </div>
      `;
      item.addEventListener("click", () => navigate(`/blog/${post.slug || post.id}`));
      item.addEventListener("keypress", (e) => {
        if (e.key === "Enter") navigate(`/blog/${post.slug || post.id}`);
      });
      els.blogList.appendChild(item);
      requestAnimationFrame(() => item.classList.add("show"));
    });

    if (els.blogPager) {
      els.blogPager.hidden = visible.length >= total;
    }
    if (els.blogPageNext) {
      const moreLabel = state.lang === "tr" ? "Daha fazlasını yükle" : "Load more";
      const doneLabel = state.lang === "tr" ? "Gösterilecek başka yok" : "No more posts";
      const hasMore = visible.length < total;
      els.blogPageNext.disabled = !hasMore;
      els.blogPageNext.textContent = hasMore ? moreLabel : doneLabel;
      if (els.blogLoader) els.blogLoader.hidden = true;
    }

    els.blogList.classList.remove("fade-in", "show");
    void els.blogList.offsetWidth;
    els.blogList.classList.add("fade-in", "show");
  };

  const renderBlogPost = (post) => {
    if (!els.blogArticleWrap || !els.blogArticle || !state.data) return;
    const copy = state.data.translations[state.lang]?.blogCopy;
    const langData = post.lang[state.lang] || post.lang.en || {};
    els.blogArticle.innerHTML = `
      <section class="hero blog-post-hero">
        <div class="blog-post-meta">${formatDate(post.date)}</div>
        <h1 class="hero-line blog-post-title">${langData.title}</h1>
        <div class="work-tags" style="margin-top: 6px;">
          ${(post.tags || []).map((tag) => `<span class="pill">${tag}</span>`).join("")}
        </div>
      </section>
      <div class="blog-post-body">${langData.body || ""}</div>
    `;
    if (els.blogBack && copy) {
      els.blogBack.textContent = copy.backToList || "Back";
    }
    if (els.blogBackBottom && copy) {
      els.blogBackBottom.textContent = copy.backToList || "Back";
    }

    if (els.blogArticle) {
      els.blogArticle.classList.remove("fade-in", "show");
      void els.blogArticle.offsetWidth;
      els.blogArticle.classList.add("fade-in", "show");
    }
  };

  const showSiteView = (replace = false) => {
    state.view = "site";
    state.currentPost = null;
    toggleViews();
    if (!replace) history.pushState({ path: "/" }, "", "/");
    document.title = getSiteTitle();
  };

  const jumpToTop = () => {
    const html = document.documentElement;
    const prevBehavior = html.style.scrollBehavior;
    html.style.scrollBehavior = "auto";
    window.scrollTo({ top: 0, behavior: "auto" });
    document.body.scrollTop = 0;
    html.scrollTop = 0;
    requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: "auto" });
      if (prevBehavior) html.style.scrollBehavior = prevBehavior;
      else html.style.removeProperty("scroll-behavior");
    });
  };

  const showBlogList = (replace = false, opts = {}) => {
    const { preservePage = false, restoreScroll = false } = opts;
    if (state.view === "site" && !preservePage) {
      state.blogPage = 1;
    }
    state.view = "blog";
    state.currentPost = null;
    toggleViews();
    renderBlogList();
    const path = "/blog";
    if (!replace) history.pushState({ path }, "", path);
    const copy = state.data?.translations[state.lang]?.blogCopy;
    if (copy?.title) document.title = `${copy.title} · ${state.data?.site?.brand || "CV + Blog"}`;
    if (restoreScroll && state.lastBlogScroll) {
      requestAnimationFrame(() => {
        window.scrollTo({ top: state.lastBlogScroll, behavior: "smooth" });
        state.lastBlogScroll = 0;
      });
    } else {
      jumpToTop();
    }
  };

  const showBlogPost = (slug, replace = false) => {
    if (!state.data) return;
    const post = state.data.blogPosts.find((p) => (p.slug || p.id) === slug);
    if (!post || !post.published) {
      showBlogList(replace);
      return;
    }
    state.lastBlogScroll = window.scrollY || document.documentElement.scrollTop || 0;
    jumpToTop();
    state.view = "blog-post";
    state.currentPost = post;
    toggleViews();
    renderBlogPost(post);
    const path = `/blog/${slug}`;
    if (!replace) history.pushState({ path }, "", path);
    const langData = post.lang[state.lang] || post.lang.en || {};
    document.title = `${langData.title} · ${state.data?.site?.brand || "CV + Blog"}`;
  };

  const fadeShell = (el, show) => {
    if (!el) return;
    if (show) {
      el.hidden = false;
      requestAnimationFrame(() => el.classList.add("visible"));
    } else {
      el.classList.remove("visible");
      el.hidden = true;
    }
  };

  const toggleViews = () => {
    if (els.siteView) els.siteView.hidden = state.view !== "site";
    if (els.blogView) els.blogView.hidden = state.view === "site";

    const listWrap = els.blogListWrap;
    const articleWrap = els.blogArticleWrap;
    if (listWrap && articleWrap) {
      if (state.view === "blog") {
        fadeShell(listWrap, true);
        fadeShell(articleWrap, false);
      } else if (state.view === "blog-post") {
        fadeShell(listWrap, false);
        fadeShell(articleWrap, true);
      } else {
        fadeShell(listWrap, false);
        fadeShell(articleWrap, false);
      }
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString(state.lang === "tr" ? "tr-TR" : "en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit"
    });
  };

  const getSiteTitle = () => {
    const brand = state.data?.site?.brand || "CV + Blog";
    const hero = state.data?.translations?.[state.lang]?.hero || {};
    const snippet = hero.kicker || stripTags(hero.line) || "";
    return snippet ? `${brand} · ${snippet}` : brand;
  };

  const navigate = (path, replace = false) => {
    if (!path) return;
    const clean = path.endsWith("/") && path !== "/" ? path.slice(0, -1) : path;
    if (clean === "/" || clean.startsWith("#")) {
      showSiteView(replace);
      if (clean.startsWith("#")) {
        scrollToHash(clean);
      }
      return;
    }
    if (clean.startsWith("/blog/")) {
      const slug = clean.split("/")[2];
      showBlogPost(slug, replace);
      return;
    }
    if (clean === "/blog") {
      const comingFromPost = !!state.currentPost;
      showBlogList(replace, { preservePage: comingFromPost, restoreScroll: comingFromPost });
      return;
    }
    showSiteView(replace);
  };

  const navigateToSection = (hash) => {
    showSiteView();
    const targetUrl = hash === "#home" ? "/" : `/${hash}`;
    history.pushState({ path: targetUrl }, "", targetUrl);
    scrollToHash(hash);
  };

  const scrollToHash = (hash) => {
    const el = document.querySelector(hash);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const initReveal = () => {
    const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      document.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
      return;
    }
    const revealables = document.querySelectorAll(".reveal");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealables.forEach((el) => io.observe(el));
  };

  const bindEvents = () => {
    if (els.langToggle) {
      els.langToggle.addEventListener("click", () => {
        const next = state.lang === "en" ? "tr" : "en";
        applyLanguage(next);
        if (state.view === "blog" || state.view === "blog-post") {
          renderBlogList();
          if (state.view === "blog-post" && state.currentPost) {
            renderBlogPost(state.currentPost);
          }
        }
      });
    }
    if (els.themeToggle) {
      els.themeToggle.addEventListener("click", () => {
        const isDark = document.documentElement.classList.contains("theme-dark");
        applyTheme(isDark ? "light" : "dark");
      });
    }
    if (els.navCv) {
      els.navCv.addEventListener("click", (e) => {
        e.preventDefault();
        showCvModal();
      });
    }
    if (els.blogBack) {
      els.blogBack.addEventListener("click", (e) => {
        e.preventDefault();
        navigate("/blog");
      });
    }
    if (els.blogBackBottom) {
      els.blogBackBottom.addEventListener("click", (e) => {
        e.preventDefault();
        navigate("/blog");
      });
    }
    if (els.blogPageNext) {
      els.blogPageNext.addEventListener("click", () => {
        if (els.blogLoader) els.blogLoader.hidden = false;
        const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const delay = prefersReducedMotion ? 0 : 200;
        setTimeout(() => {
          state.blogPage += 1;
          renderBlogList();
        }, delay);
      });
    }
    window.addEventListener("popstate", () => navigate(window.location.pathname, true));
  };

  const handleInitialRoute = () => {
    const path = window.location.pathname || "/";
    navigate(path, true);
  };

  const init = async () => {
    applyTheme(getPreferredTheme());
    if (els.year) els.year.textContent = new Date().getFullYear();
    try {
      state.data = await loadContent();
      applyLanguage(state.lang);
      bindEvents();
      initReveal();
      handleInitialRoute();
    } catch (err) {
      console.error(err);
      setText(els.workList, "Failed to load content.");
    }
  };

  document.addEventListener("DOMContentLoaded", init);
})();
