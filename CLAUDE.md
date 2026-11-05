# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Toffee is a COLRv1 variable display font (axes `wght` 300–900, `slnt` −12–0, `SHDW` 0–1000), generated entirely from
code with fontTools. There are no font sources (UFO or Glyphs files): `glyphs.py` is the design. Licensed under OFL 1.1.
Demo: https://lukehmu.github.io/toffee/ (GitHub Pages serves `index.html` from `main`).

## Commands

    uv run build.py          # -> fonts/Toffee[SHDW,slnt,wght].{ttf,woff2}  (~20 s; masters go to build/, ignored)
    uv run tests/check_kern.py   # after a build: kerned pairs keep faces >= border + 4 apart at wght 300/600/900
    uv run tests/check_font.py   # after a build: in-between VF instances vs direct builds, COLR coverage, ascender

`check_font.py` builds masters at in-between locations with `build_master()` (any wght/slnt/SHDW builds) and measures
how far the VF instance is from them. Slant is exact; weight is off by up to ~37 units where a hull's tangent edge
turns past a sample direction between the weight masters (ampersand.shadow at 600). It also reports, without failing,
faces taller than the hhea ascender (Å, Ů at 936). CI (`.github/workflows/build.yml`) builds, checks that the
committed `fonts/` match the source, and runs both checks, OTS and fontbakery.

Deps are locked in `build.py.lock`. Builds are byte-reproducible (`RELEASE_EPOCH` → `SOURCE_DATE_EPOCH`), so a rebuild
with no source change leaves `fonts/` untouched: a font diff means the source changed.

Render checks (do both after a glyph change; Chrome is the main target, blackrenderer is a second COLRv1 implementation):

    agent-browser --session toffee --args "--no-sandbox" open "file://$PWD/index.html"   # --no-sandbox: this box's Chrome needs it
    agent-browser --session toffee set viewport 1600 2000; agent-browser --session toffee screenshot preview/x.png --full
    uv run --python 3.13 --with blackrenderer blackrenderer "fonts/Toffee[SHDW,slnt,wght].ttf" "Best year yet" \
        preview/br.svg --font-size 120 --variations wght=900,slnt=-10,SHDW=600 --backend svg   # skia backend lacks libEGL here

QA (Python 3.13: fontbakery's deps have no 3.15 wheels):

    uv run --python 3.13 --with fontbakery==1.1.0 fontbakery check-universal --succinct -l WARN --json preview/fb.json \
        "fonts/Toffee[SHDW,slnt,wght].ttf"; uv run tests/fontbakery_gate.py preview/fb.json
    uv run --python 3.13 --with opentype-sanitizer==9.2.0 python -m ots "fonts/Toffee[SHDW,slnt,wght].woff2"

Expected results: one FAIL, `win_ascent_and_descent [descent]`, allowlisted in `tests/fontbakery_gate.py`. It's
deliberate: `usWinDescent` covers the longest shadow so Windows doesn't clip it. WARNs: `interpolation_issues`
("contour order differs", "start point differs") are false positives: point k of every contour is the support point
in the same direction k in every master, and the heuristic matches near-identical convex contours by shape.
`overlapping_path_segments` comes from the overlapping hulls, `missing-avar` is accepted. `proof.html` is a static proof sheet, and `preview/` is ignored scratch space for screenshots.

## How the outlines are made (read both files before changing either)

- **`glyphs.py`**: each glyph function takes `g = geo(p)` (pen size and metrics for one master) and returns strokes.
  A stroke is a list of samples `(x, y, pen_scale, roundness)` built with `LN`, `ARC`, `DOT` and `S`. The glyph's x
  origin is arbitrary, because spacing is computed later. `roundness` 1 turns the elliptical pen into a circle (dots and
  ball terminals). Group-private helpers are prefixed `_lc_`, `_uc_`, `_fig_`, `_pn_`, `_gf_` and `_ac_` (accents).
  Dot radii (`idot`, `pdot` in `geo()`) are written so that radius = c0 + c1·a. A radius that's linear in `a`
  interpolates exactly between the two weight masters; a scale that's linear in `a` would make it quadratic.
- **Accented letters** call their base glyph's function and append mark strokes, then register in `BASE_OF`. The
  build gives them the base's placement (the base strokes get the base's horizontal scale; marks only move) and emits
  them as TrueType composites: base + a mark glyph, and `base.shadow` + the mark's `.shadow`. Marks with the same
  shape at both weights (`MARK_TOL`) share one glyph, drawn around (0, 0) and named after the first letter that uses
  it (`aacute.mark` also serves `eacute`); the composite's offset places it, and gvar varies the offset. A composite
  whose first strokes don't equal its base's strokes is drawn as a plain glyph instead.
- **`build.py`**: the pen is an ellipse (half-width `a`, half-height `b`, per weight in `WEIGHTS`). Every pair of
  consecutive samples becomes one convex hull of two ellipses, sampled at `K` = 24 fixed directions and written as an
  all-off-curve TrueType contour. A glyph is therefore many overlapping convex contours, never a boolean union
  (`OVERLAP_SIMPLE` is set). Hulls are built upright and then sheared, so every slant master is the same hull sheared
  and in-between slants interpolate exactly. A sample equal to the previous one at every weight (where `S()` joins
  parts) is dropped (`skeleton()`), since its zero-length segment adds a contour and nothing else.
- **Shadow**: every glyph `x` has a `x.shadow` glyph, made of the same hulls with the pen grown by `p.border` (weight-scaled) and swept
  along `SHADOW_DIR × SHDW`. A shadow contour has K + 2 points (`SWEEP`): the directions at its two long edges take
  both the glyph's and the copy's point, so the long edges stay exact at in-between slants (SHDW 0 masters too, where
  the two coincide). COLR paints `x.shadow` (palette index 0) under `x` (index 1), as a COLRv1 paint and as the same
  two layers in COLRv0 records (Safari and older Windows have no v1). Non-COLR renderers show only `x`, the plain face. A down-right shadow over left-to-right text only works because each glyph's shadow is
  covered by the glyphs drawn after it. Sidebearings must stay ≥ `border/2`, or a glyph's border paints over its
  neighbour's face. For the same reason a baseline tail must end inside its own advance.
- **Masters**: wght × slnt × SHDW corners (8), built separately, then `varLib.build`. Then COLR/CPAL, STAT, name and
  OS/2 fixes are applied to the VF. Placement and kerning depend only on the weight (`layout()`, `kern_fea()`, cached).
  Per master, `post` underline follows the pen and `hhea` caret slope the slant; varLib turns both into MVAR.
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
- To change the colours a user sees, edit `PALETTES` (and its `PALETTE_NAMES` labels) in `build.py` (CPAL). The page's
  presets in `index.html` mirror them.
