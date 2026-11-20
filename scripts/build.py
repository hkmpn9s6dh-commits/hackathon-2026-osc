# -*- coding: utf-8 -*-
"""Build every number and figure in the report from the frozen dataset.

Usage:  py -3 scripts/build.py
Writes: out/results.json, out/figures/*.svg, out/report.html, site/index.html
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "src"))

from osc import analysis as AN          # noqa: E402
from osc import data as D               # noqa: E402
from osc import ed as ED                # noqa: E402
from osc import screen as SC            # noqa: E402
from osc.figs import (fig_dome, fig_board, fig_scatter, fig_ed, fig_survival,  # noqa: E402
                      fig_screen)
from osc.report import render_report, render_site  # noqa: E402

OUT = os.path.join(HERE, "out")
FIG = os.path.join(OUT, "figures")


def main():
    os.makedirs(FIG, exist_ok=True)
    active = D.load_active()
    candidates = D.load_candidates()
    subs = D.load_submissions()
    table, scale = D.load_scoring_meta()

    # ---- 1. reproduction -------------------------------------------------
    rep = AN.reproduce(active, table, scale, subs)
    diffs = [r["diff"] for r in rep if r["diff"] is not None]
    repro = dict(
        n=len(rep), n_with_verified=len(diffs),
        max_abs_diff=max(diffs), n_over_1e_3=sum(1 for x in diffs if x > 1e-3),
        n_a_row_zeroed=sum(1 for r in rep if not r["a_matches_row"]),
        rule="index = max(0, N(E_F) * A_d(delta) * 300)",
        rounding="published verified_score is rounded to 3 decimals",
    )

    # ---- 2. the filling grid --------------------------------------------
    grid = AN.grid(active)
    domain = {d: sum(1 for m in active if abs(m["delta"] - d) < 1e-6) for d in grid["deltas"]}

    # ---- 3. the curve ----------------------------------------------------
    dome = AN.dome(table)
    dome["plateau"]["n_materials"] = sum(1 for m in active
                                        if AN.is_plateau(m["delta"], dome))
    dec = AN.decomposition(active, scale)
    pdec = AN.plateau_decomposition(active, dome, scale)

    # ---- 4. the board ----------------------------------------------------
    board = AN.board(active, 20, scale)
    board_stats = dict(
        top20_max_delta=max(r["delta"] for r in board),
        top20_levels=sorted({round(r["delta"], 4) for r in board}),
        top1=board[0], top2=board[1],
        top1_nef_rank=board[0]["nef_rank"],
        share_top20_nef_rank_le_20=sum(1 for r in board if r["nef_rank"] <= 20) / 20.0,
    )
    robust = AN.robust_ranking(active, dome, scale, 10)

    # ---- 5. ED comparison -----------------------------------------------
    curve = ED.curve_comparison(table)
    rho_curve = AN.spearman([p["osc"] for p in curve], [p["ed"] for p in curve])
    spreads = ED.cluster_spread()
    sigma = ED.sigma_from_spread(spreads)

    # ---- 6. stress tests -------------------------------------------------
    stress = ED.stress_shape(table, active, scale, 20, sigma=sigma, draws=4000)
    st = dict(
        sigma=stress["sigma"], draws=stress["draws"],
        overlap_shape=stress["overlap_shape"],
        expected_overlap=stress["expected_overlap"],
        expected_overlap_frac=stress["expected_overlap_frac"],
        survival=stress["survival"], first=stress["first"],
        shape_board=stress["shape"][:10],
    )

    # ---- 7. the screener -------------------------------------------------
    pool = [c for c in candidates.values()
            if c["is_metal"] == "True"
            and c["material_id"] not in {m["material_id"] for m in active}]
    cv = SC.loo_cv(active, 15)
    screened = SC.screen_pool(active, pool, 15)
    screened.sort(key=lambda r: -r["pred_nef"])
    # Discovery nominations: composition siblings of the board leaders. The argument is
    # chemistry (same elements, same or related stoichiometry), NOT the screener -- the
    # screener's out-of-sample R2 above says it cannot rank N(E_F).
    nominate = [("2IMnS-1", "1SI2Mn2-1", "同元素，富硫"),
                ("1FeBr2-1", "2BrFe-1", "同计量比，不同多型"),
                ("1FeBr2-2", "2BrFe-1", "同计量比，不同多型"),
                ("2FeI3-1", "2FeI-1", "同元素，富碘"),
                ("1FeI2-1", "2FeI-1", "同计量比，不同多型")]
    smap = {r["material_id"]: r for r in screened}
    amap = {m["material_id"]: m for m in active}
    nominations = []
    for mid, parent, relation in nominate:
        if mid in smap:
            r = dict(smap[mid])
            p = amap[parent]
            r.update(relation=relation, parent=parent, parent_formula=p["formula"],
                     parent_nef=p["nef"], parent_delta=p["delta"],
                     parent_index=AN.index(p["nef"], p["a_d"], scale))
            nominations.append(r)

    # ---- 8. assemble -----------------------------------------------------
    results = dict(
        meta=dict(
            challenge="Open Superconductor Challenge (FINAL-Bench)",
            dataset_revision="4585236f24ff4e9a9d7cee24a4ee38724248ecb7",
            dataset_url="https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor",
            files=D.dataset_digest(),
            n_active=len(active), n_candidates=len(candidates),
            n_submissions=len(subs), n_pool=len(pool),
            scale=scale,
        ),
        reproduction=repro,
        grid=dict(n_delta=grid["n_delta"], ne_steps=grid["ne_steps"],
                  on_even_grid=grid["on_even_grid"], domain=domain),
        dome=dome,
        decomposition=dec,
        plateau_decomposition=pdec,
        board=board,
        board_stats=board_stats,
        robust=robust,
        ed=dict(curve=curve, spearman=rho_curve,
                spreads=[dict(n=s["n"], clusters=s["clusters"], values=s["values"],
                              spread=s["spread"], signs=s["signs"]) for s in spreads],
                sigma=sigma),
        stress=st,
        screen=dict(cv=cv, n_pool=len(pool),
                    max_pred_nef=max(r["pred_nef"] for r in screened),
                    top=screened[:10], nominations=nominations),
    )
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    # ---- 9. figures ------------------------------------------------------
    svg = dict(
        dome=fig_dome(dome, grid),
        board=fig_board(board, board_stats),
        scatter=fig_scatter(active, dome),
        ed=fig_ed(curve, rho_curve),
        survival=fig_survival(board, stress),
        screen=fig_screen(SC.loo_pairs(active, 15), cv),
    )
    for name, body in svg.items():
        with open(os.path.join(FIG, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(body)

    # ---- 10. report + site ----------------------------------------------
    with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as f:
        f.write(render_report(results, svg))
    os.makedirs(os.path.join(HERE, "site"), exist_ok=True)
    with open(os.path.join(HERE, "site", "index.html"), "w", encoding="utf-8") as f:
        f.write(render_site(results, svg))

    # GitHub Pages serves /docs
    docs = os.path.join(HERE, "docs")
    os.makedirs(docs, exist_ok=True)
    with io.open(os.path.join(docs, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_site(results, svg))
    with io.open(os.path.join(docs, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    print("wrote out/results.json, %d figures, out/report.html, site/index.html, docs/index.html"
          % len(svg))
    print("top1=%s %.2f | overlap_shape=%d/20 | band_overlap=%.2f"
          % (board[0]["formula"], board[0]["index"], st["overlap_shape"],
             st["expected_overlap"]))


if __name__ == "__main__":
    main()
