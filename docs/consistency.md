# Consistency: Toffee against comparable fonts

Toffee was measured against seven OFL display fonts (Caprasimo, Shrikhand, Bagel Fat One, Titan One, Fredoka,
Baloo 2 and Grandstander). The full research report is kept below.

## Applied (2026-11-04)

- **Constant n skeleton** (`wn = 375`): lighter weights no longer condense. n advance is about `wn + 2a + 2·sb`.
- **Width classes**: `SPACING` in `glyphs.py` gives each letter and figure an advance as a ratio of n.
  `build.py` scales the skeleton, never the pen, to fit.
- **Sidebearings**: straight `sb = 99 − 0.6a`; round 0.7×, diagonal 0.35×, plus per-glyph values from the
  references. The floor is `border/2 + 4`, so a neighbour's outline never paints over a face, which is why
  the heavy weight sits flatter than the references.
- **Tail sides**: measured inside the x- or cap-height band. Baseline tails and f's hook must end inside the
  advance; descender hooks (g, j, y) may overhang.
- **Contrast**: b/a goes from 0.54 to 0.66 at 900 and from 0.72 to 0.89 at 300.
- **Metrics**: x-height 570; caps overshoot 14.
- **Dots**: i/j dots and punctuation follow `idot = 1.58 − 0.0046a` with gap `155 − a`. Terminal balls are
  a constant 1.0× the pen.
- **Border scales with weight**: `24 + 0.21a`.

