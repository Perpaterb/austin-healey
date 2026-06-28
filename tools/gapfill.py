#!/usr/bin/env python3
"""Fetch same-domain resources still referenced but not yet captured.

Usage: gapfill.py <ROOT> <SUBDIR> <live|wayback>
Iterates: scan on-disk HTML/CSS for uncaptured same-domain URLs, fetch them,
save, update _urlmap.json. Repeats until no new gaps (or pass limit).
Self-consistent: each saved file's path is what goes into the map, so the
later rewrite pass localises them correctly.
"""
import os, re, sys, time, json
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

ROOT, SUBDIR, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
SITEDIR = os.path.join(ROOT, SUBDIR)
TS = "20240410061034"
WB = "https://web.archive.org"
MAX_PASSES = int(os.environ.get("MAX_PASSES", "6"))

if MODE == "live":
    DOMAINS = ("ahocnsw.org.au",)
    UA = "Mozilla/5.0"
else:
    DOMAINS = ("austinhealeynsw.com.au",)
    UA = "Mozilla/5.0 (compatible; site-archive/1.0)"

session = requests.Session(); session.headers.update({"User-Agent": UA})

JUNK_RE = re.compile(
    r"(wp-json|xmlrpc|/feed|oembed|api\.w\.org|/comments|replytocom"
    r"|events-calendars|tribe-bar-date|outlook-ical|[?&]ical=|eventDisplay|tribe_"
    r"|[?&]to=|/login|/logout|forgot-login|/rsvp/|/cart|/checkout"
    r"|[?&]p=\d|/embed/?$|/amp/?$|/a$|\.ics$|mailto:|tel:|javascript:|#)", re.I)
ASSET_EXT = re.compile(r"\.(css|js|jpg|jpeg|png|gif|webp|svg|ico|woff2?|ttf|eot|otf|mp4|webm|pdf|mp3)$", re.I)

with open(os.path.join(ROOT, "_urlmap.json")) as f:
    url_local = json.load(f)

def canon(u): return urldefrag(u)[0]

def same_site(u):
    h = urlparse(u).netloc.lower()
    return any(h == d or h == "www." + d for d in DOMAINS)

def dearchive(u):
    m = re.match(r"https?://web\.archive\.org/web/\d+(?:id_|if_|im_|cs_|js_)?/(.*)", u)
    return m.group(1) if m else u

def sanitize_query(q): return "@" + re.sub(r"[^A-Za-z0-9._-]", "_", q)

def local_path_for(url, is_html):
    p = urlparse(url); path, query = p.path, p.query
    if path in ("", "/"):
        return "index.html"
    if path.endswith("/"):
        stem = path.lstrip("/") + ("index" + (sanitize_query(query) if query else "") + ".html")
        return stem
    base = path.lstrip("/"); seg = base.rsplit("/", 1)[-1]
    if ASSET_EXT.search(seg) or ("." in seg and not is_html and not seg.endswith(".php")):
        local = base
        if query:
            root, ext = os.path.splitext(local); local = root + sanitize_query(query) + ext
        return local
    if seg.endswith(".php") or is_html or "." not in seg:
        root = base[:-4] if seg.endswith(".php") else base
        return root + (sanitize_query(query) if query else "") + ".html"
    return base + (sanitize_query(query) if query else "")

def fetch(orig):
    url = WB + f"/web/{TS}id_/" + orig if MODE == "wayback" else orig
    for a in range(4):
        try:
            return session.get(url, timeout=45)
        except Exception:
            if a == 3: return None
            time.sleep(2)

URL_ATTR_RE = re.compile(r'(?:src|href|data-src|poster)\s*=\s*["\']([^"\']+)["\']', re.I)
SRCSET_RE = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
CSSURL_RE = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)

def extract(base, text, css=False):
    out = set()
    rxs = [CSSURL_RE] if css else [URL_ATTR_RE, CSSURL_RE]
    for rx in rxs:
        for m in rx.finditer(text):
            v = m.group(1)
            if v.startswith(("data:", "#", "mailto:", "tel:", "javascript:")): continue
            out.add(urljoin(base, dearchive(v)))
    if not css:
        for m in SRCSET_RE.finditer(text):
            for part in m.group(1).split(","):
                u = part.strip().split(" ")[0]
                if u and not u.startswith("data:"):
                    out.add(urljoin(base, dearchive(u)))
    return out

# Match only ABSOLUTE same-domain URLs (and wayback-wrapped ones). After the
# rewrite pass, captured links are relative; whatever is still absolute and
# same-domain is genuinely uncaptured. Resolving relative paths here would
# create phantom gaps, so we deliberately do not.
_hosts = "|".join(re.escape(d) for d in DOMAINS)
ABS_RE = re.compile(
    r'(?:https?://web\.archive\.org/web/\d+(?:id_|if_|im_|cs_|js_)?/)?'  # optional wayback wrapper
    r'(?:https?:)?//(?:www\.)?(?:' + _hosts + r')/[^"\'\) <>]*',
    re.I)

def scan_disk_for_gaps():
    gaps = set()
    for dp, _, files in os.walk(SITEDIR):
        for fn in files:
            if not fn.lower().endswith((".html", ".htm", ".css")): continue
            with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as f:
                text = f.read()
            for m in ABS_RE.finditer(text):
                raw = m.group(0)
                u = dearchive(raw)
                if u.startswith("//"):
                    u = "https:" + u
                u = canon(u.replace("&amp;", "&"))
                if same_site(u) and u not in url_local and not JUNK_RE.search(u):
                    gaps.add(u)
    return gaps

total_new = 0
for p in range(MAX_PASSES):
    gaps = scan_disk_for_gaps()
    if not gaps:
        print(f"pass {p+1}: no gaps, done.")
        break
    print(f"pass {p+1}: {len(gaps)} gaps to fetch")
    new = 0
    for u in sorted(gaps):
        r = fetch(u)
        if not r or r.status_code != 200:
            continue
        ctype = r.headers.get("Content-Type", "")
        is_html = ("text/html" in ctype) or (("<html" in r.text[:600].lower()) and not ASSET_EXT.search(urlparse(u).path))
        rel = local_path_for(u, is_html)
        fp = os.path.join(SITEDIR, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(r.content)
        url_local[canon(u)] = rel
        new += 1
        time.sleep(0.12)
    total_new += new
    print(f"   fetched {new}")
    with open(os.path.join(ROOT, "_urlmap.json"), "w") as f:
        json.dump(url_local, f)
    if new == 0:
        break

print(f"gapfill done: {total_new} new files. map size now {len(url_local)}")
