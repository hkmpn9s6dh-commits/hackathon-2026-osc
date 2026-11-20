---
title: "Open Superconductor Challenge: Help Discover the Next 2D Superconductor — From Your Laptop"
thumbnail: /blog/assets/osc/thumbnail.png
authors:
- user: FINAL-Bench
date: 2026-09-29
tags:
- open-science
- superconductivity
- materials-discovery
- 2d-materials
- hubbard-model
- leaderboard
---

# Open Superconductor Challenge: Help Discover the Next 2D Superconductor — From Your Laptop

> **In one sentence:** The Open Superconductor Challenge (OSC) is a free, open-science competition on Hugging Face where anyone can screen thousands of 2D materials for **unconventional (d-wave) superconductivity** using a laptop CPU, submit a score, and climb a verified leaderboard — for a **US $3,000 prize pool + co-authorship**.

**👉 Join the challenge now: [huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard](https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard)**

---

## The problem: finding superconductors is slow and expensive

Superconductors carry electricity with zero resistance, and **unconventional (d-wave) superconductivity** — the kind seen in cuprates and twisted bilayer graphene — is one of the most important open problems in condensed-matter physics. But discovering new superconducting materials experimentally is painfully slow: each candidate can take months in the lab, and there are thousands of promising 2D materials to check.

What if we screened them *computationally, before the lab* — and did it as a community?

## The idea: crowd-screen first, verify precisely

That is exactly what the **Open Superconductor Challenge (OSC)** does. It splits the work in a way that makes discovery affordable:

- **The crowd screens broadly.** For each material, we provide a ready-made **effective model** (a doped Hubbard model). You estimate its d-wave pairing tendency with any method — a laptop CPU is enough — and submit a small file.
- **The organizers verify precisely.** We spend heavy many-body compute only on the **top** submissions, using a precise strongly-correlated reference solver that confirms which candidates are real.

This "compute arbitrage" finds promising superconductor candidates for a fraction of the usual cost — and everything a participant needs is open. Only the final verification engine stays private, which keeps the leaderboard fair and hard to game without hiding the science.

## What you get, and what you do

For every active material, OSC hands you a downfolded **Hubbard effective model**:

| Quantity | Meaning |
|---|---|
| `t` | nearest-neighbor hopping (eV) |
| `U` | on-site interaction (eV); the challenge fixes the correlated regime at **U/t = 8** |
| `N(E_F)` | density of states at the Fermi level (states/eV/atom) — the first-order BCS indicator |

Your job: compute a **material-specific d-wave (d<sub>x²−y²</sub>) pairing estimate** that beats the first-order screen, and submit it.

## How to enter in 4 steps (no GPU, no install)

1. **Sign in** with Hugging Face on the [OSC Leaderboard Space](https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard) — this verifies your identity.
2. **Download the instrument** — a single pure-Python script that runs on Windows, Linux, and macOS:
   ```bash
   huggingface-cli download FINAL-Bench/OSC-Superconductor \
     instrument/osc_instrument.py instrument/pair_baseline.py \
     --repo-type dataset --local-dir osc
   cd osc/instrument
   ```
3. **Pick a material and run it** (seconds on a laptop):
   ```bash
   python osc_instrument.py --material_id OSC-00129 --author YOUR_NAME
   ```
   To compete on the gold track, replace `estimate_pairing()` with your own many-body method (ED, VMC, DMRG, mean-field, or ML).
4. **Submit** on the material's card in the Space, or by Pull Request. Your provisional score appears instantly.

> 🤖 **AI agents welcome:** point Claude Code or Codex at the challenge and it can claim a material, run the instrument, and submit for you.

## The leaderboard today

The active set already carries a computed effective model for **63** materials out of a **4,832**-material universe (and it is growing). A snapshot of the current verified top:

| Rank | Material | OSC Pairing Index | Status |
|---|---|---|---|
| 1 | CuS₂ | 23.31 | ✅ verified |
| 2 | NV₂ | 20.39 | ✅ verified |
| 3 | Co₂Se₂ | 16.82 | ✅ verified |
| 4 | H₂Ti | 16.21 | ✅ verified |
| 5 | Br₂Cu | 15.86 | ✅ verified |

The **OSC Pairing Index** is `N(E_F) × A_ref × 10000`, where `A_ref = 0.0503` is the reference d-wave pair correlation measured by our precise 6×6 doped-Hubbard solver at U/t = 8. A higher index means a stronger d-wave pairing **tendency** by our screen — a better candidate to investigate — **not** a guaranteed critical temperature. That honesty is the point: the challenge asks you to turn a first-order screen into real, material-specific many-body physics.

## Prizes and credit

| Prize | Amount | Awarded to |
|---|---|---|
| **Grand** | $1,500 | highest verified d-wave tendency (any material) |
| **Best Method (Gold)** | $1,000 | top verified score with an open-sourced method |
| **Best Discovery (Open)** | $500 | best verified new material you propose |

One cash prize per person; ranks 2–5 and all valid entrants receive **co-authorship, hall-of-fame listing, and leaderboard credit**.

## FAQ

**Do I need a GPU?** No — the light track runs on any laptop CPU with zero installation.

**Do I have to share my code?** No; you submit only result numbers. Only prize winners share reproducible code, under a contributor license.

**Is the #1 material a confirmed superconductor?** No — it is the strongest d-wave *candidate* by our first-order screen, not a measured Tc.

**Where does the data come from?** Materials derive from the **Computational 2D Materials Database (C2DB)** under CC-BY 4.0, enriched by us and cited in the dataset's `PROVENANCE.md`.

**When does it close?** Season 1 closes **31 December 2026, 23:59 KST**.

## Get involved

Open science works best when more people join. Whether you are a condensed-matter researcher, an ML practitioner, a student, or an AI agent, you can help map the landscape of 2D superconductivity today.

**⭐ Star and enter the challenge: [huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard](https://huggingface.co/spaces/FINAL-Bench/OSC-Leaderboard)**
**📦 Dataset & tools: [huggingface.co/datasets/FINAL-Bench/OSC-Superconductor](https://huggingface.co/datasets/FINAL-Bench/OSC-Superconductor)**

*Hosted by FINAL-Bench as an open-science initiative.*
