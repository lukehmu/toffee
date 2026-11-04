"""Toffee glyph skeletons.

Every glyph is a list of strokes; a stroke is a list of samples (x, y, s, r):
skeleton point, pen scale, pen roundness (0 = the elliptical pen, 1 = a circle of
the pen's width). Consecutive samples are joined by a convex capsule, so corners
join round by construction. Sample counts never depend on the weight, so every
master stays point-compatible.
"""

import math

from fontTools.agl import toUnicode
from types import SimpleNamespace

GLYPHS: dict[str, tuple[int | None, object]] = {}


def glyph(name, uni=None):
    def deco(fn):
        GLYPHS[name] = (uni if uni is not None else ord(toUnicode(name)), fn)
        return fn

    return deco


def _lerp(v0, v1, i, n):
    return v0 + (v1 - v0) * i / n if n else v0


def LN(x0, y0, x1, y1, s0=1, s1=None, r0=0, r1=None):
    s1 = s0 if s1 is None else s1
    r1 = r0 if r1 is None else r1
    return [(x0, y0, s0, r0), (x1, y1, s1, r1)]


def ARC(cx, cy, rx, ry, a0, a1, s0=1, s1=None, r0=0, r1=None, step=10):
    s1 = s0 if s1 is None else s1
    r1 = r0 if r1 is None else r1
    n = max(1, math.ceil(abs(a1 - a0) / step))
    out = []
    for i in range(n + 1):
        t = math.radians(_lerp(a0, a1, i, n))
        out.append(
            (cx + rx * math.cos(t), cy + ry * math.sin(t), _lerp(s0, s1, i, n), _lerp(r0, r1, i, n))
        )
    return out


def DOT(x, y, s=1, r=1):
    return [(x, y, s, r)]


def S(*parts):
    return [pt for part in parts for pt in part]


def at(cx, cy, rx, ry, ang):
    t = math.radians(ang)
    return cx + rx * math.cos(t), cy + ry * math.sin(t)


def geo(p):
    a, b = p.a, p.b
    X, C, A, D, ov, ovC = 570, 730, 780, -230, 10, 14
    return SimpleNamespace(
        a=a, b=b, X=X, C=C, A=A, D=D, ov=ov, ovC=ovC,
        yb=b, yx=X - b, yC=C - b, yA=A - b, yD=D + b,
        cy=X / 2, ry=X / 2 + ov - b, cyC=C / 2, ryC=C / 2 + ovC - b,
        # Natural proportions only: build.py rescales each glyph's skeleton to its width class (SPACING).
        wn=375,
        dot=1.0,  # terminal-ball scale (circle radius = dot * a); constant relative to the pen
        # Dot radius = scale * a. Each radius is linear in a (c0 + c1*a), so the two weight masters
        # interpolate it exactly; a scale linear in a would make the radius quadratic.
        idot=(31.6 + 0.539 * a) / a,  # i/j dot: radius 51 at 300, 92 at 900; top stays at the ascender
        igap=133 - 0.92 * a,  # x-height to the i-dot: 100 at 300, 30 at 900
        pdot=(24 + 0.75 * a) / a,  # period, comma, colon and quote balls: radius 51 at 300, 108 at 900
    )


# ---------------------------------------------------------------- shared parts


def _lc_nw(g):
    """Width of n/h/u (stem to stem)."""
    return g.wn + 0.4 * g.a


def n_arch(g, x0, w, s0=0.45):
    ya = 0.42 * g.X
    return S(ARC(x0 + w / 2, ya, w / 2, g.X + g.ov - g.b - ya, 165, 0, s0, 1), LN(x0 + w, ya, x0 + w, g.yb))


def u_cup(g, x0, w, s1=0.45):
    yu = 0.58 * g.X
    return S(LN(x0, g.yx, x0, yu), ARC(x0 + w / 2, yu, w / 2, yu - g.b + g.ov, 180, 360, 1, s1))


def _lc_rx(g):
    """Half-width of the lowercase bowls; grows with the pen so counters stay open at 900."""
    return g.wn / 2 + 10 + 0.25 * g.a


def bowl_right(g, x0, rx, cy, ry, sj=0.45):
    """Bowl attached to a stem on its left (b, p): full pen, tapering into the stem."""
    cx = x0 + rx
    return S(
        ARC(cx, cy, rx, ry, 125, 95, sj, 1),
        ARC(cx, cy, rx, ry, 95, -95)[1:],
        ARC(cx, cy, rx, ry, -95, -125, 1, sj)[1:],
    )


def bowl_left(g, xs, rx, cy, ry, sj=0.45):
    """Bowl attached to a stem on its right (a, d, g, q): full pen, tapering into the stem.

    The top neck keeps its top edge at the x-height all the way into the stem (the sample rises as the
    pen shrinks), so the join never shows a notch between the neck and the stem's cap, slanted or not.
    """
    cx = xs - rx
    return S(
        LN(xs - 0.5 * g.a, cy + ry + (1 - sj) * g.b, *at(cx, cy, rx, ry, 85), sj, 1),
        ARC(cx, cy, rx, ry, 85, 275)[1:],
        ARC(cx, cy, rx, ry, 275, 305, 1, sj)[1:],
    )


def hook_left(g, xs, ytop, rh, yh=-10):
    """Stem going down into a descender hook that curls left, ending in a ball clear of the bowl."""
    return S(LN(xs, ytop, xs, yh), ARC(xs - rh, yh, rh, yh - g.yD, 0, -140, 1, g.dot, 0, 1))


def tail_right(g, xs, ytop, rt, s0=1):
    """Stem coming down into a flick to the right (t, l)."""
    yt = g.yb + rt * 0.8
    return S(LN(xs, ytop, xs, yt, s0, 1), ARC(xs + rt, yt, rt, rt * 0.8, 180, 300, 1, 0.85, 0, 0.6))


def s_shape(g, cx, rx, top, bot, k=1.0):
    h = top - bot
    r4 = h / 4
    yl = bot + r4
    yu = yl + h / 2
    x0, y0 = at(cx, yu, rx * 0.95, r4, 245)
    x1, y1 = at(cx, yl, rx, r4, 65)
    return [
        S(
            ARC(cx, yu, rx * 0.95, r4, 30, 245, g.dot * 1.05 * k, 1, 0.8, 0),
            LN(x0, y0, x1, y1),
            ARC(cx, yl, rx, r4, 65, -150, 1, g.dot * 1.05 * k, 0, 0.8),
        )
    ]


# ---------------------------------------------------------------- lowercase


@glyph("a")
def _a(g):
    rx = _lc_rx(g)
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), tail_right(g, 2 * rx, g.yx, g.wn * 0.2)]


@glyph("b")
def _b(g):
    rx = _lc_rx(g)
    return [LN(0, g.yA, 0, g.yb), bowl_right(g, 0, rx, g.cy, g.ry)]


@glyph("c")
def _c(g):
    rx = _lc_rx(g) - 5
    return [
        S(
            ARC(rx, g.cy, rx, g.ry, 45, 180, g.dot * 1.05, 1, 0.8, 0),
            ARC(rx, g.cy, rx, g.ry, 180, 315, 1, g.dot * 1.05, 0, 0.8)[1:],
        )
    ]


@glyph("d")
def _d(g):
    rx = _lc_rx(g)
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), tail_right(g, 2 * rx, g.yA, g.wn * 0.2)]


