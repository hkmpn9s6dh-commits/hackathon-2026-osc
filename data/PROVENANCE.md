# Provenance & License

## Source data — C2DB

The crystal structures and the base electronic-structure properties in OSC are derived from the
**Computational 2D Materials Database (C2DB)**, Technical University of Denmark.

- **License: Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0).**
  https://creativecommons.org/licenses/by-nc/4.0/
- C2DB material pages: https://c2db.fysik.dtu.dk/

Please cite C2DB when using OSC:
> S. Haastrup et al., *The Computational 2D Materials Database: high-throughput modeling and
> discovery of atomically thin crystals*, 2D Materials 5, 042002 (2018); and
> M. N. Gjerding et al., 2D Materials 8, 044002 (2021).

## What OSC adds (and how)

From each C2DB structure, OSC computes — with the open scripts in `instrument/` and the
organizer pipeline published in `pipeline/` — a single-band effective Hubbard model:

- **N(E_F)**: Gaussian-broadened density of states at the Fermi level from a QE calculation
  (states/eV/atom). Grid: the SCF k-mesh (coarse) for the active set, refined on a dense NSCF
  grid for finalists.
- **filling (δ)**: occupation of the band crossing E_F, weighted over the k-mesh, giving the
  doping the many-body solver is run at.
- **t**: nearest-neighbour hopping from the single active-band width (t = W_band / z).
- **U/t = 8**: a documented correlated-regime convention (control parameter, cRPA pending).

These derived quantities are **also released under CC-BY-NC 4.0**, consistent with the source.

## Non-commercial scope of the challenge

Because the source data is CC-BY-NC 4.0, **OSC is a non-commercial, academic open-science
challenge**:

- The data and derived models may be used for research and education, **not for commercial
  purposes**, with attribution to C2DB.
- Prizes are **research awards** (recognition + co-authorship + a token honorarium), not a sale
  or commercial licensing of the data.
- Participants retain the rights to their own methods and code; winners share reproducible code
  under an open contributor license.

If you intend any commercial use of the underlying materials data, obtain permission from C2DB
directly — OSC does not and cannot grant commercial rights to C2DB-derived data.

## Verification engine

The precise strongly-correlated solver used to set the *verified* scores is operated by the
organizers and is not redistributed. Its **inputs** (per-material t, U, N(E_F), filling) and its
**outputs** (the d-wave amplitude A_d(δ) per filling) are fully published here, so every verified
score is reproducible in its construction; only the internal solver implementation is withheld
to keep the ranking hard to game.
