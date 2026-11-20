# -*- coding: utf-8 -*-
"""Assemble the honest, per-material OSC tables from the downfolded + solved data.

verified_score = N(E_F) [states/eV/atom] * A_d(delta_material) * SCALE
  - N(E_F): Gaussian DOS at E_F from the SCF (states/eV/atom)
  - A_d(delta): max-distance d-wave pair correlation from the 6x6 solver run AT THIS
    material's DFT band filling (per-material; varies with doping via the d-wave dome)
  - SCALE: one fixed, monotone readability factor used EVERYWHERE (instrument + leaderboard)

Writes active_challenge.csv (enriched, honest columns) and submissions.csv (verified anchors,
single consistent scale). Also prints the per-filling A_d(delta) table for documentation.
"""
import os, csv, json, glob, io, urllib.request

SCALE = float(os.environ.get("OSC_SCALE", "100.0"))
DS = "FINAL-Bench/OSC-Superconductor"
BASE = f"https://huggingface.co/datasets/{DS}/resolve/main"


def load_existing_active():
    try:
        with urllib.request.urlopen(BASE + "/active_challenge.csv", timeout=25) as r:
            return {row["c2db_uid"]: row for row in csv.DictReader(io.StringIO(r.read().decode()))}
    except Exception:
        return {}


def load_candidates():
    """Full universe -> formula / family / osc_id / weight_class / sc_relevance by material_id."""
    try:
        with urllib.request.urlopen(BASE + "/candidates.csv", timeout=40) as r:
            return {row.get("material_id"): row for row in csv.DictReader(io.StringIO(r.read().decode()))}
    except Exception:
        return {}


def derive_formula(uid):
    import re
    m = re.match(r"\d*([A-Za-z0-9]+?)-\d+$", uid)
    return m.group(1) if m else uid