@glyph("e")
def _e(g):
    rx = _lc_rx(g) + 5
    ybar = g.cy + 0.03 * g.X
    return [
        LN(0, ybar, 2 * rx, ybar, 0.65),
        S(ARC(rx, g.cy, rx, g.ry, 5, 200), ARC(rx, g.cy, rx, g.ry, 200, 315, 1, g.dot, 0, 0.8)[1:]),
    ]


@glyph("f")
def _f(g):
    rf = g.wn * 0.36
    yh = g.yA - rf * 0.8
    return [
        S(LN(0, g.yb, 0, yh), ARC(rf, yh, rf, rf * 0.8, 180, 45, 1, g.dot * 1.1, 0, 1)),
        LN(-g.wn * 0.22, g.yx, g.wn * 0.5, g.yx, 0.85),
    ]


@glyph("g")
def _g(g):
    rx = _lc_rx(g)
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), hook_left(g, 2 * rx, g.yx, rx * 0.95)]


@glyph("h")
def _h(g):
    return [LN(0, g.yA, 0, g.yb), n_arch(g, 0, _lc_nw(g))]


@glyph("i")
def _i(g):
    return [LN(0, g.yx, 0, g.yb), DOT(0, g.X + g.igap + g.idot * g.a, g.idot)]


@glyph("j")
def _j(g):
    return [hook_left(g, 0, g.yx, g.wn * 0.34), DOT(0, g.X + g.igap + g.idot * g.a, g.idot)]


@glyph("k")
def _k(g):
    w = g.wn * 0.92 + 0.2 * g.a
    return [
        LN(0, g.yA, 0, g.yb),
        LN(0, 0.3 * g.X, w, g.yx, 0.55, 1),
        LN(w * 0.3, 0.5 * g.X, w + 10, g.yb, 0.55, 1),
    ]


@glyph("l")
def _l(g):
    return [tail_right(g, 0, g.yA, g.wn * 0.28)]


@glyph("m")
def _m(g):
    w = g.wn * 0.72 + 0.9 * g.a
    return [LN(0, g.yx, 0, g.yb), n_arch(g, 0, w), n_arch(g, w, w)]


@glyph("n")
def _n(g):
    return [LN(0, g.yx, 0, g.yb), n_arch(g, 0, _lc_nw(g))]


@glyph("o")
def _o(g):
    rx = _lc_rx(g) + 10
    return [ARC(rx, g.cy, rx, g.ry, 0, 360)]


@glyph("p")
def _p(g):
    rx = _lc_rx(g)
    return [LN(0, g.yx, 0, g.yD), bowl_right(g, 0, rx, g.cy, g.ry)]


@glyph("q")
def _q(g):
    rx = _lc_rx(g)
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), LN(2 * rx, g.yx, 2 * rx, g.yD)]


@glyph("r")
def _r(g):
    rr = g.wn * 0.42
    ya = 0.4 * g.X
    return [
        LN(0, g.yx, 0, g.yb),
        ARC(rr, ya, rr, g.X + g.ov - g.b - ya, 165, 45, 0.45, g.dot * 1.15, 0, 1),
    ]


@glyph("s")
def _s(g):
    return s_shape(g, g.wn * 0.42, g.wn * 0.42, g.X + g.ov - g.b, g.b - g.ov)


@glyph("t")
def _t(g):
    return [tail_right(g, 0, g.X + 130 - g.b, g.wn * 0.3), LN(-g.wn * 0.25, g.yx, g.wn * 0.5, g.yx, 0.85)]


@glyph("u")
def _u(g):
    w = _lc_nw(g)
    return [u_cup(g, 0, w), tail_right(g, w, g.yx, g.wn * 0.2)]


@glyph("v")
def _v(g):
    w = g.wn * 1.05 + 0.3 * g.a
    return [S(LN(0, g.yx, w / 2, g.yb, 1, 0.85), LN(w / 2, g.yb, w, g.yx, 0.85, 1))]


@glyph("w")
def _w(g):
    w = g.wn * 1.6 + 0.5 * g.a
    return [
        S(
            LN(0, g.yx, w * 0.25, g.yb, 1, 0.8),
            LN(w * 0.25, g.yb, w * 0.5, g.yx * 0.8, 0.8, 0.8),
            LN(w * 0.5, g.yx * 0.8, w * 0.75, g.yb, 0.8, 0.8),
            LN(w * 0.75, g.yb, w, g.yx, 0.8, 1),
        )
    ]


@glyph("x")
def _x(g):
    w = g.wn * 0.98 + 0.3 * g.a
    return [LN(0, g.yx, w, g.yb), LN(0, g.yb, w, g.yx, 0.8)]


@glyph("y")
def _y(g):
    w = _lc_nw(g)
    return [u_cup(g, 0, w), hook_left(g, w, g.yx, g.wn * 0.5)]


@glyph("z")
def _z(g):
    w = g.wn * 0.88 + 0.3 * g.a
    return [S(LN(0, g.yx, w, g.yx), LN(w, g.yx, 0, g.yb, 1, 1.05), LN(0, g.yb, w, g.yb))]


# ---------------------------------------------------------------- uppercase


def d_bowl(g, x0, w, ytop, ybot):
    ry = (ytop - ybot) / 2
    rx = min(ry * 1.15, w * 0.8)
    xc = x0 + w - rx
    yc = (ytop + ybot) / 2
    return S(LN(x0, ytop, xc, ytop), ARC(xc, yc, rx, ry, 90, -90), LN(xc, ybot, x0, ybot))


@glyph("A")
def _A(g):
    w = g.wn * 1.3
    return [
        S(LN(0, g.yb, w / 2, g.yC, 1, 0.9), LN(w / 2, g.yC, w, g.yb, 0.9, 1)),
        LN(w * 0.22, 0.26 * g.C, w * 0.78, 0.26 * g.C, 0.78),
    ]


@glyph("B")
def _B(g):
    w = g.wn * 1.18
    ym = 0.55 * g.C
    return [LN(0, g.yC, 0, g.yb), d_bowl(g, 0, w * 0.86, g.yC, ym), d_bowl(g, 0, w, ym, g.yb)]


@glyph("C")
def _C(g):
    rx = g.wn * 0.68
    return [ARC(rx, g.cyC, rx, g.ryC, 45, 315, g.dot * 1.1, g.dot * 1.1, 0.7, 0.7)]


@glyph("D")
def _D(g):
    return [LN(0, g.yC, 0, g.yb), d_bowl(g, 0, g.wn * 1.25, g.yC, g.yb)]


@glyph("E")
def _E(g):
    w = g.wn * 0.95
    ym = 0.5 * g.C
    return [
        S(LN(w, g.yC, 0, g.yC), LN(0, g.yC, 0, g.yb), LN(0, g.yb, w, g.yb)),
        LN(0, ym, w * 0.82, ym, 0.82),
    ]


@glyph("F")
def _F(g):
    w = g.wn * 0.92
    ym = 0.48 * g.C
    return [S(LN(w, g.yC, 0, g.yC), LN(0, g.yC, 0, g.yb)), LN(0, ym, w * 0.82, ym, 0.82)]


@glyph("G")
def _G(g):
    rx = g.wn * 0.7
    ex, ey = at(rx, g.cyC, rx, g.ryC, 345)
    return [
        S(
            ARC(rx, g.cyC, rx, g.ryC, 45, 345, g.dot * 1.1, 1, 0.7, 0),
            LN(ex, ey, rx * 0.95, ey, 1, 0.85),
        )
    ]


@glyph("H")
def _H(g):
    w = g.wn * 1.2
    return [LN(0, g.yC, 0, g.yb), LN(w, g.yC, w, g.yb), LN(0, 0.5 * g.C, w, 0.5 * g.C)]


