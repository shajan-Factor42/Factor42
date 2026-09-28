#!/usr/bin/env python3
"""Assemble the Factor42 static pages from shared partials.

Output is plain, complete HTML in the repo root — no runtime templating, so every
word, link and piece of structured data is in the page source that search engines read.
Run: python3 build_pages.py <repo_dir>
"""
import json, sys, pathlib

OUT = pathlib.Path(sys.argv[1])
BASE = "https://factor42media.com"
WEB3FORMS_KEY = "afa90fc4-141b-45da-a8cb-7c4adcd1951d"
# Set to the Cloudflare Worker URL (see _worker/README.md) to send the form through Resend instead of Web3Forms
FORM_ENDPOINT = ""
LINKEDIN = "https://www.linkedin.com/company/factor42media/"

ORG = {
    "@type": "Organization",
    "@id": f"{BASE}/#org",
    "name": "Factor42 Media",
    "legalName": "Factor42 Media Inc.",
    "url": f"{BASE}/",
    "logo": f"{BASE}/assets/img/logo-512.png",
    "description": "White-label ad operations and campaign fulfillment for agencies and media companies.",
    "sameAs": [LINKEDIN],
}


def mark(on_ink=False, cls="brand-mark", size=None):
    sq, f, ex = ("#F5F3EE", "#0B1626", "#F4A26B") if on_ink else ("#0B1626", "#F5F3EE", "#C2410C")
    dims = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg class="{cls}"{dims} viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            f'<rect x="0" y="10" width="38" height="38" rx="7" fill="{sq}"/>'
            f'<rect x="10" y="19" width="6.5" height="20" fill="{f}"/>'
            f'<rect x="10" y="19" width="18" height="6" fill="{f}"/>'
            f'<rect x="10" y="28.5" width="13" height="5.5" fill="{f}"/>'
            f'<rect x="40" y="0" width="8" height="8" rx="2" fill="{ex}"/></svg>')


BRAND_WORD = '<span class="brand-word">Factor<sup>42</sup></span>'


