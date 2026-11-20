"""Read the organisers' published ED validation tables and stress-test the ordering.

Two published sources are used, both shipped inside the challenge dataset:

* validation/comparison_4x4_ED_vs_VMC.md   -> 4x4 ED at five fillings (unbiased reference)
* validation/multisize_ED_table_kuku.md    -> five clusters, all fillings (published by a
  contributor, credited in the challenge README)

Nothing here re-runs a solver: the point is to ask whether the *ordering* implied by the
published A_d(delta) survives the method uncertainty that the challenge itself publishes.
"""
import io
import math
import os
import random

from . import data as D


def parse_4x4():
    """n, Ne, ED P_d(U=8), ED P_d(U=0) from the published comparison table."""
    path = os.path.join(D.DATA, "validation", "comparison_4x4_ED_vs_VMC.md")
    out = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 4:
                continue
            try:
                out.append(dict(n=float(c[0]), ne=int(c[1]), ed_u8=float(c[2]),
                                ed_u0=float(c[3])))
            except ValueError:
                continue
    return out


def parse_multisize():
    """cluster, N, n, P_org(U=8) from the published multi-size ED table."""
    path = os.path.join(D.DATA, "validation", "multisize_ED_table_kuku.md")
    out = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 11 or c[0] in ("cluster", "") or set(c[0]) <= set("-: "):
                continue
            try:
                out.append(dict(cluster=c[0], N=int(c[1]), n=float(c[2]),
                                r_max=float(c[8]), p_org=float(c[10])))
            except ValueError:
                continue
    return out


def interp(xs, ys, x):
    """Piecewise-linear interpolation on an ASCENDING xs, clamped at both ends."""
    if xs[0] > xs[-1]:
        xs, ys = xs[::-1], ys[::-1]
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def osc_curve(table):
    """A_d as a function of delta, as published."""
    return sorted(((36 - ne) / 36.0, a) for ne, a in table.items())


def curve_comparison(table):
    """Published A_d(delta) vs the unbiased 4x4 ED at the same band fillings."""
    ed = parse_4x4()
    xs = [d for d, _ in osc_curve(table)]
    ys = [a for _, a in osc_curve(table)]
    pts = []
    for row in ed:
        delta = 1.0 - row["n"]
        pts.append(dict(n=row["n"], delta=delta, ed=row["ed_u8"], ed_u0=row["ed_u0"],
                        osc=interp(xs, ys, delta)))
    pts.sort(key=lambda p: p["delta"])
    return pts


def cluster_spread():
    """How much the max-distance pair correlation moves between clusters at fixed n."""
    rows = parse_multisize()
    by_n = {}
    for r in rows:
        by_n.setdefault(round(r["n"], 4), []).append(r)
    out = []
    for n, rs in sorted(by_n.items()):
        pos = [r["p_org"] for r in rs if r["p_org"] > 0]
        if len(rs) < 2:
            continue
        spread = (max(pos) / min(pos)) if len(pos) >= 2 else None
        out.append(dict(n=n, clusters=[r["cluster"] for r in rs],
                        values=[r["p_org"] for r in rs], spread=spread,
                        signs=sorted({1 if r["p_org"] > 0 else (-1 if r["p_org"] < 0 else 0)
                                      for r in rs})))
    return out