@glyph("I")
def _I(g):
    return [LN(0, g.yC, 0, g.yb)]


@glyph("J")
def _J(g):
    w = g.wn * 0.95
    rj = w / 2
    yj = 0.42 * g.C
    return [S(LN(w, g.yC, w, yj), ARC(w - rj, yj, rj, yj - g.b + g.ov, 0, -160, 1, g.dot * 1.1, 0, 1))]


@glyph("K")
def _K(g):
    w = g.wn * 1.1
    return [
        LN(0, g.yC, 0, g.yb),
        LN(0, 0.3 * g.C, w, g.yC, 0.55, 1),
        LN(w * 0.3, 0.5 * g.C, w + 10, g.yb, 0.55, 1),
    ]


@glyph("L")
def _L(g):
    return [S(LN(0, g.yC, 0, g.yb), LN(0, g.yb, g.wn * 0.9, g.yb))]


@glyph("M")
def _M(g):
    w = g.wn * 1.55
    return [
        LN(0, g.yb, 0, g.yC),
        S(LN(0, g.yC, w / 2, 0.32 * g.C, 0.8, 0.75), LN(w / 2, 0.32 * g.C, w, g.yC, 0.75, 0.8)),
        LN(w, g.yC, w, g.yb),
    ]


@glyph("N")
def _N(g):
    w = g.wn * 1.2
    ym = (g.yC + g.yb) / 2
    return [
        LN(0, g.yb, 0, g.yC),
        S(LN(0, g.yC, w / 2, ym, 0.75, 1), LN(w / 2, ym, w, g.yb, 1, 0.75)),
        LN(w, g.yb, w, g.yC),
    ]


@glyph("O")
def _O(g):
    rx = g.wn * 0.72
    return [ARC(rx, g.cyC, rx, g.ryC, 0, 360)]


@glyph("P")
def _P(g):
    return [LN(0, g.yC, 0, g.yb), d_bowl(g, 0, g.wn * 1.08, g.yC, 0.42 * g.C)]


@glyph("Q")
def _Q(g):
    rx = g.wn * 0.72
    return [
        ARC(rx, g.cyC, rx, g.ryC, 0, 360),
        LN(*at(rx, g.cyC, rx, g.ryC, 290), rx * 2.25, g.yb - 60, 0.85, 1, 0, 0.6),
    ]


@glyph("R")
def _R(g):
    w = g.wn * 1.1
    return [
        LN(0, g.yC, 0, g.yb),
        d_bowl(g, 0, w, g.yC, 0.44 * g.C),
        LN(w * 0.42, 0.44 * g.C, w + 15, g.yb, 0.72, 1),
    ]


@glyph("S")
def _S(g):
    return s_shape(g, g.wn * 0.52, g.wn * 0.52, g.C + g.ov - g.b, g.b - g.ov)


@glyph("T")
def _T(g):
    w = g.wn * 1.15
    return [LN(0, g.yC, w, g.yC), LN(w / 2, g.yC, w / 2, g.yb)]


@glyph("U")
def _U(g):
    w = g.wn * 1.2
    yu = 0.48 * g.C
    return [S(LN(0, g.yC, 0, yu), ARC(w / 2, yu, w / 2, yu - g.b + g.ov, 180, 360), LN(w, yu, w, g.yC))]


@glyph("V")
def _V(g):
    w = g.wn * 1.3
    return [S(LN(0, g.yC, w / 2, g.yb, 1, 0.85), LN(w / 2, g.yb, w, g.yC, 0.85, 1))]


@glyph("W")
def _W(g):
    w = g.wn * 1.95
    return [
        S(
            LN(0, g.yC, w * 0.25, g.yb, 1, 0.8),
            LN(w * 0.25, g.yb, w * 0.5, g.yC * 0.8, 0.8, 0.8),
            LN(w * 0.5, g.yC * 0.8, w * 0.75, g.yb, 0.8, 0.8),
            LN(w * 0.75, g.yb, w, g.yC, 0.8, 1),
        )
    ]


@glyph("X")
def _X(g):
    w = g.wn * 1.2
    return [LN(0, g.yC, w, g.yb), LN(0, g.yb, w, g.yC, 0.8)]


@glyph("Y")
def _Y(g):
    w = g.wn * 1.2
    ym = 0.45 * g.C
    return [S(LN(0, g.yC, w / 2, ym, 0.9, 1), LN(w / 2, ym, w / 2, g.yb)), LN(w, g.yC, w / 2, ym, 0.8)]


@glyph("Z")
def _Z(g):
    w = g.wn * 1.05
    return [S(LN(0, g.yC, w, g.yC), LN(w, g.yC, 0, g.yb, 1, 1.05), LN(0, g.yb, w, g.yb))]


# ---------------------------------------------------------------- figures


def fig_w(g):
    return g.wn * 0.95 + g.a * 0.3


@glyph("zero")
def _0(g):
    rx = fig_w(g) / 2
    return [ARC(rx, g.cyC, rx, g.ryC, 0, 360)]


@glyph("one")
def _1(g):
    w = fig_w(g)
    x = w * 0.62
    return [LN(x, g.yC, x, g.yb), LN(x, g.yC, w * 0.15, g.C * 0.75, 1, 0.75)]


@glyph("two")
def _2(g):
    w = fig_w(g)
    rx = w / 2
    r = g.C * 0.27
    cy = g.C + g.ov - g.b - r
    ex, ey = at(rx, cy, rx, r, -35)
    return [
        S(
            ARC(rx, cy, rx, r, 160, -35, g.dot * 1.1, 1, 0.8, 0),
            LN(ex, ey, 0, g.yb, 1, 1.05),
            LN(0, g.yb, w, g.yb),
        )
    ]


@glyph("three")
def _3(g):
    w = fig_w(g)
    top, bot = g.C + g.ov - g.b, g.b - g.ov
    ym = 0.55 * g.C
    ru, rl = (top - ym) / 2, (ym - bot) / 2
    return [
        S(
            ARC(w * 0.48, ym + ru, w * 0.46, ru, 155, -90, g.dot * 1.05, 0.8, 0.8, 0),
            ARC(w * 0.48, ym - rl, w * 0.52, rl, 90, -155, 0.8, g.dot * 1.05, 0, 0.8),
        )
    ]


@glyph("four")
def _4(g):
    w = fig_w(g) * 1.05
    x = w * 0.72
    y = 0.3 * g.C
    return [LN(x, g.yC, x, g.yb), S(LN(x, g.yC, 0, y, 0.85), LN(0, y, w, y))]


@glyph("five")
def _5(g):
    w = fig_w(g)
    top = g.yC
    rl = 0.31 * g.C
    yl = g.b - g.ov + rl
    sx, sy = at(w * 0.5, yl, w * 0.5, rl, 150)
    return [
        S(LN(w * 0.95, top, w * 0.12, top), LN(w * 0.12, top, w * 0.1, 0.52 * g.C), LN(w * 0.1, 0.52 * g.C, sx, sy)),
        ARC(w * 0.5, yl, w * 0.5, rl, 150, -155, 1, g.dot * 1.05, 0, 0.8),
    ]


@glyph("six")
def _6(g):
    w = fig_w(g)
    rx = w / 2
    rl = 0.31 * g.C
    yl = g.b - g.ov + rl
    return [
        ARC(rx, yl, rx, rl, 0, 360),
        ARC(rx * 1.6, yl, rx * 1.6, g.C + g.ov - g.b - yl, 72, 180, g.dot * 1.05, 1, 0.8, 0),
    ]


