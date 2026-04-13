# SPDX-FileCopyrightText: 2026 Bora Yarkın
# SPDX-License-Identifier: GPL-3.0-only

"""
Simple SEO crawl helper to simulate Googlebot/Bingbot.

Usage:
  python tools/seo_crawl.py
  python tools/seo_crawl.py --base https://yoursite.com --lang en fr --include-www

Defaults live in the "Configurable defaults" section below so you can retarget
to another site without changing logic. The script pulls URLs from /sitemap.xml,
adds optional language-query variants, and can check the bare www host for quick
diagnostics.
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Set
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_UAS = {
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
}


# Configurable defaults (override via env or CLI)
def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_BASE_URL = os.getenv("SEO_DEFAULT_BASE", "https://example.com")
DEFAULT_SITEMAP_PATH = os.getenv("SEO_DEFAULT_SITEMAP", "/sitemap.xml")
DEFAULT_LANG_CODES = [code.strip() for code in os.getenv("SEO_DEFAULT_LANGS", "en").split(",") if code.strip()]
DEFAULT_INCLUDE_WWW = _env_flag("SEO_INCLUDE_WWW", True)


@dataclass
class PageCheck:
    url: str
    status: Optional[int]
    final_url: Optional[str]
    canonical: Optional[str]
    meta_robots: Optional[str]
    x_robots: Optional[str]
    error: Optional[str]


class CanonicalParser(HTMLParser):
    """Tiny HTML parser to extract canonical and robots meta."""

    def __init__(self) -> None:
        super().__init__()
        self.canonical: Optional[str] = None
        self.meta_robots: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = {k.lower(): v for k, v in attrs}
        if tag.lower() == "link":
            rel = attrs_dict.get("rel", "") or ""
            rel_tokens = {t.strip().lower() for t in rel.split()}
            if "canonical" in rel_tokens and not self.canonical:
                self.canonical = attrs_dict.get("href")
        elif tag.lower() == "meta":
            name = (attrs_dict.get("name") or "").lower()
            if name == "robots" and not self.meta_robots:
                self.meta_robots = attrs_dict.get("content")


def fetch(url: str, user_agent: str) -> PageCheck:
    req = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(req, timeout=15) as resp:
            status = getattr(resp, "status", None)
            final_url = resp.geturl()
            x_robots = resp.headers.get("X-Robots-Tag")
            body = resp.read().decode("utf-8", errors="ignore")
    except HTTPError as err:
        return PageCheck(url=url, status=err.code, final_url=err.geturl(), canonical=None, meta_robots=None, x_robots=err.headers.get("X-Robots-Tag"), error=str(err))
    except URLError as err:
        return PageCheck(url=url, status=None, final_url=None, canonical=None, meta_robots=None, x_robots=None, error=str(err))
    except Exception as err:  # noqa: BLE001 - we want any fetch failure
        return PageCheck(url=url, status=None, final_url=None, canonical=None, meta_robots=None, x_robots=None, error=str(err))

    parser = CanonicalParser()
    parser.feed(body)
    return PageCheck(
        url=url,
        status=status,
        final_url=final_url,
        canonical=parser.canonical,
        meta_robots=parser.meta_robots,
        x_robots=x_robots,
        error=None,
    )


def load_sitemap_urls(sitemap_url: str) -> List[str]:
    req = Request(sitemap_url, headers={"User-Agent": DEFAULT_UAS["Googlebot"]})
    try:
        with urlopen(req, timeout=15) as resp:
            xml_body = resp.read()
    except Exception:
        return []
    try:
        root = ET.fromstring(xml_body)
    except ET.ParseError:
        return []
    urls: List[str] = []
    for url_el in root.findall(".//{*}url"):
        loc_el = url_el.find("{*}loc")
        if loc_el is not None and loc_el.text:
            urls.append(loc_el.text.strip())
    return urls


def unique_urls(urls: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    deduped: List[str] = []
    for url in urls:
        if url not in seen:
            deduped.append(url)
            seen.add(url)
    return deduped


def build_url_list(base: str, sitemap_path: str, lang_codes: List[str], include_www: bool) -> List[str]:
    base = base.rstrip("/")
    urls: List[str] = [base]

    sitemap_url = sitemap_path if sitemap_path.startswith("http") else urljoin(f"{base}/", sitemap_path.lstrip("/"))
    urls.extend(load_sitemap_urls(sitemap_url))

    # Add lang variants as query strings.
    extra: List[str] = []
    for url in urls:
        for code in lang_codes:
            sep = "&" if "?" in url else "?"
            extra.append(f"{url}{sep}lang={code}")
    urls.extend(extra)

    # Optionally add bare www to detect redirect status.
    if include_www:
        parsed = urlparse(base)
        if parsed.netloc and not parsed.netloc.startswith("www."):
            www_netloc = f"www.{parsed.netloc}"
            www_base = parsed._replace(netloc=www_netloc).geturl()
            urls.append(www_base)

    return unique_urls(urls)


def run(args: argparse.Namespace) -> int:
    url_list = build_url_list(args.base, args.sitemap, args.lang, args.include_www)
    user_agents: Dict[str, str] = {}
    if args.ua:
        for ua in args.ua:
            label, _, ua_string = ua.partition("=")
            if ua_string:
                user_agents[label.strip()] = ua_string.strip()
    if not user_agents:
        user_agents = DEFAULT_UAS

    print(f"Checking {len(url_list)} URLs with {len(user_agents)} user agent(s)...\n")
    for label, ua_string in user_agents.items():
        print(f"=== {label} ===")
        for url in url_list:
            result = fetch(url, ua_string)
            if result.error:
                print(f"[{result.url}] ERR {result.error}")
                continue
            canonical_note = f"canonical={result.canonical}" if result.canonical else "canonical=missing"
            robots_note = f"meta_robots={result.meta_robots}" if result.meta_robots else "meta_robots=none"
            xrobots_note = f"x_robots={result.x_robots}" if result.x_robots else "x_robots=none"
            final_note = f"-> {result.final_url}" if result.final_url and result.final_url != result.url else ""
            print(f"[{result.url}] {result.status} {final_note} | {canonical_note} | {robots_note} | {xrobots_note}")
        print()
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl site like Google/Bing and report canonical/robots signals.")
    lang_default_display = ", ".join(DEFAULT_LANG_CODES) if DEFAULT_LANG_CODES else "none"
    parser.add_argument(
        "--base",
        default=DEFAULT_BASE_URL,
        help=f"Base site URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--sitemap",
        default=DEFAULT_SITEMAP_PATH,
        help=f"Sitemap path or full URL (default: {DEFAULT_SITEMAP_PATH})",
    )
    parser.add_argument(
        "--lang",
        nargs="*",
        default=DEFAULT_LANG_CODES,
        help=f"Language codes to append as ?lang=... variants (default: {lang_default_display})",
    )
    parser.add_argument(
        "--include-www",
        dest="include_www",
        action="store_true",
        default=DEFAULT_INCLUDE_WWW,
        help=f"Also test the www. host for redirects/status (default: {'on' if DEFAULT_INCLUDE_WWW else 'off'}).",
    )
    parser.add_argument(
        "--no-www",
        dest="include_www",
        action="store_false",
        help="Disable www host checks.",
    )
    parser.add_argument("--ua", nargs="*", help='Extra user agents as label=string (e.g., "DuckDuckBot=Mozilla/5.0 ...")')
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(run(parse_args(sys.argv[1:])))
