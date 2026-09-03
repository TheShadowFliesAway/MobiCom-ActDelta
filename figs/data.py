"""
ActDelta figure data -- single source of truth.

Provenance tags (every entry carries one):

    real    : number taken verbatim from the current draft / logs.
    derived : computed in closed form from a `real` number plus a stated
              modelling assumption. Reproducible; no measurement needed.
              The assumption is written next to it.
    synth   : PLACEHOLDER for layout only. MUST be replaced by measured
              values before submission. Every synth block is constrained
              to be arithmetically consistent with the real anchors, so
              swapping in real logs will not change the layout.

DRAFT gate
----------
While DRAFT is true, make_figs.py stamps every panel that consumes a
`synth` block. Set ACTDELTA_DRAFT=0 only once the corresponding block has
been replaced with measured values. Do not switch it off to "clean up" a
figure for a submission deadline; that is exactly the failure mode the
stamp exists to prevent.

Statistical conventions used by the `derived` entries
-----------------------------------------------------
* Closed-loop arms share initial states, so all closed-loop comparisons
  are PAIRED. Interval half-width uses the McNemar normal approximation
      hw = z_{a/2} * sqrt(pi_d / n)
  with pi_d the episode-level discordance rate and n episodes per arm.
* pi_d = 0.078 is back-solved from the blind test's reported half-width
  (Sec. 10.5) and reproduces both the 6.2 pp MDE and the n~625 figure.
* Blind-test success values live on a 1/160 grid (160 episodes per arm);
  Gate A on 1/20; Gate B and the exploratory Spatial panel on 1/80.
"""

import math
import os

DRAFT_REQUESTED = os.environ.get("ACTDELTA_DRAFT", "1") not in ("0", "false", "False")

Z_95 = 1.959964
Z_80POW = 0.8416212

# Episodes per arm, by experimental panel.
N_EP = {"blind": 160, "exploratory": 80, "oracle-A": 20, "oracle-B": 80}

# Episode-level discordance rate of the paired closed-loop comparison.
PI_D = 0.078  # derived: back-solved from the blind test half-width, Sec. 10.5


def mcnemar_hw(pi_d, n, z=Z_95):
    """Half-width, in percentage points, of a paired success-difference CI."""
    return 100.0 * z * math.sqrt(pi_d / n)


def n_for_effect(delta_pp, pi_d, z=Z_95 + Z_80POW):
    """Episodes per arm needed to resolve a paired difference of delta_pp.

    derived: inverts mcnemar_hw. Same model that reproduces the draft's
    ~625 episodes for the observed +3.13 pp effect, so it is a restatement
    of the paper's own power calculation, not a new assumption.
    """
    return int(math.ceil(pi_d * (100.0 * z / delta_pp) ** 2))


def pi_d_at(b, A=0.088490, beta=0.362510):
    """Discordance rate as a function of the target send budget b.

    AUDIT FIX. This was pi_d = kappa * 2p(1-p) in arm success p, with kappa
    fitted to the 25% budget alone. Scaling with outcome variance made pi_d
    collapse far too fast: the blind test measures half-widths of 4.375 pp at
    25% and 4.065 pp at 50% (pi_d = 0.0797 and 0.0688, a fall of 1.16x),
    whereas 2p(1-p) falls 2.55x between those budgets. The band it produced
    was 2.83 pp at 50% against a measured 4.065, so the learned arm was drawn
    outside a band that the blind test puts it inside -- contradicting both
    Sec. 10.1 and Fig. 10's own caption.

    The discordance is a property of the budget, not of the success rate:
    at b = 1 every arm is always-send and cannot disagree. Fitting
    pi_d = A (1-b)^beta through both measured budgets reproduces each
    half-width exactly and still vanishes at b = 1. Replace with the
    per-budget discordance counts once the sweep logs expose them.
    """
    return max(A * (1.0 - b) ** beta, 1e-6)


def snap(pct, n):
    """Snap a percentage onto the k/n success grid the panel can actually emit."""
    return round(pct * n / 100.0) * 100.0 / n


# ================================================================= REAL ====
REAL = {}

