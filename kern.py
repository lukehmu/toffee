"""Kerning generated from the outlines. build.py calls kern_feature() once per master."""


def kern_feature(faces, advances, p, g):
    """Return OpenType feature code (feaLib syntax) for this master, or "" for none.

    faces: {glyph: [contour, ...]}, each contour a list of (x, y) hull points, upright, at the glyph's final x.
    advances: {glyph: advance width}. p: pen params (a, b, border, sb, min_sb). g: geo() metrics.
    Every master must emit the same pairs (a zero value is fine) so varLib can merge GPOS.
    """
    return ""
