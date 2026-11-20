"""Read the organisers' published ED validation tables and stress-test the dome.

Two published sources are used, both shipped inside the challenge dataset:

* validation/comparison_4x4_ED_vs_VMC.md   -> 4x4 ED at five fillings (unbiased reference)
* validation/multisize_ED_table_kuku.md    -> five clusters, all fillings (published by a
  contributor, credited in the challenge README)

Nothing here re-runs a solver: the point is to test whether the *shape* of the published
A_d(delta) curve is reproducible from the data the challenge itself ships.
"""
import io
import os
import random
import re

from . import data as D


def _cell(s):
    return s.strip().strip("|").strip()


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
                float(c[0])
            except ValueError:
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
    """Piecewise-linear interpolation, clamped at the ends."""
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
        pts.append(dict(n=row["n"], delta=delta, ed=row["ed_u8"],
                        osc=interp(xs, ys, delta)))
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
        neg = [r["p_org"] for r in rs if r["p_org"] < 0]
        if len(rs) < 2:
            continue
        spread = (max(pos) / min(pos)) if len(pos) >= 2 else None
        out.append(dict(n=n, clusters=[r["cluster"] for r in rs],
                        values=[r["p_org"] for r in rs],
                        spread=spread, signs=sorted({1 if r["p_org"] > 0 else
                                                     (-1 if r["p_org"] < 0 else 0)
                                                     for r in rs})))
    return out


def sigma_from_spread(spreads):
    """A single log-scale for the bucket perturbation, from the median cross-cluster range."""
    vals = [s["spread"] for s in spreads if s["spread"]]
    if not vals:
        return 0.0
    import math
    logs = sorted(math.log(v) for v in vals)
    med = logs[len(logs) // 2]
    return med / 2.0  # half the median log-range ~ a 1-sigma band


def stress_shape(table, active, scale=300.0, k=20, sigma=None, draws=4000, seed=7):
    """Two stress tests on the ordering.

    shape : replace A_d(delta) by the shape of the unbiased 4x4 ED curve (normalised to
            the same median), recompute the board, and look at the overlap with the
            published top-k.
    band  : multiply each filling level's A_d by exp(eps), eps ~ N(0, sigma), where sigma
            comes from the published cross-cluster spread; report how often each published
            top-k material survives and how often it is #1.
    """
    import math
    plate = curve_comparison(table)
    # shape-normalised ED curve: same median as the published curve over the shared fillings
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

    # perturbation band
    if sigma is None:
        sigma = sigma_from_spread(cluster_spread())
    rng = random.Random(seed)
    levels = sorted({round(m["delta"], 6) for m in active})
    survive = {mid: 0 for mid in base}
    first = {mid: 0 for mid in base}
    overlap_sum = 0
    for _ in range(draws):
        eps = {d: rng.gauss(0.0, sigma) for d in levels}

        def a_pert(delta, eps=eps):
            return max(0.0, _a_of(table, delta) * math.exp(eps[round(delta, 6)]))

        b = board_of(a_pert)
        bset = set(b)
        overlap_sum += len(set(base) & bset)
        for mid in base:
            if mid in bset:
                survive[mid] += 1
        if b:
            if b[0] in first:
                first[b[0]] += 1
    return dict(
        base=base, shape=shape, overlap_shape=overlap,
        overlap_shape_frac=overlap / float(k),
        sigma=sigma,
        draws=draws,
        expected_overlap=overlap_sum / float(draws),
        expected_overlap_frac=overlap_sum / float(draws * k),
        survival={mid: survive[mid] / float(draws) for mid in base},
        first={mid: first[mid] / float(draws) for mid in base},
        levels=levels,
    )


def _a_of(table, delta):
    ne = 36 - int(round(delta * 36))
    return table.get(ne, 0.0)