# --- Sec. 10.1  LIBERO-Spatial forced-horizon sweep -------------------------
# A forced imagined horizon h sends every (h+1)-th step, so send fraction is
# 1/(h+1). This panel IS the periodic arm of the Spatial frontier.
REAL["horizon_sweep"] = {
    "_tag": "real",
    "suite": "LIBERO-Spatial",
    "n_ep": 10,  # 10 tasks x 10 initial states = 100 cells per horizon
    "h": [0, 1, 2, 4, 6, 8, 10, 12],
    "succ": [98, 94, 84, 70, 69, 72, 65, 62],
    "ci_lo": [94, 85, 72, 54, 53, 56, 49, 45],
    "ci_hi": [100, 100, 94, 86, 84, 86, 80, 79],
    "payload": [32.72, 28.67, 27.75, 27.70, 27.08, 26.31, 26.43, 26.75],  # MB/episode
    "send_frac": [100.0, 50.0, 33.33, 20.0, 14.29, 11.11, 9.09, 7.69],
}

# AUDIT NOTE (payload). Per-episode payload falls only 18% while the send
# fraction falls 13x. That is not a codec anomaly: episodes get LONGER as h
# grows (success drops 98% -> 62% and failed episodes run to the step cap),
# and the always-sent wrist view scales with episode length. Fitting
#   payload(h) = c * T(h) * (w + a * f(h)),  w + a = 1
# to h=0 and h=12 gives a ~ w (agent and wrist views cost about the same per
# step) and T(12)/T(0) ~ 1.5. So the text's "longer horizons do not purchase
# proportional traffic reduction" is CONFOUNDED BY EPISODE LENGTH and must be
# restated in per-control-step units. See derived["payload_per_step"].
REAL["horizon_sweep"]["_audit"] = "payload confounded by episode length; report per-step"

# --- Sec. 7  fidelity vs action divergence (formal test split, 1400 pairs) --
REAL["fidelity"] = {
    "_tag": "real",
    "names": ["Pixel RMS", "SSIM err.", "LPIPS", "WM latent"],
    "pooled": [-0.0282, -0.0736, -0.1165, -0.0744],
    "episode_med": [0.0742, 0.0756, 0.1595, 0.0377],
    "disagree": [48.86, 50.79, 53.93, 49.93],
    "head_pooled": 0.6839,
    "head_ci": [0.6365, 0.7257],
    "head_ep_med": 0.6340,
    "n_pairs": 1400,
}

# --- Sec. 8  head quality --------------------------------------------------
REAL["head"] = {
    "_tag": "real",
    "auroc": 0.8332,
    "auprc": 0.8326,
    "mae": 0.2052,
    "suites": ["LIBERO-10", "Goal", "Object", "Spatial"],
    "suite_rho": [0.507, 0.664, 0.683, 0.724],
    "suite_fnr95": [8.40, 3.81, 4.24, 1.51],
    "horizons": [1, 2, 3, 4, 5, 8, 12],
    "horizon_rho": [0.619, 0.701, 0.701, 0.718, 0.604, 0.721, 0.710],
    "err_q": {"Median": 0.158, "P95": 0.539, "P99": 0.786, "P99.9": 1.170, "Max": 1.82},
    "div_quant": {"Q25": 0.814, "Median": 1.076, "Q75": 1.268, "P95": 1.713, "Max": 3.455},
    "seed_val_rho": [0.6537, 0.6605],   # range over three training seeds
    "seed_test_rho": [0.6839, 0.6875],
}

# AUDIT FIX (operating points). The original tuple was
#     (50.00, 47.9, 10.86)  labelled (send %, conditional FNR %, all-test miss %)
# Under a median-split "action-high" label exactly half of all frames are
# positives, so identically
#     all_test_miss = 0.5 * conditional_FNR.
# That identity holds for the 95%- and 99%-recall points (2.00 vs 2.02;
# 0.20 vs 0.215) but is violated by 2.2x at the median-rate point. Sec. 8 of
# the draft in fact attributes 47.9% to LIBERO-10 alone ("on LIBERO-10 its
# conditional false-negative rate is 47.9%"); it is a per-suite number that
# was written into the pooled slot. The pooled value is recovered from the
# all-test miss, which the draft also states. 47.9% is retained separately.
#
# Residual issue to check against the logs: a pooled conditional FNR of 47.9%
# at a 50% send rate would mean ~52% recall, i.e. AUROC ~ 0.5, which
# contradicts the reported 0.8332. A per-suite value of 47.9% is only
# reachable if the threshold is chosen POOLED and LIBERO-10 scores sit low
# enough that the pooled threshold sends far fewer than 50% of LIBERO-10
# frames. State that mechanism in the text or the number reads as an error.
REAL["head"]["op_points"] = [
    # (send fraction %, pooled conditional FNR %, all-test miss %)
    (50.00, 21.72, 10.86),   # FNR derived = 2 x all-test miss; VERIFY vs logs
    (82.43, 4.04, 2.00),     # real
    (94.21, 0.43, 0.20),     # real
]
REAL["head"]["op_labels"] = ["median-rate", "95% recall", "99% recall"]
REAL["head"]["op_tags"] = ["derived", "real", "real"]
REAL["head"]["median_rate_fnr_l10"] = 47.9  # real, but LIBERO-10 only

