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

CHANNELS = [
    ("Search advertising (Google Ads)", "Search, Display, Performance Max and Shopping campaign setup, bidding and optimization"),
    ("YouTube advertising", "In-stream, bumper, non-skippable and Masthead video campaigns"),
    ("Digital out-of-home (DOOH)", "Programmatic billboard, transit, retail and venue screen campaigns"),
    ("Streaming TV (OTT / CTV)", "Connected TV campaigns on Roku, Hulu, Peacock, Amazon Fire TV and more"),
    ("Programmatic display, video and audio", "Campaigns across DV360, The Trade Desk, Xandr and Amazon DSP"),
    ("Paid social", "Meta, TikTok, LinkedIn and Reddit campaigns"),
    ("Email marketing", "Campaign builds, lifecycle automation and deliverability management"),
]
OFFER_CATALOG = {
    "@type": "OfferCatalog", "name": "White-label ad operations by channel",
    "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": d}} for n, d in CHANNELS],
}
ORG = {
    "@type": "Organization",
    "@id": f"{BASE}/#org",
    "name": "Factor42 Media",
    "legalName": "Factor42 Media Inc.",
    "alternateName": "Factor42",
    "url": f"{BASE}/",
    "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/img/logo-512.png", "width": 512, "height": 512},
    "image": f"{BASE}/assets/img/og-image.png",
    "slogan": "The ad ops team behind your brand.",
    "description": ("Factor42 Media is a white-label ad operations and campaign fulfillment company. Agencies and TV and radio "
                    "broadcast groups sell digital campaigns; Factor42 traffics, optimizes and reports on them under the partner's brand "
                    "across search, social, programmatic, streaming TV, audio, DOOH and email."),
    "address": {"@type": "PostalAddress", "streetAddress": "8 The Green, Ste E", "addressLocality": "Dover",
                "addressRegion": "DE", "postalCode": "19901", "addressCountry": "US"},
    "areaServed": {"@type": "Country", "name": "United States"},
    "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "url": f"{BASE}/contact", "availableLanguage": "English"},
    "knowsAbout": ["White-label ad operations", "Campaign fulfillment", "Ad trafficking", "Programmatic advertising",
                   "Connected TV advertising", "Paid search", "Paid social", "Digital out-of-home advertising",
                   "Email marketing", "Campaign reporting", "Media buying"],
    "sameAs": [LINKEDIN],
}
WEBSITE = {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/", "name": "Factor42 Media",
           "publisher": {"@id": f"{BASE}/#org"}, "inLanguage": "en-US"}


def crumbs(*pairs):
    """BreadcrumbList from (name, path) pairs, starting at Home."""
    items = [("Home", "")] + list(pairs)
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{BASE}/{pth}"} for i, (n, pth) in enumerate(items)]}


CRUMB_NAMES = {"agencies": "For agencies", "broadcasters": "For broadcasters", "about": "About", "contact": "Book a consultation",
               "privacy-policy": "Privacy policy", "terms-of-service": "Terms of service", "sla": "Service level agreements",
               "security": "Security & confidentiality", "careers": "Careers"}


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


def head(title, desc, path, graph=None, noindex=False, pre="", og_type="website", extra="", og_image=None, og_alt=None):
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
<meta property="og:image" content="{og_image or BASE + '/assets/img/og-image.png'}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{og_alt or 'Factor42 Media — the ad ops team behind your brand'}">
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
<a href="{p}white-label-digital-marketing">White-label digital marketing</a>
<a href="{p}white-label-ppc">White-label PPC</a>
<a href="{p}white-label-google-ads">White-label Google Ads</a>
<a href="{p}white-label-facebook-ads">White-label Facebook ads</a>
<a href="{p}white-label-programmatic">Programmatic, CTV &amp; DOOH</a>
<a href="{p}outsourced-ad-operations">Outsourced ad operations</a>
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
    if graph is not None:
        graph = list(graph) + [WEBSITE]
        if path in CRUMB_NAMES:
            graph.append(crumbs((CRUMB_NAMES[path], path)))
    html = head(title, desc, path, graph, noindex) + header(active) + '<main id="main">\n' + body + "</main>\n" + footer()
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")


def redirect_page(name, target, title):
    target = f"{BASE}/{target}"  # absolute: these are also requested with a trailing slash
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{target.split("#")[0]}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace({json.dumps(target)});</script>
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
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
     graph=[dict(ORG, hasOfferCatalog=OFFER_CATALOG)])

