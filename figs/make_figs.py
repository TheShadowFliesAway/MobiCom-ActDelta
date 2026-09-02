#!/usr/bin/env python3
"""Generate every data figure for the ActDelta paper.

Nothing here hardcodes a measurement; every number is read from data.py.
Panels whose data is still a placeholder are stamped (see style.stamp_synthetic)
so a placeholder can never silently reach a submission.

    python3 make_figs.py [outdir]
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator

import style as S
from style import C, M, LS, LABEL
from data import REAL, DERIVED, SYNTH, DRAFT, mcnemar_hw, n_for_effect, Z_95, Z_80POW, PI_D, self_check

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, n)

pct = FuncFormatter(lambda v, _: f"{v:g}")


def maybe_stamp(ax, tag):
    if DRAFT and tag == "synth":
        S.stamp_synthetic(ax)


# =========================================================== Fig 3: WM sel ==
def fig_wm():
    d = REAL["wm"]
    h = np.array(d["h"], float)
    b, a = np.array(d["baseline"]) * 1e2, np.array(d["adopted"]) * 1e2
    fig, ax = plt.subplots(figsize=S.figsize("col", 1.72))
    S.grid(ax)

    ax.fill_between(h, a, b, color=C["learned"], alpha=0.10, lw=0, zorder=1)
    ax.plot(h, b, ls=(0, (5, 1.6)), marker="s", mfc="white", color=C["baseline"],
            label="Baseline (joint image obj.)", zorder=3)
    ax.plot(h, a, ls="-", marker="o", color=C["adopted"],
            label="Adopted (rollout only)", zorder=4)

    for hh, bb, aa in zip(h, b, a):
        imp = (bb - aa) / bb * 100
        ax.annotate(f"$-${imp:.0f}%", xy=(hh, (aa + bb) / 2),
                    xytext=(0, 6.5), textcoords="offset points",
                    fontsize=S.BASE, color=C["learned"],
                    ha="center", va="bottom")

    ax.set_xlabel(r"Rollout horizon $h$", fontsize=7.8)
    ax.set_ylabel(r"Latent rollout MSE ($\times 10^{-2}$)", fontsize=7.8)
    ax.tick_params(axis="both", labelsize=7.4)
    ax.set_xticks(d["h"])
    ax.set_xlim(0.3, 13.4)
    ax.set_ylim(0, 5.2)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, 1.06), fontsize=7.2)

    st, zt = d["shuffled_true"], d["zero_true"]
    S.note(ax, 12.9, 0.62,
           "action dependence at $h{=}12$\n"
           f"shuffled/true {st[0]:.3f}$\\to${st[1]:.3f}\n"
           f"zero/true {zt[0]:.3f}$\\to${zt[1]:.3f}",
           size=6.8, ha="right", va="bottom")
    S.save(fig, P("fig3_wm_selection.pdf"))


# ==================================================== Fig 4: fidelity forest =
def fig_fidelity():
    d = REAL["fidelity"]
    names = d["names"] + ["Latent head $\\Phi$"]
    pooled = d["pooled"] + [d["head_pooled"]]
    epmed = d["episode_med"] + [d["head_ep_med"]]
    dis = d["disagree"] + [None]

    fig, ax = plt.subplots(figsize=S.figsize("col", 1.95))
    y = np.arange(len(names))[::-1]

    ax.axvspan(-0.20, 0.20, color="#F0F0F0", lw=0, zorder=0)
    ax.axvline(0, color=C["rule"], lw=0.6, zorder=1)

    for yi, p, e, nm in zip(y, pooled, epmed, names):
        head = nm.startswith("Latent")
        col = C["learned"] if head else C["muted"]
        ax.plot([p, e], [yi, yi], color=col, lw=0.8, alpha=0.75, zorder=2)
        ax.plot(p, yi, "o", color=col, ms=3.6, zorder=4)
        ax.plot(e, yi, "o", mfc="white", mec=col, mew=0.9, ms=3.6, zorder=4)

    lo, hi = d["head_ci"]
    ax.plot([lo, hi], [y[-1], y[-1]], color=C["learned"], lw=2.2, alpha=0.30,
            solid_capstyle="butt", zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlim(-0.24, 0.86)
    ax.set_ylim(-0.9, len(names) - 0.35)
    ax.set_xlabel(r"Spearman $\rho_s$ with action divergence $\delta_t$")
    ax.tick_params(axis="y", length=0)
    S.grid(ax, axis="x")

    S.note(ax, 0.0, len(names) - 0.72, "band of no usable ranking",
           size=S.BASE - 1.4, ha="center", style="italic")

    ax.text(0.895, 1.055, "high/low\ndisagree.", transform=ax.transAxes,
            fontsize=S.BASE - 1.5, ha="center", va="bottom", color=C["muted"])
    for yi, v in zip(y, dis):
        if v is not None:
            ax.text(0.94, (yi + 0.9) / (len(names) + 0.55), f"{v:.1f}%",
                    transform=ax.transAxes, fontsize=S.BASE - 1.3,
                    ha="center", va="center", color="#3A3A3A")

    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], ls="", marker="o", color=C["muted"], ms=3.6,
                              label="pooled"),
                       Line2D([], [], ls="", marker="o", mfc="white", mec=C["muted"],
                              ms=3.6, label="per-episode median")],
              loc="upper left", bbox_to_anchor=(0.34, 1.00), ncol=1)
    S.save(fig, P("fig4_fidelity_forest.pdf"))


# ====================================================== Fig 5: head strata ==
def fig_head_strata():
    d = REAL["head"]
    f = REAL["fidelity"]
    fig, ax = plt.subplots(figsize=S.figsize("col", 1.72))
    S.grid(ax)

    ns = len(d["suites"])
    xs = np.arange(ns)
    xh = np.arange(ns + 1, ns + 1 + len(d["horizons"]))

    band = max(max(f["episode_med"]), max(f["pooled"]))
    ax.axhspan(min(f["pooled"]), band, color="#EDEDED", lw=0, zorder=0)

    ax.bar(xs, d["suite_rho"], width=0.66, color=C["learned"], lw=0, zorder=3)
    ax.plot(xh, d["horizon_rho"], "-", marker="o", ms=2.8, color=C["oracle"],
            mfc="white", mew=0.8, zorder=4)

    pooled = f["head_pooled"]
    ax.axhline(pooled, color="#333333", lw=0.6, ls=(0, (3, 1.6)), zorder=2)
    S.note(ax, -0.55, pooled + 0.035, f"pooled {pooled:.2f}", size=S.BASE - 1.3,
           color="#333333")

    ax.axvline(ns + 0.0, color=C["rule"], lw=0.5)
    ax.set_xticks(list(xs) + list(xh))
    ax.set_xticklabels(["L-10", "Goal", "Obj.", "Spat."] + [str(h) for h in d["horizons"]])
    ax.set_ylabel(r"Head Spearman $\rho_s$")
    ax.set_ylim(0, 0.86)
    ax.set_xlim(-0.75, ns + len(d["horizons"]) + 0.4)

    S.note(ax, (ns - 1) / 2, 0.80, "by suite", size=S.BASE - 1.2, ha="center",
           color=C["learned"])
    S.note(ax, xh.mean(), 0.80, r"by horizon $h$", size=S.BASE - 1.2, ha="center",
           color=C["oracle"])
    S.note(ax, ax.get_xlim()[1] - 0.15, 0.055, "range of all four fidelity metrics",
           size=S.BASE - 1.5, ha="right", style="italic")
    S.note(ax, 0, d["suite_rho"][0] + 0.028, "weakest", size=S.BASE - 1.6,
           ha="center", color=C["hi"])
    S.save(fig, P("fig5_head_strata.pdf"))


# =================================================== Fig 6: operating point ==
def fig_operating():
    d = REAL["head"]
    ops = d["op_points"]
    x = [p[0] for p in ops]
    y = [p[2] for p in ops]
    fnr = [p[1] for p in ops]

    fig, ax = plt.subplots(figsize=S.figsize("col", 1.78))
    S.grid(ax)

    ax.axvspan(20, 55, color="#EAF0F7", lw=0, zorder=0)
    S.note(ax, 22.0, 1.0, "budgets at which the\nclosed loop is run",
           size=6.8, color=C["learned"], va="bottom")

    xs = np.linspace(x[0], 100, 200)
    ys = np.interp(xs, x + [100.0], y + [0.0])
    ax.plot(xs, ys, "-", color=C["learned"], lw=1.1, zorder=3)
    ax.plot(x, y, "o", color=C["learned"], ms=3.4, zorder=4)

    # Keep labels in whitespace above the curve; leaders preserve the exact
    # point association without covering the data line.
    place = {0: (54.0, 15.5, "left"),
             1: (69.0, 11.2, "left"),
             2: (98.0, 7.0, "right")}
    for i, (xi, yi, lab, fn) in enumerate(zip(x, y, d["op_labels"], fnr)):
        tx, ty, ha = place[i]
        ax.annotate(f"{lab}\n({fn:.1f}% cond. FNR)", xy=(xi, yi),
                    xytext=(tx, ty), textcoords="data", ha=ha,
                    va="bottom", fontsize=6.9, color="#3A3A3A",
                    arrowprops=dict(arrowstyle="-", lw=0.45,
                                    color="#777777", shrinkA=1, shrinkB=2))

    ax.axvline(25, color=C["hi"], lw=0.7, ls=(0, (3, 1.5)), zorder=2)
    S.note(ax, 25.8, 17.9, "blind-test budget", size=6.9,
           color=C["hi"], ha="left", va="top")

    ax.set_xlabel("Test frames transmitted (%)", fontsize=7.8)
    ax.set_ylabel("Missed action-high frames (%)", fontsize=7.8)
    ax.tick_params(axis="both", labelsize=7.4)
    ax.set_xlim(18, 102)
    ax.set_ylim(-0.6, 18.5)
    S.save(fig, P("fig6_operating_point.pdf"))


# ======================================================== Fig 7: frontier ====
def fig_frontier():
    fig, axes = plt.subplots(1, 2, figsize=S.figsize("full", 2.28))
    axL, axR = axes

    # ---- (a) LIBERO-Spatial forced-horizon sweep: entirely measured --------
    d = REAL["horizon_sweep"]
    x = np.array(d["send_frac"])
    y = np.array(d["succ"], float)
    lo = np.array(d["ci_lo"], float)
    hi = np.array(d["ci_hi"], float)
    o = np.argsort(x)
    x, y, lo, hi = x[o], y[o], lo[o], hi[o]

    S.grid(axL)
    axL.fill_between(x, lo, hi, color=C["band"], alpha=0.55, lw=0, zorder=1)
    axL.plot(x, y, ls="-", marker="o", color=C["periodic"], zorder=4,
             label=r"Periodic, forced horizon $h$")
    off = {12: (-1, 7.5), 10: (-9, -2), 8: (1, 7.0), 6: (0, -8.5),
           4: (0, -8.5), 2: (0, -8.5), 1: (0, -8.5), 0: (-2, -8.5)}
    for xi, yi, hh in zip(x, y, np.array(d["h"])[o]):
        dx, dy = off[int(hh)]
        axL.annotate(f"$h{{=}}{hh}$", xy=(xi, yi), xytext=(dx, dy),
                     textcoords="offset points", fontsize=S.BASE - 1.8,
                     ha="center", color=C["muted"])

    i6, i8 = list(np.array(d["h"])[o]).index(6), list(np.array(d["h"])[o]).index(8)
    S.arrow_note(axL, (x[i8], y[i8] - 1.0), (17.0, 45.0),
                 "success rises as the budget falls:\n"
                 "staleness is not a deterministic\nepisode-level cost",
                 size=S.BASE - 1.5, ha="left")

    axL.set_xscale("log")
    axL.set_xticks([10, 15, 25, 50, 100])
    axL.xaxis.set_major_formatter(pct)
    axL.set_xlim(6.4, 125)
    axL.set_ylim(40, 104)
    axL.set_xlabel("Realized agent-view send fraction (%, log)")
    axL.set_ylabel("Task success (%)")
    axL.set_title("(a) LIBERO-Spatial, forced horizon — all measured",
                  fontsize=S.BASE - 0.5, pad=3.5)
    axL.legend(loc="lower right")

    # ---- (b) LIBERO-Object budget sweep -----------------------------------
    f = SYNTH["frontier_object"]
    r = np.array(f["rate"], float)
    per = np.array(f["periodic"])
    hw = np.array(f["half_ci"])

    S.grid(axR)
    axR.fill_between(r, per - hw, per + hw, color=C["band"], alpha=0.55, lw=0,
                     zorder=1, label="periodic 95% band")
    for arm in ["periodic", "learned", "oracle", "lpips", "random"]:
        axR.plot(r, f[arm], ls=LS[arm], marker=M[arm], color=C[arm],
                 mfc="white" if arm != "periodic" else C["periodic"],
                 mew=0.8, ms=2.9, label=LABEL[arm], zorder=4)

    for rr in (25.0, 50.0):
        i = f["rate"].index(rr)
        for arm in ("periodic", "learned"):
            axR.plot(rr, f[arm][i], marker=M[arm], color=C[arm], ms=5.2,
                     mew=1.0, mfc=C[arm], zorder=6)
    axR.axvspan(23, 54, color="#F2F2F2", lw=0, zorder=0)
    S.note(axR, 34, 101.0, "frozen blind test\n(filled markers measured)",
           size=S.BASE - 1.5, ha="center", va="top")

    axR.set_xscale("log")
    axR.set_xticks([10, 15, 25, 50, 100])
    axR.xaxis.set_major_formatter(pct)
    axR.set_xlim(8.6, 125)
    axR.set_ylim(38, 104)
    axR.set_xlabel("Realized agent-view send fraction (%, log)")
    axR.set_title("(b) LIBERO-Object, budget sweep", fontsize=S.BASE - 0.5, pad=3.5)
    axR.legend(loc="upper left", bbox_to_anchor=(0.005, 0.995), ncol=1,
               fontsize=S.BASE - 1.4, borderaxespad=0.2)
    maybe_stamp(axR, f["_tag"])

    fig.subplots_adjust(wspace=0.16)
    S.save(fig, P("fig7_frontier.pdf"))


# ========================================================= Fig 8: effects ====
def fig_effects():
    eff = REAL["effects"]
    n = len(eff)
    fig, ax = plt.subplots(figsize=S.figsize("col", 2.15))
    y = np.arange(n)[::-1]

    mde = mcnemar_hw(PI_D, 160, Z_95 + Z_80POW)
    ax.axvspan(-mde, mde, color="#F3F3F3", lw=0, zorder=0)
    ax.axvline(0, color=C["periodic"], lw=0.9, zorder=2)

    colmap = {"exploratory": C["lpips"], "blind": C["learned"],
              "oracle-A": C["oracle"], "oracle-B": C["oracle"]}
    for yi, (lab, bud, e, lo, hi, nc, panel, rm) in zip(y, eff):
        col = colmap[panel]
        if lo is not None:
            ax.plot([lo, hi], [yi, yi], color=col, lw=1.0, zorder=3,
                    solid_capstyle="butt")
            for xx in (lo, hi):
                ax.plot([xx, xx], [yi - 0.16, yi + 0.16], color=col, lw=1.0, zorder=3)
            ax.plot(e, yi, marker="s" if rm else "s", ms=3.8, color=col,
                    mfc=col if rm else "white", mew=1.0, zorder=5)
        else:
            ax.plot(e, yi, marker="o", ms=3.8, mfc="white", mec=col, mew=1.0, zorder=5)
            ax.annotate("no CI", xy=(e, yi), xytext=(5, 0), textcoords="offset points",
                        fontsize=S.BASE - 1.6, color=col, va="center")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{l.split(' (')[0]} @{b}%\n{l.split(' (')[1][:-1]}"
                        for (l, b, *_ ) in eff], fontsize=S.BASE - 1.4)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-33, 33)
    ax.set_ylim(-0.75, n + 0.62)
    ax.set_xlabel("Success difference vs. rate-matched periodic (pp)")
    S.grid(ax, axis="x")

    S.note(ax, 0, n + 0.12, f"$\\pm${mde:.1f} pp: not resolvable at $n{{=}}160$",
           size=S.BASE - 1.5, ha="center", va="bottom", color=C["muted"])

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([], [], ls="", marker="s", color=C["lpips"], mfc="white", ms=3.8,
               label="not rate-matched"),
        Line2D([], [], ls="", marker="s", color=C["learned"], ms=3.8,
               label="learned, frozen"),
        Line2D([], [], ls="", marker="s", color=C["oracle"], ms=3.8, label="oracle"),
    ], loc="lower left", bbox_to_anchor=(-0.01, -0.02), fontsize=S.BASE - 1.5)
    S.save(fig, P("fig8_effects.pdf"))


# ========================================================== Fig 9: power =====
def fig_power():
    p = REAL["power"]
    z = Z_95 + Z_80POW
    n = np.linspace(60, 2500, 400)
    fig, ax = plt.subplots(figsize=S.figsize("col", 1.78))
    S.grid(ax)

    for pid, ls, lab, col in [(0.05, (0, (1.2, 1.2)), r"$\pi_d = 0.05$", C["muted"]),
                              (p["pi_d"], "-", r"$\pi_d = 0.078$ (observed)", C["learned"]),
                              (0.15, (0, (5, 1.6)), r"$\pi_d = 0.15$", C["muted"])]:
        ax.plot(n, 100 * z * np.sqrt(pid / n), ls=ls, color=col, label=lab,
                lw=1.2 if col == C["learned"] else 0.9)

    ax.axvline(160, color=C["hi"], lw=0.7, ls=(0, (3, 1.5)))
    S.note(ax, 178, 13.6, "current blind test\n(160 episodes/arm)",
           size=S.BASE - 1.4, color=C["hi"], va="top")

    ax.axhline(p["observed_effect"], color=C["muted"], lw=0.6, ls=(0, (4, 2)))
    S.note(ax, 2470, p["observed_effect"] + 0.42,
           f"observed $+{p['observed_effect']:.2f}$ pp", size=S.BASE - 1.4, ha="right")

    nstar = p["n_for_observed"]
    ax.plot(nstar, 100 * z * np.sqrt(p["pi_d"] / nstar), "o", color=C["learned"],
            ms=4.2, mfc="white", mew=1.1, zorder=6)
    S.note(ax, nstar + 55, 5.0, f"$n \\approx {nstar}$", size=S.BASE - 1.2,
           color=C["learned"])

    ax.set_xlabel("Episodes per arm (paired initial states)")
    ax.set_ylabel("Detectable effect at 80% power (pp)")
    ax.set_xlim(0, 2560)
    ax.set_ylim(0, 15.4)
    ax.legend(loc="upper right", fontsize=S.BASE - 1.3)
    S.save(fig, P("fig9_power.pdf"))


# ======================================================== Fig 10: age tail ===
def fig_age_tail():
    d = SYNTH["age_tail"]
    a = np.array(d["a"], float)
    fig, ax = plt.subplots(figsize=S.figsize("col", 2.0))
    S.grid(ax)

    series = [("periodic", "periodic", r"Periodic $h{=}3$ (exact)", "-"),
              ("bernoulli", "random", "Bernoulli 0.25 (exact)", (0, (5, 1.4, 1.2, 1.4))),
              ("learned", "learned", r"Learned $+\,K_{\max}{=}8$", "-"),
              ("oracle", "oracle", r"Oracle $\delta_t$", (0, (5, 1.6))),
              ("learned_nocap", "lpips", "Learned, no cap", (0, (1.3, 1.3)))]

    for key, col, lab, ls in series:
        v = np.array(d[key], float)
        m = v > 0
        ax.step(a[m], v[m], where="post", ls=ls, color=C[col],
                label=f"{lab},  $\\bar{{a}}={sum(d[key]):.2f}$",
                lw=1.25 if key in ("learned", "periodic") else 1.0, zorder=4)

    kmax = d["kmax"]
    ax.axvline(kmax, color=C["hi"], lw=0.7, ls=(0, (3, 1.5)), zorder=2)
    S.note(ax, kmax - 0.18, 0.62, r"$K_{\max}$", size=S.BASE - 0.8, color=C["hi"],
           ha="right")

    ax.set_yscale("log")
    ax.set_xlabel("Agent-view age $a$ (control steps)")
    ax.set_ylabel(r"$\Pr[\,\mathrm{age} > a\,]$")
    ax.set_xlim(-0.25, 12.4)
    ax.set_ylim(2.6e-2, 1.35)
    ax.set_xticks(range(0, 13, 2))
    ax.legend(loc="lower left", bbox_to_anchor=(-0.015, -0.02),
              fontsize=S.BASE - 1.7)

    S.note(ax, 12.2, 1.26, "all arms at the same 25% mean send rate",
           size=S.BASE - 1.4, ha="right", va="top")
    S.arrow_note(ax, (3.0, 0.26), (4.1, 0.60),
                 "periodic bounds\nsilence at 3 steps",
                 size=S.BASE - 1.5, color=C["periodic"])
    maybe_stamp(ax, d["_tag"])
    S.save(fig, P("fig10_age_tail.pdf"))


# ================================================ Fig 11: target vs outcome ==
def fig_target_outcome():
    d = SYNTH["delta_outcome"]
    n = d["n_per_bin"]
    x = np.arange(5)
    fig, ax = plt.subplots(figsize=S.figsize("col", 1.92))
    S.grid(ax)

    for key, col, mk, lab in [("div_succ", "learned", "s",
                               r"binned by mean suppressed-step $\delta_t$"),
                              ("age_succ", "oracle", "s",
                               "binned by mean agent-view age")]:
        v = np.array(d[key], float)
        err = S.wilson_err(v, n)
        ax.errorbar(x, v, yerr=err, ls="-" if key == "div_succ" else (0, (5, 1.6)),
                    marker=mk, ms=3.2, color=C[col], mfc="white" if key != "div_succ" else C[col],
                    mew=0.9, capsize=1.8, elinewidth=0.7, capthick=0.7, label=lab,
                    zorder=4)

    sd = d["div_succ"][0] - d["div_succ"][-1]
    sa = d["age_succ"][0] - d["age_succ"][-1]
    ax.annotate("", xy=(4.30, d["div_succ"][-1]), xytext=(4.30, d["div_succ"][0]),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color=C["learned"]))
    ax.annotate("", xy=(4.62, d["age_succ"][-1]), xytext=(4.62, d["age_succ"][0]),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color=C["oracle"]))
    S.note(ax, 4.36, (d["div_succ"][0] + d["div_succ"][-1]) / 2,
           f"{sd:.0f} pp", size=S.BASE - 1.3, color=C["learned"], ha="left")
    S.note(ax, 4.68, (d["age_succ"][0] + d["age_succ"][-1]) / 2,
           f"{sa:.0f} pp", size=S.BASE - 1.3, color=C["oracle"])

    ax.set_xticks(x)
    ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4", "Q5"])
    ax.set_xlabel(r"Episode quintile (low $\rightarrow$ high), "
                  f"$n{{=}}{n}$ episodes each")
    ax.set_ylabel("Episode success (%)")
    ax.set_xlim(-0.45, 5.15)
    ax.set_ylim(36, 104)
    ax.legend(loc="lower left", fontsize=S.BASE - 1.5)
    maybe_stamp(ax, d["_tag"])
    S.save(fig, P("fig11_target_vs_outcome.pdf"))


# =========================================================== Fig 12: wrist ===
def fig_wrist():
    d = SYNTH["wrist"]
    n = d["n_ep"]
    x = np.arange(len(d["conds"]))
    w = 0.33
    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=S.figsize("col", 1.95), gridspec_kw={"width_ratios": [2.35, 1]})
    S.grid(ax)

    per = np.array(d["periodic"], float)
    lea = np.array(d["learned"], float)
    ax.bar(x - w / 2, per, w, color=C["periodic"], lw=0, label="Periodic", zorder=3)
    ax.bar(x + w / 2, lea, w, color=C["learned"], lw=0, label="ActDelta learned", zorder=3)
    ax.errorbar(x - w / 2, per, yerr=S.wilson_err(per, n), ls="", color="#1A1A1A",
                elinewidth=0.6, capsize=1.6, capthick=0.6, zorder=5)
    ax.errorbar(x + w / 2, lea, yerr=S.wilson_err(lea, n), ls="", color="#1A1A1A",
                elinewidth=0.6, capsize=1.6, capthick=0.6, zorder=5)

    ax.set_xticks(x)
    ax.set_xticklabels(d["conds"], fontsize=S.BASE - 1.2)
    ax.set_ylabel("Task success (%) @ 25% budget")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.56, 1.045),
              fontsize=S.BASE - 1.4, ncol=1)
    S.note(ax, -0.42, 95, "(a) absolute", size=S.BASE - 1.2)

    # paired difference, which is what the design actually resolves
    S.grid(ax2)
    diff = lea - per
    hw = np.array([mcnemar_hw(p, n) for p in d["pi_d"]])
    ax2.axhline(0, color=C["periodic"], lw=0.8, zorder=2)
    ax2.errorbar(x, diff, yerr=hw, ls="", marker="s", ms=3.6, color=C["learned"],
                 elinewidth=0.9, capsize=2.0, capthick=0.8, zorder=4)
    # Sit the labels above each cap. Placing them beside the marker collides
    # with the neighbouring arm's error bar, which is wide at this n.
    for xi, dd, hh in zip(x, diff, hw):
        ax2.annotate(f"$+{dd:.1f}$", xy=(xi, dd + hh),
                     xytext=(0, 3.0), ha="center", va="bottom",
                     textcoords="offset points", fontsize=S.BASE - 1.4,
                     color=C["learned"])
    ax2.set_xticks(x)
    ax2.set_xticklabels(["real", "froz.", "none"], fontsize=S.BASE - 1.4)
    ax2.set_ylabel(r"$\Delta$ vs periodic (pp)")
    ax2.set_xlim(-0.6, 2.6)
    ax2.set_ylim(-9, 24)
    S.note(ax2, -0.5, 21.5, "(b) paired", size=S.BASE - 1.2)

    maybe_stamp(ax, d["_tag"])
    fig.subplots_adjust(wspace=0.62)
    S.save(fig, P("fig12_wrist.pdf"))


# ========================================================== Fig 13: uplink ===
def fig_uplink():
    d = SYNTH["bytes"]
    r = np.array(d["rate"], float)
    mean = np.array(d["mbps"], float)
    p95l = np.array(d["p95_learned"], float)
    p95p = np.array(d["p95_periodic"], float)

    fig, ax = plt.subplots(figsize=S.figsize("col", 1.95))
    S.grid(ax)

    for nrob, alpha in zip(d["n_robots_shown"], [1.0, 0.62, 0.36]):
        ax.plot(r, p95l * nrob, ls="-", marker="^", ms=2.8, color=C["learned"],
                alpha=alpha, mfc="white", mew=0.8, zorder=4,
                label=f"learned, P95 / 1 s ($\\times${nrob})" if nrob == 1 else None)
        ax.plot(r, p95p * nrob, ls=(0, (5, 1.6)), marker="v", ms=2.8,
                color=C["periodic"], alpha=alpha, mfc="white", mew=0.8, zorder=3,
                label=f"periodic, P95 / 1 s" if nrob == 1 else None)
        if nrob > 1:
            ax.annotate(f"$\\times{nrob}$ robots", xy=(r[-1], p95l[-1] * nrob),
                        xytext=(-2, 3), textcoords="offset points",
                        fontsize=S.BASE - 1.6, ha="right", color=C["learned"],
                        alpha=max(alpha, 0.55))
    ax.plot(r, mean, ls="-", marker="o", ms=2.8, color=C["random"], zorder=5,
            label="mean, one robot")

    ax.axhline(d["shared_link_mbps"], color=C["hi"], lw=0.7, ls=(0, (2.5, 1.5)))
    S.note(ax, 11, d["shared_link_mbps"] * 1.08,
           f"example {d['shared_link_mbps']:.0f} Mb/s shared uplink",
           size=S.BASE - 1.4, color=C["hi"], va="bottom")

    ratio = d["p95_mult_learned"] / d["p95_mult_periodic"]
    S.arrow_note(ax, (25, p95l[1]), (36, 0.34),
                 f"at a matched mean rate the\nlearned tail is {ratio:.1f}$\\times$ periodic",
                 size=S.BASE - 1.5)

    ax.set_xlabel("Agent-view send fraction (%)")
    ax.set_ylabel("Uplink demand (Mb/s)")
    ax.set_yscale("log")
    ax.set_xlim(5, 105)
    ax.set_ylim(0.06, 9)
    ax.set_yticks([0.1, 0.3, 1, 3])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.legend(loc="upper left", fontsize=S.BASE - 1.5)
    maybe_stamp(ax, d["_tag"])
    S.save(fig, P("fig13_uplink.pdf"))


# ========================================================== Fig 14: device ===
def fig_device():
    d = SYNTH["device"]
    y = np.arange(len(d["stage"]))[::-1]
    fig, ax = plt.subplots(figsize=S.figsize("col", 1.78))
    S.grid(ax, axis="x")

    cols = [C["learned"] if o else C["muted"] for o in d["onboard"]]
    ax.barh(y, d["ms"], height=0.6, color=cols, lw=0, zorder=3)
    for yi, ms, du, on in zip(y, d["ms"], d["duty"], d["onboard"]):
        if on and du < 1.0:
            ax.barh(yi, ms * du, height=0.6, color=C["learned"], alpha=0.45,
                    hatch="///", edgecolor="white", lw=0, zorder=4)
        ax.annotate(f"{ms:.1f} ms", xy=(ms, yi), xytext=(3.2, 0),
                    textcoords="offset points", fontsize=S.BASE - 1.3,
                    va="center", color="#3A3A3A")

    tot = d["worst_case_ms"]
    amo = d["amortised_ms"]
    ax.axvline(tot, color=C["hi"], lw=0.7, ls=(0, (3, 1.5)), zorder=5)
    S.note(ax, tot * 1.35, 2.55,
           f"robot-side\nworst case {tot:.1f} ms\namortised {amo:.1f} ms",
           size=S.BASE - 1.4, color=C["hi"], va="center")

    per = d["control_period_ms"]
    ax.axvline(per, color=C["random"], lw=0.7, ls=(0, (1.4, 1.4)), zorder=5)
    S.note(ax, per * 1.12, 4.05, f"{d['control_hz']:.0f} Hz control\nperiod ({per:.0f} ms)",
           size=S.BASE - 1.4, color=C["random"], va="top")

    ax.set_yticks(y)
    ax.set_yticklabels(d["stage"], fontsize=S.BASE - 1.0)
    ax.tick_params(axis="y", length=0)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 900)
    ax.set_ylim(-1.15, len(y) - 0.35)
    ax.set_xlabel("Latency per control step (ms, log)")
    S.note(ax, 0.34, -0.80, "hatched = duty-cycled at a 25% budget",
           size=S.BASE - 1.5, va="center")
    maybe_stamp(ax, d["_tag"])
    S.save(fig, P("fig14_device.pdf"))


# ============================================= auto-generated LaTeX numbers ==
def emit_tex():
    """Emit numbers that the prose and Table 2 must not be allowed to drift from."""
    w = REAL["wm"]
    imp = [(b - a) / b * 100 for b, a in zip(w["baseline"], w["adopted"])]
    imp = dict(zip(w["h"], imp))
    d = SYNTH["device"]
    lines = [
        "% AUTO-GENERATED by make_figs.py -- do not edit.",
        "% Any number here is computed from figs/data.py at build time.",
        "% Draft mode is decided HERE, by the figure build, so the figure",
        "% stamps and the red \\claimTBD marks can never disagree.",
        (r"\draftmodetrue" if DRAFT else r"\draftmodefalse"),
        r"\newcommand{\wmImpOne}{%.1f}" % imp[1],
        r"\newcommand{\wmImpFive}{%.1f}" % imp[5],
        r"\newcommand{\wmImpEight}{%.1f}" % imp[8],
        r"\newcommand{\wmImpTwelve}{%.1f}" % imp[12],
        r"\newcommand{\wmWindows}{%s}" % f"{w['n_windows']:,}",
        r"\newcommand{\mde}{%.1f}" % mcnemar_hw(PI_D, 160, Z_95 + Z_80POW),
        r"\newcommand{\pid}{%.3f}" % PI_D,
        r"\newcommand{\nForObserved}{%d}" % REAL["power"]["n_for_observed"],
        r"\newcommand{\opMedFNR}{%.2f}" % REAL["head"]["op_points"][0][1],
        r"\newcommand{\opMedMiss}{%.2f}" % REAL["head"]["op_points"][0][2],
        r"\newcommand{\opMedFNRLTen}{%.1f}" % REAL["head"]["median_rate_fnr_l10"],
        r"\newcommand{\devWorst}{%.1f}" % d["worst_case_ms"],
        r"\newcommand{\devAmort}{%.1f}" % d["amortised_ms"],
        r"\newcommand{\devPeriod}{%.0f}" % d["control_period_ms"],
        r"\newcommand{\burstRatio}{%.1f}" % (
            SYNTH["bytes"]["p95_mult_learned"] / SYNTH["bytes"]["p95_mult_periodic"]),
    ]

    # Resolution of the frontier: which arm pairs this design separates and
    # which it does not. Both numbers are arithmetic given the discordance
    # model; neither is a new measurement.
    F = SYNTH["frontier_object"]
    i25 = F["rate"].index(25.0)
    gap_lb = F["learned"][i25] - F["random"][i25]      # learned vs Bernoulli
    gap_ll = F["learned"][i25] - F["lpips"][i25]       # learned vs LPIPS
    band = F["half_ci"][i25]
    n_for_gap = n_for_effect(gap_lb, PI_D)
    lines += [
        r"\newcommand{\bandAtQuarter}{%.1f}" % band,
        r"\newcommand{\gapLearnedBern}{%.1f}" % gap_lb,
        r"\newcommand{\gapLearnedLpips}{%.1f}" % gap_ll,
        r"\newcommand{\nForBern}{%s}" % f"{n_for_gap:,}",
    ]

    # Mean observation age per arm, integrated from the same survival curves
    # the figure draws, so the legend and the prose cannot disagree.
    A = SYNTH["age_tail"]
    mean_age = lambda k: sum(A[k])
    lines += [
        r"\newcommand{\ageMeanBern}{%.2f}" % mean_age("bernoulli"),
        r"\newcommand{\ageMeanLearned}{%.2f}" % mean_age("learned"),
        r"\newcommand{\ageMeanNoCap}{%.2f}" % mean_age("learned_nocap"),
    ]
    p = P("numbers_auto.tex")
    with open(p, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  wrote", p)


if __name__ == "__main__":
    if self_check():
        sys.exit("data.py self-check failed; refusing to build figures")
    print("building figures ->", OUT)
    for fn in (fig_wm, fig_fidelity, fig_head_strata, fig_operating, fig_frontier,
               fig_effects, fig_power, fig_age_tail, fig_target_outcome,
               fig_wrist, fig_uplink, fig_device):
        fn()
    emit_tex()
    if DRAFT:
        print("\nDRAFT mode: panels backed by placeholder data are stamped.")
        print("Set ACTDELTA_DRAFT=0 only after replacing the SYNTH blocks.")
