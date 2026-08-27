# ActDelta — placeholder inventory

**Every quantitative claim in `main.tex` is a placeholder.** Nothing here was
measured. The numbers were chosen to be (a) mutually consistent and (b)
consistent with the pre-registered pass/fail thresholds in
`../IDEA2-closed-loop-predictive-transmission.md` §8.1. Replace all of them
before submission.

Three groups matter most, because the paper's claims collapse without them:
**M-A** (§2.2), **M-1(b)** (§2.4) and **M-2** (§2.5).

> **Where the figure numbers now live.** Every figure's data has moved out of
> `main.tex` into a JSON file beside its drawing code, under
> `figures/experiment/` and `figures/schematic/` — see `figures/README.md`.
> Replacing a measurement means editing that JSON and running `make` in
> `figures/`; you never edit figure `.tex` for a data change. The map from the
> figure numbers used below to the files:
>
> | Paper | File (`figures/…`) |
> |---|---|
> | Fig. 1 architecture | `schematic/fig-arch` |
> | Fig. 2 M-0 link CDFs | `experiment/fig-m0-uplink-cdf` |
> | Fig. 3 M-1 prediction window | `experiment/fig-m1-rollout-error` |
> | Fig. 4a/4b M-2 | `experiment/fig-m2-fidelity-vs-decision`, `…/fig-m2-distance-ranking` |
> | Fig. 5a/5b M-3 | `experiment/fig-m3-imagined-steps`, `…/fig-m3-decision-error` |
> | Fig. 6 M-4 divergence | `experiment/fig-m4-divergence-trace` |
> | Fig. 7 protocol FSM | `schematic/fig-proto` |
> | Fig. 8 C2 bytes | `experiment/fig-c2-byte-reduction` |
> | Fig. 9 Pareto | `experiment/fig-pareto` |
> | Fig. 10 ρ sweep | `experiment/fig-rho-compute-ratio` |
> | Fig. 11 ablation | `experiment/fig-ablation` |
> | Fig. 12 physical robot | `experiment/fig-real-franka` |
>
> Each JSON carries its own `meta.source`, `meta.placeholder` and, where one
> exists, `meta.kill_threshold`, so this document and the figures cannot drift
> apart silently.
>
> **τ\* = 0.35 is now defined in exactly one place.** It is a scalar in
> `fig-m3-decision-error.json` (the panel that measures it) and is referenced
> from `fig-m1-rollout-error.json` and `fig-m4-divergence-trace.json`. In each
> figure the shaded safe band, the horizontal rule and the axis tick label are
> all drawn from that scalar, so the normalization warning below is now
> enforced by the build rather than by memory — but the three JSONs still have
> to be edited together.

---

## 0. The derivation chain (change these first)

Most byte numbers are derived from four base quantities. Change a base and
every dependent number must be recomputed.

| Base quantity | Placeholder | Used by |
|---|---|---|
| Frame payload, 3 views at native camera resolution | 137 kB | every uplink figure |
| Episode length | 50 s = 750 control steps at 15 Hz | every MB/episode number |
| Status-quo upload rate | 10 Hz = 66.7% of control steps | 68.4 MB baseline |
| Control period | 66.7 ms (15 Hz) | Table 1, Table 3, ρ |

Derived: `uplink MB = send_rate × 750 × 137 kB`.
Check: status quo `0.667 × 750 × 137 kB = 68.4 MB`; ActDelta
`0.041 × 750 × 137 kB = 4.2 MB`; fidelity trigger
`0.100 × 750 × 137 kB = 10.3 MB`. Headline ratios follow:
`10.3 → 4.2 = 59%`, `68.4 / 4.2 = 16.3×`, `68.4 / 0.9 = 75.2×`.

---

## 1. §2.1 M-0 — link feasibility (Fig. 2)

| Claim | Placeholder | Note |
|---|---|---|
| Sustained uplink needed at 10 / 15 / 30 Hz | 11.0 / 16.4 / 32.9 Mbps | = 137 kB × rate |
| Irish 5G uplink exceeds 11.0 Mbps | 23% of the time | **real, measurable from the trace set** |
| Irish exceeds 16.4 Mbps | 10.5% | idem |
| Lumos5G / MN-Wild at 11.0 Mbps | 45% / 14% | idem |
| Client-side downscale to 224² | 36 kB, factor 3.8 | arithmetic, verify against real JPEG |
| Uploads that queue behind their predecessor | 41% | needs trace replay |
| Mean observation age, status quo | 310 ms | needs trace replay |
| Whole Fig. 2 CDF curves | invented | **replaceable from public traces without any robot** |

