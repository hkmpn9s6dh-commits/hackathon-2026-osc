---
license: cc-by-nc-4.0
tags:
- open-science
- superconductivity
- superconductor-discovery
- strongly-correlated
- materials-discovery
- 2d-materials
- twisted-bilayer
- moire
- hubbard-model
- d-wave
- machine-learning-for-materials
- computational-materials-science
- challenge
- leaderboard
- benchmark
- cpu-friendly
language:
- en
pretty_name: "OSC — Open Superconductor Challenge"
size_categories:
- 1K<n<10K
configs:
- config_name: candidates
  data_files:
  - split: candidates
    path: candidates.csv
- config_name: active_challenge
  data_files:
  - split: active
    path: active_challenge.csv
- config_name: submissions
  data_files:
  - split: leaderboard
    path: submissions.csv
---

# OSC — Open Superconductor Challenge

**Screen thousands of 2D materials for unconventional (d-wave) superconductivity — from your own laptop — and climb an open, verified leaderboard.**

🏆 **Leaderboard, live challenge & submission:** **https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard**

---

## TL;DR (the short answer)

OSC is a free, open-science competition on Hugging Face to find the next candidate **twisted-2D superconductor**. We provide a computed **effective model** (`t`, `U`, `N(E_F)`) for each material; you estimate its **d-wave pairing tendency** with any method — a laptop CPU is enough — and submit a small file. Provisional scores appear instantly; the organizers' precise **strongly-correlated solver** verifies the top entries and sets the official rank. Prize pool **US $3,000 + co-authorship**. Season 1 closes **31 December 2026 (23:59 KST)**. Materials derive from **C2DB** (CC-BY-NC 4.0). No installation and no GPU are required for the light track.

- **What you get:** an effective Hubbard model per material — hopping `t`, interaction `U`, and the density of states at the Fermi level `N(E_F)`.
- **What you do:** compute a d-wave (d<sub>x²−y²</sub>) pairing estimate and submit it.
- **What we do:** verify the top submissions with a precise many-body reference solver.
- **Who can join:** anyone — researchers, students, and AI coding agents.

---

## What is the Open Superconductor Challenge?

The **Open Superconductor Challenge (OSC)** is a crowd-sourced materials-screening benchmark for **unconventional superconductivity** in two-dimensional (2D) materials. Discovering superconductors experimentally is slow and expensive, so OSC screens candidates *computationally, before the lab*: the community estimates a superconducting-pairing signal for thousands of materials, and a precise reference solver confirms the most promising ones.

OSC targets **d-wave (d<sub>x²−y²</sub>) pairing tendency** — the pairing symmetry associated with cuprates, twisted bilayer graphene, and other strongly-correlated systems — using the doped **Hubbard model** as the effective description. It is hosted by **FINAL-Bench** as an open-science initiative and is designed to be reproducible, hard to game, and accessible without specialized hardware.

## Why OSC matters

- **Compute arbitrage:** the crowd screens broadly on laptops; the organizers spend heavy DFT and many-body compute only on the top candidates. This finds promising materials for a fraction of the usual cost.
- **Open and fair:** the candidate list, protocol, and baseline tools are fully open (GPL/MIT); only the final verification engine is private, which keeps the ranking un-gameable without hiding the science.
- **Reproducible science:** every material carries a provenance trail to C2DB, and winning methods are shared under a contributor license.

---

## Dataset contents

| File | Description |
|---|---|
| `candidates.csv` | The full browsable universe — **4,832** dynamically-stable 2D materials (C2DB-derived) enriched with our tags: chemical family, cost class, is-metal, band gap, and a screening prior. |
| `active_challenge.csv` | The **active competition set** (metallic / small-gap materials) with the provided **effective model**: `t` (eV), `U` (eV), `U/t`, and **`nef`** = N(E_F) (states/eV/atom). |
| `submissions.csv` | The baseline leaderboard rows and verified anchor scores (the OSC Pairing Index). |
| `instrument/osc_instrument.py` | The participant tool — pure Python, no install, runs in seconds on any laptop. |
| `instrument/pair_baseline.py` | An open d-wave pair-susceptibility routine to build a competitive method on. |
| `PROVENANCE.md` | Data source and license details (C2DB, CC-BY-NC 4.0). |

