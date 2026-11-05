# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools[woff]>=4.55"]
# ///
"""Cheap checks on the built VF. Run after `uv run build.py`:  uv run tests/check_font.py

- In-between instances match directly built masters (point distance): slant must be exact up to rounding,
  weight within the pen's own non-linearity (an ellipse's support point isn't linear in its axes).
- Every cmap glyph that has ink has a COLRv1 paint, a clip box and a COLRv0 record; no .shadow/.mark is mapped.
- Report-only (WARN, exit 0): face yMax above the hhea ascender at either weight master.

Exit 1 on any FAIL.
"""

import io
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib.instancer import instantiateVariableFont  # noqa: E402

import build  # noqa: E402

VF = ROOT / "fonts" / "Toffee[SHDW,slnt,wght].ttf"
# (wght, slnt, SHDW), max allowed contour distance in units.
# Slant is exact up to rounding: the VF interpolates the shear linearly from 0 to tan 12 while a direct
# build uses tan 6, up to ~1.5 units apart at the far end of a shadow.
# Weight isn't exact: an ellipse's support point isn't linear in its axes (p99 ~13), and where a tangent
# edge between two pen positions turns past a sample direction between the weight masters, the in-between
# point cuts across the corner (worst ~37, ampersand.shadow at 600). The limit catches regressions.
INSTANCES = [
    ((900, -6, 0), 3),
    ((300, -6, 0), 3),
    ((900, -6, 1000), 3),
    ((600, 0, 0), 40),
    ((600, -6, 500), 40),
]

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL", msg)


def reload(font):
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return TTFont(buf)


def contours(font, name):
    glyf = font["glyf"]
    g = glyf[name]
    if g.numberOfContours == 0:
        return []
    coords, ends, _ = g.getCoordinates(glyf)
    out, s = [], 0
    for e in ends:
        out.append(list(coords[s : e + 1]))
        s = e + 1
    return out


def seg_dist(pt, a, b):
    (px, py), (ax, ay), (bx, by) = pt, a, b
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy
    u = 0.0 if ll == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / ll))
    return math.hypot(px - ax - u * dx, py - ay - u * dy)


def off_polygon(pt, poly):
    """Distance from a point to a closed control polygon."""
    return min(seg_dist(pt, a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


def contour_dist(ca, cb):
    """How far two point-compatible contours are apart as shapes.

    Point to point, except where a point has slid along its contour: a hull support point can switch
    between the two ends of a straight tangent edge from one master to the next (two pen sizes, or a glyph
    and its shadow copy), and the in-between instance then puts it partway along that same edge. So a
    point that moved is measured to the other contour's control polygon, both ways.
    """
    worst = 0.0
    for p, q in zip(ca, cb):
        d = math.dist(p, q)
        if d > 1:
            d = max(off_polygon(p, cb), off_polygon(q, ca))
        worst = max(worst, d)
    return worst


def check_instances(vf):
    for loc, tol in INSTANCES:
        wght, slnt, shdw = loc
        inst = instantiateVariableFont(vf, {"wght": wght, "slnt": slnt, "SHDW": shdw}, inplace=False)
        direct = reload(build.build_master(wght, slnt, shdw))
        worst, who, dists = 0.0, None, []
        for n in direct.getGlyphOrder():
            a, b = contours(inst, n), contours(direct, n)
            if [len(c) for c in a] != [len(c) for c in b]:
                fail(f"{loc} {n}: VF instance and direct build have different contours")
                continue
            for ca, cb in zip(a, b):
                d = contour_dist(ca, cb)
                dists.append(d)
                if d > worst:
                    worst, who = d, n
        dists.sort()
        p99 = dists[int(0.99 * (len(dists) - 1))] if dists else 0
        print(f"instance {loc}: max contour distance {worst:.1f} at {who}, p99 {p99:.1f}, limit {tol}")
        if worst > tol:
            fail(f"instance {loc}: {who} is {worst:.1f} units from a direct build (limit {tol})")


def check_colr(vf):
    colr = vf["COLR"].table
    v1 = {r.BaseGlyph for r in colr.BaseGlyphList.BaseGlyphPaintRecord}
    clips = set(colr.ClipList.clips) if colr.ClipList else set()
    v0 = {r.BaseGlyph for r in colr.BaseGlyphRecordArray.BaseGlyphRecord} if colr.BaseGlyphRecordArray else set()
    glyf = vf["glyf"]
    mapped = set(vf.getBestCmap().values())
    for n in sorted(mapped):
        if n.endswith(".shadow") or ".mark" in n:
            fail(f"cmap maps to {n}")
        if glyf[n].numberOfContours == 0:
            continue
        for label, have in [("COLRv1 paint", v1), ("clip box", clips), ("COLRv0 record", v0)]:
            if n not in have:
                fail(f"{n}: no {label}")
    print(f"COLR: {len(mapped)} mapped glyphs, {len(v1)} v1 paints, {len(clips)} clip boxes, {len(v0)} v0 records")


def check_ascender(vf):
    asc = vf["hhea"].ascent
    over = {}
    for wght in build.WEIGHTS:
        inst = instantiateVariableFont(vf, {"wght": wght, "slnt": 0, "SHDW": 0}, inplace=False)
        glyf = inst["glyf"]
        for n in set(inst.getBestCmap().values()):
            g = glyf[n]
            g.recalcBounds(glyf)
            if g.numberOfContours and g.yMax > asc:
                over[n] = max(over.get(n, 0), g.yMax)
    if over:
        top = ", ".join(f"{n} {y}" for n, y in sorted(over.items(), key=lambda kv: -kv[1]))
        print(f"WARN face yMax above hhea ascender {asc} ({len(over)} glyphs): {top}")
    else:
        print(f"face yMax <= hhea ascender {asc} for every mapped glyph")


def main():
    vf = TTFont(VF)
    check_colr(vf)
    check_ascender(vf)
    check_instances(vf)
    if failures:
        raise SystemExit(f"{len(failures)} failure(s)")
    print("ok")


if __name__ == "__main__":
    main()