Fig. 2's three CDFs are the cheapest real data in the paper. Do them first.

---

## 2. §2.2 M-A — compute asymmetry (Table 1) ⚠ GO/NO-GO

Pass criterion: **≥ 100× per-control-step compute gap.** Below 20× the paper dies.

| Row | \sys W | SmolVLA | π0 | OpenVLA |
|---|---|---|---|---|
| Weights (bf16) | 0.14 GB | 0.90 GB | 6.6 GB | 15.2 GB |
| Peak memory | 0.21 GB | 1.4 GB | 8.1 GB | 16.9 GB |
| FLOP / control step | 3.6 G | 391 G | 2.14 T | 4.90 T |
| ratio to W | 1× | **109×** | 594× | **1361×** |
| Latency, Orin NX | 11.7 ms | 128 ms | 1.42 s † | OOM |
| Energy / step | 0.19 J | 2.6 J | 27 J † | — |
| Latency, A100 | 1.9 ms | 14 ms | 38 ms | 62 ms |

All twenty-odd cells are estimates. The FLOP counts are the load-bearing ones;
the memory figures are close to real (weights = 2 bytes × parameters) and the
"OpenVLA does not fit in 16 GB" claim is safe. Also placeholders: robot budget
`B ≈ 8.0 TFLOP/s`, hence `ρ = 0.109` and `ρ_min = 3.6 G / 4.90 T = 7.3e-4`.

**This is the one experiment that needs no training and can run in a day.** Do
it second, and be ready to shrink the world model until the ratio clears 100×.

---

## 3. §2.4 M-1 — prediction window (Fig. 3) ⚠ GO/NO-GO

Pass criteria: (a) > 40% of timesteps predictable for 5 steps;
(b) **action conditioning cuts 5-step error by > 30%**. (b) failing kills the paper.

| Claim | Placeholder |
|---|---|
| Error at k=5, action-conditioned / unconditioned | 0.31 / 0.58 → **46.6% reduction** |
| Timesteps under threshold for ≥ 5 steps | 63% |
| Usable window, conditioned / unconditioned | 5.4 / 2.9 steps |
| Usable window on DROID | 4.1 steps |
| All three curves, k = 1…12 | invented |

The error axis is normalized so that 0.35 = the policy-flip threshold of Fig. 5b.
Keep that normalization when substituting real numbers, or Fig. 3, Fig. 5, Fig. 6
and Eq. 5 stop agreeing with each other.

---

## 4. §2.5 M-2 — fidelity vs. decision relevance (Fig. 4) ⚠ GO/NO-GO

Pass criteria: head vs. action divergence **ρ_s > 0.60**; pixel L2 vs. action
divergence **ρ_s < 0.85**. Either failing kills the paper (C1 collapses).

| Quantity | Placeholder |
|---|---|
| Spearman: pixel L2 / SSIM / LPIPS / depth / WM latent / \sys head | 0.31 / 0.28 / 0.36 / 0.39 / 0.52 / **0.74** |
| Quadrant: correctly skipped | 41.7% |
| Quadrant: **wasted** (high pixel error, action unchanged) | **31.7%** |
| Quadrant: **missed** (low pixel error, action flips) | **12.4%** |
| Quadrant: correctly sent | 14.2% |
| Combined misclassification | 44.1% |
| Scatter points | 89 invented points in the stated proportions |
| Corpus | 2,000 DROID episodes + 4 LIBERO suites |

The quadrant split at (0.35, 0.30) is itself a choice; state how the thresholds
were picked when the real data arrives. The 31.7% figure is what predicts the
59% byte saving — if the real number moves, the headline moves with it.

---

## 5. §2.6 M-3 — cost of imagined observations (Fig. 5)

| Claim | Placeholder |
|---|---|
| Success vs. imagined steps (0,2,4,6,8,10,12,16) | 79.4 / 78.6 / 77.1 / 74.2 / 68.5 / 60.3 / 49.1 / 28.4 |
| Success vs. decision-space error (0.05…0.75) | 79.1 / 78.4 / 77.0 / 73.8 / 66.2 / 55.1 / 41.7 / 29.0 |
| Policy-flip threshold τ* | 0.35 |
| Operating threshold τ₀ | 0.15 |
| Head error, P99 (ε_Φ) | 0.09 |

