# SPDX-FileCopyrightText: 2026 Bora Yarkın
# SPDX-License-Identifier: GPL-3.0-only

import json
import os
import re
import secrets
import sqlite3
import struct
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

from flask import (
    Flask,
    abort,
    has_request_context,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
ASSET_DIR = STATIC_DIR / "assets"
DEMO_DIR = STATIC_DIR / "demo"

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    static_url_path="/assets",
    template_folder="templates",
    instance_relative_config=True,
)
SETUP_CONFIG_PATH = Path(app.instance_path) / "setup.json"


def load_setup_config() -> Dict[str, Any]:
    try:
        SETUP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if SETUP_CONFIG_PATH.exists():
            return json.loads(SETUP_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_setup_config(data: Dict[str, Any]) -> None:
    try:
        SETUP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETUP_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def normalize_site_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    if not parsed.netloc:
        return ""
    scheme = parsed.scheme or "https"
    path = parsed.path.rstrip("/") if parsed.path else ""
    normalized = urlunparse((scheme, parsed.netloc.lower(), path, "", "", ""))
    return normalized.rstrip("/")


_setup_config = load_setup_config()
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or _setup_config.get("secret_key") or "change-me"

DB_PATH = Path(app.instance_path) / "content.db"
SEED_PATH = DEMO_DIR / "demo.json"
SITE_URL_CONFIG = normalize_site_url(os.environ.get("SITE_URL") or os.environ.get("PUBLIC_URL") or _setup_config.get("site_url") or "")

DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME") or _setup_config.get("admin_username") or "admin"
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
ROOT_FILES = {
    "manifest.json",
    "robots.txt",
    "sitemap.xml",
    "favicon.ico",
}
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_ICON_EXTS = {".ico", ".png", ".svg"}
ALLOWED_CV_EXTS = {".pdf"}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS site_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    brand TEXT,
    email TEXT,
    cv_path_en TEXT,
    cv_path_tr TEXT,
    profile_picture TEXT,
    favicon_path TEXT,
    site_url TEXT
);

CREATE TABLE IF NOT EXISTS translations (
    lang TEXT PRIMARY KEY,
    nav_cv_label TEXT,
    hero_kicker TEXT,
    hero_line TEXT,
    hero_body1 TEXT,
    hero_body2 TEXT,
    work_title TEXT,
    work_sub TEXT,
    work_link_label TEXT,
    exp_title TEXT,
    exp_sub TEXT,
    skills_title TEXT,
    skills_sub TEXT,
    edu_title TEXT,
    edu_meta TEXT,
    contact_title TEXT,
    contact_sub TEXT,
    contact_line1 TEXT,
    blog_title TEXT,
    blog_sub TEXT,
    blog_empty TEXT,
    blog_draft_label TEXT,
    blog_published_label TEXT,
    blog_back TEXT
);

CREATE TABLE IF NOT EXISTS hero_body_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    body_html TEXT,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nav_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    href TEXT NOT NULL,
    label TEXT NOT NULL,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hero_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    link_id TEXT,
    label TEXT,
    url TEXT,
    icon TEXT,
    is_download INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    label TEXT,
    url TEXT,
    icon TEXT,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ord INTEGER NOT NULL DEFAULT 0,
    link TEXT
);

