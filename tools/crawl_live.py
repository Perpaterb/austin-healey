#!/usr/bin/env python3
"""Mirror a live same-domain WordPress site using requests (wget is WAF-blocked)."""
import os, re, sys, time, hashlib
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

START = "https://ahocnsw.org.au/"
DOMAIN = "ahocnsw.org.au"
ROOT = sys.argv[1] if len(sys.argv) > 1 else "old-site"
SITEDIR = os.path.join(ROOT, DOMAIN)

HEADERS = {
    # The site's WAF blocks wget and full Chrome UA strings; a bare UA passes.
    "User-Agent": "Mozilla/5.0",
}

SKIP_RE = re.compile(
    r"(wp-json|xmlrpc|/feed/?|wp-login|wp-admin|/comments/|replytocom"
    r"|events-calendars"                 # Tribe calendar views (list/month/day) = crawler trap
    r"|tribe-bar-date|outlook-ical|eventDisplay|[?&]ical=|tribe_|ai1ec"
    r"|[?&]p=\d|[?&]ver=|/embed/?$|/amp/?$"
    r"|/a$)",                            # malformed trailing-anchor artifacts
    re.I)
ASSET_EXT = re.compile(r"\.(css|js|jpg|jpeg|png|gif|webp|svg|ico|woff2?|ttf|eot|otf|mp4|webm|pdf|json|xml)$", re.I)

session = requests.Session()
session.headers.update(HEADERS)

# url(without fragment) -> local relative path (posix, relative to SITEDIR)
url_local = {}

def canon(url):
    url, _ = urldefrag(url)
    return url

def sanitize_query(q):
    return "@" + re.sub(r"[^A-Za-z0-9._-]", "_", q)

def local_path_for(url, is_html):
    """Map a URL to a posix path relative to SITEDIR."""
    p = urlparse(url)
    path = p.path
    query = p.query
    if path == "" or path == "/":
        local = "index.html"
    elif path.endswith("/"):
        local = path.lstrip("/") + "index.html"
    else:
        base = path.lstrip("/")
        seg = base.rsplit("/", 1)[-1]
        if "." in seg:  # has an extension -> asset-like
            local = base
            if query:
                root, ext = os.path.splitext(local)
                local = root + sanitize_query(query) + ext
        else:
            if is_html:
                local = base + "/index.html"
            else:
                local = base + (sanitize_query(query) if query else "")
    # never allow empty
    return local or "index.html"

def save(url, content, is_html):
    rel = local_path_for(url, is_html)
    url_local[canon(url)] = rel
    fp = os.path.join(SITEDIR, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "wb") as f:
        f.write(content)
    return rel

# Extract asset + link URLs from HTML text
URL_ATTR_RE = re.compile(r'(?:src|href|data-src|poster)\s*=\s*["\']([^"\']+)["\']', re.I)
SRCSET_RE = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
CSSURL_RE = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)

def extract(base_url, text, css=False):
    urls = set()
    if css:
        for m in CSSURL_RE.finditer(text):
            urls.add(urljoin(base_url, m.group(1)))
        return urls
    for m in URL_ATTR_RE.finditer(text):
        urls.add(urljoin(base_url, m.group(1)))
    for m in SRCSET_RE.finditer(text):
        for part in m.group(1).split(","):
            u = part.strip().split(" ")[0]
            if u:
                urls.add(urljoin(base_url, u))
    for m in CSSURL_RE.finditer(text):  # inline styles
        urls.add(urljoin(base_url, m.group(1)))
    return urls

def same_domain(url):
    return urlparse(url).netloc.endswith(DOMAIN)

def is_html_url(url):
    p = urlparse(url)
    if ASSET_EXT.search(p.path):
        return False
    return True

def get(url):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30)
            return r
        except Exception as e:
            if attempt == 2:
                print("  FAIL", url, e)
                return None
            time.sleep(1.5)

# BFS over HTML pages
html_queue = deque([canon(START)])
html_seen = set(html_queue)
assets = set()
pages_done = 0
MAX_PAGES = int(os.environ.get("MAX_PAGES", "250"))

while html_queue and pages_done < MAX_PAGES:
    url = html_queue.popleft()
    if SKIP_RE.search(url) or not same_domain(url):
        continue
    r = get(url)
    if not r or r.status_code != 200:
        print("  skip", r.status_code if r else "ERR", url)
        continue
    ctype = r.headers.get("Content-Type", "")
    if "text/html" not in ctype:
        save(url, r.content, is_html=False)
        assets.discard(url)
        continue
    text = r.text
    save(url, r.content, is_html=True)
    pages_done += 1
    print(f"[page {pages_done}] {url}")
    for u in extract(url, text):
        u = canon(u)
        if not same_domain(u) or SKIP_RE.search(u):
            # still keep same-domain assets even if skip? skip covers wp-json etc.
            if not same_domain(u):
                continue
        if is_html_url(u):
            if u not in html_seen and not SKIP_RE.search(u):
                html_seen.add(u)
                html_queue.append(u)
        else:
            assets.add(u)
    time.sleep(0.25)

print(f"\nPages: {pages_done}. Assets to fetch: {len(assets)}")

# Download assets (recurse one level into CSS for fonts/images)
css_queue = deque()
done_assets = 0
for u in list(assets):
    if not same_domain(u):
        continue
    r = get(u)
    if not r or r.status_code != 200:
        print("  asset skip", r.status_code if r else "ERR", u)
        continue
    is_css = "css" in r.headers.get("Content-Type", "") or u.lower().split("?")[0].endswith(".css")
    rel = save(u, r.content, is_html=False)
    done_assets += 1
    if is_css:
        for cu in extract(u, r.text, css=True):
            cu = canon(cu)
            if same_domain(cu) and cu not in assets:
                css_queue.append(cu)
print(f"Assets fetched: {done_assets}. CSS-referenced extra: {len(css_queue)}")

for u in css_queue:
    r = get(u)
    if not r or r.status_code != 200:
        continue
    save(u, r.content, is_html=False)
    done_assets += 1

print(f"Total local files mapped: {len(url_local)}")

# Persist URL->local map for the rewrite pass
import json
with open(os.path.join(ROOT, "_urlmap.json"), "w") as f:
    json.dump(url_local, f)
print("Saved urlmap.")
