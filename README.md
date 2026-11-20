# Eighteen Steps

**An audit of the OSC Pairing Index: what the published tables actually determine, and where
they contradict the challenge's own documentation.**

This repository reconstructs the published scores of the
[Open Superconductor Challenge](https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor)
(FINAL-Bench, season 1) from the tables the challenge itself publishes, and asks what the
resulting ordering measures.

Report (Chinese, English figures): `out/report.html` · Landing page: `docs/index.html`

## Findings

1. **The scores are reproducible — with two holes nobody documents.** Of 1,073 verified
   scores, **1,064** equal `max(0, N(E_F) × A_d(δ) × 300)` with `A_d` read from
   `scoring_meta.json`, to better than 1e-3 (the published values are rounded to three
   decimals). The other **9** sit at `Ne = 4, 6, 8`, fillings for which the table has **no
   entry**; the dump writes their `A_d` as 0. Separately, 88 rows sit on a negative table
   value, 85 written as 0 and 3 kept negative — so "`A_d` = 0" means two different things.

2. **At half filling the table contradicts the challenge's own physics.** The README says
   `A_d` vanishes "at half-filling and heavy overdoping". Half filling is δ = 0; the shipped
   table gives **0.03844**, i.e. **66% of the peak**. **120 materials (11%)** sit exactly
   there and therefore carry a near-maximal amplitude. On a U/t = 8 Mott insulator, a d-wave
   variational state holding two thirds of its peak correlation at half filling is the
   strongest available evidence that `A_d` is an ansatz artefact — and the documentation uses
   the opposite claim to justify the index. One of the two has to give.

3. **The index is N(E_F) times a nearly binary filling filter.** `A_d` takes only **12
   positive values**; the seven levels with δ ≤ 1/3 span **1.52×**, and one step past 1/3
   drops **3.4×** (4.6× from the peak). Inside that plateau the board *is* the `N(E_F)`
   ranking (Spearman 0.97, 703 materials); across the whole board the filling accounts for
   57% of the variance in log-index and `N(E_F)` for 25%.

4. **The #1 material sits exactly on the peak.** `I2Mn2S` has δ = 0.2778, the argmax of
   `A_d`. The #2, `Br2Fe2`, has 12% higher `N(E_F)` but 23% lower `A_d` at δ = 0.0556, and
   loses 14% of index. The ordering is a filling lottery, not a material comparison.

5. **The unbiased reference cannot adjudicate, and we say so.** Against the published 4×4
   ED, Spearman is **−0.60** with n = 5 (exact permutation p = **0.35**); carrying ED onto
   the 15 table fillings instead gives **−0.72**; the organisers' own write-up reads ≈ −0.1
   from a different interpolation. Three numbers, one underpowered statistic. What *is*
   solid: substituting the ED shape into the index leaves **4 of the top 20** in place
   (2 of 20 if ED is carried onto the grid).

6. **The famous "28% chance" is an artefact of the error model.** With the same marginal σ
   taken from the published cross-cluster spread, a single global rescale leaves **20/20** of
   the top-20 in place, an AR(1) error along filling leaves **15/20**, and independent
   per-level noise leaves **9/20**. Errors from one ansatz on one cluster cannot be
   independent across neighbouring fillings, so the i.i.d. number understates stability. The
   defensible statement: the ordering is immune to a global calibration and sensitive to
   filling-dependent method error, and the published data cannot tell the two apart.

7. **The Discovery track cannot be screened from the published descriptors — and we show the
   sanity check failing.** A composition-only nearest-neighbour model predicts `log N(E_F)`
   with leave-one-out R² = 0.12, and it under-predicts the three known leaders by 3.7×–8.6×
   (0.94 / 0.47 / 0.84 against 3.65 / 4.08 / 3.49). A model that cannot recover the champions
   says nothing about whether the pool contains a challenger; the earlier "no challenger in
   the pool" reading was shrinkage, and is withdrawn.

8. **The dump is the anchor table, not the participant leaderboard.** All 1,073 rows are
   `is_anchor = true`, all authored `OSC-66`, method "canonical scoring at material's DFT
   filling". The challenge README says the board tops out "currently ≈ 22"; this dump tops out
   at **64.02**. Either the README is stale or the dump is newer — quote the snapshot, not
   "the leaderboard".

## What we submit

- `submission/method/` — a reproducibility package: `package.json` (claims, numbers,
  limitations), `run.sh`, `SHA256SUMS`. It is an audit plus a rank-sensitivity test, **not** a
  new many-body solver, and it does not claim to improve any per-material estimate.
- `submission/discovery/` — five downfolding nominations: composition siblings of the three
  verified leaders. **No numeric claims** — the screener above cannot make one, and the
  argument is chemical. Note the stoichiometry: `Br2Fe` / `FeI2` are the same composition as
  *each other's* polymorphs, not as `Br2Fe2` / `Fe2I2`.

## Reproduce

```sh
py -3 scripts/build.py            # recompute every number, seven figures, report, site
py -3 scripts/make_submission.py  # regenerate the submission bundle
py -3 verify/verify.py            # 94 independent assertions; exit 0 = everything holds
```

`build.py` runs `verify.py` itself and stamps the real assertion count into the pages, so the
number printed in the report is the number that ran. Pure Python 3.8+, standard library only,
no network at run time. `data/SHA256SUMS` pins the inputs (and `data/** -text` keeps them
byte-exact through git).

## Layout

```
data/            frozen copy of the challenge tables + the two published ED validation tables
src/osc/         analysis (score rule, grid, dome, ED comparison, stress tests, screener)
scripts/         build.py (numbers + figures + report), make_submission.py
verify/          verify.py — independent re-derivation, does not read out/results.json
out/             results.json, report.html, figures/, verify.json
docs/            the landing page served by GitHub Pages
submission/      method package + discovery nominations
SPEC.md          gate A: quoted rules, golden path, acceptance criteria
```

## Data provenance and licence

Materials derive from C2DB via the OSC dataset (CC-BY-NC 4.0); the multi-size ED table is
credited to the contributor **Ku-ku** in the challenge README. This repository is a
non-commercial academic analysis. It does **not** claim to have discovered a superconductor,
and it does **not** claim the organisers' `A_d` values are miscalculated — only that the table
contradicts its own documentation at half filling, and that using its ordering to rank
materials is not identified by the evidence the challenge publishes.

If you use this, please cite the challenge: FINAL-Bench — Open Superconductor Challenge.
