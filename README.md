# Toffee

A heavy, rounded display face built as a COLRv1 variable font. The style is taken from a "Best year yet" door sign; the glyphs are original.

Axes:
- `wght` 300–900
- `slnt` −12–0
- `SHDW` 0–1000: long-shadow length; 0 = outline only

CPAL palettes: 0 toffee (chocolate shadow, cream face), 1 orange/white, 2 black/yellow, 3 pink/ink.
Without COLR support you get a plain monochrome face.

    uv run build.py          # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}
    open specimen.html       # sliders + glyph grid; proof.html = proof sheet

Glyphs are stroke skeletons in `glyphs.py`. `build.py` traces each stroke with an elliptical pen as a chain of convex hulls; the shadow is the same hulls swept along the shadow vector. Every master therefore has the same points, and there are no boolean operations.
