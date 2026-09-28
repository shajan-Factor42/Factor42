#!/usr/bin/env python3
"""Serve the site like GitHub Pages (extensionless .html, 404.html) under a /Factor42/ prefix,
screenshot every page at desktop and phone widths, and check every internal link and asset."""
import http.server, threading, pathlib, sys, urllib.parse, re, functools
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(sys.argv[1]).resolve()
SHOTS = pathlib.Path(sys.argv[2]); SHOTS.mkdir(parents=True, exist_ok=True)
PREFIX = "/Factor42"

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_head(self):
        path = urllib.parse.urlparse(self.path).path
        if not path.startswith(PREFIX):
            self.send_error(404); return None
        rel = path[len(PREFIX):].lstrip("/")
        f = ROOT / rel
        if f.is_dir(): f = f / "index.html"
        elif not f.exists() and (ROOT / (rel + ".html")).exists(): f = ROOT / (rel + ".html")
        if not f.exists():
            self.send_response(404); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.missing = True
            return open(ROOT / "404.html", "rb")
        ctype = self.guess_type(str(f))
        self.send_response(200); self.send_header("Content-Type", ctype); self.end_headers()
        return open(f, "rb")

srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:8765{PREFIX}/"

pages = ["privacy-policy", "terms-of-service", "sla", "security", "careers", "library", "", "agencies", "broadcasters", "about", "contact", "thank-you", "blog/", "blog/is-seo-dead", "blog/what-to-demand-from-anyone-who-runs-your-ads", "blog/why-ctv-belongs-in-your-mix"]
problems, links = [], set()
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, tag in [(1440, 900, "desktop"), (390, 844, "phone")]:
        for pg_name in pages:
            pg = b.new_page(viewport={"width": vw, "height": vh})
            errs = []
            pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" else None)
            bad = []
            pg.on("response", lambda r, bad=bad: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            pg.goto(BASE + pg_name, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if overflow > 0: problems.append(f"[{tag}] {pg_name or 'home'}: horizontal overflow {overflow}px")
            fam = pg.evaluate("getComputedStyle(document.querySelector('h1')).fontFamily")
            loaded = pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight)")
            if tag == "desktop" and pg_name == "": print("fonts loaded:", loaded)
            for e in errs: problems.append(f"[{tag}] {pg_name or 'home'}: console error {e}")
            for x in bad: problems.append(f"[{tag}] {pg_name or 'home'}: {x}")
            for h in pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)"):
                links.add(h)
            pg.screenshot(path=str(SHOTS / f"{tag}-{(pg_name or 'home').replace('/','_')}.png"), full_page=True)
            pg.close()
    # check internal links
    pg = b.new_page()
    dead = {}
    for h in sorted(links):
        u = urllib.parse.urlparse(h)
        if u.netloc != "127.0.0.1:8765": continue
        target = h.split("#")[0]
        r = pg.request.get(target)
        if r.status >= 400:
            dead.setdefault(u.path, 0); dead[u.path] += 1
        frag = u.fragment
        if frag and r.status < 400:
            pg.goto(target)
            if not pg.query_selector(f"#{frag}"): problems.append(f"missing anchor #{frag} on {u.path}")
    b.close()
srv.shutdown()
print("checked", len(links), "links")
print("DEAD INTERNAL LINKS:", dead or "none")
print("PROBLEMS:", *problems, sep="\n  ") if problems else print("PROBLEMS: none")
