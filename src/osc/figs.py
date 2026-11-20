# -*- coding: utf-8 -*-
"""Hand-rolled SVG figures (no plotting library on this machine)."""
import math

W, H = 720, 380
INK = "#14202b"
MUTED = "#6b7785"
GRID = "#e3e8ee"
TEAL = "#0f766e"
AMBER = "#b45309"
SLATE = "#94a3b8"
PAPER = "#ffffff"
FONT = "font-family='Inter,Segoe UI,Helvetica,Arial,sans-serif'"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _head(w=W, h=H):
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d' width='%d' "
            "height='%d' role='img'>" % (w, h, w, h)
            + "<rect width='100%%' height='100%%' fill='%s'/>" % PAPER)


def _text(x, y, s, size=11, fill=INK, anchor="start", weight="400"):
    return ("<text x='%.1f' y='%.1f' font-size='%s' fill='%s' text-anchor='%s' "
            "font-weight='%s' %s>%s</text>" % (x, y, size, fill, anchor, weight, FONT, _esc(s)))


def _line(x1, y1, x2, y2, stroke=GRID, w=1, dash=None):
    d = " stroke-dasharray='%s'" % dash if dash else ""
    return ("<line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' stroke='%s' "
            "stroke-width='%s'%s/>" % (x1, y1, x2, y2, stroke, w, d))


def _box(x, y, w, h, fill, stroke="none", op=1.0, r=2):
    return ("<rect x='%.1f' y='%.1f' width='%.1f' height='%.1f' rx='%s' fill='%s' "
            "stroke='%s' fill-opacity='%s'/>" % (x, y, w, h, r, fill, stroke, op))


def _scale(domain, rng):
    d0, d1 = domain
    r0, r1 = rng

    def f(v):
        if d1 == d0:
            return (r0 + r1) / 2.0
        return r0 + (v - d0) * (r1 - r0) / (d1 - d0)
    return f


