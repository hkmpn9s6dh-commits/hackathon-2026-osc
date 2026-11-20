# Multi-size ED of the U/t=8 Hubbard model: d-wave pair correlation at the largest distance
Prepared 2026-10-01 by team ku-ku. Shared for discussion only; this is not a submission.

## Definitions
- Model: square-lattice Hubbard model, t=1, U=8 or U=0. Periodic tilted clusters with lattice vectors 2x4 (2,0),(0,4); sqrt8 (2,2),(-2,2); sqrt10 (3,1),(-1,3); 3x4 (3,0),(0,4); 4x4 (4,0),(0,4). Sector Sz=0, N_up=N_dn.
- Pair operator (ours): Delta_d(i) = 1/2 sum_delta g(delta) b_{i,i+delta}, where b_ij = (c_i↑ c_j↓ + c_j↑ c_i↓)/sqrt2, g(±x)=+1 and g(±y)=-1. P_d(R) is <Delta_d(j)^† Delta_d(i)> averaged over all pairs whose minimum-image separation is R.
- Organizers' normalization: P_org = 2·P_ours. We derived this analytically and checked it numerically to 1e-15 on 4x4.
- R_max is the largest minimum-image distance on each cluster: sqrt5 for 2x4, sqrt10 and 3x4; 2 for sqrt8; 2·sqrt2 for 4x4.
- Degenerate ground states (|E-E0|<1e-7) are averaged with equal weight. For N≤12 the full degenerate multiplet is obtained with dense diagonalization (dim≤5000) or with Lanczos plus deflation until no further state lies within 1e-7. The largest residual ‖Hψ−E0ψ‖ is 9.6e-12.
- U=0 reference: canonical ED, using the same equal-weight average over the degenerate ground manifold. This agrees with a canonical Wick evaluation (equal occupation of the partially filled shell) to ≤1.9e-13. The grand-canonical Wick value at T=0.01 is also listed in the CSV. One exception is 4x4 at n=1: there the U=0 value is canonical Wick, not ED (400-fold degeneracy).
- 4x4 values come from our earlier run (phase6). That run used a separate symmetry-adapted code (translation + C4v) with the same operator definitions. We did not cross-check the two codes on a common cluster in this step, so the 4x4 rows come from a different code but are not independently validated against the smaller-cluster code.

