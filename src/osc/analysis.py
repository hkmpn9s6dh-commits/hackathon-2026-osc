"""The scoring rule, the filling grid, and what the board actually orders."""
import math

N_SITES = 36          # the organisers' 6x6 cluster
GRID = 2              # solver_delta is reported on even-Ne steps of the 36-site cluster


def ne_from_delta(delta):
    """Electron count on the 6x6 cluster implied by a hole filling delta."""
    return N_SITES - int(round(delta * N_SITES))


def index(nef, a_d, scale=300.0):
    """OSC Pairing Index. Negative A_d (no d-wave order) is clamped to zero."""
    return max(0.0, nef * a_d * scale)


def reproduce(active, table, scale=300.0, submissions=None):
    """Recompute every verified score from (nef, delta) and the published A_d table."""
    rows = []
    for m in active:
        ne = ne_from_delta(m["delta"])
        a_tab = table.get(ne, 0.0)
        calc = index(m["nef"], a_tab, scale)
        ver = submissions.get(m["material_id"], {}).get("verified") if submissions else None
        rows.append(dict(
            material_id=m["material_id"], osc_id=m["osc_id"], formula=m["formula"],
            ne=ne, delta=m["delta"], nef=m["nef"], covered=ne in table,
            a_table=a_tab, a_row=m["a_d"], calc=calc, verified=ver,
            diff=(None if ver is None else abs(calc - ver)),
            a_matches_row=abs(a_tab - m["a_d"]) <= 1e-9,
        ))
    return rows


def grid(active):
    """The filling grid: which distinct delta values the solver actually uses."""
    counts = {}
    for m in active:
        counts[round(m["delta"], 6)] = counts.get(round(m["delta"], 6), 0) + 1
    ds = sorted(counts)
    steps = sorted({ne_from_delta(d) for d in ds})
    return dict(
        n_delta=len(ds), deltas=ds, ne_steps=steps, counts={d: counts[d] for d in ds},
        on_even_grid=all(ne % GRID == 0 for ne in steps),
    )


def dome(table):
    """Describe the A_d(delta) curve: is it a dome, a plateau, or a cliff?"""
    pts = sorted(((N_SITES - ne) / N_SITES, a) for ne, a in table.items())
    pos = [(d, a) for d, a in pts if a > 0]
    peak_d, peak_a = max(pos, key=lambda t: t[1])
    # the cliff: the largest absolute drop between adjacent fillings, counting
    # non-positive A_d as zero (a negative amplitude means "no d-wave order").
    drops = []
    for (d0, a0), (d1, a1) in zip(pts, pts[1:]):
        drop = a0 - max(a1, 0.0)
        drops.append((drop, d0, d1, a0, max(a1, 0.0), a1))
    drop, cliff_from, cliff_to, a_from, a_to, a_raw = max(drops)
    plateau = [(d, a) for d, a in pts if d <= cliff_from + 1e-9]
    half = [a for d, a in pts if abs(d) < 1e-9]
    half_a = half[0] if half else 0.0
    return dict(
        points=[dict(delta=d, a_d=a) for d, a in pts],
        entries=len(pts),
        positive_levels=len(pos),
        missing_ne=[ne for ne in range(0, 37, 2) if ne not in table],
        half_filling=dict(delta=0.0, a_d=half_a, share_of_peak=half_a / peak_a if peak_a else 0.0),
        peak=dict(delta=peak_d, a_d=peak_a),
        cliff=dict(from_delta=cliff_from, to_delta=cliff_to,
                   a_from=a_from, a_to=a_to, a_to_raw=a_raw,
                   drop=drop, ratio=(a_from / a_to if a_to > 0 else None)),
        plateau=dict(max_delta=cliff_from, n=len(plateau),
                     a_min=min(a for _, a in plateau), a_max=max(a for _, a in plateau),
                     spread=max(a for _, a in plateau) / min(a for _, a in plateau),
                     n_materials=None),
        zero_or_negative=[d for d, a in pts if a <= 0],
    )


def is_plateau(delta, d):
    return delta <= d["plateau"]["max_delta"] + 1e-9