# ---------------------------------------------------------------- dome
def fig_dome(dome):
    ml, mr, mt, mb = 62, 24, 36, 54
    x = _scale((0, 1), (ml, W - mr))
    ys = [p["a_d"] for p in dome["points"]]
    y = _scale((min(ys) - 0.006, max(ys) + 0.008), (H - mb, mt))
    s = [_head()]
    s.append(_text(ml, 18, "A_d(delta): flat for delta <= 1/3, then a cliff", 13, INK, weight="600"))
    s.append(_text(ml, 32, "%d published levels, %d of them positive; 6x6 cluster, U/t = 8"
                   % (dome["entries"], dome["positive_levels"]), 10, MUTED))

    px = x(dome["plateau"]["max_delta"])
    s.append(_box(ml, mt, px - ml, H - mb - mt, TEAL, op=0.06))
    s.append(_text(ml + 6, mt + 14, "plateau: 7 levels, 1.52x", 10, TEAL, weight="600"))

    s.append(_line(ml, H - mb, W - mr, H - mb, INK, 1))
    s.append(_line(ml, mt, ml, H - mb, INK, 1))
    for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        s.append(_line(x(t), H - mb, x(t), H - mb + 4, INK, 1))
        s.append(_text(x(t), H - mb + 16, "%.1f" % t, 9, MUTED, "middle"))
    s.append(_text((ml + W - mr) / 2, H - 14, "hole filling  delta", 10, MUTED, "middle"))
    s.append("<g transform='translate(20,%.0f) rotate(-90)'>" % ((H - mb + mt) / 2)
             + _text(0, 0, "A_d", 9, MUTED, "middle") + "</g>")

    step = 0.01 if (max(ys) - min(ys)) < 0.08 else 0.02
    t = math.ceil(min(ys) / step) * step
    while t <= max(ys) + 1e-9:
        s.append(_line(ml, y(t), W - mr, y(t), GRID, 1))
        s.append(_text(ml - 6, y(t) + 3, "%.2f" % t, 9, MUTED, "end"))
        t += step
    if min(ys) < 0:
        s.append(_line(ml, y(0), W - mr, y(0), SLATE, 1, "3 3"))

    pts = sorted(dome["points"], key=lambda p: p["delta"])
    for a, b in zip(pts, pts[1:]):
        s.append(_line(x(a["delta"]), y(a["a_d"]), x(b["delta"]), y(a["a_d"]), TEAL, 1.8))
        s.append(_line(x(b["delta"]), y(a["a_d"]), x(b["delta"]), y(b["a_d"]), TEAL, 1.8))
    for p in pts:
        s.append("<circle cx='%.1f' cy='%.1f' r='2.6' fill='%s'/>"
                 % (x(p["delta"]), y(p["a_d"]), TEAL))

    hf = dome["half_filling"]
    s.append("<circle cx='%.1f' cy='%.1f' r='5' fill='none' stroke='%s' stroke-width='1.6'/>"
             % (x(0.0), y(hf["a_d"]), AMBER))
    s.append(_text(x(0.0) + 10, y(hf["a_d"]) - 10,
                   "half filling: %.4f = %d%% of peak" % (hf["a_d"], round(100 * hf["share_of_peak"])),
                   9, AMBER, "start", "600"))

    c = dome["cliff"]
    s.append(_text(x(c["to_delta"]) + 8, y(c["a_to"]) + 18,
                   "cliff: %.4f -> %.4f (x%.1f)" % (c["a_from"], c["a_to"], c["ratio"]),
                   9, AMBER, "start", "600"))
    s.append(_text(x(dome["peak"]["delta"]) + 6, y(dome["peak"]["a_d"]) - 8,
                   "peak %.4f" % dome["peak"]["a_d"], 9, INK, "start", "600"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- board
def fig_board(board, stats):
    ml, mr, mt, mb = 118, 150, 40, 32
    n = len(board)
    rowh = (H - mt - mb) / float(n)
    xmax = max(r["index"] for r in board) * 1.02
    x = _scale((0, xmax), (ml, W - mr))
    s = [_head()]
    s.append(_text(14, 18, "Top-20 by index, with each material's N(E_F) rank", 13, INK, weight="600"))
    nlo = sum(1 for r in board if r["nef_rank"] <= 20)
    s.append(_text(14, 32, "every entry sits at delta <= %.3f; %d of 20 also have N(E_F) rank <= 20"
                   % (stats["top20_max_delta"], nlo), 10, MUTED))
    for i, r in enumerate(board):
        yy = mt + i * rowh
        wbar = x(r["index"]) - ml
        col = TEAL if r["nef_rank"] <= 20 else SLATE
        s.append(_box(ml, yy + 1.5, wbar, rowh - 3.2, col, op=0.80 if r["nef_rank"] <= 20 else 0.45))
        s.append(_text(ml - 6, yy + rowh - 4, "%d. %s" % (r["rank"], r["formula"]), 9.5, INK, "end"))
        s.append(_text(x(r["index"]) + 5, yy + rowh - 4,
                       "%.1f  (N(E_F) #%d)" % (r["index"], r["nef_rank"]), 9, MUTED))
    s.append(_line(ml, H - mb + 2, W - mr, H - mb + 2, INK, 1))
    s.append(_text((ml + W - mr) / 2, H - 10, "OSC Pairing Index", 10, MUTED, "middle"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- scatter
def fig_scatter(active, dome):
    ml, mr, mt, mb = 60, 24, 36, 50
    lim = (0.001, 5.0)
    x = _scale((math.log10(lim[0]), math.log10(lim[1])), (ml, W - mr))
    y = _scale((-0.3, 2.0), (H - mb, mt))
    s = [_head()]
    s.append(_text(ml, 18, "Inside the plateau the index is a straight line in N(E_F)", 13, INK, weight="600"))
    s.append(_text(ml, 32, "703 plateau materials (teal) vs 370 others (grey)", 10, MUTED))
    for t in (-0.2, 0.0, 0.5, 1.0, 1.5, 2.0):
        s.append(_line(ml, y(t), W - mr, y(t), GRID, 1))
        s.append(_text(ml - 6, y(t) + 3, "%.1f" % t, 9, MUTED, "end"))
    for t in (0.01, 0.1, 1.0):
        s.append(_line(x(math.log10(t)), mt, x(math.log10(t)), H - mb, GRID, 1))
        s.append(_text(x(math.log10(t)), H - mb + 14, "%g" % t, 9, MUTED, "middle"))
    s.append(_line(ml, H - mb, W - mr, H - mb, INK, 1))
    s.append(_text((ml + W - mr) / 2, H - 14, "N(E_F)  [states/eV/atom, log]", 10, MUTED, "middle"))
    s.append("<g transform='translate(20,%.0f) rotate(-90)'>" % ((H - mb + mt) / 2)
             + _text(0, 0, "index (log)", 9, MUTED, "middle") + "</g>")
    for m in active:
        idx = max(0.0, m["nef"] * m["a_d"] * 300.0)
        if idx <= 0 or m["nef"] <= 0:
            continue
        pl = m["delta"] <= dome["plateau"]["max_delta"] + 1e-9
        s.append("<circle cx='%.1f' cy='%.1f' r='2.1' fill='%s' fill-opacity='%s'/>"
                 % (x(math.log10(m["nef"])), y(math.log10(idx)),
                    TEAL if pl else SLATE, 0.62 if pl else 0.40))
    top = sorted(active, key=lambda m: -m["nef"] * m["a_d"])[:3]
    for m in top:
        idx = m["nef"] * m["a_d"] * 300.0
        s.append("<circle cx='%.1f' cy='%.1f' r='5' fill='none' stroke='%s' stroke-width='1.4'/>"
                 % (x(math.log10(m["nef"])), y(math.log10(idx)), AMBER))
    for i, m in enumerate(top):
        idx = m["nef"] * m["a_d"] * 300.0
        s.append(_text(ml + 14, H - mb - 52 + 16 * i,
                       "%s   index %.1f   N(E_F) %.2f" % (m["formula"], idx, m["nef"]),
                       9, AMBER, "start", "600"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- ed
def fig_ed(curve, rho):
    ml, mr, mt, mb = 62, 132, 38, 54
    x = _scale((0.45, 1.05), (ml, W - mr))
    vals = [p["ed"] for p in curve] + [p["osc"] for p in curve] + [p["ed_u0"] for p in curve]
    y = _scale((min(vals) * 1.3, max(vals) * 1.15), (H - mb, mt))
    s = [_head()]
    s.append(_text(ml, 18, "Published curve vs the unbiased 4x4 ED: different order", 13, INK, weight="600"))
    s.append(_text(ml, 32, "same fillings, different cluster size; Spearman rho = %.2f (n=5)" % rho, 10, MUTED))
    t = math.ceil(min(vals) * 1.3 / 0.02) * 0.02
    while t <= max(vals) * 1.15 + 1e-9:
        s.append(_line(ml, y(t), W - mr, y(t), GRID, 1))
        s.append(_text(ml - 6, y(t) + 3, "%.2f" % t, 9, MUTED, "end"))
        t += 0.02
    s.append(_line(ml, y(0), W - mr, y(0), SLATE, 1, "3 3"))
    s.append(_line(ml, H - mb, W - mr, H - mb, INK, 1))
    s.append(_line(ml, mt, ml, H - mb, INK, 1))
    for p in curve:
        s.append(_text(x(p["n"]), H - mb + 15, "%.3f" % p["n"], 9, MUTED, "middle"))
    s.append(_text((ml + W - mr) / 2, H - 14, "band filling  n = 1 - delta", 10, MUTED, "middle"))
    s.append("<g transform='translate(20,%.0f) rotate(-90)'>" % ((H - mb + mt) / 2)
             + _text(0, 0, "A_d at max distance", 9, MUTED, "middle") + "</g>")
    for key, col, dash, lab in (("osc", TEAL, None, "published 6x6"),
                                ("ed", AMBER, "5 4", "4x4 ED, U=8"),
                                ("ed_u0", SLATE, "1 3", "4x4 ED, U=0")):
        pts = [(x(p["n"]), y(p[key])) for p in curve]
        for a, b in zip(pts, pts[1:]):
            s.append(_line(a[0], a[1], b[0], b[1], col, 2, dash))
        for px, py in pts:
            s.append("<circle cx='%.1f' cy='%.1f' r='3' fill='%s'/>" % (px, py, col))
    s.append(_line(W - mr + 12, mt + 16, W - mr + 34, mt + 16, TEAL, 2))
    s.append(_text(W - mr + 38, mt + 19, "published", 9, INK))
    s.append(_line(W - mr + 12, mt + 34, W - mr + 34, mt + 34, AMBER, 2, "5 4"))
    s.append(_text(W - mr + 38, mt + 37, "ED U=8", 9, INK))
    s.append(_line(W - mr + 12, mt + 52, W - mr + 34, mt + 52, SLATE, 2, "1 3"))
    s.append(_text(W - mr + 38, mt + 55, "ED U=0", 9, INK))
    s.append(_text(W - mr + 12, mt + 78, "ED at n=0.5 is", 9, AMBER, "start", "600"))
    s.append(_text(W - mr + 12, mt + 90, "97% band effect", 9, AMBER, "start", "600"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- survival
def fig_survival(board, stress):
    ml, mr, mt, mb = 130, 70, 42, 36
    n = len(board)
    rowh = (H - mt - mb) / float(n)
    x = _scale((0, 1), (ml, W - mr))
    s = [_head()]
    s.append(_text(14, 18, "Top-20 survival under independent level noise (the worst case)", 13, INK, weight="600"))
    s.append(_text(14, 32, "sigma = %.2f, %d draws; a global rescale gives 20/20 by construction"
                   % (stress["sigma"], stress["draws"]), 10, MUTED))
    for i, r in enumerate(board):
        p = stress["survival"].get(r["material_id"], 0.0)
        yy = mt + i * rowh
        s.append(_box(ml, yy + 1.8, x(p) - ml, rowh - 3.6, TEAL, op=0.75))
        s.append(_text(ml - 6, yy + rowh - 4, "%s" % r["formula"], 9, INK, "end"))
        s.append(_text(x(p) + 5, yy + rowh - 4, "%d%%" % round(100 * p), 9, MUTED))
    s.append(_line(ml, H - mb + 2, W - mr, H - mb + 2, INK, 1))
    s.append(_text((ml + W - mr) / 2, H - 12, "P(still in top-20)", 10, MUTED, "middle"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- structures
def fig_structures(stress):
    ml, mr, mt, mb = 150, 90, 46, 30
    rows = [("single global factor", stress["structures"]["global"]["expected_overlap"]),
            ("AR(1) rho=0.9", stress["structures"]["ar1"]["expected_overlap"]),
            ("independent levels", stress["structures"]["independent"]["expected_overlap"])]
    x = _scale((0, 20), (ml, W - mr))
    s = [_head(W, 230)]
    s.append(_text(14, 18, "The answer depends on the error structure, not on the data", 13, INK, weight="600"))
    s.append(_text(14, 32, "expected top-20 overlap out of 20, same marginal sigma", 10, MUTED))
    bh = 40
    for i, (lab, v) in enumerate(rows):
        yy = mt + i * (bh + 8)
        s.append(_box(ml, yy, max(2, x(v) - ml), bh, TEAL, op=0.30 + 0.20 * (2 - i)))
        s.append(_text(ml - 8, yy + bh / 2 + 4, lab, 10, INK, "end"))
        s.append(_text(x(v) + 6, yy + bh / 2 + 4, "%.1f / 20" % v, 10, MUTED))
    s.append(_line(ml, mt + 3 * (bh + 8) - 4, W - mr, mt + 3 * (bh + 8) - 4, INK, 1))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- screen
def fig_screen(pairs, cv):
    ml, mr, mt, mb = 62, 26, 38, 52
    x = _scale((-3.7, 1.7), (ml, W - mr))
    y = _scale((-3.7, 1.7), (H - mb, mt))
    s = [_head()]
    s.append(_text(ml, 18, "Composition-only screener: it cannot even recover the leaders", 13, INK, weight="600"))
    s.append(_text(ml, 32, "leave-one-out, k=15 neighbours; R2 = %.2f, MAE = %.2f in log N(E_F)"
                   % (cv["r2"], cv["mae"]), 10, MUTED))
    s.append(_line(ml, H - mb, W - mr, H - mb, INK, 1))
    s.append(_line(ml, mt, ml, H - mb, INK, 1))
    s.append(_line(x(-3.7), y(-3.7), x(1.7), y(1.7), SLATE, 1, "4 3"))
    for t in (-3, -2, -1, 0, 1):
        s.append(_text(x(t), H - mb + 14, "%d" % t, 9, MUTED, "middle"))
        s.append(_text(ml - 5, y(t) + 3, "%d" % t, 9, MUTED, "end"))
    s.append(_text((ml + W - mr) / 2, H - 14, "predicted log N(E_F)", 10, MUTED, "middle"))
    s.append("<g transform='translate(20,%.0f) rotate(-90)'>" % ((H - mb + mt) / 2)
             + _text(0, 0, "true log N(E_F)", 9, MUTED, "middle") + "</g>")
    for t, p in pairs:
        s.append("<circle cx='%.1f' cy='%.1f' r='1.9' fill='%s' fill-opacity='0.42'/>"
                 % (x(p), y(t), TEAL))
    s.append(_text(x(0.2), y(-2.9), "y = x", 9, MUTED))
    s.append("</svg>")
    return "".join(s)
