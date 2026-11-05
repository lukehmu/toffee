# /// script
# dependencies = ["fonttools"]
# ///
"""favicon.svg: Toffee "T" (shadow + face layers, palette 0) on the page's orange, from the font's outlines."""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

font = instantiateVariableFont(TTFont(sys.argv[1]), {"wght": 900, "slnt": -8, "SHDW": 350})
gs = font.getGlyphSet()
ch = sys.argv[3] if len(sys.argv) > 3 else "T"
name = font.getBestCmap()[ord(ch)]
bp = BoundsPen(gs)
for g in (name + ".shadow", name):
    gs[g].draw(bp)
x0, y0, x1, y1 = bp.bounds
w, h = x1 - x0, y1 - y0
side = max(w, h) * 1.16
pad_x, pad_y = (side - w) / 2, (side - h) / 2
paths = []
for g, col in ((name + ".shadow", "#3c1c20"), (name, "#f3ecd1")):
    p = SVGPathPen(gs)
    gs[g].draw(p)
    paths.append(f'<path fill="{col}" d="{p.getCommands()}"/>')
s = side
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s:.0f} {s:.0f}">'
       f'<rect width="{s:.0f}" height="{s:.0f}" rx="{s * .2:.0f}" fill="#e2482a"/>'
       f'<g transform="translate({pad_x - x0:.0f} {s - pad_y + y0:.0f}) scale(1 -1)">'
       + "".join(paths) + "</g></svg>\n")
open(sys.argv[2], "w").write(svg)
print(len(svg), "bytes", bp.bounds)