Not applied: wn 360 (the photo's narrower 900; a judgment call), and kerning.

## Applied (2026-11-05): joins and counters at 900

- **Soft joins**: the concave corners where strokes meet are filleted (`fillet()` in `glyphs.py`, radius
  `10 + 0.35a`; smaller in acute crotches and in e's eye): a d g q (both counter corners), b p þ (bottom), e
  (eye, aperture and the beak under the bar), u y (crotch), t (right corners), f (right, under the bar), k K
  (upper crotch), the caps' stem/bar/bowl corners, A M N V W X Y Z v w x z, G's bar, and 1 2 4 7. Joins that
  are already soft (n h m arches, b p tops, u y counters) or whose fillet added under ~100 units² at both
  masters (5 6 8 9, the sides of x X, under A's bar, k's arm/leg, Y's stem) have none: each fillet costs
  about 0.6 KB of woff2. bowl_left ends at 320° and bowl_right at ±145°, so a/b/d/p close at 300.
- **Counters at 900**: e's bar thins to 0.55 and drops 11 units; s's terminals are shorter with smaller
  balls; B's waist is lower (0.52C) and thin; the figures' bowls use a pen scale of 0.88 at 900 (their width
  is fixed by the class, so a wider skeleton would just be scaled back), 0's class is 1.00 (heavy references
  1.00), 8's waist drops, 4 has a thinner diagonal and bar, 5's bowl starts inside its stem; % rings, @'s
  inner a and the Æ's A half grow with the pen; @ is taller.
- **Marks**: the double acute's strokes stay `border + 10` apart; the ogonek ends 25 above the descender;
  ď ť ľ Ľ's comma sits `border + 10` off the stem; cap marks end under 912 (ascender 930), with circumflex
  and caron as tall as the acute; f's ball and the asterisk stop at the ascender and cap height.
- **Space** is `0.4 × n advance` (241 at 300, 265 at 900; it was a fixed 232).
- **Comma and curly quotes**: the tail height is `150 + 0.25a` (it was `1.9r`), so the light ’ is nearly as
  tall as the straight quote and the 900 one is no longer twice the 300 one.
- **Weight axis**: caron, circumflex, acute and % keep one roundness and (for caron and %) one slope at
  both masters, so the hull's sides switch pens in the same directions and 600 stays straight (caron 9.2%
  → 2.0% off a directly built 600 master, % 7.6% → 1.5%). The acute keeps its old slope (a constant one
  turned it into a dot at 900 caps), so it is still 6.5% off. & is unchanged (6.0%).

---

# Toffee against comparable open fonts

Measured on 2026-11-04. Toffee is the **snapshot of commit `624a609`** (the build of 19:50, after the
`refine/lower` merge). Other sessions were changing the repo while this ran: the earlier build had an n
advance of 679 rather than 724. All numbers are in units of 1000 UPM, from monochrome face glyphs at SHDW 0
and slnt 0, instanced with `fontTools.varLib.instancer`.

The measurements came from nonzero-winding horizontal scanlines through flattened outlines. The scripts,
the raw data and the HTML page behind the screenshot were throwaway and are not in this repo. The
screenshot is [`compare.png`](compare.png), downscaled.

## 1. Reference picks

| font | why it's in | caveat |
|---|---|---|
| **Caprasimo** | Closest in spirit: a heavy, soft retro "fat face" (Cooper-like) with ball terminals | single weight; serif-ish softness |
| **Shrikhand** | Heavy, slanted retro display with ball terminals, like the photo's lean | italic (14°), so its sidebearings are skewed: left out of the spacing ratios |
| **Bagel Fat One** | Heavy, rounded, fat display, low x-height | reverse contrast on round letters (o top 192 > side 122): left out of the contrast reasoning |
| **Titan One** | Heavy rounded display with very tight counters, the "fattest" in the set | single weight |
| **Fredoka** (wdth, wght VF) | Rounded sans with a weight axis from 300 to 700: shows how width and spacing move with weight | monoline (contrast 1.0) |
| **Baloo 2** (wght VF) | Rounded, soft, with a weight axis from 400 to 800 | small caps-to-x ratio |
| **Grandstander** (wght VF) | Playful, rounded, with a weight axis from 100 to 900 | quirky: H narrower than n, o lower than the x-height, the same advances at every weight |

Rejected after rendering: **Corben Bold** (bracketed serifs, very wide, n/x 1.52), **Lilita One** (flat-sided
and condensed, no balls), **Chewy** (not in `ofl/`; Apache-licensed). All of them are still drawn in the
screenshot.

The photo was measured as well (cream-pixel scanlines on the full-resolution JPG). In
pixels: cap B 403, x-height ≈317, e's vertical side 113, e's top/bottom strokes 95/99, e's crossbar 47,
e's ink width 284, B's ink width 319, B's stem 119, B's counter 73, slant ≈11°, gaps between letters 18–54.
As ratios, the photo has:

| x/cap | n-ish stem / x | contrast (e top / side) | e bar / stem | e ink width / x | B width / cap | B counter / stem | slant |
|---|---|---|---|---|---|---|---|
| **0.78** | **0.36** | **0.84–0.88** | **0.42** | **0.90** | **0.79** | **0.61** | **≈11°** |

## 2. Measurement tables

Medians are over the reference fonts only. Toffee is the last column of every table. "SB" means
sidebearing, taken from outline bounds. Scanlines run at x/2 for n and l, at cap/4 for the H stems, and
through the bbox centre for o and O. Horizontal strokes are measured with a vertical scanline through the
counter's centre.


### Heaviest weights

#### Vertical metrics

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| x-height | 500 | 529 | 527 | 580 | 508 | 493 | 584 | 527 | 538 |
| cap height | 676 | 666 | 734 | 710 | 691 | 617 | 654 | 676 | 728 |
| x / cap | 0.740 | 0.794 | 0.718 | 0.817 | 0.735 | 0.799 | 0.894 | 0.794 | 0.739 |
| ascender (b,d,h top) | 734 | 739 | 771 | 780 | 728 | 661 | 730 | 734 | 778 |
| ascender / cap | 1.087 | 1.110 | 1.050 | 1.099 | 1.054 | 1.071 | 1.117 | 1.087 | 1.069 |
| descender (p,q) | -193 | -190 | -206 | -145 | -221 | -190 | -231 | -193 | -228 |
| o overshoot top | 16 | 0 | 0 | 9 | 3 | 8 | -56 | 3 | 10 |
| o overshoot bottom | 14 | 9 | 2 | 9 | 18 | 16 | 8 | 9 | 8 |
| o overshoot % x | 3.0 | 0.9 | 0.2 | 1.6 | 2.1 | 2.4 | -4.0 | 1.6 | 1.6 |
| O overshoot top | 20 | 15 | 0 | 10 | 8 | 8 | 6 | 8 | 10 |
| O overshoot bottom | 20 | 12 | 3 | 9 | 20 | 18 | 26 | 18 | 8 |
| O overshoot % cap | 2.9 | 2.0 | 0.2 | 1.3 | 2.0 | 2.1 | 2.4 | 2.0 | 1.2 |

#### Stems and contrast

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| n stem (left) | 219 | 251 | 191 | 270 | 181 | 170 | 200 | 200 | 223 |
| n stem (right) | 220 | 252 | 194 | 270 | 183 | 170 | 186 | 194 | 216 |
| l stem | 220 | 251 | 190 | 270 | 181 | 170 | 174 | 190 | 222 |
| i stem | 219 | 252 | 187 | 271 | 181 | 170 | 197 | 197 | 223 |
| H stem | 240 | 251 | 211 | 279 | 183 | 175 | 202 | 211 | 222 |
| o side (vertical) | 233 | 266 | 122 | 276 | 183 | 174 | 188 | 188 | 223 |
| O side | 264 | 262 | 127 | 292 | 183 | 180 | 198 | 198 | 223 |
| o top (horizontal) | 136 | 139 | 192 | 145 | 183 | 133 | 142 | 142 | 117 |
| o bottom | 131 | 138 | 227 | 145 | 183 | 133 | 180 | 145 | 117 |
| O top | 135 | 136 | 239 | 158 | 183 | 141 | 163 | 158 | 118 |
| n arch top | 100 | 102 | 138 | 99 | 171 | 133 | 159 | 133 | 83 |
| H crossbar | 108 | 189 | 147 | 187 | 156 | 138 | 171 | 156 | 115 |
| e crossbar | 64 | 74 | 33 | 85 | 94 | 115 | 109 | 85 | 74 |
| contrast o top/side | 0.59 | 0.52 | 1.57 | 0.53 | 1.00 | 0.76 | 0.76 | 0.76 | 0.52 |
| contrast n arch/stem | 0.46 | 0.41 | 0.72 | 0.37 | 0.94 | 0.78 | 0.80 | 0.72 | 0.37 |
| contrast H bar/stem | 0.45 | 0.75 | 0.70 | 0.67 | 0.85 | 0.79 | 0.85 | 0.75 | 0.52 |
| e bar / n stem | 0.29 | 0.29 | 0.17 | 0.31 | 0.52 | 0.68 | 0.54 | 0.31 | 0.33 |
| H stem / n stem | 1.10 | 1.00 | 1.10 | 1.03 | 1.01 | 1.03 | 1.01 | 1.03 | 1.00 |
| n stem % x-height | 43.8 | 47.4 | 36.2 | 46.6 | 35.7 | 34.5 | 34.2 | 36.2 | 41.4 |
| H stem % cap | 35.5 | 37.7 | 28.7 | 39.3 | 26.5 | 28.4 | 30.9 | 30.9 | 30.5 |

#### Widths (advance) and ratios to n

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| adv n | 671 | 716 | 547 | 673 | 566 | 583 | 665 | 665 | 724 |
| adv o | 602 | 656 | 558 | 685 | 558 | 586 | 585 | 586 | 755 |
| adv H | 802 | 834 | 672 | 727 | 650 | 672 | 547 | 672 | 755 |
| adv O | 778 | 733 | 706 | 756 | 721 | 703 | 677 | 721 | 826 |
| adv a | 567 | 654 | 551 | 664 | 557 | 544 | 648 | 567 | 887 |
| adv e | 530 | 560 | 526 | 640 | 535 | 549 | 562 | 549 | 754 |
| adv s | 477 | 593 | 540 | 611 | 457 | 492 | 494 | 494 | 614 |
| adv m | 964 | 1048 | 804 | 981 | 791 | 847 | 929 | 929 | 1048 |
| adv v | 627 | 599 | 537 | 679 | 577 | 545 | 504 | 577 | 732 |
| avg a–z | 595 | 619 | 529 | 631 | 515 | 527 | 554 | 554 | 709 |
| o/n | 0.897 | 0.916 | 1.020 | 1.018 | 0.986 | 1.005 | 0.880 | 0.986 | 1.043 |
| H/n | 1.195 | 1.165 | 1.229 | 1.080 | 1.148 | 1.153 | 0.823 | 1.153 | 1.043 |
| O/n | 1.160 | 1.024 | 1.291 | 1.123 | 1.274 | 1.206 | 1.018 | 1.160 | 1.141 |
| a/n | 0.845 | 0.913 | 1.007 | 0.987 | 0.984 | 0.933 | 0.974 | 0.974 | 1.225 |
| e/n | 0.790 | 0.782 | 0.962 | 0.951 | 0.945 | 0.942 | 0.844 | 0.942 | 1.041 |
| s/n | 0.710 | 0.828 | 0.987 | 0.908 | 0.807 | 0.844 | 0.743 | 0.828 | 0.848 |
| m/n | 1.437 | 1.464 | 1.470 | 1.458 | 1.398 | 1.453 | 1.397 | 1.453 | 1.448 |
| v/n | 0.935 | 0.837 | 0.982 | 1.009 | 1.019 | 0.935 | 0.757 | 0.935 | 1.011 |
| O/H | 0.971 | 0.879 | 1.051 | 1.040 | 1.109 | 1.046 | 1.238 | 1.046 | 1.094 |
| H/n | 1.195 | 1.165 | 1.229 | 1.080 | 1.148 | 1.153 | 0.823 | 1.153 | 1.043 |
| avg a–z / n | 0.887 | 0.865 | 0.968 | 0.937 | 0.910 | 0.904 | 0.833 | 0.904 | 0.979 |
| avg A–Z / H | 0.936 | 0.893 | 0.983 | 0.942 | 0.992 | 0.905 | 1.043 | 0.942 | 0.980 |
| n adv / x-height | 1.342 | 1.353 | 1.038 | 1.160 | 1.115 | 1.183 | 1.138 | 1.160 | 1.344 |

#### Counters

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| n counter (inner) | 99 | 83 | 110 | 63 | 143 | 138 | 184 | 110 | 202 |
| o counter (inner) | 88 | 94 | 267 | 82 | 164 | 176 | 169 | 164 | 252 |
| H counter | 152 | 177 | 186 | 89 | 228 | 192 | 77 | 177 | 233 |
| n counter / stem | 0.45 | 0.33 | 0.58 | 0.23 | 0.79 | 0.81 | 0.92 | 0.58 | 0.90 |
| o counter / side | 0.38 | 0.35 | 2.18 | 0.30 | 0.90 | 1.01 | 0.90 | 0.90 | 1.13 |
| H counter / stem | 0.63 | 0.70 | 0.88 | 0.32 | 1.25 | 1.10 | 0.38 | 0.70 | 1.05 |
| o counter / n counter | 0.89 | 1.13 | 2.43 | 1.30 | 1.14 | 1.28 | 0.92 | 1.14 | 1.25 |

#### Spacing (sidebearings from outline bounds)

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| n LSB | 26 | -41 | 27 | 35 | 30 | 52 | 34 | 30 | 38 |
| n RSB | 21 | 26 | 25 | 35 | 28 | 53 | 46 | 28 | 38 |
| o LSB | 26 | 10 | 23 | 25 | 14 | 31 | 26 | 25 | 28 |
| o RSB | 26 | 4 | 22 | 25 | 14 | 31 | 28 | 25 | 28 |
| H LSB | 20 | -26 | 32 | 40 | 28 | 65 | 25 | 28 | 38 |
| H RSB | 19 | -84 | 31 | 40 | 28 | 65 | 26 | 28 | 38 |
| O LSB | 34 | 40 | 24 | 25 | 14 | 35 | 20 | 25 | 28 |
| O RSB | 34 | -22 | 21 | 25 | 14 | 35 | 30 | 25 | 28 |
| v LSB | -1 | 14 | 13 | 5 | 15 | 20 | -1 | 13 | 38 |
| v RSB | -3 | -12 | 13 | 5 | 16 | 24 | 14 | 13 | 38 |
| o SB / n LSB | 1.01 | -0.17 | 0.83 | 0.71 | 0.47 | 0.60 | 0.80 | 0.71 | 0.74 |
| O SB / H SB | 1.77 | -0.16 | 0.71 | 0.62 | 0.50 | 0.54 | 0.99 | 0.62 | 0.74 |
| v SB / n LSB | -0.08 | -0.02 | 0.48 | 0.14 | 0.52 | 0.42 | 0.19 | 0.19 | 1.00 |
| n LSB / n stem | 0.12 | -0.16 | 0.14 | 0.13 | 0.17 | 0.31 | 0.17 | 0.14 | 0.17 |
| n LSB / n counter | 0.26 | -0.49 | 0.25 | 0.56 | 0.21 | 0.38 | 0.18 | 0.25 | 0.19 |
| H LSB / H stem | 0.08 | -0.10 | 0.15 | 0.14 | 0.15 | 0.37 | 0.12 | 0.14 | 0.17 |
| n (LSB+RSB) / counter | 0.48 | -0.18 | 0.47 | 1.11 | 0.40 | 0.76 | 0.44 | 0.47 | 0.38 |

#### Dots and balls

| metric | Capr | Shri | Bagel | Titan | Fred700 | Bal800 | Gr900 | ref median | **Toffee900** |
|---|---|---|---|---|---|---|---|---|---|
| i dot width | 275 | 252 | 199 | 280 | 181 | 186 | 236 | 236 | 225 |
| i dot height | 196 | 523 | 188 | 180 | 181 | 180 | 220 | 188 | 225 |
| i dot w / i stem | 1.26 | 1.00 | 1.06 | 1.03 | 1.00 | 1.09 | 1.20 | 1.06 | 1.01 |
| dot–stem gap | 18 | – | 21 | 38 | 49 | 43 | 58 | 41 | 53 |
| gap / i stem | 0.08 | – | 0.11 | 0.14 | 0.27 | 0.25 | 0.30 | 0.20 | 0.24 |
| period width | 228 | 206 | 248 | 213 | 192 | 194 | 234 | 213 | 225 |
| period w / n stem | 1.04 | 0.82 | 1.30 | 0.79 | 1.06 | 1.14 | 1.17 | 1.06 | 1.01 |
| period adv | 300 | 297 | 297 | 293 | 220 | 238 | 316 | 297 | 303 |

### Regular (400)

#### Vertical metrics

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| x-height | 481 | 469 | 578 | 481 | 539 |
| cap height | 688 | 613 | 653 | 653 | 729 |
| x / cap | 0.699 | 0.765 | 0.886 | 0.765 | 0.739 |
| ascender (b,d,h top) | 697 | 655 | 722 | 697 | 779 |
| ascender / cap | 1.013 | 1.069 | 1.105 | 1.069 | 1.069 |
| descender (p,q) | -207 | -190 | -228 | -207 | -229 |
| o overshoot top | -1 | 6 | -43 | -1 | 10 |
| o overshoot bottom | 16 | 13 | 15 | 15 | 9 |
| o overshoot % x | 1.5 | 2.0 | -2.4 | 1.5 | 1.7 |
| O overshoot top | 4 | 8 | 7 | 7 | 10 |
| O overshoot bottom | 17 | 13 | 26 | 17 | 9 |
| O overshoot % cap | 1.5 | 1.7 | 2.5 | 1.7 | 1.3 |

#### Stems and contrast

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| n stem (left) | 87 | 80 | 105 | 87 | 96 |
| n stem (right) | 88 | 80 | 98 | 88 | 94 |
| l stem | 89 | 80 | 91 | 89 | 96 |
| i stem | 88 | 80 | 99 | 88 | 96 |
| H stem | 90 | 82 | 105 | 90 | 96 |
| o side (vertical) | 88 | 82 | 98 | 88 | 96 |
| O side | 91 | 84 | 102 | 91 | 96 |
| o top (horizontal) | 86 | 66 | 77 | 77 | 62 |
| o bottom | 86 | 66 | 89 | 86 | 62 |
| O top | 91 | 69 | 86 | 86 | 62 |
| n arch top | 83 | 66 | 87 | 83 | 44 |
| H crossbar | 84 | 68 | 91 | 84 | 61 |
| e crossbar | 60 | 63 | 66 | 63 | 40 |
| contrast o top/side | 0.98 | 0.80 | 0.79 | 0.80 | 0.65 |
| contrast n arch/stem | 0.96 | 0.83 | 0.83 | 0.83 | 0.46 |
| contrast H bar/stem | 0.93 | 0.83 | 0.87 | 0.87 | 0.64 |
| e bar / n stem | 0.68 | 0.79 | 0.63 | 0.68 | 0.41 |
| H stem / n stem | 1.03 | 1.02 | 1.00 | 1.02 | 0.99 |
| n stem % x-height | 18.1 | 17.1 | 18.1 | 18.1 | 17.9 |
| H stem % cap | 13.1 | 13.4 | 16.1 | 13.4 | 13.1 |

#### Widths (advance) and ratios to n

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| adv n | 557 | 550 | 665 | 557 | 471 |
| adv o | 560 | 553 | 586 | 560 | 496 |
| adv H | 687 | 654 | 547 | 654 | 507 |
| adv O | 732 | 689 | 677 | 689 | 554 |
| adv a | 574 | 499 | 648 | 574 | 595 |
| adv e | 540 | 519 | 552 | 540 | 495 |
| adv s | 459 | 447 | 496 | 459 | 397 |
| adv m | 826 | 816 | 929 | 826 | 661 |
| adv v | 537 | 495 | 504 | 504 | 480 |
| avg a–z | 509 | 489 | 552 | 509 | 461 |
| o/n | 1.005 | 1.005 | 0.880 | 1.005 | 1.053 |
| H/n | 1.233 | 1.189 | 0.823 | 1.189 | 1.076 |
| O/n | 1.314 | 1.253 | 1.018 | 1.253 | 1.176 |
| a/n | 1.031 | 0.907 | 0.974 | 0.974 | 1.263 |
| e/n | 0.969 | 0.944 | 0.830 | 0.944 | 1.051 |
| s/n | 0.824 | 0.813 | 0.746 | 0.813 | 0.843 |
| m/n | 1.483 | 1.484 | 1.397 | 1.483 | 1.403 |
| v/n | 0.964 | 0.900 | 0.757 | 0.900 | 1.019 |
| O/H | 1.066 | 1.054 | 1.238 | 1.066 | 1.093 |
| H/n | 1.233 | 1.189 | 0.823 | 1.189 | 1.076 |
| avg a–z / n | 0.913 | 0.890 | 0.830 | 0.890 | 0.980 |
| avg A–Z / H | 0.957 | 0.896 | 1.030 | 0.957 | 0.974 |
| n adv / x-height | 1.159 | 1.173 | 1.150 | 1.159 | 0.873 |

#### Counters

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| n counter (inner) | 262 | 240 | 302 | 262 | 200 |
| o counter (inner) | 317 | 291 | 306 | 306 | 246 |
| H counter | 361 | 312 | 187 | 312 | 238 |
| n counter / stem | 3.00 | 3.00 | 2.88 | 3.00 | 2.08 |
| o counter / side | 3.61 | 3.55 | 3.13 | 3.55 | 2.56 |
| H counter / stem | 4.01 | 3.80 | 1.78 | 3.80 | 2.49 |
| o counter / n counter | 1.21 | 1.21 | 1.01 | 1.21 | 1.23 |

#### Spacing (sidebearings from outline bounds)

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| n LSB | 64 | 75 | 62 | 64 | 38 |
| n RSB | 56 | 75 | 80 | 75 | 39 |
| o LSB | 34 | 49 | 44 | 44 | 28 |
| o RSB | 34 | 49 | 45 | 45 | 29 |
| H LSB | 73 | 89 | 57 | 73 | 38 |
| H RSB | 73 | 89 | 71 | 73 | 39 |
| O LSB | 26 | 54 | 50 | 50 | 28 |
| O RSB | 26 | 55 | 68 | 55 | 29 |
| v LSB | 31 | 30 | 12 | 30 | 38 |
| v RSB | 31 | 36 | 25 | 31 | 39 |
| o SB / n LSB | 0.53 | 0.65 | 0.72 | 0.65 | 0.74 |
| O SB / H SB | 0.36 | 0.61 | 0.93 | 0.61 | 0.75 |
| v SB / n LSB | 0.48 | 0.44 | 0.29 | 0.44 | 1.00 |
| n LSB / n stem | 0.73 | 0.94 | 0.60 | 0.73 | 0.40 |
| n LSB / n counter | 0.24 | 0.31 | 0.21 | 0.24 | 0.19 |
| H LSB / H stem | 0.81 | 1.09 | 0.54 | 0.81 | 0.40 |
| n (LSB+RSB) / counter | 0.46 | 0.62 | 0.47 | 0.47 | 0.38 |

#### Dots and balls

| metric | Fred400 | Bal400 | Gr400 | ref median | **Toffee400** |
|---|---|---|---|---|---|
| i dot width | 101 | 103 | 139 | 103 | 82 |
| i dot height | 103 | 100 | 143 | 103 | 82 |
| i dot w / i stem | 1.15 | 1.29 | 1.40 | 1.29 | 0.85 |
| dot–stem gap | 120 | 91 | 80 | 91 | 51 |
| gap / i stem | 1.37 | 1.14 | 0.80 | 1.14 | 0.53 |
| period width | 106 | 109 | 160 | 109 | 82 |
| period w / n stem | 1.22 | 1.36 | 1.53 | 1.36 | 0.85 |
| period adv | 211 | 141 | 316 | 211 | 159 |

### Light (300)

#### Vertical metrics

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| x-height | 472 | 578 | 525 | 540 |
| cap height | 687 | 653 | 670 | 730 |
| x / cap | 0.687 | 0.885 | 0.786 | 0.740 |
| ascender (b,d,h top) | 687 | 722 | 704 | 780 |
| ascender / cap | 1.000 | 1.105 | 1.053 | 1.069 |
| descender (p,q) | -202 | -228 | -215 | -230 |
| o overshoot top | -3 | -41 | -22 | 10 |
| o overshoot bottom | 15 | 17 | 16 | 9 |
| o overshoot % x | 1.3 | -2.1 | -0.4 | 1.8 |
| O overshoot top | 3 | 7 | 5 | 10 |
| O overshoot bottom | 16 | 26 | 21 | 9 |
| O overshoot % cap | 1.4 | 2.5 | 1.9 | 1.3 |

#### Stems and contrast

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| n stem (left) | 56 | 85 | 71 | 71 |
| n stem (right) | 57 | 80 | 69 | 69 |
| l stem | 58 | 75 | 66 | 70 |
| i stem | 57 | 80 | 68 | 71 |
| H stem | 59 | 86 | 72 | 70 |
| o side (vertical) | 56 | 80 | 68 | 71 |
| O side | 60 | 83 | 71 | 71 |
| o top (horizontal) | 54 | 64 | 59 | 51 |
| o bottom | 54 | 71 | 63 | 51 |
| O top | 60 | 71 | 65 | 51 |
| n arch top | 52 | 72 | 62 | 36 |
| H crossbar | 60 | 76 | 68 | 50 |
| e crossbar | 48 | 58 | 53 | 33 |
| contrast o top/side | 0.96 | 0.80 | 0.88 | 0.72 |
| contrast n arch/stem | 0.93 | 0.84 | 0.88 | 0.51 |
| contrast H bar/stem | 1.02 | 0.88 | 0.95 | 0.71 |
| e bar / n stem | 0.86 | 0.67 | 0.77 | 0.47 |
| H stem / n stem | 1.05 | 1.01 | 1.03 | 0.99 |
| n stem % x-height | 11.9 | 14.8 | 13.3 | 13.2 |
| H stem % cap | 8.6 | 13.2 | 10.9 | 9.6 |

#### Widths (advance) and ratios to n

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| adv n | 554 | 665 | 610 | 420 |
| adv o | 560 | 586 | 573 | 444 |
| adv H | 699 | 547 | 623 | 457 |
| adv O | 735 | 677 | 706 | 499 |
| adv a | 580 | 648 | 614 | 536 |
| adv e | 542 | 550 | 546 | 443 |
| adv s | 460 | 496 | 478 | 354 |
| adv m | 837 | 929 | 883 | 584 |
| adv v | 524 | 504 | 514 | 429 |
| avg a–z | 506 | 552 | 529 | 412 |
| o/n | 1.011 | 0.881 | 0.946 | 1.057 |
| H/n | 1.262 | 0.823 | 1.042 | 1.088 |
| O/n | 1.327 | 1.018 | 1.172 | 1.188 |
| a/n | 1.047 | 0.974 | 1.010 | 1.276 |
| e/n | 0.978 | 0.827 | 0.903 | 1.055 |
| s/n | 0.830 | 0.747 | 0.788 | 0.843 |
| m/n | 1.511 | 1.397 | 1.454 | 1.390 |
| v/n | 0.946 | 0.757 | 0.851 | 1.021 |
| O/H | 1.052 | 1.238 | 1.145 | 1.092 |
| H/n | 1.262 | 0.823 | 1.042 | 1.088 |
| avg a–z / n | 0.914 | 0.830 | 0.872 | 0.980 |
| avg A–Z / H | 0.946 | 1.027 | 0.987 | 0.972 |
| n adv / x-height | 1.173 | 1.152 | 1.162 | 0.778 |

#### Counters

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| n counter (inner) | 301 | 325 | 313 | 200 |
| o counter (inner) | 368 | 333 | 351 | 245 |
| H counter | 405 | 209 | 307 | 239 |
| n counter / stem | 5.38 | 3.81 | 4.59 | 2.81 |
| o counter / side | 6.57 | 4.18 | 5.37 | 3.46 |
| H counter / stem | 6.86 | 2.43 | 4.65 | 3.40 |
| o counter / n counter | 1.22 | 1.02 | 1.12 | 1.22 |

#### Spacing (sidebearings from outline bounds)

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| n LSB | 75 | 68 | 72 | 38 |
| n RSB | 65 | 87 | 76 | 38 |
| o LSB | 40 | 48 | 44 | 28 |
| o RSB | 40 | 49 | 44 | 28 |
| H LSB | 88 | 63 | 75 | 38 |
| H RSB | 88 | 81 | 84 | 38 |
| O LSB | 30 | 56 | 43 | 28 |
| O RSB | 30 | 76 | 53 | 28 |
| v LSB | 36 | 14 | 25 | 38 |
| v RSB | 35 | 27 | 31 | 38 |
| o SB / n LSB | 0.53 | 0.71 | 0.62 | 0.74 |
| O SB / H SB | 0.34 | 0.92 | 0.63 | 0.74 |
| v SB / n LSB | 0.48 | 0.30 | 0.39 | 1.00 |
| n LSB / n stem | 1.34 | 0.80 | 1.07 | 0.54 |
| n LSB / n counter | 0.25 | 0.21 | 0.23 | 0.19 |
| H LSB / H stem | 1.49 | 0.73 | 1.11 | 0.54 |
| n (LSB+RSB) / counter | 0.47 | 0.48 | 0.47 | 0.38 |

#### Dots and balls

| metric | Fred300 | Gr300 | ref median | **Toffee300** |
|---|---|---|---|---|
| i dot width | 75 | 120 | 97 | 53 |
| i dot height | 77 | 128 | 103 | 53 |
| i dot w / i stem | 1.32 | 1.50 | 1.41 | 0.75 |
| dot–stem gap | 144 | 84 | 114 | 51 |
| gap / i stem | 2.53 | 1.05 | 1.79 | 0.71 |
| period width | 78 | 146 | 112 | 53 |
| period w / n stem | 1.39 | 1.70 | 1.55 | 0.75 |
| period adv | 208 | 316 | 262 | 130 |

### How the weight axis moves (heavy / regular)

| font | n stem | o top | n adv | o adv | H adv | avg a–z | n counter | n LSB | o LSB | H LSB | x-height | contrast o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fredoka | 181/87 | 183/86 | 566/557 | 558/560 | 650/687 | 515/509 | 143/262 | 30/64 | 14/34 | 28/73 | 508/481 | 1.00/0.98 |
| Baloo 2 | 170/80 | 133/66 | 583/550 | 586/553 | 672/654 | 527/489 | 138/240 | 52/75 | 31/49 | 65/89 | 493/469 | 0.76/0.80 |
| Grandstander | 200/105 | 142/77 | 665/665 | 585/586 | 547/547 | 554/552 | 184/302 | 34/62 | 26/44 | 25/57 | 584/578 | 0.76/0.79 |
| **Toffee 900/400** | 223/96 | 117/62 | 724/471 | 755/496 | 755/507 | 709/461 | 202/200 | 38/38 | 28/28 | 38/38 | 538/539 | 0.52/0.65 |
| Fredoka 700/300 | 181/56 | 183/54 | 566/554 | 558/560 | 650/699 | 515/506 | 143/301 | 30/75 | 14/40 | 28/88 | 508/472 | 1.00/0.96 |
| Grandstander 900/300 | 200/85 | 142/64 | 665/665 | 585/586 | 547/547 | 554/552 | 184/325 | 34/68 | 26/48 | 25/63 | 584/578 | 0.76/0.80 |
| **Toffee 900/300** | 223/71 | 117/51 | 724/420 | 755/444 | 755/457 | 709/412 | 202/200 | 38/38 | 28/28 | 38/38 | 538/540 | 0.52/0.72 |

(Δadv n / Δstem): Fredoka: 0.10, Baloo 2: 0.37, Grandstander: 0.00, **Toffee 900/400**: 2.00, Fredoka 700/300: 0.10, Grandstander 900/300: 0.00, **Toffee 900/300**: 2.00
(ΔLSB n / Δstem): Fredoka: -0.36, Baloo 2: -0.26, Grandstander: -0.30, **Toffee 900/400**: 0.00, Fredoka 700/300: -0.36, Grandstander 900/300: -0.30, **Toffee 900/300**: 0.00

### Every glyph's advance / n advance

⚠ marks a deviation above 0.12 from the heavy median. Δk is the change in skeleton width, in `wn`, that would hit the heavy median at 900 (or the 400 median at 300) with today's n.

| glyph | heavy ref median | heavy min–max | 400 ref median | Toffee900 | Toffee300 | T900 − med | Δk@900 (wn) | Δk@300 (wn) |
|---|---|---|---|---|---|---|---|---|
| a ⚠ | 0.97 | 0.84–1.01 | 0.97 | 1.23 | 1.28 | +0.25 | -0.48 | -0.49 |
| b | 0.98 | 0.90–1.04 | 1.00 | 1.03 | 1.03 | +0.05 | -0.09 | -0.05 |
| c | 0.82 | 0.76–0.95 | 0.87 | 0.94 | 0.89 | +0.12 | -0.23 | -0.03 |
| d ⚠ | 0.98 | 0.90–1.06 | 0.99 | 1.23 | 1.28 | +0.25 | -0.47 | -0.46 |
| e | 0.94 | 0.78–0.96 | 0.94 | 1.04 | 1.05 | +0.10 | -0.19 | -0.18 |
| f | 0.74 | 0.58–0.83 | 0.68 | 0.85 | 0.84 | +0.11 | -0.21 | -0.26 |
| g | 0.96 | 0.86–1.01 | 0.98 | 1.04 | 1.05 | +0.08 | -0.15 | -0.13 |
| h | 0.99 | 0.84–1.01 | 0.96 | 1.00 | 1.00 | +0.01 | -0.01 | -0.06 |
| i | 0.48 | 0.44–0.53 | 0.44 | 0.42 | 0.35 | -0.07 | +0.12 | +0.14 |
| j ⚠ | 0.49 | 0.41–0.59 | 0.44 | 0.73 | 0.70 | +0.24 | -0.46 | -0.42 |
| k | 0.95 | 0.87–1.09 | 0.88 | 0.94 | 0.96 | -0.01 | +0.02 | -0.13 |
| l | 0.51 | 0.43–0.55 | 0.48 | 0.61 | 0.60 | +0.11 | -0.20 | -0.18 |
| m | 1.45 | 1.40–1.47 | 1.48 | 1.45 | 1.39 | -0.01 | +0.01 | +0.15 |
| n | 1.00 | 1.00–1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| o | 0.99 | 0.88–1.02 | 1.01 | 1.04 | 1.06 | +0.06 | -0.11 | -0.08 |
| p | 0.99 | 0.92–1.07 | 0.99 | 1.03 | 1.03 | +0.04 | -0.08 | -0.06 |
| q | 0.97 | 0.91–1.04 | 0.99 | 1.03 | 1.03 | +0.06 | -0.12 | -0.06 |
| r | 0.80 | 0.64–0.88 | 0.69 | 0.81 | 0.78 | +0.02 | -0.03 | -0.14 |
| s | 0.83 | 0.71–0.99 | 0.81 | 0.85 | 0.84 | +0.02 | -0.04 | -0.05 |
| t | 0.72 | 0.60–0.95 | 0.68 | 0.76 | 0.79 | +0.04 | -0.09 | -0.18 |
| u ⚠ | 1.00 | 0.89–1.01 | 0.97 | 1.20 | 1.25 | +0.19 | -0.37 | -0.44 |
| v | 0.94 | 0.76–1.02 | 0.90 | 1.01 | 1.02 | +0.08 | -0.14 | -0.20 |
| w | 1.36 | 1.14–1.50 | 1.33 | 1.33 | 1.38 | -0.03 | +0.05 | -0.08 |
| x | 0.90 | 0.84–1.02 | 0.88 | 0.97 | 0.98 | +0.08 | -0.15 | -0.17 |
| y | 0.95 | 0.81–1.02 | 0.89 | 1.00 | 1.00 | +0.05 | -0.10 | -0.18 |
| z | 0.86 | 0.77–0.96 | 0.85 | 0.93 | 0.92 | +0.07 | -0.14 | -0.11 |
| A | 1.10 | 0.91–1.30 | 1.08 | 1.10 | 1.15 | -0.00 | +0.00 | -0.12 |
| B | 1.06 | 0.88–1.18 | 1.09 | 1.03 | 1.08 | -0.03 | +0.06 | +0.02 |
| C | 0.98 | 0.85–1.21 | 1.07 | 1.04 | 1.01 | +0.06 | -0.12 | +0.10 |
| D | 1.14 | 0.90–1.21 | 1.19 | 1.06 | 1.10 | -0.09 | +0.17 | +0.15 |
| E | 0.94 | 0.72–1.12 | 0.97 | 0.91 | 0.94 | -0.03 | +0.05 | +0.05 |
| F | 0.91 | 0.71–1.08 | 0.94 | 0.90 | 0.92 | -0.01 | +0.03 | +0.04 |
| G | 1.14 | 0.96–1.29 | 1.16 | 1.13 | 1.16 | -0.01 | +0.02 | -0.00 |
| H | 1.15 | 0.82–1.23 | 1.19 | 1.04 | 1.09 | -0.11 | +0.21 | +0.16 |
| I | 0.52 | 0.42–0.62 | 0.42 | 0.41 | 0.35 | -0.11 | +0.21 | +0.12 |
| J | 0.89 | 0.61–1.06 | 0.89 | 0.91 | 0.90 | +0.03 | -0.05 | -0.03 |
| K | 1.05 | 0.84–1.23 | 1.03 | 1.00 | 1.05 | -0.05 | +0.10 | -0.03 |
| L | 0.91 | 0.72–1.09 | 0.91 | 0.89 | 0.90 | -0.02 | +0.05 | +0.01 |
| M ⚠ | 1.37 | 1.12–1.52 | 1.42 | 1.23 | 1.30 | -0.14 | +0.27 | +0.19 |
| N ⚠ | 1.16 | 0.96–1.25 | 1.20 | 1.04 | 1.09 | -0.12 | +0.23 | +0.18 |
| O | 1.16 | 1.02–1.29 | 1.25 | 1.14 | 1.19 | -0.02 | +0.04 | +0.11 |
| P | 1.02 | 0.76–1.15 | 1.03 | 0.98 | 1.01 | -0.04 | +0.07 | +0.03 |
| Q | 1.16 | 0.97–1.38 | 1.25 | 1.23 | 1.30 | +0.07 | -0.13 | -0.07 |
| R | 1.06 | 0.82–1.18 | 1.07 | 1.01 | 1.06 | -0.05 | +0.10 | +0.01 |
| S | 0.96 | 0.87–1.18 | 0.95 | 0.92 | 0.91 | -0.04 | +0.07 | +0.06 |
| T | 1.04 | 0.78–1.23 | 0.95 | 1.02 | 1.06 | -0.03 | +0.05 | -0.17 |
| U | 1.14 | 0.91–1.22 | 1.18 | 1.04 | 1.09 | -0.10 | +0.18 | +0.15 |
| V | 1.09 | 0.89–1.29 | 1.06 | 1.10 | 1.15 | +0.01 | -0.01 | -0.15 |
| W | 1.55 | 1.01–1.70 | 1.46 | 1.44 | 1.55 | -0.11 | +0.22 | -0.14 |
| X | 1.13 | 0.94–1.24 | 1.07 | 1.04 | 1.09 | -0.09 | +0.17 | -0.02 |
| Y | 1.10 | 0.80–1.28 | 1.00 | 1.00 | 1.06 | -0.11 | +0.20 | -0.10 |
| Z | 1.02 | 0.78–1.13 | 1.01 | 0.97 | 1.00 | -0.05 | +0.10 | +0.02 |
| 0 | 1.00 | 0.82–1.14 | 1.05 | 1.06 | 1.02 | +0.06 | -0.12 | +0.06 |
| 1 | 0.67 | 0.61–0.89 | 0.65 | 0.69 | 0.67 | +0.02 | -0.04 | -0.03 |
| 2 ⚠ | 0.91 | 0.75–1.14 | 0.92 | 1.08 | 1.05 | +0.17 | -0.33 | -0.20 |
| 3 ⚠ | 0.90 | 0.78–1.10 | 0.92 | 1.05 | 0.97 | +0.14 | -0.27 | -0.09 |
| 4 ⚠ | 0.97 | 0.83–1.27 | 0.98 | 1.12 | 1.10 | +0.15 | -0.28 | -0.20 |
| 5 ⚠ | 0.90 | 0.85–1.11 | 0.93 | 1.04 | 0.96 | +0.15 | -0.28 | -0.05 |
| 6 ⚠ | 0.96 | 0.87–1.08 | 0.96 | 1.10 | 1.03 | +0.15 | -0.28 | -0.12 |
| 7 ⚠ | 0.89 | 0.76–1.10 | 0.83 | 1.09 | 1.06 | +0.19 | -0.37 | -0.38 |
| 8 | 0.96 | 0.89–1.17 | 1.00 | 1.06 | 1.02 | +0.10 | -0.19 | -0.02 |
| 9 ⚠ | 0.96 | 0.80–1.08 | 0.96 | 1.10 | 1.03 | +0.15 | -0.28 | -0.12 |

Toffee's per-glyph sidebearings are uniform: 38 straight and 28 round at every weight.


## 3. Where Toffee is out of family, or inconsistent with itself

Width deltas are taken from the per-glyph table above. "Ratio" means advance ÷ n advance; the "ref" figure
is the heavy-weight median.

**A. The weight axis condenses the face. This is the biggest problem.** n's skeleton is `wn + 0.4a =
200 + 2a`, and its inner counter is `nw − 2a`, which is **exactly 200 units at every weight**. So a
lighter weight only loses ink, and the letter shrinks around a fixed hole. The n advance goes from 724 at
900 to 420 at 300: Δadvance/Δstem = **2.0**. The references hold the advance nearly still: Fredoka 0.10,
Baloo 2 0.37, Grandstander 0.00. Their counters grow instead, from 143 to 301 (Fredoka 700→300). The
result:

- At 300, Toffee's n advance / x-height is **0.78**, against **1.16** for the references at 300 and at 400.
- Its n counter / stem is 2.8, against 4.6.
- The 400 row in `compare.png` reads as a condensed face, not as a Regular of the same family.

At 900, n advance / x is 1.34. That matches Caprasimo and Shrikhand (1.34–1.35) but is wider than the
reference median (1.16). It is also more open than the photo: e's ink width / x is 1.28 in Toffee and 0.90
in the photo, and B's ink width / cap is 0.92 against 0.79.

**B. Sidebearings are flat (38) at every weight.** Every variable reference opens its sidebearings as the
weight drops: Δn-LSB/Δstem = −0.36, −0.26 and −0.30 for Fredoka, Baloo 2 and Grandstander. One rule holds
at every weight in the references: **sidebearing ≈ 0.24 × n counter**; the median is 0.25 at heavy, 0.24
at 400 and 0.23 at 300. Toffee comes to 0.19 at every weight. Its n LSB / stem is 0.17 at 900 (references
0.14, so slightly loose) but 0.54 at 300 (references 1.07, so too tight).

**C. Diagonals get the straight sidebearing.** In Toffee, v, w, x, y, A, V and Y have a sidebearing /
n-LSB ratio of **1.00**. The reference medians are 0.25–0.49: v 0.26/0.44, w 0.33/0.31, x 0.40/0.37, y
0.36/0.49, A 0.36/0.49 and Y 0.25/0.26. "tiv" in `compare.png` shows this.

**D. The round-side sets are incomplete, and one pair is backwards** (`ROUND_LEFT` / `ROUND_RIGHT`):

- **g** is missing from `ROUND_LEFT` (references 0.55 × n-LSB).
- **s** is missing from both sets (references 0.61 left and 0.64 right; `S` is already in both).
- The right sides of **c** and **e** take the straight sidebearing (38), but the references treat them as
  round (0.67 and 0.69).
- The right sides of **B, P and R** are straight in Toffee; the references use 0.66, 0.47 and 0.44.
- **J**'s left side is straight; the references use 0.45.
- The parentheses are swapped: `parenright` is in `ROUND_LEFT` and `parenleft` in `ROUND_RIGHT`. `(` bulges
  to the left (`ARC(rx, …, 118→242)`), so it belongs in `ROUND_LEFT`.

**E. Tails and hooks are counted in the advance.** Spacing comes from ink bounds, so each flick widens its
glyph:

| glyph | Toffee ratio at 900 | ref |
|---|---|---|
| a | 1.23 | 0.97 |
| d | 1.23 | 0.98 |
| u | 1.20 | 1.00 |
| l | 0.61 | 0.51 |
| f | 0.85 | 0.74 |
| j | 0.73 | 0.49 |

The references let tails and hooks overhang:

- j has a negative LSB (median −1.7 × n-LSB).
- f's sidebearings are 0.21 and 0.18 × n-LSB.
- r's RSB is 0.33 and k's RSB 0.23.
- t's sidebearings are 0.34 and 0.59.

`compare.png` shows the gaps after f and r in "Hamburgefonstiv".

**F. Lowercase and caps follow two different width rules.** The latest lowercase pass added `+k·a` terms
(`_lc_nw`, `_lc_rx`, and k, m, v, w, x, z). Caps are still plain `wn` multiples. So at 900 the caps now run
**narrow** against n:

| glyph | Toffee ratio at 900 | ref |
|---|---|---|
| H | 1.04 | 1.15 |
| N | 1.04 | 1.16 |
| U | 1.04 | 1.14 |
| M | 1.23 | 1.37 |
| W | 1.44 | 1.55 |
| Y | 1.00 | 1.10 |
| I | 0.41 | 0.52 |
| D | 1.06 | 1.14 |

H/n also drifts with weight (1.04 at 900, 1.09 at 300). In the references the ratios hardly move between
heavy and 400.

**G. The figures are too wide at 900.** `fig_w = 1.05wn + 0.8a` gives ratios of 1.04–1.12; the reference
range is 0.90–0.97 (1: 0.67). The 0.8a term is what pushes them out at 900.

**H. Dots shrink faster than stems.** `dot = 0.62 + 0.0035a` gives an i-dot / stem ratio of 1.01 at 900,
0.85 at 400 and **0.75 at 300**. The references go the other way: 1.06, 1.29 and 1.41 (a light weight's
dot is relatively bigger). The dot-to-stem gap is a fixed 50 in Toffee; the references use 41 at heavy, 91
at 400 and 114 at 300.

**I. Contrast.** Toffee's o top / side is 0.52 at 900 and 0.72 at 300.

- At 900 that matches the Cooper-style fat faces (Caprasimo 0.59, Shrikhand 0.52, Titan 0.53).
- It does **not** match the photo (0.84–0.88) or the rounded faces (Fredoka 1.00, Baloo 2 and
  Grandstander 0.76).
- Toffee's n-arch / stem is 0.37, and its H bar / stem 0.52 against a reference median of 0.75. The H bar
  is thin even for the fat faces.

**J. Vertical metrics.**

- x/cap is 0.739. The photo is 0.78 and the reference median 0.79; only Caprasimo, Fredoka and Bagel are
  as low as Toffee.
- O's overshoot is 1.2% of cap, against 2.0% in the references, because one `ov = 10` serves both cases.
- The descender (−230) is at the deep end of the references (−145 to −231, median −193).
- The ascender / cap ratio (1.07) is in family (references 1.05–1.12).

**K. Self-consistency that holds up.**

- Stems are uniform: n, l, i, H, o-side and O-side are all 2a ± 1%. The references vary by up to 10%.
- The o-counter / n-counter ratio is 1.25 (references 1.14–1.21).
- m/n = 1.45 matches the references exactly.
- w, s, r, t, k, y, b, p and q are within ±0.06 of the reference medians.
- The 11° lean of the photo matches the `slnt −12` axis.

## 4. Recommendations in Toffee's parameters

Toffee has only two weight masters (a = 112 at 900, a = 36 at 300), so any rule that is linear in `a` is
reproduced exactly by interpolation. Each rule below is given as a formula in `a` with its values at 900
and 300 (and at 400, where a ≈ 48.7). **R** marks a value the references support; **P** a value the photo
supports; **J** a judgment call.

### 4.1 Width system

1. **Make `wn` a constant: `wn = 385`.** This replaces `200 + 1.6a` and `_lc_nw = wn + 0.4a`; the n
   skeleton becomes stem-to-stem 385 at every weight. **R.**
   - The skeleton barely moves in the references: solving for their n advance and sidebearings gives 377
     at 900, 386 at 400 and 387 at 300.
   - The n advance becomes `N = wn + 2a + 2·SB_s = 583 + 0.8a`: **673 at 900, 622 at 400, 612 at 300.**
     n/x is 1.25 at 900 and 1.13 at 300; the references are 1.16 at both.
   - The n counter becomes `wn − 2a`: **161 at 900** (counter/stem 0.72), **313 at 300** (references 313).
   - For a closer match to the photo (about 0.85× today's 900 width), use **`wn = 360`** instead
     (N = 648 at 900, n counter 136, counter/stem 0.61, the same as the photo's B). **J.**
2. **Define every glyph by a width class `r` (advance ÷ N), not by an ad-hoc multiple.** The skeleton
   width follows from the class:
   `W = r·N − 2a − SB_left − SB_right`, which is `W = r·wn + (r − 1)(2a + 2·SB_s) + (SB_s − SB_side)` for
   each non-straight side. Bowl radii are `rx = W/2`. Because `2a + 2·SB_s` is 288 at 900 and 226 at 300,
   the ratios hold at every weight.

   The classes, rounded from the heavy-reference medians (400 medians agree to ±0.05). **R**, except where
   marked:

   | r | lowercase | caps | figures |
   |---|---|---|---|
   | 0.50 | i j l | I (0.52) | |
   | 0.75 | f t r (r 0.80) | | 1 (0.67), **J** |
   | 0.85 | c s z; x 0.90 | | |
   | 0.92 | | E F L J (0.90–0.94) | 2 3 5 7 (0.90) |
   | 0.95 | e g k v y | | 0 4 6 8 9 (0.96–1.00) |
   | 1.00 | n h u a b d o p q | C S P Z T (0.96–1.04) | |
   | 1.08 | | A B K R V Y (1.05–1.10) | |
   | 1.15 | | D G H N O Q U X (1.13–1.16) | |
   | 1.36 / 1.45 | w / m | M 1.37 | |
   | 1.55 | | W | |

   To get tabular figures, set every figure to 0.93 instead (**J**).
3. **Leave tails, hooks and terminal flicks out of the spacing box.** Compute the advance from the stem
   and bowl only, then let the flick overhang:
   - **a, d, u, l, t**: the tail overhangs the RSB by ~0.5 × its own reach. Alternatively, shrink
     `tail_right`'s `rt` from 0.28wn to ~0.18wn. **J.**
   - **j**: LSB = −1.5·SB_s (**R**, median −1.7).
   - **f**: both sidebearings 0.2·SB_s, with the crossbar and hook overhanging (**R**).
   - **r**: RSB 0.33·SB_s (**R**).

   With the overhang, a, d and u land at 1.00 instead of 1.20–1.25, and j at 0.50 instead of 0.73.

### 4.2 Sidebearings (they should scale with weight)

| side | rule | 900 | 400 | 300 | support |
|---|---|---|---|---|---|
| straight `SB_s` | `99 − 0.6a` (≈0.24 × n counter) | **32** | 70 | **77** | **R**: references 30 / 64–75 / 72–76; ΔSB/Δstem −0.3 |
| round `SB_r` | `0.70·SB_s` | **22** | 49 | **54** | **R**: o 0.71 / 0.65 / 0.62; c 0.68, e 0.70, O/H 0.62 |
| s, S | `0.62·SB_s` | 20 | 43 | 48 | **R** (0.61 / 0.64) |
| diagonal `SB_d` (v w x y A V X Y, the k and R legs) | `0.35·SB_s` | **11** | 24 | **27** | **R**: medians 0.25–0.49 |
| open round (right side of c, e, C, G) | `0.70·SB_s` | 22 | 49 | 54 | **R** |
| P, R right side | `0.45·SB_s` | 14 | 31 | 35 | **R** |
| B right side | `0.65·SB_s` | 21 | 45 | 50 | **R** |
| J left side | `0.45·SB_s` | 14 | 31 | 35 | **R** |
| T both sides | `0.5·SB_s` | 16 | 35 | 39 | **R** |

Also add g to the round-left set, add s to both sets, and swap the parentheses (section 3D).

`BORDER/2 + 14` ties the spacing to the outline border. The cleaner fix is to keep the sidebearings above
and widen the COLR outline with tracking or the clip box, not with the base sidebearings (**J**). At 900,
`SB_s = 32` is close to today's 38: the photo's letter gaps average ~65 units for a pair, against 54
(round + straight) under these rules.

### 4.3 Contrast (`b/a`)

| | today | recommended | support |
|---|---|---|---|
| 900 | 60/112 = **0.54** | **0.75 → b = 84** | **P** (0.84–0.88) and the rounded references (0.76); the fat faces sit at 0.52–0.59, so this is a **J** between the two |
| 300 | 26/36 = **0.72** | **0.90 → b = 32** | **R** (300 references 0.88; 400 references 0.80–0.98) |

Supporting rules:

- e's crossbar should be ≈0.42 × stem at 900 (**P** 0.42; fat faces 0.29–0.31) and ≈0.75 × stem at 300
  (**R** 0.77). With b = 84, that is an e-bar pen scale of **0.56 at 900 and 0.85 at 300**, against 0.65
  at both today.
- The H bar should match o's top (pen scale 1.0, as now). Its ratio to the stem then follows b/a.

### 4.4 Vertical metrics

- **x/cap = 0.78**: X = **570** with C = 730. **P** (0.78) and **R** (median 0.79).
- Keep a = 112. Stem / x then becomes 39%; the photo and the reference median are 36%, which a ≈ 103
  would match (**J**). At 300 the stem / x of 12.6% stays in family (references 11.9–14.8%).
- **Overshoot**: lowercase `ov_x = 10` (1.75% of 570; references 1.6%) and caps **`ov_C = 14`** (references
  2.0% of cap; Toffee is 1.2% today). Split `ov` into two values. **R.**
- Ascender 780 is fine (references 1.05–1.12 × cap). Descender −230 can stay, or move to **−210** for a
  tighter line (references median −193). **J.**

### 4.5 Dots and balls

- **i/j dot and punctuation: `dot = 1.58 − 0.0046a`.** Today it is `0.62 + 0.0035a`. This gives a dot
  diameter / stem of **1.065 at 900** (diameter 239) and **1.41 at 300** (102). **R**: references 1.06 /
  1.29 / 1.41.
- **Dot gap = `155 − a`.** Today it is a fixed 50. This gives **43 at 900** and **119 at 300**. **R**:
  references 41 / 91 / 114.
- **Terminal balls** (c, e, s, r, f, J, the hooks): keep them separate from the i-dot. Use
  **`ball = 1.10` × pen half-width, constant across weight**, so balls stay a little fatter than the
  stroke without ballooning at 300. **J**: the light references have no true balls, and the photo's balls
  are ≈1.1–1.2 × the stroke.

### 4.6 Supported versus judgment calls

- **Supported by the references** (several fonts agree, at more than one weight):
  - the near-constant skeleton width;
  - sidebearings rising as the weight drops (≈0.24 × counter);
  - the round, diagonal and overhang ratios;
  - the width classes;
  - dot size and gap against weight;
  - the cap overshoot;
  - the contrast at 300.
- **Supported by the photo:** x/cap 0.78; stem 36% of x; contrast ≈0.85; e-bar 0.42 × stem; 900 widths
  about 15% narrower than today; slant ≈11°, which matches the axis.
- **Judgment calls:**
  - 900 contrast exactly 0.75;
  - `wn` 385 versus 360 (reference median versus photo);
  - a = 112 versus 103;
  - descender −210;
  - the terminal-ball constant 1.10;
  - how far tails overhang;
  - proportional versus tabular figures.