@glyph("seven")
def _7(g):
    w = fig_w(g)
    return [S(LN(0, g.yC, w, g.yC), LN(w, g.yC, w * 0.32, g.yb, 1, 1.05))]


@glyph("eight")
def _8(g):
    w = fig_w(g)
    top, bot = g.C + g.ov - g.b, g.b - g.ov
    ym = 0.56 * g.C
    ru, rl = (top - ym) / 2, (ym - bot) / 2
    return [ARC(w / 2, ym + ru, w * 0.43, ru, 0, 360), ARC(w / 2, ym - rl, w / 2, rl, 0, 360)]


@glyph("nine")
def _9(g):
    w = fig_w(g)
    rx = w / 2
    ru = 0.31 * g.C
    yu = g.C + g.ov - g.b - ru
    return [
        ARC(rx, yu, rx, ru, 0, 360),
        ARC(w - rx * 1.6, yu, rx * 1.6, yu - g.b + g.ov, 252, 360, g.dot * 1.05, 1, 0.8, 0),
    ]


# ---------------------------------------------------------------- punctuation


def ball(g, x, y, s=1.0):
    return DOT(x, y + 0, g.pdot * s)


@glyph("period")
def _period(g):
    return [ball(g, 0, g.pdot * g.a)]


def _gf_tail(g, x, y, flip=False):
    """Curved tail from a ball at (x, y): sweeps down and left (comma, quoteright) or, flipped, up and
    right (quoteleft). Starts at the ball's centre so the hull grows out of the ball."""
    r = g.pdot * g.a
    rt, rh = 0.9 * r, 1.9 * r
    s0, s1 = g.pdot * 0.6, g.pdot * 0.2
    if flip:
        return ARC(x + rt, y, rt, rh, 180, 75, s0, s1, 1, 1)
    return ARC(x - rt, y, rt, rh, 0, -105, s0, s1, 1, 1)


def _gf_tail_drop(g):
    """How far below the ball's centre the tail reaches (tip centre plus its radius)."""
    r = g.pdot * g.a
    return 1.9 * r * math.sin(math.radians(105)) + 0.2 * r


@glyph("comma")
def _comma(g):
    r = g.pdot * g.a
    return [S(ball(g, 0, r), _gf_tail(g, 0, r))]


@glyph("colon")
def _colon(g):
    r = g.pdot * g.a
    return [ball(g, 0, r), ball(g, 0, g.X - r)]


@glyph("semicolon")
def _semicolon(g):
    r = g.pdot * g.a
    return [S(ball(g, 0, r), _gf_tail(g, 0, r)), ball(g, 0, g.X - r)]


@glyph("exclam")
def _exclam(g):
    r = g.pdot * g.a
    return [LN(0, g.yC, 0, 2 * r + 120, 1.05, 0.7, 0.3, 0.3), ball(g, 0, r)]


@glyph("question")
def _question(g):
    r = g.pdot * g.a
    w = g.wn * 0.95
    rq = 0.2 * g.C
    yq = g.C + g.ov - g.b - rq
    return [
        S(ARC(w / 2, yq, w / 2, rq, 160, -90, g.pdot * 1.05, 1, 0.8, 0), LN(w / 2, yq - rq, w / 2, 2 * r + 120, 1, 0.8)),
        ball(g, w / 2, r),
    ]


def tick(g, x, ytop, flip=False):
    """A comma-shaped quote: a 9 (ball at top, tail curling down-left) or, flipped, a 6 (ball at the
    bottom, tail curling up-right). Both fill the same band from ytop down."""
    r = g.pdot * g.a
    if flip:
        yb = ytop - _gf_tail_drop(g)
        return S(DOT(x, yb, g.pdot), _gf_tail(g, x, yb, flip=True))
    return S(DOT(x, ytop - r, g.pdot), _gf_tail(g, x, ytop - r))


@glyph("quotesingle")
def _qs(g):
    return [LN(0, g.yC, 0, g.C - 230, 1, 0.7)]


@glyph("quotedbl")
def _qd(g):
    d = 2 * g.a + 60
    return [LN(0, g.yC, 0, g.C - 230, 1, 0.7), LN(d, g.yC, d, g.C - 230, 1, 0.7)]


@glyph("quoteright", 0x2019)
def _qr(g):
    return [tick(g, 0, g.C)]


@glyph("quoteleft", 0x2018)
def _ql(g):
    return [tick(g, 0, g.C, flip=True)]


@glyph("quotedblright", 0x201D)
def _qdr(g):
    d = 2 * g.a * g.pdot + 90
    return [tick(g, 0, g.C), tick(g, d, g.C)]


@glyph("quotedblleft", 0x201C)
def _qdl(g):
    d = 2 * g.a * g.pdot + 90
    return [tick(g, 0, g.C, flip=True), tick(g, d, g.C, flip=True)]


@glyph("hyphen")
def _hyphen(g):
    return [LN(0, 0.48 * g.X, g.wn * 0.55, 0.48 * g.X, 0.9)]


@glyph("endash", 0x2013)
def _endash(g):
    return [LN(0, 0.48 * g.X, g.wn * 1.1, 0.48 * g.X, 0.9)]


@glyph("emdash", 0x2014)
def _emdash(g):
    return [LN(0, 0.48 * g.X, g.wn * 2.2, 0.48 * g.X, 0.9)]


@glyph("underscore")
def _underscore(g):
    return [LN(0, -120, g.wn * 1.2, -120, 0.9)]


@glyph("parenleft")
def _pl(g):
    ry = (g.C + 150 - (g.D + 60)) / 2
    cy = (g.C + 150 + g.D + 60) / 2
    rx = g.wn * 0.9
    return [ARC(rx, cy, rx, ry, 118, 242, 0.85, 0.85, 0.3, 0.3, step=8)]


@glyph("parenright")
def _pr(g):
    ry = (g.C + 150 - (g.D + 60)) / 2
    cy = (g.C + 150 + g.D + 60) / 2
    rx = g.wn * 0.9
    return [ARC(0, cy, rx, ry, 62, -62, 0.85, 0.85, 0.3, 0.3, step=8)]


@glyph("bracketleft")
def _bl(g):
    w = g.wn * 0.45
    t, b = g.C + 110, g.D + 60
    return [S(LN(w, t, 0, t, 0.8), LN(0, t, 0, b, 0.9), LN(0, b, w, b, 0.8))]


@glyph("bracketright")
def _br(g):
    w = g.wn * 0.45
    t, b = g.C + 110, g.D + 60
    return [S(LN(0, t, w, t, 0.8), LN(w, t, w, b, 0.9), LN(w, b, 0, b, 0.8))]


@glyph("slash")
def _slash(g):
    return [LN(0, g.D + 80, g.wn * 0.95, g.C + 60, 0.85)]


@glyph("backslash")
def _backslash(g):
    return [LN(0, g.C + 60, g.wn * 0.95, g.D + 80, 0.85)]


@glyph("bar")
def _bar(g):
    return [LN(0, g.C + 110, 0, g.D + 60, 0.75)]


def _fig_op_w(g):
    return g.wn * 1.0 + g.a * 0.7


def _fig_op_y(g):
    return 0.46 * g.C


@glyph("plus")
def _plus(g):
    w = _fig_op_w(g)
    y = _fig_op_y(g)
    return [LN(0, y, w, y, 0.9), LN(w / 2, y - w / 2, w / 2, y + w / 2, 0.85)]


@glyph("minus", 0x2212)
def _minus(g):
    y = _fig_op_y(g)
    return [LN(0, y, _fig_op_w(g), y, 0.9)]


