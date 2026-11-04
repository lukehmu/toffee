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
    X, C, A, D, ov = 540, 730, 780, -230, 10
    return SimpleNamespace(
        a=a, b=b, X=X, C=C, A=A, D=D, ov=ov,
        yb=b, yx=X - b, yC=C - b, yA=A - b, yD=D + b,
        cy=X / 2, ry=X / 2 + ov - b, cyC=C / 2, ryC=C / 2 + ov - b,
        wn=200 + 1.6 * a,
        dot=0.62 + 0.0035 * a,  # dot/ball scale (circle radius = dot * a)
    )


# ---------------------------------------------------------------- shared parts


def n_arch(g, x0, w, s0=0.45):
    ya = 0.42 * g.X
    return S(ARC(x0 + w / 2, ya, w / 2, g.X + g.ov - g.b - ya, 165, 0, s0, 1), LN(x0 + w, ya, x0 + w, g.yb))


def u_cup(g, x0, w, s1=0.45):
    yu = 0.58 * g.X
    return S(LN(x0, g.yx, x0, yu), ARC(x0 + w / 2, yu, w / 2, yu - g.b + g.ov, 180, 360, 1, s1))


def bowl_right(g, x0, rx, cy, ry):
    """Bowl attached to a stem on its left (b, p)."""
    return ARC(x0 + rx, cy, rx, ry, 125, -125, 0.5, 0.5)


def bowl_left(g, xs, rx, cy, ry):
    """Bowl attached to a stem on its right (a, d, g, q)."""
    return ARC(xs - rx, cy, rx, ry, 55, 305, 0.5, 0.5)


def hook_left(g, xs, ytop, rh, yh=-30):
    """Stem going down into a descender hook that curls left, ending in a ball."""
    return S(LN(xs, ytop, xs, yh), ARC(xs - rh, yh, rh, yh - g.yD, 0, -165, 1, g.dot * 1.15, 0, 1))


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
    rx = g.wn / 2 + 10
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), tail_right(g, 2 * rx, g.yx, g.wn * 0.28)]


@glyph("b")
def _b(g):
    rx = g.wn / 2 + 10
    return [LN(0, g.yA, 0, g.yb), bowl_right(g, 0, rx, g.cy, g.ry)]


@glyph("c")
def _c(g):
    rx = g.wn / 2 + 5
    return [ARC(rx, g.cy, rx, g.ry, 45, 315, g.dot * 1.1, g.dot * 1.1, 0.7, 0.7)]


@glyph("d")
def _d(g):
    rx = g.wn / 2 + 10
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), tail_right(g, 2 * rx, g.yA, g.wn * 0.28)]


@glyph("e")
def _e(g):
    rx = g.wn / 2 + 15
    ybar = g.cy + 0.04 * g.X
    return [LN(0, ybar, 2 * rx, ybar, 0.8), ARC(rx, g.cy, rx, g.ry, 5, 320, 1, g.dot * 1.1, 0, 0.6)]


@glyph("f")
def _f(g):
    rf = g.wn * 0.36
    yh = g.yA - rf * 0.8
    return [
        S(LN(0, g.yb, 0, yh), ARC(rf, yh, rf, rf * 0.8, 180, 30, 1, g.dot * 1.1, 0, 1)),
        LN(-g.wn * 0.22, g.yx, g.wn * 0.55, g.yx, 0.85),
    ]


@glyph("g")
def _g(g):
    rx = g.wn / 2 + 10
    return [bowl_left(g, 2 * rx, rx, g.cy, g.ry), hook_left(g, 2 * rx, g.yx, rx * 0.95)]


@glyph("h")
def _h(g):
    return [LN(0, g.yA, 0, g.yb), n_arch(g, 0, g.wn)]


@glyph("i")
def _i(g):
    return [LN(0, g.yx, 0, g.yb), DOT(0, g.X + 50 + g.dot * g.a, g.dot)]