CREATE TABLE IF NOT EXISTS work_i18n (
    work_id INTEGER NOT NULL,
    lang TEXT NOT NULL,
    title TEXT,
    meta TEXT,
    brief TEXT,
    detail TEXT,
    PRIMARY KEY (work_id, lang),
    FOREIGN KEY (work_id) REFERENCES work_items (id) ON DELETE CASCADE,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_tags (
    work_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (work_id, tag),
    FOREIGN KEY (work_id) REFERENCES work_items (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ord INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experience_i18n (
    exp_id INTEGER NOT NULL,
    lang TEXT NOT NULL,
    company TEXT,
    role TEXT,
    date TEXT,
    desc TEXT,
    PRIMARY KEY (exp_id, lang),
    FOREIGN KEY (exp_id) REFERENCES experience (id) ON DELETE CASCADE,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experience_bullets (
    exp_id INTEGER NOT NULL,
    lang TEXT NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    bullet TEXT,
    PRIMARY KEY (exp_id, lang, ord),
    FOREIGN KEY (exp_id) REFERENCES experience (id) ON DELETE CASCADE,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ord INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS skills_group_i18n (
    group_id INTEGER NOT NULL,
    lang TEXT NOT NULL,
    label TEXT,
    text TEXT,
    PRIMARY KEY (group_id, lang),
    FOREIGN KEY (group_id) REFERENCES skills_groups (id) ON DELETE CASCADE,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS blog_posts (
    slug TEXT PRIMARY KEY,
    legacy_id TEXT,
    published INTEGER NOT NULL DEFAULT 0,
    date TEXT,
    position INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS blog_post_i18n (
    slug TEXT NOT NULL,
    lang TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    body TEXT,
    PRIMARY KEY (slug, lang),
    FOREIGN KEY (slug) REFERENCES blog_posts (slug) ON DELETE CASCADE,
    FOREIGN KEY (lang) REFERENCES translations (lang) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS blog_tags (
    slug TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (slug, tag),
    FOREIGN KEY (slug) REFERENCES blog_posts (slug) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_user (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def apply_schema_patches(conn: sqlite3.Connection) -> None:
    site_cols = {row["name"] for row in conn.execute("PRAGMA table_info(site_settings)").fetchall() if row and "name" in row.keys()}
    if "profile_picture" not in site_cols:
        conn.execute("ALTER TABLE site_settings ADD COLUMN profile_picture TEXT")
    if "favicon_path" not in site_cols:
        conn.execute("ALTER TABLE site_settings ADD COLUMN favicon_path TEXT")
    if "site_url" not in site_cols:
        conn.execute("ALTER TABLE site_settings ADD COLUMN site_url TEXT")


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def load_seed_content() -> Dict[str, Any]:
    if SEED_PATH.exists():
        try:
            return json.loads(SEED_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"site": {}, "translations": {}, "blogPosts": []}


def ensure_admin_user(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT COUNT(*) AS c FROM admin_user").fetchone()
    if row and row["c"] == 0:
        conn.execute(
            """
            INSERT INTO admin_user (id, username, password_hash, updated_at)
            VALUES (1, ?, ?, ?)
            """,
            (
                DEFAULT_ADMIN_USERNAME,
                generate_password_hash(DEFAULT_ADMIN_PASSWORD),
                datetime.utcnow().isoformat(),
            ),
        )


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
        apply_schema_patches(conn)
        seed_if_empty(conn)
        ensure_admin_user(conn)


def seed_if_empty(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT COUNT(*) AS c FROM site_settings").fetchone()
    if row and row["c"] > 0:
        return
    data = load_seed_content()
    write_content(conn, data)


def write_content(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    conn.executescript(
        """
        DELETE FROM nav_items;
        DELETE FROM hero_links;
        DELETE FROM hero_body_lines;
        DELETE FROM contact_links;
        DELETE FROM work_tags;
        DELETE FROM work_i18n;
        DELETE FROM work_items;
        DELETE FROM experience_bullets;
        DELETE FROM experience_i18n;
        DELETE FROM experience;
        DELETE FROM skills_group_i18n;
        DELETE FROM skills_groups;
        DELETE FROM blog_tags;
        DELETE FROM blog_post_i18n;
        DELETE FROM blog_posts;
        DELETE FROM translations;
        DELETE FROM site_settings;
        """
    )

    site = data.get("site", {}) or {}
    conn.execute(
        """
        INSERT INTO site_settings (
            id, brand, email, cv_path_en, cv_path_tr, profile_picture, favicon_path, site_url
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            site.get("brand", ""),
            site.get("email", ""),
            site.get("cvPath", ""),
            site.get("cvPathTr") or site.get("cvTr") or "",
            site.get("profilePicture") or site.get("profile_picture") or "assets/profile_picture.jpeg",
            site.get("favicon") or site.get("favicon_path") or "assets/favicon.ico",
            site.get("siteUrl") or site.get("site_url") or SITE_URL_CONFIG or "",
        ),
    )

    translations: Dict[str, Any] = data.get("translations", {}) or {}
    for lang, t in translations.items():
        nav = t.get("nav", {}) or {}
        hero = t.get("hero", {}) or {}
        hero_bodies_raw = hero.get("bodies")
        if isinstance(hero_bodies_raw, list):
            hero_bodies = [str(b) for b in hero_bodies_raw if b is not None]
        else:
            hero_bodies = []
            if hero.get("body1"):
                hero_bodies.append(hero.get("body1"))
            if hero.get("body2"):
                hero_bodies.append(hero.get("body2"))
        if not hero_bodies:
            hero_bodies = [hero.get("body1", ""), hero.get("body2", "")]
        hero_body1 = hero_bodies[0] if len(hero_bodies) > 0 else ""
        hero_body2 = hero_bodies[1] if len(hero_bodies) > 1 else ""
        work = t.get("work", {}) or {}
        exp = t.get("experience", {}) or {}
        skills = t.get("skills", {}) or {}
        contact = t.get("contact", {}) or {}
        blog = t.get("blogCopy", {}) or {}
        conn.execute(
            """
            INSERT OR REPLACE INTO translations (
                lang, nav_cv_label, hero_kicker, hero_line, hero_body1, hero_body2,
                work_title, work_sub, work_link_label,
                exp_title, exp_sub,
                skills_title, skills_sub, edu_title, edu_meta,
                contact_title, contact_sub, contact_line1,
                blog_title, blog_sub, blog_empty, blog_draft_label, blog_published_label, blog_back
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lang,
                nav.get("cvLabel", ""),
                hero.get("kicker", ""),
                hero.get("line", ""),
                hero_body1,
                hero_body2,
                work.get("title", ""),
                work.get("sub", ""),
                work.get("workLinkLabel", ""),
                exp.get("title", ""),
                exp.get("sub", ""),
                skills.get("title", ""),
                skills.get("sub", ""),
                (skills.get("education") or {}).get("title", ""),
                (skills.get("education") or {}).get("meta", ""),
                contact.get("title", ""),
                contact.get("sub", ""),
                contact.get("line1", ""),
                blog.get("title", ""),
                blog.get("sub", ""),
                blog.get("empty", ""),
                blog.get("draftLabel", ""),
                blog.get("publishedLabel", ""),
                blog.get("backToList", ""),
            ),
        )

        for idx, item in enumerate(nav.get("items") or []):
            conn.execute(
                """
                INSERT INTO nav_items (lang, ord, href, label)
                VALUES (?, ?, ?, ?)
                """,
                (lang, idx, item.get("href", ""), item.get("label", "")),
            )

        for idx, link in enumerate(t.get("heroLinks") or []):
            conn.execute(
                """
                INSERT INTO hero_links (lang, ord, link_id, label, url, icon, is_download)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lang,
                    idx,
                    link.get("id", ""),
                    link.get("label", ""),
                    link.get("url", ""),
                    link.get("icon", ""),
                    1 if link.get("download") else 0,
                ),
            )

        conn.execute("DELETE FROM hero_body_lines WHERE lang = ?", (lang,))
        for idx, body in enumerate(hero_bodies):
            conn.execute(
                """
                INSERT INTO hero_body_lines (lang, ord, body_html)
                VALUES (?, ?, ?)
                """,
                (lang, idx, body),
            )

        for idx, link in enumerate(t.get("contactLinks") or []):
            conn.execute(
                """
                INSERT INTO contact_links (lang, ord, label, url, icon)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    lang,
                    idx,
                    link.get("label", ""),
                    link.get("url", ""),
                    link.get("icon", ""),
                ),
            )

    primary_lang = "en" if "en" in translations else next(iter(translations.keys()), None)
    primary_work = translations.get(primary_lang, {}).get("work", {}).get("items", []) if primary_lang else []
    for idx, base_item in enumerate(primary_work):
        cur = conn.execute(
            "INSERT INTO work_items (ord, link) VALUES (?, ?)",
            (idx, base_item.get("link", "")),
        ).lastrowid
        for t_idx, tag in enumerate(base_item.get("tags") or []):
            conn.execute(
                "INSERT INTO work_tags (work_id, tag, ord) VALUES (?, ?, ?)",
                (cur, tag, t_idx),
            )
        for lang, t in translations.items():
            items = t.get("work", {}).get("items", []) or []
            item = items[idx] if idx < len(items) else base_item
            conn.execute(
                """
                INSERT INTO work_i18n (work_id, lang, title, meta, brief, detail)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cur,
                    lang,
                    item.get("title", ""),
                    item.get("meta", ""),
                    item.get("brief", ""),
                    item.get("detail", ""),
                ),
            )

    primary_exp = translations.get(primary_lang, {}).get("experience", {}).get("items", []) if primary_lang else []
    for idx, base_item in enumerate(primary_exp):
        exp_id = conn.execute(
            "INSERT INTO experience (ord) VALUES (?)",
            (idx,),
        ).lastrowid
        for lang, t in translations.items():
            items = t.get("experience", {}).get("items", []) or []
            item = items[idx] if idx < len(items) else base_item
            conn.execute(
                """
                INSERT INTO experience_i18n (exp_id, lang, company, role, date, desc)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    exp_id,
                    lang,
                    item.get("company", ""),
                    item.get("role", ""),
                    item.get("date", ""),
                    item.get("desc", ""),
                ),
            )
            for b_idx, bullet in enumerate(item.get("bullets") or []):
                conn.execute(
                    """
                    INSERT INTO experience_bullets (exp_id, lang, ord, bullet)
                    VALUES (?, ?, ?, ?)
                    """,
                    (exp_id, lang, b_idx, bullet),
                )

    primary_groups = translations.get(primary_lang, {}).get("skills", {}).get("groups", []) if primary_lang else []
    for idx, base_group in enumerate(primary_groups):
        group_id = conn.execute(
            "INSERT INTO skills_groups (ord) VALUES (?)",
            (idx,),
        ).lastrowid
        for lang, t in translations.items():
            groups = t.get("skills", {}).get("groups", []) or []
            g = groups[idx] if idx < len(groups) else base_group
            conn.execute(
                """
                INSERT INTO skills_group_i18n (group_id, lang, label, text)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, lang, g.get("label", ""), g.get("text", "")),
            )

    posts = data.get("blogPosts", []) or []
    for position, post in enumerate(posts):
        slug = (post.get("slug") or post.get("id") or "").strip()
        if not slug:
            continue
        conn.execute(
            """
            INSERT INTO blog_posts (slug, legacy_id, published, date, position)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                slug,
                post.get("id") or slug,
                1 if post.get("published") else 0,
                post.get("date", ""),
                position,
            ),
        )
        for tag in post.get("tags") or []:
            conn.execute(
                "INSERT INTO blog_tags (slug, tag) VALUES (?, ?)",
                (slug, tag),
            )
        for lang, pdata in (post.get("lang") or {}).items():
            if lang not in translations:
                continue
            conn.execute(
                """
                INSERT INTO blog_post_i18n (slug, lang, title, summary, body)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    slug,
                    lang,
                    pdata.get("title", ""),
                    pdata.get("summary", ""),
                    pdata.get("body", ""),
                ),
            )


def fetch_content(conn: sqlite3.Connection) -> Dict[str, Any]:
    content: Dict[str, Any] = {"site": {}, "translations": {}, "blogPosts": []}
    site_row = conn.execute("SELECT * FROM site_settings WHERE id = 1").fetchone()
    if site_row:
        content["site"] = {
            "brand": site_row["brand"] or "",
            "email": site_row["email"] or "",
            "cvPath": site_row["cv_path_en"] or "",
            "cvPathTr": site_row["cv_path_tr"] or "",
            "profilePicture": site_row["profile_picture"] or "assets/profile_picture.jpeg",
            "favicon": site_row["favicon_path"] or "assets/favicon.ico",
            "siteUrl": site_row["site_url"] or SITE_URL_CONFIG or "",
        }

    nav_map = {}
    for row in conn.execute("SELECT lang, href, label, ord FROM nav_items ORDER BY ord"):
        nav_map.setdefault(row["lang"], []).append({"href": row["href"], "label": row["label"]})

    hero_map = {}
    for row in conn.execute("SELECT lang, link_id, label, url, icon, is_download, ord FROM hero_links ORDER BY ord"):
        hero_map.setdefault(row["lang"], []).append(
            {
                "id": row["link_id"],
                "label": row["label"],
                "url": row["url"],
                "icon": row["icon"],
                "download": bool(row["is_download"]),
            }
        )

    hero_body_map = {}
    for row in conn.execute("SELECT lang, body_html, ord FROM hero_body_lines ORDER BY ord"):
        hero_body_map.setdefault(row["lang"], []).append(row["body_html"])

    contact_link_map = {}
    for row in conn.execute("SELECT lang, label, url, icon, ord FROM contact_links ORDER BY ord"):
        contact_link_map.setdefault(row["lang"], []).append({"label": row["label"], "url": row["url"], "icon": row["icon"]})

    work_rows = conn.execute("SELECT id, ord, link FROM work_items ORDER BY ord").fetchall()
    work_tags_map: Dict[int, List[str]] = {}
    for row in conn.execute("SELECT work_id, tag FROM work_tags ORDER BY ord"):
        work_tags_map.setdefault(row["work_id"], []).append(row["tag"])
    work_i18n_map: Dict[tuple, sqlite3.Row] = {}
    for row in conn.execute("SELECT * FROM work_i18n"):
        work_i18n_map[(row["work_id"], row["lang"])] = row

    exp_rows = conn.execute("SELECT id, ord FROM experience ORDER BY ord").fetchall()
    exp_i18n_map: Dict[tuple, sqlite3.Row] = {}
    for row in conn.execute("SELECT * FROM experience_i18n"):
        exp_i18n_map[(row["exp_id"], row["lang"])] = row
    exp_bullet_map: Dict[tuple, List[str]] = {}
    for row in conn.execute("SELECT exp_id, lang, bullet FROM experience_bullets ORDER BY ord"):
        exp_bullet_map.setdefault((row["exp_id"], row["lang"]), []).append(row["bullet"])

    skill_rows = conn.execute("SELECT id, ord FROM skills_groups ORDER BY ord").fetchall()
    skill_i18n_map: Dict[tuple, sqlite3.Row] = {}
    for row in conn.execute("SELECT * FROM skills_group_i18n"):
        skill_i18n_map[(row["group_id"], row["lang"])] = row

    for trow in conn.execute("SELECT * FROM translations"):
        lang = trow["lang"]
        translations: Dict[str, Any] = {
            "nav": {"items": nav_map.get(lang, []), "cvLabel": trow["nav_cv_label"] or ""},
            "heroLinks": hero_map.get(lang, []),
            "contactLinks": contact_link_map.get(lang, []),
            "hero": {
                "kicker": trow["hero_kicker"] or "",
                "line": trow["hero_line"] or "",
                "body1": trow["hero_body1"] or "",
                "body2": trow["hero_body2"] or "",
                "bodies": [],
            },
            "work": {
                "title": trow["work_title"] or "",
                "sub": trow["work_sub"] or "",
                "workLinkLabel": trow["work_link_label"] or "",
                "items": [],
            },
            "experience": {
                "title": trow["exp_title"] or "",
                "sub": trow["exp_sub"] or "",
                "items": [],
            },
            "skills": {
                "title": trow["skills_title"] or "",
                "sub": trow["skills_sub"] or "",
                "education": {"title": trow["edu_title"] or "", "meta": trow["edu_meta"] or ""},
                "groups": [],
            },
            "contact": {
                "title": trow["contact_title"] or "",
                "sub": trow["contact_sub"] or "",
                "line1": trow["contact_line1"] or "",
            },
            "blogCopy": {
                "title": trow["blog_title"] or "",
                "sub": trow["blog_sub"] or "",
                "empty": trow["blog_empty"] or "",
                "draftLabel": trow["blog_draft_label"] or "",
                "publishedLabel": trow["blog_published_label"] or "",
                "backToList": trow["blog_back"] or "",
            },
        }

        bodies = hero_body_map.get(lang, [])
        if not bodies:
            if trow["hero_body1"]:
                bodies.append(trow["hero_body1"])
            if trow["hero_body2"]:
                bodies.append(trow["hero_body2"])
        translations["hero"]["bodies"] = bodies
        translations["hero"]["body1"] = bodies[0] if len(bodies) > 0 else ""
        translations["hero"]["body2"] = bodies[1] if len(bodies) > 1 else ""

        for w in work_rows:
            row = work_i18n_map.get((w["id"], lang))
            if not row:
                continue
            translations["work"]["items"].append(
                {
                    "title": row["title"] or "",
                    "meta": row["meta"] or "",
                    "brief": row["brief"] or "",
                    "detail": row["detail"] or "",
                    "tags": work_tags_map.get(w["id"], []),
                    "link": w["link"] or None,
                }
            )

        for e in exp_rows:
            row = exp_i18n_map.get((e["id"], lang))
            if not row:
                continue
            translations["experience"]["items"].append(
                {
                    "company": row["company"] or "",
                    "role": row["role"] or "",
                    "date": row["date"] or "",
                    "desc": row["desc"] or "",
                    "bullets": exp_bullet_map.get((e["id"], lang), []),
                }
            )

        for g in skill_rows:
            row = skill_i18n_map.get((g["id"], lang))
            if not row:
                continue
            translations["skills"]["groups"].append({"label": row["label"] or "", "text": row["text"] or ""})

        content["translations"][lang] = translations

    blog_tags_map: Dict[str, List[str]] = {}
    for row in conn.execute("SELECT slug, tag FROM blog_tags"):
        blog_tags_map.setdefault(row["slug"], []).append(row["tag"])
    blog_i18n_map: Dict[tuple, sqlite3.Row] = {}
    for row in conn.execute("SELECT * FROM blog_post_i18n"):
        blog_i18n_map[(row["slug"], row["lang"])] = row

    posts = conn.execute("SELECT slug, legacy_id, published, date, position FROM blog_posts ORDER BY position").fetchall()
    for post in posts:
        entry = {
            "id": post["legacy_id"] or post["slug"],
            "slug": post["slug"],
            "published": bool(post["published"]),
            "tags": blog_tags_map.get(post["slug"], []),
            "date": post["date"] or "",
            "lang": {},
        }
        for lang in content["translations"].keys():
            row = blog_i18n_map.get((post["slug"], lang))
            if row:
                entry["lang"][lang] = {
                    "title": row["title"] or "",
                    "summary": row["summary"] or "",
                    "body": row["body"] or "",
                }
        content["blogPosts"].append(entry)

    return content


def get_content() -> Dict[str, Any]:
    init_db()
    with get_db() as conn:
        return fetch_content(conn)


def save_content(data: Dict[str, Any]) -> None:
    init_db()
    with get_db() as conn:
        write_content(conn, data)


def is_authenticated() -> bool:
    return session.get("is_admin") is True


def is_setup_done() -> bool:
    cfg = load_setup_config()
    return bool(cfg.get("setup_done"))


def setup_allowed() -> bool:
    return not is_setup_done() or is_authenticated()


def get_admin_user() -> Optional[sqlite3.Row]:
    init_db()
    with get_db() as conn:
        return conn.execute("SELECT username, password_hash FROM admin_user WHERE id = 1").fetchone()


def verify_admin(username: str, password: str) -> bool:
    admin = get_admin_user()
    if not admin:
        return False
    return username == admin["username"] and check_password_hash(admin["password_hash"], password)


def set_admin_credentials(username: str, password: str) -> None:
    init_db()
    with get_db() as conn:
        conn.execute(
            """
            UPDATE admin_user
            SET username = ?, password_hash = ?, updated_at = ?
            WHERE id = 1
            """,
            (username, generate_password_hash(password), datetime.utcnow().isoformat()),
        )


def set_admin_username(username: str) -> None:
    init_db()
    with get_db() as conn:
        conn.execute(
            """
            UPDATE admin_user
            SET username = ?, updated_at = ?
            WHERE id = 1
            """,
            (username, datetime.utcnow().isoformat()),
        )


def store_uploaded_file(
    file_storage,
    dest_name: Optional[str],
    allowed_exts: Optional[set],
    directory: Path = ASSET_DIR,
) -> Optional[str]:
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None
    filename = secure_filename(file_storage.filename)
    ext = Path(filename).suffix.lower()
    if allowed_exts and ext not in allowed_exts:
        return None
    target_name = dest_name or filename
    if Path(target_name).suffix.lower() != ext:
        target_name = f"{Path(target_name).stem}{ext}"
    directory.mkdir(parents=True, exist_ok=True)
    dest_path = directory / target_name
    file_storage.save(dest_path)
    try:
        return str(dest_path.relative_to(STATIC_DIR))
    except ValueError:
        return str(dest_path)


def generate_favicon_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    letters = re.sub(r"[^A-Za-z0-9]", "", text.strip())[:3] or "CV"
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64' fill='none'><rect width='64' height='64' rx='12' fill='%230b0c12'/><text x='12' y='44' font-family='Arial, sans-serif' font-size='28' font-weight='700' fill='%23f8fafc'>{letters}</text></svg>"
    dest_path = ASSET_DIR / "favicon.svg"
    dest_path.write_text(svg, encoding="utf-8")
    try:
        return str(dest_path.relative_to(STATIC_DIR))
    except ValueError:
        return str(dest_path)


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def extract_png_from_ico(ico_bytes: bytes, preferred_size: int = 48) -> Optional[bytes]:
    if len(ico_bytes) < 6:
        return None
    try:
        reserved, ico_type, count = struct.unpack_from("<HHH", ico_bytes, 0)
    except struct.error:
        return None
    if reserved != 0 or ico_type != 1 or count < 1:
        return None
    dir_start = 6
    dir_size = 16 * count
    if len(ico_bytes) < dir_start + dir_size:
        return None

    entries = []
    offset = dir_start
    for _ in range(count):
        try:
            width, height, _, _, _, _, size, img_offset = struct.unpack_from("<BBBBHHII", ico_bytes, offset)
        except struct.error:
            return None
        width = 256 if width == 0 else width
        height = 256 if height == 0 else height
        entries.append({"w": width, "h": height, "size": size, "offset": img_offset})
        offset += 16

    candidates = [e for e in entries if e["w"] == e["h"] and e["w"] >= preferred_size]
    if not candidates:
        candidates = [e for e in entries if e["w"] == e["h"]]
    if not candidates:
        return None

    def sort_key(entry: Dict[str, int]) -> tuple:
        size = entry["w"]
        prefer_multiple = 0 if preferred_size and size % preferred_size == 0 else 1
        prefer_exact = 0 if size == preferred_size else 1
        return (prefer_multiple, prefer_exact, size)

    for entry in sorted(candidates, key=sort_key):
        img_offset = entry["offset"]
        img_size = entry["size"]
        if img_offset < 0 or img_size <= 0:
            continue
        end = img_offset + img_size
        if end > len(ico_bytes):
            continue
        payload = ico_bytes[img_offset:end]
        if payload.startswith(PNG_SIGNATURE):
            return payload
    return None


def update_site_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    init_db()
    with get_db() as conn:
        apply_schema_patches(conn)
        current = conn.execute("SELECT * FROM site_settings WHERE id = 1").fetchone()
        current_data = current if current else {}

        def val(key: str, default: str = "") -> str:
            aliases = {
                "cv_path_en": ["cvPath", "cv_en"],
                "cv_path_tr": ["cvPathTr", "cv_tr"],
                "profile_picture": ["profilePicture"],
                "favicon_path": ["favicon"],
                "site_url": ["siteUrl"],
            }
            for candidate in [key, *aliases.get(key, [])]:
                if candidate in data and data[candidate] is not None:
                    return data[candidate]
            if current_data and key in current_data.keys():
                return current_data[key]
            return default

        brand = val("brand", "")
        email = val("email", "")
        cv_en = val("cv_path_en", "")
        cv_tr = val("cv_path_tr", "")
        profile_pic = val("profile_picture", "assets/profile_picture.jpeg")
        favicon_path = val("favicon_path", "assets/favicon.ico")
        site_url_raw = val("site_url", SITE_URL_CONFIG or "")
        site_url = normalize_site_url(site_url_raw)
        if current:
            conn.execute(
                """
                UPDATE site_settings
                SET brand = ?, email = ?, cv_path_en = ?, cv_path_tr = ?, profile_picture = ?, favicon_path = ?, site_url = ?
                WHERE id = 1
                """,
                (brand, email, cv_en, cv_tr, profile_pic, favicon_path, site_url),
            )
        else:
            conn.execute(
                """
                INSERT INTO site_settings (id, brand, email, cv_path_en, cv_path_tr, profile_picture, favicon_path, site_url)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                """,
                (brand, email, cv_en, cv_tr, profile_pic, favicon_path, site_url),
            )
        return {
            "brand": brand,
            "email": email,
            "cvPath": cv_en,
            "cvPathTr": cv_tr,
            "profilePicture": profile_pic,
            "favicon": favicon_path,
            "siteUrl": site_url,
        }


def strip_tags(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"<[^>]*?>", "", str(value)).strip()


def normalize_ws(value: str) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def short_description(text: str, limit: int = 160) -> str:
    clean = normalize_ws(strip_tags(text))
    if len(clean) <= limit:
        return clean
    truncated = clean[:limit].rsplit(" ", 1)[0]
    return truncated or clean[:limit]


def shorten_title(text: str, limit: int = 65) -> str:
    clean = normalize_ws(strip_tags(text))
    if len(clean) <= limit:
        return clean
    shortened = clean[: limit - 1].rsplit(" ", 1)[0]
    return shortened or clean[: limit - 1]


def _forwarded_parts() -> Dict[str, str]:
    """Extract proto/host from Forwarded or X-Forwarded headers."""
    proto = request.headers.get("X-Forwarded-Proto", "")
    host = request.headers.get("X-Forwarded-Host", "")
    fwd = request.headers.get("Forwarded", "")
    if fwd:
        # Parse the first forwarded entry
        first = fwd.split(",", 1)[0]
        for part in first.split(";"):
            key_val = part.strip().split("=", 1)
            if len(key_val) != 2:
                continue
            key, val = key_val
            val = val.strip('"')
            if key.lower() == "proto" and not proto:
                proto = val
            elif key.lower() == "host" and not host:
                host = val
    return {"proto": proto, "host": host}


def get_base_url() -> str:
    cfg = load_setup_config()
    db_url = ""
    try:
        with get_db() as conn:
            row = conn.execute("SELECT site_url FROM site_settings WHERE id = 1").fetchone()
            if row and row["site_url"]:
                db_url = normalize_site_url(row["site_url"])
    except Exception:
        db_url = ""
    cfg_url = normalize_site_url(cfg.get("site_url") or "")
    env_url = normalize_site_url(os.environ.get("SITE_URL") or os.environ.get("PUBLIC_URL") or "")
    chosen = db_url or cfg_url or env_url
    if chosen:
        return chosen.rstrip("/")
    if has_request_context():
        forwarded = _forwarded_parts()
        forwarded_scheme = forwarded.get("proto") or request.headers.get("X-Forwarded-Proto") or request.scheme
        forwarded_host = forwarded.get("host") or request.headers.get("X-Forwarded-Host") or request.host
        candidate = f"{forwarded_scheme}://{forwarded_host}" if forwarded_host else ""
        root = normalize_site_url(candidate) or normalize_site_url(request.url_root)
        if root:
            return root
    return ""


def resolve_public_base_url() -> str:
    base = normalize_site_url(get_base_url() or "")
    parsed = urlparse(base) if base else None
    if parsed and parsed.hostname and not is_local_request_host(parsed.hostname):
        return base
    if has_request_context():
        forwarded = _forwarded_parts()
        forwarded_scheme = forwarded.get("proto") or request.headers.get("X-Forwarded-Proto") or request.scheme
        forwarded_host = forwarded.get("host") or request.headers.get("X-Forwarded-Host") or request.host
        candidate = f"{forwarded_scheme}://{forwarded_host}" if forwarded_host else ""
        req_base = normalize_site_url(candidate) or normalize_site_url(request.url_root)
        parsed_req = urlparse(req_base) if req_base else None
        if parsed_req and parsed_req.hostname and not is_local_request_host(parsed_req.hostname):
            return req_base
    return base or ""


def get_default_lang(content: Dict[str, Any], requested: Optional[str] = None) -> str:
    langs = list(content.get("translations", {}).keys())
    if not langs:
        return "en"
    if requested and requested in langs:
        return requested
    if has_request_context():
        param_lang = (request.args.get("lang") or "").lower()
        if param_lang in langs:
            return param_lang
        for lang, _ in request.accept_languages:
            root = lang.split("-")[0].lower()
            if root in langs:
                return root
    if "en" in langs:
        return "en"
    return langs[0]


def find_blog_post(content: Dict[str, Any], slug: str) -> Optional[Dict[str, Any]]:
    needle = (slug or "").strip().strip("/")
    if not needle:
        return None
    for post in content.get("blogPosts", []) or []:
        if not isinstance(post, dict):
            continue
        post_slug = (post.get("slug") or post.get("id") or "").strip().strip("/")
        if post_slug == needle:
            return post
    return None


def build_seo_payload(
    content: Dict[str, Any],
    path: str,
    default_lang: str,
) -> Dict[str, Any]:
    translations = content.get("translations", {}) or {}
    langs = [str(lang).lower() for lang in translations.keys()] or ["en"]
    default_lang = (default_lang or "").lower()
    meta_lang = default_lang if default_lang in langs else langs[0]
    primary_lang = "en" if "en" in langs else langs[0]
    brand = content.get("site", {}).get("brand") or "Your Name"
    translation = next((trans for code, trans in translations.items() if str(code).lower() == meta_lang), {})

    base_url = resolve_public_base_url()
    path_part = path or "/"
    if not path_part.startswith("/"):
        path_part = f"/{path_part}"
    normalized_path = path_part.rstrip("/") if path_part != "/" else "/"

    page_kind = "site"
    blog_slug = ""
    if normalized_path == "/blog":
        page_kind = "blog"
    elif normalized_path.startswith("/blog/"):
        page_kind = "blog-post"
        blog_slug = normalized_path.split("/", 2)[2]

    blog_post = None
    blog_post_lang = meta_lang
    blog_post_data: Dict[str, Any] = {}
    if page_kind == "blog-post":
        candidate = find_blog_post(content, blog_slug)
        if candidate and candidate.get("published"):
            blog_post = candidate
            lang_map = candidate.get("lang") or {}
            for code in (meta_lang, primary_lang, "en"):
                pdata = lang_map.get(code)
                if isinstance(pdata, dict):
                    blog_post_lang = code
                    blog_post_data = pdata
                    break
            if not blog_post_data:
                for code, pdata in lang_map.items():
                    if isinstance(pdata, dict):
                        blog_post_lang = str(code).lower()
                        blog_post_data = pdata
                        break

    hero = translation.get("hero", {}) or {}
    bodies = hero.get("bodies") or [hero.get("body1", ""), hero.get("body2", "")]
    description_candidates = [
        " ".join([b for b in bodies if b]),
        hero.get("kicker", ""),
        translation.get("contact", {}).get("sub", ""),
        translation.get("work", {}).get("sub", ""),
    ]
    descriptions: Dict[str, str] = {}
    for lang_code, trans in translations.items():
        lang_key = str(lang_code).lower()
        descriptions[lang_key] = short_description(
            " ".join(
                [
                    *(trans.get("hero", {}).get("bodies") or []),
                    trans.get("hero", {}).get("kicker", ""),
                    trans.get("contact", {}).get("sub", ""),
                ]
            )
            or trans.get("hero", {}).get("body1", "")
        )
    fallback_description = ""
    for candidate in description_candidates:
        candidate_desc = short_description(candidate)
        if candidate_desc:
            fallback_description = candidate_desc
            break
    if not fallback_description:
        fallback_description = descriptions.get(meta_lang, "") or descriptions.get(langs[0], "")
    if not fallback_description:
        fallback_description = short_description(f"{brand} — portfolio and blog.")

    canonical_suffix = "" if meta_lang == primary_lang else f"?lang={meta_lang}"
    canonical_url = f"{base_url}{path_part}{canonical_suffix}" if base_url else f"{path_part}{canonical_suffix}"
    if canonical_url.endswith("//"):
        canonical_url = canonical_url.rstrip("/")
    hreflangs = []
    for lang in langs:
        suffix = "" if lang == primary_lang else f"?lang={lang}"
        href = f"{base_url}{path_part}{suffix}" if base_url else f"{path_part}{suffix}"
        hreflangs.append({"lang": lang, "url": href})
    hreflangs.append({"lang": "x-default", "url": f"{base_url}{path_part}" if base_url else path_part})

    profile_path = content.get("site", {}).get("profilePicture") or "assets/profile_picture.jpeg"
    if profile_path.startswith(("http://", "https://")):
        image_url = profile_path
    elif base_url:
        image_url = f"{base_url}/{profile_path.lstrip('/')}"
    else:
        image_url = url_for("static", filename=profile_path, _external=True)

    og_type = "website"
    meta_description = fallback_description
    hero_title = strip_tags(hero.get("line") or hero.get("kicker") or "Portfolio")
    meta_title = shorten_title(f"{brand} · {hero_title}")

    if page_kind == "blog":
        blog_copy = translation.get("blogCopy", {}) or {}
        blog_title = strip_tags(blog_copy.get("title") or "") or "Blog"
        meta_title = shorten_title(f"{brand} · {blog_title}")
        blog_desc = blog_copy.get("sub") or ""
        if blog_desc:
            meta_description = short_description(blog_desc)
    elif page_kind == "blog-post":
        og_type = "article"
        if blog_post_data:
            post_title = strip_tags(blog_post_data.get("title") or "")
            if post_title:
                meta_title = shorten_title(f"{post_title} · {brand}")
            desc_src = blog_post_data.get("summary") or blog_post_data.get("body") or meta_description
            meta_description = short_description(desc_src)

    same_as = [l.get("url") for l in translation.get("heroLinks") or [] if isinstance(l.get("url"), str) and l.get("url", "").startswith("http")]
    structured_graph: List[Dict[str, Any]] = []
    if base_url:
        structured_graph.append(
            {
                "@type": "WebSite",
                "@id": f"{base_url}/#website",
                "url": base_url,
                "name": brand,
                "inLanguage": langs,
            }
        )
    person = {
        "@type": "Person",
        "@id": f"{base_url}/#owner" if base_url else None,
        "name": brand,
        "email": content.get("site", {}).get("email") or None,
        "url": base_url or None,
        "sameAs": [u for u in same_as if u],
    }
    structured_graph.append({k: v for k, v in person.items() if v})

    if page_kind == "blog" and base_url:
        blog_copy = translation.get("blogCopy", {}) or {}
        blog_title = strip_tags(blog_copy.get("title") or "") or "Blog"
        structured_graph.append(
            {
                "@type": "Blog",
                "@id": f"{base_url}/blog/#blog",
                "url": f"{base_url}/blog",
                "name": blog_title,
                "inLanguage": meta_lang,
            }
        )
    elif page_kind == "blog-post" and blog_post and blog_post_data:
        blog_entry = {
            "@type": "BlogPosting",
            "headline": blog_post_data.get("title", ""),
            "description": short_description(blog_post_data.get("summary") or blog_post_data.get("body") or "", 180),
            "inLanguage": blog_post_lang,
            "datePublished": blog_post.get("date") or None,
            "url": canonical_url,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": canonical_url,
            },
        }
        structured_graph.append({k: v for k, v in blog_entry.items() if v})

    structured_data = json.dumps({"@context": "https://schema.org", "@graph": structured_graph})
    return {
        "title": meta_title,
        "description": meta_description,
        "descriptions": descriptions,
        "canonical_url": canonical_url,
        "base_url": base_url,
        "og_type": og_type,
        "image_url": image_url,
        "hreflangs": hreflangs,
        "structured_data": structured_data,
    }


def is_local_request_host(host: str) -> bool:
    hostname = (host or "").split(":")[0].lower()
    return hostname in LOCAL_HOSTS or hostname.endswith(".local")


@app.before_request
def enforce_canonical_host() -> Optional[Any]:
    if not has_request_context():
        return None
    base_url = resolve_public_base_url()
    parsed = urlparse(base_url) if base_url else None
    if not parsed or not parsed.netloc:
        return None
    forwarded = _forwarded_parts()
    request_host = forwarded.get("host") or request.headers.get("X-Forwarded-Host", request.host)
    hostname_only = request_host.split(":")[0].lower()
    if is_local_request_host(hostname_only):
        return None
    target_host = parsed.netloc.lower()
    if is_local_request_host(target_host):
        return None
    req_scheme = forwarded.get("proto") or request.headers.get("X-Forwarded-Proto", request.scheme)
    target_scheme = parsed.scheme or req_scheme or "https"
    if request_host != target_host or req_scheme != target_scheme:
        dest = f"{target_scheme}://{target_host}{request.full_path}"
        if dest.endswith("?"):
            dest = dest[:-1]
        return redirect(dest, code=301)
    return None


def get_root_files(content: Dict[str, Any]) -> set:
    site = content.get("site", {}) or {}
    dynamic_files = {
        Path(site.get("cvPath") or "").name,
        Path(site.get("cvPathTr") or "").name,
        Path(site.get("cvPath") or site.get("cvTr") or "").name,
        Path(site.get("profilePicture") or "").name,
        Path(site.get("favicon") or site.get("favicon_path") or "").name,
    }
    return {name for name in (ROOT_FILES | dynamic_files) if name}


def render_shell(
    default_lang: Optional[str] = None,
    preloaded_content: Optional[Dict[str, Any]] = None,
    slug: Optional[str] = None,
) -> Any:
    content = preloaded_content or get_content()
    lang = get_default_lang(content, default_lang)
    brand = content.get("site", {}).get("brand", "Brand")

    request_path = request.path or "/"
    blog_slug = slug
    if blog_slug is None and request_path.startswith("/blog/"):
        blog_slug = request_path[len("/blog/") :]
    blog_slug = (blog_slug or "").strip().strip("/")

    initial_view = "site"
    current_post = None
    if request_path.rstrip("/") == "/blog" and not blog_slug:
        initial_view = "blog"
    elif request_path.startswith("/blog/") and blog_slug:
        post = find_blog_post(content, blog_slug)
        if post and post.get("published"):
            initial_view = "blog-post"
            current_post = post
        else:
            initial_view = "blog"

    seo = build_seo_payload(content, request_path, lang)
    return render_template(
        "index.html",
        content=content,
        brand=brand,
        default_lang=lang,
        seo=seo,
        initial_view=initial_view,
        current_post=current_post,
    )


@app.route("/")
def index() -> Any:
    return render_shell(request.args.get("lang"))


@app.route("/blog")
@app.route("/blog/<path:slug>")
def blog(slug: Optional[str] = None) -> Any:
    content = get_content()
    if slug:
        post = find_blog_post(content, slug)
        if not post or not post.get("published"):
            return render_shell(request.args.get("lang"), preloaded_content=content, slug=slug), 404
    return render_shell(request.args.get("lang"), preloaded_content=content, slug=slug)


@app.route("/admin")
def admin_page() -> Any:
    if not is_authenticated():
        return redirect(url_for("login_page"))
    content = get_content()
    brand = content.get("site", {}).get("brand", "Admin")
    return render_template("admin.html", brand=brand)


@app.route("/login", methods=["GET", "POST"])
def login_page() -> Any:
    if is_authenticated():
        return redirect(url_for("admin_page"))
    content = get_content()
    brand = content.get("site", {}).get("brand", "Admin")
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if verify_admin(username, password):
            session["is_admin"] = True
            session["username"] = username
            return redirect(url_for("admin_page"))
        error = "Invalid credentials"
    return render_template("login.html", brand=brand, error=error)


@app.route("/setup")
def setup_page() -> Any:
    cfg = load_setup_config()
    if cfg.get("setup_done"):
        if is_authenticated():
            return redirect(url_for("admin_page"))
        return redirect(url_for("login_page"))
    content = get_content()
    brand = content.get("site", {}).get("brand", "Setup")
    admin = get_admin_user()
    return render_template(
        "setup.html",
        content=content,
        brand=brand,
        default_lang=get_default_lang(content),
        setup_cfg=cfg,
        admin_username=admin["username"] if admin else DEFAULT_ADMIN_USERNAME,
    )


@app.post("/api/login")
def api_login() -> Any:
    payload = request.get_json(silent=True) or request.form
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if verify_admin(username, password):
        session["is_admin"] = True
        session["username"] = username
        return jsonify({"status": "ok"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.post("/api/logout")
def api_logout() -> Any:
    session.clear()
    return jsonify({"status": "ok"})


@app.post("/api/setup")
def api_setup() -> Any:
    cfg = load_setup_config()
    if cfg.get("setup_done"):
        return jsonify({"error": "Setup is already completed"}), 403

    content = get_content()
    form = request.form
    files = request.files
    brand = (form.get("brand") or "").strip()
    email = (form.get("email") or "").strip()
    site_url = (form.get("site_url") or form.get("siteUrl") or "").strip()
    admin_username = (form.get("admin_username") or form.get("adminUsername") or "").strip() or DEFAULT_ADMIN_USERNAME
    admin_password = form.get("admin_password") or form.get("adminPassword") or DEFAULT_ADMIN_PASSWORD
    secret_key = form.get("secret_key") or form.get("secretKey") or cfg.get("secret_key") or secrets.token_hex(32)
    favicon_text = (form.get("favicon_text") or "").strip()

    def save_or_error(file_obj, dest_name, allowed, directory=ASSET_DIR) -> Optional[str]:
        if not file_obj or not getattr(file_obj, "filename", ""):
            return None
        saved = store_uploaded_file(file_obj, dest_name, allowed, directory=directory)
        if not saved:
            raise ValueError("Invalid file type")
        return saved

    try:
        cv_en_path = save_or_error(files.get("cv_en"), None, ALLOWED_CV_EXTS)
        cv_tr_path = save_or_error(files.get("cv_tr"), None, ALLOWED_CV_EXTS)
        profile_path = save_or_error(files.get("profile_picture"), "profile_picture", ALLOWED_IMAGE_EXTS)
        favicon_path = None
        if files.get("favicon"):
            favicon_path = save_or_error(files.get("favicon"), "favicon", ALLOWED_ICON_EXTS, directory=ASSET_DIR)
        elif favicon_text:
            favicon_path = generate_favicon_from_text(favicon_text)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    resolved_site_url = normalize_site_url(site_url or content.get("site", {}).get("siteUrl") or get_base_url() or "")

    updates: Dict[str, Any] = {
        "brand": brand or content.get("site", {}).get("brand") or "",
        "email": email or content.get("site", {}).get("email") or "",
        "cv_path_en": cv_en_path or content.get("site", {}).get("cvPath") or "",
        "cv_path_tr": cv_tr_path or content.get("site", {}).get("cvPathTr") or "",
        "profile_picture": profile_path or content.get("site", {}).get("profilePicture") or "assets/profile_picture.jpeg",
        "favicon_path": favicon_path or content.get("site", {}).get("favicon") or "favicon.ico",
        "site_url": resolved_site_url,
    }

    site_data = update_site_settings(updates)
    if admin_username or admin_password:
        if admin_password:
            set_admin_credentials(admin_username, admin_password)
        else:
            set_admin_username(admin_username)
    cfg["secret_key"] = secret_key
    if resolved_site_url:
        cfg["site_url"] = resolved_site_url
    cfg["admin_username"] = admin_username
    cfg["setup_done"] = True
    save_setup_config(cfg)
    app.config["SECRET_KEY"] = secret_key

    return jsonify({"status": "ok", "site": site_data})


@app.get("/api/content")
def api_get_content() -> Any:
    return jsonify(get_content())


@app.post("/api/content")
def api_save_content() -> Any:
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload"}), 400
    save_content(data)
    return jsonify({"status": "saved"})


@app.post("/api/export")
def api_export_content() -> Any:
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True)
    data: Any
    if isinstance(payload, dict) and payload.get("data") is not None:
        data = payload["data"]
    elif isinstance(payload, dict):
        data = payload
    elif payload is None:
        data = get_content()
    else:
        return jsonify({"error": "Invalid payload"}), 400

    try:
        body = json.dumps(data, indent=2)
    except TypeError:
        return jsonify({"error": "Invalid data"}), 400

    response = make_response(body)
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = 'attachment; filename="content.json"'
    return response


@app.post("/api/upload-cv")
def api_upload_cv() -> Any:
    cfg = load_setup_config()
    if not is_authenticated() and cfg.get("setup_done"):
        return jsonify({"error": "Unauthorized"}), 401
    lang = (request.form.get("lang") or "").lower()
    if lang not in {"en", "tr"}:
        return jsonify({"error": "Invalid language"}), 400
    file_obj = request.files.get("file")
    if not file_obj or not getattr(file_obj, "filename", ""):
        return jsonify({"error": "No file uploaded"}), 400
    saved = store_uploaded_file(file_obj, None, ALLOWED_CV_EXTS)
    if not saved:
        return jsonify({"error": "Invalid file type"}), 400
    updates = {"cv_path_en": saved} if lang == "en" else {"cv_path_tr": saved}
    site = update_site_settings(updates)
    return jsonify({"status": "ok", "path": saved, "site": site})


@app.route("/api/change-password", methods=["GET", "POST", "OPTIONS"], strict_slashes=False)
def api_change_password() -> Any:
    if request.method == "OPTIONS":
        return ("", 204)
    if request.method != "POST":
        return jsonify({"error": "Use POST"}), 400
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or request.form
    current = (payload.get("current_password") or payload.get("currentPassword") or "").strip()
    new_pw = (payload.get("new_password") or payload.get("newPassword") or "").strip()
    confirm = (payload.get("confirm_password") or payload.get("confirmPassword") or "").strip()
    if not current or not new_pw or not confirm:
        return jsonify({"error": "All fields are required"}), 400
    if new_pw != confirm:
        return jsonify({"error": "New password and confirmation do not match"}), 400
    if len(new_pw) < 8:
        return jsonify({"error": "New password must be at least 8 characters"}), 400
    admin = get_admin_user()
    if not admin or not check_password_hash(admin["password_hash"], current):
        return jsonify({"error": "Current password is incorrect"}), 400
    set_admin_credentials(admin["username"], new_pw)
    return jsonify({"status": "ok"})


@app.route("/robots.txt")
def robots() -> Any:
    base_url = resolve_public_base_url() or normalize_site_url(request.url_root) or (request.url_root[:-1] if request.url_root.endswith("/") else request.url_root)
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {base_url}/sitemap.xml",
        ]
    )
    response = make_response(body)
    response.headers["Content-Type"] = "text/plain"
    return response


@app.route("/sitemap.xml")
def sitemap() -> Any:
    content = get_content()
    base_url = resolve_public_base_url() or normalize_site_url(request.url_root)
    if not base_url:
        base_url = request.url_root[:-1] if request.url_root.endswith("/") else request.url_root
    languages = [str(code).lower() for code in (content.get("translations", {}) or {}).keys()] or ["en"]
    primary_lang = "en" if "en" in languages else languages[0]

    def alt_links(path: str) -> List[Dict[str, str]]:
        links = []
        for code in languages:
            suffix = "" if code == primary_lang else f"?lang={code}"
            links.append({"lang": code, "href": f"{base_url}{path}{suffix}"})
        links.append({"lang": "x-default", "href": f"{base_url}{path}"})
        return links

    urls = [
        {"path": "/", "changefreq": "weekly", "priority": "1.0", "alternates": alt_links("/")},
        {"path": "/blog", "changefreq": "weekly", "priority": "0.8", "alternates": alt_links("/blog")},
    ]
    for post in content.get("blogPosts", []):
        if not post.get("published"):
            continue
        slug = (post.get("slug") or post.get("id") or "").strip()
        if not slug:
            continue
        urls.append(
            {
                "path": f"/blog/{slug}",
                "changefreq": "daily",
                "priority": "0.6",
                "lastmod": post.get("date") or "",
                "alternates": alt_links(f"/blog/{slug}"),
            }
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for url in urls:
        loc = f"{base_url}{url['path']}"
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if url.get("lastmod"):
            lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        lines.append(f"    <priority>{url['priority']}</priority>")
        for alt in url.get("alternates", []):
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{alt["lang"]}" href="{alt["href"]}" />')
        lines.append("  </url>")
    lines.append("</urlset>")
    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route("/manifest.json")
def manifest() -> Any:
    content = get_content()
    brand = content.get("site", {}).get("brand") or "Portfolio"
    favicon_path = content.get("site", {}).get("favicon") or "favicon.ico"
    icon_ext = Path(favicon_path).suffix.lower()
    icon_type = "image/png"
    if icon_ext == ".svg":
        icon_type = "image/svg+xml"
    elif icon_ext in {".ico", ".cur"}:
        icon_type = "image/x-icon"
    data = {
        "name": brand,
        "short_name": brand,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#060708",
        "theme_color": "#060708",
        "icons": [
            {
                "src": url_for("favicon"),
                "sizes": "64x64",
                "type": icon_type,
            }
        ],
    }
    response = jsonify(data)
    response.headers["Content-Type"] = "application/manifest+json"
    return response


@app.get("/cv/<lang>")
def download_cv(lang: str) -> Any:
    lang = (lang or "").lower()
    if lang not in {"en", "tr"}:
        abort(404)
    content = get_content()
    site = content.get("site", {}) or {}
    raw = site.get("cvPathTr") if lang == "tr" else site.get("cvPath")
    if not raw:
        abort(404)
    if raw.startswith("http://") or raw.startswith("https://"):
        return redirect(raw)
    path = raw.lstrip("/")
    full_path = STATIC_DIR / path
    if not full_path.is_file():
        abort(404)
    return send_file(full_path, as_attachment=True, download_name=full_path.name, mimetype="application/pdf")


@app.route("/favicon.ico")
def favicon() -> Any:
    content = get_content()
    fav_path = content.get("site", {}).get("favicon") or "favicon.ico"
    target = STATIC_DIR / fav_path
    if target.is_file():
        return send_from_directory(target.parent, target.name)
    fallback = STATIC_DIR / "favicon.ico"
    if fallback.is_file():
        return send_from_directory(fallback.parent, fallback.name)
    abort(404)


@app.route("/favicon.png")
def favicon_png() -> Any:
    content = get_content()
    fav_path = content.get("site", {}).get("favicon") or "favicon.ico"
    target = STATIC_DIR / fav_path
    ext = target.suffix.lower()

    if target.is_file() and ext == ".png":
        return send_from_directory(target.parent, target.name)

    if target.is_file() and ext == ".ico":
        extracted = extract_png_from_ico(target.read_bytes(), preferred_size=48)
        if extracted:
            response = make_response(extracted)
            response.headers["Content-Type"] = "image/png"
            response.headers["Cache-Control"] = "public, max-age=14400"
            return response

    fallback_ico = STATIC_DIR / "assets" / "favicon.ico"
    if fallback_ico.is_file():
        extracted = extract_png_from_ico(fallback_ico.read_bytes(), preferred_size=48)
        if extracted:
            response = make_response(extracted)
            response.headers["Content-Type"] = "image/png"
            response.headers["Cache-Control"] = "public, max-age=14400"
            return response
    abort(404)


@app.route("/<path:filename>")
def serve_root_file(filename: str) -> Any:
    safe_name = Path(filename).name
    content = get_content()
    allowed = get_root_files(content)
    if safe_name in allowed and (ASSET_DIR / safe_name).is_file():
        return send_from_directory(ASSET_DIR, safe_name)
    abort(404)


@app.errorhandler(404)
def not_found(_: Exception) -> Any:
    if "." in (request.path.rsplit("/", 1)[-1]):
        return ("", 404)
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_shell(), 404


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)
