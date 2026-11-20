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
            reproduced=R["reproduction"]["n"],
            max_abs_diff=R["reproduction"]["max_abs_diff"],
            delta_levels=R["grid"]["n_delta"],
            plateau_levels=len([p for p in R["dome"]["points"]
                                if p["delta"] <= R["dome"]["plateau"]["max_delta"] + 1e-9]),
            plateau_spread=R["dome"]["plateau"]["spread"],
            cliff_ratio=R["dome"]["cliff"]["ratio"],
            share_a_d=R["decomposition"]["share_a"],
            share_nef=R["decomposition"]["share_nef"],
            plateau_spearman=R["plateau_decomposition"]["spearman"],
            ed_spearman=R["ed"]["spearman"],
            top20_overlap_shape=R["stress"]["overlap_shape"],
            top20_overlap_band=R["stress"]["expected_overlap"],
            top1_stays_first=R["stress"]["first"][R["board_stats"]["top1"]["material_id"]],
        ),
        how_to_reproduce=["./submission/method/run.sh",
                          "py -3 scripts/build.py",
                          "py -3 verify/verify.py"],
        claims=[
            "Every one of the 1073 verified scores is recomputed from (N(E_F), delta) plus "
            "the published A_d table, to better than 1e-3.",
            "A_d depends only on delta; the index is therefore N(E_F) times a step function "
            "with 15 values, 7 of them on a plateau that spans only 1.52x.",
            "Inside the plateau the board is the N(E_F) ranking (Spearman 0.97).",
            "The shape of A_d(delta) is not reproduced by the unbiased 4x4 ED that the "
            "challenge ships (Spearman -0.60); substituting the ED shape leaves 1 of the "
            "top-20 in place.",
        ],
        limitations=[
            "The organisers' 6x6 solver is not public and was not re-run.",
            "4x4 ED has a different maximum distance from 6x6; only shape and order are "
            "compared, not absolute amplitudes.",
            "The perturbation band is a proxy for method uncertainty, not a confidence "
            "interval.",
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
