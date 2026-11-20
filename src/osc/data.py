"""Load and validate the OSC public tables. No network, no deps."""
import csv
import hashlib
import io
import json
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_active():
    """Active challenge set: one row per material with the effective model."""
    def opt(s):
        return None if s.strip() in ("", "None") else float(s)

    out = []
    for r in _rows("active_challenge.csv"):
        out.append(dict(
            osc_id=r["osc_id"], material_id=r["material_id"], formula=r["formula"],
            family=r["family"], nef=float(r["nef"]), a_d=float(r["A_dwave"]),
            delta=float(r["solver_delta"]), t=float(r["t_ev"]), u=float(r["U_ev"]),
            u_over_t=float(r["U_over_t"]), n_band=float(r["n_band"]),
            delta_hole=opt(r["delta_hole"]), nef_method=r["nef_method"],
        ))
    return out


def load_candidates():
    out = {}
    for r in _rows("candidates.csv"):
        out[r["material_id"]] = dict(
            osc_id=r["osc_id"], material_id=r["material_id"], formula=r["formula"],
            family=r["family"], elements=r["elements"], is_metal=r["is_metal"],
            gap=float(r["gap_pbe"]) if r["gap_pbe"] not in ("", "None") else None,
            magnetic=r["magnetic"], n_atoms=int(r["n_atoms"]),
            weight_class=r["weight_class"], score_mult=float(r["score_mult"]),
            sc_relevance=float(r["sc_relevance"]),
        )
    return out


def load_submissions():
    out = {}
    for r in _rows("submissions.csv"):
        out[r["material_id"]] = dict(
            material_id=r["material_id"], author=r["author"],
            method_name=r["method_name"],
            provisional=float(r["provisional_score"]),
            verified=float(r["verified_score"]),
            is_anchor=r["is_anchor"] == "true",
            verify_note=r["verify_note"],
        )
    return out


def load_scoring_meta():
    with io.open(os.path.join(DATA, "scoring_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    # key Ne (electrons on the 6x6 cluster) -> A_d ; delta is 1 - Ne/36
    return {int(k): float(v[1]) for k, v in meta["A_by_Ne"].items()}, float(meta["scale"])


def dataset_digest():
    files = ["active_challenge.csv", "candidates.csv", "submissions.csv",
             "scoring_meta.json", "README.md", "validation/multisize_ED_table_kuku.md",
             "validation/comparison_4x4_ED_vs_VMC.md"]
    out = {}
    for name in files:
        p = os.path.join(DATA, name.replace("/", os.sep))
        out[name] = sha256(p) if os.path.exists(p) else None
    return out