## Table (values truncated from the CSV; ratio = P_d(U=8)/P_d(U=0), blank when |P_d(U=0)|<1e-12)
| cluster | N | n | N_up=N_dn | dim | E0 (U=8) | deg U=8 | deg U=0 | R_max | P_d(R_max) U=8 ours | P_org U=8 | P_d U=0 ours | P_org U=0 | ratio U8/U0 | U=0 method |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2x4 | 8 | 0.25 | 1 | 64 | -7.51754096 | 1 | 1 | 2.2360 | 0.00108014 | 0.00216029 | 0 | 0 | — | canonical ED |
| 2x4 | 8 | 0.5 | 2 | 784 | -10.49762201 | 1 | 4 | 2.2360 | -0.00181807 | -0.00363614 | 0.0156249 | 0.0312499 | -0.1163 | canonical ED |
| 2x4 | 8 | 0.75 | 3 | 3136 | -10.62689735 | 1 | 1 | 2.2360 | 0.0969231 | 0.193846 | 0.0937500 | 0.187500 | 1.03384 | canonical ED |
| 2x4 | 8 | 1.0 | 4 | 4900 | -7.12671234 | 1 | 4 | 2.2360 | 0.0164203 | 0.0328407 | 0.0312500 | 0.0625000 | 0.5254 | canonical ED |
| sqrt8 | 8 | 0.25 | 1 | 64 | -7.46479305 | 1 | 1 | 2.0 | 0 | 0 | 0 | 0 | — | canonical ED |
| sqrt8 | 8 | 0.5 | 2 | 784 | -6.70043783 | 4 | 36 | 2.0 | 0.0231024 | 0.0462048 | 0.0138888 | 0.0277777 | 1.6633 | canonical ED |
| sqrt8 | 8 | 0.75 | 3 | 3136 | -5.95282782 | 4 | 225 | 2.0 | 0.00755747 | 0.0151149 | 0.0138888 | 0.0277777 | 0.5441 | canonical ED |
| sqrt8 | 8 | 1.0 | 4 | 4900 | -3.78398080 | 1 | 400 | 2.0 | -0.0407816 | -0.0815632 | 0 | 0 | — | canonical ED |
| sqrt10 | 10 | 0.2 | 1 | 100 | -7.59126715 | 1 | 1 | 2.2360 | 0 | 0 | 0 | 0 | — | canonical ED |
| sqrt10 | 10 | 0.4 | 2 | 2025 | -8.86885383 | 5 | 16 | 2.2360 | 0.0160575 | 0.0321150 | 0 | 0 | — | canonical ED |
| sqrt10 | 10 | 0.6 | 3 | 14400 | -9.83963907 | 1 | 36 | 2.2360 | -0.0185496 | -0.0370993 | 0.0249999 | 0.0499999 | -0.7419 | canonical ED |
| sqrt10 | 10 | 0.8 | 4 | 44100 | -8.11706774 | 5 | 16 | 2.2360 | 0.0454973 | 0.0909946 | 0.0749999 | 0.149999 | 0.6066 | canonical ED |
| sqrt10 | 10 | 1.0 | 5 | 63504 | -5.10409191 | 1 | 1 | 2.2360 | 0.0179901 | 0.0359803 | 0.150000 | 0.300000 | 0.1199 | canonical ED |
| 3x4 | 12 | 0.1666 | 1 | 144 | -7.67599209 | 1 | 1 | 2.2360 | 2.8763189154397937e-05 | 5.7526378308795875e-05 | 0 | 0 | — | canonical ED |
| 3x4 | 12 | 0.3333 | 2 | 4356 | -11.037873924 | 1 | 4 | 2.2360 | -0.00324717 | -0.00649435 | 0.00694444 | 0.0138888 | -0.4675 | canonical ED |
| 3x4 | 12 | 0.5 | 3 | 48400 | -13.067143245 | 1 | 1 | 2.2360 | 0.0519376 | 0.103875 | 0.0416666 | 0.0833333 | 1.2465 | canonical ED |
| 3x4 | 12 | 0.6666 | 4 | 245025 | -12.64005415 | 1 | 4 | 2.2360 | 0.0180304 | 0.0360609 | 0.0434027 | 0.0868055 | 0.4154 | canonical ED |
| 3x4 | 12 | 0.8333 | 5 | 627264 | -10.76537911 | 1 | 1 | 2.2360 | 0.0284133 | 0.0568266 | 0.0607638 | 0.121527 | 0.4676 | canonical ED |
| 3x4 | 12 | 1.0 | 6 | 853776 | -5.83348425 | 1 | 1 | 2.2360 | 0.00501354 | 0.0100270 | 0.0173611 | 0.0347222 | 0.2887 | canonical ED |
| 4x4 | 16 | 0.125 | 1 | 256 | -7.76409059 | 1 | 1 | 2.8284 | 0 | 0 | 0 | 0 | — | canonical ED |
| 4x4 | 16 | 0.25 | 2 | 14400 | -11.32149713 | 3 | 16 | 2.8284 | 0.00604701 | 0.0120940 | 0 | 0 | — | canonical ED |
| 4x4 | 16 | 0.375 | 3 | 313600 | -14.72354031 | 1 | 36 | 2.8284 | -0.00686542 | -0.0137308 | 0.00781250 | 0.0156250 | -0.8787 | canonical ED |
| 4x4 | 16 | 0.5 | 4 | 3312400 | -16.46062675 | 3 | 16 | 2.8284 | 0.0240379 | 0.0480759 | 0.0234374 | 0.0468749 | 1.02561 | canonical ED |
| 4x4 | 16 | 0.625 | 5 | 19079424 | -17.51036669 | 1 | 1 | 2.8284 | 0.0300609 | 0.0601219 | 0.0468750 | 0.0937500 | 0.6413 | canonical ED |
| 4x4 | 16 | 0.75 | 6 | 64128064 | -14.92531021 | 2 | 36 | 2.8284 | 0.00491554 | 0.00983108 | 0.0208333 | 0.0416666 | 0.2359 | canonical ED |
| 4x4 | 16 | 0.875 | 7 | 130873600 | -11.86883556 | 3 | 225 | 2.8284 | 0.00960950 | 0.0192190 | 0.00520833 | 0.0104166 | 1.8450 | canonical ED |
| 4x4 | 16 | 1.0 | 8 | 165636900 | -8.46887501 | 1 | 400 | 2.8284 | 0.00309854 | 0.00619709 | — | 0 | — | canonical Wick, not ED |

## Size-dependence check (rule fixed before this recomputation: adjacent-size differences shrink monotonically, and the last difference is ≤25% of the largest-size value)
Only fillings available on ≥3 cluster sizes are judged. Sizes ordered by N; 2x4 and sqrt8 (both N=8) in our cluster-list order. Swapping them changes no verdict.
| n | sizes | P_org U=8 per size | sign stable (N≥10) | monotone | last diff / 25% limit | converged | absolute calibration |
|---|---|---|---|---|---|---|---|
| 0.25 | 2x4, sqrt8, 4x4 | 2x4 0.002160, sqrt8 0, 4x4 0.01209 | yes (one size only) | no | 0.01209 / 0.003023 | no | not allowed |
| 0.5 | 2x4, sqrt8, 3x4, 4x4 | 2x4 -0.003636, sqrt8 0.04620, 3x4 0.1038, 4x4 0.04807 | yes | no | 0.05579 / 0.01201 | no | not allowed |
| 0.75 | 2x4, sqrt8, 4x4 | 2x4 0.1938, sqrt8 0.01511, 4x4 0.009831 | yes (one size only) | yes | 0.005283 / 0.002457 | no | not allowed |
| 1.0 | 2x4, sqrt8, sqrt10, 3x4, 4x4 | 2x4 0.03284, sqrt8 -0.08156, sqrt10 0.03598, 3x4 0.01002, 4x4 0.006197 | yes | no | 0.003829 / 0.001549 | no | not allowed |

**Reading:** the sign of P_d(R_max, U=8) is the same on the N≥10 clusters at all four fillings (for n=0.25 and 0.75 only 4x4 qualifies, so that check is trivial). No filling shows converged absolute values, so on these sizes we consider only the sign and ranking of the 4x4 values usable for calibration.

Caveats: N≤16 clusters with different shapes and different R_max are not a strict finite-size sequence. 2x4 and sqrt8 have strongly degenerate U=0 shells (up to 400-fold), and sqrt8 has R_max=2, where pair operators still share sites.
