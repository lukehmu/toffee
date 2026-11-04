# Toffee

A heavy, rounded display face built as a COLRv1 variable font. The style is taken from a "Best year yet" door sign; the glyphs are original.

**Demo:** https://lukehmu.github.io/toffee/ lets you type in it and set every axis and colour.

Axes:
- `wght` 300–900
- `slnt` −12–0
- `SHDW` 0–1000: long-shadow length; 0 = outline only

CPAL palettes: 0 toffee (chocolate shadow, cream face), 1 orange/white, 2 black/yellow, 3 pink/ink.
Without COLR support you get a plain monochrome face.

In CSS:

```css
@font-face { font-family: Toffee; src: url("Toffee[SHDW,slnt,wght].woff2") format("woff2"); font-weight: 300 900; }
@font-palette-values --mine { font-family: Toffee; override-colors: 0 #3c1c20, 1 #f3ecd1; } /* 0 shadow, 1 face */
h1 { font-family: Toffee; font-variation-settings: "wght" 900, "slnt" -10, "SHDW" 600; font-palette: --mine; }
```

    uv run build.py          # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}
    open index.html          # the demo page; proof.html = proof sheet

Glyphs are stroke skeletons in `glyphs.py`. `build.py` traces each stroke with an elliptical pen as a chain of convex hulls; the shadow is the same hulls swept along the shadow vector. Every master therefore has the same points, and there are no boolean operations.

## Licence

SIL Open Font License 1.1: see `OFL.txt`.