def head(title, desc, path, graph=None, noindex=False, pre="", og_type="website", extra=""):
    a = pre
    url = f"{BASE}/{path}"
    ld = ""
    if graph is not None:
        ld = ('<script type="application/ld+json">'
              + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
              + "</script>")
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    canonical = "" if noindex else f'<link rel="canonical" href="{url}">\n'
    fb = '<meta name="facebook-domain-verification" content="1ievhlaysp0e671sdb05lk6szhztvl">\n' if path == "" else ""
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{fb}<meta name="robots" content="{robots}">
{canonical}{extra}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Factor42 Media">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Factor42 Media — the ad ops team behind your brand">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B1626">
<link rel="icon" href="{a}assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{a}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{a}assets/img/apple-touch-icon.png">
<link rel="preload" href="{a}assets/fonts/schibsted-grotesk-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{a}assets/fonts/geist-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a}assets/css/site.css">
<script>document.documentElement.className='js';</script>
<script src="{a}assets/js/site.js" defer></script>
{ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


NAV = [("agencies", "Agencies"), ("broadcasters", "Broadcasters"), ("./#solutions", "Solutions"), ("about", "About"), ("blog/", "Blog")]


def header(active="", pre=""):
    p = pre
    home = pre or "./"
    def link(href, label):
        h = (pre or "./") + href[2:] if href.startswith("./") else pre + href
        cur = ' aria-current="page"' if href == active else ""
        return f'<li><a href="{h}"{cur}>{label}</a></li>'
    items = "\n".join(link(h, l) for h, l in NAV)
    mitems = "\n".join(link(h, l).replace("<li>", "").replace("</li>", "") for h, l in NAV)
    contact_cur = ' aria-current="page"' if active == "contact" else ""
    return f"""<header class="site-header">
<div class="wrap header-inner">
<a class="brand" href="{home}" aria-label="Factor42 Media home">{mark()}{BRAND_WORD}</a>
<nav class="nav" aria-label="Primary"><ul>
{items}
</ul></nav>
<div class="header-cta">
<a href="{p}contact"{contact_cur}>Contact</a>
<a class="btn btn-ink btn-sm" href="{p}contact">Book a consultation</a>
</div>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg></button>
</div>
<nav class="mobile-nav wrap" id="mobile-nav" aria-label="Mobile">
{mitems}
<a href="{p}contact"{contact_cur}>Contact</a>
<a class="btn btn-ink" href="{p}contact">Book a consultation</a>
</nav>
</header>
"""


def footer(pre=""):
    p = pre
    home = pre or "./"
    return f"""<footer class="site-footer on-ink">
<div class="wrap">
<div class="footer-grid">
<div class="footer-brand">
<a class="brand" href="{home}" aria-label="Factor42 Media home">{mark(on_ink=True)}{BRAND_WORD}</a>
<p>Full-service digital ad fulfillment for media companies and agencies. We execute your campaigns so you can focus on growth.</p>
<a href="{LINKEDIN}" rel="noopener">LinkedIn →</a>
</div>
<div class="footer-col">
<h2>Services</h2>
<a href="{p}agencies">For agencies</a>
<a href="{p}broadcasters">For broadcasters</a>
<a href="{p}agencies#ppc">White-label PPC &amp; paid social</a>
<a href="{home}#solutions">All channels</a>
</div>
<div class="footer-col">
<h2>Company</h2>
<a href="{p}about">About us</a>
<a href="{p}careers">Careers</a>
<a href="{p}blog/">Blog</a>
<a href="{p}contact">Contact</a>
</div>
<div class="footer-col">
<h2>Legal</h2>
<a href="{p}privacy-policy">Privacy policy</a>
<a href="{p}terms-of-service">Terms of service</a>
<a href="{p}sla">SLA</a>
<a href="{p}security">Security</a>
</div>
</div>
<div class="footer-base">
<span>© 2026 Factor42 Media Inc. All rights reserved.</span>
<span>Built for media companies &amp; agencies worldwide</span>
</div>
</div>
</footer>
</body>
</html>
"""


def cta(title, text=None, button="Book a free consultation", with_mark=False, pre=""):
    p = f"<p>{text}</p>" if text else ""
    art = ""
    if with_mark:
        art = ('<svg class="cta-mark" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
               '<rect x="0" y="10" width="38" height="38" rx="7" fill="#FFFFFF" fill-opacity="0.14"/>'
               '<rect x="10" y="19" width="6.5" height="20" fill="#FFFFFF"/>'
               '<rect x="10" y="19" width="18" height="6" fill="#FFFFFF"/>'
               '<rect x="10" y="28.5" width="13" height="5.5" fill="#FFFFFF"/>'
               '<rect x="40" y="0" width="8" height="8" rx="2" fill="#0B1626"/></svg>')
    cls = "cta-band cta-band--mark" if with_mark else "cta-band"
    return f"""<section class="{cls}">
<div class="wrap">
<div>
<h2>{title}</h2>
{p}
<div class="actions mt-16" style="margin-top:28px"><a class="btn btn-white" href="{pre}contact">{button} <span aria-hidden="true">→</span></a></div>
</div>
{art}
</div>
</section>
"""


def page(name, title, desc, path, active, body, graph=None, noindex=False):
    html = head(title, desc, path, graph, noindex) + header(active) + '<main id="main">\n' + body + "</main>\n" + footer()
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")


def redirect_page(name, target, title):
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{BASE}/{target}">
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
<p>This page has moved to <a href="{target}">{BASE}/{target}</a>.</p>
</body>
</html>
"""
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- pages
bodies = pathlib.Path(__file__).parent / "bodies"
body = lambda n: (bodies / f"{n}.html").read_text(encoding="utf-8")

FAQ = [
    ("Will my clients know you exist?", "No. Every report, dashboard and client-facing email carries your brand. We never contact your clients unless you ask us to."),
    ("Which platforms do you cover?", "Google Ads, YouTube, Meta, TikTok, LinkedIn, Reddit, X, Pinterest, Snapchat, DV360, The Trade Desk, Amazon DSP, major DOOH exchanges, connected TV and the major email platforms."),
    ("How fast can a campaign launch?", "Trafficking turnaround averages 12 minutes, and Google Ads campaigns launch in under four hours on average once the brief and creative are in."),
    ("What does it cost?", "Pricing depends on your channel mix and volume. Book a consultation and we will send a rate card built around what you sell."),
]
faq_html = "\n".join(f'<div class="row"><h3>{q}</h3><p>{a}</p></div>' for q, a in FAQ)

def contact_body():
    b = body("contact")
    if not FORM_ENDPOINT:
        return b.replace("{{KEY}}", WEB3FORMS_KEY)
    b = b.replace('action="https://api.web3forms.com/submit"', f'action="{FORM_ENDPOINT}"')
    drop = ['<input type="hidden" name="access_key" value="{{KEY}}">\n',
            '<input type="hidden" name="subject" value="New consultation request — factor42media.com">\n',
            '<input type="hidden" name="from_name" value="Factor42 website">\n',
            '<input type="hidden" name="redirect" value="https://factor42media.com/thank-you">\n']
    for d in drop:
        assert d in b, d
        b = b.replace(d, "")
    return b


page("index",
     "White-Label Ad Operations & Campaign Fulfillment | Factor42 Media",
     "White-label ad ops for agencies and media companies. We traffic, optimize and report on campaigns across every channel, under your brand.",
     "", "", body("home") + cta("Ready to scale your ad operations?", "Join 100+ media companies and agencies who trust Factor42 to execute their campaigns with speed and precision.", with_mark=True),
     graph=[ORG, {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/", "name": "Factor42 Media", "publisher": {"@id": f"{BASE}/#org"}}])

page("agencies",
     "White-Label Ad Ops & PPC for Agencies | Factor42 Media",
     "Add search, social, programmatic, CTV and DOOH without adding headcount. Factor42 runs your campaigns and reporting under your agency's brand.",
     "agencies", "agencies", body("agencies").replace("{{FAQ}}", faq_html) + cta("Add a channel to your agency this month."),
     graph=[ORG,
            {"@type": "Service", "name": "White-label ad operations for agencies", "serviceType": "White-label ad operations and campaign fulfillment", "provider": {"@id": f"{BASE}/#org"}, "url": f"{BASE}/agencies", "audience": {"@type": "BusinessAudience", "name": "Marketing and advertising agencies"}},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}])

page("broadcasters",
     "Digital Ad Fulfillment for TV & Radio Groups | Factor42 Media",
     "Give every seller in every market a full digital menu. Factor42 builds, launches and reports on digital campaigns for broadcast groups, under your brand.",
     "broadcasters", "broadcasters", body("broadcasters") + cta("Put a full digital menu in every seller's hands.", button="Talk to our broadcast team"),
     graph=[ORG, {"@type": "Service", "name": "Digital ad fulfillment for broadcast and media groups", "serviceType": "White-label digital advertising fulfillment", "provider": {"@id": f"{BASE}/#org"}, "url": f"{BASE}/broadcasters", "audience": {"@type": "BusinessAudience", "name": "TV and radio broadcast groups"}}])

page("about",
     "About Factor42 Media | White-Label Ad Operations",
     "Factor42 Media is a white-label ad operations and campaign fulfillment company. Agencies and media groups sell the campaigns; we run them under their names.",
     "about", "about", body("about") + cta("Let's talk about your ad operations."),
     graph=[ORG, {"@type": "AboutPage", "url": f"{BASE}/about", "name": "About Factor42 Media", "about": {"@id": f"{BASE}/#org"}}])

page("contact",
     "Book a Free Consultation | Factor42 Media",
     "Tell us what you sell and where. Factor42 will follow up with a fulfillment plan and a wholesale rate card built around your volume.",
     "contact", "contact", contact_body(),
     graph=[ORG, {"@type": "ContactPage", "url": f"{BASE}/contact", "name": "Book a consultation with Factor42 Media", "about": {"@id": f"{BASE}/#org"}}])

page("thank-you", "Thanks — we've got it | Factor42 Media", "Your consultation request has been received.",
     "thank-you", "", body("thank-you"), noindex=True)

# 404 is served at any missing path, so it uses root-absolute links
html404 = (head("Page not found | Factor42 Media", "This page could not be found.", "404", None, noindex=True, pre="/")
           + header("", pre="/") + '<main id="main">\n' + body("404") + "</main>\n" + footer(pre="/"))
(OUT / "404.html").write_text(html404, encoding="utf-8")

# Legal and company pages
def legal(name, h1, title, desc, eyebrow):
    body = (f'<article class="wrap post legal">\n<header class="post-head">\n<p class="eyebrow">{eyebrow}</p>\n<h1>{h1}</h1>\n</header>\n'
            f'<div class="prose">\n{body_of(name)}</div>\n</article>\n')
    page(name, title, desc, name, "", body, graph=[ORG, {"@type": "WebPage", "url": f"{BASE}/{name}", "name": h1, "about": {"@id": f"{BASE}/#org"}}])

body_of = lambda n: (bodies / f"{n}.html").read_text(encoding="utf-8")
legal("privacy-policy", "Privacy policy", "Privacy Policy | Factor42 Media", "How Factor42 Media collects, uses and protects information submitted through factor42media.com.", "Legal")
legal("terms-of-service", "Terms of service", "Terms of Service | Factor42 Media", "The terms that govern use of the factor42media.com website.", "Legal")
legal("sla", "Service level agreements", "Service Level Agreements | Factor42 Media", "How Factor42 service level agreements work: trafficking turnaround, QA, pacing, reporting, communication and escalation.", "Our commitments")
legal("security", "Security &amp; confidentiality", "Security & Confidentiality | Factor42 Media", "How Factor42 protects partner ad accounts, campaign data and client confidentiality.", "Trust")
page("careers", "Careers at Factor42 Media | Ad Ops Jobs", "Join the ad ops team behind agencies and media groups. Factor42 hires ad ops specialists, campaign managers and analysts.",
     "careers", "", body("careers"), graph=[ORG])

# Old URLs from the previous site
redirect_page("consultation", "contact", "Book a consultation | Factor42 Media")
redirect_page("white-label-ppc", "agencies#ppc", "White-label PPC | Factor42 Media")
redirect_page("library", "blog/", "Library | Factor42 Media")

print("built:", sorted(p.name for p in OUT.glob("*.html")))


# ================================================================ blog
import re, html as _html, math

ART_DIR = pathlib.Path(__file__).parent / "articles"
PUBLISHED = "2026-09-28"

CATS = [
    ("seasonal", "Seasonal & timing", ["holiday", "back-to-school", "summer", "q1", "political", "yearly", "calendar", "mid-year", "midyear", "timing", "last-minute", "season"]),
    ("partner", "Choosing a partner", ["agenc", "vendor", "provider", "contract", "proposal", "quote", "pricing", "retainer", "invoice", "red-flag", "buyer", "demand", "renew", "full-service", "three-models", "third-option", "cheaper", "cant-afford", "can-t-afford", "relationship", "expectations", "point-of-contact", "one-team", "switching", "logins", "tool-trap", "nobody-owns", "overpaying", "three-vendors", "one-place", "one-dashboard", "82", "audit", "time-tax", "one-hour", "convenience", "ping-pong", "pingpong", "sprawl", "questions", "media-plan"]),
    ("channels", "Channels & platforms", ["ctv", "streaming", "tv", "dooh", "out-of-home", "audio", "podcast", "tiktok", "reddit", "amazon", "retail-media", "display", "discovery", "email", "social", "seo", "sem", "search", "geofenc", "device-id", "programmatic", "business-profile", "reviews", "structured-data", "ai-answers", "local"]),
]
DEFAULT_CAT = ("strategy", "Strategy & budget")


def slugify(t):
    t = t.lower().replace("&", " and ").replace("’", "").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def unescape_md(t):
    return re.sub(r'\\([\\`*_{}\[\]()#+\-.!"\'>|~])', r"\1", t)


def inline(t):
    t = _html.escape(unescape_md(t), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def is_heading(b):
    raw = unescape_md(b).strip()
    if "\n" in b or len(raw) > 100:
        return False
    if re.match(r"^\d+\.\s", raw):
        return True
    return len(raw.split()) <= 15 and not re.search(r"[.!;,:]$", raw)


OVERRIDES = {"programmatic-without-the-agency-markup": "channels", "reddit-tiktok-and-dooh": "channels",
             "geo-fencing-explained": "channels", "owning-your-data": "strategy",
             "a-consolidated-media-plan-for-2-000-a-month": "strategy", "why-your-channels-should-talk": "strategy"}
CAT_NAMES = {c: n for c, n, _ in CATS} | {DEFAULT_CAT[0]: DEFAULT_CAT[1]}


def categorize(slug, title):
    if slug in OVERRIDES:
        return OVERRIDES[slug], CAT_NAMES[OVERRIDES[slug]]
    key = slug + " " + slugify(title)
    for cid, name, words in CATS:
        if any(w in key for w in words):
            return cid, name
    return DEFAULT_CAT


def parse_article(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    has_id = lines[0].startswith("ID:")
    fid = lines[0].split(":", 1)[1].strip() if has_id else ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n|\n", "\n".join(lines[1:] if has_id else lines)) if b.strip()]
    label, title = unescape_md(blocks[0]), unescape_md(blocks[1])
    body = blocks[2:]
    out, i, first_para = [], 0, None
    words = 0
    while i < len(body):
        b = body[i]
        words += len(b.split())
        if is_heading(b):
            out.append(f"<h2>{inline(b)}</h2>")
            i += 1
            continue
        out.append(f"<p>{inline(b)}</p>")
        if first_para is None:
            first_para = unescape_md(b)
        # short items after a line ending in a colon become a bullet list
        if unescape_md(b).rstrip().endswith(":"):
            items, j = [], i + 1
            while j < len(body) and len(unescape_md(body[j])) < 170 and not is_heading(body[j]):
                items.append(body[j]); j += 1
            if len(items) >= 2:
                out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
                words += sum(len(x.split()) for x in items)
                i = j
                continue
        i += 1
    slug = slugify(label)
    cid, cname = categorize(slug, title)
    desc = re.sub(r"\s+", " ", (first_para or title).replace("*", ""))
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0].rstrip(",;:—-– ") + "…"
    return {"slug": slug, "label": label, "title": title, "html": "\n".join(out), "desc": desc,
            "cat": cid, "cat_name": cname, "mins": max(3, math.ceil(words / 230)), "id": fid}


posts = [parse_article(f) for f in sorted(ART_DIR.glob("*.txt"))]
seen = {}
for pst in posts:
    base = pst["slug"]
    if base in seen:
        seen[base] += 1
        pst["slug"] = f"{base}-{seen[base]}"
    else:
        seen[base] = 1
posts.sort(key=lambda x: x["title"].lower())
BLOG_DIR = OUT / "blog"
BLOG_DIR.mkdir(exist_ok=True)
for old in BLOG_DIR.glob("*.html"):
    old.unlink()

CAT_ORDER = [("channels", "Channels & platforms"), ("strategy", "Strategy & budget"), ("partner", "Choosing a partner"), ("seasonal", "Seasonal & timing")]


def card(pst, pre):
    return (f'<li class="post-card" data-cat="{pst["cat"]}"><a href="{pre}{pst["slug"]}">'
            f'<span class="label">{pst["cat_name"]} · {pst["mins"]} min read</span>'
            f'<h3>{_html.escape(pst["title"])}</h3>'
            f'<p>{_html.escape(pst["desc"])}</p>'
            f'<span class="link-accent">Read article →</span></a></li>')


# ---- index
counts = {c: sum(1 for x in posts if x["cat"] == c) for c, _ in CAT_ORDER}
filters = ['<button class="chip-btn" type="button" data-filter="all" aria-pressed="true">All <span>' + str(len(posts)) + "</span></button>"]
filters += [f'<button class="chip-btn" type="button" data-filter="{c}" aria-pressed="false">{n} <span>{counts[c]}</span></button>' for c, n in CAT_ORDER if counts[c]]
index_body = f"""<div class="wrap hero hero--wide hero--end">
<div class="hero-copy">
<p class="eyebrow">The Factor42 blog</p>
<h1 class="display">Straight talk on <span class="accent">digital advertising.</span></h1>
</div>
<p class="lede">Practical guides on channels, budgets and choosing the right partner — written for the businesses buying media and the teams selling it.</p>
</div>
<section class="section" style="padding-top:0" aria-label="Articles">
<div class="wrap">
<div class="filters" role="group" aria-label="Filter by topic" hidden>
{"".join(filters)}
</div>
<ul class="post-grid">
{"".join(card(x, "") for x in posts)}
</ul>
</div>
</section>
"""
idx_graph = [ORG, {"@type": "Blog", "@id": f"{BASE}/blog/#blog", "url": f"{BASE}/blog/", "name": "The Factor42 blog", "publisher": {"@id": f"{BASE}/#org"},
                   "blogPost": [{"@type": "BlogPosting", "headline": x["title"], "url": f"{BASE}/blog/{x['slug']}"} for x in posts]}]
html_idx = (head("Blog: Digital Advertising Guides | Factor42 Media",
                 "Practical guides on advertising channels, budgets and choosing the right partner, from the ad ops team at Factor42 Media.",
                 "blog/", idx_graph, pre="../")
            + header("blog/", pre="../") + '<main id="main">\n' + index_body
            + cta("Want this handled for you?", "Every channel in these guides, run by one team.", pre="../") + "</main>\n" + footer(pre="../"))
(BLOG_DIR / "index.html").write_text(html_idx, encoding="utf-8")

# ---- posts
for pst in posts:
    related = [x for x in posts if x["cat"] == pst["cat"] and x["slug"] != pst["slug"]]
    k = posts.index(pst)
    related = (related[k % max(1, len(related)):] + related)[:3]
    url = f"{BASE}/blog/{pst['slug']}"
    graph = [ORG,
             {"@type": "BlogPosting", "@id": f"{url}#article", "headline": pst["title"], "description": pst["desc"], "url": url,
              "mainEntityOfPage": url, "datePublished": PUBLISHED, "dateModified": PUBLISHED,
              "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"},
              "image": f"{BASE}/assets/img/og-image.png", "articleSection": pst["cat_name"], "inLanguage": "en-US"},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
                 {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE}/blog/"},
                 {"@type": "ListItem", "position": 3, "name": pst["title"], "item": url}]}]
    extra = (f'<meta property="article:published_time" content="{PUBLISHED}">\n'
             f'<meta property="article:section" content="{pst["cat_name"]}">\n')
    title_tag = pst["title"] if len(pst["title"]) <= 62 else pst["label"]
    body = f"""<article class="wrap post">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="./">Blog</a><span aria-hidden="true">/</span><span>{pst["cat_name"]}</span></nav>
<header class="post-head">
<h1>{_html.escape(pst["title"])}</h1>
<p class="post-meta"><span>Factor42 Media</span><span>{pst["mins"]} min read</span></p>
</header>
<div class="prose">
{pst["html"]}
</div>
<aside class="post-cta" aria-label="Work with Factor42">
<div><p class="eyebrow">Factor42 Media</p><p class="post-cta-title">Every channel, run by one team.</p></div>
<a class="btn btn-accent" href="../contact">Book a free consultation <span aria-hidden="true">→</span></a>
</aside>
</article>
<section class="section section-white related" aria-labelledby="related-title">
<div class="wrap">
<div class="related-head"><h2 class="section-title" id="related-title">Keep reading</h2><a class="link-accent" href="./">All articles →</a></div>
<ul class="post-grid post-grid--3">
{"".join(card(x, "") for x in related)}
</ul>
</div>
</section>
"""
    page_html = (head(f"{_html.escape(title_tag)} | Factor42 Media", _html.escape(pst["desc"]), f"blog/{pst['slug']}", graph, pre="../", og_type="article", extra=extra)
                 + header("blog/", pre="../") + '<main id="main">\n' + body + "</main>\n" + footer(pre="../"))
    (BLOG_DIR / f"{pst['slug']}.html").write_text(page_html, encoding="utf-8")

# ---- sitemap
core = [("", 1.0), ("agencies", 0.9), ("broadcasters", 0.9), ("about", 0.6), ("contact", 0.7), ("blog/", 0.7), ("careers", 0.4), ("sla", 0.4), ("security", 0.4), ("privacy-policy", 0.2), ("terms-of-service", 0.2)]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f"  <url><loc>{BASE}/{u}</loc><lastmod>{PUBLISHED}</lastmod><priority>{pr}</priority></url>" for u, pr in core]
sm += [f"  <url><loc>{BASE}/blog/{x['slug']}</loc><lastmod>{PUBLISHED}</lastmod><priority>0.5</priority></url>" for x in posts]
sm.append("</urlset>")
(OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
print("blog:", len(posts), "posts;", {n: counts[c] for c, n in CAT_ORDER})
