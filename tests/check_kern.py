# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools[woff]>=4.55"]
# ///
"""Paint-model check on the built VF: after kerning, the face gap of every kerned pair stays >= border + 4.

Run: uv run tests/check_kern.py   (after uv run build.py)
"""

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib.instancer import instantiateVariableFont  # noqa: E402

import kern  # noqa: E402

VF = ROOT / "fonts" / "Toffee[SHDW,slnt,wght].ttf"
MIN_EXTRA = 4  # units above the border; kern.py aims for MARGIN (8)


def pairs_of(font):
    out = {}
    for lk in font["GPOS"].table.LookupList.Lookup:
        for st in lk.SubTable:
            if st.LookupType == 9:
                st = st.ExtSubTable
            if st.Format != 1:
                raise SystemExit("unexpected PairPos format")
            for left, ps in zip(st.Coverage.glyphs, st.PairSet):
                for rec in ps.PairValueRecord:
                    out[(left, rec.SecondGlyph)] = rec.Value1.XAdvance if rec.Value1 else 0
    return out


def measure(wght):
    f = instantiateVariableFont(TTFont(VF), {"wght": wght, "slnt": 0, "SHDW": 0}, inplace=False)
    glyf = f["glyf"]
    faces, adv = {}, {}
    for n in f.getGlyphOrder():
        if n.endswith(".shadow") or n in (".notdef", "space"):
            continue
        g = glyf[n]
        cs = []
        if g.numberOfContours > 0:
            coords, ends, _ = g.getCoordinates(glyf)
            s = 0
            for e in ends:
                cs.append(list(coords[s : e + 1]))
                s = e + 1
        faces[n], adv[n] = cs, f["hmtx"][n][0]
    a = 36 + (wght - 300) * (112 - 36) / 600
    border = 24 + 0.21 * a
    fc = kern.Faces(faces, adv, border, v_slack=0)  # the true paint-model rule, no kerning slack
    ps = pairs_of(f)
    worst = (1e9, None)
    nz = 0
    for (left, right), k in ps.items():
        nz += k != 0
        gap = fc.face_gap(left, right)
        if gap is None:
            continue
        slack = gap + k - border
        if slack < worst[0]:
            worst = (slack, (left, right, k))
    return ps, worst, nz


def main():
    allp = {}
    for w in (300, 600, 900):
        ps, (slack, who), nz = measure(w)
        allp[w] = ps
        print(f"wght {w}: {len(ps)} pairs, {nz} nonzero, min face gap - border = {slack:.1f} at {who}")
        assert slack >= MIN_EXTRA, f"wght {w}: face gap {slack:.1f} < {MIN_EXTRA} at {who}"
    assert allp[300] != allp[900], "kerning does not vary with weight"
    for pair in [("A", "V"), ("T", "o"), ("L", "T"), ("r", "period")]:
        print(pair, {w: allp[w].get(pair) for w in allp})
    print("ok")


if __name__ == "__main__":
    main()
