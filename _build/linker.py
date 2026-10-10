"""Contextual internal links for blog articles.

Each rule maps a phrase (regex, case-insensitive) to candidate target articles. For every
article, the first natural mention of a phrase in body text (not headings, not inside an
existing link) is linked to a candidate target, at most MAX_LINKS per article, one link per
paragraph, each target once, never to itself. Among candidates, the target with the fewest
links so far wins, so links spread across the whole library. Only adds <a> tags; wording
is never changed.
"""
import re

MAX_LINKS = 5

RULES = [
    (r"streaming TV advertising|streaming TV|connected TV|\bCTV\b|\bOTT\b",
     ["what-is-streaming-tv-advertising", "streaming-tv-within-reach", "why-ctv-belongs-in-your-mix",
      "connected-tv-myths", "streaming-tv-for-the-price-of-facebook"]),
    (r"streaming audio|podcast ads|podcasts?\b|digital audio",
     ["digital-audio", "finding-your-niche-with-audio"]),
    (r"digital out-of-home|\bDOOH\b|digital billboards?", ["dooh-is-now-affordable", "reddit-tiktok-and-dooh"]),
    (r"programmatic(?: advertising| display| buying)?", ["programmatic-without-the-agency-markup"]),
    (r"geo-?fenc(?:ing|e)", ["geo-fencing-explained"]),
    (r"device ID", ["device-id-targeting"]),
    (r"search engine marketing|paid search", ["what-is-search-engine-marketing"]),
    (r"Google Business Profile", ["connecting-google-business-profile-to-paid-search"]),
    (r"online reviews|customer reviews|reviews", ["the-power-of-reviews"]),
    (r"local SEO|local search", ["local-seo-in-the-age-of-ai"]),
    (r"\bSEO\b|search optimization", ["is-seo-dead", "local-seo-in-the-age-of-ai"]),
    (r"AI answers|AI-powered search|AI search|AI assistants", ["showing-up-in-ai-answers"]),
    (r"structured data|schema markup", ["structured-data-made-simple"]),
    (r"email marketing|email campaigns?|email list", ["email-still-returns-36-for-every-1", "how-email-fits-into-a-consolidated-strategy", "last-minute-email-campaigns"]),
    (r"marketing automation|automated (?:emails?|flows|sequences)", ["what-is-marketing-automation"]),
    (r"first-party data", ["first-party-data"]),
    (r"A/B test(?:ing|s)?", ["a-simple-guide-to-a-b-testing"]),
    (r"ad fatigue|creative fatigue", ["avoiding-ad-fatigue"]),
    (r"marketing funnel|the funnel|funnel", ["building-a-funnel-that-converts"]),
    (r"buying journey|customer journey|path to purchase", ["understanding-the-buying-journey", "how-ai-is-rewriting-the-customer-journey"]),
    (r"micro-moments?", ["master-the-micro-moment"]),
    (r"TikTok", ["is-tiktok-right-for-your-business", "reddit-tiktok-and-dooh"]),
    (r"Reddit", ["why-your-next-ad-dollar-might-belong-on-reddit", "reddit-tiktok-and-dooh"]),
    (r"Amazon advertising|Amazon ads|on Amazon", ["amazon-advertising-for-beginners"]),
    (r"retail media", ["winning-in-retail-media"]),
    (r"display ads|display advertising|banner ads", ["display-advertising-that-gets-noticed", "why-creative-decides-display-ads"]),
    (r"Discovery ads|Demand Gen", ["google-discovery-ads"]),
    (r"social media marketing|paid social|social media|social strategy", ["the-new-reality-of-social-media", "why-your-social-feels-a-step-behind"]),
    (r"competitors' customers|conquesting|your competitors", ["competitive-conquesting"]),
    (r"untapped markets?|new markets?", ["finding-untapped-markets"]),
    (r"integrated marketing|integrated campaigns?", ["what-is-integrated-marketing"]),
    (r"consolidated media buying", ["what-consolidated-media-buying-is", "stop-paying-three-vendors-to-do-one-job"]),
    (r"consolidated partner|consolidated provider|consolidated model", ["in-house-agency-or-consolidated-partner", "too-small-for-an-agency-too-busy-to-diy"]),
    (r"consolidated media|consolidat(?:ing|ion|e) (?:your )?marketing|consolidat(?:ing|ion)",
     ["every-channel-one-place", "switching-from-multiple-vendors-to-one", "what-consolidated-media-buying-is", "a-consolidated-media-plan-for-2-000-a-month"]),
    (r"vendor sprawl|multiple vendors|several vendors|separate vendors", ["calculate-your-vendor-sprawl", "switching-from-multiple-vendors-to-one", "nobody-owns-your-results"]),
    (r"retainers?", ["the-hidden-math-of-agency-retainers"]),
    (r"management fees?|agency fees?|markups?", ["what-agencies-actually-charge", "what-your-agencys-invoice-isnt-telling-you"]),
    (r"hidden fees|transparent pricing|all-in price", ["transparent-pricing"]),
    (r"invoices?", ["what-your-agencys-invoice-isnt-telling-you"]),
    (r"proposals?", ["red-flags-in-a-marketing-proposal"]),
    (r"(?:sign|signing) (?:a |another )?contract|long contracts?|contracts?", ["five-questions-before-you-sign-a-contract"]),
    (r"single point of contact|point of contact", ["the-single-point-of-contact-advantage"]),
    (r"account manag(?:er|ement)", ["the-client-relationship-you-deserve"]),
    (r"one dashboard|single dashboard|dashboards?|one report", ["one-dashboard-to-rule-them-all"]),
    (r"logins|logging into", ["seven-logins-six-reports-one-headache"]),
    (r"software subscriptions?|subscriptions|software", ["the-tool-trap"]),
    (r"time tax|hours a week|your time", ["the-time-tax-of-managing-your-own-marketing", "you-have-one-hour-a-day-for-marketing"]),
    (r"your (?:ad )?accounts and data|own your (?:data|accounts)|ownership of", ["owning-your-data"]),
    (r"full-service", ["what-full-service-should-include", "when-you-cant-afford-an-agency"]),
    (r"media plan", ["five-questions-your-media-plan-must-answer"]),
    (r"small budgets?|limited budgets?|modest budgets?|tight budgets?",
     ["doing-more-with-less", "a-consolidated-media-plan-for-2-000-a-month", "grow-revenue-without-growing-budget"]),
    (r"marketing budget|your budget|ad budget",
     ["getting-the-most-from-your-budget", "grow-revenue-without-growing-budget", "a-consolidated-media-plan-for-2-000-a-month"]),
    (r"\bROI\b|return on (?:ad spend|investment)", ["maximizing-roi"]),
    (r"attribution|measurement|measuring results", ["beyond-the-click"]),
    (r"privacy", ["privacy-and-ethics-in-digital-advertising"]),
    (r"brand consistency|consistent brand|consistent message", ["brand-consistency-across-channels"]),
    (r"holiday season|the holidays|holiday", ["holiday-campaigns-that-deliver"]),
    (r"back-to-school", ["back-to-school-marketing"]),
    (r"summer", ["summer-advertising-secrets"]),
    (r"\bQ1\b|new year", ["jumpstart-q1"]),
    (r"political (?:ad|advertising|season)", ["what-political-ad-season-means"]),
    (r"marketing calendar|seasonal (?:peaks|calendar|moments)|seasonality", ["take-charge-of-your-yearly-calendar", "timing-your-digital-ads"]),
    (r"mid-year", ["the-mid-year-marketing-checkup"]),
    (r"recession|downturn|going dark", ["recession-proofing-your-marketing", "marketing-through-economic-uncertainty"]),
    (r"economic uncertainty|uncertain times|uncertain economy", ["marketing-through-economic-uncertainty"]),
    (r"money is tight|efficiency", ["when-money-is-tight-efficiency-is-everything"]),
    (r"trends", ["trends-worth-your-budget", "trends-small-businesses-must-master"]),
    (r"digital advertising", ["what-is-digital-advertising"]),
    (r"cheapest (?:quote|option)|lowest (?:quote|bid)|low quote", ["why-the-cheapest-quote-isnt-the-cheapest-outcome"]),
    (r"cheaper", ["why-cheaper-doesnt-mean-worse"]),
    (r"overpaying|more than 70%|over 70%", ["youre-probably-overpaying-to-run-your-marketing"]),
    (r"actually working|is working|what's working", ["how-to-tell-if-your-provider-is-working"]),
    (r"renew(?:al|ing)?", ["when-to-renew-when-to-walk"]),
    (r"vet(?:ting)? (?:a |any )?provider|choosing a provider|evaluate (?:a |any )?provider", ["7-questions-to-vet-a-provider", "what-to-demand-from-anyone-who-runs-your-ads"]),
    (r"expectations", ["setting-expectations-with-your-partner"]),
    (r"accountab(?:le|ility)|owns the results|nobody owns", ["nobody-owns-your-results"]),
    (r"finger-pointing|chasing (?:vendors|answers)|back-and-forth", ["the-end-of-vendor-ping-pong"]),
    (r"convenience", ["how-much-is-convenience-costing-you"]),
    (r"audit", ["audit-your-marketing-spend-in-an-afternoon"]),
    (r"the hard way|fragmented|fragmentation", ["why-82-run-marketing-the-hard-way", "one-team-every-channel"]),
    (r"(?:can't|cannot) afford (?:an |a )?(?:full-service )?agency|traditional agency", ["when-you-cant-afford-an-agency", "too-small-for-an-agency-too-busy-to-diy"]),
    (r"in-house", ["in-house-agency-or-consolidated-partner"]),
    (r"silos|work together|talk to each other|coordinated", ["why-your-channels-should-talk", "what-is-integrated-marketing"]),
    (r"under one roof|one place", ["from-search-to-streaming-tv-one-roof", "every-channel-one-place"]),
    (r"toolkit", ["the-essential-marketing-toolkit"]),
    (r"creative", ["why-creative-decides-display-ads"]),
    (r"targeting", ["device-id-targeting", "geo-fencing-explained"]),
    # broader, natural phrasings so niche articles can be reached
    (r"cut(?:ting)? back|pull(?:ing)? back|cut(?:ting)? (?:your |their )?marketing", ["recession-proofing-your-marketing", "marketing-through-economic-uncertainty"]),
    (r"economic uncertainty|uncertain economy|the economy|economic conditions", ["marketing-through-economic-uncertainty"]),
    (r"timing|the right moment", ["timing-your-digital-ads"]),
    (r"attention spans?|grab(?:bing)? attention|scroll(?:ing)? past|in seconds", ["master-the-micro-moment"]),
    (r"marketing tools|the right tools|tools and platforms", ["the-essential-marketing-toolkit", "the-tool-trap"]),
    (r"elections?", ["what-political-ad-season-means"]),
    (r"frequency|the same ads?", ["avoiding-ad-fatigue"]),
    (r"check-?ups?|take stock|halfway", ["the-mid-year-marketing-checkup"]),
    (r"cheapest|lowest price|price alone", ["why-the-cheapest-quote-isnt-the-cheapest-outcome"]),
    (r"Walmart|Instacart", ["winning-in-retail-media"]),
    (r"school year|students", ["back-to-school-marketing"]),
    (r"Google Maps|map results|local listings?|business listings?", ["connecting-google-business-profile-to-paid-search"]),
    (r"audio|Spotify|radio", ["digital-audio", "finding-your-niche-with-audio"]),
    (r"automat(?:e|ed|ion|ing)", ["what-is-marketing-automation"]),
    (r"test(?:ing)? (?:two|different|variations|versions)|testing (?:headlines|creative|offers|ads)|split test(?:ing)?", ["a-simple-guide-to-a-b-testing"]),
    (r"YouTube|Gmail", ["google-discovery-ads"]),
    (r"newer channels|emerging channels|new channels", ["reddit-tiktok-and-dooh"]),
    (r"search engines understand|rich results|rich snippets", ["structured-data-made-simple"]),
    (r"right provider|new provider|choos(?:e|ing) (?:a |the right )?(?:partner|provider)|hire (?:a |an )?(?:agency|provider)", ["7-questions-to-vet-a-provider", "what-to-demand-from-anyone-who-runs-your-ads"]),
    (r"slow season|seasonal", ["summer-advertising-secrets", "back-to-school-marketing", "timing-your-digital-ads"]),
    (r"new customers|new audiences|grow(?:ing)? your (?:business|customer base)", ["finding-untapped-markets"]),
    (r"Amazon", ["amazon-advertising-for-beginners"]),
    (r"January|first quarter|start of the year", ["jumpstart-q1"]),
    (r"sales pitch|pitch|quotes?", ["red-flags-in-a-marketing-proposal", "why-the-cheapest-quote-isnt-the-cheapest-outcome"]),
    (r"every dollar|results per dollar|get more from", ["maximizing-roi"]),
    (r"where (?:your|the) money (?:goes|is going)|spending", ["audit-your-marketing-spend-in-an-afternoon"]),
    (r"what's changing|changing landscape|advertising trends|marketing trends", ["trends-worth-your-budget", "trends-small-businesses-must-master"]),
]
# whole words only: never link part of a word or part of a hyphenated compound
COMPILED = [(re.compile(r"(?<![\w-])(?:" + rx + r")(?![\w-])", re.I), targets) for rx, targets in RULES]
CTA = re.compile(r"\b(Get in touch|get in touch|Let's talk|let's talk|Contact us|contact us)\b")