page("agencies",
     "White-Label Ad Ops & PPC for Agencies | Factor42 Media",
     "Add search, social, programmatic, CTV and DOOH without adding headcount. Factor42 runs your campaigns and reporting under your agency's brand.",
     "agencies", "agencies", body("agencies").replace("{{FAQ}}", faq_html) + cta("Add a channel to your agency this month."),
     graph=[ORG,
            {"@type": "Service", "name": "White-label ad operations for agencies", "serviceType": "White-label ad operations and campaign fulfillment", "provider": {"@id": f"{BASE}/#org"}, "url": f"{BASE}/agencies", "areaServed": {"@type": "Country", "name": "United States"}, "audience": {"@type": "BusinessAudience", "name": "Marketing and advertising agencies"}, "hasOfferCatalog": OFFER_CATALOG},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}])

page("broadcasters",
     "Digital Ad Fulfillment for TV & Radio Groups | Factor42 Media",
     "Give every seller in every market a full digital menu. Factor42 builds, launches and reports on digital campaigns for broadcast groups, under your brand.",
     "broadcasters", "broadcasters", body("broadcasters") + cta("Put a full digital menu in every seller's hands.", button="Talk to our broadcast team"),
     graph=[ORG, {"@type": "Service", "name": "Digital ad fulfillment for broadcast and media groups", "serviceType": "White-label digital advertising fulfillment", "provider": {"@id": f"{BASE}/#org"}, "url": f"{BASE}/broadcasters", "areaServed": {"@type": "Country", "name": "United States"}, "audience": {"@type": "BusinessAudience", "name": "TV and radio broadcast groups"}, "hasOfferCatalog": OFFER_CATALOG}])

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
legal("terms-of-service", "Terms of service", "Terms of Service | Factor42 Media", "The terms that govern use of factor42media.com: acceptable use, content ownership, disclaimers and liability.", "Legal")
legal("sla", "Service level agreements", "Service Level Agreements | Factor42 Media", "How Factor42 service level agreements work: trafficking turnaround, QA, pacing, reporting, communication and escalation.", "Our commitments")
legal("security", "Security &amp; confidentiality", "Security & Confidentiality | Factor42 Media", "How Factor42 protects partner ad accounts, campaign data and client confidentiality.", "Trust")
page("careers", "Careers at Factor42 Media | Ad Ops Jobs", "Join the ad ops team behind agencies and media groups. Factor42 hires ad ops specialists, campaign managers and analysts.",
     "careers", "", body("careers"), graph=[ORG])

# ---- service landing pages (content in services.py); blog cards are filled in after the blog build
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from services import SERVICES, PROCESS, PROOF, HUB
SVC_BY_SLUG = {s["slug"]: s for s in SERVICES}
SVC_BLURB = {s["slug"]: s["lede"].split(". ")[0].rstrip(".") + "." for s in SERVICES}


