<!-- SPDX-FileCopyrightText: 2026 Bora Yarkın -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

# Bilingual CV + Blog Starter (Flask)

A polished two-language CV + blog starter built with Flask, SQLite, and a JSON content model. Edit everything (hero copy, projects, experience, skills, blog posts) via `/setup`, `/admin`, or the checked-in content file.

## Highlights
- Bilingual EN/TR with canonical + `hreflang`, server-rendered meta + JSON-LD
- `/setup` wizard to bootstrap secrets, branding, favicon, profile image, and CV uploads
- `/admin` to edit all content, export/import JSON, and save to SQLite
- Seed + demo content in `static/demo/demo.json`; persistent content in `static/assets/content.json`
- Safe upload handling for CVs, profile picture, favicon, and other assets

## Stack
- Flask, SQLite, Jinja templates
- Vanilla JS + CSS with asset path helpers for `/assets` and uploads

## Quick start
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python app.py`
4. Open `http://localhost:5000/setup`, fill brand/domain/admin/secret key, upload favicon/profile/CV PDFs (EN/TR), then submit
5. Log into `/admin`, edit content, and click **Save to SQLite**

## Content & data
- Primary JSON under version control: `static/assets/content.json`
- Demo seed used when the DB is empty: `static/demo/demo.json`
- SQLite database: `instance/content.db` (auto-created). Delete it to reseed from the demo JSON.
- CV placeholders: `static/assets/cv-en.pdf`, `static/assets/cv-tr.pdf`; profile image + favicon also live under `static/assets/`

## Useful endpoints
- Site root with language toggle: `/` (use `/?lang=en` or `/?lang=tr`)
- Setup wizard: `/setup`
- Admin panel: `/admin`
- Content API: `/api/content`
- SEO: `/sitemap.xml`, `/robots.txt`

## Deployment notes
- Set `FLASK_SECRET_KEY`; optionally set `ADMIN_USERNAME` / `ADMIN_PASSWORD` and `SITE_URL`
- Behind a proxy, configure `PREFERRED_URL_SCHEME` / `SERVER_NAME` if needed
- If you change domains, update `SITE_URL` or rerun `/setup`; sitemap/robots follow automatically

## Project layout
```
app.py               # Flask app, schema, routes, uploads, SEO helpers
.github/             # Community health files, templates, and automation config
static/assets/       # Persistent assets (CVs, uploads, favicon, content.json)
static/demo/         # Demo seed content
static/scripts/      # Front-end JS
static/styles/       # Styles
templates/           # Jinja templates
instance/            # SQLite DB + setup.json (ignored)
```

## Project health
- Community docs live in `.github/` to keep the root tidy.
- Contributing guide: `.github/CONTRIBUTING.md`
- Code of conduct: `.github/CODE_OF_CONDUCT.md`
- Security policy: `.github/SECURITY.md`
- Support guide: `.github/SUPPORT.md`
- Changelog: `CHANGELOG.md`
- Copyright notice: `.github/COPYRIGHT.md`

## License
GNU General Public License v3 only (`GPL-3.0-only`) – see `LICENSE`.