τ*, τ₀ and ε_Φ propagate into §3.3, §3.4, Eq. 5 and §5.4.

---

## 6. §2.7 M-4 — divergence under loss (Fig. 6)

| Claim | Placeholder |
|---|---|
| Injected uplink loss | 1.2% |
| Episode catastrophe rate, no protocol | **34.2%** |
| Episode lost at | t = 8.4 s |
| Intervals containing a contact event, resync-only | 19.7% |
| All three divergence traces | invented |

---

## 7. §3 Design constants

| Constant | Placeholder | Where |
|---|---|---|
| World model size / latent | 68 M params, 96 tokens, 6 blocks, width 384 | §3.1 |
| Training cost | 19 h on 8× RTX 3090, 2,000 LIBERO demos + 40 k DROID | §4 |
| fp16 cross-platform drift | 4×10⁻⁴ per step | §3.1 |
| Cost of 8-bit latent quantization | 0.4 pp | §3.1, §5.5 |
| Head size / latency / training | 2.1 M, 1.1 ms, 1.4 M pairs, 9 GPU-h | §3.2 |
| VLA vision tower cost (the rejected alternative) | 214 GFLOP/step = 59× our pipeline | §3.2 |
| Gap: head vs. true VLA-encoder latent | 1.6 pp | §3.2 |
| τ₀ / α / [τ_min, τ_max] | 0.15 / 0.5 / [0.08, 0.30] | §3.3 |
| Heartbeat period / size / rate | 8 steps / 16 B / 240 B/s | §3.4 |
| Forced resync interval | 60 steps (4 s), 1.7% send-rate floor | §3.4 |
| Drift rate β / head miss rate | 0.07 per step / 1.3% | §3.4, Eq. 5 |
| Stop-the-robot floor | 0.6 Mbps sustained uplink | §3.5 |
| Code size | 5,200 Python + 1,100 C++ | §4 |

---

## 8. §5 Evaluation

### 8.1 Fig. 8 — the C2 single-variable result (the paper's core claim)

Uplink MB per episode, fidelity trigger vs. \sys, at matched success (78.2% vs. 78.9%):

| | L-Spatial | L-Object | L-Goal | L-Long | Simpler | Kinetix |
|---|---|---|---|---|---|---|
| fidelity | 9.1 | 8.4 | 10.3 | 13.6 | 11.8 | 15.2 |
| \sys | 3.6 | 3.1 | 4.2 | 6.0 | 5.3 | 8.1 |
| reduction | 60.4% | 63.1% | **59.2%** | 55.9% | 55.1% | 46.7% |

LIBERO mean = 59.2% is the abstract's headline. Kinetix at 46.7% is deliberately
the weakest column and is used in §7 as the honest boundary case.

### 8.2 Table 2 — end-to-end

Every cell is a placeholder. Success (LIBERO / SimplerEnv / Kinetix), uplink MB,
send rate, P99.9 divergence:

| Arm | LIBERO | Simpler | Kinetix | MB | send | div |
|---|---|---|---|---|---|---|
| oracle | 79.4 | 70.6 | 68.2 | — | 100% | — |
| (1) status quo | 71.2 | 62.8 | 55.1 | 68.4 | 66.7% | — |
| (2) H.265 | 74.6 | 65.9 | 58.7 | 11.9 | 66.7% | — |
| (3) pixel diff | 72.9 | 64.1 | 57.0 | 9.4 | 9.1% | 0.61 |
| (4) SoD + Taylor | 68.7 | 60.3 | 52.4 | 14.7 | 14.3% | 0.74 |
| (5) SoD on latent | 73.5 | 65.0 | 58.1 | 12.3 | 12.0% | 0.44 |
| (6) WM + fidelity | 78.2 | 69.1 | 63.4 | 10.3 | 10.0% | 0.29 |
| (7) learned codec | 75.8 | 67.2 | 60.8 | 7.7 | 66.7% | — |
| (8) **\sys** | 78.9 | 69.8 | 64.6 | 4.2 | 4.1% | 0.21 |
| (9) \sys + (7) | 78.4 | 69.4 | 64.0 | 0.9 | 4.1% | 0.21 |

