# ===================================================================
#  ActDelta paper build
#
#    make            draft build. Placeholder panels are stamped and
#                    unverified claims are marked in red.
#    make final      camera-ready. REFUSES to build while figs/data.py
#                    still contains a SYNTH block.
#    make figs       regenerate figures only
#    make check      run the cross-panel consistency assertions
#    make offline    draft build using _offline/acmart.cls, for machines
#                    without the real acmart bundle. Not for submission.
#    make clean
# ===================================================================

TEX      := pdflatex -interaction=nonstopmode -halt-on-error
BIB      := bibtex
MAIN     := main
FIGDIR   := figs
FIGSRC   := $(FIGDIR)/data.py $(FIGDIR)/style.py $(FIGDIR)/make_figs.py
FIGOUT   := $(FIGDIR)/fig3_wm_selection.pdf $(FIGDIR)/numbers_auto.tex

.PHONY: all figs check final offline clean veryclean $(MAIN).pdf

all: $(MAIN).pdf

# ---------------------------------------------------------------- figures
# Always regenerate. Timestamps cannot see ACTDELTA_DRAFT, so a
# file-dependency rule would silently keep stamped panels after
# ACTDELTA_DRAFT=0. Generation takes a few seconds; correctness is worth it.
figs:
	cd $(FIGDIR) && python3 make_figs.py

check:
	cd $(FIGDIR) && python3 data.py

# ------------------------------------------------------------------ paper
$(MAIN).pdf: $(MAIN).tex refs.bib figs
	$(TEX) $(MAIN)
	-$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)
	@echo
	@echo "--- draft build complete ---"
	@grep -c 'PLACEHOLDER' $(FIGDIR)/data.py > /dev/null 2>&1 && \
	  echo "NOTE: figs/data.py still contains placeholder blocks; \
	panels are stamped and claims are marked." || true

# ------------------------------------------------------------ camera-ready
# The gate is deliberately annoying. Retagging a block in data.py without
# replacing its numbers will pass this check, so the gate is a reminder,
# not a proof. Verify against the logs.
final:
	@if grep -q '^SYNTH\[' $(FIGDIR)/data.py; then \
	  echo ""; \
	  echo "REFUSING to build a camera-ready copy."; \
	  echo "figs/data.py still defines these placeholder blocks:"; \
	  grep -o '^SYNTH\["[a-z_]*"\]' $(FIGDIR)/data.py | sort -u | sed 's/^/    /'; \
	  echo ""; \
	  echo "Replace each with measured values, move it into REAL, then rerun."; \
	  exit 1; \
	fi
	ACTDELTA_DRAFT=0 $(MAKE) figs
	@cp $(MAIN).tex $(MAIN).tex.bak
	@trap 'mv -f $(MAIN).tex.bak $(MAIN).tex' EXIT; \
	 sed -i 's/^\\newif\\ifdraftmode \\draftmodetrue/\\newif\\ifdraftmode \\draftmodefalse/' $(MAIN).tex; \
	 $(TEX) $(MAIN) && { $(BIB) $(MAIN) || true; } && $(TEX) $(MAIN) && $(TEX) $(MAIN)

# -------------------------------------------------------- offline fallback
offline: figs
	TEXINPUTS="./_offline:" BIBINPUTS=".:" $(TEX) $(MAIN)
	-TEXINPUTS="./_offline:" $(BIB) $(MAIN)
	TEXINPUTS="./_offline:" $(TEX) $(MAIN)
	TEXINPUTS="./_offline:" $(TEX) $(MAIN)

clean:
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).out $(MAIN).bbl $(MAIN).blg \
	      $(MAIN).toc $(MAIN).fls $(MAIN).fdb_latexmk $(MAIN).tex.bak

veryclean: clean
	rm -f $(MAIN).pdf $(FIGDIR)/fig*.pdf $(FIGDIR)/numbers_auto.tex
