"""OpenType layout besides kerning, and the OS/2 code page bits. build.py calls these per master / on the VF.

- ccmp: base + combining mark -> the precomposed glyph (from Unicode's canonical decompositions, plus the
  Latvian comma letters typed with U+0326); i/j before a mark above -> dotless; a mark above after a capital
  or an ascender -> its .case variant.
- locl: Romanian and Moldavian ş ţ -> ș ț (comma below).
- mark: anchors for every letter, so combinations with no precomposed glyph still land in place.
- Code pages: a bit is set only when every character of that code page is in the cmap (the soft hyphen
  excepted: it is a format control that renderers handle without a glyph, and fontbakery warns if mapped).

Every master emits the same lookups with different anchor values, so varLib can merge GSUB/GPOS.
"""

import unicodedata
from types import SimpleNamespace

from glyphs import BASE_OF, COMBINING, GLYPHS, accent_top, geo, mark_x

ROMANIAN = {"Scedilla": "Scommaaccent", "scedilla": "scommaaccent", "Tcedilla": "uni021A", "tcedilla": "uni021B"}
# OS/2 ulCodePageRange bit -> Python codec, for the single-byte Windows code pages.
CODE_PAGES = {0: "cp1252", 1: "cp1250", 2: "cp1251", 3: "cp1253", 4: "cp1254", 5: "cp1255", 6: "cp1256",
              7: "cp1257", 8: "cp1258", 16: "cp874", 29: "mac_roman"}


def zero_width(placed):
    """Combining marks: no advance, ink left where it was drawn (centred on x = 0)."""
    for name in COMBINING:
        st, _, _, *rest = placed[name]
        placed[name] = (st, 0.0, 0, *rest)


def _cmap():
    return {uni: name for name, (uni, _) in GLYPHS.items() if uni is not None}


def compositions():
    """[(base, mark, precomposed)] for every precomposed glyph whose parts are both in the font."""
    cmap = _cmap()
    out = []
    for name, (uni, _) in GLYPHS.items():
        if uni is None:
            continue
        d = unicodedata.decomposition(chr(uni)).split()
        if len(d) != 2 or d[0].startswith("<"):
            continue
        base, mark = (int(c, 16) for c in d)
        if base in cmap and mark in cmap:
            out.append((cmap[base], cmap[mark], name))
            if mark == 0x0327 and "commaaccent" in name:  # Ķ ļ ņ ...: drawn with a comma, often typed so
                out.append((cmap[base], "uni0326", name))
    return out


def _mark_kind(name):
    """'top' / 'bottom' / 'ogonek' for the mark a precomposed glyph already carries, else None."""
    uni = GLYPHS[name][0]
    d = unicodedata.decomposition(chr(uni)).split() if uni is not None else []
    if len(d) != 2 or d[0].startswith("<"):
        return None
    mark = int(d[1], 16)
    return {0x0326: "bottom", 0x0327: "bottom", 0x0328: "ogonek"}.get(mark, "top")


def _letters():
    """Encoded letters (and the dotless forms) that can carry a mark, with their case."""
    out = {}
    for name, (uni, _) in GLYPHS.items():
        if name in ("dotlessi", "uni0237"):
            out[name] = "Ll"
        elif uni is not None and unicodedata.category(chr(uni)) in ("Lu", "Ll"):
            out[name] = unicodedata.category(chr(uni))
    return out


def _tall(name):
    """A lowercase letter reaching the ascender (b d h k l ...): marks above use the capital variants.

    Decided on one reference pen, so every master puts the same glyphs in the class."""
    g = geo(SimpleNamespace(a=74, b=53))
    strokes = GLYPHS[name][1](g)
    if name in BASE_OF and strokes[: len(GLYPHS[BASE_OF[name]][1](g))] == GLYPHS[BASE_OF[name]][1](g):
        strokes = GLYPHS[BASE_OF[name]][1](g)
    return max(y for st in strokes for _, y, *_ in st) > g.X + 150