def service_body(s):
    others = [x for x in SERVICES if x["slug"] not in (s["slug"], HUB)]
    if s["includes"] == "SERVICE_CARDS":
        inc = "".join(f'<a class="item item-link" href="{x["slug"]}"><span class="num">{i + 1:02d}</span><h3 class="card-title">{x["nav"]}</h3>'
                      f'<p>{SVC_BLURB[x["slug"]]}</p><span class="link-accent">See the service →</span></a>' for i, x in enumerate(others))
    else:
        inc = "".join(f'<div class="item"><span class="num">{i + 1:02d}</span><h3 class="card-title">{t}</h3><p>{d}</p></div>'
                      for i, (t, d) in enumerate(s["includes"]))
    glance = (["Your logo on every report", "Wholesale pricing, your margin", "Your ad accounts, your data", "Team-to-team support"])
    what = "".join(f"<p>{p}</p>" for p in s["what"])
    why = "".join(f'<div class="row"><h3>{t}</h3><p>{d}</p></div>' for t, d in s["why"])
    steps = "".join(f'<div class="item"><span class="num">{i + 1:02d}</span><h3 class="card-title">{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(PROCESS))
    faq = "".join(f'<div class="row"><h3>{q}</h3><p>{a}</p></div>' for q, a in s["faq"])
    plats = "".join(f"<li>{p}</li>" for p in s["platforms"])
    stats = "".join(f'<div class="stat"><b>{n}</b><span>{l}</span></div>' for n, l in PROOF)
    if s["slug"] == HUB:
        rel = [("For agencies", "agencies", "How the white-label model works for marketing agencies, plus PPC and paid social."),
               ("For broadcasters", "broadcasters", "A full digital menu for TV and radio sellers, reported by market."),
               ("Outsourced ad operations", "outsourced-ad-operations", "Trafficking, QA, pacing and reporting as a service.")]
    else:
        rel = [("All white-label services", HUB, "Every channel Factor42 fulfills for agencies and media companies.")]
        rel += [(x["nav"], x["slug"], SVC_BLURB[x["slug"]]) for x in others if x["slug"] != s["slug"]][:3]
    related = "".join(f'<a class="item item-link" href="{u}"><h3 class="card-title">{n}</h3><p>{d}</p><span class="link-accent">Learn more →</span></a>' for n, u, d in rel)
    return f"""<nav class="wrap breadcrumbs crumbs-top" aria-label="Breadcrumb"><a href="./">Home</a><span aria-hidden="true">/</span><a href="agencies">For agencies</a><span aria-hidden="true">/</span><span>{s["nav"] if s["slug"] != HUB else "White-label digital marketing"}</span></nav>
<div class="wrap hero hero--wide">
<div class="hero-copy">
<p class="eyebrow">{s["eyebrow"]}</p>
<h1 class="display">{s["h1"]}</h1>
<p class="lede">{s["lede"]}</p>
<div class="actions mt-8">
<a class="btn btn-accent" href="contact">Get a wholesale rate card <span aria-hidden="true">→</span></a>
<a class="link-underline" href="#faq">Read the FAQ</a>
</div>
</div>
<div class="panel-ink on-ink">
<p class="eyebrow">White-label means</p>
<ul class="bullets">{"".join(f"<li>{g}</li>" for g in glance)}</ul>
</div>
</div>

<div class="wrap">
<div class="stats" aria-label="Results">{stats}</div>
<div class="platforms">
<p class="eyebrow">Platforms</p>
<ul aria-label="Platforms we run">{plats}</ul>
</div>
</div>

<section class="section section-white" aria-labelledby="what-title">
<div class="wrap two-col two-col--side">
<div class="stack">
<p class="eyebrow">The model</p>
<h2 class="section-title" id="what-title">{s["what_title"]}</h2>
</div>
<div class="prose prose--flush">{what}</div>
</div>
</section>

<section class="section" aria-labelledby="inc-title">
<div class="wrap">
<div class="section-head">
<div class="stack">
<p class="eyebrow">{"Services" if s["slug"] == HUB else "Scope"}</p>
<h2 class="section-title" id="inc-title">{s["includes_title"]}</h2>
</div>
<p class="lede">Your team keeps the strategy and the client. We handle the execution.</p>
</div>
<div class="grid grid-3">{inc}</div>
</div>
</section>

<section class="section section-white" aria-labelledby="why-title">
<div class="wrap two-col two-col--side">
<div class="stack">
<p class="eyebrow">Why Factor42</p>
<h2 class="section-title" id="why-title">{s["why_title"]}</h2>
<a class="link-accent" href="agencies">How white-label works for agencies →</a>
</div>
<div class="rows">{why}</div>
</div>
</section>

<section class="section section-ink on-ink" aria-labelledby="how-title">
<div class="wrap">
<div class="section-head">
<div class="stack">
<p class="eyebrow">How it works</p>
<h2 class="section-title" id="how-title">From brief to branded report.</h2>
</div>
<p class="lede">The same four steps for every channel, so your team learns one workflow.</p>
</div>
<div class="grid grid-4">{steps}</div>
</div>
</section>

<section class="section" aria-labelledby="econ-title">
<div class="wrap">
<div class="section-head section-head--narrow">
<div class="stack">
<p class="eyebrow">The economics</p>
<h2 class="section-title" id="econ-title">You set the price. You keep the margin.</h2>
<p class="lede">We charge a wholesale fulfillment rate, priced by channel and volume. What you charge your client is up to you.</p>
</div>
</div>
<div class="econ">
<div><span class="label">Your client pays you</span><b>Your retail rate</b><span>Your management fee or CPM, set by you</span></div>
<div><span class="label">You pay Factor42</span><b>Our wholesale rate</b><span>Fulfillment, priced by channel and volume</span></div>
<div class="econ-ink"><span class="label">Your margin</span><b>The difference</b><span>Without adding headcount</span></div>
</div>
</div>
</section>

<section class="section section-white" id="faq" aria-labelledby="faq-title">
<div class="wrap two-col two-col--side">
<div class="stack">
<p class="eyebrow">FAQ</p>
<h2 class="section-title" id="faq-title">Common questions</h2>
</div>
<div class="rows">{faq}</div>
</div>
</section>

<section class="section" aria-labelledby="rel-title">
<div class="wrap">
<div class="related-head"><h2 class="section-title" id="rel-title">{"Who we work with" if s["slug"] == HUB else "Related services"}</h2><a class="link-accent" href="{"agencies" if s["slug"] == HUB else HUB}">{"For agencies →" if s["slug"] == HUB else "All services →"}</a></div>
<div class="grid grid-4 grid-links">{related}</div>
</div>
</section>

<!--FROM_BLOG:{",".join(s["blog"])}-->
"""


for s in SERVICES:
    url = f"{BASE}/{s['slug']}"
    trail = [("For agencies", "agencies"), ("White-label digital marketing" if s["slug"] == HUB else s["nav"], s["slug"])]
    graph = [ORG,
             {"@type": "Service", "@id": f"{url}#service", "name": s["eyebrow"], "serviceType": s["service_type"], "description": s["desc"],
              "url": url, "provider": {"@id": f"{BASE}/#org"}, "areaServed": {"@type": "Country", "name": "United States"},
              "audience": {"@type": "BusinessAudience", "name": "Marketing agencies and media companies"},
              **({"hasOfferCatalog": OFFER_CATALOG} if s["slug"] == HUB else {})},
             {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]]},
             crumbs(*trail)]
    page(s["slug"], s["title"], s["desc"], s["slug"], "agencies", service_body(s) + cta("Add a channel to your agency this month.",
         "Tell us what you sell. We'll send a fulfillment plan and a wholesale rate card."), graph=graph)

