#!/usr/bin/env python3
"""Render a 1200x630 social share image for every blog article.

Reads the generated blog pages (title + topic), renders each card in headless Chromium with the
site's own fonts, and writes assets/img/blog/<slug>.png. Run after build_pages.py, then run
build_pages.py again so pages point at the images (it uses an article's image only if the file exists).

    python3 _build/render_og.py .
"""
import sys, re, html, json, pathlib, hashlib
from playwright.sync_api import sync_playwright

SITE = pathlib.Path(sys.argv[1]).resolve()
OUT = SITE / "assets" / "img" / "blog"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = (SITE / "assets" / "fonts").as_uri()
MARK = (SITE / "assets" / "img" / "mark.svg").read_text()
LOGO = (SITE / "assets" / "img" / "logo.svg").read_text()
MANIFEST = OUT / "manifest.json"

# one look per topic, all from the brand palette
THEMES = {
    "Channels & platforms": dict(bg="#F5F3EE", ink="#0B1626", accent="#C2410C", muted="#4A5264", bar="#C2410C", logo="light"),
    "Strategy & budget":    dict(bg="#0B1626", ink="#F5F3EE", accent="#F4A26B", muted="#B8BFCC", bar="#C2410C", logo="dark"),
    "Choosing a partner":   dict(bg="#EDEAE3", ink="#0B1626", accent="#C2410C", muted="#4A5264", bar="#0B1626", logo="light"),
    "Seasonal & timing":    dict(bg="#C2410C", ink="#FFFFFF", accent="#FDE7DA", muted="#FDE7DA", bar="#0B1626", logo="rust"),
}


LOGO_COLORS = {  # logo colours: ink square + wordmark, paper "F", rust exponent + "42", slate "MEDIA"
    "light": {},
    "dark": {"#0B1626": "#F5F3EE", "#F5F3EE": "#0B1626", "#C2410C": "#F4A26B", "#4A5264": "#B8BFCC"},
    "rust": {"#0B1626": "#FFFFFF", "#F5F3EE": "#C2410C", "#C2410C": "#0B1626", "#4A5264": "#FDE7DA"},
}


def logo_svg(variant):
    s = LOGO.replace("<svg ", '<svg style="width:100%;height:auto" ', 1)
    swap = LOGO_COLORS[variant]
    return re.sub(r'fill="(#[0-9A-Fa-f]{6})"', lambda m: f'fill="{swap.get(m.group(1).upper(), m.group(1))}"', s)


def card_html(title, topic, mins):
    t = THEMES.get(topic, THEMES["Channels & platforms"])
    n = len(title)
    size = 76 if n <= 45 else 66 if n <= 62 else 58 if n <= 80 else 50
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: D; font-weight: 800; src: url('{FONTS}/schibsted-grotesk-latin-800-normal.woff2'); }}
@font-face {{ font-family: M; font-weight: 400; src: url('{FONTS}/geist-mono-latin-400-normal.woff2'); }}
html,body {{ margin:0; }}
.c {{ width:1200px; height:630px; box-sizing:border-box; background:{t['bg']}; position:relative; overflow:hidden;
      padding:64px 80px 78px; display:flex; flex-direction:column; justify-content:space-between; }}
.top {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.logo {{ width:300px; }}
.topic {{ font-family:M; font-size:20px; letter-spacing:.14em; text-transform:uppercase; color:{t['accent']}; text-align:right; line-height:1.5; }}
.topic span {{ display:block; color:{t['muted']}; }}
h1 {{ margin:0; font-family:D; font-weight:800; font-size:{size}px; line-height:1.02; letter-spacing:-0.035em; color:{t['ink']}; max-width:1000px; }}
.foot {{ font-family:M; font-size:19px; letter-spacing:.14em; color:{t['muted']}; }}
.mark {{ position:absolute; right:-60px; bottom:-70px; width:380px; height:380px; opacity:.07; }}
.mark svg {{ width:100%; height:100%; }}
.bar {{ position:absolute; left:0; right:0; bottom:0; height:14px; background:{t['bar']}; }}
</style></head><body><div class="c">
<div class="top"><div class="logo">{logo_svg(t['logo'])}</div><div class="topic">{html.escape(topic)}<span>{mins} min read</span></div></div>
<h1>{html.escape(title)}</h1>
<div class="foot">FACTOR42MEDIA.COM/BLOG</div>
<div class="mark">{MARK}</div><div class="bar"></div>
</div></body></html>"""


articles = []
for f in sorted((SITE / "blog").glob("*.html")):
    src = f.read_text(encoding="utf-8")
    if f.name == "index.html" or 'http-equiv="refresh"' in src:
        continue
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", src, re.S).group(1))
    topic = html.unescape(re.search(r'"articleSection": "([^"]+)"', src).group(1))
    mins = re.search(r"(\d+) min read", src).group(1)
    articles.append((f.stem, title, topic, mins))

manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
todo = []
for slug, title, topic, mins in articles:
    key = hashlib.sha1(f"{title}|{topic}|{mins}|v1".encode()).hexdigest()[:12]
    if manifest.get(slug) != key or not (OUT / f"{slug}.png").exists():
        todo.append((slug, title, topic, mins, key))

tmp = pathlib.Path(__file__).parent / "_og_render.html"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    for slug, title, topic, mins, key in todo:
        tmp.write_text(card_html(title, topic, mins), encoding="utf-8")
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(60)
        pg.screenshot(path=str(OUT / f"{slug}.png"), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        manifest[slug] = key
    b.close()
tmp.unlink(missing_ok=True)
live = {a[0] for a in articles}
for stale in [s for s in manifest if s not in live]:
    (OUT / f"{stale}.png").unlink(missing_ok=True); manifest.pop(stale)
MANIFEST.write_text(json.dumps(manifest, indent=0, sort_keys=True) + "\n")
print(f"share images: {len(articles)} articles, {len(todo)} rendered")
