# -*- coding: utf-8 -*-
"""Gate B: independent re-derivation of every number in the report.

This file deliberately does NOT read out/results.json. It loads the three raw tables,
recomputes everything, and asserts. If a number in the report drifts, this fails.

Usage:  py -3 verify/verify.py [-v]
Exit 0 = all assertions pass. Exit 1 = a failure (printed).
"""
import csv
import hashlib
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
SITE = os.path.join(HERE, "site")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    if not cond or "-v" in sys.argv:
        print(("  ok  " if cond else "  FAIL") + "  " + name + ("  " + detail if detail else ""))


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def spearman(a, b):
    def rk(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                out[order[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return out
    ra, rb = rk(a), rk(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0


# --------------------------------------------------------------------------
def main():
    print("== 1. dataset integrity")
    man = os.path.join(DATA, "SHA256SUMS")
    check("SHA256 manifest exists", os.path.exists(man))
    if os.path.exists(man):
        with io.open(man, encoding="utf-8") as f:
            lines = [l.split() for l in f if l.strip()]
        for digest, name in lines:
            p = os.path.join(DATA, name)
            check("hash %s" % name, os.path.exists(p) and sha(p) == digest)

    active = rows("active_challenge.csv")
    cand = rows("candidates.csv")
    subs = rows("submissions.csv")
    meta = json.load(io.open(os.path.join(DATA, "scoring_meta.json"), encoding="utf-8"))
    table = {int(k): float(v[1]) for k, v in meta["A_by_Ne"].items()}
    scale = float(meta["scale"])

    check("active rows = 1073", len(active) == 1073, str(len(active)))
    check("candidate rows = 4832", len(cand) == 4832, str(len(cand)))
    check("submission rows = 1073", len(subs) == 1073, str(len(subs)))
    check("scale = 300", close(scale, 300.0))
    check("A_d table has 15 levels", len(table) == 15, str(len(table)))

    print("== 2. every verified score is reproduced from the public table")
    sub = {r["material_id"]: r for r in subs}
    worst, over, zeroed = 0.0, 0, 0
    for r in active:
        ne = 36 - int(round(float(r["solver_delta"]) * 36))
        a = table.get(ne, 0.0)
        calc = max(0.0, float(r["nef"]) * a * scale)
        if float(r["A_dwave"]) != a:
            zeroed += 1
            if not (float(r["A_dwave"]) == 0.0 and a < 0):
                check("row A_d clamp is well formed (%s)" % r["osc_id"], False)
        v = float(sub[r["material_id"]]["verified_score"])
        d = abs(calc - v)
        worst = max(worst, d)
        if d > 1e-3:
            over += 1
    check("max |recomputed - verified| <= 1e-3", worst <= 1e-3, "%.5f" % worst)
    check("no row exceeds 1e-3", over == 0, str(over))
    check("85 rows carry a clamped negative A_d", zeroed == 85, str(zeroed))

    print("== 3. the filling grid")
    deltas = sorted({round(float(r["solver_delta"]), 6) for r in active})
    check("18 distinct deltas", len(deltas) == 18, str(len(deltas)))
    nes = sorted({36 - int(round(d * 36)) for d in deltas})
    check("all electron counts even", all(n % 2 == 0 for n in nes), str(nes))
    check("grid spans Ne=2..36", nes[0] == 2 and nes[-1] == 36, "%d..%d" % (nes[0], nes[-1]))
    check("delta*36 integral within 2e-3",
          max(abs(d * 36 - round(d * 36)) for d in deltas) < 2e-3)

    print("== 4. plateau and cliff")
    pts = sorted(((36 - ne) / 36.0, a) for ne, a in table.items())
    plateau = [(d, a) for d, a in pts if d <= 1 / 3.0 + 1e-9]
    check("7 levels on the plateau", len(plateau) == 7, str(len(plateau)))
    pmin, pmax = min(a for _, a in plateau), max(a for _, a in plateau)
    check("plateau spread ~1.52x", close(pmax / pmin, 1.5216, 0.01), "%.4f" % (pmax / pmin))
    a_cliff_from = [a for d, a in pts if close(d, 1 / 3.0, 1e-6)][0]
    a_cliff_to = [a for d, a in pts if close(d, 0.388888, 1e-5)][0]
    check("cliff at delta=1/3 -> 0.389", close(a_cliff_to / a_cliff_from, 1 / 3.3877, 0.01),
          "%.4f -> %.4f" % (a_cliff_from, a_cliff_to))
    check("peak at delta=0.2778", close([d for d, a in pts if a == pmax][0], 0.277778, 1e-5))

    print("== 5. variance decomposition")
    pos = [r for r in active if float(r["nef"]) > 0 and float(r["A_dwave"]) > 0]
    xs = [math.log(float(r["nef"])) for r in pos]
    ys = [math.log(float(r["A_dwave"])) for r in pos]
    zs = [math.log(float(r["nef"]) * float(r["A_dwave"]) * scale) for r in pos]
    n = len(pos)

    def mean(v):
        return sum(v) / len(v)

    def cov(a, b):
        ma, mb = mean(a), mean(b)
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)

    vz, vx, vy, cxy = cov(zs, zs), cov(xs, xs), cov(ys, ys), cov(xs, ys)
    check("share(A_d) ~ 57%", close(vy / vz, 0.570, 0.01), "%.3f" % (vy / vz))
    check("share(N(E_F)) ~ 25%", close(vx / vz, 0.246, 0.01), "%.3f" % (vx / vz))
    check("shares + covariance sum to 1", close(vy / vz + vx / vz + 2 * cxy / vz, 1.0, 1e-9))
    check("976 materials with positive index", n == 976, str(n))

    plat = [r for r in active if float(r["solver_delta"]) <= 1 / 3.0 + 1e-9
            and float(r["nef"]) > 0]
    pz = [math.log(float(r["nef"]) * float(r["A_dwave"]) * scale) for r in plat]
    px = [math.log(float(r["nef"])) for r in plat]
    check("703 materials on the plateau", len(plat) == 703, str(len(plat)))
    check("plateau Spearman(index, N(E_F)) ~ 0.968", close(spearman(px, pz), 0.968, 0.002),
          "%.4f" % spearman(px, pz))

    print("== 6. the board")
    ranked = sorted(active, key=lambda r: -max(0.0, float(r["nef"]) * float(r["A_dwave"]) * scale))
    top1 = ranked[0]
    check("top-1 is I2Mn2S", top1["formula"] == "I2Mn2S", top1["formula"])
    check("top-1 index 64.02", close(float(top1["nef"]) * float(top1["A_dwave"]) * scale, 64.024, 0.01))
    nef_sorted = sorted(active, key=lambda r: -float(r["nef"]))
    check("top-1 has N(E_F) rank 2", nef_sorted[1]["material_id"] == top1["material_id"])
    top20 = ranked[:20]
    check("top-20 all at delta <= 0.2778",
          max(float(r["solver_delta"]) for r in top20) <= 0.2778 + 1e-9,
          "%.4f" % max(float(r["solver_delta"]) for r in top20))
    nef_rank = {r["material_id"]: i + 1 for i, r in enumerate(nef_sorted)}
    check("19 of top-20 have N(E_F) rank <= 20",
          sum(1 for r in top20 if nef_rank[r["material_id"]] <= 20) == 19)

    print("== 7. ED comparison")
    ed = []
    with io.open(os.path.join(DATA, "validation", "comparison_4x4_ED_vs_VMC.md"), encoding="utf-8") as f:
        for line in f:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 4:
                continue
            try:
                ed.append((float(c[0]), float(c[2])))
            except ValueError:
                continue
    check("5 ED fillings parsed", len(ed) == 5, str(len(ed)))
    xs_tab = [d for d, _ in pts]
    ys_tab = [a for _, a in pts]

    def interp(x):
        if x <= xs_tab[0]:
            return ys_tab[0]
        if x >= xs_tab[-1]:
            return ys_tab[-1]
        for i in range(len(xs_tab) - 1):
            if xs_tab[i] <= x <= xs_tab[i + 1]:
                t = (x - xs_tab[i]) / (xs_tab[i + 1] - xs_tab[i])
                return ys_tab[i] + t * (ys_tab[i + 1] - ys_tab[i])
        return ys_tab[-1]

    osc = [interp(1 - nn) for nn, _ in ed]
    rho = spearman(osc, [v for _, v in ed])
    check("Spearman(published, 4x4 ED) = -0.60", close(rho, -0.6, 1e-6), "%.6f" % rho)
    check("published A_d has a node at n=0.5", osc[0] < 0 and ed[0][1] > 0.04,
          "%.4f vs %.4f" % (osc[0], ed[0][1]))

    print("== 8. stress tests are reproducible")
    # shape substitution
    med_ed = sorted(v for _, v in ed)[len(ed) // 2]
    med_osc = sorted(osc)[len(osc) // 2]
    fac = med_osc / med_ed
    ed_xs = [1 - nn for nn, _ in ed]
    ed_ys = [v * fac for _, v in ed]

    def a_shape(d):
        if d > ed_xs[-1] + 1e-9:
            return 0.0
        return max(0.0, interp_ed(ed_xs, ed_ys, d))

    def interp_ed(xx, yy, x):
        if x <= xx[0]:
            return yy[0]
        if x >= xx[-1]:
            return yy[-1]
        for i in range(len(xx) - 1):
            if xx[i] <= x <= xx[i + 1]:
                t = (x - xx[i]) / (xx[i + 1] - xx[i])
                return yy[i] + t * (yy[i + 1] - yy[i])
        return yy[-1]

    base = [r["material_id"] for r in top20]
    shaped = [r["material_id"] for r in sorted(
        active, key=lambda r: -max(0.0, float(r["nef"]) * a_shape(float(r["solver_delta"])) * scale))[:20]]
    check("shape substitution keeps 1 of 20", len(set(base) & set(shaped)) == 1,
          str(len(set(base) & set(shaped))))

    # band: same seed, same random module, same order -> deterministic
    import random
    rng = random.Random(7)
    sigma = 0.8790
    levels = [round(float(r["solver_delta"]), 6) for r in active]
    uniq = sorted(set(levels))
    hits = {m: 0 for m in base}
    first = 0
    ov = 0
    draws = 400
    for _ in range(draws):
        eps = {d: rng.gauss(0.0, sigma) for d in uniq}
        sc = {}
        for r in active:
            d = round(float(r["solver_delta"]), 6)
            sc[r["material_id"]] = max(0.0, float(r["nef"]) * table.get(36 - int(round(d * 36)), 0.0)
                                       * math.exp(eps[d]) * scale)
        order = sorted(sc, key=lambda m: -sc[m])[:20]
        ov += len(set(base) & set(order))
        for m in base:
            if m in order:
                hits[m] += 1
        if order and order[0] == base[0]:
            first += 1
    check("band overlap in [0.35,0.55] of 20", 0.35 <= ov / float(draws * 20) <= 0.55,
          "%.3f" % (ov / float(draws * 20)))
    check("no top-20 item survives more than 2/3",
          max(hits.values()) / float(draws) <= 0.68, "%.2f" % (max(hits.values()) / float(draws)))
    check("top-1 keeps first place < 1/3 of draws", first / float(draws) < 0.34,
          "%.2f" % (first / float(draws)))

    print("== 9. the screener's out-of-sample numbers")
    import collections
    ELEM = re.compile(r"([A-Z][a-z]?)(\d*)")

    def vec(f):
        d = collections.defaultdict(int)
        for e, k in ELEM.findall(f):
            d[e] += int(k) if k else 1
        tot = float(sum(d.values()))
        return {e: v / tot for e, v in d.items()}

    def cos(a, b):
        if len(a) > len(b):
            a, b = b, a
        num = sum(v * b.get(k, 0.0) for k, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return num / (na * nb) if na and nb else 0.0

    vs = [vec(r["formula"]) for r in active]
    nef_log = [math.log(float(r["nef"])) for r in active]
    D = [round(float(r["solver_delta"]), 4) for r in active]
    pred, dpred = [], []
    for i in range(len(active)):
        sims = sorted(((cos(vs[i], vs[j]), j) for j in range(len(active)) if j != i),
                      reverse=True)[:15]
        w = [max(0.0, s) + 1e-6 for s, _ in sims]
        pred.append(sum(wi * nef_log[j] for wi, (_, j) in zip(w, sims)) / sum(w))
        votes = collections.Counter()
        for wi, (_, j) in zip(w, sims):
            votes[D[j]] += wi
        dpred.append(votes.most_common(1)[0][0])
    resid = [p - t for p, t in zip(pred, nef_log)]
    ssr = sum(r * r for r in resid)
    sst = sum((t - sum(nef_log) / len(nef_log)) ** 2 for t in nef_log)
    r2 = 1 - ssr / sst
    mae = sum(abs(r) for r in resid) / len(resid)
    check("screener R2 ~ 0.12", 0.08 <= r2 <= 0.16, "%.3f" % r2)
    check("screener MAE ~ 0.45", 0.42 <= mae <= 0.48, "%.3f" % mae)
    acc = sum(1 for a, b in zip(dpred, D) if a == b) / float(len(D))
    check("delta exact ~ 17%", 0.15 <= acc <= 0.20, "%.3f" % acc)

    print("== 10. artefacts")
    for p in ("out/results.json", "out/report.html", "site/index.html",
              "out/figures/dome.svg", "out/figures/board.svg", "out/figures/scatter.svg",
              "out/figures/ed.svg", "out/figures/survival.svg", "out/figures/screen.svg"):
        check("exists %s" % p, os.path.exists(os.path.join(HERE, p)))
    html = io.open(os.path.join(HERE, "out", "report.html"), encoding="utf-8").read()
    for token in ("64.02", "1,073", "0.968", "-0.60", "18"):
        check("report mentions %s" % token, token in html)
    nfig = html.count("<svg")
    check("report embeds 6 figures", nfig == 6, str(nfig))

    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    if FAIL:
        print("failed: " + ", ".join(FAIL))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
