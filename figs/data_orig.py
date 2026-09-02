"""
ActDelta figure data.

EVERY entry is tagged:
    "real"  -> number taken verbatim from the current draft / logs
    "synth" -> PLACEHOLDER produced for layout purposes only.
               Replace with measured values before submission.

Keep this file as the single source of truth; make_figs.py never hardcodes numbers.
"""

# ----------------------------------------------------------------- REAL ----
REAL = {}

# Sec. 10.1 LIBERO-Spatial forced-horizon sweep.
# send fraction of a periodic scheduler with imagined horizon h is 1/(h+1).
REAL["horizon_sweep"] = {
    "h":        [0, 1, 2, 4, 6, 8, 10, 12],
    "succ":     [98, 94, 84, 70, 69, 72, 65, 62],
    "ci_lo":    [94, 85, 72, 54, 53, 56, 49, 45],
    "ci_hi":    [100, 100, 94, 86, 84, 86, 80, 79],
    "payload":  [32.72, 28.67, 27.75, 27.70, 27.08, 26.31, 26.43, 26.75],  # MB/episode
    "send_frac": [100.0, 50.0, 33.33, 20.0, 14.29, 11.11, 9.09, 7.69],
}

# Sec. 7 fidelity vs action divergence (formal test split, 1400 pairs)
REAL["fidelity"] = {
    "names":        ["Pixel RMS", "SSIM err.", "LPIPS", "WM latent"],
    "pooled":       [-0.0282, -0.0736, -0.1165, -0.0744],
    "episode_med":  [0.0742, 0.0756, 0.1595, 0.0377],
    "disagree":     [48.86, 50.79, 53.93, 49.93],
    "head_pooled":  0.6839,
    "head_ci":      [0.6365, 0.7257],
    "head_ep_med":  0.6340,
}

# Sec. 8 head quality
REAL["head"] = {
    "auroc": 0.8332, "auprc": 0.8326, "mae": 0.2052,
    "suites":       ["LIBERO-10", "Goal", "Object", "Spatial"],
    "suite_rho":    [0.507, 0.664, 0.683, 0.724],
    "suite_fnr95":  [8.40, 3.81, 4.24, 1.51],
    "horizons":     [1, 2, 3, 4, 5, 8, 12],
    "horizon_rho":  [0.619, 0.701, 0.701, 0.718, 0.604, 0.721, 0.710],
    "err_q":        {"Median": 0.158, "P95": 0.539, "P99": 0.786, "P99.9": 1.170, "Max": 1.82},
    # operating points: (send fraction %, conditional FNR %, all-test miss %)
    "op_points":    [(50.00, 47.9, 10.86), (82.43, 4.04, 2.00), (94.21, 0.43, 0.20)],
    "op_labels":    ["median-rate", "95% recall", "99% recall"],
    "div_quant":    {"Q25": 0.814, "Median": 1.076, "Q75": 1.268, "P95": 1.713, "Max": 3.455},
}

# Sec. 5 world-model selection (four-suite base)
REAL["wm"] = {
    "h":       [1, 5, 8, 12],
    "baseline": [0.002124, 0.016618, 0.028354, 0.043681],
    "adopted":  [0.002022, 0.014418, 0.023435, 0.034013],
}

# Sec. 10.2 / 10.3 closed-loop effects (pp vs rate-matched periodic)
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
    "budgets": [25, 50],
    "learned": [77.50, 88.13],
    "periodic": [74.38, 91.88],
    "learned_rate": [24.87, 49.92],
    "periodic_rate": [25.17, 50.12],
}

REAL["dataset"] = {
    "suites": ["Spatial", "Object", "Goal", "LIBERO-10"],
    "transitions": [5375, 7294, 5937, 13289],
    "succ": [49, 48, 48, 47],
}

# ------------------------------------------------------------- SYNTHETIC ---
# Everything below is a PLACEHOLDER. Shapes are chosen to be consistent with
# the measured anchor points above so that swapping in real logs will not
# change the layout.
SYNTH = {}