@glyph("j")
def _j(g):
    return [hook_left(g, 0, g.yx, g.wn * 0.42), DOT(0, g.X + 50 + g.dot * g.a, g.dot)]


@glyph("k")
def _k(g):
    w = g.wn * 0.92
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
    w = g.wn * 0.8
    return [LN(0, g.yx, 0, g.yb), n_arch(g, 0, w), n_arch(g, w, w)]


@glyph("n")
def _n(g):
    return [LN(0, g.yx, 0, g.yb), n_arch(g, 0, g.wn)]


@glyph("o")
def _o(g):
    rx = g.wn / 2 + 20
    return [ARC(rx, g.cy, rx, g.ry, 0, 360)]


@glyph("p")
def _p(g):
    rx = g.wn / 2 + 10
    return [LN(0, g.yx, 0, g.yD), bowl_right(g, 0, rx, g.cy, g.ry)]


@glyph("q")
def _q(g):
    rx = g.wn / 2 + 10
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
    return [u_cup(g, 0, g.wn), tail_right(g, g.wn, g.yx, g.wn * 0.28)]


@glyph("v")
def _v(g):
    w = g.wn * 1.05
    return [S(LN(0, g.yx, w / 2, g.yb, 1, 0.85), LN(w / 2, g.yb, w, g.yx, 0.85, 1))]


@glyph("w")
def _w(g):
    w = g.wn * 1.6
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
    w = g.wn * 0.98
    return [LN(0, g.yx, w, g.yb), LN(0, g.yb, w, g.yx, 0.8)]


@glyph("y")
def _y(g):
    return [u_cup(g, 0, g.wn), hook_left(g, g.wn, g.yx, g.wn * 0.5)]


@glyph("z")
def _z(g):
    w = g.wn * 0.88
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
        LN(w * 0.24, 0.3 * g.C, w * 0.76, 0.3 * g.C, 0.85),
    ]


@glyph("B")
def _B(g):
    w = g.wn * 1.08
    ym = 0.54 * g.C
    return [LN(0, g.yC, 0, g.yb), d_bowl(g, 0, w * 0.9, g.yC, ym), d_bowl(g, 0, w, ym, g.yb)]


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
        LN(0, ym, w * 0.85, ym),
    ]


@glyph("F")
def _F(g):
    w = g.wn * 0.92
    ym = 0.48 * g.C
    return [S(LN(w, g.yC, 0, g.yC), LN(0, g.yC, 0, g.yb)), LN(0, ym, w * 0.85, ym)]


@glyph("G")
def _G(g):
    rx = g.wn * 0.7
    yb = 0.45 * g.C
    return [
        ARC(rx, g.cyC, rx, g.ryC, 45, 360, g.dot * 1.1, 1, 0.7, 0),
        LN(rx * 1.05, yb, 2 * rx, yb, 0.85),
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
    return [LN(0, g.yb, 0, g.yC), LN(0, g.yC, w, g.yb, 0.9), LN(w, g.yb, w, g.yC)]


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
        LN(rx * 1.25, 0.25 * g.C, rx * 2.15, g.yb - 50, 0.6, 1, 0, 0.6),
    ]


