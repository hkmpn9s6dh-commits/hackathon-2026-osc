# -*- coding: utf-8 -*-
"""OSC open baseline pairing solver (MIT).

Given an effective single-band model (t, U, lattice, filling), compute a cheap,
textbook, CPU-only estimate of d-wave (d_x2-y2) pairing tendency -> `provisional_score`.

This is a *weak-coupling screening proxy*, NOT a prediction. It measures the
band-structure phase space for d-wave pairing (the bare d-wave pair susceptibility
weighted by the d-wave form factor) and modulates it by the correlation strength U/t.
The precise (strong-coupling) verification is done separately by the organizers.

No external deps beyond numpy. Runs in milliseconds on any laptop CPU.
"""
import argparse, json, math
import numpy as np


def dispersion(kx, ky, t, lattice):
    if lattice == "square":
        return -2.0 * t * (np.cos(kx) + np.cos(ky))
    if lattice == "triangular":
        return -2.0 * t * (np.cos(kx) + np.cos(ky) + np.cos(kx + ky))
    if lattice == "honeycomb":
        # magnitude of NN structure factor (two-atom cell) -> band |E|
        f = 1.0 + np.exp(1j * kx) + np.exp(1j * ky)
        return -t * np.abs(f)
    raise ValueError("lattice must be square/triangular/honeycomb")


def dwave_form(kx, ky, lattice):
    # d_{x2-y2}
    return np.cos(kx) - np.cos(ky)


def find_mu(eps, filling, beta):
    """Bisect chemical potential so mean occupation matches `filling` (0..2 per site)."""
    lo, hi = eps.min() - 10, eps.max() + 10
    target = filling / 2.0  # per spin
    for _ in range(80):
        mu = 0.5 * (lo + hi)
        occ = np.mean(1.0 / (1.0 + np.exp(beta * (eps - mu))))
        if occ < target:
            lo = mu
        else:
            hi = mu
    return 0.5 * (lo + hi)


def chi_d0(t, lattice, filling, T_over_t, ngrid):
    """Bare static d-wave pair susceptibility on the tight-binding band."""
    ks = np.linspace(-math.pi, math.pi, ngrid, endpoint=False)
    KX, KY = np.meshgrid(ks, ks)
    eps = dispersion(KX, KY, t, lattice).ravel()
    g = dwave_form(KX, KY, lattice).ravel()
    beta = 1.0 / max(1e-6, T_over_t * abs(t))
    mu = find_mu(eps, filling, beta)
    xi = eps - mu
    # pair bubble kernel  tanh(beta xi/2)/(2 xi)  (limit -> beta/4 as xi->0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ker = np.tanh(beta * xi / 2.0) / (2.0 * xi)
    ker = np.where(np.abs(xi) < 1e-9, beta / 4.0, ker)
    chi = np.mean(g * g * ker)
    return float(chi), float(mu)


def provisional_score(t, U, lattice="square", filling=0.9, T_over_t=0.05, ngrid=64):
    """Screening score in ~[0,1+]. Higher = stronger d-wave pairing tendency.
    Combines bare d-wave phase space (chi_d0*|t|) with correlation strength U/t."""
    chi, mu = chi_d0(abs(t), lattice, filling, T_over_t, ngrid)
    x = chi * abs(t)                      # dimensionless band phase-space factor
    uot = abs(U) / max(1e-6, abs(t))
    # weak/intermediate-coupling enhancement, saturating (avoids blow-up at large U/t)
    corr = uot / (1.0 + uot / 8.0)        # ~U/t for small, saturates near 8
    score = x * corr
    return dict(provisional_score=round(float(score), 5),
                chi_d0_t=round(x, 5), U_over_t=round(uot, 4),
                mu=round(mu, 5), lattice=lattice, filling=filling)


def main():
    ap = argparse.ArgumentParser(description="OSC baseline d-wave pairing score")
    ap.add_argument("--t", type=float, required=True, help="hopping (eV)")
    ap.add_argument("--U", type=float, required=True, help="on-site interaction (eV)")
    ap.add_argument("--lattice", default="square", choices=["square", "triangular", "honeycomb"])
    ap.add_argument("--filling", type=float, default=0.9, help="electrons per site (0-2)")
    ap.add_argument("--T_over_t", type=float, default=0.05)
    ap.add_argument("--ngrid", type=int, default=64)
    ap.add_argument("--material_id", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    r = provisional_score(a.t, a.U, a.lattice, a.filling, a.T_over_t, a.ngrid)
    r["material_id"] = a.material_id
    r["t"] = a.t; r["U"] = a.U
    print(json.dumps(r, indent=1))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
