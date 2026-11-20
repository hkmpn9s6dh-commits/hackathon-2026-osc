# -*- coding: utf-8 -*-
"""Run the precise 6x6 doped-Hubbard solver once per UNIQUE filling present in df_batch,
then assign the material-specific d-wave amplitude A_d(delta) to every material.

verified_score = N(E_F) * A_d(delta_material)  (a physical, per-material quantity: it varies
with doping via the d-wave dome). Cheap: only the distinct fillings are solved.
"""
import os, sys, json, glob, subprocess, time

SOLVER = "/data/ginipick/hubbard_doped/pair_corr.py"
CVD = os.environ.get("CUDA_VISIBLE_DEVICES", "3")
OPT = int(os.environ.get("OSC_OPT", "200"))


def solve(nup, ndn):
    out = f"/tmp/Abatch_{nup}_{ndn}.json"
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=CVD)
    subprocess.run([sys.executable, "-u", SOLVER, "--size", "6x6", "--nup", str(nup),
                    "--ndn", str(ndn), "--opt", str(OPT), "--meas", "20", "--Bmeas", "384",
                    "--dwave", "0.15", "--out", out],
                   env=env, cwd=os.path.dirname(SOLVER), timeout=900, check=False)
    d = json.load(open(out))
    pds = {k: v for k, v in d.items() if k.startswith("Pd_") and not k.endswith("err")}
    if not pds:
        return None
    best = max(pds, key=lambda k: sum(int(c) for c in k.split("_")[1]))
    return float(pds[best])


def main():
    rows = [json.load(open(f)) for f in glob.glob("df_batch/*.json")]
    uniq = sorted(set((r["solver_nup"], r["solver_ndn"]) for r in rows))
    print(f"{len(rows)} materials, {len(uniq)} unique fillings to solve", flush=True)
    A = {}
    for nup, ndn in uniq:
        t0 = time.time()
        a = solve(nup, ndn)
        A[(nup, ndn)] = a
        print(f"  Ne={nup+ndn} delta={1-(nup+ndn)/36.0:+.3f}  A_d={a}  ({time.time()-t0:.0f}s)", flush=True)
    os.makedirs("solved", exist_ok=True)
    for r in rows:
        a = A.get((r["solver_nup"], r["solver_ndn"]))
        r["A_dwave"] = round(a, 5) if a is not None else None
        json.dump(r, open("solved/" + r["material_id"] + ".json", "w"), indent=1)
    json.dump({f"{k[0]+k[1]}": v for k, v in A.items()}, open("solved/A_by_Ne.json", "w"), indent=1)
    print("done -> solved/", flush=True)


if __name__ == "__main__":
    main()