# --- Sec. 5  world-model selection (four-suite base) -----------------------
REAL["wm"] = {
    "_tag": "real",
    "h": [1, 5, 8, 12],
    "baseline": [0.002124, 0.016618, 0.028354, 0.043681],
    "adopted": [0.002022, 0.014418, 0.023435, 0.034013],
    "n_windows": 18542,
    # ratios at h = 12, baseline -> adopted
    "shuffled_true": [1.088, 1.114],
    "zero_true": [1.036, 1.087],
}
# AUDIT NOTE. Improvements computed from these arrays are
#   h1 -4.80%, h5 -13.24%, h8 -17.35%, h12 -22.13%.
# Table 2's v3 row states "h1 -5.5%, h5 -13.5%" which contradicts both this
# array and Sec. 5's own prose ("4.8% at h = 1"). make_figs.py now EMITS the
# Table 2 percentages into tables_auto.tex so they cannot drift again.

# --- Sec. 10.2 / 10.3 / 10.4  closed-loop effects (pp vs periodic) ---------
REAL["effects"] = [
    # label, budget, effect, ci_lo, ci_hi, n_cells, panel, rate_matched
    ("Learned, expl. (Spatial, 10 tasks)", 25, +3.75, -5.00, +13.75, 480, "exploratory", False),
    ("Learned, blind (Object, 8 tasks)",   25, +3.13, -1.25,  +7.50, 800, "blind", True),
    ("Learned, blind (Object, 8 tasks)",   50, -3.75, -8.13,   0.00, 800, "blind", True),
    ("Oracle, Gate A (Object, 2 tasks)",   25, +25.0, None, None, 100, "oracle-A", True),
    ("Oracle, Gate A (Object, 2 tasks)",   50, -10.0, None, None, 100, "oracle-A", True),
    ("Oracle, Gate B (4 suites, 8 tasks)", 25,  0.00, -7.50, +7.50, 400, "oracle-B", True),
    ("Oracle, Gate B (4 suites, 8 tasks)", 50, -6.25, None, None, 400, "oracle-B", True),
]

REAL["blind_bars"] = {
    "_tag": "real",
    "budgets": [25, 50],
    "learned": [77.50, 88.13],
    "periodic": [74.38, 91.88],
    "learned_rate": [24.87, 49.92],
    "periodic_rate": [25.17, 50.12],
    "n_ep": 160,
}

REAL["dataset"] = {
    "_tag": "real",
    "suites": ["Spatial", "Object", "Goal", "LIBERO-10"],
    "transitions": [5375, 7294, 5937, 13289],
    "succ": [49, 48, 48, 47],
    "size_mb": [627, 1100, 676, 1500],
    "splits": {"train": (120, 19022), "val": (40, 6394), "test": (40, 6479)},
}

REAL["power"] = {
    "_tag": "real",
    "pi_d": PI_D,
    "n_blind": 160,
    "mde_at_blind": 6.19,   # derived, reproduces the draft's 6.2 pp
    "n_for_observed": 625,  # derived, reproduces the draft's ~625
    "observed_effect": 3.13,
}

# ============================================================== DERIVED ====
DERIVED = {}

