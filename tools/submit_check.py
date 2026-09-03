import pymupdf, os, re, sys, json
os.chdir("/home/zjx/mobicom_paper/MobiCom-ActDelta")
src=open('main.tex',encoding='utf-8').read()
log=open('main.log',encoding='utf-8',errors='replace').read().replace("\n","")
d=pymupdf.open("main.pdf"); fails=[]
def chk(c,m):
    print(("  ok    " if c else "  FAIL  ")+m)
    if not c: fails.append(m)
ref=next(i for i,p in enumerate(d,1) for b in p.get_text("dict")["blocks"] if b.get("type")==0
         for l in b["lines"] if "".join(x["text"] for x in l["spans"]).strip()=="References" and l["bbox"][1]<120)

print("MobiCom submission rules")
chk('[sigconf,10pt,anonymous,review]' in src, "documentclass [sigconf,10pt,anonymous,review]{acmart}")
chk(ref-1<=12, f"body {ref-1} pages, references from p{ref} (limit 12, refs excluded)")
worst=0
for pno,pg in enumerate(d,1):
    if pno>12: break
    for side in ("L","R"):
        n=sum(1 for b in pg.get_text("dict")["blocks"] if b.get("type")==0 for l in b["lines"]
              if (lambda t,x0,y0,s0: t and 52<=x0<=566 and 70<y0<710 and (x0<310)==(side=="L")
                  and s0["font"] in ("LinLibertineT","LinLibertineTI") and 9.6<=s0["size"]<=10.3)
                 ("".join(x["text"] for x in l["spans"]).strip(),l["bbox"][0],l["bbox"][1],l["spans"][0]))
        worst=max(worst,n)
chk(worst<=55, f"max {worst} lines per column (limit 55)")
chk(abs(d[0].rect.width-612)<1 and abs(d[0].rect.height-792)<1, "US letter 8.5x11 in")
chk(sum(len(p.get_links()) for p in d)==0, "no embedded hyperlinks (CFP forbids)")
chk(not [x for p in d for x in p.get_fonts(full=True) if x[2].lower().startswith('type3')], "no Type 3 fonts")
md=d.metadata; leak=[k for k in ('author','title','subject','keywords') if md.get(k)]
try:
    xr=d.xref_xml_metadata(); xmp=d.xref_stream(xr).decode('utf-8','replace') if xr else ""
except Exception: xmp=""
chk(not leak, f"no identity in the PDF info dictionary")
chk('Anonymous Author(s)' in xmp or not xmp, "XMP dc:creator is the anonymous placeholder")
chk(os.path.getsize("main.pdf")<15e6, f"file size {os.path.getsize('main.pdf')/1e6:.2f} MB (limit 15)")
chk(bool(re.search(r'\\ccsdesc',src)) and bool(re.search(r'\\keywords',src)), "CCS concepts and keywords present")

print("\nDouble-blind")
chk(not re.search(r'our (previous|prior|earlier) (work|paper)|we (previously|earlier) (showed|presented)',src,re.I), "no first-person self-citation")
chk('acknowledg' not in src.lower().replace('acknowledgement, retransmission',''), "no acknowledgements section")
chk(not re.findall(r'https?://(?!doi\.org|www\.acm\.org)[^\s}]+', src), "no de-anonymising URLs in the source")

print("\nBuild and typography")
for probe,msg in (("not found","no missing input files"),("Emergency stop","no fatal errors"),
                  ("! LaTeX Error","no LaTeX errors"),("Overfull","no overfull boxes"),
                  ("draft setting","no image fell back to a draft box"),
                  ("Citation","no undefined citations")):
    bad = probe in log and (probe!="Citation" or "undefined" in log)
    chk(not bad, msg)

print("\nFigures and data")
refs=re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}',src)
chk(all(os.path.exists("figs/"+r) for r in refs), f"all {len(refs)} figure files present")
COL=241.14749/72.27; TXT=506.295/72.27; bad=[]
for m in re.finditer(r'\\includegraphics\[width=([^\]]+)\]\{([^}]+)\}',src):
    pth="figs/"+m.group(2)
    if not os.path.exists(pth): bad.append(m.group(2)); continue
    tgt=TXT if 'textwidth' in m.group(1) else COL
    if abs(tgt/(pymupdf.open(pth)[0].rect.width/72.0)-1)>1e-4: bad.append(m.group(2))
chk(not bad, f"all {len(refs)} figures included at 1.0000x")
chk(not re.search(r'^SYNTH\[', open('figs/data.py',encoding='utf-8').read(), re.M), "no SYNTH placeholder block in data.py")
chk(src.count('\\claimTBD{')==0, "no \\claimTBD unverified-claim markers left")
chk(src.count('\\synthcap')<=1, "no \\synthcap placeholder caption prefixes left")
chk('\\draftmodefalse' in open('figs/numbers_auto.tex',encoding='utf-8').read(), "figures built in camera-ready (non-draft) mode")
alltxt="".join(p.get_text() for p in d)
chk('PLACEHOLDER' not in alltxt.upper(), "no PLACEHOLDER watermark in the PDF")

print(f"\nsections {src.count(chr(92)+'section{')}   figures {len(set(re.findall(r'Figure (\\d+):',alltxt)))}   "
      f"tables {len(set(re.findall(r'Table (\\d+):',alltxt)))}   refs {len(re.findall(r'^.[0-9]+.', ''))}")
print(f"\n{'ALL CHECKS PASS' if not fails else str(len(fails))+' FAILURES: '+str(fails)}")
sys.exit(1 if fails else 0)
