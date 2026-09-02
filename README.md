# ActDelta — revised paper package

Read `PLACEHOLDERS.md` first. It lists which numbers are measured, which are
still estimates, and what each estimate is anchored to.

## Build

```
make check     # cross-panel consistency assertions in figs/data.py
make           # draft build (real acmart from your TeX distribution)
make final     # camera-ready; refuses while placeholders remain
```

`make` needs the real `acmart` bundle. On Overleaf, upload this whole folder
and set `main.tex` as the root document — nothing else is required.

`make offline` builds against `_offline/acmart.cls`, a stand-in for machines
without acmart. `main-offline-preview.pdf` in this package was produced that
way. **Line breaks, float placement, the reference format and the page count
will differ from a real acmart build.** Use it to read the text and check the
figures, not to judge length.

## Layout

```
main.tex                revised paper. 4 new TikZ schematics; 10 \claimTBD{} marks
refs.bib                52 entries
figs/data.py            single source of truth. real / derived / synth tags,
                        audit reasoning in comments, 8 build-time assertions
figs/style.py           sigconf geometry, per-arm colour/marker/dash, watermark
figs/make_figs.py       12 figures + numbers_auto.tex
figs/numbers_auto.tex   generated macros; \input by Table 2 and §5 so the
                        table and the prose cannot drift apart
figs/data_orig.py       your uploaded file, unmodified, for diffing
figs/figstyles.tex      palette + TikZ styles shared by Figs. 1-3. Same
                        semantic colours as style.py, so the schematics and
                        the measured panels read as one figure set
figs/fig1_system.tex    Fig. 1, system overview
figs/fig2_ladder.tex    Fig. 2, the three questions and their verdicts
figs/fig3_protocol.tex  Fig. 3, the four frozen stages
                        These three are \input by main.tex, not imported as
                        PDFs: they are drawn at true \columnwidth (84 mm) so
                        nothing is rescaled and no label falls below 7 pt.
_offline/acmart.cls     fallback class. NOT for submission.
```

Everything not needed to build the paper — reference PDFs, page renders, the
unused TikZ figure set, Figma/SVG exports — lives outside the repo in
`../ActDelta-archive/`. LaTeX build artifacts are gitignored; `make clean`
removes them.

## Placeholder data

Six blocks in `figs/data.py` are still estimates: `age_tail`, `bytes`,
`delta_outcome`, `device`, `frontier_object`, `wrist`. See `PLACEHOLDERS.md`
for what each is anchored to and what to replace.

Draft mode stamps every panel drawn from an estimate and prints the
corresponding sentences in red. The figure build sets it and LaTeX reads it
from `figs/numbers_auto.tex`, so stamps and marks cannot disagree:

```
make                    # draft
ACTDELTA_DRAFT=0 make   # clean, after the blocks are replaced
make final              # the above, plus refuses while SYNTH blocks remain
```

## Replacing an estimate

Edit the block in `figs/data.py`, move it from `SYNTH` to `REAL`, then
`make check && make`. If an assertion fails, the message names the identity
that broke — most often a success rate that isn't on the grid its episode
count can emit, which usually means the episode count is wrong rather than
the rate. There are 11 such assertions; they cover the cross-panel identities
that were violated in the original draft.