## The effective model (what you receive per material)

For every active material OSC provides a downfolded **Hubbard effective model**:

- **`t`** — nearest-neighbor hopping (eV), from the DFT band structure.
- **`U`** — on-site Coulomb interaction (eV); the challenge fixes the strongly-correlated regime at **U/t = 8** (cuprate convention).
- **`N(E_F)`** (`nef`) — density of states at the Fermi level (states/eV/atom), the first-order BCS indicator: higher N(E_F) → stronger pairing tendency.

Your task is to do better than the first-order screen by computing an actual, **material-specific** d-wave pairing estimate.

---

## How to participate (light track — any laptop, no install)

You do **not** need a GPU or any installation for the light track. An AI coding agent (Claude Code, Codex) can also do every step for you — just point it at this challenge.

**1. Sign in** with Hugging Face on the [OSC Leaderboard Space](https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard) — this verifies your identity so entries can't be posted under someone else's handle.

**2. Get the instrument** (pure Python — Windows / Linux / macOS, nothing to install):
```bash
huggingface-cli download FINAL-Bench/OSC-Superconductor \
  instrument/osc_instrument.py instrument/pair_baseline.py \
  --repo-type dataset --local-dir osc
cd osc/instrument
```

**3. Pick a material and run:**
```bash
python osc_instrument.py --material_id OSC-00129 --author YOUR_NAME
# reads the material's (t, U, N(E_F)); prints an OSC Pairing Index on the leaderboard's scale
# -> writes submission.json
```
To **compete on the gold track**, edit `estimate_pairing()` with your own many-body method — exact diagonalization (ED), variational Monte Carlo (VMC), DMRG, mean-field, or machine learning — that improves on the first-order N(E_F) screen.

**4. Submit your score.** Open the material's card in the **Active Challenge** tab of the Space and submit (you must be signed in), or open a Pull Request adding your `submission.json` under `submissions/` in this dataset. Your provisional score appears on the leaderboard immediately.

---

## Scoring: the OSC Pairing Index

The leaderboard reports an **OSC Pairing Index**, a per-material, physically-grounded score:

```
Pairing Index = N(E_F) × A_d(δ_material) × 300
```

where **A_d(δ)** is the max-distance d-wave (d<sub>x²−y²</sub>) pair correlation from the organizers'
precise 6×6 doped-Hubbard solver **run at each material's DFT band filling δ** (U/t = 8). Because
A_d depends strongly on doping, A_d(δ) traces a **d-wave dome** peaking near optimal hole doping
(δ ≈ 0.25–0.30) and vanishing at half-filling and heavy overdoping — so materials at different
fillings get genuinely different amplitudes. A_d ≤ 0 (no d-wave order) scores 0. The ×300 is a
single, monotone readability factor used **everywhere** (instrument, baseline, verified). The full
A_d(δ) table is in `scoring_meta.json`; the pipeline is in `pipeline/`.

- **Baseline** — N(E_F) × the published A_d(δ) for the material; the bar to beat (reproduces the anchor).
- **Provisional** — your submitted estimate, on the same scale; appears instantly.
- **Verified** — the organizers' precise solver at the material's filling sets the official rank.

**Honest interpretation:** the index is a **d-wave pair-correlation screening indicator**, not a
guaranteed critical temperature (Tc) or a confirmed superconductor. Two caveats we state plainly:

- **Not proven interaction-driven pairing.** A_d comes from a d-wave-biased variational (NQS/AGP)
  wavefunction, so it measures the pair correlation that a paired trial state sustains — not an
  unbiased proof that the Hubbard model itself wants d-wave. Independent exact-diagonalization (ED)
  cross-checks (contributed by participants) and our own control runs (d-wave vs Fermi-sea on a
  common 4×4 cluster) show the enhancement over the non-interacting case is **not monotonic and is
  dominated by finite-size effects** — consistent with the modern result that the pure 2D Hubbard
  model shows no robust d-wave superconductivity at U/t = 8 (Qin et al., *Science* 2020). Treat the
  A_d(δ) "dome" as partly a finite-size/ansatz feature.