@glyph("equal")
def _equal(g):
    w = _fig_op_w(g)
    y = _fig_op_y(g)
    d = g.b * 0.9 + 60
    return [LN(0, y + d, w, y + d, 0.9), LN(0, y - d, w, y - d, 0.9)]


@glyph("less")
def _less(g):
    w = _fig_op_w(g) * 0.9
    y = _fig_op_y(g)
    return [S(LN(w, y + w * 0.6, 0, y, 0.85), LN(0, y, w, y - w * 0.6, 0.85))]


@glyph("greater")
def _greater(g):
    w = _fig_op_w(g) * 0.9
    y = _fig_op_y(g)
    return [S(LN(0, y + w * 0.6, w, y, 0.85), LN(w, y, 0, y - w * 0.6, 0.85))]


@glyph("asterisk")
def _asterisk(g):
    r = g.wn * 0.42 + g.a * 0.3
    cx, cy = r, g.C - r * 1.0
    out = []
    for ang in (90, 162, 234, 306, 18):
        x, y = at(cx, cy, r, r, ang)
        out.append(LN(cx, cy, x, y, 0.55, 0.6, 0, 1))
    return out


@glyph("numbersign")
def _numbersign(g):
    sc = 0.7
    sp = 2 * g.a * sc + 100
    lean = 120
    w = sp + lean
    t, b = g.C - 50, 50
    y1, y2 = 0.3 * g.C, 0.66 * g.C
    return [
        LN(0, b, lean, t, sc),
        LN(sp, b, sp + lean, t, sc),
        LN(-30, y1, w + 30, y1, sc),
        LN(30, y2, w + 60, y2, sc),
    ]


@glyph("percent")
def _percent(g):
    r = g.wn * 0.26 + g.a * 0.5
    w = 4 * r + 60
    ry = 0.19 * g.C
    return [
        ARC(r, g.C - ry - g.b, r, ry, 0, 360, 0.7),
        ARC(w - r, ry + g.b, r, ry, 0, 360, 0.7),
        LN(w * 0.18, g.b, w * 0.82, g.yC, 0.75),
    ]


@glyph("dollar")
def _dollar(g):
    rx = g.wn * 0.5
    return [*s_shape(g, rx, rx, g.C + g.ov - g.b - 40, g.b - g.ov + 40), LN(rx, -90, rx, g.C + 90, 0.55)]


@glyph("ampersand")
def _ampersand(g):
    w = g.wn * 1.3 + g.a * 1.3
    ru = 0.21 * g.C
    yu = g.C + g.ov - g.b - ru
    xu = w * 0.38
    rl = 0.27 * g.C
    yl = g.b - g.ov + rl
    rux = w * 0.22 + 0.3 * g.a  # the loop grows with the pen so its counter stays open at 900
    su = 0.82 - 0.0022 * g.a  # loop stroke at the junctions: 0.74 at 300, 0.57 at 900
    sx, sy = at(xu, yu, rux, ru, 230)
    ex, ey = at(w * 0.42, yl, w * 0.42, rl, 140)
    return [
        S(
            LN(w, g.yb, sx, sy, 1, su),
            ARC(xu, yu, rux, ru, 230, 90, su, 0.8),
            ARC(xu, yu, rux, ru, 90, -60, 0.8, su)[1:],
        ),
        S(
            ARC(w * 0.42, yl, w * 0.42, rl, 140, 340, 1, 0.9),
            LN(*at(w * 0.42, yl, w * 0.42, rl, 340), w * 1.02, 0.45 * g.C, 0.9, 0.9),
        ),
        LN(*at(xu, yu, rux, ru, -60), ex, ey, su, 1),
    ]


@glyph("at")
def _at(g):
    w = g.wn * 1.9 + g.a * 1.5
    R = w / 2
    cy = 0.37 * g.C
    ry = 0.42 * g.C
    rb = g.wn * 0.3 + g.a * 0.2  # inner bowl half-width
    rbv = rb * 1.1
    si = 0.557 - 0.00158 * g.a  # inner stroke: 0.5 at 300, 0.38 at 900, so the counter stays open
    cxi = R - 0.45 * rb
    xs = cxi + rb  # stem on the bowl's right edge, like the a
    rt = 0.42 * rb
    yt = cy - rbv * 0.55
    return [
        ARC(R, cy, R, ry, -20, 305, 0.7, 0.7),
        ARC(cxi, cy, rb, rbv, 0, 360, si),
        S(LN(xs, cy + rbv * 0.8, xs, yt, si), ARC(xs + rt, yt, rt, rt * 0.8, 180, 270, si, si * 0.9)),
    ]


@glyph("ellipsis", 0x2026)
def _ellipsis(g):
    r = g.pdot * g.a
    d = 2 * r + 70
    return [ball(g, 0, r), ball(g, d, r), ball(g, 2 * d, r)]


@glyph("bullet", 0x2022)
def _bullet(g):
    return [DOT(0, 0.48 * g.X, g.pdot * 1.15)]


@glyph("periodcentered", 0x00B7)
def _middot(g):
    return [ball(g, 0, 0.48 * g.X - g.pdot * g.a)]


@glyph("asciitilde")
def _tilde(g):
    w = _fig_op_w(g) * 1.1
    y = 0.5 * g.C
    h = 25 + g.b * 0.9
    return [S(ARC(w * 0.25, y, w * 0.25, h, 180, 0, 0.7), ARC(w * 0.75, y, w * 0.25, h, 180, 360, 0.7))]


@glyph("braceleft")
def _bracel(g):
    w = g.wn * 0.5
    t, b = g.C + 110, g.D + 60
    m = (t + b) / 2
    return [
        S(LN(w, t, w * 0.5, t, 0.8), LN(w * 0.5, t, w * 0.5, m + 60, 0.85), LN(w * 0.5, m + 60, 0, m, 0.85)),
        S(LN(0, m, w * 0.5, m - 60, 0.85), LN(w * 0.5, m - 60, w * 0.5, b, 0.85), LN(w * 0.5, b, w, b, 0.8)),
    ]


@glyph("braceright")
def _bracer(g):
    w = g.wn * 0.5
    t, b = g.C + 110, g.D + 60
    m = (t + b) / 2
    return [
        S(LN(0, t, w * 0.5, t, 0.8), LN(w * 0.5, t, w * 0.5, m + 60, 0.85), LN(w * 0.5, m + 60, w, m, 0.85)),
        S(LN(w, m, w * 0.5, m - 60, 0.85), LN(w * 0.5, m - 60, w * 0.5, b, 0.85), LN(w * 0.5, b, 0, b, 0.8)),
    ]


@glyph("asciicircum")
def _circum(g):
    w = g.wn * 0.9
    return [S(LN(0, g.C - 280, w / 2, g.yC, 0.8), LN(w / 2, g.yC, w, g.C - 280, 0.8))]


@glyph("grave")
def _grave(g):
    return [LN(0, g.C, 120, g.C - 130, 0.8, 0.6, 1, 0.5)]


@glyph("sterling", 0x00A3)
def _sterling(g):
    w = g.wn * 1.05
    rx = w * 0.38
    ry = 0.22 * g.C
    yh = g.C + g.ov - g.b - ry
    return [
        S(ARC(w * 0.2 + rx, yh, rx, ry, 20, 180, g.dot * 1.05, 1, 0.8, 0), LN(w * 0.2, yh, w * 0.2, g.b * 1.6), LN(w * 0.2, g.b * 1.6, 0, g.yb), LN(0, g.yb, w, g.yb)),
        LN(-w * 0.05, 0.42 * g.C, w * 0.6, 0.42 * g.C, 0.8),
    ]