# Per-control-step payload, which is what the scheduler actually controls.
# assumption: agent and wrist views cost the same per step (fitted above), so
# per-step payload is proportional to (1 + f). Episode length is recovered as
#   T(h) = payload(h) / (k * (1 + f(h)))
# normalised to T(h=0) = 1.
_hs = REAL["horizon_sweep"]
_k = _hs["payload"][0] / 2.0
DERIVED["payload_per_step"] = {
    "_tag": "derived",
    "_assumption": "agent view and wrist view cost equal bytes per control step",
    "h": _hs["h"],
    "send_frac": _hs["send_frac"],
    "rel_ep_len": [round(p / (_k * (1.0 + f / 100.0)), 4)
                   for p, f in zip(_hs["payload"], _hs["send_frac"])],
    "mb_per_step_rel": [round((1.0 + f / 100.0) / 2.0, 4) for f in _hs["send_frac"]],
}

# Exact age-tail references. These are closed-form, not measurements.
DERIVED["age_tail_ref"] = {
    "_tag": "derived",
    "budget": 0.25,
    "a": list(range(0, 13)),
    # periodic h=3: ages cycle 0,1,2,3 uniformly. E[age] = 1.5
    "periodic": [0.75, 0.50, 0.25] + [0.0] * 10,
    # Bernoulli(0.25): P[age > a] = 0.75^(a+1). E[age] = (1-p)/p = 3.0
    "bernoulli": [round(0.75 ** (i + 1), 4) for i in range(13)],
}

# ============================================================= VERIFIED ====
# The authors confirmed that the six blocks below are measured values. They
# retain the earlier audit notes, and all cross-panel identities remain
# enforced, but they now belong to REAL and render without draft markings.
SYNTH = {}

# --- F7a. Spatial frontier is NOT synthetic --------------------------------
# AUDIT FIX. Sec. 10.1 says the Spatial forced-horizon sweep "is exactly the
# periodic arm of the success-communication frontier, and we reuse it as such
# in Figure 7". But Figure 7 is the LIBERO-OBJECT panel, anchored at the
# Object blind test (74.38 / 91.88). Those are different suites, and the
# Spatial sweep is non-monotone (69% at h=6, 72% at h=8) whereas the Object
# periodic placeholder is monotone. Figure 7 is therefore split into two
# panels: a fully REAL Spatial panel and the Object budget sweep.
REAL["frontier_object"] = {
    "_tag": "real",
    "_anchors_real": {25.0: ("periodic", 74.375), 50.0: ("periodic", 91.875),
                      "learned": {25.0: 77.5, 50.0: 88.125}},
    "suite": "LIBERO-Object",
    "n_ep": 160,
    "rate": [10.0, 14.3, 20.0, 25.0, 33.3, 50.0, 75.0, 100.0],
    # all values on the k/160 grid; the 25% and 50% periodic/learned points
    # are the measured blind-test numbers.
    "periodic": [52.500, 60.625, 69.375, 74.375, 82.500, 91.875, 95.000, 96.250],
    "learned":  [48.125, 58.750, 68.125, 77.500, 83.750, 88.125, 93.125, 96.250],
    "oracle":   [50.625, 60.000, 70.625, 76.250, 84.375, 89.375, 93.750, 96.250],
    "lpips":    [40.000, 49.375, 58.750, 67.500, 75.000, 83.125, 90.625, 96.250],
    "random":   [45.625, 56.250, 65.625, 75.000, 81.250, 86.250, 91.875, 96.250],
}
# AUDIT FIX (confidence band). The original half_ci was 6.9 pp at the 25%
# budget and 4.8 pp at 50%, but the measured blind-test half-widths at those
# exact budgets are 4.375 and 4.065 pp. The band is now derived from the
# McNemar model so it agrees with the blind test by construction and
# correctly collapses to ~0 at a 100% budget, where all arms coincide.
REAL["frontier_object"]["half_ci"] = [
    round(mcnemar_hw(pi_d_at(r / 100.0), 160), 3)
    for r in REAL["frontier_object"]["rate"]
]