- **Single-band approximation** (N(E_F) and δ from DFT, t from the active-band width, U/t = 8 as a
  control).

Use the index to **rank and prioritize candidates**, not to claim superconductivity. You compete by
computing a better, material-specific pairing estimate with your own many-body method.

### Why top scores cluster near the baseline — and the only two ways to exceed it

Every submission is scored on the material's **real** values — our pipeline N(E_F) and A_d at the
material's **real DFT filling** — regardless of any N(E_F)/A_d/δ a submission claims. A claimed value
is recorded (as `claimed`) but never ranked as-is. So the leaderboard tops out at the single
highest-scoring active material (currently ≈ 22), and many entries tie there. **Inflated claims are
automatically scored down to the material's real value** — this is deliberate, to keep the ranking
un-gameable. There are exactly two honest ways to go higher:

1. **Discovery track** — propose a *new* material (outside the active set) with a higher
   N(E_F) × A_d(δ). We downfold it ourselves with the published pipeline (DFT SCF → downfolding →
   solver); if its real value exceeds the baseline, your entry leads. New proposals are **queued for
   organizer downfolding** and posted when the DFT completes. *Caveat:* for multi-band metals the
   active-band selection can shift the filling δ (and therefore the score) substantially; such cases
   are flagged and the band choice is refined before a score is finalized.
2. **Method track (verified)** — a *reproducible* method that genuinely improves the estimate for a
   material. See the rules below.

## Gold / Method track — procedure and how it is judged

**How to submit (Gold / Method):**
1. **Register** your score and method name on Hugging Face (a PR under `submissions/`, or on the Space).
2. **Email a reproducibility package** to the organizers: the code, frozen checkpoint/config, a
   `run_*.sh` that reproduces the number, a SHA256 manifest, and any independent-seed robustness
   evidence. Do **not** rescale or empirically fit to the published references.
3. We **independently reproduce** it. If it reproduces, it is recorded as a **verified-reproducible
   Method contribution** (credited, with a badge).

**How the Method rank is decided — read this before expecting a higher score:**
Method standing is judged by **reproducibility and agreement with the independent reference (exact
diagonalization)** — **not** by the raw size of a claimed A_d. This is deliberate: a d-wave-biased
variational wavefunction can always report a larger A_d, and independent multi-size ED shows that the
**absolute** d-wave amplitude is *not size-converged* (see `validation/`), so a bigger A_d is not, by
itself, "more correct." Concretely:
- A claimed A_d larger than our solver value does **not** automatically beat the baseline on the
  leaderboard. The displayed score stays canonical.
- A reproduced method can **raise (or lower) a material's official A_d only once the ED calibration
  shows it is closer to the exact answer**; that correction then applies to everyone (and the
  contributor is credited / eligible for co-authorship).
- Until the calibration is settled, verified methods receive recognition (badge, Method shortlist),
  and absolute-score credit is held — not denied, just deferred to a calibrated basis.

**Multi-band materials:** when more than one band crosses E_F, the active-band choice can shift the
filling δ and hence the score; such materials are marked **provisional (band selection being refined)**
and are not finalized until resolved — this applies to the material for every submitter.

## Tracks & prizes (total US $3,000)

| Prize | Amount | Awarded to |
|---|---|---|
| **Grand** | $1,500 | highest **verified** d-wave tendency (any material) |
| **Best Method (Gold)** | $1,000 | top **verified** score with an open-sourced method |
| **Best Discovery (Open)** | $500 | best **verified** new material you propose |

One cash prize per person (the runner-up succeeds on overlap). On overlap, the higher prize is kept
with precedence **Grand > Best Method > Best Discovery**. **"Per person" means per person or team
(real identity)** — multiple accounts by the same person count as one entrant. For **Discovery**, the
award goes to the **first** entrant to propose a new material that then verifies; once a material is
added to the active set, later identical submissions get its canonical score but not the Discovery
credit. Ranks 2–5 and all valid entrants receive **co-authorship, hall-of-fame listing, and
leaderboard credit**.