# F1. Success-communication frontier, LIBERO-Object blind panel.
# periodic anchors at 25% (74.38) and 50% (91.88) are REAL; the rest of the
# curve and all non-periodic arms are synthetic.
SYNTH["frontier"] = {
    "rate":     [10.0, 14.3, 20.0, 25.0, 33.3, 50.0, 75.0, 100.0],
    "periodic": [52.5, 60.6, 69.4, 74.38, 82.5, 91.88, 95.0, 96.3],
    "learned":  [48.1, 58.8, 68.1, 77.50, 83.8, 88.13, 93.1, 96.3],
    "oracle":   [50.6, 60.0, 70.6, 76.25, 84.4, 89.38, 93.8, 96.3],
    "lpips":    [41.9, 50.0, 60.6, 66.25, 76.9, 86.25, 91.9, 96.3],
    "random":   [45.0, 53.1, 63.1, 68.75, 78.1, 87.50, 92.5, 96.3],
    "half_ci":  [6.5, 6.6, 6.8, 6.9, 6.4, 4.8, 3.6, 2.9],
}

# F5. Observation-age tail at a 25% target budget (Object blind panel).
# ages in control steps; P(age > a).
SYNTH["age_tail"] = {
    "a":        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "periodic": [0.75, 0.50, 0.25, 0.00, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "learned":  [0.75, 0.56, 0.42, 0.31, 0.23, 0.17, 0.12, 0.09, 0.00, 0.0, 0.0, 0.0, 0.0],
    "oracle":   [0.75, 0.57, 0.44, 0.33, 0.25, 0.19, 0.14, 0.10, 0.00, 0.0, 0.0, 0.0, 0.0],
    "learned_nocap": [0.75, 0.57, 0.44, 0.34, 0.27, 0.21, 0.17, 0.13, 0.10, 0.08, 0.06, 0.05, 0.04],
    "kmax": 8,
}

# F7. Wrist-view ablation at 25% budget: does the wrist view mask the cost of
# suppressing the agent view?
SYNTH["wrist"] = {
    "conds":    ["Real wrist\n(current)", "Wrist frozen\nat last sync", "Wrist\nremoved"],
    "periodic": [74.38, 61.25, 43.75],
    "learned":  [77.50, 68.13, 55.00],
    "err":      [4.4, 5.1, 5.6],
    "err2":     [4.4, 5.0, 5.5],
}

# F8. Does instantaneous divergence at a suppressed step predict episode failure?
# bins of max suppressed-step standardized delta vs empirical episode success.
SYNTH["delta_outcome"] = {
    "bins":   ["<0.8", "0.8-1.1", "1.1-1.3", "1.3-1.7", ">1.7"],
    "succ":   [79.0, 77.5, 74.0, 72.5, 68.0],
    "err":    [5.5, 5.0, 5.2, 5.6, 7.0],
    "n":      [128, 176, 168, 152, 96],
    # contrast: age-based binning separates outcomes much more sharply
    "age_bins": ["1-2", "3-4", "5-6", "7-8", ">8"],
    "age_succ": [86.0, 80.5, 71.0, 62.5, 48.0],
    "age_err":  [4.2, 4.6, 5.4, 6.2, 8.5],
}

# F9. Wire-byte accounting under a fixed codec (H.264 CQ, 256x256 agent view).
SYNTH["bytes"] = {
    "rate":       [10.0, 25.0, 50.0, 100.0],
    "kb_per_ep":  [3.1, 7.4, 14.1, 26.8],       # MB/episode, agent view only
    "mbps":       [0.42, 1.02, 1.94, 3.68],     # mean uplink demand
    "p95_mbps":   [1.30, 2.55, 4.10, 6.20],     # burstiness matters for scheduling
    "p95_mbps_periodic": [0.75, 1.55, 2.60, 4.30],
}

# F10. On-device cost of the trigger path (Jetson Orin NX 16GB, fp16).
SYNTH["device"] = {
    "stage":  ["Encoder", "Latent rollout\n(1 step)", "Relevance head", "H.264 encode", "Policy\n(remote)"],
    "ms":     [4.8, 2.1, 0.6, 1.9, 118.0],
    "onboard": [True, True, True, True, False],
}