# Old URLs from the previous site
redirect_page("consultation", "contact", "Book a consultation | Factor42 Media")
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
            "cat": cid, "cat_name": cname, "mins": max(3, math.ceil(words / 230)), "id": fid, "words": words}


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

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from linker import link_library
LINK_STATS = link_library(posts)

# "Keep reading": 3 same-topic articles per post, favouring the least-linked ones, so every
# article also gets several links from related articles. Skips articles already linked in the text.
_rel_in = {x["slug"]: 0 for x in posts}
RELATED = {}
for pst in sorted(posts, key=lambda x: x["slug"]):
    in_text = set(re.findall(r'<a href="([^"./][^"]*)">', pst["html"]))
    cands = [x for x in posts if x["cat"] == pst["cat"] and x["slug"] != pst["slug"] and x["slug"] not in in_text]
    cands.sort(key=lambda x: (_rel_in[x["slug"]] + LINK_STATS[x["slug"]][1], x["slug"]))
    RELATED[pst["slug"]] = cands[:3]
    for x in cands[:3]:
        _rel_in[x["slug"]] += 1
pst_by_slug = {x["slug"]: x for x in posts}
BLOG_DIR = OUT / "blog"
BLOG_DIR.mkdir(exist_ok=True)
for old in BLOG_DIR.glob("*.html"):
    old.unlink()

CAT_ORDER = [("channels", "Channels & platforms"), ("strategy", "Strategy & budget"), ("partner", "Choosing a partner"), ("seasonal", "Seasonal & timing")]


