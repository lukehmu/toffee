# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Toffee is a COLRv1 variable display font (axes `wght` 300–900, `slnt` −12–0, `SHDW` 0–1000), generated entirely from
code with fontTools. There are no font sources (UFO or Glyphs files): `glyphs.py` is the design. Licensed under OFL 1.1.
Demo: https://lukehmu.github.io/toffee/ (GitHub Pages serves `index.html` from `main`).

## Commands

    uv run build.py          # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}  (~30 s; masters go to build/, ignored)
    uv run tests/check_kern.py   # after a build: kerned pairs keep faces >= border + 4 apart at wght 300/600/900

Deps are locked in `build.py.lock`. Builds are byte-reproducible (`RELEASE_EPOCH` → `SOURCE_DATE_EPOCH`), so a rebuild
with no source change leaves `fonts/` untouched: a font diff means the source changed.

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
  ball terminals). Group-private helpers are prefixed `_lc_`, `_uc_`, `_fig_`, `_pn_`, `_gf_` and `_ac_` (accents).
  Dot radii (`idot`, `pdot` in `geo()`) are written so that radius = c0 + c1·a. A radius that's linear in `a`
  interpolates exactly between the two weight masters; a scale that's linear in `a` would make it quadratic.
- **Accented letters** call their base glyph's function and append mark strokes, then register in `BASE_OF`. The
  build gives them the base's placement (the base strokes get the base's horizontal scale; marks only move) and emits
  them as TrueType composites: base + `name.mark`, and `base.shadow` + `name.mark.shadow`. A composite whose first
  strokes don't equal its base's strokes is drawn as a plain glyph instead.
- **Combining marks and layout** (`features.py`): U+0300–030C, 0326–0328 are zero-width glyphs in `glyphs.py`
  (`COMBINING`; build.py's `zero_width()` hook zeroes their advance), drawn where the precomposed marks sit, with
  `.case` variants over the cap height. `ot_features()` emits, per master: `ccmp` (base + mark → the precomposed
  glyph, from Unicode's canonical decompositions; i/j → dotless before a mark above; a mark above after a capital
  or ascender → `.case`), `locl` for Romanian/Moldavian ş ţ → ș ț, and `mark` anchors at `mark_x()` (the same x the
  composites use), stacking above a mark a letter already carries. Its classes must not depend on the weight, or
  varLib can't merge GSUB. `set_code_pages()` sets an OS/2 code page bit only when the whole page is mapped.
- **`build.py`**: the pen is an ellipse (half-width `a`, half-height `b`, per weight in `WEIGHTS`). Every pair of
  consecutive samples becomes one convex hull of two ellipses, sampled at `K` = 24 fixed directions and written as an
  all-off-curve TrueType contour. A glyph is therefore many overlapping convex contours, never a boolean union
  (`OVERLAP_SIMPLE` is set). Slant is a shear applied inside the hull maths.
- **Shadow**: every glyph `x` has a `x.shadow` glyph, made of the same hulls with the pen grown by `p.border` (weight-scaled) and swept
  along `SHADOW_DIR × SHDW`. COLR paints `x.shadow` (palette index 0) under `x` (index 1). Non-COLR renderers show
  only `x`, the plain face. A down-right shadow over left-to-right text only works because each glyph's shadow is
  covered by the glyphs drawn after it. Sidebearings must stay ≥ `border/2`, or a glyph's border paints over its
  neighbour's face. For the same reason a baseline tail must end inside its own advance.
- **Masters**: wght × slnt × SHDW corners (8), built separately, then `varLib.build`. Then COLR/CPAL, STAT, name and
  OS/2 fixes are applied to the VF.
- **Spacing**: `place()` reads `SPACING` in `glyphs.py`, which gives each glyph a width class r (its advance as a
  ratio of n's) and a side type for each side: straight, round, diagonal, or a ("T", ratio) tail side measured
  only inside the x-height band. It solves a horizontal skeleton scale that hits the class; the pen is never
  scaled. Sidebearings (`pen_params`) open up as the weight drops, with a floor of `border/2 + 4`. Glyphs not in
  `SPACING` keep their drawn width. `FIXED_WIDTH` groups share one advance. The numbers come from
  `docs/consistency.md` (measured against 7 OFL fonts); change them there first.
- **Kerning** (`kern.py`): computed per master from the upright faces' row profiles, so values follow the weight.
  It closes open pairs towards the n–n/H–H reference gap. A paint-model floor (face gap ≥ border + `MARGIN`, with
  `V_SLACK` extra vertical tolerance because shapes move vertically between weights) overrides it. The pair list
  depends only on glyph names (accented letters included through `BASE_OF`), so every master emits the same pairs
  and varLib can merge GPOS.

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
