"""
Figure style for ActDelta (MobiCom / ACM sigconf).

Conventions taken from recent MobiCom best-paper figures:

  * Vector PDF, TrueType embedded (fonttype 42). ACM rejects Type 3.
  * Serif face matched to the body text so figure labels and prose look like
    one document. acmart uses Libertine; we fall back through Libertinus ->
    Linux Libertine -> Liberation Serif -> DejaVu Serif.
  * Exact column geometry, so nothing is ever rescaled by \\includegraphics.
    Rescaling is the single most common cause of illegibly small axis text.
  * Label text never below 6 pt at final size.
  * One desaturated colour per experimental arm, held fixed across ALL figures,
    plus a distinct marker and dash pattern per arm so the figures survive
    greyscale printing and the two most common colour-vision deficiencies.
  * Two spines, hairline gridlines, no legend frame, no chartjunk.
  * The takeaway is annotated ON the axes. A reader who reads only figures
    and captions should still get the paper's argument.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

# ---------------------------------------------------------------- geometry
# Measured from the class itself, not rounded: acmart sigconf at 10 pt reports
#   \columnwidth = 241.14749pt   \textwidth = 506.295pt
# in TeX points (1/72.27 in). A figure emitted at exactly these sizes and
# included with width=\columnwidth is scaled by exactly 1.000, so a 7 pt label
# in the figure is 7 pt on the page. Rounding these to 3.33/7.00 is enough to
# make \includegraphics rescale, which is what this module exists to avoid.
COL = 241.14749 / 72.27     # 3.336750 in
FULL = 506.295 / 72.27      # 7.005604 in


def figsize(width="col", h=1.85):
    return ({"col": COL, "full": FULL}.get(width, width), h)


# ------------------------------------------------------------------ colour
# One desaturated colour per arm, held fixed everywhere.
#
# Chosen after extracting the palettes actually used in recent MobiCom
# papers. Most of them (Asteroid'24, Soar'24, Uirapuru'25) simply ship
# matplotlib tab10 or ColorBrewer Set1 -- saturated blue/red/orange/green.
# AquaScan'25 is the exception and uses a muted set; these values follow it
# in spirit while staying dark enough for hairline strokes on white.
#
# The arms are also separated in GREYSCALE, because these papers are read
# printed. Luminance ladder, 0-255 after gamma:
#     periodic  75 | learned  94 | oracle 112 | random 126 | lpips 139
# with a 13/255 minimum gap, on top of the per-arm marker and dash below.
C = {
    "periodic":  "#4A4A4A",   # the control: neutral dark grey, never colour
    "learned":   "#35618A",   # ActDelta learned trigger
    "oracle":    "#AF5551",   # oracle delta_t
    "lpips":     "#A08A5B",   # conventional fidelity criterion
    "random":    "#6B8578",   # content-blind Bernoulli
    "baseline":  "#9A9A9A",   # rejected world-model variant
    "adopted":   "#35618A",
    "band":      "#D8D8D8",   # confidence band fill
    "hi":        "#8C3B36",   # annotation / warning
    "muted":     "#7A7A7A",
    "rule":      "#BFBFBF",
    "synth":     "#AF5551",
}

# Marker + dash per arm, so the figures read in greyscale.
M = {"periodic": "o", "learned": "s", "oracle": "^", "lpips": "v", "random": "D"}
LS = {"periodic": "-", "learned": "-", "oracle": (0, (5, 1.6)),
      "lpips": (0, (1.2, 1.2)), "random": (0, (5, 1.4, 1.2, 1.4))}
LABEL = {"periodic": "Periodic (control)", "learned": "ActDelta learned",
         "oracle": r"Oracle $\delta_t$", "lpips": "LPIPS threshold",
         "random": "Random (Bernoulli)"}


def _register_texlive_serif():
    """Make the body text's own face visible to matplotlib.

    acmart sets Libertine, but TeX ships it as Type 1, which matplotlib
    cannot embed. TeX Live also ships Libertinus as OpenType, which it can.
    Registering it here is what lets _pick_serif() reach its first choice
    instead of falling through to whatever Times clone the machine happens
    to have -- which is why the previously committed panels were set in
    Times New Roman while the paper itself was set in Libertine.
    """
    import glob
    pats = ["/usr/share/fonts/**/Libertinus*.otf",
            os.path.expanduser("~/texlive/*/texmf-dist/fonts/opentype/public/"
                               "libertinus-fonts/Libertinus*.otf"),
            "/usr/local/texlive/*/texmf-dist/fonts/opentype/public/"
            "libertinus-fonts/Libertinus*.otf"]
    for pat in pats:
        for f in glob.glob(pat, recursive=True):
            try:
                font_manager.fontManager.addfont(f)
            except Exception:
                pass


_register_texlive_serif()


def _pick_serif():
    have = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("Libertinus Serif", "Linux Libertine O", "Linux Libertine",
                 "Liberation Serif", "Times New Roman", "Nimbus Roman",
                 "DejaVu Serif"):
        if cand in have:
            return cand
    return "serif"


SERIF = _pick_serif()

BASE = 7.0

plt.rcParams.update({
    # --- fonts
    "font.family": "serif",
    "font.serif": [SERIF, "DejaVu Serif"],
    "font.size": BASE,
    "axes.labelsize": BASE,
    "axes.titlesize": BASE,
    "xtick.labelsize": BASE - 0.5,
    "ytick.labelsize": BASE - 0.5,
    "legend.fontsize": BASE - 0.5,
    "mathtext.fontset": "stix",
    "mathtext.default": "it",
    # --- embed real fonts; ACM rejects Type 3
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "pdf.compression": 9,
    # --- axes
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#3A3A3A",
    "axes.labelpad": 2.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    # --- grid
    "grid.color": "#DCDCDC",
    "grid.linewidth": 0.4,
    "grid.alpha": 1.0,
    # --- ticks
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 2.2,
    "ytick.major.size": 2.2,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.pad": 1.8,
    "ytick.major.pad": 1.8,
    "xtick.color": "#3A3A3A",
    "ytick.color": "#3A3A3A",
    # --- lines
    "lines.linewidth": 1.1,
    "lines.markersize": 3.0,
    "lines.markeredgewidth": 0.7,
    # --- legend
    "legend.frameon": False,
    "legend.handlelength": 1.9,
    "legend.handletextpad": 0.5,
    "legend.labelspacing": 0.28,
    "legend.columnspacing": 1.0,
    "legend.borderaxespad": 0.3,
    # --- output
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": None,
    "savefig.transparent": False,
})


def grid(ax, axis="y"):
    ax.grid(True, axis=axis, zorder=0)
    ax.set_axisbelow(True)


def note(ax, x, y, s, color=None, size=BASE - 1.0, ha="left", va="center", **kw):
    """In-axes annotation carrying the takeaway."""
    return ax.text(x, y, s, color=color or C["muted"], fontsize=size,
                   ha=ha, va=va, zorder=6, **kw)


def arrow_note(ax, xy, xytext, s, color=None, size=BASE - 1.0, **kw):
    color = color or C["hi"]
    ax.annotate(s, xy=xy, xytext=xytext, fontsize=size, color=color, zorder=7,
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=color,
                                shrinkA=1, shrinkB=2,
                                connectionstyle="arc3,rad=0.18"), **kw)


def stamp_synthetic(ax, text="PLACEHOLDER DATA"):
    """Mark a panel whose values are not yet measured.

    Visible in the compiled PDF on purpose. It disappears only when the
    corresponding block in data.py is retagged, which is the one action that
    should ever remove it.
    """
    ax.text(0.5, 0.5, text, transform=ax.transAxes,
            fontsize=BASE + 3.5, color=C["synth"], alpha=0.105,
            ha="center", va="center", rotation=24, zorder=1,
            fontweight="bold", family="sans-serif")


def wilson(k, n, z=1.959964):
    """Wilson score interval; correct at the small n these panels use."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z / d * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, c - hw), min(1.0, c + hw)


def wilson_err(pcts, n):
    """Asymmetric error bars, in pp, for a list of success percentages."""
    lo, hi = [], []
    for v in pcts:
        k = round(v * n / 100.0)
        a, b = wilson(k, n)
        lo.append(v - 100 * a)
        hi.append(100 * b - v)
    return np.array([lo, hi])


def save(fig, path, wspace=None):
    """Write the figure at exactly its declared figsize.

    tight_layout packs the axes inside that fixed canvas, so margins are
    trimmed without changing the outer dimensions. Panel spacing, where a
    figure sets it, is re-applied afterwards because tight_layout would
    otherwise recompute it.
    """
    fig.tight_layout(pad=0.30)
    if wspace is not None:
        fig.subplots_adjust(wspace=wspace)
    fig.savefig(path)
    plt.close(fig)
    print("  wrote", path)