Row (9) assumes the learned codec achieves **4.6×** on resync frames (not the
8.9× it achieves on the full stream), because resync frames carry more
decision-relevant content. Verify this assumption explicitly — it is doing real
work in the 75× headline.

### 8.3 Fig. 9 — Pareto sweep

\sys (τ = 0.30 → 0.08): (2.1, 74.8) (3.0, 77.6) (4.2, 78.9) (6.5, 79.1) (10.0, 79.2).
Fidelity trigger: (4.4, 68.1) (6.8, 74.0) (10.3, 78.2) (15.9, 78.8) (24.0, 79.0).
The claimed "roughly constant 2.4× separation" is a property of these invented
points; check whether it survives real data before repeating the claim.

### 8.4 Fig. 10 — ρ sweep

ρ ∈ {1e-3, 3e-3, 1e-2, 3e-2, 0.109, 0.35, 1.0} →
byte reduction {36, 45, 52, 56, **59**, 62, 63}%,
success {71.4, 74.9, 77.2, 78.4, **78.9**, 79.1, 79.2}%.
Only ρ = 0.109 is native hardware; the rest are MPS-emulated budgets.

### 8.5 §5.4 — protocol

Catastrophe rate at 0 / 1.2% / 5% loss: no protocol 1.8 / 34.2 / 71.5%;
resync only — / 9.4 / 22.1%; full protocol — / 2.1 / 4.6%.
Median detect-to-recover 84 ms. P99.9 divergence 0.21 vs. predicted bound 0.24,
max observed 0.33, over 2,400 episodes. T_resync insensitive over 30–120 steps
(±0.9 pp, ±1.4% bytes); −6.1 pp past 180 steps.

### 8.6 Fig. 11 — ablation (at 1.2% loss)

Success: 61.2 / 68.9 / 71.3 / 74.6 / 76.4 / 78.2 / **78.9** / 79.3.
Bytes (MB): 4.0 / 3.4 / 6.9 / 5.8 / 7.1 / 10.3 / **4.2** / 3.8.
Rows: no seq numbers, no forced resync, no action conditioning, static τ,
WM-latent trigger, fidelity trigger, \sys, oracle divergence.
Further sweeps: WM 18 M → 76.1% (3.1-step window), 210 M → 79.2% (misses the
deadline); head transfer π0 → OpenVLA costs 2.3 pp and 8% bytes, jointly trained
head recovers to 0.6 pp; without latent quantization, 3.1% of episodes drift.

### 8.7 Table 3 and §5.6 — robot cost

Encoder 6.9 ms / 0.11 GB / 0.11 J; rollout 3.4 ms / 0.06 GB / 0.05 J;
head+trigger 1.1 ms / 0.02 GB / 0.02 J; protocol 0.3 ms / 0.01 J.
Total 11.7 ms / 0.21 GB / 0.19 J = 17.5% of the control period.
Power accounting: 2.85 W compute, 5.2 W radio (status quo) vs. 0.32 W (ours),
net 5.5 W → 3.2 W = 1.7×; trigger at 7.5 Hz → 1.42 W, net 2.6×.
The 5 G uplink power model behind 5.2 W is an assumption; MN-Wild has real
power traces and should replace it.

### 8.8 Fig. 12 — physical robot

Success at 1 / 2 / 4 / 8 / 12 Mbps: status quo 20 / 35 / 60 / 75 / 80;
\sys 65 / 75 / 80 / 80 / 80. 160 trials, two tasks. Byte ratio at 2 Mbps 13.2×
(5.8 MB vs. 0.44 MB) against 16.3× in simulation.

---

## 8.9 Figure conventions (keep these when the real data lands)

The plots share one visual language, defined once in the `compactplot` /
`widecompact` styles in `figures/preamble.tex`. Preserve it when substituting
measurements, or the paper stops reading as one artifact.

| Element | Meaning | Where it is used |
|---|---|---|
| **cB red, thick, filled circles** | \sys, always | Figs. 3, 5a, 6, 8, 9, 10, 11, 12 |
| **cA blue, dashed, squares** | the arm we are compared against | Figs. 3, 6, 8, 9, 11, 12 |
| **cGrey** | status quo, oracle bounds, annotations | everywhere |
| **cE purple** | protocol ablations (Fig. 11) | Fig. 11 |
| **light shaded band** | a region where something *fails* | Figs. 2, 3, 5, 6, 10, 12 |
| **circled numbers** `\cnum{n}` | flow steps, matched between figure and caption | Fig. 1 |
| **red boxes vs. grey boxes** | new in \sys vs. reused unchanged | Fig. 1 |