def main():
    solved = [json.load(open(f)) for f in glob.glob("solved/*.json")]
    solved = [s for s in solved if s.get("A_dwave") is not None]
    old = load_existing_active()
    cand = load_candidates()

    def meta(uid, key, default=""):
        c = cand.get(uid, {}) or old.get(uid, {})
        return c.get(key) or default

    # stable osc_id: reuse candidates/old, else assign new
    nextid = [90000]
    def osc_id_for(uid):
        oid = meta(uid, "osc_id")
        if oid:
            return oid
        nextid[0] += 1
        return f"OSC-{nextid[0]}"
    # A_d(Ne) dome table from solved materials (for particle-hole remap)
    A_by_Ne = {s["solver_Ne"]: s["A_dwave"] for s in solved if s.get("A_dwave") is not None}
    T_MIN = 0.01  # eV; below this the single-band effective model is ill-defined (U/t -> inf)
    # verified score per material, with two honest fixes:
    #   fix4: t<T_MIN (e.g. 2CuO-1 t=0.0002) -> effective model ill-defined, excluded from scoring
    #   fix5: n_band>1 (Ne>36) -> particle-hole symmetry, A_d(Ne)=A_d(72-Ne)
    kept, excluded = [], []
    for s in solved:
        t = s.get("t_ev"); Ne = s.get("solver_Ne")
        if t is None or float(t) < T_MIN:
            s["status"] = "excluded"; s["exclude_reason"] = f"effective model ill-defined (t={t} eV < {T_MIN})"
            excluded.append(s); continue
        Ad = s.get("A_dwave")
        if Ne is not None and Ne > 36:                       # electron-doped past half-filling
            Ne_eff = 72 - Ne
            Ad = A_by_Ne.get(Ne_eff, Ad); s["ph_mapped"] = True; s["Ne_eff"] = Ne_eff
        if Ad is None:
            s["status"] = "excluded"; s["exclude_reason"] = f"no solver A_d for Ne={Ne}"
            excluded.append(s); continue
        Ad = max(0.0, Ad)
        s["A_dwave"] = round(Ad, 5)
        s["verified_score"] = round(s["nef_states_eV_atom"] * Ad * SCALE, 3)
        kept.append(s)
    print(f"[fix4/5] excluded {len(excluded)}: " + ", ".join(f"{e['material_id']}({e['exclude_reason'][:22]})" for e in excluded[:8]))
    solved = kept
    solved.sort(key=lambda s: -s["verified_score"])
    oid_map = {s["material_id"]: osc_id_for(s["material_id"]) for s in solved}
    fml_map = {s["material_id"]: meta(s["material_id"], "formula", derive_formula(s["material_id"])) for s in solved}
    # per-filling A table
    AbynE = {}
    for s in solved:
        AbynE[s["solver_Ne"]] = (s["solver_delta"], s["A_dwave"])
    print("=== A_d(delta) — the d-wave dome (per filling) ===")
    for Ne in sorted(AbynE):
        d, a = AbynE[Ne]
        print(f"  Ne={Ne:2d} delta={d:+.3f}  A_d={a:.4f}")
    print(f"\n=== verified top 8 (SCALE={SCALE}) ===")
    for s in solved[:8]:
        print(f"  {s['material_id']:14} nef={s['nef_states_eV_atom']:.3f} "
              f"delta={s['solver_delta']:+.3f} A={s['A_dwave']:.4f} -> {s['verified_score']:.2f}")

    # ---- active_challenge.csv (enriched) ----
    acols = ["osc_id", "material_id", "c2db_uid", "formula", "family", "weight_class",
             "sc_relevance", "status", "t_ev", "U_ev", "U_over_t", "ef_scf_ev",
             "n_band", "delta_hole", "solver_delta", "nef", "nef_method", "A_dwave", "runtime_s"]
    arows = []
    for s in solved:
        uid = s["material_id"]
        arows.append({
            "osc_id": oid_map[uid], "material_id": uid,
            "c2db_uid": uid, "formula": fml_map[uid],
            "family": meta(uid, "family", "2D"), "weight_class": meta(uid, "weight_class", "light"),
            "sc_relevance": meta(uid, "sc_relevance", ""), "status": "ok",
            "t_ev": s.get("t_ev"), "U_ev": round((s.get("t_ev") or 0) * 8, 5),
            "U_over_t": 8.0, "ef_scf_ev": s.get("ef_scf_ev"),
            "n_band": s.get("n_band"), "delta_hole": s.get("delta_hole"),
            "solver_delta": s.get("solver_delta"),
            "nef": s["nef_states_eV_atom"], "nef_method": "gaussian_dos_scf_mesh",
            "A_dwave": s["A_dwave"], "runtime_s": meta(uid, "runtime_s", "")})
    with open("active_challenge.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=acols, extrasaction="ignore"); w.writeheader(); w.writerows(arows)

    # ---- submissions.csv (verified anchors, one scale, with scoring breakdown) ----
    scols = ["material_id", "osc_id", "formula", "author", "method_name",
             "provisional_score", "verified_score", "verified", "is_anchor",
             "nef", "solver_delta", "A_dwave", "verify_note"]
    srows = []
    for s in solved:
        uid = s["material_id"]
        nef = s["nef_states_eV_atom"]; d = s["solver_delta"]; Ad = s["A_dwave"]
        note = (f"overdoped (δ={d:+.2f}): d-wave amplitude ≤0 → not a d-wave candidate"
                if Ad <= 0 else f"d-wave dome, δ={d:+.2f}, A_d={Ad:.3f}")
        srows.append({
            "material_id": uid, "osc_id": oid_map[uid],
            "formula": fml_map[uid], "author": "OSC-66",
            "method_name": f"precise 6×6 solver @ δ={d:+.2f}",
            "provisional_score": s["verified_score"], "verified_score": s["verified_score"],
            "verified": "true", "is_anchor": "true",
            "nef": round(nef, 4), "solver_delta": d, "A_dwave": round(Ad, 5), "verify_note": note})
    with open("submissions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=scols, extrasaction="ignore"); w.writeheader(); w.writerows(srows)
    print(f"\nwrote active_challenge.csv ({len(arows)}) + submissions.csv ({len(srows)})")
    json.dump({"scale": SCALE, "A_by_Ne": {str(k): v for k, v in AbynE.items()}},
              open("scoring_meta.json", "w"), indent=1)


if __name__ == "__main__":
    main()
