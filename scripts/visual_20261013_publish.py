"""Publish verified visual edits; preserve existing package components."""
from pathlib import Path
import hashlib,json,shutil,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'temp/visual_20261013_candidate';P=ROOT/'deliverables/latex'
audit=json.loads((ROOT/'results/visual_20261013_integration.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,record in audit.items():
    assert sha(P/name)==record['source_sha256'],f'Concurrent source update: {name}'
    assert sha(C/name)==record['candidate_sha256']
for name in ['sn-jnl.cls','sn-bibliography.bib','sn-vancouver-num.bst']:
    assert sha(P/name)==sha(C/name),f'Concurrent dependency update: {name}'
pack=P/'Springer_Nature_LaTeX_submission.zip'
with zipfile.ZipFile(pack) as z:existing=z.namelist()
backup=ROOT/'temp/visual_20261013_prepublication';backup.mkdir(exist_ok=True)
for name in ['manuscript.tex','manuscript.pdf','manuscript_marked.tex','manuscript_marked.pdf',pack.name]:shutil.copy2(P/name,backup/name)
for name in ['manuscript.tex','manuscript.pdf','manuscript_marked.tex','manuscript_marked.pdf']:
    shutil.copy2(C/name,P/name)
for f in (C/'figures').iterdir():
    if f.suffix in ['.pdf','.svg','.png']:shutil.copy2(f,P/'figures'/f.name)
names=existing+[f'figures/Figure_{i}.{ext}' for i in [1,2] for ext in ['svg','png']]
tmp=C/'submission_refreshed.zip'
with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name in dict.fromkeys(names):z.write(P/name,name)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    for name in names:assert hashlib.sha256(z.read(name)).hexdigest()==sha(P/name)
shutil.copy2(tmp,pack)
spec=json.loads((ROOT/'results/visual_20261013_table_blocks.json').read_text(encoding='utf-8'))
table_source='\\documentclass{article}\n\\usepackage[paperwidth=170mm,paperheight=240mm,margin=20mm]{geometry}\n\\usepackage{booktabs,amsmath}\n'+spec['preamble']+'\n\\begin{document}\n'+'\n\\clearpage\n'.join(x['replacement'].replace('\\footnotetext{','\\par\\noindent{') for x in spec['replacements'])+'\n\\end{document}\n'
art=ROOT/'deliverables/Nature_style_figures_and_tables.zip'
with zipfile.ZipFile(art,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for i in [1,2]:
        for ext in ['pdf','svg','png']:z.write(P/'figures'/f'Figure_{i}.{ext}',f'Figure_{i}.{ext}')
    z.writestr('Tables.tex',table_source)
    z.writestr('README.txt','Figures 1 and 2: editable vector PDF and SVG, plus source-rendered 1200 dpi PNG.\nTables.tex: editable LaTeX for Tables 1-4. The tables are also integrated in manuscript.tex.\nStyle foundation: SciencePlots science/nature, explicitly adapted to the current Springer Nature manuscript text width.\nNumerical data, figure/table captions, and table notes were retained. No statistical analysis was rerun for the visual update.\n')
with zipfile.ZipFile(art) as z:assert z.testzip() is None
print(json.dumps({'main_pdf':str(P/'manuscript.pdf'),'submission_zip':str(pack),'artwork_zip':str(art),
 'files':{name:sha(P/name) for name in ['manuscript.tex','manuscript.pdf','manuscript_marked.tex','manuscript_marked.pdf']},
 'submission_entries':names},indent=2))
