# Figures

Every figure in the paper is **three files with the same stem**:

| File | What it is | Who writes it |
|---|---|---|
| `<fig>.tex` | the drawing code — TikZ/pgfplots, standalone-compilable | you, by hand |
| `<fig>.json` | the data — numbers and labels, no layout | you, or an export script |
| `<fig>.pdf` | the compiled figure, included by `main.tex` | `make` |

`main.tex` only ever does `\includegraphics`. It loads no TikZ and no pgfplots,
which is why the paper now builds in ~2 s instead of recompiling 14 pictures on
every run.

```
figures/
├── preamble.tex          shared by every figure: fonts, sizes, colours, styles
├── macros.tex            \sys, \pizero, ... — also \input by main.tex
├── build.py              JSON -> pgfplots-readable tables
├── Makefile
├── experiment/           figures that show measured data
└── schematic/            architecture / protocol / state diagrams
```

## Building

```sh
make                      # rebuild every figure that is out of date
make experiment/fig-pareto.pdf
make check                # is any .build output stale?
make clean                # intermediates + generated data, PDFs kept
make distclean            # PDFs too
```

`make` needs TeX Live (`~/texlive/2026`, put on `PATH` by the Makefile) and
`python3`. **The paper itself does not** — the figure PDFs are committed, so
`latexmk -pdf main.tex` works without ever running `make`.

## Why JSON needs `build.py`

LaTeX cannot read JSON. `build.py` bridges the gap: for each `<fig>.json` it
writes `.build/<fig>/` containing one whitespace-separated `.dat` per data
series plus a `data.tex` of scalars and labels. `preamble.tex` pulls that
directory in automatically using `\jobname`, so a figure's `.tex` never names
it. Nothing in `.build/` is edited by hand or committed.

Inside a figure's `.tex` you reach the data by name:

| Macro | Gives you | From the JSON block |
|---|---|---|
| `\figdata{series}` | path to that series' `.dat`, for `\addplot table` | `series` |
| `\figval{key}` | one number | `scalars` |
| `\figlabel{key}` | one piece of label text (may contain LaTeX) | `labels` |
| `\figgrid{key}` | generated `\heatcell` calls | `grids` |
| `\figgridcols{key}` `\figgridrows{key}` | tick lists for `\foreach` | `grids` |

Asking for a name that is not in the JSON is a build error, not a silent blank.

## The dividing line between `.tex` and `.json`

Put it in the **JSON** if a real measurement would replace it: data points,
percentages, thresholds you quote, legend text naming a condition.

Put it in the **`.tex`** if it is layout: axis ranges, colours, where an
annotation node sits, bar widths, which mark shape a series gets.

The test is: *when the experiment lands, should this change?* If yes, JSON.

Two consequences worth knowing about:

- **Derived positions are drawn from the data.** In `fig-m0-uplink-cdf.tex`
  the highlighted crossing is plotted at `(\figval{rate10},\figval{irishatrate10})`,
  not at literal coordinates, so the "77% of the time" callout cannot drift
  away from the curve. Same for the shaded bands: their edges *are* the
  threshold scalars, so a band can never disagree with the rule drawn on it.
- **One number, one home.** τ\* = 0.35, the policy-flip threshold, is measured
  in `fig-m3-decision-error.json` and referenced by `fig-m1-rollout-error.json`
  and `fig-m4-divergence-trace.json`. Three figures draw a band, a rule and a
  tick label from it. They still have to be edited together — the build does
  not check across files — but each figure is now internally consistent by
  construction.

## Schematics

`schematic/*.json` is **metadata only** — LaTeX never reads it. The
architecture diagram and the protocol state machine have no tabular data; their
content is node text and topology, which lives in the `.tex`. The JSON records
what the figure claims, where the claim comes from, whether its numbers are
real, and what elsewhere in the paper it has to stay consistent with — e.g.
`fig-arch.json` notes that its GFLOP/TFLOP pair fixes the ρ that
`fig-rho-compute-ratio.json` sweeps around.

## Matching the paper exactly

A standalone figure has no acmart around it, so `preamble.tex` reproduces what
acmart would have supplied — all three measured from a real
`acmart[sigconf,10pt]` document, not guessed:

- **fonts**: Libertine + `zi4` + `newtxmath`, the exact stack `acmart.cls`
  loads for `sigconf`;
- **font sizes**: 10/12, `\small` 9/11, `\footnotesize` 8/10, `\scriptsize`
  7/8, `\tiny` 6/7. These are *not* article's 10pt values — article gives
  `\tiny` 5/6 — and figures lean hard on `\tiny`;
- **widths**: `\figcolwidth` = 241.14749pt, `\figtextwidth` = 506.295pt.

Size every plot against **`\figlinewidth`**, never `\columnwidth` or
`\linewidth`: `standalone` resets both at `\begin{document}` to the cropped
page, so `width=1.0\columnwidth` silently becomes the full text width.
`\figlinewidth` defaults to one column; a figure that lived inside a
`subfigure` declares its real container instead, because in `main.tex` a
`subfigure` is a minipage and a minipage overwrites all three length registers:

```latex
\figcontainer{0.48\figtextwidth}   % subfigure{0.48\textwidth} in a figure*
\figcontainer{0.49\figcolwidth}    % subfigure{0.49\columnwidth}
```

This is more explicit than what it replaces: the figure now states the width it
was designed for instead of inheriting it from a wrapper two files away.

Figures are included at **natural size**. Never add `width=` to the
`\includegraphics` in `main.tex`: scaling a figure scales its text too, and the
figure's labels stop matching the body text. If a figure is the wrong size,
change its width in its own `.tex` and rebuild.

## Adding a figure

1. `experiment/fig-thing.json` — at minimum a `meta` block; add `series`,
   `scalars`, `labels` as needed.
2. `experiment/fig-thing.tex` — copy the header of any existing figure.
3. `make` — produces `experiment/fig-thing.pdf`.
4. In `main.tex`: `\figexp{fig-thing}` inside the usual `figure` environment,
   with the caption and `\label` staying in `main.tex` (so cross-references and
   subfigure lettering keep working).

## One figure depends on `main.aux`

`fig-rho-compute-ratio.tex` is the only figure that cites something in
`main.tex` — its x label names the equation that defines ρ. It loads `xr` and
imports `../../main.aux` so the standalone build prints the same equation
number the body text does. If `main.aux` does not exist the reference renders
as `??` (loudly, not silently); one `latexmk -pdf main.tex` in the paper
directory followed by `make` here fixes it. No other figure has this
dependency, which is why `xr` is loaded in that one file and not in
`preamble.tex`.
