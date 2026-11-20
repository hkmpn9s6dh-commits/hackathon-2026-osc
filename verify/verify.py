# -*- coding: utf-8 -*-
"""Gate B: independent re-derivation of every number in the report.

Deliberately does NOT read out/results.json for the numbers it checks: it re-derives them
from the raw tables. If a number in the report drifts, this fails.

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
sys.path.insert(0, os.path.join(HERE, "src"))

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
    from osc.analysis import spearman as sp
    return sp(a, b)


def failed_names():
    return list(FAIL)


def main():
    print("== 1. dataset integrity")
    man = os.path.join(DATA, "SHA256SUMS")
    check("SHA256 manifest exists", os.path.exists(man))
    if os.path.exists(man):
        with io.open(man, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                digest, name = line.split()
                p = os.path.join(DATA, name)
                check("hash %s" % name, os.path.exists(p) and sha(p) == digest)

    from osc import data as DD
    raw = rows("active_challenge.csv")
    active = DD.load_active()
    cand = rows("candidates.csv")
    subs = rows("submissions.csv")
    meta = json.load(io.open(os.path.join(DATA, "scoring_meta.json"), encoding="utf-8"))
    table = {int(k): float(v[1]) for k, v in meta["A_by_Ne"].items()}
    scale = float(meta["scale"])

    check("active rows = 1073", len(raw) == 1073, str(len(active)))
    check("candidate rows = 4832", len(cand) == 4832, str(len(cand)))
    check("submission rows = 1073", len(subs) == 1073, str(len(subs)))
    check("scale = 300", close(scale, 300.0))
    check("A_d table has 15 entries", len(table) == 15, str(len(table)))
    check("all rows are organiser anchors", all(r["is_anchor"] == "true" for r in subs))
    check("all anchors authored by OSC-66", {r["author"] for r in subs} == {"OSC-66"})

    print("== 2. reproduction, and the two holes in it")
    sub = {r["material_id"]: r for r in subs}
    worst, over, covered, uncovered = 0.0, 0, 0, 0
    neg_table, neg_zero, neg_kept = 0, 0, 0
    for r in raw:
        ne = 36 - int(round(float(r["solver_delta"]) * 36))
        a_tab = table.get(ne)
        a_row = float(r["A_dwave"])
        if a_tab is None:
            uncovered += 1
            check("uncovered row has row A_d = 0 (%s)" % r["osc_id"], a_row == 0.0)
        else:
            covered += 1
            if a_tab < 0:
                neg_table += 1
                if a_row == 0.0:
                    neg_zero += 1
                elif a_row == a_tab:
                    neg_kept += 1
                else:
                    check("negative A_d row is 0 or the table value (%s)" % r["osc_id"], False)
            elif a_row != a_tab:
                check("positive A_d row equals the table (%s)" % r["osc_id"], False)
        calc = max(0.0, float(r["nef"]) * (a_tab if a_tab is not None else 0.0) * scale)
        v = float(sub[r["material_id"]]["verified_score"])
        d = abs(calc - v)
        worst = max(worst, d)
        if d > 1e-3:
            over += 1
    check("1064 rows are covered by the table", covered == 1064, str(covered))
    check("9 rows fall in table holes (Ne=4,6,8)", uncovered == 9, str(uncovered))
    check("max |recomputed - verified| <= 1e-3", worst <= 1e-3, "%.6f" % worst)
    check("no row exceeds 1e-3", over == 0, str(over))
    check("88 rows sit on a negative table value", neg_table == 88, str(neg_table))
    check("85 of them are written as 0", neg_zero == 85, str(neg_zero))
    check("3 of them keep the negative value", neg_kept == 3, str(neg_kept))

    print("== 3. filling grid")
    deltas = sorted({round(float(r["solver_delta"]), 6) for r in raw})
    check("18 distinct deltas", len(deltas) == 18, str(len(deltas)))
    nes = sorted({36 - int(round(d * 36)) for d in deltas})
    check("all electron counts even", all(n % 2 == 0 for n in nes), str(nes))
    check("grid spans Ne=2..36", nes[0] == 2 and nes[-1] == 36)
    check("delta*36 integral within 2e-3",
          max(abs(d * 36 - round(d * 36)) for d in deltas) < 2e-3)
    pos = sorted({v for v in table.values() if v > 0})
    check("12 distinct positive A_d values", len(pos) == 12, str(len(pos)))
    check("missing Ne entries are 0,4,6,8",
          [n for n in range(0, 37, 2) if n not in table] == [0, 4, 6, 8])

    print("== 4. half filling")
    hf = [r for r in raw if abs(float(r["solver_delta"])) < 1e-9]
    check("120 materials at half filling", len(hf) == 120, str(len(hf)))
    check("half-filling A_d = 0.03844", close(table[36], 0.03844, 1e-9), str(table[36]))
    check("half-filling is 65.7% of the peak",
          close(table[36] / max(table.values()), 0.6572, 0.001),
          "%.4f" % (table[36] / max(table.values())))

    print("== 5. plateau and cliff")
    pts = sorted(((36 - ne) / 36.0, a) for ne, a in table.items())
    plateau = [(d, a) for d, a in pts if d <= 1 / 3.0 + 1e-9]
    check("7 levels on the plateau", len(plateau) == 7, str(len(plateau)))
    pmin, pmax = min(a for _, a in plateau), max(a for _, a in plateau)
    check("plateau spread ~1.52x", close(pmax / pmin, 1.5216, 0.01), "%.4f" % (pmax / pmin))
    a_from = [a for d, a in pts if close(d, 1 / 3.0, 1e-6)][0]
    a_to = [a for d, a in pts if close(d, 0.388888, 1e-5)][0]
    check("cliff ratio 3.387", close(a_from / a_to, 3.3877, 0.01), "%.4f" % (a_from / a_to))
    check("peak at delta=0.2778", close([d for d, a in pts if a == pmax][0], 0.277778, 1e-4))

    print("== 6. variance decomposition")
    act = [r for r in raw if float(r["nef"]) > 0 and float(r["A_dwave"]) > 0]
    xs = [math.log(float(r["nef"])) for r in act]
    ys = [math.log(float(r["A_dwave"])) for r in act]
    zs = [math.log(float(r["nef"]) * float(r["A_dwave"]) * scale) for r in act]

    def mean(v):
        return sum(v) / len(v)

    def cov(a, b):
        ma, mb = mean(a), mean(b)
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)

    vz, vx, vy, cxy = cov(zs, zs), cov(xs, xs), cov(ys, ys), cov(xs, ys)
    check("share(A_d) ~ 57%", close(vy / vz, 0.570, 0.01), "%.3f" % (vy / vz))
    check("share(N(E_F)) ~ 25%", close(vx / vz, 0.246, 0.01), "%.3f" % (vx / vz))
    check("shares + covariance sum to 1", close(vy / vz + vx / vz + 2 * cxy / vz, 1.0, 1e-9))
    plat = [r for r in raw if float(r["solver_delta"]) <= 1 / 3.0 + 1e-9
            and float(r["nef"]) > 0 and float(r["A_dwave"]) > 0]
    pz = [math.log(float(r["nef"]) * float(r["A_dwave"]) * scale) for r in plat]
    px = [math.log(float(r["nef"])) for r in plat]
    check("703 materials on the plateau", len(plat) == 703, str(len(plat)))
    check("plateau Spearman(index, N(E_F)) ~ 0.968",
          close(spearman(px, pz), 0.968, 0.002), "%.4f" % spearman(px, pz))

    print("== 7. the board")
    ranked = sorted(active, key=lambda r: -max(0.0, r["nef"] * r["a_d"] * scale))
    top1 = ranked[0]
    check("top-1 is I2Mn2S", top1["formula"] == "I2Mn2S", top1["formula"])
    check("top-1 index 64.02", close(top1["nef"] * top1["a_d"] * scale, 64.024, 0.01))
    check("top-1 sits exactly on the A_d peak", close(top1["delta"], 0.277778, 1e-4))
    nef_sorted = sorted(active, key=lambda r: -r["nef"])
    check("top-1 has N(E_F) rank 2", nef_sorted[1]["material_id"] == top1["material_id"])
    top20 = ranked[:20]
    check("top-20 all at delta <= 0.2778", max(r["delta"] for r in top20) <= 0.2778 + 1e-9)
    nef_rank = {r["material_id"]: i + 1 for i, r in enumerate(nef_sorted)}
    check("19 of top-20 have N(E_F) rank <= 20",
          sum(1 for r in top20 if nef_rank[r["material_id"]] <= 20) == 19)

    print("== 8. ED comparison")
    from osc import ed as ED
    cc = ED.curve_comparison(table)
    check("5 ED fillings", len(cc) == 5, str(len(cc)))
    check("curve is sorted by delta", [p["delta"] for p in cc] == sorted(p["delta"] for p in cc))
    rho = spearman([p["osc"] for p in cc], [p["ed"] for p in cc])
    check("Spearman = -0.60", close(rho, -0.6, 1e-6), "%.4f" % rho)
    check("public value has a node at n=0.5", [p for p in cc if close(p["n"], 0.5)][0]["osc"] < 0)
    check("ED at n=0.5 is positive", [p for p in cc if close(p["n"], 0.5)][0]["ed"] > 0.04)
    check("ED at n=0.5 is ~97% band effect",
          close([p for p in cc if close(p["n"], 0.5)][0]["ed_u0"]
                / [p for p in cc if close(p["n"], 0.5)][0]["ed"], 0.975, 0.01))
    check("grid Spearman ~ -0.72", close(ED.ed_grid_spearman(table), -0.7193, 0.01),
          "%.4f" % ED.ed_grid_spearman(table))

    print("== 9. stress tests")
    st = ED.stress_shape(table, active, scale, 20, draws=600)
    check("ED shape is positive at the published peak",
          st["shape_a"][0.2778] > 0.03, str(st["shape_a"][0.2778]))
    check("ED shape at delta=0.5 exceeds its value at 0.2778",
          st["shape_a"][0.5] > st["shape_a"][0.2778])
    check("shape substitution keeps 4 of 20", st["overlap_shape"] == 4, str(st["overlap_shape"]))
    s = st["structures"]
    check("global rescale leaves 20 of 20", close(s["global"]["expected_overlap"], 20.0, 0.01))
    check("AR(1) leaves 12-17 of 20", 12 <= s["ar1"]["expected_overlap"] <= 17,
          "%.2f" % s["ar1"]["expected_overlap"])
    check("independent leaves 7-11 of 20", 7 <= s["independent"]["expected_overlap"] <= 11,
          "%.2f" % s["independent"]["expected_overlap"])
    check("i.i.d. is the worst of the three",
          s["independent"]["expected_overlap"] < s["ar1"]["expected_overlap"]
          < s["global"]["expected_overlap"])
    check("overlap falls as sigma grows",
          all(a["expected_overlap"] > b["expected_overlap"]
              for a, b in zip(st["sweep"], st["sweep"][1:])))

    print("== 10. the screener, and its sanity check")
    from osc import screen as SC
    cv = SC.loo_cv(active, 15)
    check("screener R2 in [0.08,0.16]", 0.08 <= cv["r2"] <= 0.16, "%.3f" % cv["r2"])
    check("screener MAE in [0.42,0.48]", 0.42 <= cv["mae"] <= 0.48, "%.3f" % cv["mae"])
    leaders = SC.recover_leaders(active)
    check("three leaders recovered by the check", len(leaders) == 3, str(len(leaders)))
    check("every leader is under-predicted by >= 3x",
          all(l["nef"] / l["pred_nef"] >= 3.0 for l in leaders),
          str([round(l["nef"] / l["pred_nef"], 2) for l in leaders]))

    print("== 11. artefacts")
    for p in ("out/results.json", "out/report.html", "docs/index.html",
              "out/figures/dome.svg", "out/figures/board.svg", "out/figures/scatter.svg",
              "out/figures/ed.svg", "out/figures/survival.svg", "out/figures/screen.svg",
              "out/figures/structures.svg"):
        check("exists %s" % p, os.path.exists(os.path.join(HERE, p)))
    html = io.open(os.path.join(HERE, "out", "report.html"), encoding="utf-8").read()
    for token in ("64.02", "1,064", "0.0384", "19.7", "0.968"):
        check("report mentions %s" % token, token in html)
    check("no unreplaced placeholder", "{poslev}" not in html and "{css}" not in html)
    nfig = html.count("<svg")
    check("report embeds 7 figures", nfig == 7, str(nfig))

    with io.open(os.path.join(OUT, "verify.json"), "w", encoding="utf-8") as f:
        json.dump(dict(passed=len(PASS), failed=len(FAIL), names=list(PASS)),
                  f, ensure_ascii=False, indent=1)
    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    if FAIL:
        print("failed: " + ", ".join(FAIL))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
