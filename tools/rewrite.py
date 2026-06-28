#!/usr/bin/env python3
"""Rewrite captured HTML/CSS so links point to local relative files.

Usage: rewrite.py <ROOT> <SITE_SUBDIR>
Reads <ROOT>/_urlmap.json (original-URL -> local-relative-path).
For every .html/.css file, resolves each URL against the file's own original
URL, maps it to the captured local file, and substitutes a relative path.
"""
import os, re, sys, json, posixpath
from urllib.parse import urljoin, urlparse, urldefrag

ROOT = sys.argv[1]
SUBDIR = sys.argv[2]
SITEDIR = os.path.join(ROOT, SUBDIR)

with open(os.path.join(ROOT, "_urlmap.json")) as f:
    url_local = json.load(f)

# invert: local-rel -> original url (first wins)
local_url = {}
for u, rel in url_local.items():
    local_url.setdefault(rel, u)

def canon(url):
    return urldefrag(url)[0]

def toggle_www(url):
    p = urlparse(url)
    if p.netloc.startswith("www."):
        new = p._replace(netloc=p.netloc[4:])
    else:
        new = p._replace(netloc="www." + p.netloc)
    return new.geturl()

def lookup(orig):
    orig = canon(orig)
    if orig in url_local:
        return url_local[orig]
    t = toggle_www(orig)
    if t in url_local:
        return url_local[t]
    # try http<->https
    for variant in (orig.replace("https://", "http://", 1),
                    orig.replace("http://", "https://", 1)):
        if variant in url_local:
            return url_local[variant]
        vt = toggle_www(variant)
        if vt in url_local:
            return url_local[vt]
    return None

def dearchive(u):
    m = re.match(r"https?://web\.archive\.org/web/\d+(?:id_|if_|im_|cs_|js_)?/(.*)", u)
    return m.group(1) if m else u

URL_ATTR_RE = re.compile(r'((?:src|href|data-src|poster)\s*=\s*)(["\'])([^"\']+)(\2)', re.I)
SRCSET_RE = re.compile(r'(srcset\s*=\s*)(["\'])([^"\']+)(\2)', re.I)
CSSURL_RE = re.compile(r'(url\(\s*)(["\']?)([^"\')]+)(["\']?\s*\))', re.I)

stats = {"rewritten": 0, "files": 0, "miss": 0}

def make_rel(target_rel, cur_rel):
    cur_dir = posixpath.dirname(cur_rel)
    rp = posixpath.relpath(target_rel, cur_dir or ".")
    return rp

def rewrite_file(path, cur_rel, base_url):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    def repl_url(v):
        v_clean = v.strip()
        if v_clean.startswith(("data:", "#", "mailto:", "tel:", "javascript:")):
            return None
        absu = urljoin(base_url, dearchive(v_clean))
        rel = lookup(absu)
        if rel is None:
            stats["miss"] += 1
            return None
        stats["rewritten"] += 1
        return make_rel(rel, cur_rel)

    def attr_sub(m):
        pre, q, val, q2 = m.group(1), m.group(2), m.group(3), m.group(4)
        nv = repl_url(val)
        return f"{pre}{q}{nv}{q}" if nv else m.group(0)

    def srcset_sub(m):
        pre, q, val, _ = m.group(1), m.group(2), m.group(3), m.group(4)
        out = []
        changed = False
        for part in val.split(","):
            part = part.strip()
            if not part:
                continue
            bits = part.split(None, 1)
            nv = repl_url(bits[0])
            if nv:
                changed = True
                bits[0] = nv
            out.append(" ".join(bits))
        return f"{pre}{q}{', '.join(out)}{q}" if changed else m.group(0)

    def css_sub(m):
        pre, q, val, post = m.group(1), m.group(2), m.group(3), m.group(4)
        nv = repl_url(val)
        return f"{pre}{q}{nv}{post}" if nv else m.group(0)

    text = URL_ATTR_RE.sub(attr_sub, text)
    text = SRCSET_RE.sub(srcset_sub, text)
    text = CSSURL_RE.sub(css_sub, text)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

for dirpath, _, files in os.walk(SITEDIR):
    for fn in files:
        if not fn.lower().endswith((".html", ".htm", ".css")):
            continue
        path = os.path.join(dirpath, fn)
        cur_rel = os.path.relpath(path, SITEDIR).replace(os.sep, "/")
        base_url = local_url.get(cur_rel)
        if not base_url:
            continue
        stats["files"] += 1
        rewrite_file(path, cur_rel, base_url)

print(f"Files rewritten: {stats['files']}, links localised: {stats['rewritten']}, "
      f"left external/uncaptured: {stats['miss']}")