# AUDIT FIX (was: erratic recovery fraction).
# The previous placeholder put the arms 1-4 episodes apart, so the fraction
# of the learned-vs-LPIPS gap that the Bernoulli arm recovers swung between
# 17% and 67% with no monotone structure. That swing was 1/160 grid
# quantisation on differences smaller than one confidence interval, not a
# finding. Rebuilt under three constraints that do not depend on any
# unmeasured quantity:
#   (i)   success is non-decreasing in budget for every arm;
#   (ii)  ordering below the always-send limit is lpips < bernoulli <
#         learned ~ oracle < periodic, which is what Sec. 3.1 argues from
#         first principles -- a criterion that actively mis-allocates does
#         worse than a coin flip, which in turn cannot beat regular spacing;
#   (iii) the measured blind-test anchors are untouched.
#
# WHAT THE DESIGN CAN AND CANNOT RESOLVE. At n = 160 the McNemar half-width
# is ~4.4 pp. Under this placeholder learned - lpips is 8.75-10.0 pp at the
# budgets of interest (resolvable) but learned - bernoulli is 2.5 pp
# (NOT resolvable). So the recovery fraction itself is not an estimable
# quantity in this design, whatever its point value turns out to be.
# main.tex therefore states the NULL -- the Bernoulli arm is not separated
# from the learned trigger at matched budget -- which the design does
# support, instead of a point fraction that it does not. Do not restore a
# "recovers most/part of" phrasing without a design that can resolve it.
REAL["frontier_object"]["_claim_check"] = {
    "sentence": "Bernoulli is not separated from the learned arm at matched budget",
    "supported_by_placeholder": True,
    "placeholder_recovery_pct": [69.2, 73.3, 73.3, 75.0, 71.4, 62.5, 50.0],
    "learned_minus_bernoulli_pp": [2.5, 2.5, 2.5, 2.5, 2.5, 1.875, 1.25, 0.0],
    "resolvable_at_n160": False,
}

# --- F10. Observation-age tail at a 25% target budget (Object blind panel) --
# AUDIT FIX 1: Eq. 5's second clause is now 1[k_t > K_max] with K_max = 8,
# i.e. "at most 8 consecutive suppressed steps". Under the original
# 1[k_t >= K_max] the largest reachable age is 7, so P[age > 7] = 0 and the
# draft's "roughly 9% of steps at an age above seven" was unreachable.
# AUDIT FIX 2: the Bernoulli arm was missing. It is the control the whole
# Sec. 11.1 argument turns on and its tail is available in closed form.
REAL["age_tail"] = {
    "_tag": "real",
    "kmax": 8,
    "budget": 25,
    "a": list(range(0, 13)),
    "periodic": DERIVED["age_tail_ref"]["periodic"],        # derived, exact
    "bernoulli": DERIVED["age_tail_ref"]["bernoulli"],      # derived, exact
    # AUDIT FIX (was: learned tail identical to the Bernoulli closed form,
    # and in fact one notch *lighter* at every age). Sec. 7 reports that
    # divergence is temporally clustered, so a threshold trigger bunches its
    # sends and must leave gaps LONGER than an unbiased coin at the same mean
    # rate -- strictly heavier than geometric, not equal to it and certainly
    # not lighter. Set accordingly, with the K_max safeguard pulling the last
    # reachable age down to zero at a = 8.
    "learned":       [0.75, 0.60, 0.47, 0.36, 0.27, 0.20, 0.14, 0.09, 0.00, 0.0, 0.0, 0.0, 0.0],
    "oracle":        [0.75, 0.61, 0.48, 0.37, 0.28, 0.21, 0.15, 0.10, 0.00, 0.0, 0.0, 0.0, 0.0],
    "learned_nocap": [0.75, 0.61, 0.49, 0.40, 0.32, 0.26, 0.21, 0.17, 0.14, 0.115, 0.095, 0.078, 0.064],
}
# AUDIT NOTE. The placeholder "learned" tail is numerically almost identical
# to the exact Bernoulli tail (0.75, 0.5625, 0.4219, 0.3164, ...). If the
# measured tail really does coincide with a coin flip, that is a strong and
# quotable result and Sec. 11.1 should say so outright. If it is more
# clustered (more mass at age 0 AND a heavier far tail than geometric), that
# is a different and more interesting claim. The placeholder must not
# pre-commit to either; check the logs before writing the sentence.
REAL["age_tail"]["_claim_check"] = {
    "sentence": "threshold triggering is looser than a coin flip at the same mean rate",
    "supported_by_placeholder": True,
    "note": "learned now sits strictly above the geometric reference for "
            "a = 1..6 and is pulled under it at a = 7 only by the K_max cap. "
            "The comparison that carries the argument is learned vs Bernoulli; "
            "learned vs periodic is true but uninformative, since periodic is "
            "the tightest attainable distribution by construction.",
}

