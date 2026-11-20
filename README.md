# Eighteen Steps

**An audit of the OSC Pairing Index: what the published tables actually determine, and where
they contradict the challenge's own documentation.**

This repository reconstructs the published scores of the
[Open Superconductor Challenge](https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor)
(FINAL-Bench, season 1) from the tables the challenge itself publishes, and asks what the
resulting ordering measures.

Report (Chinese, English figures): `out/report.html` · Landing page: `docs/index.html`

## Findings

1. **The scores are reproducible — with holes nobody documents.** Of 1,073 verified scores,
   **1,064** equal `max(0, N(E_F) × A_d(δ) × 300)` with `A_d` read from `scoring_meta.json` and
   `nef` taken from `active_challenge.csv` (6 dp), to better than 1e-3 (the published values
   are rounded to three decimals). Using the 4-dp `nef` shipped inside `submissions.csv`
   instead puts 21 rows over 1e-3 (max 1.3e-3); the two dumps differ in precision and the
   report says which one it uses. The other **9** rows sit at `Ne = 4, 6, 8`, fillings for
   which the table has **no entry**; the dump writes their `A_d` as 0. Separately, 88 rows sit
   on a negative table value — in `active_challenge.csv` 85 are written as 0 and 3 keep the
   negative value; in `submissions.csv` all 88 are 0 — so "`A_d` = 0" has three origins:
   missing entry, clamped negative, and (for three rows) a genuinely tiny value.

2. **At half filling the table contradicts the challenge's own text.** The README says `A_d`
   vanishes "at half-filling and heavy overdoping". Half filling is δ = 0; the shipped table
   gives **0.03844**, not 0. **120 active materials (11%)** sit on that level.

   Three things have to be said together, and an earlier draft of this note got two of them
   wrong. (i) 0.03844 is the **lowest** level of the plateau, not a near-maximal one: 583
   materials have a *higher* `A_d`. The problem is not that the value is too big, it is that
   the README says it should be zero. (ii) A non-zero value at half filling is **not** by
   itself evidence of an ansatz artefact: the published 4×4 ED gives 0.0062 there, and the
   2×4 / √10 clusters give 0.033–0.036 — same order. Finite-size effects can do this on their
   own. (iii) The consequence for the board is small: only **one** top-20 member (`Cr2I2Te2`)
   sits on that level; forcing `A_d(0) = 0` swaps it for `Fe3Se2Si` and leaves the other 19
   alone. So the finding is a documentation/data conflict worth fixing, not a result that
   reorders the board.

3. **The index is N(E_F) times a nearly binary filling filter.** `A_d` takes only **12
   positive values**; the seven levels with δ ≤ 1/3 span **1.52×**, and one step past 1/3
   drops **3.4×** (4.6× from the peak). Inside that plateau the board *is* the `N(E_F)`
   ranking (Spearman 0.97, 703 materials); across the whole board the filling accounts for
   57% of the variance in log-index, `N(E_F)` for 25%, and their covariance for 18%
   (computed on the 976 rows with a positive index — the 97 zero rows are excluded, and the
   decomposition is an algebraic identity, not a fitted model).

4. **The #1 material sits on the peak level.** `I2Mn2S` has δ = 0.2778, the level where `A_d`
   is largest (68 materials share that level). The #2, `Br2Fe2`, has 12% higher `N(E_F)` but
   23% lower `A_d` at δ = 0.0556, and loses 14% of index. The ordering is a two-step rule —
   bin by filling, then sort by `N(E_F)` — not a direct material comparison.

5. **The unbiased reference cannot adjudicate the shape, and we say so.** Against the
   published 4×4 ED, Spearman is **−0.60** with n = 5 (exact permutation p = **0.35**); the
   organisers read ≈ −0.1 from their own interpolation; both are underpowered, and the two
   clusters differ in maximum distance (2√2 vs 3√2), so amplitudes are not comparable. (An
   earlier draft also quoted −0.72 from carrying ED onto the 15 table levels; that number is
   driven by extrapolating ED beyond δ = 0.5, where it has no data, and is withdrawn.) What
   survives is a sensitivity statement, not a verdict: substituting the ED shape into the
   index — with the rule "no ED data above δ = 0.5, so set 0", which is a modelling choice —
   leaves **4 of the top 20** in place.

6. **The "28% chance" figure is an artefact of the error model, and it is ours, not the
   challenge's.** With the same marginal σ taken from the published cross-cluster spread, a
   single global rescale leaves **20/20** of the top-20 in place, an AR(1) error along filling
   leaves **15/20**, and independent per-level noise leaves **9/20**. The 20/20 row is a
   multiplicative identity, not evidence; AR(1) with ρ = 0.9 is an assumption, not an estimate.
   None of the three is a bound. The defensible statement is the weakest one: the ordering is
   invariant to a global calibration, the published data contain no estimate of the
   filling-dependent error, and therefore the stability of the order is **not identified**.

7. **The Discovery track cannot be screened from the published descriptors.** A
   composition-only nearest-neighbour model predicts `log N(E_F)` with leave-one-out R² = 0.12.
   Its sanity check is mixed: it ranks `I2Mn2S` 8th and `Fe2I2` 24th out of 1,073, but puts
   `Br2Fe2` at **405th**. A model that misplaces the runner-up by 400 places cannot say whether
   the un-downfolded pool contains a challenger; the earlier "no challenger in the pool"
   reading was shrinkage, and is withdrawn.

8. **The dump is the anchor table, not the participant leaderboard.** All 1,073 rows are
   `is_anchor = true`, all authored `OSC-66`; 1,013 carry the method name "precise 6×6 solver
   @ δ=+0.xx" and 60 "canonical scoring at material's DFT filling" — which is itself direct
   evidence that `A_d` is a lookup by filling. The challenge README says the board tops out
   "currently ≈ 22"; this dump tops out at **64.02**. Either the README is stale or the dump
   is newer — quote the snapshot, not "the leaderboard".

## What we submit

- `submission/method/` — a reproducibility package: `package.json` (claims, numbers,
  limitations), `run.sh`, `SHA256SUMS`. It is an audit plus a rank-sensitivity test, **not** a
  new many-body solver, and it does not claim to improve any per-material estimate. If the
  Method track requires a per-material estimator, this entry does not fit it; it is offered as
  a code-and-data audit that the organisers can check in one command.
- `submission/discovery/` — five downfolding nominations: composition siblings of the three
  verified leaders. **No numeric claims** — the screener above cannot make one, and the
  argument is chemical. Note the stoichiometry: `Br2Fe` / `FeI2` are the same composition as
  *each other's* polymorphs, not as `Br2Fe2` / `Fe2I2`; and all five are already in
  `candidates.csv`, so the Discovery track here is about *which object to downfold first*, not
  about discovering a new compound.

## Reproduce

```sh
py -3 scripts/build.py            # recompute every number, seven figures, report, site
py -3 scripts/make_submission.py  # regenerate the submission bundle
py -3 verify/verify.py            # 94 independent assertions; exit 0 = everything holds
```

`build.py` runs `verify.py` itself and stamps the real assertion count into the pages, so the
number printed in the report is the number that ran. `verify.py` covers the data hashes, the
per-row recomputation, the grid and the cliff, the board facts, the ED comparison, the three
error structures, the screener sanity check and the artefact set; it does not cover purely
typographic numbers. Pure Python 3.8+, standard library only, no network at run time.
`data/SHA256SUMS` pins the inputs (and `data/** -text` keeps them byte-exact through git).

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
