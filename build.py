# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools[woff]>=4.55"]
# ///
"""Build Toffee: a COLRv1 variable font (wght, slnt, SHDW) from glyphs.py skeletons."""

import math
from pathlib import Path
from types import SimpleNamespace

from fontTools.colorLib.builder import buildCPAL  # noqa: F401  (import check)
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
from fontTools.fontBuilder import FontBuilder
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.ttLib.tables.otTables import PaintFormat
from fontTools import varLib

from glyphs import GLYPHS, ROUND_LEFT, ROUND_RIGHT, geo

ROOT = Path(__file__).parent
OUT = ROOT / "fonts"
MASTERS = ROOT / "build"
FAMILY = "Toffee"

K = 24  # support directions per convex piece
DIRS = [(math.cos(2 * math.pi * k / K), math.sin(2 * math.pi * k / K)) for k in range(K)]
Y0 = 270  # shear origin
BORDER = 48
SIDEBEARING = BORDER / 2 + 14
ROUND_ADJ = 10
SHADOW_DIR = (0.66, -0.75)
SHADOW_MAX = 1000

WEIGHTS = {300: (36, 26), 900: (112, 60)}  # wght -> (pen half-width, pen half-height)
SLANTS = {0: 0.0, -12: math.tan(math.radians(12))}
SHADOWS = {0: 0.0, SHADOW_MAX: float(SHADOW_MAX)}

PALETTES = [
    [(0.235, 0.110, 0.125, 1.0), (0.953, 0.925, 0.82, 1.0)],  # chocolate shadow, cream face
    [(0.95, 0.27, 0.13, 1.0), (1.0, 1.0, 1.0, 1.0)],  # orange shadow, white face
    [(0.0, 0.0, 0.0, 1.0), (1.0, 0.82, 0.25, 1.0)],  # black shadow, yellow face
    [(0.98, 0.45, 0.62, 1.0), (0.12, 0.12, 0.2, 1.0)],  # pink shadow, ink face
]


def hull(ells, t):
    """Convex hull of ellipses (cx, cy, pa, pb) after shear t, sampled at K directions, clockwise."""
    pts = []
    for ux, uy in DIRS:
        vx, vy = ux, t * ux + uy  # M^T u
        best = None
        for cx, cy, pa, pb in ells:
            h = math.sqrt(pa * pa * vx * vx + pb * pb * vy * vy)
            val = ux * cx + uy * cy + h
            if best is None or val > best[0] + 1e-9:
                ex, ey = pa * pa * vx / h, pb * pb * vy / h
                best = (val, cx + ex + t * ey, cy + ey)
        pts.append((best[1], best[2]))
    return pts[::-1]


def outline(strokes, p, dx, t, shadow=None):
    contours = []
    for st in strokes:
        ells = []
        for x, y, s, r in st:
            pa = s * p.a
            pb = s * (p.b + r * (p.a - p.b))
            if shadow is not None:
                pa, pb = pa + BORDER, pb + BORDER
            ells.append((x + dx + t * (y - Y0), y, pa, pb))
        pieces = [[ells[0]]] if len(ells) == 1 else [[ells[i], ells[i + 1]] for i in range(len(ells) - 1)]
        for piece in pieces:
            if shadow:
                sx, sy = SHADOW_DIR[0] * shadow, SHADOW_DIR[1] * shadow
                piece = piece + [(cx + sx, cy + sy, pa, pb) for cx, cy, pa, pb in piece]
            contours.append(hull(piece, t))
    return contours


def to_glyph(contours):
    pen = TTGlyphPen(None)
    for c in contours:
        pen.qCurveTo(*c, None)
        pen.closePath()
    g = pen.glyph()
    if g.numberOfContours > 0:
        g.flags[0] |= flagOverlapSimple
    return g


def spacing(name, strokes, p):
    """Return (dx, advance) from the upright face outline."""
    xs = [x for c in outline(strokes, p, 0, 0.0) for x, _ in c]
    lsb = SIDEBEARING - (ROUND_ADJ if name in ROUND_LEFT else 0)
    rsb = SIDEBEARING - (ROUND_ADJ if name in ROUND_RIGHT else 0)
    return lsb - min(xs), round(max(xs) - min(xs) + lsb + rsb)