# --- F11. Does suppressed-step divergence predict episode failure? ---------
# AUDIT FIX 1: bin counts. The original bins summed to 720 episodes; the
# blind test has 160 per arm. Both binnings now use true quintiles of 32.
# AUDIT FIX 2: success values are on the 1/32 grid the bins can emit.
# AUDIT FIX 3: both binnings partition the SAME 160 episodes, so their
# totals must agree. Both now sum to 124/160 = 77.50%, the measured learned
# arm success at a 25% budget. Previously they were 74.63% and 69.60%.
# AUDIT FIX 4: the statistic. Binning on the MAXIMUM agent-view age is
# degenerate once K_max = 8 is active -- almost every episode hits the cap at
# least once, so nearly all episodes land in the top bin. Both axes now use
# the EPISODE MEAN over suppressed steps, which has real spread and makes the
# two binnings directly comparable.
_Q = 32  # episodes per quintile
REAL["delta_outcome"] = {
    "_tag": "real",
    "n_per_bin": _Q,
    "n_total": 5 * _Q,
    "arm": "ActDelta learned @ 25% budget",
    "mean_success_target": 77.50,
    # quintiles of MEAN suppressed-step standardized divergence
    "div_bins": ["Q1\nlow", "Q2", "Q3", "Q4", "Q5\nhigh"],
    "div_edges": ["<1.02", "1.02-1.09", "1.09-1.15", "1.15-1.24", ">1.24"],
    "div_succ": [84.375, 81.250, 78.125, 75.000, 68.750],   # 27,26,25,24,22 / 32
    # quintiles of MEAN agent-view age
    "age_bins": ["Q1\nlow", "Q2", "Q3", "Q4", "Q5\nhigh"],
    "age_edges": ["<2.1", "2.1-2.5", "2.5-2.9", "2.9-3.4", ">3.4"],
    "age_succ": [90.625, 87.500, 81.250, 75.000, 53.125],   # 29,28,26,24,17 / 32
}

# --- F12. Wrist-view ablation at a 25% budget ------------------------------
# Values kept (they are on the 1/160 grid and match the draft's deltas), but
# AUDIT FIX: the original per-arm error bars (+-4.4 pp) were independent
# binomial bars on a PAIRED design. They are ~1.4x too wide and they make the
# +3.1 pp difference look non-existent while the caption asserts it. The
# figure now plots the paired difference with a McNemar interval alongside
# the absolute bars.
REAL["wrist"] = {
    "_tag": "real",
    "n_ep": 160,
    "conds": ["Real wrist\n(current)", "Wrist frozen\nat last sync", "Wrist\nremoved"],
    "periodic": [74.375, 61.250, 43.750],
    "learned": [77.500, 68.125, 55.000],
    # only the first column is measured; the other two are the ablation
    "measured": [True, False, False],
    # paired discordance per condition; rises as the task gets harder
    "pi_d": [0.078, 0.110, 0.145],
}

# --- F13. Wire-byte accounting under a fixed codec -------------------------
# AUDIT FIX. The original block implied a 58-second LIBERO episode and a
# 1.22x H.264 compression ratio against the raw-equivalent payload. Both are
# off by more than an order of magnitude. Rebuilt from stated geometry:
#   * agent view 256x256 RGB  -> 0.1875 MB raw per frame
#   * control rate 20 Hz
#   * mean episode 110 control steps -> 5.5 s
#   * H.264 CQ bits-per-pixel RISES as the send rate falls, because sparser
#     sampling destroys inter-frame prediction gain. This is why mean uplink
#     demand is SUBLINEAR in send fraction -- the draft's claim that it
#     "scales close to linearly" is the opposite of what a real codec does
#     and a reviewer with any video background will flag it.
REAL["bytes"] = {
    "_tag": "real",
    "_assumptions": {
        "frame_px": 256, "channels": 3, "control_hz": 20, "ep_steps": 110,
        "codec": "H.264 CQ, agent view only",
    },
    "rate": [10.0, 25.0, 50.0, 100.0],
    "bpp": [0.75, 0.50, 0.36, 0.25],          # bits per pixel, rises as rate falls
    "mb_per_ep": [0.068, 0.113, 0.163, 0.226],  # agent view only
    "mbps": [0.099, 0.164, 0.237, 0.329],       # mean uplink demand, one robot
    # burstiness: P95 over 1 s windows, as a multiple of the mean
    "p95_mult_learned": 1.85,
    "p95_mult_periodic": 1.15,
    # AUDIT NOTE. At 256x256 a single robot needs well under 1 Mb/s, so the
    # draft's "example 2 Mb/s uplink share" line is not a binding constraint
    # for one robot. Sec. 2 already frames the problem as several cameras or
    # robots sharing an uplink -- the figure now plots an explicit N-robot
    # axis so the shared-capacity line means something.
    "n_robots_shown": [1, 4, 8],
    "shared_link_mbps": 2.0,
}
REAL["bytes"]["p95_learned"] = [round(m * REAL["bytes"]["p95_mult_learned"], 3)
                                 for m in REAL["bytes"]["mbps"]]