@glyph("Euro", 0x20AC)
def _euro(g):
    rx = g.wn * 0.62
    x0 = 70
    return [
        ARC(x0 + rx, g.cyC, rx, g.ryC, 45, 315, g.dot * 1.05, g.dot * 1.05, 0.7, 0.7),
        LN(0, 0.58 * g.C, x0 + rx * 1.05, 0.58 * g.C, 0.7),
        LN(0, 0.4 * g.C, x0 + rx * 1.0, 0.4 * g.C, 0.7),
    ]


# Spacing system (see docs/consistency.md). Per glyph: (width class r, left side, right side).
# r = advance / n-advance; build.py scales the skeleton (not the pen) horizontally to hit it.
# Sides are multiples of the straight sidebearing: 1 straight, R round, D diagonal. A ("T", ratio) side has a
# tail or hook: it is measured only inside the x-height (caps: cap-height) band, so the tail overhangs.
# Glyphs not listed keep their drawn width with PUNCT_SIDE sidebearings.
R, D = 0.7, 0.35
T, TR = ("T", 1.0), ("T", 0.7)
SPACING = {
    # lowercase
    "a": (1.00, R, T), "b": (1.00, 1, R), "c": (0.85, R, R), "d": (1.00, R, T), "e": (0.95, R, R),
    "f": (0.75, 0.2, ("T", 0.3)), "g": (0.95, TR, 1), "h": (1.00, 1, 1), "i": (0.50, 1, 1), "j": (0.50, T, 1),
    "k": (0.95, 1, D), "l": (0.50, 1, T), "m": (1.45, 1, 1), "n": (1.00, 1, 1), "o": (1.00, R, R),
    "p": (1.00, 1, R), "q": (1.00, R, 1), "r": (0.80, 1, D), "s": (0.85, 0.62, 0.62), "t": (0.75, 0.34, ("T", 0.5)),
    "u": (1.00, 1, T), "v": (0.95, D, D), "w": (1.36, D, D), "x": (0.90, D, D), "y": (0.95, T, 1),
    "z": (0.85, 0.8, 0.8),
    # uppercase
    "A": (1.08, D, D), "B": (1.08, 1, 0.66), "C": (1.00, R, R), "D": (1.15, 1, R), "E": (0.92, 1, 0.8),
    "F": (0.92, 1, 0.8), "G": (1.15, R, 0.8), "H": (1.15, 1, 1), "I": (0.52, 1, 1), "J": (0.92, 0.45, 1),
    "K": (1.08, 1, D), "L": (0.92, 1, 0.6), "M": (1.37, 1, 1), "N": (1.15, 1, 1), "O": (1.15, R, R),
    "P": (1.00, 1, 0.47), "Q": (1.15, R, TR), "R": (1.08, 1, 0.44), "S": (1.00, 0.62, 0.62), "T": (1.00, 0.5, 0.5),
    "U": (1.15, 1, 1), "V": (1.08, D, D), "W": (1.55, D, D), "X": (1.15, D, D), "Y": (1.08, D, D),
    "Z": (1.00, 0.8, 0.8),
    # figures (proportional)
    "zero": (0.96, R, R), "one": (0.67, 0.5, 1), "two": (0.92, R, 0.8), "three": (0.92, 0.6, R),
    "four": (0.96, 0.5, 1), "five": (0.92, 0.8, R), "six": (0.96, R, R), "seven": (0.92, 0.6, 0.5),
    "eight": (0.96, R, R), "nine": (0.96, R, R),
    # accented letters with their own shapes; i and I composites measure only the stem (marks overhang)
    "AE": (1.45, D, 0.8), "OE": (1.50, R, 0.8), "Oslash": (1.15, R, R), "Eth": (1.18, 0.4, R),
    "Dcroat": (1.18, 0.4, R), "Thorn": (1.00, 1, 0.47), "Lslash": (0.95, 0.4, 0.6),
    "ae": (1.45, R, R), "oe": (1.55, R, R), "oslash": (1.00, R, R), "eth": (1.00, R, R), "thorn": (1.00, 1, R),
    "germandbls": (1.00, 1, R), "lslash": (0.55, 0.4, T), "dotlessi": (0.50, 1, 1),
    "igrave": (0.50, T, T), "iacute": (0.50, T, T), "icircumflex": (0.50, T, T), "idieresis": (0.50, T, T),
    "Igrave": (0.52, T, T), "Iacute": (0.52, T, T), "Icircumflex": (0.52, T, T), "Idieresis": (0.52, T, T),
}
PUNCT_SIDE = 0.8
# Composite glyphs (accented letters) space like their base letter: {"eacute": "e", ...}.
BASE_OF: dict[str, str] = {
    "Agrave": "A", "Aacute": "A", "Acircumflex": "A", "Atilde": "A", "Adieresis": "A", "Aring": "A", "Aogonek": "A",
    "Cacute": "C", "Ccaron": "C", "Ccedilla": "C",
    "Dcaron": "D",
    "Egrave": "E", "Eacute": "E", "Ecircumflex": "E", "Edieresis": "E", "Ecaron": "E", "Eogonek": "E",
    "Igrave": "I", "Iacute": "I", "Icircumflex": "I", "Idieresis": "I",
    "Lcaron": "L",
    "Nacute": "N", "Ntilde": "N", "Ncaron": "N",
    "Ograve": "O", "Oacute": "O", "Ocircumflex": "O", "Otilde": "O", "Odieresis": "O", "Ohungarumlaut": "O",
    "Racute": "R", "Rcaron": "R",
    "Sacute": "S", "Scaron": "S",
    "Tcaron": "T",
    "Ugrave": "U", "Uacute": "U", "Ucircumflex": "U", "Udieresis": "U", "Uring": "U", "Uhungarumlaut": "U",
    "Yacute": "Y", "Ydieresis": "Y",
    "Zacute": "Z", "Zcaron": "Z", "Zdotaccent": "Z",
    "agrave": "a", "aacute": "a", "acircumflex": "a", "atilde": "a", "adieresis": "a", "aring": "a", "aogonek": "a",
    "cacute": "c", "ccaron": "c", "ccedilla": "c",
    "dcaron": "d", "dcroat": "d",
    "egrave": "e", "eacute": "e", "ecircumflex": "e", "edieresis": "e", "ecaron": "e", "eogonek": "e",
    "igrave": "i", "iacute": "i", "icircumflex": "i", "idieresis": "i",
    "lcaron": "l",
    "nacute": "n", "ntilde": "n", "ncaron": "n",
    "ograve": "o", "oacute": "o", "ocircumflex": "o", "otilde": "o", "odieresis": "o", "ohungarumlaut": "o",
    "racute": "r", "rcaron": "r",
    "sacute": "s", "scaron": "s",
    "tcaron": "t",
    "ugrave": "u", "uacute": "u", "ucircumflex": "u", "udieresis": "u", "uring": "u", "uhungarumlaut": "u",
    "yacute": "y", "ydieresis": "y",
    "zacute": "z", "zcaron": "z", "zdotaccent": "z",
}


# ---------------------------------------------------------------- accents
# Marks are strokes of the same pen at a smaller scale (radius linear in a, like the dots). Each sits in an ink
# band above the x-height (lowercase) or a flatter, lower one above the cap height (capitals), centred on the
# base's optical middle. Composites call the base glyph's function and append the mark strokes.