Every series is separable in **grayscale** by dash pattern and marker, not by
colour alone — MobiCom reviewers print. Legends sit on an opaque white ground
so a curve passing behind them stays readable. Two conventions carry meaning
and should not be dropped: the *shaded failure band* (which turns "here is a
curve" into "here is where it breaks"), and the `better` arrow on Fig. 9
(which tells a reader which corner of a Pareto plot to look at).

Annotations that will need re-placing if the numbers move: the `77% of the
time` callout (Fig. 2), the `-47%` gap bar and the `2.9`/`5.4` crossings
(Fig. 3), the two quadrant callouts (Fig. 4a), the `2.4x` gap bar (Fig. 9),
the per-suite reduction labels (Fig. 8), and the `+40 pp` bar (Fig. 12). All
are positioned in data coordinates, so they move with the axes but not with
the values.

**Captions are deliberately short** (median 29 words, none over 48). The
format review found the caption median at 64 words, which is roughly twice what
the MobiCom corpus does, so the setup, the provenance and the per-point
interpretation now live in the body prose of the subsection that owns the
figure, and each caption is a bolded claim plus the one sentence a reader needs
to parse the axes. Two consequences for whoever substitutes the real data.
First, do not shrink the caption font to buy space: it is at 10 pt, which the
review confirmed is correct, and shrinking it is the wrong fix. Second, several
numbers that used to be in captions are now sentences in the body — the eight
uplink figures of the ablation (§5.5), the $\rho_{\min}$ value and the
$\rho\approx10^{-2}$ window (§5.3), the per-task numbers at 2 Mbps (§5.7), and
the Pareto knee (§5.2). Search the subsection for the value, not just the
caption, when a measurement changes.

---

## 9. Citation hygiene

**Done (2026-08-19).** Every 25xx/26xx arXiv entry was checked against the arXiv
metadata API and now carries the paper's real author list and real title. Of the
24 entries that showed `author = {{Anonymous}}`, 23 are fixed; the only one left
is `policyvoi2027`, which is deliberate (see below). Six in-text sentences that
described those papers were rewritten at the same time, because the reconstructed
titles had led to claims the real papers do not make — in particular
`genvidcomp2025` optimizes compression rate, not downstream task performance, so
the "closest to our criterion" credit in §6 now goes to `cdtsemcom2026`, which
really does optimize a decision-value-per-bit objective. Two entries had
identifiers pointing at unrelated papers (a spin-Seebeck paper and a coronagraph
paper) and were repointed by title search. One entry, the former
`latentpred2026`, could not be found at all and was removed rather than invented;
`cdtsemcom2026` took its place in the argument.

**Still open for camera-ready.**

- **DOIs.** Only `tofc2025` carries one. Add the rest.
- **Venues.** 28 of the 72 entries are still arXiv preprints (39%). Several will
  have appeared by camera-ready; convert each to the real venue.
  `vlacache2025` → NeurIPS 2025, `edgeserving2026` → IEEE ICCCN 2026 and
  `tofc2025` → IEEE TMC are already converted.
- **Do not put an `@` sign in the header comment of `references.bib`.** BibTeX
  has no comment syntax and reads it as the start of an entry; that is a real
  build failure, and it already happened once.

`policyvoi2027` is the companion submission. §3.2 and §6 declare the shared
"unavailable ground truth → obtainable proxy → offline calibration" methodology
and the latency/bandwidth split. Both papers must carry that declaration or a
reviewer seeing both will read it as self-repetition.

---

## 10. Double-blind checklist before upload

- [ ] Uncomment `\hypersetup{draft}` in `main.tex` (the CFP forbids embedded links)
- [ ] Confirm no author names in the PDF metadata (`pdfinfo main.pdf`)
- [ ] Run the **banal** format checker
- [x] Body is exactly 12 pages; references start on page 13. Both columns of
      page 12 are full to the bottom, so *any* added sentence pushes the body to
      13 pages — cut before you add.
- [ ] Decide whether to keep the `review` option's line numbers. MobiCom does
      not require them and the format review left the call to us; they are
      currently on, which is why the PDF shows numbers in both margins.
- [ ] File under 15 MB (currently ~0.7 MB)

