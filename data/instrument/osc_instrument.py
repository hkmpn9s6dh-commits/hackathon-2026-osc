# -*- coding: utf-8 -*-
"""OSC participant instrument (light track) — CPU-only, runs in seconds on any laptop.

Given a challenge material, produce a d-wave superconducting-tendency score on the SAME
scale as the leaderboard, then submit it.

The default `estimate_pairing` reproduces the OSC leaderboard baseline:
    score = N(E_F) * correlation_enhancement(U/t)
where N(E_F) (density of states at the Fermi level) is the first-order BCS indicator we
computed for you, and the U/t factor adds the correlation enhancement. Running this as-is
reproduces the baseline row for that material.

To COMPETE (gold track): replace `estimate_pairing` with your own many-body method — a real
d-wave pair susceptibility, exact diagonalization, VMC, DMRG, mean-field variant, or ML —
that improves on the first-order N(E_F) screen using the full effective model (t, U, N(E_F)).
Everything you need is provided per material: t, U, U/t, N(E_F).

Usage:
  python osc_instrument.py --material_id OSC-00129 --author YOUR_NAME
  python osc_instrument.py --t 0.5 --U 4.0 --nef 0.12         # custom model
"""
import os, sys, csv, json, argparse, urllib.request

ACTIVE_URL = os.environ.get(
    "OSC_ACTIVE_URL",
    "https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor/resolve/main/active_challenge.csv")


def load_active():
    try:
        with urllib.request.urlopen(ACTIVE_URL, timeout=30) as r:
            return list(csv.DictReader(r.read().decode("utf-8", "replace").splitlines()))
    except Exception as e:
        print(f"[warn] could not fetch active table: {e}", file=sys.stderr)
        return []


def lookup(mid):
    for row in load_active():
        if row.get("material_id") == mid or row.get("osc_id") == mid:
            return row
    return None


# The OSC Pairing Index (one scale everywhere: instrument, baseline, verified):
#     Index = N(E_F) [states/eV/atom] * A_d * SCALE
# A_d is the d-wave (d_x2-y2) pair correlation of the material's effective model. The organizers'
# verified score uses A_d from the precise 6x6 solver run AT THE MATERIAL'S DFT band filling
# delta (A_d(delta) -- the d-wave dome, published in scoring_meta.json). The challenge table ships
# that A_d per material so the baseline below reproduces the verified anchor; you compete by
# computing a BETTER, material-specific A_d with your own many-body method.
SCALE = 300.0


def estimate_pairing(nef, A_d):
    """OSC BASELINE — reproduces the material's verified anchor on the leaderboard scale.

    Index = N(E_F) * A_d * SCALE, where A_d is the published d-wave amplitude for this material's
    filling (from the organizers' precise solver on the d-wave dome).

    >>> REPLACE A_d with your OWN computed d-wave pair correlation to compete (gold track). <<<
    You have the full effective model per material: t (eV), U (eV), U/t=8, N(E_F), and the band
    filling delta. A stronger entry recomputes A_d for the real material (multi-orbital, a
    different U/t or a better solver) instead of using the provided single-band dome value.
    See instrument/pair_baseline.py for an open d-wave routine to build on.
    """
    if nef is None or A_d is None:
        raise ValueError("N(E_F) or A_d not available for this material.")
    return round(float(nef) * float(A_d) * SCALE, 3)


def main():
    ap = argparse.ArgumentParser(description="OSC participant instrument (light track)")
    ap.add_argument("--material_id", default="", help="OSC id / material_id from the challenge table")
    ap.add_argument("--t", type=float, help="hopping (eV) for a custom model")
    ap.add_argument("--U", type=float, help="on-site interaction (eV)")
    ap.add_argument("--nef", type=float, help="N(E_F) states/eV/atom for a custom model")
    ap.add_argument("--A_d", type=float, help="d-wave amplitude (custom model / your own method)")
    ap.add_argument("--method_name", default="OSC-baseline (published A_d)")
    ap.add_argument("--author", default="")
    ap.add_argument("--out", default="submission.json")
    a = ap.parse_args()

    mid, t, U, nef, A_d = a.material_id, a.t, a.U, a.nef, a.A_d
    ut, delta = None, None
    if mid and (nef is None or A_d is None):
        row = lookup(mid)
        if not row or row.get("nef") in (None, "", "None"):
            print(f"[error] {mid} not found or has no effective model yet.", file=sys.stderr); sys.exit(2)
        t = float(row["t_ev"]) if row.get("t_ev") else None
        U = float(row["U_ev"]) if row.get("U_ev") else None
        ut = float(row.get("U_over_t") or 8.0)
        nef = float(row["nef"])
        A_d = float(row["A_dwave"]) if row.get("A_dwave") not in (None, "", "None") else None
        delta = row.get("solver_delta")
        print(f"[OSC] {mid} ({row.get('formula')}): t={t} eV, U/t={ut}, N(E_F)={nef}, "
              f"filling delta={delta}, published A_d={A_d}")
    if nef is None or A_d is None:
        print("[error] provide --material_id OR --nef and --A_d", file=sys.stderr); sys.exit(2)
    if ut is None:
        ut = 8.0

    score = estimate_pairing(nef, A_d)
    if A_d is not None and float(A_d) <= 0:
        level = "off-dome — no d-wave at this filling"
    elif score >= 15: level = "STRONG d-wave candidate"
    elif score >= 8: level = "MODERATE"
    elif score >= 2: level = "WEAK"
    else: level = "negligible"
    sub = dict(material_id=mid or f"custom(nef={nef},A_d={A_d})", t=t, U=U, nef=nef,
               U_over_t=round(ut, 4), A_dwave=A_d, solver_delta=delta,
               provisional_score=score, level=level, method_name=a.method_name,
               author=a.author, track="light")
    print(f"[level] {level}  (score {score} on a ~0-22 scale; strong ≳15, off-dome = 0)")
    json.dump(sub, open(a.out, "w"), indent=1)
    print(json.dumps(sub, indent=1))
    print(f"\n[OK] wrote {a.out}. Sign in on the OSC Space and submit this score on the material's card, "
          f"or open a PR adding it under submissions/.")


if __name__ == "__main__":
    main()
