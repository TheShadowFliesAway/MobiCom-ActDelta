# IDEA 2 · ActDelta — ACM MobiCom 2027 paper

Clean submission template. Source of truth: the MobiCom 2027 CFP,
<https://sigmobile.org/mobicom/2027/cfp.html>.

## Files

| File | What it is |
|---|---|
| `main.tex` | The paper. Contains no figure code --- see `figures/`. |
| `figures/` | One directory per figure kind. Each figure is three files with the same stem: `<fig>.tex` (drawing code), `<fig>.json` (data), `<fig>.pdf` (what `main.tex` includes). `figures/README.md` has the details. |
| `references.bib` | Your bibliography. |
| `acmart.cls` | Official ACM class, **v2.19 (2026/06/27)**, from TeX Live / CTAN. Unmodified. |
| `ACM-Reference-Format.bst` | Official ACM BibTeX style. Unmodified. |
| `acm*.bbx` `acm*.cbx` `acmdatamodel.dbx` | biblatex support files (only if you use biblatex instead of BibTeX). |
| `reference/sigconf.tex` | The official acmart sigconf sample — every macro demonstrated. Read it, don't edit it. |
| `reference/sigconf.pdf` | What that sample compiles to. |
| `reference/acmguide.pdf` | The full acmart manual. |

## Building

```sh
latexmk -pdf main.tex     # full build (pdflatex + bibtex + reruns)
latexmk -c main.tex       # clean intermediates, keep the PDF
```

The figure PDFs are committed, so this works on a fresh checkout with nothing
but TeX Live --- `main.tex` loads no TikZ and no pgfplots and takes ~2 s. To
change a figure instead:

```sh
cd figures && make        # rebuilds only the figures whose .tex or .json moved
```

`make` additionally needs `python3`, because figure data is JSON and LaTeX
cannot read JSON --- `figures/build.py` converts it to tables pgfplots can.
Replacing a placeholder measurement means editing a `.json` and running `make`;
you do not touch figure `.tex` for a data change. See `figures/README.md`.

TeX Live 2026 (scheme-full) is installed at `~/texlive/2026`, no root required.
`~/.bashrc` puts it on `PATH`; in a non-login shell, prepend it manually:

```sh
export PATH="$HOME/texlive/2026/bin/x86_64-linux:$PATH"
```

`acmart.cls` and the `.bst` also sit in this directory, so the build does not
depend on the system-wide acmart version.

PDF inspection tools (`pdfinfo`, `pdftoppm`, `pdftotext`) come from poppler,
installed in the conda base environment.

`main.pdf` in this directory is a verified build.

## Current state (after the 2026-08-19 format review)

15 pages total: **body exactly 12 pages, references 13--15**. Both columns of
page 12 are full to the last line, so the length is at the limit rather than
under it — anything added has to be paid for by a cut somewhere else. 53 lines
per column, under the CFP's 55.

Five preamble decisions come out of the review and are deliberate; each has a
comment in `main.tex` at the point where it is made.

| Setting | Why |
|---|---|
| `\def\@parfont{\bfseries}` | acmart/sigconf sets run-in paragraph headings in *italic*; all 21 MobiCom papers in the comparison corpus set them **bold** and reserve italic for emphasis. |
| `\title[ActDelta: …]{…}` | A real short running head. The full title in the header would run the page width, and `\sys` cannot go there — the macro ends in `\xspace`, which puts a space before the colon when the header re-typesets the title. |
| ACM reference block left printed | `printacmref=false` only hides a block that is mandatory at camera-ready. `anonymous` already suppresses the names inside it. |
| `\acmConference[ACM MobiCom '27]{…}{…}{To be announced}` | The venue string was `TBD`, which is the kind of thing that survives to camera-ready. SIGMOBILE had not published the 2027 location as of 2026-08-19; the `ACM` prefix and the dates are right, the location is the one field still to fill. |
| Captions are short | Median 29 words, max 48, at 10 pt. The review found 64 words median, about twice the corpus. Setup and per-point interpretation moved into body prose — see §8.9 of `PLACEHOLDERS.md` before you edit a caption. |

Line numbers in both margins come from the `review` class option. MobiCom does
not ask for them; keeping or dropping them is a taste call, recorded as an open
item in `PLACEHOLDERS.md` §10.

## MobiCom 2027 requirements (from the CFP)

**Format**
- `\documentclass[sigconf,10pt]{acmart}` — this template adds `anonymous,review`
  for double-blind review; drop both for camera-ready.
- Font no smaller than **10 pt**.
- Two columns, each **9.25 in × 3.33 in**, **0.33 in** between columns, at most
  **55 lines** of text per column. US Letter (8.5 × 11 in).
- Pages single-spaced and **numbered**.

**Length**
- **12 pages** of body, including figures, tables, and everything else.
- **References do not count** — as many pages as necessary.
- **Appendices do not count**, but must follow the bibliography, and reviewers
  are not required to read them.
- Non-bibliographic content over the limit **will not be reviewed**.

**File**
- PDF only, Acrobat-compatible. PostScript and MS Word are rejected.
- Under **15 MB**.
- Check with the **banal** format checker before submitting:
  <https://www.sysnet.ucsd.edu/~voelker/banal/> (the PC runs it both before and
  after the deadline).

**Double-blind — violations are not reviewed**
- No author names or affiliations anywhere in the paper *or in the PDF
  metadata*. Remove funding acknowledgments too.
- **No embedded hyperlinks** — they can compromise anonymity. Uncomment
  `\hypersetup{draft}` in `main.tex` before generating the submission PDF.
- Cite your own work in the third person. `[3] Reference deleted for
  double-blind review` is **not** permitted.
- Anonymize supplemental material links; they may not carry text that evades
  the 12-page limit.
- Preprints are allowed, but the submission must not point at the
  non-anonymized version, and publicizing it during review is discouraged.

**Submission**
- HotCRP: <https://mobicom27.hotcrp.com/>
- Registered abstracts need a real title and an abstract of **≥ 100 words**;
  `TBD` placeholders get desk-rejected.
- All authors declared at submission time; ORCID expected for each.

## Dates

- Conference: **October 18–22, 2027**
- Summer round: abstract **Aug 26, 2026**, paper **Sep 2, 2026** (both 23:59 AoE);
  early reject Oct 23, 2026; rebuttal Nov 3–6, 2026; notification Nov 19, 2026.
- **Winter round: TBD** as of the last check (2026-08-18). This is the round
  these three ideas target — watch the site for the dates.