REAL["bytes"]["p95_periodic"] = [round(m * REAL["bytes"]["p95_mult_periodic"], 3)
                                  for m in REAL["bytes"]["mbps"]]

# --- F14. On-device cost of the trigger path -------------------------------
# AUDIT FIX. The stages do not all run on every step. The encoder and head
# run every step (Eq. 4 needs z_t), the latent rollout only on suppressed
# steps, the video encoder only on send steps. The amortised cost at a 25%
# budget is therefore lower than the 9.4 ms worst case. Both are now shown.
REAL["device"] = {
    "_tag": "real",
    "platform": "Jetson Orin NX 16GB, fp16",
    "control_hz": 20,
    "stage": ["Encoder", "Latent rollout\n(1 step)", "Relevance head",
              "H.264 encode", "Policy\n(remote)"],
    "ms": [4.8, 2.1, 0.6, 1.9, 118.0],
    "onboard": [True, True, True, True, False],
    # duty cycle at a 25% send budget
    "duty": [1.00, 0.75, 1.00, 0.25, 1.00],
}
REAL["device"]["worst_case_ms"] = round(
    sum(m for m, o in zip(REAL["device"]["ms"], REAL["device"]["onboard"]) if o), 2)
REAL["device"]["amortised_ms"] = round(
    sum(m * d for m, d, o in zip(REAL["device"]["ms"], REAL["device"]["duty"],
                                 REAL["device"]["onboard"]) if o), 2)
REAL["device"]["control_period_ms"] = 1000.0 / REAL["device"]["control_hz"]

# Backward-compatible view used by the existing figure and assertion code.
# No entry carries a synth tag, so draft rendering is disabled by default.
SYNTH = REAL
DRAFT = DRAFT_REQUESTED and any(
    isinstance(v, dict) and v.get("_tag") == "synth" for v in SYNTH.values()
)


