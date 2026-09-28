#!/usr/bin/env python3
"""Render PNG logo, icons and the social share image with headless Chromium."""
import pathlib, sys
from playwright.sync_api import sync_playwright

SITE = pathlib.Path(sys.argv[1])
IMG = SITE / "assets" / "img"
FONTS = (SITE / "assets" / "fonts").as_uri()
MARK = (IMG / "mark.svg").read_text()
LOGO = (IMG / "logo.svg").read_text()
LOGO_FLUID = LOGO.replace("<svg ", '<svg style="width:100%;height:auto" ', 1)

FONT_CSS = f"""
@font-face {{ font-family: D; font-weight: 800; src: url('{FONTS}/schibsted-grotesk-latin-800-normal.woff2'); }}
@font-face {{ font-family: B; font-weight: 400; src: url('{FONTS}/geist-sans-latin-400-normal.woff2'); }}
@font-face {{ font-family: M; font-weight: 400; src: url('{FONTS}/geist-mono-latin-400-normal.woff2'); }}
html,body {{ margin:0; }}
"""

WHITE_MARK = MARK.replace('fill="#0B1626"', 'fill="#FFFFFF"', 1).replace('fill="#F5F3EE"', 'fill="#C2410C"').replace('rx="2.0" fill="#C2410C"', 'rx="2.0" fill="#0B1626"')

jobs = {
    "logo-512.png": (512, 512, f'<div style="width:512px;height:512px;background:#FFFFFF;display:grid;place-items:center"><div style="width:360px;height:360px">{MARK}</div></div>', False),
    "favicon-32.png": (32, 32, f'<div style="width:32px;height:32px">{MARK}</div>', True),
    "apple-touch-icon.png": (180, 180, f'<div style="width:180px;height:180px;background:#C2410C;display:grid;place-items:center"><div style="width:104px;height:104px">{WHITE_MARK}</div></div>', False),
    "logo-1200.png": (1200, 340, f'<div style="width:1200px;height:340px;display:grid;place-items:center"><div style="width:1000px">{LOGO_FLUID}</div></div>', True),
    "og-image.png": (1200, 630, f"""
<div style="width:1200px;height:630px;box-sizing:border-box;background:#F5F3EE;position:relative;overflow:hidden;padding:72px 80px;display:flex;flex-direction:column;justify-content:space-between">
  <div style="width:430px">{LOGO_FLUID}</div>
  <div style="font-family:D;font-weight:800;font-size:88px;line-height:.95;letter-spacing:-0.04em;color:#0B1626;max-width:820px">The ad ops team behind <span style="color:#C2410C">your brand.</span></div>
  <div style="font-family:M;font-size:20px;letter-spacing:.14em;color:#4A5264">WHITE-LABEL AD OPERATIONS · FACTOR42MEDIA.COM</div>
  <div style="position:absolute;right:-70px;bottom:-60px;width:420px;height:420px;opacity:.07">{MARK}</div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:14px;background:#C2410C"></div>
</div>""", False),
}

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (w, h, html, transparent) in jobs.items():
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        tmp = pathlib.Path(__file__).parent / "_render.html"
        tmp.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{FONT_CSS} svg{{display:block;width:100%;height:100%}}</style></head><body>{html}</body></html>")
        pg.goto(tmp.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(IMG / name), omit_background=transparent, clip={"x": 0, "y": 0, "width": w, "height": h})
        pg.close()
    b.close()
print("pngs:", ", ".join(jobs))
