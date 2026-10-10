#!/usr/bin/env python3
"""SEO, schema, brand and internal-link audit for the generated Factor42 site.

Run: python3 _build/audit_site.py .   (prints a report; exit code 1 if any ERROR)
"""
import sys, re, json, pathlib, collections
from html.parser import HTMLParser

ROOT = pathlib.Path(sys.argv[1]).resolve()
BASE = "https://factor42media.com"
PALETTE = {"#0b1626", "#4a5264", "#5a6272", "#f5f3ee", "#edeae3", "#ffffff", "#fff", "#d9d5cc", "#e6e2da", "#b9b3a7",
           "#c2410c", "#9a3409", "#f4a26b", "#fde7da", "#b8bfcc", "#d5dae3", "#9aa3b3", "#6b7282", "#3a4254", "#26303f",
           "#1c2a40", "#eeebe4", "#faf9f6", "#c9c4b9", "#7c2a08", "#9a1c0c", "#fdece8"}
FONTS = {"Schibsted Grotesk", "Geist", "Geist Mono"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self._in = None; self.meta = {}; self.links = []; self.canonical = None
        self.h = []; self.ld = []; self._ld = None; self.imgs = []; self.text = []; self._main = 0
        self.main_links = []; self._hbuf = None; self.robots = ""; self._skip = 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "title": self._in = "title"
        elif tag == "meta":
            k = a.get("name") or a.get("property") or a.get("http-equiv")
            if k: self.meta[k.lower()] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self._main: self.main_links.append(a["href"])
        elif tag == "script" and a.get("type") == "application/ld+json": self._ld = []
        elif tag in ("script", "style"): self._skip += 1
        elif tag in ("h1", "h2", "h3", "h4"): self._hbuf = [tag, ""]
        elif tag == "img": self.imgs.append(a)
        elif tag == "main": self._main += 1

    def handle_endtag(self, tag):
        if tag == "title": self._in = None
        elif tag == "script" and self._ld is not None:
            self.ld.append("".join(self._ld)); self._ld = None
        elif tag in ("script", "style") and self._skip: self._skip -= 1
        elif tag in ("h1", "h2", "h3", "h4") and self._hbuf and self._hbuf[0] == tag:
            self.h.append((tag, self._hbuf[1].strip())); self._hbuf = None
        elif tag == "main": self._main -= 1

    def handle_data(self, d):
        if self._in == "title": self.title += d
        if self._ld is not None: self._ld.append(d); return
        if self._skip: return
        if self._hbuf: self._hbuf[1] += d
        if self._main: self.text.append(d)


def url_for(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html": return f"{BASE}/"
    if rel.endswith("/index.html"): return f"{BASE}/{rel[:-10]}"
    return f"{BASE}/{rel[:-5]}"


def resolve(href, page_url):
    from urllib.parse import urljoin, urlparse
    u = urljoin(page_url, href)
    p = urlparse(u)
    if p.netloc not in ("factor42media.com", "www.factor42media.com"): return None
    path = p.path
    if path.endswith("/") and path != "/" and not path.endswith("/blog/"): path = path.rstrip("/")
    return f"{BASE}{path}"


pages = {}
for f in sorted(ROOT.rglob("*.html")):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(("_build/", "_worker/", "node_modules/")): continue
    p = Page(); src = f.read_text(encoding="utf-8"); p.feed(src); p.src = src
    pages[url_for(f)] = p

issues = collections.defaultdict(list)   # url -> [(level, msg)]
def flag(u, lvl, msg): issues[u].append((lvl, msg))

redirects = {u for u, p in pages.items() if "refresh" in p.meta}
indexable = {u for u, p in pages.items() if u not in redirects and "noindex" not in p.meta.get("robots", "")}
sitemap = set(re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text()))

inbound = collections.Counter(); inbound_body = collections.Counter()
titles = collections.defaultdict(list); descs = collections.defaultdict(list)
schema_types = collections.Counter()

for u, p in pages.items():
    if u in redirects:
        tgt = p.meta["refresh"].split("url=", 1)[-1]
        if not p.canonical: flag(u, "ERROR", "redirect page without canonical")
        if (resolve(tgt, u) or "").split("#")[0] not in pages and not tgt.startswith(BASE + "/#"):
            flag(u, "ERROR", f"redirect target missing: {tgt}")
        continue
    is_idx = u in indexable
    t = p.title.strip(); d = p.meta.get("description", "").strip()
    if is_idx:
        titles[t].append(u); descs[d].append(u)
        if not t: flag(u, "ERROR", "missing <title>")
        elif len(t) > 65: flag(u, "WARN", f"title {len(t)} chars (>65): {t}")
        elif len(t) < 25: flag(u, "WARN", f"title short ({len(t)}): {t}")
        if not d: flag(u, "ERROR", "missing meta description")
        elif len(d) > 160: flag(u, "WARN", f"description {len(d)} chars (>160)")
        elif len(d) < 70: flag(u, "WARN", f"description short ({len(d)})")
        if p.canonical != u: flag(u, "ERROR", f"canonical {p.canonical} != {u}")
        for k in ("og:title", "og:description", "og:image", "og:url", "twitter:card"):
            if k not in p.meta: flag(u, "ERROR", f"missing {k}")
        if p.meta.get("og:url") and p.meta["og:url"] != u: flag(u, "ERROR", f"og:url {p.meta['og:url']} != {u}")
        img = p.meta.get("og:image", "")
        if img.startswith(BASE) and not (ROOT / img[len(BASE) + 1:]).exists(): flag(u, "ERROR", f"og:image file missing: {img}")
        if "/blog/" in u and u != f"{BASE}/blog/" and "/assets/img/blog/" not in img: flag(u, "WARN", "article uses the generic share image")
        if u not in sitemap: flag(u, "ERROR", "indexable page missing from sitemap")
    h1s = [h for h in p.h if h[0] == "h1"]
    if len(h1s) != 1: flag(u, "ERROR", f"{len(h1s)} <h1> tags")
    last = 1
    for tag, txt in p.h:
        lvl = int(tag[1])
        if lvl > last + 1: flag(u, "WARN", f"heading jumps h{last}->h{lvl} at '{txt[:40]}'")
        last = lvl
    for img in p.imgs:
        if "alt" not in img: flag(u, "ERROR", f"img without alt: {img.get('src')}")
    # JSON-LD
    if is_idx and not p.ld: flag(u, "ERROR", "no JSON-LD")
    for blob in p.ld:
        try:
            data = json.loads(blob)
        except Exception as e:
            flag(u, "ERROR", f"invalid JSON-LD: {e}"); continue
        nodes = data.get("@graph", [data])
        for n in nodes:
            ty = n.get("@type"); schema_types[ty] += 1
            if ty == "BlogPosting":
                for k in ("headline", "datePublished", "author", "publisher", "image", "mainEntityOfPage", "description"):
                    if k not in n: flag(u, "ERROR", f"BlogPosting missing {k}")
                if len(n.get("headline", "")) > 110: flag(u, "WARN", "BlogPosting headline >110 chars")
            if ty == "FAQPage":
                for q in n.get("mainEntity", []):
                    if q["name"] not in p.src: flag(u, "ERROR", f"FAQ schema question not visible on page: {q['name'][:40]}")
            if ty == "Organization" and "address" not in n: flag(u, "INFO", "Organization has no address")
        if is_idx and u != f"{BASE}/" and "BreadcrumbList" not in blob: flag(u, "INFO", "no BreadcrumbList")
    # links
    body_internal = set()
    for href in p.links:
        r = resolve(href, u)
        if r:
            r0 = r.split("#")[0]
            if r0 not in pages: flag(u, "ERROR", f"broken internal link: {href}")
            elif r0 != u: inbound[r0] += 1
    for href in p.main_links:
        r = resolve(href, u)
        if r and r.split("#")[0] != u: body_internal.add(r.split("#")[0])
    p.body_internal = body_internal
    m_prose = re.search(r'<div class="prose">(.*?)</div>\s*<aside', p.src, re.S)
    p.prose_links = {resolve(h, u).split("#")[0] for h in re.findall(r'<a href="([^"]+)"', m_prose.group(1))
                     if resolve(h, u) and "/contact" not in h} if m_prose else set()
    for r in body_internal: inbound_body[r] += 1
    # brand
    text = " ".join(p.text)
    for bad in re.findall(r"Factor 42(?! Blog)|FACTOR 42|factor 42|Factor-42|Factor42media(?!\.com)", text):
        flag(u, "WARN", f"brand name written as '{bad}'")
    for m in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", re.sub(r"<script.*?</script>", "", p.src, flags=re.S)):
        if m.lower() not in PALETTE: flag(u, "WARN", f"off-palette colour {m}")
    for need, what in (('class="site-header"', "shared header"), ('class="site-footer', "shared footer"),
                       ('class="brand-mark"', "logo mark"), ('Factor<sup>42</sup>', "wordmark"), ("assets/css/site.css", "site stylesheet")):
        if need not in p.src: flag(u, "ERROR", f"brand: missing {what}")
    if is_idx and not re.search(r"Factor42 Media", t) and "blog/" not in u: flag(u, "WARN", "title lacks 'Factor42 Media'")
    if re.search(r"fonts\.googleapis|cdn\.|unpkg|jsdelivr", p.src): flag(u, "WARN", "loads third-party asset")

css = (ROOT / "assets/css/site.css").read_text()
for m in sorted(set(c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", css)) - PALETTE):
    flag("assets/css/site.css", "WARN", f"off-palette colour {m}")
for fam in set(re.findall(r'font-family:\s*"([^"]+)"', css)) - FONTS:
    flag("assets/css/site.css", "WARN", f"unexpected font {fam}")

for t, us in titles.items():
    if len(us) > 1: [flag(x, "ERROR", f"duplicate title shared with {len(us)-1} other page(s)") for x in us]
for d, us in descs.items():
    if d and len(us) > 1: [flag(x, "ERROR", f"duplicate description shared with {len(us)-1} other page(s)") for x in us]
for u in indexable:
    if inbound[u] == 0: flag(u, "ERROR", "orphan: no internal links point here")
    if u.startswith(f"{BASE}/blog/") and u != f"{BASE}/blog/":
        if inbound_body[u] < 2: flag(u, "WARN", f"only {inbound_body[u]} in-content link(s) from other pages")
        if len(pages[u].prose_links) < 1: flag(u, "WARN", "no links inside the article text")
for s in sitemap:
    if s not in indexable: flag("sitemap.xml", "ERROR", f"sitemap lists non-indexable/missing URL {s}")

robots = (ROOT / "robots.txt").read_text()
llms = (ROOT / "llms.txt").read_text() if (ROOT / "llms.txt").exists() else ""
blog_urls = [u for u in indexable if u.startswith(f"{BASE}/blog/") and u != f"{BASE}/blog/"]
missing_llms = [u for u in blog_urls if u not in llms]
if missing_llms: flag("llms.txt", "INFO", f"{len(missing_llms)} of {len(blog_urls)} articles not listed")
for bot in ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended"):
    if bot not in robots: flag("robots.txt", "INFO", f"no explicit rule for {bot}")

# ---- report
lv = collections.Counter(l for v in issues.values() for l, _ in v)
by_msg = collections.Counter()
for v in issues.values():
    for l, m in v:
        key = re.sub(r"\d+", "N", m.split(":")[0])
        by_msg[(l, key)] += 1
print(f"pages: {len(pages)} | indexable: {len(indexable)} | redirects: {len(redirects)} | sitemap URLs: {len(sitemap)}")
print(f"schema types: {dict(schema_types)}")
print(f"ERROR {lv['ERROR']} | WARN {lv['WARN']} | INFO {lv['INFO']}")
for (l, k), n in sorted(by_msg.items(), key=lambda x: ({'ERROR': 0, 'WARN': 1, 'INFO': 2}[x[0][0]], -x[1])):
    print(f"  {l:5} x{n:<4} {k}")
if "-v" in sys.argv:
    for u, v in sorted(issues.items()):
        for l, m in v: print(f"{l:5} {u.replace(BASE,'')}  {m}")
prose_in = collections.Counter(t for u in blog_urls for t in pages[u].prose_links)
avg_out = sum(len(pages[u].prose_links) for u in blog_urls) / max(1, len(blog_urls))
print(f"articles: in-text links out avg {avg_out:.1f} (min {min(len(pages[u].prose_links) for u in blog_urls)}); "
      f"links in from other pages' content min {min(inbound_body[u] for u in blog_urls)}; in-text links in avg {sum(prose_in.values())/len(blog_urls):.1f}")
print(f"every indexable page has at least {min(inbound[u] for u in indexable)} internal links pointing to it")
sys.exit(1 if lv["ERROR"] else 0)
