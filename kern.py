"""Kerning generated from the outlines. build.py calls kern_feature() once per master.

Method (measured on the upright faces at their final x, per master, so values follow the weight):
- Each face becomes a horizontal profile: for every row y (step STEP), the leftmost and rightmost ink.
- Reference gap: the mean gap of n-n and H-H (the font's own straight-sidebearing rhythm).
- Optical gap of a pair: the mean of the per-row gaps over the rows where both glyphs have ink, each gap
  capped at CAP * reference, so a deep open space (T o) counts as a bounded gap.
- Kern = -(optical - reference) * STRENGTH when that is below -MIN_KERN. Only closes pairs.
- Paint-model floor: the right glyph's border is painted over the left glyph's face, so wherever the two have
  ink within +-border of each other vertically, the face-to-face gap stays >= border + MARGIN. The floor wins
  over the optical value and can open a pair (a positive kern).
- The pair list depends on glyph names only, so every master emits the same pairs (zero where nothing is needed).
"""

import math

STEP = 10
Y_LO, Y_HI = -200, 1100
CAP = 1.6  # per-row gap cap, in reference gaps
STRENGTH = 0.85
MIN_KERN = 10
MARGIN = 16  # face gap above the border that must remain
V_SLACK = 60  # extra vertical tolerance for the paint-model floor
MIN_ROWS = 4  # overlap rows needed before the optical measure is trusted

# Left-hand glyphs whose right side has an awkward shape, and right-hand glyphs whose left side does.
LEFT = (
    "T V W Y A L P F K X R r v w y f k x one seven period comma colon semicolon "
    "quotesingle quotedbl quoteright quoteleft quotedblright quotedblleft ellipsis"
).split()
RIGHT = "T V W Y A X quotesingle quotedbl quoteright quoteleft quotedblright quotedblleft".split()
# Neighbours: letters, figures and the common punctuation.
OTHERS = (
    "a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z "
    "zero one two three four five six seven eight nine period comma colon semicolon exclam question "
    "quotesingle quotedbl quoteright quoteleft quotedblright quotedblleft hyphen endash emdash "
    "parenleft parenright ellipsis"
).split()


def _with_composites(base_names, have):
    """The names plus every accented glyph built on one of them (BASE_OF), in a stable order."""
    from glyphs import BASE_OF

    out = [n for n in base_names if n in have]
    out += [c for c, b in BASE_OF.items() if b in base_names and c in have]
    return out


def pair_list(names):
    """Deterministic (left, right) pairs from glyph names alone."""
    have = set(names)
    others = _with_composites(OTHERS, have)
    lefts, rights = _with_composites(LEFT, have), _with_composites(RIGHT, have)
    pairs, seen = [], set()
    for left in lefts:
        for right in others:
            if (left, right) not in seen:
                seen.add((left, right))
                pairs.append((left, right))
    for right in rights:
        for left in others:
            if (left, right) not in seen:
                seen.add((left, right))
                pairs.append((left, right))
    return pairs


def profile(contours):
    """{row index: (xmin, xmax)} of the ink of a glyph made of polygons."""
    rows = {}
    for c in contours:
        n = len(c)
        ys = [pt[1] for pt in c]
        i0 = max(math.ceil(min(ys) / STEP), Y_LO // STEP)
        i1 = min(math.floor(max(ys) / STEP), Y_HI // STEP)
        for i in range(i0, i1 + 1):
            y = i * STEP
            lo = hi = None
            for k in range(n):
                x0, y0 = c[k]
                x1, y1 = c[(k + 1) % n]
                if not (y0 <= y <= y1 or y1 <= y <= y0):
                    continue
                xs = (x0, x1) if y0 == y1 else (x0 + (x1 - x0) * (y - y0) / (y1 - y0),)
                for x in xs:
                    lo = x if lo is None or x < lo else lo
                    hi = x if hi is None or x > hi else hi
            if lo is not None:
                old = rows.get(i)
                rows[i] = (lo, hi) if old is None else (min(old[0], lo), max(old[1], hi))
    return rows


class Faces:
    """Row profiles of every glyph, plus the dilated left edge the paint-model floor needs."""

    def __init__(self, faces, advances, border, v_slack=V_SLACK):
        self.adv = advances
        self.prof = {n: profile(c) for n, c in faces.items()}
        # Vertical tolerance: the border, plus slack for shapes that move vertically between weights,
        # so a pair that comes close at an interpolated weight is already caught at both masters.
        w = int((border + v_slack) // STEP)
        self.dil = {}
        for n, pr in self.prof.items():
            d = {}
            if pr:
                for i in range(min(pr) - w, max(pr) + w + 1):
                    vals = [pr[j][0] for j in range(i - w, i + w + 1) if j in pr]
                    if vals:
                        d[i] = min(vals)
            self.dil[n] = d

    def gaps(self, left, right):
        """[(row, gap)] for rows where both have ink: left's right edge to right's left edge."""
        pl, pr, adv = self.prof[left], self.prof[right], self.adv[left]
        return [(i, adv + pr[i][0] - pl[i][1]) for i in pl if i in pr]

    def face_gap(self, left, right):
        """Smallest face-to-face gap between ink within +-border of each other vertically."""
        pl, dr, adv = self.prof[left], self.dil[right], self.adv[left]
        vals = [adv + dr[i] - pl[i][1] for i in pl if i in dr]
        return min(vals) if vals else None


def reference(fc):
    means = []
    for n in ("n", "H"):
        g = [v for _, v in fc.gaps(n, n)]
        means.append(sum(g) / len(g))
    return sum(means) / len(means)


def kern_values(faces, advances, p):
    """{(left, right): int value} for every pair in pair_list."""
    fc = Faces(faces, advances, p.border)
    ref = reference(fc)
    out = {}
    for left, right in pair_list(faces):
        g = fc.gaps(left, right)
        k = 0
        if len(g) >= MIN_ROWS:
            eff = sum(min(v, CAP * ref) for _, v in g) / len(g)
            k = round(min(-(eff - ref) * STRENGTH, 0))
            if abs(k) < MIN_KERN:
                k = 0
        floor = fc.face_gap(left, right)
        if floor is not None:
            k = max(k, math.ceil(p.border + MARGIN - floor))
        out[(left, right)] = k
    return out


def kern_feature(faces, advances, p, g):
    """Return OpenType feature code (feaLib syntax) for this master, or "" for none.

    faces: {glyph: [contour, ...]}, each contour a list of (x, y) hull points, upright, at the glyph's final x.
    advances: {glyph: advance width}. p: pen params (a, b, border, sb, min_sb). g: geo() metrics.
    Every master must emit the same pairs (a zero value is fine) so varLib can merge GPOS.
    """
    vals = kern_values(faces, advances, p)
    if not vals:
        return ""
    lines = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "", "feature kern {"]
    lines += [f"    pos {left} {right} {v};" for (left, right), v in vals.items()]
    lines.append("} kern;")
    return "\n".join(lines) + "\n"
