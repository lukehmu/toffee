# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools[woff]>=4.55"]
# ///
"""Build Toffee: a COLRv1 variable font (wght, slnt, SHDW) from glyphs.py skeletons."""

import functools
import math
import os
from pathlib import Path
from types import SimpleNamespace

from fontTools.colorLib.builder import populateCOLRv0
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
from fontTools.fontBuilder import FontBuilder
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.ttLib.tables.otTables import PaintFormat
from fontTools import varLib

from features import ot_features, set_code_pages, zero_width
from glyphs import BASE_OF, GLYPHS, PUNCT_SIDE, SPACING, geo
from kern import kern_feature

ROOT = Path(__file__).parent
OUT = ROOT / "fonts"
MASTERS = ROOT / "build"
FAMILY = "Toffee"

K = 24  # support directions per convex piece
DIRS = [(math.cos(2 * math.pi * k / K), math.sin(2 * math.pi * k / K)) for k in range(K)]
Y0 = 270  # shear origin
SCALE_LIMITS = (0.7, 1.35)  # how far a glyph's skeleton may be stretched to reach its width class
SHADOW_DIR = (0.66, -0.75)
SHADOW_MAX = 1000
VERSION = 1.0
VERSION_STRING = "Version 1.000"
RELEASE_EPOCH = 1793750400  # 2026-11-04 00:00 UTC; bump with VERSION
FIXED_WIDTH = [["plus", "minus", "equal", "less", "greater", "multiply", "divide", "plusminus", "logicalnot"]]
MARK_TOL = 1.0  # accent marks whose skeletons match this closely (at both weights) share one glyph

WEIGHTS = {300: (36, 32), 900: (112, 74)}  # wght -> (pen half-width, pen half-height)
SLANTS = (0, -12)  # slnt masters, degrees (shear = tan of the angle)
SHADOWS = (0, SHADOW_MAX)

