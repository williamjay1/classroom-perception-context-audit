from pathlib import Path
import os,subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'temp/visual_20261013_candidate'
BIN=Path(os.environ.get('MIKTEX_BIN') or r'C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64')
env=os.environ.copy();env['TEMP']=str(ROOT/'temp');env['TMP']=env['TEMP']
result={}
for stem in ['manuscript','manuscript_marked']:
    cmds=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['bibtex',stem],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]
    for i,cmd in enumerate(cmds):
        p=subprocess.run([str(BIN/(cmd[0]+'.exe'))]+cmd[1:],cwd=DIR,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (DIR/f'{stem}_build_{i}.txt').write_bytes(p.stdout)
        assert p.returncode==0,(stem,cmd,p.stdout[-3000:])
    log=(DIR/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
    result[stem]={'overfull':re.findall(r'Overfull[^\n]*(?:\n[^\n]*)?',log),
        'undefined':re.findall(r'.*(?:undefined|Rerun to).*',log),
        'output':re.findall(r'Output written[^\n]*',log)}
(ROOT/'results/visual_20261013_compile.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