def card(pst, pre, hl="h3"):
    return (f'<li class="post-card" data-cat="{pst["cat"]}"><a href="{pre}{pst["slug"]}">'
            f'<span class="label">{pst["cat_name"]} · {pst["mins"]} min read</span>'
            f'<{hl}>{_html.escape(pst["title"])}</{hl}>'
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
{"".join(card(x, "", "h2") for x in posts)}
</ul>
</div>
</section>
"""
idx_graph = [ORG, WEBSITE, crumbs(("Blog", "blog/")), {"@type": "Blog", "@id": f"{BASE}/blog/#blog", "url": f"{BASE}/blog/", "name": "The Factor42 blog", "isPartOf": {"@id": f"{BASE}/#website"}, "publisher": {"@id": f"{BASE}/#org"}, "inLanguage": "en-US",
                   "description": "Guides on digital advertising channels, budgets and choosing a marketing partner, from Factor42 Media.",
                   "blogPost": [{"@type": "BlogPosting", "headline": x["title"], "url": f"{BASE}/blog/{x['slug']}"} for x in posts]}]
html_idx = (head("Blog: Digital Advertising Guides | Factor42 Media",
                 "Practical guides on advertising channels, budgets and choosing the right partner, from the ad ops team at Factor42 Media.",
                 "blog/", idx_graph, pre="../")
            + header("blog/", pre="../") + '<main id="main">\n' + index_body
            + cta("Want this handled for you?", "Every channel in these guides, run by one team.", pre="../") + "</main>\n" + footer(pre="../"))
(BLOG_DIR / "index.html").write_text(html_idx, encoding="utf-8")

# ---- posts
for pst in posts:
    related = RELATED[pst["slug"]]
    url = f"{BASE}/blog/{pst['slug']}"
    _img_file = OUT / "assets" / "img" / "blog" / f"{pst['slug']}.png"
    post_img = f"{BASE}/assets/img/blog/{pst['slug']}.png" if _img_file.exists() else f"{BASE}/assets/img/og-image.png"
    graph = [ORG,
             {"@type": "BlogPosting", "@id": f"{url}#article", "headline": pst["title"], "description": pst["desc"], "url": url,
              "mainEntityOfPage": url, "datePublished": PUBLISHED, "dateModified": PUBLISHED,
              "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"},
              "image": {"@type": "ImageObject", "url": post_img, "width": 1200, "height": 630}, "articleSection": pst["cat_name"], "inLanguage": "en-US",
              "wordCount": pst["words"], "timeRequired": f"PT{pst['mins']}M", "isPartOf": {"@id": f"{BASE}/blog/#blog"},
              "keywords": pst["cat_name"]}, WEBSITE,
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
                 {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE}/blog/"},
                 {"@type": "ListItem", "position": 3, "name": pst["title"], "item": url}]}]
    extra = (f'<meta property="article:published_time" content="{PUBLISHED}">\n'
             f'<meta property="article:section" content="{pst["cat_name"]}">\n')
    full = f"{pst['title']} | Factor42 Media"
    if len(full) <= 65:
        title_tag = full
    elif len(pst["title"]) <= 65:
        title_tag = pst["title"]
    elif len(f"{pst['label']} | Factor42 Media") <= 65:
        title_tag = f"{pst['label']} | Factor42 Media"
    else:
        title_tag = pst["label"]
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
    page_html = (head(_html.escape(title_tag), _html.escape(pst["desc"]), f"blog/{pst['slug']}", graph, pre="../", og_type="article", extra=extra, og_image=post_img, og_alt=_html.escape(pst["title"]))
                 + header("blog/", pre="../") + '<main id="main">\n' + body + "</main>\n" + footer(pre="../"))
    (BLOG_DIR / f"{pst['slug']}.html").write_text(page_html, encoding="utf-8")

# ---- "From the blog" sections on service pages (placeholders in bodies/*.html)
for _f in ["index.html", "agencies.html", "broadcasters.html"] + [f"{x['slug']}.html" for x in SERVICES]:
    _path = OUT / _f; _src = _path.read_text(encoding="utf-8")
    def _fb(m):
        picks = [pst_by_slug[x] for x in m.group(1).split(",")]
        return ('<section class="section section-white" aria-labelledby="fromblog-title">\n<div class="wrap">\n'
                '<div class="related-head"><h2 class="section-title" id="fromblog-title">From the blog</h2><a class="link-accent" href="blog/">All articles →</a></div>\n'
                '<ul class="post-grid post-grid--3">\n' + "".join(card(x, "blog/") for x in picks) + "\n</ul>\n</div>\n</section>\n")
    _path.write_text(re.sub(r"<!--FROM_BLOG:([a-z0-9,-]+)-->", _fb, _src), encoding="utf-8")

# ---- robots.txt: open to search and AI crawlers, explicitly
AI_BOTS = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
           "Claude-User", "PerplexityBot", "Perplexity-User", "Applebot", "Applebot-Extended", "Amazonbot", "CCBot", "meta-externalagent"]
(OUT / "robots.txt").write_text(
    "# Factor42 Media: search engines and AI assistants are welcome to crawl and cite this site.\n"
    + "".join(f"User-agent: {b}\n" for b in AI_BOTS) + "Allow: /\nDisallow: /thank-you\nDisallow: /_build/\nDisallow: /_worker/\n\n"
    "User-agent: *\nAllow: /\nDisallow: /thank-you\nDisallow: /_build/\nDisallow: /_worker/\n\n"
    f"Sitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

# ---- llms.txt (index for AI assistants) and llms-full.txt (full text)
def _plain(h):
    t = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", h)
    t = re.sub(r"<li>(.*?)</li>", r"- \1\n", t)
    t = re.sub(r"</p>", "\n", t)
    return _html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

ABOUT_LLM = ("> Factor42 Media is a white-label ad operations and campaign fulfillment company. Agencies and TV and radio broadcast "
             "groups sell digital campaigns to their clients; Factor42 traffics, QAs, optimizes and reports on those campaigns under "
             "the partner's brand.\n\n"
             "- Channels: Google Ads (Search, Display, Performance Max, Shopping), YouTube, Meta, Instagram, TikTok, LinkedIn, Reddit, X, "
             "Pinterest, Snapchat, programmatic display, video and audio (DV360, The Trade Desk, Xandr, Amazon DSP), streaming TV (OTT/CTV), "
             "digital out-of-home (DOOH) and email marketing.\n"
             "- Results: 98.6% campaign delivery rate; 100+ agency and media partners; 12-minute average trafficking turnaround; "
             "Google Ads campaigns launch in under 4 hours on average.\n"
             "- Who it serves: marketing agencies (white-label ad ops, PPC and paid social) and TV/radio broadcast groups "
             "(digital fulfillment for station sellers, market-level reporting).\n"
             "- Company: Factor42 Media Inc., 8 The Green, Ste E, Dover, DE 19901, United States. Contact: https://factor42media.com/contact\n")
CORE = [("Home", "", "Overview, services, process and every channel Factor42 runs"),
        ("For agencies", "agencies", "White-label ad ops, PPC and paid social for agencies; economics and FAQ"),
        ("For broadcasters", "broadcasters", "Digital menu for TV and radio sellers, order-to-delivery workflow, market reporting, switchover"),
] + [(x["eyebrow"], x["slug"], x["desc"]) for x in SERVICES] + [
        ("About", "about", "Company and working principles"),
        ("Service level agreements", "sla", "What Factor42 SLAs cover: turnaround, QA, pacing, reporting, escalation"),
        ("Security & confidentiality", "security", "Account access, confidentiality and data handling"),
        ("Book a consultation", "contact", "Request a fulfillment plan and wholesale rate card"),
        ("Blog", "blog/", "105 guides on advertising channels, budgets and choosing a marketing partner")]
lines = ["# Factor42 Media", "", ABOUT_LLM, "## Pages", ""]
lines += [f"- [{n}]({BASE}/{u}): {d}" for n, u, d in CORE]
for cid, cname in CAT_ORDER:
    lines += ["", f"## Blog: {cname}", ""]
    lines += [f"- [{x['title']}]({BASE}/blog/{x['slug']}): {x['desc']}" for x in posts if x["cat"] == cid]
lines += ["", "## Optional", "", f"- [Full text of every page and article]({BASE}/llms-full.txt)"]
(OUT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

full = ["# Factor42 Media: full text", "", ABOUT_LLM]
for cid, cname in CAT_ORDER:
    for x in posts:
        if x["cat"] == cid:
            full += ["", "---", "", f"# {x['title']}", f"URL: {BASE}/blog/{x['slug']}", f"Topic: {cname}", "", _plain(x["html"])]
(OUT / "llms-full.txt").write_text("\n".join(full) + "\n", encoding="utf-8")

# ---- sitemap
core = [("", 1.0), ("agencies", 0.9), ("broadcasters", 0.9)] + [(x["slug"], 0.8) for x in SERVICES] + [("about", 0.6), ("contact", 0.7), ("blog/", 0.7), ("careers", 0.4), ("sla", 0.4), ("security", 0.4), ("privacy-policy", 0.2), ("terms-of-service", 0.2)]
import subprocess, datetime


def lastmod(rel_file):
    """Today if the generated file differs from the last commit, else the date it was last committed."""
    try:
        old = subprocess.run(["git", "-C", str(OUT), "show", f"HEAD:{rel_file}"], capture_output=True, check=True).stdout
        if old == (OUT / rel_file).read_bytes():
            d = subprocess.run(["git", "-C", str(OUT), "log", "-1", "--format=%cs", "--", rel_file], capture_output=True, text=True).stdout.strip()
            if d:
                return d
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return datetime.date.today().isoformat()


def _file_for(u):
    return "index.html" if u == "" else (u + "index.html" if u.endswith("/") else u + ".html")


sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f"  <url><loc>{BASE}/{u}</loc><lastmod>{lastmod(_file_for(u))}</lastmod><priority>{pr}</priority></url>" for u, pr in core]
sm += [f"  <url><loc>{BASE}/blog/{x['slug']}</loc><lastmod>{lastmod('blog/' + x['slug'] + '.html')}</lastmod><priority>0.5</priority></url>" for x in posts]
sm.append("</urlset>")
(OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
print("blog:", len(posts), "posts;", {n: counts[c] for c, n in CAT_ORDER})


# ================================================================ old-site redirects
# Addresses from the previous factor42media.com that Google still has. Each gets a static
# page that forwards (instant meta refresh, which Google treats as a permanent redirect)
# and declares the new page canonical. Both /blog/<old>/ and /blog-<old>.html forms existed.
# Runs after the blog build, which clears blog/*.html.
OLD_BLOG = {
    # same article, new address
    "overpaying-marketing": "blog/youre-probably-overpaying-to-run-your-marketing",
    "what-agencies-charge": "blog/what-agencies-actually-charge",
    "three-marketing-models": "blog/in-house-agency-or-consolidated-partner",
    "cant-afford-agency": "blog/when-you-cant-afford-an-agency",
    "streaming-tv": "blog/streaming-tv-for-the-price-of-facebook",
    "one-dashboard": "blog/one-dashboard-to-rule-them-all",
    "retainer-math": "blog/the-hidden-math-of-agency-retainers",
    "seven-logins": "blog/seven-logins-six-reports-one-headache",
    "reddit-tiktok-dooh": "blog/reddit-tiktok-and-dooh",
    "audit-marketing-spend": "blog/audit-your-marketing-spend-in-an-afternoon",
    "third-option": "blog/too-small-for-an-agency-too-busy-to-diy",
    "82-percent-hard-way": "blog/why-82-run-marketing-the-hard-way",
    "tool-trap": "blog/the-tool-trap",
    "stop-paying-three-vendors": "blog/stop-paying-three-vendors-to-do-one-job",
    "every-channel-one-place": "blog/every-channel-one-place",
    # retired agency-facing posts: closest current page
    "google-ads-vs-programmatic": "blog/programmatic-without-the-agency-markup",
    "dsp-consolidation": "blog/what-consolidated-media-buying-is",
    "vetting-ad-ops-partner": "blog/7-questions-to-vet-a-provider",
    "paid-social-launch-checklist": "white-label-facebook-ads",
    "white-label-trafficking-retention": "outsourced-ad-operations",
    "trafficking-mistakes-retainers": "outsourced-ad-operations",
}


def forward_page(target, title):
    url = f"{BASE}/{target}"
    canon = url.split("#")[0]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{canon}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({json.dumps(url)});</script>
</head>
<body>
<p>This page has moved to <a href="{url}">{url}</a>.</p>
</body>
</html>
"""


post_slugs = {x["slug"] for x in posts}
redirects_written = 0
for old, target in OLD_BLOG.items():
    t_path = target.split("#")[0]
    assert (OUT / f"{t_path}.html").exists(), f"redirect target missing: {target}"
    t_title = next((x["title"] for x in posts if f"blog/{x['slug']}" == t_path), "Factor42 Media")
    page_html = forward_page(target, f"{_html.escape(t_title)} | Factor42 Media")
    # /blog/<old> and /blog/<old>/  (GitHub Pages serves blog/<old>.html for both)
    if old not in post_slugs:
        (BLOG_DIR / f"{old}.html").write_text(page_html, encoding="utf-8"); redirects_written += 1
    # /blog-<old>.html
    (OUT / f"blog-{old}.html").write_text(page_html, encoding="utf-8"); redirects_written += 1
(OUT / "blog.html").write_text(forward_page("blog/", "Blog | Factor42 Media"), encoding="utf-8"); redirects_written += 1
print("old-site redirects:", redirects_written)