@glyph("R")
def _R(g):
    w = g.wn * 1.1
    return [
        LN(0, g.yC, 0, g.yb),
        d_bowl(g, 0, w, g.yC, 0.44 * g.C),
        LN(w * 0.45, 0.44 * g.C, w + 15, g.yb, 0.8, 1),
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
    return g.wn * 1.05 + g.a * 0.8


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
    return DOT(x, y + 0, g.dot * s)


@glyph("period")
def _period(g):
    return [ball(g, 0, g.dot * g.a)]


@glyph("comma")
def _comma(g):
    r = g.dot * g.a
    return [S(ball(g, 0, r), [(r * 0.15, -r * 1.2, g.dot * 0.4, 1)])]


@glyph("colon")
def _colon(g):
    r = g.dot * g.a
    return [ball(g, 0, r), ball(g, 0, g.X - r)]


@glyph("semicolon")
def _semicolon(g):
    r = g.dot * g.a
    return [S(ball(g, 0, r), [(r * 0.15, -r * 1.2, g.dot * 0.4, 1)]), ball(g, 0, g.X - r)]


@glyph("exclam")
def _exclam(g):
    r = g.dot * g.a
    return [LN(0, g.yC, 0, 2 * r + 120, 1.05, 0.7, 0.3, 0.3), ball(g, 0, r)]


@glyph("question")
def _question(g):
    r = g.dot * g.a
    w = g.wn * 0.95
    rq = 0.2 * g.C
    yq = g.C + g.ov - g.b - rq
    return [
        S(ARC(w / 2, yq, w / 2, rq, 160, -90, g.dot * 1.05, 1, 0.8, 0), LN(w / 2, yq - rq, w / 2, 2 * r + 120, 1, 0.8)),
        ball(g, w / 2, r),
    ]


def tick(g, x, ytop, flip=False):
    """A comma-shaped quote: ball at top, tail going down (or ball at bottom, tail up)."""
    r = g.dot * g.a
    if flip:
        return S([(x - r * 0.15, ytop, g.dot * 0.4, 1)], DOT(x, ytop - r * 1.6, g.dot))
    return S(DOT(x, ytop - r, g.dot), [(x + r * 0.15, ytop - r * 2.6, g.dot * 0.4, 1)])


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
    d = 2 * g.a * g.dot + 70
    return [tick(g, 0, g.C), tick(g, d, g.C)]


@glyph("quotedblleft", 0x201C)
def _qdl(g):
    d = 2 * g.a * g.dot + 70
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
    sx, sy = at(xu, yu, w * 0.22, ru, 230)
    ex, ey = at(w * 0.42, yl, w * 0.42, rl, 140)
    return [
        S(
            LN(w, g.yb, sx, sy, 1, 0.9),
            ARC(xu, yu, w * 0.22, ru, 230, -60, 0.9, 0.8),
        ),
        S(
            ARC(w * 0.42, yl, w * 0.42, rl, 140, 340, 1, 0.9),
            LN(*at(w * 0.42, yl, w * 0.42, rl, 340), w * 1.02, 0.45 * g.C, 0.9, 0.9),
        ),
        LN(*at(xu, yu, w * 0.22, ru, -60), ex, ey, 0.8, 1),
    ]


@glyph("at")
def _at(g):
    w = g.wn * 1.9 + g.a * 1.5
    R = w / 2
    cy = 0.37 * g.C
    ry = 0.42 * g.C
    rb = g.wn * 0.3 + g.a * 0.2
    xs = R + rb * 0.85
    return [
        ARC(R, cy, R, ry, -30, 320, 0.7, 0.7),
        ARC(R, cy, rb, rb * 1.1, 0, 360, 0.5),
        S(LN(xs, cy + rb, xs, cy - rb * 0.6, 0.5), ARC(xs + R * 0.2, cy - rb * 0.6, R * 0.2, rb * 0.4, 180, 330, 0.5, 0.5)),
    ]


@glyph("ellipsis", 0x2026)
def _ellipsis(g):
    r = g.dot * g.a
    d = 2 * r + 70
    return [ball(g, 0, r), ball(g, d, r), ball(g, 2 * d, r)]


@glyph("bullet", 0x2022)
def _bullet(g):
    return [DOT(0, 0.48 * g.X, g.dot * 1.15)]


@glyph("periodcentered", 0x00B7)
def _middot(g):
    return [ball(g, 0, 0.48 * g.X - g.dot * g.a)]


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


ROUND_LEFT = set("acdeoqCGOQS") | {"zero", "two", "three", "five", "six", "eight", "nine", "parenright", "Euro"}
ROUND_RIGHT = set("bopDOQS") | {"zero", "three", "five", "six", "eight", "nine", "parenleft"}
