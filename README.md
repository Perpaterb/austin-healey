# Austin Healey Owners Club (NSW) — site archive

Local, offline-browsable replicas of the club's two previous websites, captured as a
reference base for building the new site.

## What's here

| Folder | Source | Era | Tech |
|--------|--------|-----|------|
| `old-site/` | <https://ahocnsw.org.au/> (live) | current | WordPress |
| `old-old-site/` | <http://www.austinhealeynsw.com.au/> via the Wayback Machine snapshot `20240410061034` | previous | hosted CMS |

Both are full static captures: HTML, CSS, JS, and images, with every internal link
rewritten to a relative path so they browse locally with no server or internet.

## Viewing

Open the entry page directly in a browser:

- Current site: `old-site/ahocnsw.org.au/index.html`
- Previous site: `old-old-site/austinhealeynsw.com.au/index.html`

Or serve either folder over HTTP (some browsers are stricter about `file://`):

```
python3 -m http.server -d old-site/ahocnsw.org.au 8001     # then open http://localhost:8001
python3 -m http.server -d old-old-site/austinhealeynsw.com.au 8002
```

## Capture notes & known gaps

**Current site (`old-site/`)** — complete. All 54 pages and every referenced image
resolve locally. The live site sits behind a WAF that blocks `wget` (TLS fingerprint),
so it was captured with the `requests`-based crawler in `tools/`. The Tribe Events
calendar generates an effectively infinite space of date/list URLs; those calendar
*views* are excluded, but individual event pages are kept.

**Previous site (`old-old-site/`)** — as complete as the archive allows. Two caveats:

- **Missing images.** The Internet Archive only ever captured ~9 of this domain's
  images, so most of the CMS gallery/hero/news photos are not recoverable from
  Wayback. Every missing image is listed in `old-old-site/MISSING-IMAGES.txt`
  (143 files) so they can be re-sourced from the club's own originals.
- **`.html.html` filenames.** A few pages exist in two eras under the same name (e.g.
  the CMS `/contact` and the older FrontPage `/contact.html`). The doubled extension
  keeps these distinct rather than overwriting one with the other.
- Some shop/cart/login chrome links from the CMS template were never archived and
  are left as dead links; they were not part of the site's content.
- **Documents recovered.** All 160 PDFs the archive holds for this domain were pulled
  in, including the full run of *Flat Chat* newsletters (2020-2025) plus membership
  forms, constitutions, rally papers and competition results. Browse them at
  `old-old-site/austinhealeynsw.com.au/newsletters-archive.html` (also linked from the
  newsletters page).

## Tools

The scrapers used to build this archive live in `tools/` and are re-runnable
(`tools/` needs Python 3 with `requests`; a venv is fine):

| Script | Purpose |
|--------|---------|
| `crawl_live.py` | Mirror the live WordPress site (BFS, page requisites). |
| `crawl_wayback.py` | Rebuild a site from a Wayback snapshot via the raw `id_` endpoint. |
| `gapfill.py` | Fetch any same-domain resources still referenced but not yet captured. |
| `rewrite.py` | Rewrite absolute/Wayback URLs to local relative paths. |
| `verify.py` | Audit a capture for broken local links and missing resources. |

Typical flow: `crawl_*` → `rewrite` → `gapfill` → `rewrite` → `verify`.
