# -*- coding: utf-8 -*-
"""Emit the files a participant would hand to the organisers.

Discovery nominations follow the shape of the public submissions/*.json files; the
Method package is a reproducibility bundle (config + run.sh + SHA256 manifest).
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
SUB = os.path.join(HERE, "submission")

RUN_SH = """#!/bin/sh
# Reproduce every number in the OSC audit. Pure Python 3.8+, no network, no deps.
set -e
cd "$(dirname "$0")/.."
py -3 scripts/build.py
py -3 verify/verify.py
"""


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    R = json.load(io.open(os.path.join(OUT, "results.json"), encoding="utf-8"))
    os.makedirs(os.path.join(SUB, "discovery"), exist_ok=True)
    os.makedirs(os.path.join(SUB, "method"), exist_ok=True)

    for n in R["screen"]["nominations"]:
        doc = dict(
            track="discovery",
            material_id=n["material_id"],
            osc_id=n["osc_id"],
            formula=n["formula"],
            author="CB (WorkBuddy agent, on behalf of the account owner)",
            method_name="composition sibling of a verified leader",
            relation=n["relation"],
            parent=dict(material_id=n["parent"], formula=n["parent_formula"],
                        nef=n["parent_nef"], delta=n["parent_delta"],
                        verified_index=n["parent_index"]),
            claimed_index=None,
            note=("Proposed as a downfolding target, not as a score claim. Composition "
                  "screening cannot rank N(E_F) out of sample (R2=%.3f), so no numeric "
                  "prediction is offered; the argument is chemical (same elements, same or "
                  "related stoichiometry as a verified leader)." % R["screen"]["cv"]["r2"]),
        )
        with io.open(os.path.join(SUB, "discovery", n["material_id"] + ".json"), "w",
                     encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)

    method = dict(
        track="method",
        title="The OSC index is a step function of band filling: a reproducibility audit "
              "and a rank-robustness test",
        author="CB (WorkBuddy agent, on behalf of the account owner)",
        scope="audit of the published tables; no private solver was re-run",
        key_numbers=dict(
            reproduced=R["reproduction"]["n_covered"],
            rows_total=R["reproduction"]["n"],
            rows_in_table_holes=R["reproduction"]["n_uncovered"],
            max_abs_diff=R["reproduction"]["max_abs_diff"],
            delta_levels=R["grid"]["n_delta"],
            positive_levels=R["dome"]["positive_levels"],
            half_filling_a_d=R["half_filling"]["a_d"],
            half_filling_share_of_peak=R["half_filling"]["share_of_peak"],
            materials_at_half_filling=R["half_filling"]["n_materials"],
            plateau_levels=len([p for p in R["dome"]["points"]
                                if p["delta"] <= R["dome"]["plateau"]["max_delta"] + 1e-9]),
            plateau_spread=R["dome"]["plateau"]["spread"],
            cliff_ratio=R["dome"]["cliff"]["ratio"],
            share_a_d=R["decomposition"]["share_a"],
            share_nef=R["decomposition"]["share_nef"],
            plateau_spearman=R["plateau_decomposition"]["spearman"],
            ed_spearman=R["ed"]["spearman"],
            ed_spearman_p_perm=R["ed"]["p_perm"],
            ed_spearman_on_grid=R["ed"]["grid_spearman"],
            top20_overlap_shape=R["stress"]["overlap_shape"],
            top20_overlap_global=R["stress"]["structures"]["global"]["expected_overlap"],
            top20_overlap_ar1=R["stress"]["structures"]["ar1"]["expected_overlap"],
            top20_overlap_independent=R["stress"]["structures"]["independent"]["expected_overlap"],
            screener_r2=R["screen"]["cv"]["r2"],
            screener_leader_ratio=[round(l["nef"] / l["pred_nef"], 2) for l in R["screen"]["leaders"]],
        ),
        how_to_reproduce=["./submission/method/run.sh",
                          "py -3 scripts/build.py",
                          "py -3 verify/verify.py"],
        claims=[
            "1064 of the 1073 verified scores are recomputed from (N(E_F), delta) plus the "
            "published A_d table to better than 1e-3; the remaining 9 sit at Ne=4,6,8, where "
            "the table has no entry and the dump writes 0.",
            "The shipped table contradicts the challenge README at half filling: 0.03844 "
            "(66% of the peak) at delta=0, where the README says A_d vanishes. 120 materials "
            "(11%) sit on that level.",
            "A_d takes 12 positive values; the seven levels with delta<=1/3 span 1.52x and "
            "the next step drops 3.4x. Inside the plateau the board is the N(E_F) ranking "
            "(Spearman 0.97).",
            "The #1 material sits exactly on the argmax of A_d; the #2 has 12% higher N(E_F) "
            "and loses 14% of index.",
            "ED cannot adjudicate the shape (n=5, permutation p=0.35, rho -0.60 to -0.72), "
            "but substituting the ED shape leaves 4 of the top-20 in place.",
            "Rank stability depends on the error structure, not its size: global rescale "
            "20/20, AR(1) 15/20, independent 9/20. The '28% chance' reading is an i.i.d. "
            "artefact and is withdrawn.",
            "The composition-only screener fails its sanity check (leaders under-predicted "
            "3.7x-8.6x), so it cannot say whether the un-downfolded pool contains a "
            "challenger.",
        ],
        limitations=[
            "The organisers' 6x6 solver is not public and was not re-run.",
            "4x4 ED has a different maximum distance from 6x6; only shape and order are "
            "compared, not absolute amplitudes.",
            "The perturbation band is a proxy for method uncertainty, not a confidence "
            "interval; only the ordering of the three error structures is robust.",
            "The Discovery nominations carry no numeric prediction and rest on composition "
            "analogy only.",
        ],
    )
    with io.open(os.path.join(SUB, "method", "package.json"), "w", encoding="utf-8") as f:
        json.dump(method, f, ensure_ascii=False, indent=1)

    run = os.path.join(SUB, "method", "run.sh")
    with io.open(run, "w", encoding="utf-8", newline="\n") as f:
        f.write(RUN_SH)

    files = ["out/results.json", "out/report.html", "src/osc/analysis.py", "src/osc/ed.py",
             "src/osc/screen.py", "verify/verify.py", "scripts/build.py",
             "data/active_challenge.csv", "data/scoring_meta.json"]
    with io.open(os.path.join(SUB, "method", "SHA256SUMS"), "w", encoding="utf-8",
                 newline="\n") as f:
        for rel in files:
            f.write("%s  %s\n" % (sha(os.path.join(HERE, rel)), rel))

    print("wrote %d discovery nominations + method package" % len(R["screen"]["nominations"]))


if __name__ == "__main__":
    main()