def _link_block(block, used_targets, used_rules, self_slug, counts, budget):
    """Return (new_block, added) linking at most one phrase in a <p>/<li> block."""
    if "<a " in block or budget <= 0:
        return block, 0
    parts = re.split(r"(<[^>]+>)", block)
    for ri, (rx, targets) in enumerate(COMPILED):
        if ri in used_rules:
            continue
        cands = [t for t in targets if t != self_slug and t not in used_targets and t in counts]
        if not cands:
            continue
        for i, part in enumerate(parts):
            if part.startswith("<"):
                continue
            m = rx.search(part)
            if not m:
                continue
            target = min(cands, key=lambda t: (counts[t], targets.index(t)))
            parts[i] = part[:m.start()] + f'<a href="{target}">{m.group(0)}</a>' + part[m.end():]
            used_targets.add(target); used_rules.add(ri); counts[target] += 1
            return "".join(parts), 1
    return block, 0


def add_links(html, self_slug, counts, contact_href="../contact"):
    used_targets, used_rules, added = set(), set(), 0
    blocks = re.split(r"(<(?:p|li)>.*?</(?:p|li)>)", html, flags=re.S)
    # skip the first paragraph (the intro reads cleaner unlinked) unless the article is short
    first_p_seen = False
    for i, b in enumerate(blocks):
        if not re.match(r"<(?:p|li)>", b):
            continue
        if b.startswith("<p>") and not first_p_seen:
            first_p_seen = True
            continue
        nb, n = _link_block(b, used_targets, used_rules, self_slug, counts, MAX_LINKS - added)
        blocks[i] = nb; added += n
    out = "".join(blocks)
    # link the closing call to action ("Get in touch…") to the contact page
    last = list(re.finditer(r"<p>(?:(?!</p>).)*</p>", out, flags=re.S))
    for m in reversed(last[-2:]):
        seg = m.group(0)
        if "<a " not in seg and CTA.search(seg):
            seg2 = CTA.sub(lambda c: f'<a href="{contact_href}">{c.group(0)}</a>', seg, count=1)
            out = out[:m.start()] + seg2 + out[m.end():]
            break
    return out, added