def _ac_zone(g, cap, narrow=False):
    """Mark geometry: skeleton band (lo, hi), pen radius r, scale s, half-width hw, dot radius rd."""
    k = 0.85 if cap else 1.0
    r = k * (6.7 + 0.618 * g.a)  # mark pen radius: 29 at 300, 76 at 900 (lowercase)
    if cap:
        bot, top = g.C + 90 - 0.6 * g.a, 900 + 0.2 * g.a
        hw = 95 + 0.5 * g.a
    else:
        bot, top = g.X + 118 - 0.8 * g.a, 810 + 0.1 * g.a
        hw = 80 + 0.5 * g.a
    lo, hi = bot + r, top - r
    rd = (0.88 if cap else 1.0) * (27.1 + 0.526 * g.a)  # dieresis/dot radius: 46 at 300, 86 at 900
    if narrow:  # over a lone stem (i, I): marks stay close to its width
        hw, rd = hw * 0.72, rd * 0.85
    return SimpleNamespace(
        lo=lo, hi=hi, mid=(lo + hi) / 2, bot=bot, top=top, r=r, s=r / g.a, hw=hw, rd=rd, narrow=narrow, cap=cap
    )


def _ac_acute(g, cx, z, flip=False):
    d = -1 if flip else 1
    w = 0.32 * z.hw
    return [LN(cx - d * w, z.lo, cx + d * w, z.hi, z.s * 0.75, z.s * 1.05, 0.4, 1)]


def _ac_grave(g, cx, z):
    return _ac_acute(g, cx, z, flip=True)


def _ac_circumflex(g, cx, z, flip=False):
    y0, y1 = (z.hi, z.lo) if flip else (z.lo, z.hi)
    s = z.s * 0.9
    return [S(LN(cx - z.hw, y0, cx, y1, s, s, 0.7, 0.4), LN(cx, y1, cx + z.hw, y0, s, s, 0.4, 0.7))]


def _ac_caron(g, cx, z):
    return _ac_circumflex(g, cx, z, flip=True)


def _ac_tilde(g, cx, z):
    w = z.hw * 1.05
    h = (z.hi - z.lo) / 2 + 6
    s = z.s * 0.85
    return [
        S(
            ARC(cx - w / 2, z.mid, w / 2, h, 180, 0, s, s, 0.8, 0.3),
            ARC(cx + w / 2, z.mid, w / 2, h, 180, 360, s, s, 0.3, 0.8)[1:],
        )
    ]


def _ac_dieresis(g, cx, z):
    y = max(z.bot + z.rd, (z.bot + z.top) / 2 - 8)
    d = z.rd + (8 + 0.1 * g.a if z.narrow else 18 + 0.15 * g.a)
    return [DOT(cx - d, y, z.rd / g.a), DOT(cx + d, y, z.rd / g.a)]


def _ac_dotaccent(g, cx, z):
    r = z.rd * 1.05
    return [DOT(cx, max(z.bot + r, (z.bot + z.top) / 2 - 8), r / g.a)]


def _ac_ring(g, cx, z):
    s = z.s * 0.62
    bot, top = (z.bot, z.top + 10) if z.cap else (z.bot - 4, z.top + 20)  # a ring needs height for its counter
    ry = (top - bot) / 2 - s * g.b
    rx = ry * 0.6 + 40 + 0.15 * g.a
    return [ARC(cx, (bot + top) / 2, rx, ry, 90, 450, s, s, 0.3, 0.3)]


def _ac_macron(g, cx, z):
    return [LN(cx - z.hw * 0.85, z.mid, cx + z.hw * 0.85, z.mid, z.s * 0.85, z.s * 0.85, 0.6, 0.6)]


def _ac_hungarumlaut(g, cx, z):
    d = 0.42 * z.hw
    return [*_ac_acute(g, cx - d, z), *_ac_acute(g, cx + d, z)]


def _ac_cedilla(g, cx, z):
    s = z.s * 0.85
    rh = 38 + 0.35 * g.a
    yc = -95 - 0.3 * g.a
    return [S(LN(cx - 8, 40, cx + 6, yc + rh * 0.55, s, s), ARC(cx - 10, yc, rh, rh * 0.75, 50, -150, s, z.s * 1.05, 0, 1))]


def _ac_ogonek(g, cx, z):
    """Hook hanging from the base's bottom at cx, curling left and back right."""
    s = z.s * 0.85
    ro = 45 + 0.35 * g.a
    yo = -100 - 0.25 * g.a
    return [ARC(cx, yo, ro, -yo + 30, 90, 300, s, z.s * 1.05, 0, 1)]


def _ac_commacaron(g, x, ytop):
    """The caron of ď ľ ť Ľ: a small comma beside the stem's top."""
    r = 1.15 * _ac_zone(g, False).r
    x += r
    # The tail stays above the x-height, so spacing's x-height band ignores the comma.
    return [S(DOT(x, ytop - r, r / g.a), [(x - 0.1 * r, ytop - 2 * r - 60 + 0.5 * g.a, 0.35 * r / g.a, 1)])]


_AC_DRAW = {
    "grave": _ac_grave, "acute": _ac_acute, "circumflex": _ac_circumflex, "caron": _ac_caron,
    "tilde": _ac_tilde, "dieresis": _ac_dieresis, "dotaccent": _ac_dotaccent, "ring": _ac_ring,
    "macron": _ac_macron, "hungarumlaut": _ac_hungarumlaut, "cedilla": _ac_cedilla, "ogonek": _ac_ogonek,
}


def _ac_xspan(strokes):
    xs = [x for st in strokes for x, *_ in st]
    return min(xs), max(xs)


# A base's optical middle where the skeleton extent misleads (tails, hooks, open sides).
_AC_MID = {
    "a": lambda g: _lc_rx(g),
    "u": lambda g: _lc_nw(g) / 2,
    "y": lambda g: _lc_nw(g) / 2,
    "c": lambda g: (_lc_rx(g) - 5) * 0.95,
    "C": lambda g: g.wn * 0.68 * 0.95,
    "r": lambda g: g.wn * 0.42 * 0.75,
    "dotlessi": lambda g: 0,
    "I": lambda g: 0,
}
# Where an ogonek hangs from (x of its top).
_AC_FOOT = {
    "a": lambda g: 2 * _lc_rx(g) + 10,
    "e": lambda g: 1.5 * (_lc_rx(g) + 5),
    "A": lambda g: g.wn * 1.3 - 30,
    "E": lambda g: g.wn * 0.75,
}


def _ac_composite(base, mark):
    def fn(g):
        strokes = GLYPHS[base][1](g)
        mid = _AC_MID.get(base)
        cx = mid(g) if mid else sum(_ac_xspan(strokes)) / 2
        z = _ac_zone(g, base[0].isupper(), base in ("dotlessi", "I"))
        if mark == "ogonek":
            cx = _AC_FOOT[base](g)
        return [*strokes, *_AC_DRAW[mark](g, cx, z)]

    return fn


def _ac_comma_composite(base):
    def fn(g):
        strokes = GLYPHS[base][1](g)
        if base == "d":
            x, top = 2 * _lc_rx(g), g.A
        elif base == "L":
            x, top = 0, g.C
        else:  # l, t
            x, top = 0, g.A
        return [*strokes, *_ac_commacaron(g, x + g.a + 25, top)]

    return fn


@glyph("dotlessi")
def _dotlessi(g):
    return [LN(0, g.yx, 0, g.yb)]


