# SPDX-FileCopyrightText: 2026 Bora Yarkın
# SPDX-License-Identifier: GPL-3.0-only

"""
Submit URLs to Bing via the URL Submission API using your sitemap as source.

Usage:
  BING_API_KEY=... python tools/bing_submit.py
  BING_API_KEY=... python tools/bing_submit.py --site https://yoursite.com --sitemap https://yoursite.com/sitemap.xml

Defaults live in the "Configurable defaults" section below so you can quickly
point the script at another site without changing code paths.

Notes:
  - Requires a Bing Webmaster API key for the verified site.
  - Uses only the standard library (urllib + xml.etree).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import List, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Configurable defaults (override via env or CLI)
DEFAULT_SITE_URL = os.getenv("BING_DEFAULT_SITE", "https://example.com")
DEFAULT_SITEMAP_URL = os.getenv("BING_DEFAULT_SITEMAP", f"{DEFAULT_SITE_URL.rstrip('/')}/sitemap.xml")
DEFAULT_USER_AGENT = os.getenv(
    "BING_SITEMAP_UA",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
)


def fetch_sitemap_urls(sitemap_url: str, user_agent: str) -> List[str]:
    req = Request(sitemap_url, headers={"User-Agent": user_agent})
    with urlopen(req, timeout=20) as resp:
        body = resp.read()
    root = ET.fromstring(body)
    urls: List[str] = []
    for url_el in root.findall(".//{*}url"):
        loc_el = url_el.find("{*}loc")
        if loc_el is not None and loc_el.text:
            urls.append(loc_el.text.strip())
    return urls


def submit_urls(api_key: str, site_url: str, urls: List[str]) -> Tuple[int, str]:
    endpoint = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?{urlencode({'apikey': api_key})}"
    payload = {"siteUrl": site_url, "urlList": urls}
    body = json.dumps(payload).encode("utf-8")
    req = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=20) as resp:
            status = getattr(resp, "status", None) or 200
            text = resp.read().decode("utf-8", errors="ignore")
            return status, text
    except HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="ignore")
    except URLError as err:
        return 0, str(err)


def run(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.getenv("BING_API_KEY")
    if not api_key:
        print("Missing API key. Provide --api-key or set BING_API_KEY.", file=sys.stderr)
        return 1

    try:
        urls = fetch_sitemap_urls(args.sitemap, args.user_agent)
    except Exception as err:  # noqa: BLE001
        print(f"Failed to load sitemap: {err}", file=sys.stderr)
        return 1

    if not urls:
        print("No URLs found in sitemap.", file=sys.stderr)
        return 1

    print(f"Submitting {len(urls)} URLs to Bing for {args.site} ...")
    status, text = submit_urls(api_key, args.site, urls)
    print(f"Bing response status: {status}")
    print(text)
    return 0 if status == 200 else 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit sitemap URLs to Bing URL Submission API.")
    parser.add_argument("--api-key", help="Bing Webmaster API key (or set BING_API_KEY).")
    parser.add_argument(
        "--site",
        default=DEFAULT_SITE_URL,
        help=f"Verified site URL (default: {DEFAULT_SITE_URL})",
    )
    parser.add_argument(
        "--sitemap",
        default=DEFAULT_SITEMAP_URL,
        help=f"Sitemap URL to pull URLs from (default: {DEFAULT_SITEMAP_URL})",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"UA used to fetch the sitemap (default: {DEFAULT_USER_AGENT})",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(run(parse_args(sys.argv[1:])))