def build_master(wght, slnt, shdw):
    a, b = WEIGHTS[wght]
    p = SimpleNamespace(a=a, b=b)
    g = geo(p)
    t = SLANTS[slnt]
    order = [".notdef", "space"]
    cmap = {0x20: "space", 0xA0: "space"}
    glyf = {".notdef": TTGlyphPen(None).glyph(), "space": TTGlyphPen(None).glyph()}
    space_adv = round(0.3 * g.wn + 120)
    adv = {".notdef": space_adv, "space": space_adv}
    for name, (uni, fn) in GLYPHS.items():
        strokes = fn(g)
        dx, advance = spacing(name, strokes, p)
        glyf[name] = to_glyph(outline(strokes, p, dx, t))
        glyf[name + ".shadow"] = to_glyph(outline(strokes, p, dx, t, shadow=SHADOWS[shdw]))
        adv[name] = adv[name + ".shadow"] = advance
        order += [name, name + ".shadow"]
        if uni is not None:
            cmap[uni] = name
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    gl = fb.font["glyf"]
    metrics = {}
    for n in order:
        gl[n].recalcBounds(gl)
        metrics[n] = (adv[n], getattr(gl[n], "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=930, descent=-300)
    fb.setupNameTable({"familyName": FAMILY, "styleName": "Regular"})
    fb.setupOS2(
        usWeightClass=wght,
        sTypoAscender=930, sTypoDescender=-300, sTypoLineGap=0,
        usWinAscent=1300, usWinDescent=1300,
        sxHeight=540, sCapHeight=730, fsSelection=0x80 | 0x40,
        achVendID="NONE", version=4,
    )
    fb.setupPost()
    return fb.font


def main():
    MASTERS.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    doc = DesignSpaceDocument()
    for tag, name, lo, default, hi in [
        ("wght", "Weight", 300, 900, 900),
        ("slnt", "Slant", -12, 0, 0),
        ("SHDW", "Shadow", 0, 0, SHADOW_MAX),
    ]:
        ax = AxisDescriptor()
        ax.tag, ax.name, ax.minimum, ax.default, ax.maximum = tag, name, lo, default, hi
        doc.addAxis(ax)
    for w in WEIGHTS:
        for sl in SLANTS:
            for sh in SHADOWS:
                font = build_master(w, sl, sh)
                path = MASTERS / f"{FAMILY}-{w}-{sl}-{sh}.ttf"
                font.save(path)
                src = SourceDescriptor()
                src.path = str(path)
                src.location = {"Weight": w, "Slant": sl, "Shadow": sh}
                doc.addSource(src)
    for w, wname in [(300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")]:
        for sl, suffix in [(0, ""), (-12, " Oblique")]:
            inst = InstanceDescriptor()
            inst.familyName = FAMILY
            inst.styleName = (wname + suffix).replace("Regular Oblique", "Oblique")
            inst.location = {"Weight": w, "Slant": sl, "Shadow": 0}
            doc.addInstance(inst)
    vf, _, _ = varLib.build(doc)

    # COLRv1: each base glyph = its shadow layer (palette 0) under its face (palette 1).
    colr = {}
    clips = {}
    masters = [TTFont(s.path) for s in doc.sources]
    for name in GLYPHS:
        colr[name] = {
            "Format": PaintFormat.PaintColrLayers,
            "Layers": [
                {"Format": PaintFormat.PaintGlyph, "Glyph": name + ".shadow",
                 "Paint": {"Format": PaintFormat.PaintSolid, "PaletteIndex": 0, "Alpha": 1.0}},
                {"Format": PaintFormat.PaintGlyph, "Glyph": name,
                 "Paint": {"Format": PaintFormat.PaintSolid, "PaletteIndex": 1, "Alpha": 1.0}},
            ],
        }
        boxes = []
        for m in masters:
            gg = m["glyf"][name + ".shadow"]
            if gg.numberOfContours:
                boxes.append((gg.xMin, gg.yMin, gg.xMax, gg.yMax))
        clips[name] = (min(b[0] for b in boxes) - 2, min(b[1] for b in boxes) - 2,
                       max(b[2] for b in boxes) + 2, max(b[3] for b in boxes) + 2)
    fb = FontBuilder(font=vf)
    fb.setupCPAL(PALETTES)
    fb.setupCOLR(colr, version=1, clipBoxes=clips)
    buildStatTable(
        vf,
        [
            {"tag": "wght", "name": "Weight", "values": [
                {"value": 300, "name": "Light"}, {"value": 400, "name": "Regular", "flags": 2},
                {"value": 500, "name": "Medium"}, {"value": 600, "name": "SemiBold"},
                {"value": 700, "name": "Bold"}, {"value": 800, "name": "ExtraBold"}, {"value": 900, "name": "Black"}]},
            {"tag": "slnt", "name": "Slant", "values": [
                {"value": 0, "name": "Upright", "flags": 2}, {"value": -12, "name": "Oblique"}]},
            {"tag": "SHDW", "name": "Shadow", "values": [
                {"value": 0, "name": "Outline", "flags": 2}, {"value": 400, "name": "Shadow"},
                {"value": 1000, "name": "Long Shadow"}]},
        ],
        elidedFallbackName=2,
    )
    vf["name"].setName("Black", 2, 3, 1, 0x409)
    vf["name"].setName(f"{FAMILY}-Black", 6, 3, 1, 0x409)
    vf["name"].setName(f"{FAMILY} Black", 4, 3, 1, 0x409)
    vf["name"].setName(f"{FAMILY}-Variable", 25, 3, 1, 0x409)
    stem = OUT / f"{FAMILY}[SHDW,slnt,wght]"
    vf.save(stem.with_suffix(".ttf"))
    vf.flavor = "woff2"
    vf.save(stem.with_suffix(".woff2"))
    print("glyphs:", len(GLYPHS), "->", stem.with_suffix(".ttf").stat().st_size // 1024, "KB ttf,",
          stem.with_suffix(".woff2").stat().st_size // 1024, "KB woff2")


if __name__ == "__main__":
    main()
