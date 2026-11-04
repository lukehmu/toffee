# Toffee

A heavy, rounded display face built as a COLRv1 variable font. The style is taken from a "Best year yet" door sign; the glyphs are original.

**Demo:** https://lukehmu.github.io/toffee/ lets you type in it and set every axis and colour.

Axes:
- `wght` 300–900
- `slnt` −12–0
- `SHDW` 0–1000: long-shadow length; 0 = outline only

CPAL palettes: 0 toffee (chocolate shadow, cream face), 1 orange/white, 2 black/yellow, 3 pink/ink.

**Browser support.** The outline and shadow are COLRv1 colour layers. Chrome and Edge 98+ and Firefox 107+ draw
them. Safari and iOS don't support COLRv1 yet, so there, like any other non-COLR renderer, you get the plain
monochrome face. To feature-detect: `CSS.supports("font-tech(color-COLRv1)")`.

**Character set.** Basic Latin (A–Z, a–z, 0–9, ASCII punctuation), curly quotes, dashes, ellipsis, bullet, £ and €.

In CSS:

```css
@font-face { font-family: Toffee; src: url("Toffee[SHDW,slnt,wght].woff2") format("woff2"); font-weight: 300 900; }
@font-palette-values --mine { font-family: Toffee; override-colors: 0 #3c1c20, 1 #f3ecd1; } /* 0 shadow, 1 face */
h1 { font-family: Toffee; font-variation-settings: "wght" 900, "slnt" -10, "SHDW" 600; font-palette: --mine; }
```

Tips:
- Each glyph's shadow is painted under the glyphs that come after it, so it works for left-to-right text with
  shadows falling down-right.
- Keep `line-height` around 1 or more at heavy weights. Tighter, and the next line's outline covers descenders.
- Don't use strongly negative `letter-spacing`. Neighbours' outlines would paint over each other's faces.

## Building

    uv run build.py          # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}; deps pinned in build.py.lock
    open index.html          # the demo page; proof.html = proof sheet

Builds are reproducible: font timestamps come from `RELEASE_EPOCH` in `build.py` (via `SOURCE_DATE_EPOCH`).

Glyphs are stroke skeletons in `glyphs.py`. `build.py` traces each stroke with an elliptical pen as a chain of
convex hulls; the shadow is the same hulls swept along the shadow vector. Every master therefore has the same
points, and there are no boolean operations. Widths and spacing follow measured reference fonts: see
[`docs/consistency.md`](docs/consistency.md). `CLAUDE.md` has the details for contributors.

## Licence

SIL Open Font License 1.1: see `OFL.txt`.