def ot_features(placed, g, t, y0):
    """Feature code (feaLib) for one master: languagesystems, ccmp, locl, mark. Put it before kern."""
    letters = _letters()
    tops = [n for n, k in COMBINING.items() if k == "top"]
    case_base = sorted(
        n for n, c in letters.items()
        if c == "Lu" or (_mark_kind(n) != "top" and n not in ("i", "j") and _tall(n))
    )
    lines = [
        "languagesystem DFLT dflt;",
        "languagesystem latn dflt;",
        "languagesystem latn ROM;",
        "languagesystem latn MOL;",
        f"@CMB_TOP = [{' '.join(tops)}];",
        f"@CMB_TOP_CASE = [{' '.join(n + '.case' for n in tops)}];",
        f"@CASE_BASE = [{' '.join(case_base)}];",
        "lookup ccmp_compose {",
        *(f"    sub {b} {m} by {c};" for b, m, c in compositions()),
        "} ccmp_compose;",
        "lookup ccmp_dotless {",
        "    sub i' @CMB_TOP by dotlessi;",
        "    sub j' @CMB_TOP by uni0237;",
        "} ccmp_dotless;",
        "lookup ccmp_case {",
        "    sub @CASE_BASE @CMB_TOP' by @CMB_TOP_CASE;",
        "} ccmp_case;",
        "feature ccmp {",
        "    lookup ccmp_compose;",
        "    lookup ccmp_dotless;",
        "    lookup ccmp_case;",
        "} ccmp;",
        "lookup locl_rom {",
        *(f"    sub {a} by {b};" for a, b in ROMANIAN.items()),
        "} locl_rom;",
        "feature locl {",
        "    script latn;",
        "    language ROM exclude_dflt;",
        "    lookup locl_rom;",
        "    language MOL exclude_dflt;",
        "    lookup locl_rom;",
        "} locl;",
    ]

    def anchor(x, y):
        return f"<anchor {round(x + t * (y - y0))} {round(y)}>"

    for name, kind in COMBINING.items():
        y = {"top": g.X, "top.case": g.C}.get(kind, 0)
        cls = {"top.case": "top"}.get(kind, kind)
        lines.append(f"markClass {name} {anchor(0, y)} @M_{cls.upper()};")

    lines.append("feature mark {")
    for name, case in letters.items():
        st, dx, _, k, sk0 = placed[name]
        base, carried = name, None
        if name in BASE_OF and placed.get(BASE_OF[name], (None,))[1:] == placed[name][1:]:
            base, carried = BASE_OF[name], _mark_kind(name)  # a composite: its base's anchors
        elif _mark_kind(name) is not None:
            carried = _mark_kind(name)

        def fx(kind):
            return sk0 + (mark_x(base, kind, g) - sk0) * k + dx

        parts = []
        if name not in ("i", "j"):
            if carried == "top":  # stack above the mark it carries (Lithuanian ė́ ū̃)
                ytop = accent_top(g, case == "Lu")
            elif case == "Lu":
                ytop = g.C
            elif name in case_base:
                ytop = g.C + 25 - 0.2 * g.a  # the capital marks, kept under the line ascender
            else:
                ytop = g.X
            parts.append(f"{anchor(fx('top'), ytop)} mark @M_TOP")
        if carried not in ("bottom", "ogonek"):
            strokes = GLYPHS[base][1](g)
            ybot = g.D if min(y for s in strokes for _, y, *_ in s) < -100 else 0
            parts.append(f"{anchor(fx('bottom'), ybot)} mark @M_BOTTOM")
            parts.append(f"{anchor(fx('ogonek'), ybot)} mark @M_OGONEK")
        if parts:
            lines.append(f"    pos base {name} " + " ".join(parts) + ";")
    lines.append("} mark;")
    return "\n".join(lines) + "\n"


def set_code_pages(font):
    """OS/2 ulCodePageRange: claim a code page only when all of its characters are mapped."""
    cmap = font.getBestCmap()
    bits = 0
    for bit, codec in CODE_PAGES.items():
        chars = []
        for byte in range(0x20, 0x100):
            try:
                c = bytes([byte]).decode(codec)
            except UnicodeDecodeError:
                continue
            if c.isprintable() or c == "\xa0":  # not the soft hyphen, a format control (fontbakery)
                chars.append(ord(c))
        if all(c in cmap for c in chars):
            bits |= 1 << bit
    os2 = font["OS/2"]
    os2.ulCodePageRange1, os2.ulCodePageRange2 = bits & 0xFFFFFFFF, bits >> 32