PALETTES = [
    [(0.235, 0.110, 0.125, 1.0), (0.953, 0.925, 0.82, 1.0)],  # chocolate shadow, cream face
    [(0.95, 0.27, 0.13, 1.0), (1.0, 1.0, 1.0, 1.0)],  # orange shadow, white face
    [(0.0, 0.0, 0.0, 1.0), (1.0, 0.82, 0.25, 1.0)],  # black shadow, yellow face
    [(0.98, 0.45, 0.62, 1.0), (0.12, 0.12, 0.2, 1.0)],  # pink shadow, ink face
]
PALETTE_NAMES = ["Toffee", "Orange and white", "Black and yellow", "Pink and ink"]  # CPAL labels = index.html PRESETS names
PALETTE_ENTRIES = ["Shadow", "Face"]  # what palette index 0 and 1 paint
STYLES = [(300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")]
SHADOW_STYLES = [(0, "Outline"), (400, "Drop"), (1000, "Long")]  # SHDW names (STAT); 0 is elided


def hull(ells):
    """Convex hull of axis-aligned ellipses (cx, cy, pa, pb): its support point in each of the K DIRS."""
    pts = []
    for ux, uy in DIRS:
        best = None
        for cx, cy, pa, pb in ells:
            h = math.sqrt(pa * pa * ux * ux + pb * pb * uy * uy)
            val = ux * cx + uy * cy + h
            if best is None or val > best[0] + 1e-9:
                best = (val, cx + pa * pa * ux / h, cy + pb * pb * uy / h)
        pts.append((best[1], best[2]))
    return pts


def _sweep_plan():
    """[(direction index, from the shadow copy?)]: the shadow contour of a convex piece P is hull(P, P + o).

    Direction k takes the copy's point when u_k . o > 0. o is fixed in sheared space, so before the shear
    it depends on the slant, and a direction near the long edges' normal would switch from P to the copy
    between slant masters: the in-between point would then sit partway along the long edge, cutting the
    corner. So the direction at each long edge takes both points (P's, then the copy's, or the reverse),
    K + 2 in all, the same in every master; the other directions must keep their side at every slant.
    """
    def side(t):
        ox, oy = SHADOW_DIR[0] - t * SHADOW_DIR[1], SHADOW_DIR[1]
        return [ux * ox + uy * oy for ux, uy in DIRS]

    ts = [math.tan(math.radians(-s)) for s in SLANTS]
    mid = side(sum(ts) / len(ts))
    front = [v > 0 for v in mid]
    both = {min((k - 1) % K, k, key=lambda i: abs(mid[i])) for k in range(K) if front[k - 1] != front[k]}
    for t in ts:
        assert all(k in both or (v > 0) == front[k] for k, v in enumerate(side(t))), "SHADOW_DIR vs K"
    plan = []
    for k in range(K):
        if k in both:
            plan += [(k, front[k - 1]), (k, not front[k - 1])]
        else:
            plan.append((k, front[k]))
    return plan


SWEEP = _sweep_plan()


def outline(strokes, p, dx, t, shadow=None):
    """Convex contours (clockwise) of the strokes: hulls built upright, then sheared by t about Y0.

    Every slant master is the same upright hull sheared, so points interpolate linearly between slant
    masters (a hull built in sheared space picks different support points per slant, and in-between
    instances distort). The shadow copy is offset by (sx - t*sy, sy) before the shear, so after it the
    shadow points along SHADOW_DIR at every slant. A shadow contour has K + 2 points (SWEEP), also at
    SHDW 0, where the copy coincides.
    """
    contours = []
    sx, sy = (SHADOW_DIR[0] * shadow, SHADOW_DIR[1] * shadow) if shadow else (0.0, 0.0)
    ox, oy = sx - t * sy, sy
    for st in strokes:
        ells = []
        for x, y, s, r in st:
            pa = s * p.a
            pb = s * (p.b + r * (p.a - p.b))
            if shadow is not None:
                pa, pb = pa + p.border, pb + p.border
            ells.append((x + dx, y, pa, pb))
        pieces = [[ells[0]]] if len(ells) == 1 else [[ells[i], ells[i + 1]] for i in range(len(ells) - 1)]
        for piece in pieces:
            pts = hull(piece)
            if shadow is not None:
                pts = [(pts[k][0] + ox, pts[k][1] + oy) if copy else pts[k] for k, copy in SWEEP]
            contours.append([(px + t * (py - Y0), py) for px, py in pts[::-1]])
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


def pen_params(a, b):
    """Per-weight pen, border and spacing. All linear in a, so two masters reproduce them exactly."""
    border = 24 + 0.21 * a  # outline thickness of the shadow layer
    sb = 99 - 0.6 * a  # straight sidebearing: references open sidebearings as weight drops
    # A glyph's border must not paint over its neighbour's face, so no side goes below half the border.
    return SimpleNamespace(a=a, b=b, border=border, sb=sb, min_sb=border / 2 + 4)


def ink_x(strokes, p, band=None):
    """Ink x-extent of the upright outline, optionally only from points with band[0] <= y <= band[1]."""
    contours = outline(strokes, p, 0, 0.0)
    if band is None:
        xs = [x for c in contours for x, _ in c]
        return min(xs), max(xs)
    lo, hi = band
    xs = []
    for c in contours:  # clip each convex polygon to the band: vertices inside plus edge crossings
        for (xa, ya), (xb, yb) in zip(c, c[1:] + c[:1]):
            if lo <= ya <= hi:
                xs.append(xa)
            for yy in (lo, hi):
                if (ya - yy) * (yb - yy) < 0:
                    xs.append(xa + (xb - xa) * (yy - ya) / (yb - ya))
    if not xs:
        return ink_x(strokes, p)
    return min(xs), max(xs)


def place(name, strokes, p, g, n_adv, clamped):
    """Return (strokes, dx, advance) following the SPACING table in glyphs.py.

    A side marked ("T", ratio) is measured only inside the main band (x-height, or cap height for
    capitals), so tails, hooks and descender flicks overhang into the neighbour's space.
    """
    spec = SPACING.get(name) or SPACING.get(BASE_OF.get(name, ""))
    if spec is None:
        x0, x1 = ink_x(strokes, p)
        side = max(PUNCT_SIDE * p.sb, p.min_sb)
        return strokes, side - x0, round(x1 - x0 + 2 * side), 1.0, 0.0
    r, left, right = spec
    top = g.C if name[0].isupper() else g.X
    band = (0.3 * top, top)

    def extents(st):
        full = ink_x(st, p)
        lo = ink_x(st, p, band)[0] if isinstance(left, tuple) else full[0]
        hi = ink_x(st, p, band)[1] if isinstance(right, tuple) else full[1]
        return lo, hi

    def ratio(side):
        return side[1] if isinstance(side, tuple) else side

    adv = r * n_adv
    sl = max(ratio(left) * p.sb, p.min_sb)
    sr = max(ratio(right) * p.sb, p.min_sb)
    sk = [x for st in strokes for x, *_ in st]
    sk0 = min(sk)

    def scaled(k):
        return [[(sk0 + (x - sk0) * k, y, s, rr) for x, y, s, rr in st] for st in strokes]

    # Measured width is linear in the skeleton scale k, so two measurements solve for the target.
    w1 = (lambda e: e[1] - e[0])(extents(strokes))
    w2 = (lambda e: e[1] - e[0])(extents(scaled(1.2)))
    k = 1.0
    if w2 - w1 > 1:
        k = 1 + 0.2 * (adv - sl - sr - w1) / (w2 - w1)
        if not SCALE_LIMITS[0] <= k <= SCALE_LIMITS[1]:
            clamped.append(f"{name}:{k:.2f}")
            k = min(max(k, SCALE_LIMITS[0]), SCALE_LIMITS[1])
        strokes = scaled(k)
    x0, x1 = extents(strokes)
    spare = adv - (x1 - x0) - sl - sr  # non-zero only when the scale was clamped
    sl += spare * sl / (sl + sr)
    dx = sl - x0
    if isinstance(right, tuple):
        # A right-hand tail (baseline flick, f's hook) must end inside the advance: overhanging it would
        # slide under the next glyph, whose border is painted on top of this glyph's face.
        overhang = ink_x(strokes, p)[1] + dx - adv
        adv += max(0.0, overhang)
    return strokes, dx, round(adv), k, sk0


def place_composite(strokes, n_base, base_placed):
    """An accented letter takes its base's placement: base strokes get the base's scale, marks only move.

    Stretching a mark with its base would make the same accent change width from letter to letter.
    """
    _, dx, adv, k, sk0 = base_placed
    out = [[(sk0 + (x - sk0) * k, y, s, r) for x, y, s, r in st] for st in strokes[:n_base]]
    for st in strokes[n_base:]:
        xs = [x for x, *_ in st]
        mid = (min(xs) + max(xs)) / 2
        shift = (sk0 + (mid - sk0) * k) - mid
        out.append([(x + shift, y, s, r) for x, y, s, r in st])
    return out, dx, adv, k, sk0


def compound(base, mark, offset):
    """A TrueType composite: base at the origin, mark moved by offset."""
    pen = TTGlyphPen({base, mark})  # the pen only checks that component names exist
    pen.addComponent(base, (1, 0, 0, 1, 0, 0))
    pen.addComponent(mark, (1, 0, 0, 1, *offset))
    g = pen.glyph()
    g.components[0].flags |= 0x0400  # OVERLAP_COMPOUND: the components overlap
    return g


def notdef():
    pen = TTGlyphPen(None)
    for box in [(60, 0, 440, 730), (120, 60, 380, 670)]:
        x0, y0, x1, y1 = box
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        if box[0] == 120:
            pts.reverse()
        pen.moveTo(pts[0])
        for pt in pts[1:]:
            pen.lineTo(pt)
        pen.closePath()
    return pen.glyph()


def pen_at(wght):
    """(a, b) of the pen at any weight: linear between the two weight masters, as the VF interpolates."""
    (w0, (a0, b0)), (w1, (a1, b1)) = sorted(WEIGHTS.items())
    f = (wght - w0) / (w1 - w0)
    return a0 + (a1 - a0) * f, b0 + (b1 - b0) * f


def _same(u, v):
    return all(abs(i - j) < 1e-6 for i, j in zip(u, v))


@functools.cache
def _kept(name):
    """Per stroke, the sample indices to keep.

    A sample equal to the one before it at every weight master (S() joining two parts at a shared point)
    makes a zero-length segment: one more contour that adds nothing. Deciding over all weights keeps the
    point count the same in every master; a stroke's first sample always stays, so dots keep their one.
    """
    per_w = [GLYPHS[name][1](geo(pen_params(*ab))) for ab in WEIGHTS.values()]
    return [
        [j for j in range(len(st)) if j == 0 or not all(_same(sw[i][j - 1], sw[i][j]) for sw in per_w)]
        for i, st in enumerate(per_w[0])
    ]


def skeleton(name, g):
    """glyphs.py's strokes for a glyph, without zero-length segments."""
    return [[st[j] for j in keep] for st, keep in zip(GLYPHS[name][1](g), _kept(name))]


@functools.cache
def layout(wght):
    """Pen, metrics and placed skeletons at one weight (slant and shadow don't change them).

    Returns (p, g, placed, composite_of): placed[name] = (strokes, dx, advance, k, sk0), and
    composite_of[accented glyph] = (base glyph, number of base strokes).
    """
    a, b = pen_at(wght)
    p = pen_params(a, b)
    g = geo(p)
    n_adv = g.wn + 2 * a + 2 * p.sb  # every width class is a ratio of this
    clamped = []
    placed = {}
    composite_of = {}
    for name in GLYPHS:
        strokes = skeleton(name, g)
        base = BASE_OF.get(name)
        base_strokes = skeleton(base, g) if base in GLYPHS else None
        if base_strokes is not None and strokes[: len(base_strokes)] == base_strokes:
            continue  # placed below, from its base
        placed[name] = place(name, strokes, p, g, n_adv, clamped)
    for name in GLYPHS:
        if name not in placed:
            base = BASE_OF[name]
            if base in placed:
                n_base = len(skeleton(base, g))
                placed[name] = place_composite(skeleton(name, g), n_base, placed[base])
                composite_of[name] = (base, n_base)
            else:  # base is itself a composite: just space it normally
                placed[name] = place(name, skeleton(name, g), p, g, n_adv, clamped)
    if clamped:
        print(f"wght {wght}: width class out of scale range, clamped:", " ".join(clamped))
    for group in FIXED_WIDTH:  # one advance for the group, each glyph centred in it
        width = max(placed[n][2] for n in group)
        for n in group:
            st, dx, advance, *rest = placed[n]
            placed[n] = (st, dx + (width - advance) / 2, width, *rest)
    zero_width(placed)
    return p, g, placed, composite_of


def mark_strokes(placed, composite_of, name):
    """An accented glyph's mark strokes relative to their centroid, and the centroid."""
    strokes = placed[name][0][composite_of[name][1] :]
    pts = [(x, y) for st in strokes for x, y, *_ in st]
    cx, cy = sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)
    return [[(x - cx, y - cy, s, r) for x, y, s, r in st] for st in strokes], (cx, cy)


@functools.cache
def mark_glyphs():
    """{accented glyph: its mark glyph}. Marks with the same shape at both weights share one glyph.

    The same accent is drawn once and placed by the composite's offset, which varies per master.
    Named after the first glyph that uses it.
    """
    lays = [layout(w) for w in WEIGHTS]
    assert all(lay[3] == lays[0][3] for lay in lays), "composites differ between weight masters"

    def close(m1, m2):
        return [len(st) for st in m1] == [len(st) for st in m2] and all(
            abs(a[0] - b[0]) <= MARK_TOL and abs(a[1] - b[1]) <= MARK_TOL and _same(a[2:], b[2:])
            for s1, s2 in zip(m1, m2)
            for a, b in zip(s1, s2)
        )

    shapes, out = [], {}
    for name in lays[0][3]:
        sig = [mark_strokes(lay[2], lay[3], name)[0] for lay in lays]
        for other, mark in shapes:
            if all(close(a, b) for a, b in zip(sig, other)):
                out[name] = mark
                break
        else:
            shapes.append((sig, name + ".mark"))
            out[name] = name + ".mark"
    return out


def build_master(wght, slnt, shdw):
    """One master. Any location builds (tests compare in-between VF instances with direct builds)."""
    p, g, placed, composite_of = layout(wght)
    marks = mark_glyphs()
    t = math.tan(math.radians(-slnt))
    order = [".notdef", "space"]
    cmap = {0x20: "space", 0xA0: "space"}
    glyf = {".notdef": notdef(), "space": TTGlyphPen(None).glyph()}
    space_adv = round(0.4 * (g.wn + 2 * p.a + 2 * p.sb))  # a word space scales with the weight, like n
    adv = {".notdef": 500, "space": space_adv}
    for name, (uni, _) in GLYPHS.items():
        strokes, dx, advance, *_ = placed[name]
        if name in composite_of:
            # TrueType composite: the base glyph's outline (identical by construction) plus a mark glyph,
            # drawn around (0, 0) and moved into place. Shear about Y0 turns a move (x, y) into (x + t*y, y).
            base, _ = composite_of[name]
            mark = marks[name]
            rel, (cx, cy) = mark_strokes(placed, composite_of, name)
            if mark not in glyf:
                glyf[mark] = to_glyph(outline(rel, p, 0, t))
                glyf[mark + ".shadow"] = to_glyph(outline(rel, p, 0, t, shadow=float(shdw)))
                adv[mark] = adv[mark + ".shadow"] = 0
                order += [mark, mark + ".shadow"]
            offset = (round(cx + dx + t * cy), round(cy))
            glyf[name] = compound(base, mark, offset)
            glyf[name + ".shadow"] = compound(base + ".shadow", mark + ".shadow", offset)
        else:
            glyf[name] = to_glyph(outline(strokes, p, dx, t))
            glyf[name + ".shadow"] = to_glyph(outline(strokes, p, dx, t, shadow=float(shdw)))
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
    # Caret slope follows the slant; varLib puts the run in MVAR (hcrn), so in-between slants get it too.
    fb.setupHorizontalHeader(ascent=930, descent=-300, caretSlopeRise=1000, caretSlopeRun=round(1000 * t))
    fb.setupNameTable({"familyName": FAMILY, "styleName": "Regular", "version": VERSION_STRING}, mac=False)
    fb.font["head"].fontRevision = VERSION
    fb.setupOS2(
        usWeightClass=wght,
        sTypoAscender=930, sTypoDescender=-300, sTypoLineGap=0,
        usWinAscent=1000, usWinDescent=300,  # replaced on the VF by the real extremes over all masters
        sxHeight=g.X, sCapHeight=g.C, fsSelection=0x80 | 0x40,
        achVendID="NONE", version=4,
    )
    # Underline half the pen's height thick, a little below the baseline; varies with weight (MVAR unds/undo).
    fb.setupPost(italicAngle=slnt, underlineThickness=round(p.b), underlinePosition=-round(100 + p.b / 2))
    fea = ot_features(placed, g, t, Y0) + kern_fea(wght)
    if fea:
        fb.addOpenTypeFeatures(fea)
    return fb.font


@functools.cache
def kern_fea(wght):
    """The kern feature at one weight, from the upright faces at their final x."""
    p, g, placed, _ = layout(wght)
    faces = {n: outline(placed[n][0], p, placed[n][1], 0.0) for n in GLYPHS}
    return kern_feature(faces, {n: placed[n][2] for n in GLYPHS}, p, g)


def main():
    # Reproducible output: fontTools stamps head.created/modified from SOURCE_DATE_EPOCH when it's set.
    # Default it to this version's release date, so an unchanged source rebuilds to identical bytes.
    os.environ.setdefault("SOURCE_DATE_EPOCH", str(RELEASE_EPOCH))
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
    # Named instances: every weight upright and oblique, plus a few with the shadow on.
    named = [(w, sl, 0, (wname + suffix).replace("Regular Oblique", "Oblique"))
             for w, wname in STYLES for sl, suffix in [(0, ""), (-12, " Oblique")]]
    named += [(w, 0, sh, f"{wname} {sname}") for w, wname in [(700, "Bold"), (900, "Black")]
              for sh, sname in SHADOW_STYLES[1:]]
    for w, sl, sh, style in named:
        inst = InstanceDescriptor()
        inst.familyName = FAMILY
        inst.styleName = style
        inst.postScriptFontName = f"{FAMILY}-{style.replace(' ', '')}"
        inst.location = {"Weight": w, "Slant": sl, "Shadow": sh}
        doc.addInstance(inst)
    vf, _, _ = varLib.build(doc)

    # COLRv1: each base glyph = its shadow layer (palette 0) under its face (palette 1). The same two
    # layers as COLRv0 records too, for renderers without v1 (Safari, older Windows); v1 renderers use v1.
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
    fb.setupCPAL(PALETTES, paletteLabels=PALETTE_NAMES, paletteEntryLabels=PALETTE_ENTRIES)
    fb.setupCOLR(colr, version=1, clipBoxes=clips)
    populateCOLRv0(vf["COLR"].table, {n: [(n + ".shadow", 0), (n, 1)] for n in GLYPHS}, vf.getReverseGlyphMap())
    buildStatTable(
        vf,
        [
            {"tag": "wght", "name": "Weight", "values": [
                {"value": v, "name": n, **({"flags": 2} if v == 400 else {})} for v, n in STYLES]},
            {"tag": "slnt", "name": "Slant", "values": [
                {"value": 0, "name": "Upright", "flags": 2}, {"value": -12, "name": "Oblique"}]},
            {"tag": "SHDW", "name": "Shadow", "values": [
                {"value": v, "name": n, **({"flags": 2} if v == 0 else {})} for v, n in SHADOW_STYLES]},
        ],
        elidedFallbackName=2,
        macNames=False,  # with Mac names it can't reuse fvar's Windows-only records, and duplicates them
    )
    for nid, text in [
        (0, "Copyright 2026 The Toffee Project Authors (https://github.com/lukehmu/toffee)"),
        (13, "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
             "This license is available with a FAQ at: https://openfontlicense.org"),
        (14, "https://openfontlicense.org"),
    ]:
        vf["name"].setName(text, nid, 3, 1, 0x409)
    vf["OS/2"].fsType = 0  # installable embedding
    # The default instance is Black, which isn't one of the four RIBBI styles: legacy menus get
    # "Toffee Black" / Regular (IDs 1/2), and typographic family/subfamily go in IDs 16/17.
    for nid, text in [
        (1, f"{FAMILY} Black"),
        (2, "Regular"),
        (3, f"{VERSION:.3f};NONE;{FAMILY}-Black"),
        (4, f"{FAMILY} Black"),
        (6, f"{FAMILY}-Black"),
        (16, FAMILY),
        (17, "Black"),
        (25, FAMILY),
    ]:
        vf["name"].setName(text, nid, 3, 1, 0x409)
    os2 = vf["OS/2"]
    set_code_pages(vf)
    os2.usWinAscent = max(m["head"].yMax for m in masters)
    os2.usWinDescent = max(-m["head"].yMin for m in masters)
    prep = newTable("prep")  # smart dropout control for unhinted TrueType
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    vf["prep"] = prep
    vf["name"].removeNames(platformID=1)
    gasp = newTable("gasp")
    gasp.version, gasp.gaspRange = 1, {0xFFFF: 0x000F}
    vf["gasp"] = gasp
    stem = OUT / f"{FAMILY}[SHDW,slnt,wght]"
    vf.save(stem.with_suffix(".ttf"))
    vf.flavor = "woff2"
    vf.save(stem.with_suffix(".woff2"))
    print("glyphs:", len(GLYPHS), "->", stem.with_suffix(".ttf").stat().st_size // 1024, "KB ttf,",
          stem.with_suffix(".woff2").stat().st_size // 1024, "KB woff2")


if __name__ == "__main__":
    main()