def decomposition(active, scale=300.0):
    """How much of the spread in the index is N(E_F) and how much is the filling?"""
    pos = [m for m in active if index(m["nef"], m["a_d"], scale) > 0 and m["nef"] > 0]
    xs = [math.log(m["nef"]) for m in pos]
    ys = [math.log(m["a_d"]) for m in pos]
    zs = [math.log(index(m["nef"], m["a_d"], scale)) for m in pos]
    n = len(pos)

    def mean(v):
        return sum(v) / len(v)

    def cov(a, b, ma=None, mb=None):
        ma = mean(a) if ma is None else ma
        mb = mean(b) if mb is None else mb
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)

    mz, mx, my = mean(zs), mean(xs), mean(ys)
    vz = cov(zs, zs, mz, mz)
    vx = cov(xs, xs, mx, mx)
    vy = cov(ys, ys, my, my)
    cxy = cov(xs, ys, mx, my)
    return dict(
        n=n, var_log_index=vz, var_log_nef=vx, var_log_a=vy, cov=cxy,
        share_nef=vx / vz, share_a=vy / vz, share_cov=2 * cxy / vz,
        corr_log=spearman(xs, zs), corr_pearson=cxy / math.sqrt(vx * vy),
    )


def ranks(v):
    """Average ranks, ties share the mean rank."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            out[order[k]] = r
        i = j + 1
    return out


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0


def board(active, k=20, scale=300.0):
    """The published leaderboard: top-k by index, plus what drives it."""
    rows = sorted(active, key=lambda m: -index(m["nef"], m["a_d"], scale))
    nef_sorted = sorted(active, key=lambda m: -m["nef"])
    nef_rank = {m["material_id"]: i + 1 for i, m in enumerate(nef_sorted)}
    out = []
    for i, m in enumerate(rows[:k]):
        out.append(dict(
            rank=i + 1, material_id=m["material_id"], osc_id=m["osc_id"],
            formula=m["formula"], nef=m["nef"], delta=m["delta"],
            a_d=m["a_d"], index=index(m["nef"], m["a_d"], scale),
            nef_rank=nef_rank[m["material_id"]],
        ))
    return out


def robust_ranking(active, dome_info, scale=300.0, k=10):
    """Rank materials (not fillings): N(E_F) inside the plateau, where every
    published cluster agrees the d-wave channel is on."""
    plateau = [m for m in active if is_plateau(m["delta"], dome_info)]
    rows = sorted(plateau, key=lambda m: -m["nef"])[:k]
    board_rank = {m["material_id"]: i + 1 for i, m in enumerate(
        sorted(active, key=lambda m: -index(m["nef"], m["a_d"], scale)))}
    return [dict(rank=i + 1, material_id=m["material_id"], osc_id=m["osc_id"],
                 formula=m["formula"], nef=m["nef"], delta=m["delta"],
                 a_d=m["a_d"], index=index(m["nef"], m["a_d"], scale),
                 board_rank=board_rank[m["material_id"]]) for i, m in enumerate(rows)]


def plateau_decomposition(active, dome_info, scale=300.0):
    """Inside the plateau, A_d is nearly flat, so the ordering is N(E_F)."""
    rows = [m for m in active if is_plateau(m["delta"], dome_info)
            and index(m["nef"], m["a_d"], scale) > 0]
    zs = [math.log(index(m["nef"], m["a_d"], scale)) for m in rows]
    xs = [math.log(m["nef"]) for m in rows]
    n = len(rows)
    mx, mz = sum(xs) / n, sum(zs) / n
    vx = sum((v - mx) ** 2 for v in xs) / n
    vz = sum((v - mz) ** 2 for v in zs) / n
    cxz = sum((a - mx) * (b - mz) for a, b in zip(xs, zs)) / n
    return dict(n=n, var_log_index=vz, var_log_nef=vx, pearson=cxz / math.sqrt(vx * vz),
                spearman=spearman(xs, zs),
                a_min=min(m["a_d"] for m in rows), a_max=max(m["a_d"] for m in rows))
