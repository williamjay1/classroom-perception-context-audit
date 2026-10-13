"""Apply visual changes to current source without modifying other work."""
from pathlib import Path
import shutil,json,re,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'deliverables/latex'; DST=ROOT/'temp/visual_20261013_candidate'
spec=json.loads((ROOT/'results/visual_20261013_table_blocks.json').read_text(encoding='utf-8'))
DST.mkdir(exist_ok=True)
manifest={}
for p in SRC.iterdir():
    if p.is_file() and p.suffix in ['.cls','.bst','.bib','.txt','.tex','.pdf']:
        shutil.copy2(p,DST/p.name)
    elif p.is_dir() and p.name=='bst':shutil.copytree(p,DST/p.name,dirs_exist_ok=True)
for name in ['manuscript.tex','manuscript_marked.tex']:
    p=SRC/name
    if not p.exists():continue
    text=p.read_text(encoding='utf-8')
    before=text
    for entry in spec['replacements']:
        original=entry['original'].replace('\r\n','\n')
        replacement=entry['replacement']
        if name=='manuscript_marked.tex':
            original=original.replace('%\n\\begin{tabular','\\color{blue}\n\\begin{tabular')
            replacement=replacement.replace('\\BMCVisualTableStyle','\\BMCVisualTableStyle\n\\color{blue}',1)
        assert text.count(original)==1,(name,entry['label'],text.count(original))
        text=text.replace(original,replacement)
    assert text.count('\\begin{document}')==1
    text=text.replace('\\begin{document}',spec['preamble']+'\n\\begin{document}')
    (DST/name).write_text(text,encoding='utf-8',newline='\n')
    manifest[name]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'candidate_sha256':hashlib.sha256((DST/name).read_bytes()).hexdigest()}
(ROOT/'results/visual_20261013_integration.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(SRC/'Springer_Nature_LaTeX_submission.zip') as z:
    print('Existing package entries:',z.namelist())
print(json.dumps(manifest,indent=2))