def sigma_from_spread(spreads):
    """A single log-scale for the band test: half the median log-range across clusters.

    This is a PROXY for method uncertainty, not a confidence interval; the report says so.
    """
    vals = [s["spread"] for s in spreads if s["spread"]]
    if not vals:
        return 0.0
    logs = sorted(math.log(v) for v in vals)
    med = logs[len(logs) // 2]
    return med / 2.0


def stress_shape(table, active, scale=300.0, k=20, sigma=None, draws=4000, seed=7):
    """Two stress tests on the ordering.

    shape : replace A_d(delta) by the shape of the unbiased 4x4 ED curve (normalised to the
            same median), recompute the board, and look at the overlap with the published
            top-k. Interpolation runs on an ascending delta axis and is clamped at the ends;
            beyond the last shared filling (delta > 0.5) the ED reference says nothing, so
            those levels are set to 0 - that is stated in the report.
    band  : multiply each filling level's A_d by exp(eps), with marginal sd `sigma` and three
            correlation structures along the filling axis (independent / AR(1) rho=0.9 /
            a single global multiplier). The structure matters more than sigma, so all three
            are reported.
    """
    plate = curve_comparison(table)
    med_ed = sorted(p["ed"] for p in plate)[len(plate) // 2]
    med_osc = sorted(p["osc"] for p in plate)[len(plate) // 2]
    factor = med_osc / med_ed if med_ed else 1.0
    ed_xs = [p["delta"] for p in plate]
    ed_ys = [p["ed"] * factor for p in plate]

    def a_shape(delta):
        if delta > ed_xs[-1] + 1e-9:
            return 0.0
        return max(0.0, interp(ed_xs, ed_ys, delta))

    def board_of(fn):
        rows = sorted(active, key=lambda m: -max(0.0, m["nef"] * fn(m["delta"]) * scale))
        return [m["material_id"] for m in rows[:k]]

    base = board_of(lambda d: _a_of(table, d))
    shape = board_of(a_shape)
    overlap = len(set(base) & set(shape))
    levels = sorted({round(m["delta"], 6) for m in active})
    shape_a = {d: round(a_shape(d), 6) for d in levels}

    if sigma is None:
        sigma = sigma_from_spread(cluster_spread())
    rng = random.Random(seed)

    def draw_eps(structure):
        z = [rng.gauss(0.0, 1.0) for _ in levels]
        if structure == "global":
            g = rng.gauss(0.0, 1.0)
            return {d: sigma * g for d in levels}
        if structure == "ar1":
            out, prev = [], 0.0
            for v in z:
                prev = 0.9 * prev + math.sqrt(1 - 0.81) * v
                out.append(prev)
            return {d: sigma * v for d, v in zip(levels, out)}
        return {d: sigma * v for d, v in zip(levels, z)}

    def run(structure, n_draws):
        survive = {mid: 0 for mid in base}
        first = {mid: 0 for mid in base}
        ov = 0
        for _ in range(n_draws):
            eps = draw_eps(structure)

            def a_pert(delta, eps=eps):
                return max(0.0, _a_of(table, delta) * math.exp(eps[round(delta, 6)]))

            b = board_of(a_pert)
            bset = set(b)
            ov += len(set(base) & bset)
            for mid in base:
                if mid in bset:
                    survive[mid] += 1
            if b and b[0] in first:
                first[b[0]] += 1
        return dict(structure=structure, draws=n_draws,
                    expected_overlap=ov / float(n_draws),
                    expected_overlap_frac=ov / float(n_draws * k),
                    survival={m: survive[m] / float(n_draws) for m in base},
                    first={m: first[m] / float(n_draws) for m in base})

    band = run("independent", draws)
    structures = {s: run(s, max(1200, draws // 2))
                  for s in ("independent", "ar1", "global")}
    sweep = []
    orig = sigma
    for sig in (0.4, 0.6, 0.88, 1.2):
        sigma = sig
        r = run("independent", max(800, draws // 4))
        sweep.append(dict(sigma=sig, expected_overlap=r["expected_overlap"]))
    sigma = orig

    return dict(
        base=base, shape=shape, overlap_shape=overlap,
        overlap_shape_frac=overlap / float(k), shape_a=shape_a,
        sigma=sigma, draws=draws, structure="independent",
        expected_overlap=band["expected_overlap"],
        expected_overlap_frac=band["expected_overlap_frac"],
        survival=band["survival"], first=band["first"],
        structures={k: dict(expected_overlap=v["expected_overlap"],
                            first=v["first"][base[0]], draws=v["draws"])
                    for k, v in structures.items()},
        sweep=sweep, levels=levels,
    )


def ed_overlap_range(table, active, scale=300.0, k=20):
    """How sensitive the ED overlap is to the interpolation direction."""
    plate = curve_comparison(table)
    out = {"as_shipped": None, "on_grid": None}

    # (a) ED values carried onto the 18 filling levels (the 15 table entries + holes)
    xs = [p["delta"] for p in plate]
    ys = [p["ed"] for p in plate]
    med_ed = sorted(ys)[len(ys) // 2]
    levels = sorted({round(m["delta"], 6) for m in active})
    norm = med_ed if med_ed else 1.0

    def board_of(fn):
        rows = sorted(active, key=lambda m: -max(0.0, m["nef"] * fn(m["delta"]) * scale))
        return [m["material_id"] for m in rows[:k]]

    base = board_of(lambda d: _a_of(table, d))
    a = {}
    for d in levels:
        a[d] = max(0.0, interp(xs, ys, d)) / norm
    alt = board_of(lambda d: a[round(d, 6)])
    out["on_grid"] = len(set(base) & set(alt))
    return out


def _a_of(table, delta):
    ne = 36 - int(round(delta * 36))
    return table.get(ne, 0.0)


def ed_grid_spearman(table):
    """Spearman between published A_d and ED interpolated onto the 15 table fillings."""
    from . import analysis as AN
    plate = curve_comparison(table)
    xs = [p["delta"] for p in plate]
    ys = [p["ed"] for p in plate]
    levels = sorted(((36 - ne) / 36.0, a) for ne, a in table.items())
    pub = [a for _, a in levels]
    edv = [interp(xs, ys, d) for d, _ in levels]
    return AN.spearman(pub, edv)