---

## Frequently asked questions

### Do I need a GPU or to install anything?
No. The light track is a single pure-Python script that runs in seconds on any laptop CPU — Windows, Linux, or macOS. A GPU only helps if you choose the advanced full-stack track.

### What exactly am I predicting?
A **d-wave (d<sub>x²−y²</sub>) superconducting pairing tendency** for a given 2D material, from its effective Hubbard model. This is a screening signal, not a measured critical temperature.

### Does the #1 material mean the best superconductor?
It means the strongest d-wave pairing *tendency by our first-order screen* — the top candidate to investigate. It is not a confirmed superconductor or the highest Tc.

### How are winners verified?
The organizers run a precise strongly-correlated (NQS/GFMC-class) solver at each material's DFT band filling to get its d-wave amplitude A_d(δ); the verified score is N(E_F) × A_d(δ) × 300. The solver's inputs and its A_d(δ) table are published, so every verified score is reproducible; only the internal solver implementation is withheld to keep the ranking hard to game.

### Do I have to reveal my method or code?
No — you submit only result numbers. Only prize winners share reproducible code, under a contributor license. The verification engine runs on our servers and is never distributed, which is what keeps the ranking un-gameable.

### Where does the data come from?
Materials derive from the **Computational 2D Materials Database (C2DB)** under CC-BY-NC 4.0. We add value (family tags, cost classes, effective models, screening priors) and cite the source in `PROVENANCE.md`.

### When does the challenge close?
**Season 1 closes 31 December 2026, 23:59 KST.** The leaderboard, instrument, and authenticated submission are live now, and the active set is being expanded.

### Can an AI agent enter for me?
Yes. Point an AI coding agent (Claude Code / Codex) at the challenge and it can download the instrument, compute a score, and submit on your behalf.

---

## Keywords

superconductor discovery · unconventional superconductivity · d-wave pairing · 2D materials · twisted bilayer · moiré materials · strongly-correlated electrons · doped Hubbard model · density of states at the Fermi level · N(E_F) · computational materials science · machine learning for materials · open-science challenge · Hugging Face leaderboard · CPU-only benchmark · crowd-sourced materials screening.

## Citation & license

- **Baseline tools, downfolding pipeline, and protocol:** open source (`instrument/`, `pipeline/`).
- **Materials & derived models:** derived from C2DB under **CC-BY-NC 4.0** — see `PROVENANCE.md`.
- **Non-commercial:** because the source data is CC-BY-NC, OSC is a **non-commercial academic**
  challenge; prizes are research awards (recognition + co-authorship + honorarium), not a
  commercial use of the data. Any commercial use of the underlying data must be cleared with C2DB.

## Independent validation & contributors

OSC's verification solver is cross-checked against independent exact diagonalization (ED). The
first such cross-check — a common 4×4 cluster (U/t = 8) ED table with U = 0 controls — was
contributed by **Ku-ku** and is published at `validation/comparison_4x4_ED_vs_VMC.md` (CC-BY-NC 4.0,
with attribution). It independently reproduced all 64 verified scores from the published pipeline,
and checked the particle-hole relation on the **4×4** cluster at maximal distance (R = √5, (2,2);
agreement ≤ 3.3e-14) — the 6×6 R = (3,3) case was not computed. Because our 6×6 VMC A_d and the 4×4
ED values are essentially uncorrelated across filling on a single cluster size, ED is used (as
agreed) to correct **sign and rank** first, not absolute values, until the size dependence
converges. Contributors of verified ED/method
references are credited in `validation/` and the README, and are eligible for co-authorship on the
challenge report. We thank the participants and reviewers whose scrutiny made the scoring honest.
- **Verification engine:** operated by the organizers (FINAL-Bench), not distributed.

If OSC helps your work, please link the challenge Space (https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard) and credit **FINAL-Bench — Open Superconductor Challenge**.

*Hosted by FINAL-Bench as an open-science initiative. Season 1 is open until 31 December 2026 (23:59 KST). Star and watch to follow the leaderboard.*
