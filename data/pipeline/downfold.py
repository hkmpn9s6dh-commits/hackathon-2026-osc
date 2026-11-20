# -*- coding: utf-8 -*-
"""OSC downfolding from the existing QE SCF (no new DFT) -- reproducible and fast.

For every material with a finished SCF (tu_batch/<uid>/osc.xml) it computes:
  * N(E_F): a Gaussian-broadened density of states at the Fermi level, evaluated from the
            SCF eigenvalues over the SCF k-mesh, in states / eV / atom (both spins).
            (This replaces the old smearing-entropy proxy; grid is the SCF mesh -- coarse,
             refined on a dense NSCF grid for finalists.)
  * filling: occupation of the band crossing E_F (weighted over the k-mesh), n_band in [0,2],
             which sets the doping delta = 1 - n_band the many-body solver is run at.
             n_band is the site DENSITY (0..2, half-filling = 1): the per-spin band fraction o from
             the pw.x <occupations> (in [0,1]) times the spin factor 2, consistent with dos_at_ef().
  * t: nearest-neighbour hopping from the single active-band width, t = W_band / z (documented).

E_F reference = the QE SCF Fermi level of the metal. All energies are relative to it.
Everything is scriptable and published for the Discovery track.
"""
import os, sys, json, math, glob, argparse
import xml.etree.ElementTree as ET

HA = 27.211386245988
SIGMA = float(os.environ.get("OSC_DOS_SIGMA", "0.15"))  # Gaussian broadening (eV)


def _t(el):
    return (el.text or "").strip()


def parse_xml(xml_path):
    root = ET.parse(xml_path).getroot()
    out = root.find(".//output")
    bs = out.find("band_structure")
    fermi = float(_t(bs.find("fermi_energy"))) * HA
    nelec = float(_t(bs.find("nelec")))
    nat = int(out.find(".//atomic_structure").get("nat"))
    ks = bs.findall("ks_energies")
    W, E, O = [], [], []
    for k in ks:
        W.append(float(k.find("k_point").get("weight")))
        E.append([float(x) * HA for x in _t(k.find("eigenvalues")).split()])
        O.append([float(x) for x in _t(k.find("occupations")).split()])
    return dict(fermi=fermi, nelec=nelec, nat=nat, nk=len(E), nb=len(E[0]),
                weights=W, eig=E, occ=O)


def dos_at_ef(d, sigma=SIGMA):
    """Gaussian DOS at E_F, states/eV/cell (x2 for spin)."""
    ws = sum(d["weights"]) or 1.0
    w = [x / ws for x in d["weights"]]
    ef = d["fermi"]
    pref = 1.0 / (sigma * math.sqrt(2 * math.pi))
    n = 0.0
    for k in range(d["nk"]):
        for b in range(d["nb"]):
            x = (d["eig"][k][b] - ef) / sigma
            if abs(x) < 8:
                n += w[k] * pref * math.exp(-0.5 * x * x)
    return 2.0 * n  # spin


def active_band(d):
    ws = sum(d["weights"]) or 1.0
    w = [x / ws for x in d["weights"]]
    ef = d["fermi"]
    cand = []
    for b in range(d["nb"]):
        o = sum(w[k] * d["occ"][k][b] for k in range(d["nk"]))
        emin = min(d["eig"][k][b] for k in range(d["nk"]))
        emax = max(d["eig"][k][b] for k in range(d["nk"]))
        cand.append((b, o, emin < ef < emax, emin, emax))
    crossers = [c for c in cand if c[2]] or cand
    # The per-band <occupations> in a non-spin-polarized pw.x run are per-spin fractions in [0,1];
    # the spin factor 2 is carried by the k-point weights (which sum to 2 and are renormalized to 1
    # above), exactly as dos_at_ef() accounts for with its 2.0*n. So o is the per-spin filling f and
    # the site density is n = 2f. Select the crossing band nearest HALF filling (|2f-1| minimal), and
    # report n_band as the density 2f (0..2, half-filling = 1).  [fixes the factor-of-2 in delta]
    b, o, cx, emin, emax = min(crossers, key=lambda c: abs(2.0 * c[1] - 1.0))
    return dict(band=b, n_band=max(0.0, min(2.0, 2.0 * o)), W_band=emax - emin, crosses=cx)


def downfold(xml_path, zt=8.0):
    d = parse_xml(xml_path)
    fb = active_band(d)
    nef_cell = dos_at_ef(d)
    nef_atom = nef_cell / d["nat"]
    t_ev = fb["W_band"] / zt if fb["W_band"] > 0 else None
    Ne = int(round(fb["n_band"] * 36)); Ne -= Ne % 2
    Ne = max(2, min(70, Ne))
    return dict(status="ok", nat=d["nat"], nelec=d["nelec"], ef_scf_ev=round(d["fermi"], 4),
                nk_scf=d["nk"], active_band=fb["band"], n_band=round(fb["n_band"], 4),
                delta_hole=round(1 - fb["n_band"], 4), W_band_ev=round(fb["W_band"], 4),
                t_ev=round(t_ev, 5) if t_ev else None, U_over_t=8.0,
                nef_states_eV_atom=round(nef_atom, 5), nef_states_eV_cell=round(nef_cell, 5),
                solver_Ne=Ne, solver_nup=Ne // 2, solver_ndn=Ne // 2,
                solver_delta=round(1 - Ne / 36.0, 4), dos_sigma_eV=SIGMA,
                method="Gaussian DOS at E_F over SCF k-mesh; band-occupation filling; single active-band t=W/z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tu_root", default="tu_batch")
    ap.add_argument("--out_dir", default="df_batch")
    ap.add_argument("--one", default="", help="process a single dir name")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    dirs = ([os.path.join(a.tu_root, a.one)] if a.one
            else sorted(glob.glob(os.path.join(a.tu_root, "*"))))
    ok = 0
    for dd in dirs:
        xml = os.path.join(dd, "osc.xml")
        if not os.path.isfile(xml):
            continue
        uid = os.path.basename(dd.rstrip("/"))
        try:
            row = downfold(xml); row["material_id"] = uid
            json.dump(row, open(os.path.join(a.out_dir, uid + ".json"), "w"), indent=1)
            ok += 1
            if a.one or ok <= 3:
                print(uid, "nef/atom=%.4f n_band=%.3f delta=%.3f t=%.3f Ne=%d" %
                      (row["nef_states_eV_atom"], row["n_band"], row["delta_hole"],
                       row["t_ev"] or 0, row["solver_Ne"]))
        except Exception as e:
            print("ERR", uid, e)
    print("downfolded", ok, "materials ->", a.out_dir)


if __name__ == "__main__":
    main()