# mark -> bases ("i" means the dotless i). Names are base + mark (AGL), e.g. Aacute, idieresis.
_AC_SETS = {
    "grave": "AEIOUaeiou",
    "acute": "AEIOUYaeiouyCcNnRrSsZz",
    "circumflex": "AEIOUaeiou",
    "tilde": "ANOano",
    "dieresis": "AEIOUYaeiouy",
    "ring": "AaUu",
    "caron": "CcDEeNnRrSsTZz",
    "cedilla": "Cc",
    "ogonek": "AaEe",
    "dotaccent": "Zz",
    "hungarumlaut": "OoUu",
}
for _mark, _bases in _AC_SETS.items():
    for _b in _bases:
        _name = _b + _mark
        GLYPHS[_name] = (ord(toUnicode(_name)), _ac_composite("dotlessi" if _b == "i" else _b, _mark))
for _b in "dltL":
    GLYPHS[_b + "caron"] = (ord(toUnicode(_b + "caron")), _ac_comma_composite(_b))


# Spacing marks: the lowercase variant, centred on 0.
def _ac_spacing(mark):
    def fn(g):
        return _AC_DRAW[mark](g, 0, _ac_zone(g, False))

    return fn


for _mark in ("acute", "dieresis", "cedilla", "ring", "macron", "caron", "dotaccent", "ogonek", "hungarumlaut"):
    GLYPHS[_mark] = (ord(toUnicode(_mark)), _ac_spacing(_mark))


# Letters with their own shapes.


@glyph("AE")
def _AE(g):
    wa, we = g.wn * 0.72, g.wn * 0.78
    ym = 0.5 * g.C
    return [
        LN(0, g.yb, wa, g.yC, 1, 0.9),
        S(LN(wa + we, g.yC, wa, g.yC), LN(wa, g.yC, wa, g.yb), LN(wa, g.yb, wa + we, g.yb)),
        LN(wa, ym, wa + we * 0.82, ym, 0.82),
        LN(wa * 0.3, 0.26 * g.C, wa, 0.26 * g.C, 0.78),
    ]


@glyph("ae")
def _ae(g):
    # Single-storey a: its straight stem tells æ from œ, so the e springs from the stem instead of rounding it.
    rx = _lc_rx(g) * 0.88
    xs = 2 * rx
    re = _lc_rx(g) * 0.88 + 5
    xe = xs + re * 0.8
    ybar = g.cy + 0.03 * g.X
    return [
        bowl_left(g, xs, rx, g.cy, g.ry),
        LN(xs, g.yx, xs, g.yb),
        LN(xs, ybar, xe + re, ybar, 0.65),
        ARC(xe, g.cy, re, g.ry, 5, 125, 1, 0.6),
        ARC(xe, g.cy, re, g.ry, 235, 315, 0.6, g.dot, 0, 0.8),
    ]


@glyph("OE")
def _OE(g):
    rx = g.wn * 0.6
    xe = rx * 1.5
    we = g.wn * 0.72
    ry = g.ryC - g.ovC
    ym = 0.5 * g.C
    return [
        S(LN(xe + we, g.yC, rx, g.yC), ARC(rx, g.cyC, rx, ry, 90, 270), LN(rx, g.yb, xe + we, g.yb)),
        LN(xe, g.yC, xe, g.yb),
        LN(xe, ym, xe + we * 0.82, ym, 0.82),
    ]


@glyph("oe")
def _oe(g):
    ro = _lc_rx(g) + 5
    re = _lc_rx(g) + 5
    xe = 2 * ro + re - 0.3 * g.a
    ybar = g.cy + 0.03 * g.X
    return [
        ARC(ro, g.cy, ro, g.ry, 0, 360),
        LN(xe - re, ybar, xe + re, ybar, 0.65),
        S(ARC(xe, g.cy, re, g.ry, 5, 200), ARC(xe, g.cy, re, g.ry, 200, 315, 1, g.dot, 0, 0.8)[1:]),
    ]


@glyph("Oslash")
def _Oslash(g):
    rx = g.wn * 0.72
    return [*_O(g), LN(rx * 0.1, g.yb - 50, rx * 1.9, g.yC + 50, 0.72)]


@glyph("oslash")
def _oslash(g):
    rx = _lc_rx(g) + 10
    return [*_o(g), LN(rx * 0.06, g.yb - 60, rx * 1.94, g.yx + 60, 0.72)]


def _ac_eth_bar(g):
    return LN(-g.wn * 0.2, 0.5 * g.C, g.wn * 0.36, 0.5 * g.C, 0.8)


@glyph("Eth")
def _Eth(g):
    return [*_D(g), _ac_eth_bar(g)]


@glyph("Dcroat")
def _Dcroat(g):
    return [*_D(g), _ac_eth_bar(g)]


@glyph("dcroat")
def _dcroat(g):
    xs = 2 * _lc_rx(g)
    y = (g.X + g.A) / 2 + 20
    return [*_d(g), LN(xs - g.wn * 0.26, y, xs + g.wn * 0.2, y, 0.8)]


@glyph("eth")
def _eth(g):
    rx = _lc_rx(g)
    x0 = rx * 0.3
    rys = g.yA - g.cy
    px, py = at(x0, g.cy, 2 * rx - x0, rys, 60)
    return [
        ARC(rx, g.cy, rx, g.ry, 0, 360),
        ARC(x0, g.cy, 2 * rx - x0, rys, 0, 110, 0.9, g.dot, 0, 0.8),
        LN(px - g.wn * 0.27, py - 40, px + g.wn * 0.3, py + 45, 0.62),
    ]


@glyph("Thorn")
def _Thorn(g):
    return [LN(0, g.yC, 0, g.yb), d_bowl(g, 0, g.wn * 1.0, 0.8 * g.C, 0.2 * g.C)]


@glyph("thorn")
def _thorn(g):
    return [LN(0, g.yA, 0, g.yD), bowl_right(g, 0, _lc_rx(g), g.cy, g.ry)]


@glyph("germandbls")
def _germandbls(g):
    ru, rl = g.wn * 0.3 + 0.2 * g.a, g.wn * 0.42 + 0.2 * g.a
    ym = 0.6 * g.X + 90
    top = g.A + g.ov - g.b
    hu = (top - ym) / 2
    hl = (ym - (g.b - g.ov)) / 2
    cl = ru + 0.12 * g.wn
    return [
        S(LN(0, g.yb, 0, ym + hu), ARC(ru, ym + hu, ru, hu, 180, -90)[1:]),
        S(LN(ru, ym, cl, ym), ARC(cl, ym - hl, rl, hl, 90, -125, 1, g.dot * 1.05, 0, 0.8)),
    ]


@glyph("Lslash")
def _Lslash(g):
    return [*_L(g), LN(-g.wn * 0.16, 0.34 * g.C, g.wn * 0.3, 0.6 * g.C, 0.72)]


@glyph("lslash")
def _lslash(g):
    return [*_l(g), LN(-g.wn * 0.2, 0.4 * g.A, g.wn * 0.22, 0.62 * g.A, 0.72)]


@glyph("multiply")
def _multiply(g):
    w = _fig_op_w(g) * 0.78
    y = _fig_op_y(g)
    return [LN(0, y - w / 2, w, y + w / 2, 0.85), LN(0, y + w / 2, w, y - w / 2, 0.85)]


@glyph("divide")
def _divide(g):
    w = _fig_op_w(g)
    y = _fig_op_y(g)
    r = g.pdot * 0.8
    d = r * g.a + g.b * 0.9 + 50
    return [LN(0, y, w, y, 0.9), DOT(w / 2, y + d, r), DOT(w / 2, y - d, r)]