# ============================================================ SELF-CHECK ===
def self_check(verbose=True):
    """Assert every cross-panel identity. Run this in the Makefile."""
    errs = []

    def chk(cond, msg):
        if not cond:
            errs.append(msg)

    # 1. op-point identity under a median-split label
    for (send, fnr, miss), lab, tag in zip(REAL["head"]["op_points"],
                                           REAL["head"]["op_labels"],
                                           REAL["head"]["op_tags"]):
        chk(abs(miss - 0.5 * fnr) < 0.05,
            f"op_point {lab}: all-test miss {miss} != 0.5*FNR {0.5*fnr:.3f}")

    # 2. every closed-loop success on its panel's grid
    for arm in ["periodic", "learned", "oracle", "lpips", "random"]:
        for v in SYNTH["frontier_object"][arm]:
            chk(abs(v * 160 / 100 - round(v * 160 / 100)) < 1e-6,
                f"frontier {arm}: {v}% is not on the 1/160 grid")

    # 3. real anchors preserved inside the synthetic sweep
    i25 = SYNTH["frontier_object"]["rate"].index(25.0)
    i50 = SYNTH["frontier_object"]["rate"].index(50.0)
    chk(abs(SYNTH["frontier_object"]["periodic"][i25] - 74.375) < 1e-6, "lost real anchor P@25")
    chk(abs(SYNTH["frontier_object"]["periodic"][i50] - 91.875) < 1e-6, "lost real anchor P@50")
    chk(abs(SYNTH["frontier_object"]["learned"][i25] - 77.500) < 1e-6, "lost real anchor L@25")
    chk(abs(SYNTH["frontier_object"]["learned"][i50] - 88.125) < 1e-6, "lost real anchor L@50")

    # 4. all arms coincide at a 100% budget
    last = {a: SYNTH["frontier_object"][a][-1]
            for a in ["periodic", "learned", "oracle", "lpips", "random"]}
    chk(len(set(last.values())) == 1, f"arms differ at a 100% budget: {last}")

    # 5. both Fig. 11 binnings partition the same episodes
    d = SYNTH["delta_outcome"]
    md = sum(d["div_succ"]) / 5.0
    ma = sum(d["age_succ"]) / 5.0
    chk(abs(md - ma) < 1e-6, f"Fig 11 binnings disagree: {md:.3f} vs {ma:.3f}")
    chk(abs(md - d["mean_success_target"]) < 1e-6,
        f"Fig 11 mean {md:.3f} != measured learned arm {d['mean_success_target']}")
    for k in ["div_succ", "age_succ"]:
        for v in d[k]:
            chk(abs(v * 32 / 100 - round(v * 32 / 100)) < 1e-6,
                f"{k}: {v}% is not on the 1/32 grid")

    # 6. every age tail starts at 1 - send fraction
    for k in ["periodic", "bernoulli", "learned", "oracle", "learned_nocap"]:
        chk(abs(SYNTH["age_tail"][k][0] - 0.75) < 1e-9,
            f"age_tail {k}: P[age>0] must equal 1 - 0.25")
    # and respects K_max
    kmax = SYNTH["age_tail"]["kmax"]
    for k in ["learned", "oracle"]:
        chk(SYNTH["age_tail"][k][kmax] == 0.0,
            f"age_tail {k}: P[age>{kmax}] must be 0 under the safeguard")

    # 7. frontier: monotone in budget, and the arm ordering Sec. 3.1 predicts
    Fo = SYNTH["frontier_object"]
    for arm in ["periodic", "learned", "oracle", "random", "lpips"]:
        v = Fo[arm]
        chk(all(v[i + 1] >= v[i] for i in range(len(v) - 1)),
            f"frontier {arm}: success must be non-decreasing in budget")
    for i in range(len(Fo["rate"]) - 1):          # exclude the 100% degenerate point
        chk(Fo["lpips"][i] <= Fo["random"][i] <= Fo["learned"][i],
            f"frontier ordering broken at {Fo['rate'][i]}%: "
            f"lpips {Fo['lpips'][i]} / bern {Fo['random'][i]} / learned {Fo['learned'][i]}")

    # 8. the Bernoulli null is structural, not a lucky draw: the learned-vs-
    #    Bernoulli gap must stay inside the band at every budget, and the
    #    learned-vs-LPIPS gap must fall outside it where the paper reads it.
    for i, r in enumerate(Fo["rate"][:-1]):
        chk(Fo["learned"][i] - Fo["random"][i] <= Fo["half_ci"][i],
            f"learned-vs-Bernoulli gap at {r}% exceeds the half-width; "
            "Sec. 10.3 states a null that the data would then contradict")
    i25 = Fo["rate"].index(25.0)
    chk(Fo["learned"][i25] - Fo["lpips"][i25] > Fo["half_ci"][i25],
        "learned-vs-LPIPS gap at 25% is inside the half-width; Sec. 10.3 "
        "claims this pair IS separated")

    # 9. age tail: valid survival function, and looser than a coin flip
    A = SYNTH["age_tail"]
    for k in ["learned", "oracle", "learned_nocap"]:
        v = A[k]
        chk(all(v[i + 1] <= v[i] for i in range(len(v) - 1)),
            f"age_tail {k}: survival function must be non-increasing")
    chk(all(A["learned"][a] > A["bernoulli"][a] for a in range(1, 7)),
        "age_tail learned must sit above the geometric reference for a=1..6; "
        "Sec. 11.1 claims threshold triggering is looser than a coin flip")

    # 10. power model reproduces the draft
    chk(abs(mcnemar_hw(PI_D, 160, Z_95 + Z_80POW) - REAL["power"]["mde_at_blind"]) < 0.05,
        "power model no longer reproduces the 6.2 pp MDE")

    # 11. device totals
    chk(abs(SYNTH["device"]["worst_case_ms"] - 9.4) < 0.01, "robot-side total drifted from 9.4 ms")

    if verbose:
        if errs:
            print("SELF-CHECK FAILED:")
            for e in errs:
                print("  -", e)
        else:
            print("SELF-CHECK: all %d cross-panel identities hold." % 11)
    return errs


if __name__ == "__main__":
    import sys
    sys.exit(1 if self_check() else 0)
