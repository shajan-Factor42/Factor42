#!/usr/bin/env python3
"""Build Factor42 logo SVGs with the wordmark converted to outlines, then render PNGs."""
import pathlib, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = pathlib.Path(sys.argv[1])
FONTS = pathlib.Path("/tmp/fontwork/node_modules/@fontsource")
DISPLAY = TTFont(FONTS / "schibsted-grotesk/files/schibsted-grotesk-latin-800-normal.woff2")
MONO = TTFont(FONTS / "geist-mono/files/geist-mono-latin-400-normal.woff2")

INK, PAPER, ACCENT, ACCENT_LIGHT = "#0B1626", "#F5F3EE", "#C2410C", "#F4A26B"


def outline(font, text, size, x, baseline, tracking_em=0.0):
    """Return (svg path d, advance width in px) for text set at `size` px, baseline at y."""
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    kern = {}
    s = size / upm
    pen = SVGPathPen(gs)
    cx = x
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (s, 0, 0, -s, cx, baseline))
        gs[g].draw(tp)
        cx += hmtx[g][0] * s + tracking_em * size
    return pen.getCommands(), cx - x - tracking_em * size


def mark_svg(sq, f, ex, ox=0, oy=0, scale=1.0):
    r = lambda v: round(v * scale, 3)
    return (f'<g transform="translate({ox} {oy})">'
            f'<rect x="0" y="{r(10)}" width="{r(38)}" height="{r(38)}" rx="{r(7)}" fill="{sq}"/>'
            f'<rect x="{r(10)}" y="{r(19)}" width="{r(6.5)}" height="{r(20)}" fill="{f}"/>'
            f'<rect x="{r(10)}" y="{r(19)}" width="{r(18)}" height="{r(6)}" fill="{f}"/>'
            f'<rect x="{r(10)}" y="{r(28.5)}" width="{r(13)}" height="{r(5.5)}" fill="{f}"/>'
            f'<rect x="{r(40)}" y="0" width="{r(8)}" height="{r(8)}" rx="{r(2)}" fill="{ex}"/></g>')


def lockup(reversed_=False, with_media=True):
    sq, f, ex = (PAPER, INK, ACCENT_LIGHT) if reversed_ else (INK, PAPER, ACCENT)
    word_color = PAPER if reversed_ else INK
    sup_color = ACCENT_LIGHT if reversed_ else ACCENT
    media_color = "#B8BFCC" if reversed_ else "#4A5264"
    mark_scale = 2.0                     # mark is 96 x 96
    size = 92                            # wordmark size
    tx = 96 + 24
    baseline = 92
    d1, w1 = outline(DISPLAY, "Factor", size, tx, baseline, -0.045)
    d2, w2 = outline(DISPLAY, "42", size * 0.5, tx + w1 + size * 0.06 - 0.045 * size, baseline - 0.9 * size * 0.5, -0.02)
    parts = [mark_svg(sq, f, ex, 0, 0, mark_scale),
             f'<path d="{d1}" fill="{word_color}"/>',
             f'<path d="{d2}" fill="{sup_color}"/>']
    width = tx + w1 + w2 + size * 0.06 + 6
    height = 96
    if with_media:
        height = 122
        d3, _ = outline(MONO, "MEDIA", 14, tx + 3, 118, 0.62)
        parts.append(f'<path d="{d3}" fill="{media_color}"/>')
    return width, height, parts


def write_svg(name, w, h, parts, bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(w,2)} {h}" width="{round(w,2)}" height="{h}" role="img" aria-label="Factor42 Media">'
           f'<title>Factor42 Media</title>{bgrect}{"".join(parts)}</svg>\n')
    (OUT / name).write_text(svg)
    return svg


w, h, parts = lockup()
write_svg("logo.svg", w, h, parts)
w, h, parts = lockup(reversed_=True)
write_svg("logo-reversed.svg", w, h, parts)
w, h, parts = lockup(with_media=False)
write_svg("logo-horizontal.svg", w, h, parts)
(OUT / "mark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Factor42 Media"><title>Factor42 Media</title>' + mark_svg(INK, PAPER, ACCENT) + "</svg>\n")
# Favicon: adapts to dark browser chrome
(OUT / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><style>.s{fill:#0B1626}.f{fill:#F5F3EE}@media (prefers-color-scheme:dark){.s{fill:#F5F3EE}.f{fill:#0B1626}}</style>'
    '<rect class="s" x="0" y="10" width="38" height="38" rx="7"/><rect class="f" x="10" y="19" width="6.5" height="20"/><rect class="f" x="10" y="19" width="18" height="6"/><rect class="f" x="10" y="28.5" width="13" height="5.5"/><rect x="40" y="0" width="8" height="8" rx="2" fill="#C2410C"/></svg>\n')
print("svgs written")
