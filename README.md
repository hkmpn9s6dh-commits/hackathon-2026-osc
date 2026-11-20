# Eighteen Steps

**An audit of the OSC Pairing Index: the leaderboard is a step function of band filling,
not a per-material pairing estimate.**

This repository reconstructs every published score of the
[Open Superconductor Challenge](https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor)
(FINAL-Bench, season 1) from the three tables the challenge itself publishes, and then asks
what the resulting ranking actually measures.

Report (Chinese, with English figures): `out/report.html` · Landing page: `docs/index.html`

## Findings

1. **Every score is reproducible.** All 1,073 `verified_score` values equal
   `max(0, N(E_F) × A_d(δ) × 300)` with `A_d` read from `scoring_meta.json`, to better than
   1e-3 (the published scores are rounded to three decimals). Nothing in the board is hidden
   computation.
2. **`A_d` is not a dome.** It is a **plateau plus a cliff**: seven filling levels with
   `δ ≤ 1/3` span only 1.52× (0.0384–0.0585), then one step drops 3.39× to 0.0127.
   The index therefore has 15 distinct values, and `A_d` depends on the filling alone.
3. **Inside the plateau the board is the `N(E_F)` ranking** (Spearman 0.97, 703 materials).
   Across the whole board the filling accounts for 57% of the variance in log-index and
   `N(E_F)` for 25%. The current #1 (`I2Mn2S`, 64.02) wins because its filling sits one level
   below the dome peak; the #2 material has 12% higher `N(E_F)` and loses 14% of index.
4. **The shape is not supported by the unbiased reference the challenge ships.** Against the
   published 4×4 exact diagonalisation at the same fillings, Spearman is **−0.60**; at
   `n = 0.5` the published curve has a node while ED is near its own maximum. Substituting the
   ED shape into the index leaves **1 of the top 20** in place; perturbing each filling level
   inside the published cross-cluster spread leaves **9.1 of 20** and lets the current #1 keep
   first place only 28% of the time.
5. **The Discovery track cannot be screened from the published descriptors.** A composition-only
   nearest-neighbour model predicts `log N(E_F)` with leave-one-out R² = 0.12 and δ with 17%
   accuracy (majority class: 14%). The 759 metals that have not been downfolded contain no
   predicted challenger; discovery is bound to the organisers' DFT queue.

## What we submit

- `submission/method/` — a reproducibility package: `package.json` (claims and numbers),
  `run.sh`, `SHA256SUMS`. It is an audit + rank-robustness test, not a new many-body solver.
- `submission/discovery/` — five downfolding nominations: composition siblings of the three
  verified leaders (same elements, same or related stoichiometry). **No numeric claims**: the
  screener above cannot make one, and the argument is chemical, not statistical.

## Reproduce

```sh
py -3 scripts/build.py            # recompute every number, six figures, report, site
py -3 scripts/make_submission.py  # regenerate the submission bundle
py -3 verify/verify.py            # 63 independent assertions; exit 0 = everything holds
```

Pure Python 3.8+, standard library only, no network at run time. `data/SHA256SUMS` pins the
inputs.

## Layout

```
data/            frozen copy of the challenge tables + the two published ED validation tables
src/osc/         analysis (score rule, grid, dome, ED comparison, stress tests, screener)
scripts/         build.py (numbers + figures + report), make_submission.py
verify/          verify.py — independent re-derivation, does not read out/results.json
out/             results.json, report.html, figures/
docs/            the landing page served by GitHub Pages
submission/      method package + discovery nominations
SPEC.md          gate A: quoted rules, golden path, acceptance criteria
```

## Data provenance and licence

Materials derive from C2DB via the OSC dataset (CC-BY-NC 4.0); the ED multi-size table is
credited to the contributor **Ku-ku** in the challenge README. This repository is a
non-commercial academic analysis. It does **not** claim to have discovered a superconductor,
and it does **not** claim that the organisers' `A_d` values are wrong — only that using their
*ordering* to rank materials is not supported by the evidence the challenge publishes.

If you use this, please cite the challenge: FINAL-Bench — Open Superconductor Challenge.
