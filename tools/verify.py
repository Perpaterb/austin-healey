#!/usr/bin/env python3
"""Audit a captured site: broken local resource links + remaining missing refs."""
import os, re, sys, posixpath
from urllib.parse import urlparse, unquote

SITEDIR = sys.argv[1]
DOMAINS = sys.argv[2].split(",")

RES_RE = re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
IMG_RE = re.compile(r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']', re.I)

broken_local = []
missing_abs = {}
img_total = img_broken = 0

for dp, _, files in os.walk(SITEDIR):
    for fn in files:
        if not fn.lower().endswith((".html", ".htm")): continue
        path = os.path.join(dp, fn)
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        # broken local resource links
        for m in RES_RE.finditer(text):
            v = m.group(1).strip()
            if v.startswith(("http://", "https://", "//", "data:", "#", "mailto:", "tel:", "javascript:")):
                continue
            target = posixpath.normpath(posixpath.join(dp, unquote(v.split("?")[0].split("#")[0])))
            if not os.path.exists(target):
                broken_local.append((os.path.relpath(path, SITEDIR), v))
        # remaining absolute same-domain (genuinely uncaptured/unarchived)
        for m in re.finditer(r'(?:https?:)?//(?:www\.)?(?:' + "|".join(re.escape(d) for d in DOMAINS) + r')/[^"\'\) <>]*', text):
            u = m.group(0)
            if re.search(r'wp-json|xmlrpc|/feed|oembed|api\.w\.org|/comments|\?ical=|events-calendars|tribe-bar-date', u, re.I):
                continue
            missing_abs[u.split("?")[0]] = missing_abs.get(u.split("?")[0], 0) + 1
        # image stats
        for m in IMG_RE.finditer(text):
            v = m.group(1).strip()
            img_total += 1
            if v.startswith(("http://", "https://", "//")):
                img_broken += 1  # still remote = not captured locally
            else:
                target = posixpath.normpath(posixpath.join(dp, unquote(v.split("?")[0])))
                if not os.path.exists(target):
                    img_broken += 1

print(f"  <img> tags: {img_total}, not-resolving-locally: {img_broken}")
print(f"  broken LOCAL resource links: {len(broken_local)}")
for f, v in broken_local[:8]:
    print(f"     {f}  ->  {v}")
print(f"  distinct remaining same-domain absolute refs (asset/page): {len(missing_abs)}")
ass = {k: v for k, v in missing_abs.items() if re.search(r'\.(png|jpg|jpeg|gif|webp|svg|css|js|pdf)$', k, re.I)}
print(f"     of which look like ASSETS (likely unarchived/broken at source): {len(ass)}")
for k in list(ass)[:12]:
    print(f"     IMG/ASSET miss: {k}")
