# OSC validation — 4×4 Hubbard d-wave pair correlation: exact ED vs our VMC

Independent exact-diagonalization (ED) cross-check of the OSC verification solver on a common
**4×4 periodic cluster, U/t = 8**, maximal-distance pair correlation **R = (2,2)**, with a single
shared normalization (organizer convention; the ED values below use P_org = 2·P_ED).

- **ED columns** contributed by **Ku-ku** (translation-momentum-sector exact diagonalization,
  degenerate ground states averaged with equal weight; U = 0 reference = canonical free-fermion;
  n = 1.0 U = 0 is the analytic Wick value). ED is the unbiased reference.
- **VMC columns** are our solver (variational Monte Carlo + d-wave AGP ansatz): `dwave=0.15`
  (the d-wave channel used for the OSC score) and `dwave=0.0` (Fermi-sea control). Our 6×6 OSC
  score uses the max-distance diagonal **R = (3,3)**; this table is 4×4 R = (2,2) for comparison.

| n | Ne | ED P_d (U=8) | ED P_d (U=0) | ED ratio U8/U0 | VMC P_d (dwave 0.15) | VMC P_d (Fermi 0.0) |
|---|---|---|---|---|---|---|
| 0.500 | 8  | 0.048076 | 0.046875 | 1.026 | 0.0636 | 0.0836 |
| 0.625 | 10 | 0.060122 | 0.093750 | 0.641 | 0.1150 | 0.1135 |
| 0.750 | 12 | 0.009831 | 0.041667 | 0.236 | 0.0219 | 0.0104 |
| 0.875 | 14 | 0.019219 | 0.010417 | 1.845 | 0.0023 | 0.0229 |
| 1.000 | 16 | 0.006197 | 0.000000 | –     | 0.0008 | −0.0002 |

(ED values from Ku-ku's full-filling table, organizer normalization. VMC from our
`validation/compare_4x4_dwave_vs_fermi.json`.)

## What this shows (honestly)

- **Absolute values differ by method, as expected.** Our d-wave AGP ansatz tends to *overestimate*
  the d-wave correlation relative to unbiased ED (e.g. n = 0.625: VMC 0.115 vs ED 0.060), because
  d-wave pairing is partly built into the ansatz. OSC scores are therefore a **variational
  screening indicator**, calibrated against ED here, not an exact many-body result.
- **Interaction enhancement is weak and non-monotonic.** Of the four fillings with a defined ED
  U=8/U=0 ratio, two are below 1 (0.641, 0.236) and two are above 1 (1.026, 1.845); the ratio jumps
  around with filling and cluster rather than showing a clean enhancement — consistent with the
  modern result that the pure 2D Hubbard model has no robust d-wave superconductivity at U/t = 8
  (Qin et al., *Science* 2020). The A_d(δ) "dome" used in OSC is partly a finite-size/ansatz feature.
  Note: our 6×6 VMC A_d and the 4×4 ED values (interpolated to the same δ) are essentially
  uncorrelated across filling (Spearman ≈ −0.1), so a single cluster size is not yet a calibration.
- The earlier apparent "opposite direction" between the two was a comparison of **different
  quantities** (ours: d-wave channel on/off at U = 8; ED: U = 8 / U = 0), now reconciled.

## Credit & license

- ED cross-validation: **Ku-ku** (contributor). This comparison is released for OSC validation.
- License: **CC-BY-NC 4.0** (same as the OSC dataset), with attribution to the ED contributor.
