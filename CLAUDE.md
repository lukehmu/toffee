# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Toffee is a COLRv1 variable display font (axes `wght` 300–900, `slnt` −12–0, `SHDW` 0–1000), generated entirely from
code with fontTools. There are no font sources (UFO or Glyphs files): `glyphs.py` is the design. Licensed under OFL 1.1.
Demo: https://lukehmu.github.io/toffee/ (GitHub Pages serves `index.html` from `main`).

## Commands

    uv run build.py        # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}  (~10 s; masters go to build/, ignored)

Render checks (do both after a glyph change; Chrome is the main target, blackrenderer is a second COLRv1 implementation):

    agent-browser --session toffee --args "--no-sandbox" open "file://$PWD/index.html"   # --no-sandbox: this box's Chrome needs it
    agent-browser --session toffee set viewport 1600 2000; agent-browser --session toffee screenshot preview/x.png --full
    uv run --python 3.13 --with blackrenderer blackrenderer "fonts/Toffee[SHDW,slnt,wght].ttf" "Best year yet" \
        preview/br.svg --font-size 120 --variations wght=900,slnt=-10,SHDW=600 --backend svg   # skia backend lacks libEGL here

QA (Python 3.13: fontbakery's deps have no 3.15 wheels):

    uv run --python 3.13 --with fontbakery fontbakery check-universal --succinct -l WARN "fonts/Toffee[SHDW,slnt,wght].ttf"

Expected results: one FAIL, `win_ascent_and_descent [descent]`. It's deliberate: `usWinDescent` covers the longest
shadow so Windows doesn't clip it. `interpolation_issues` "start point differs" warnings are false positives
(see the hulls below). `proof.html` is a static proof sheet, and `preview/` is ignored scratch space for screenshots.

## How the outlines are made (read both files before changing either)

- **`glyphs.py`**: each glyph function takes `g = geo(p)` (pen size and metrics for one master) and returns strokes.
  A stroke is a list of samples `(x, y, pen_scale, roundness)` built with `LN`, `ARC`, `DOT` and `S`. The glyph's x
  origin is arbitrary, because spacing is computed later. `roundness` 1 turns the elliptical pen into a circle (dots and
  ball terminals). Group-private helpers are prefixed `_lc_`, `_uc_`, `_fig_` and `_pn_`.
- **`build.py`**: the pen is an ellipse (half-width `a`, half-height `b`, per weight in `WEIGHTS`). Every pair of
  consecutive samples becomes one convex hull of two ellipses, sampled at `K` = 24 fixed directions and written as an
  all-off-curve TrueType contour. A glyph is therefore many overlapping convex contours, never a boolean union
  (`OVERLAP_SIMPLE` is set). Slant is a shear applied inside the hull maths.
- **Shadow**: every glyph `x` has a `x.shadow` glyph, made of the same hulls with the pen grown by `BORDER` and swept
  along `SHADOW_DIR × SHDW`. COLR paints `x.shadow` (palette index 0) under `x` (index 1). Non-COLR renderers show
  only `x`, the plain face. A down-right shadow over left-to-right text only works because each glyph's shadow is
  covered by the glyphs drawn after it. Sidebearings must stay ≥ `BORDER/2`, or a glyph's border paints over its
  neighbour's face.
- **Masters**: wght × slnt × SHDW corners (8), built separately, then `varLib.build`. Then COLR/CPAL, STAT, name and
  OS/2 fixes are applied to the VF.
- **Spacing**: in `spacing()`, from the upright outline's bbox plus `SIDEBEARING`, minus `ROUND_ADJ` for glyphs in
  `ROUND_LEFT`/`ROUND_RIGHT`. `FIXED_WIDTH` groups share one advance. There is no kerning.

## The invariant that breaks builds

Every master must produce the same number of samples for each glyph, which keeps the points compatible. `ARC` derives
its sample count from its angles, so pass literal angles and never compute them from `g.a`, `g.b` or `g.wn`.
Positions, radii and scales may depend on weight; counts may not. Breaking this fails in `varLib.build` with an
incompatibility error.

## Conventions

- `fonts/` is committed on purpose (the release files that Pages links to). Rebuild and commit it together with any
  `glyphs.py` or `build.py` change.
- To change the colours a user sees, edit `PALETTES` in `build.py` (CPAL). The page's presets in `index.html` mirror
  them.
