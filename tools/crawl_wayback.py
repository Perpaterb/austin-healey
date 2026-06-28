#!/usr/bin/env python3
"""Replicate a site from the Wayback Machine at a target timestamp.

Discovers pages by BFS over internal links, fetching each at the snapshot
nearest the target timestamp via the raw `id_` endpoint (original bytes, no
Wayback toolbar). Assets (css/js/img/fonts) saved too. Link map persisted for
a later rewrite pass.
"""
import os, re, sys, time, json
import requests
from urllib.parse import urljoin, urlparse, urldefrag, quote
from collections import deque

TS = "20240410061034"
# original site domains (with/without www)
DOMAINS = ("austinhealeynsw.com.au",)
START = "http://www.austinhealeynsw.com.au/"
ROOT = sys.argv[1] if len(sys.argv) > 1 else "old-old-site"
SITEDIR = os.path.join(ROOT, "austinhealeynsw.com.au")
WB = "https://web.archive.org"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; site-archive/1.0)"}
session = requests.Session()
session.headers.update(HEADERS)

# Don't follow these. Real content (galleries, ad/event detail with ?id=) IS kept;
# junk dropped: contact spam tokens, calendar month/year nav, auth, rsvp, ical.
SKIP_RE = re.compile(
    r"(/login/|/logout|forgot-login|/cart|/checkout|mailto:|tel:|javascript:"
    r"|\.ics$|/rsvp/"
    r"|[?&]to="                          # /contact/?to=<token> spam-form variants
    r"|events/calendar/?\?"              # calendar month/year navigation permutations
    r"|[?&]month=|[?&]year="
    r"|outlook-ical|[?&]ical=|[?&]ec3_ical"
    r")", re.I)
ASSET_EXT = re.compile(r"\.(css|js|jpg|jpeg|png|gif|webp|svg|ico|woff2?|ttf|eot|otf|mp4|webm|pdf|mp3)$", re.I)

url_local = {}

def canon(url):
    url, _ = urldefrag(url)
    return url

def norm_original(url):
    """Normalise an original-site URL: force host to www, http scheme key-agnostic."""
    p = urlparse(url)
    host = p.netloc.lower()
    if host.startswith("www."):
        host_key = host[4:]
    else:
        host_key = host
    return host_key, p

def same_site(url):
    p = urlparse(url)
    host = p.netloc.lower()
    return any(host == d or host == "www." + d for d in DOMAINS)

def wb_url(original):
    """Build the raw snapshot URL for an original-site URL."""
    return f"{WB}/web/{TS}id_/{original}"

def sanitize_query(q):
    return "@" + re.sub(r"[^A-Za-z0-9._-]", "_", q)

def local_path_for(url, is_html):
    p = urlparse(url)
    path = p.path
    query = p.query
    host = p.netloc.lower()
    prefix = "www/" if host.startswith("www.") else ""  # keep www and non-www separate if both
    prefix = ""  # collapse: treat www and bare as same tree
    if path in ("", "/"):
        local = "index.html"
    elif path.endswith("/"):
        base = path.lstrip("/") + "index.html"
        if query:
            base = path.lstrip("/") + "index" + sanitize_query(query) + ".html"
        local = base
    else:
        base = path.lstrip("/")
        seg = base.rsplit("/", 1)[-1]
        if ASSET_EXT.search(seg) or ("." in seg and not is_html):
            local = base
            if query:
                root, ext = os.path.splitext(local)
                local = root + sanitize_query(query) + ext
        elif seg.endswith(".php") or is_html:
            # dynamic or extensionless html page
            root = base[:-4] if seg.endswith(".php") else base
            local = root + (sanitize_query(query) if query else "") + ".html"
        else:
            local = base + (sanitize_query(query) if query else "")
    return local or "index.html"

def save(url, content, is_html):
    rel = local_path_for(url, is_html)
    url_local[canon(url)] = rel
    fp = os.path.join(SITEDIR, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "wb") as f:
        f.write(content)
    return rel

