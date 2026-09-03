"""Whole-paper preflight. Written after a referenced figure went missing and
neither the figure check (which globbed existing files) nor the log check
(which grepped a log LaTeX wraps at 79 columns) noticed."""
import pymupdf, os, re, glob, sys
ROOT="/home/zjx/mobicom_paper/MobiCom-ActDelta"
os.chdir(ROOT)
src=open('main.tex',encoding='utf-8').read()
log=open('main.log',encoding='utf-8',errors='replace').read()
flat=log.replace("\n","")           # undo LaTeX's 79-column wrapping
fail=[]
def chk(cond,msg):
    print(("  OK   " if cond else "  FAIL ")+msg)
    if not cond: fail.append(msg)

# 1. every \includegraphics target must exist on disk
refs=re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}',src)
missing=[r for r in refs if not os.path.exists(f"figs/{r}") and not os.path.exists(r)]
chk(not missing, f"all {len(refs)} \\includegraphics targets exist"+(f" -- MISSING {missing}" if missing else ""))

# 2. every \input target must exist
inputs=re.findall(r'\\input\{([^}]+)\}',src)
mi=[i for i in inputs if not os.path.exists(i) and not os.path.exists(i+'.tex')]
chk(not mi, f"all {len(inputs)} \\input targets exist"+(f" -- MISSING {mi}" if mi else ""))

# 3. log, read unwrapped
chk("not found" not in flat, "no 'not found' in the log")
chk("Emergency stop" not in flat and "! LaTeX Error" not in flat, "no LaTeX errors")
chk("Citation" not in flat or "undefined" not in flat, "no undefined citations")
chk("Reference" not in flat or "undefined" not in flat.replace("Package rerunfilecheck",""), "no undefined references")
chk("Overfull" not in flat, "no overfull boxes")
chk("draft setting" not in flat, "no figure fell back to a draft box")

# 4. the PDF itself
d=pymupdf.open("main.pdf")
ref=next(i for i,p in enumerate(d,1) for b in p.get_text("dict")["blocks"] if b.get("type")==0
         for l in b["lines"] if "".join(x["text"] for x in l["spans"]).strip()=="References" and l["bbox"][1]<120)
chk(ref-1<=12, f"body is {ref-1} pages (limit 12)")
chk(not [x for p in d for x in p.get_fonts(full=True) if x[2].lower().startswith('type3')], "no Type 3 fonts")
chk(sum(len(p.get_links()) for p in d)==0, "no embedded hyperlinks")
chk(os.path.getsize("main.pdf")<15e6, f"file size {os.path.getsize('main.pdf')/1e6:.2f} MB < 15 MB")
chk(abs(d[0].rect.width-612)<1 and abs(d[0].rect.height-792)<1, "US letter")

# 5. every figure included at 1.0000x -- iterate over REFERENCES, not the directory
COL=241.14749/72.27; TXT=506.295/72.27
bad=[]
for m in re.finditer(r'\\includegraphics\[width=([^\]]+)\]\{([^}]+)\}',src):
    w,f=m.group(1),m.group(2); p=f"figs/{f}"
    if not os.path.exists(p): bad.append((f,"missing")); continue
    tgt = TXT if 'textwidth' in w else COL
    dev = abs(tgt/(pymupdf.open(p)[0].rect.width/72.0)-1)
    if dev>1e-4: bad.append((f,f"{dev*100:.2f}% off"))
chk(not bad, f"all {len(refs)} figures included at 1.0000x"+(f" -- {bad}" if bad else ""))

# 6. how many figures does the compiled paper actually show?
n=len(set(re.findall(r'Figure (\d+):', d[0].get_text()+"".join(p.get_text() for p in d))))
print(f"\n  figures numbered in the compiled PDF: {n}")
print(f"  sections: {src.count(chr(92)+'section{')}")
sys.exit(1 if fail else 0)
