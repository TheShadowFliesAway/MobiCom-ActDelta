# Figure build.  Each figure is <stem>.tex + <stem>.json -> <stem>.pdf.
#
#   make            build every figure that is out of date
#   make FIG.pdf    build one figure, e.g. make experiment/fig-pareto.pdf
#   make clean      drop intermediates and generated data, keep the PDFs
#   make distclean  drop the PDFs too
#
# main.tex only ever \includegraphics the PDFs, so it does not depend on this
# Makefile at all -- the PDFs are committed and the paper builds without it.

TEXMF_BIN := $(HOME)/texlive/2026/bin/x86_64-linux
export PATH := $(TEXMF_BIN):$(PATH)

PYTHON := python3

# pdflatex directly, not latexmk.  These figures are self-contained standalone
# documents: no bibliography, no multi-pass cross-references, nothing latexmk's
# scheduling buys us.  What latexmk does cost us is a false failure -- running
# two dozen sub-second jobs back to back trips its "the log file was created
# significantly earlier than this run" heuristic on a filesystem whose
# timestamps drift, and it reports an error for a figure it just built fine.
PDFLATEX := pdflatex -interaction=nonstopmode -halt-on-error

SOURCES := $(wildcard experiment/*.tex) $(wildcard schematic/*.tex)
PDFS    := $(SOURCES:.tex=.pdf)
JSONS   := $(wildcard experiment/*.json) $(wildcard schematic/*.json)
STAMP   := .build/.stamp

.PHONY: all clean distclean check
all: $(PDFS)

# One stamp for the whole JSON -> .build step: build.py is fast and regenerating
# everything keeps the dependency graph honest when a figure gains a series.
$(STAMP): build.py $(JSONS)
	@$(PYTHON) build.py
	@mkdir -p .build && touch $@

# A figure depends on its own drawing code, its own data, and the shared
# preamble/macros -- change the house style and every figure rebuilds.
# On failure, print the actual LaTeX error rather than a wall of log.
%.pdf: %.tex $(STAMP) preamble.tex macros.tex
	@echo "  pdflatex $<"
	@cd $(dir $<) && $(PDFLATEX) $(notdir $<) >/dev/null 2>&1 \
	  || { echo "*** $< failed:"; sed -n '/^!/,+8p' $(<:.tex=.log); exit 1; }
	@grep -q "Rerun to get" $(<:.tex=.log) \
	  && (cd $(dir $<) && $(PDFLATEX) $(notdir $<) >/dev/null 2>&1) || true

check:
	@$(PYTHON) build.py --check && echo "figure data up to date"

clean:
	@rm -rf .build
	@rm -f experiment/*.aux experiment/*.log experiment/*.fls \
	       experiment/*.fdb_latexmk experiment/*.out experiment/*.synctex.gz \
	       schematic/*.aux schematic/*.log schematic/*.fls \
	       schematic/*.fdb_latexmk schematic/*.out schematic/*.synctex.gz
	@echo "cleaned intermediates (PDFs kept)"

distclean: clean
	@rm -f $(PDFS)
	@echo "removed figure PDFs"