# Note: `content=` deliberately excluded; it grabs meta-tag prose (e.g. og:title) as URLs.
URL_ATTR_RE = re.compile(r'(?:src|href|data-src|poster)\s*=\s*["\']([^"\']+)["\']', re.I)
SRCSET_RE = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
CSSURL_RE = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)

def dearchive(u):
    """Strip any web.archive.org/web/<ts>(id_|...)/ prefix to recover original URL."""
    m = re.match(r"https?://web\.archive\.org/web/\d+(?:id_|if_|im_|cs_|js_)?/(.*)", u)
    if m:
        return m.group(1)
    return u

def extract(base_url, text, css=False):
    urls = set()
    src = text
    if css:
        for m in CSSURL_RE.finditer(src):
            urls.add(urljoin(base_url, dearchive(m.group(1))))
        return urls
    for m in URL_ATTR_RE.finditer(src):
        v = m.group(1)
        if v.startswith(("data:", "#", "mailto:", "tel:", "javascript:")):
            continue
        urls.add(urljoin(base_url, dearchive(v)))
    for m in SRCSET_RE.finditer(src):
        for part in m.group(1).split(","):
            u = part.strip().split(" ")[0]
            if u and not u.startswith("data:"):
                urls.add(urljoin(base_url, dearchive(u)))
    for m in CSSURL_RE.finditer(src):
        v = m.group(1)
        if not v.startswith("data:"):
            urls.add(urljoin(base_url, dearchive(v)))
    return urls

def is_html_url(url):
    p = urlparse(url)
    seg = p.path.rsplit("/", 1)[-1]
    if ASSET_EXT.search(seg):
        return False
    return True

def get(original):
    url = wb_url(original)
    for attempt in range(4):
        try:
            r = session.get(url, timeout=45, allow_redirects=True)
            return r
        except Exception as e:
            if attempt == 3:
                print("  FAIL", original, e)
                return None
            time.sleep(2)

html_queue = deque([canon(START)])
html_seen = set(html_queue)
assets = set()
pages_done = 0
MAX_PAGES = int(os.environ.get("MAX_PAGES", "400"))

while html_queue and pages_done < MAX_PAGES:
    url = html_queue.popleft()
    if SKIP_RE.search(url) or not same_site(url):
        continue
    r = get(url)
    if not r or r.status_code != 200:
        print("  skip", r.status_code if r else "ERR", url)
        continue
    ctype = r.headers.get("Content-Type", "")
    if "text/html" not in ctype and "<html" not in r.text[:500].lower():
        save(url, r.content, is_html=False)
        continue
    text = r.text
    save(url, r.content, is_html=True)
    pages_done += 1
    print(f"[page {pages_done}] {url}")
    for u in extract(url, text):
        u = canon(u)
        if SKIP_RE.search(u):
            continue
        if same_site(u):
            if is_html_url(u):
                if u not in html_seen:
                    html_seen.add(u)
                    html_queue.append(u)
            else:
                assets.add(u)
        # external assets (fonts.googleapis, etc.) skipped for now
    time.sleep(0.2)

print(f"\nPages: {pages_done}. Assets: {len(assets)}")

done_assets = 0
css_extra = deque()
for u in list(assets):
    if not same_site(u):
        continue
    r = get(u)
    if not r or r.status_code != 200:
        print("  asset skip", r.status_code if r else "ERR", u)
        continue
    is_css = u.lower().split("?")[0].endswith(".css") or "css" in r.headers.get("Content-Type", "")
    save(u, r.content, is_html=False)
    done_assets += 1
    if is_css:
        for cu in extract(u, r.text, css=True):
            if same_site(cu) and canon(cu) not in assets:
                css_extra.append(canon(cu))

for u in css_extra:
    r = get(u)
    if not r or r.status_code != 200:
        continue
    save(u, r.content, is_html=False)
    done_assets += 1

print(f"Assets fetched: {done_assets}. Total mapped: {len(url_local)}")
os.makedirs(ROOT, exist_ok=True)
with open(os.path.join(ROOT, "_urlmap.json"), "w") as f:
    json.dump(url_local, f)
print("Saved urlmap.")