MAX_INBOUND = 8


def link_library(posts, contact_href="../contact"):
    """Balanced linking across the whole library.

    Collects every possible (article, paragraph, phrase -> target) option, then assigns
    links in rounds: each round walks targets from least- to most-linked and gives each
    one more inbound link where an article still has room. Stops when no round adds a link.
    Mutates post["html"]; returns {slug: (outbound, inbound)}.
    """
    slugs = {p["slug"] for p in posts}
    state = {}
    options = {}  # target -> list of (slug, block_index, rule_index)
    for p in posts:
        blocks = re.split(r"(<(?:p|li)>.*?</(?:p|li)>)", p["html"], flags=re.S)
        first_p = next((i for i, b in enumerate(blocks) if b.startswith("<p>")), None)
        state[p["slug"]] = {"blocks": blocks, "used_blocks": set(), "used_rules": set(), "used_targets": set(), "out": 0}
        for bi, b in enumerate(blocks):
            if not re.match(r"<(?:p|li)>", b) or bi == first_p or "<a " in b:
                continue
            text = re.sub(r"<[^>]+>", "\x00", b)
            for ri, (rx, targets) in enumerate(COMPILED):
                if rx.search(text):
                    for t in targets:
                        if t != p["slug"] and t in slugs:
                            options.setdefault(t, []).append((p["slug"], bi, ri))
    inbound = {s: 0 for s in slugs}
    progress = True
    while progress:
        progress = False
        for t in sorted(slugs, key=lambda s: (inbound[s], s)):
            if inbound[t] >= MAX_INBOUND:
                continue
            best = None
            for (s, bi, ri) in options.get(t, []):
                st = state[s]
                if st["out"] >= MAX_LINKS or bi in st["used_blocks"] or ri in st["used_rules"] or t in st["used_targets"]:
                    continue
                key = (st["out"], s, bi)
                if best is None or key < best[0]:
                    best = (key, s, bi, ri)
            if best:
                _, s, bi, ri = best
                st = state[s]
                rx = COMPILED[ri][0]
                parts = re.split(r"(<[^>]+>)", st["blocks"][bi])
                for i, part in enumerate(parts):
                    if part.startswith("<"):
                        continue
                    m = rx.search(part)
                    if m:
                        parts[i] = part[:m.start()] + f'<a href="{t}">{m.group(0)}</a>' + part[m.end():]
                        break
                st["blocks"][bi] = "".join(parts)
                st["used_blocks"].add(bi); st["used_rules"].add(ri); st["used_targets"].add(t)
                st["out"] += 1; inbound[t] += 1; progress = True
    result = {}
    for p in posts:
        st = state[p["slug"]]
        out = "".join(st["blocks"])
        last = list(re.finditer(r"<p>(?:(?!</p>).)*</p>", out, flags=re.S))
        for m in reversed(last[-2:]):
            seg = m.group(0)
            if "<a " not in seg and CTA.search(seg):
                seg2 = CTA.sub(lambda c: f'<a href="{contact_href}">{c.group(0)}</a>', seg, count=1)
                out = out[:m.start()] + seg2 + out[m.end():]
                break
        p["html"] = out
        result[p["slug"]] = (st["out"], inbound[p["slug"]])
    return result
