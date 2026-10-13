"""Read-only numerical audit of four LaTeX tables and Figure 2 PDF vectors.

The source of statistical truth is the already verified aggregate JSON. This
script never imports a figure/table production script and never fits a model.
It writes only the authorized visual-review Markdown report.
"""
from pathlib import Path
import argparse, hashlib, json, re, math, statistics
from datetime import datetime, timezone
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
INITIAL_NORMALIZED_BODY_HASH = 'd1bbe3a6ceccea390622c254332bda23345f2fbe71b45da7f33e663cbbe18d3f'
NUM = re.compile(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def model(v,label): return next(m for m in v['models'] if m['label']==label)
def outnumber(x):
    if isinstance(x,int): return str(x)
    p=4 if x!=0 and abs(x)<.0005 else 3
    s=f'{x:.{p}f}'
    return '0.000' if s=='-0.000' else s
def effect(v): return [outnumber(v[k]) for k in ('estimate','ci95_low','ci95_high')]
def trio(m,w,b,d): return [m['terms'][w],m['terms'][b],m['contextual_associations'][d]]
def body(text):
    text=text.split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0]
    return re.sub(r'\\begin\{(table\*?|figure\*?)\}.*?\\end\{\1\}','',text,flags=re.S)
def normalized(s): return re.sub(r'\s+',' ',s).strip()
def split_outer(s,delimiter):
    parts=[]; start=0; depth=0; i=0
    while i<len(s):
        if s[i]=='{' and (i==0 or s[i-1]!='\\'): depth+=1
        elif s[i]=='}' and (i==0 or s[i-1]!='\\'): depth-=1
        if depth==0 and s.startswith(delimiter,i):
            parts.append(s[start:i]);i+=len(delimiter);start=i;continue
        i+=1
    if s[start:].strip():parts.append(s[start:])
    return parts
def tables(text):
    blocks=re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}',text,re.S)
    result={}
    for t in blocks:
        label=re.search(r'\\label\{(tab\d+)\}',t)[1]
        table=re.search(r'\\begin\{(tabular\*?|tabularx)\}.*?\\midrule(.*?)\\(?:botrule|bottomrule)',t,re.S)
        if not table:raise ValueError(f'{label}: unrecognized table body')
        rows=[]
        for row in split_outer(table[2],r'\\'):
            cells=split_outer(row,'&')
            if len(cells)<2:continue
            tokens=[NUM.findall(c.replace('−','-').replace('{,}','').replace(',','')) for c in cells[1:]]
            if any(tokens):rows.append((cells,tokens))
        result[label]=(t,rows)
    return result

def pdf_vectors(path, expected):
    """Calibrate PDF plot positions from printed tick labels; check all 27 coordinates."""
    page=pymupdf.open(path)[0];draws=page.get_drawings()
    markers=[]
    for d in draws:
        r=d['rect'];fill=d['fill']
        if fill is None or min(fill)>.9 or not(2<=r.width<=18 and 2<=r.height<=18):continue
        if d['type'] not in ('f','fs'):continue
        x,y=(r.x0+r.x1)/2,(r.y0+r.y1)/2
        lines=[]
        for l in draws:
            if len(l['items'])!=1 or l['items'][0][0]!='l':continue
            p,q=l['items'][0][1:]
            color=l['color']
            if color is None or max(abs(a-b) for a,b in zip(color,fill))>.002:continue
            if abs(p.y-q.y)<.002 and abs(p.y-y)<.004 and min(p.x,q.x)-.004<=x<=max(p.x,q.x)+.004 and abs(p.x-q.x)>3:
                lines.append((min(p.x,q.x),max(p.x,q.x)))
        if len(lines)==1:markers.append({'x':x,'y':y,'low_x':lines[0][0],'high_x':lines[0][1]})
    if len(markers)!=9:raise ValueError(f'Figure 2 has {len(markers)} eligible marker/CI pairs; expected 9')
    ybands=[]
    for marker in sorted(markers,key=lambda m:m['y']):
        if not ybands or abs(marker['y']-ybands[-1])>1:ybands.append(marker['y'])
    vertical=len(ybands)==9
    markers.sort(key=lambda m:m['y'] if vertical else m['x'])
    groups=[markers[i:i+3] for i in (0,3,6)]
    means=[statistics.mean(m['x'] for m in g) for g in groups]
    bounds=[0,(means[0]+means[1])/2,(means[1]+means[2])/2,page.rect.width]
    spans=[s for b in page.get_text('dict')['blocks'] if 'lines'in b for l in b['lines'] for s in l['spans']]
    checks=[]
    for pi,g in enumerate(groups):
        g.sort(key=lambda m:m['y']);ticks=[]
        for s in spans:
            t=s['text'].strip().replace('−','-')
            if not re.fullmatch(r'[-+]?\d+(?:\.\d+)?',t):continue
            x=(s['bbox'][0]+s['bbox'][2])/2;y=(s['bbox'][1]+s['bbox'][3])/2
            below_rows=y>max(m['y'] for m in g)+8
            if vertical:
                upper_y=min(m['y'] for m in groups[pi+1])-8 if pi<2 else page.rect.height
                in_panel=below_rows and y<upper_y
            else:in_panel=bounds[pi]<x<bounds[pi+1] and below_rows
            if in_panel:
                # The glyph bounding box may be slightly asymmetric. Calibrate
                # using the actual vector tick, with the glyph supplying value.
                tick_paths=[]
                for td in draws:
                    if len(td['items'])!=1 or td['items'][0][0]!='l':continue
                    p,q=td['items'][0][1:]
                    if abs(p.x-q.x)<.002 and 1<abs(p.y-q.y)<10:
                        if abs(p.x-x)<.5 and abs((p.y+q.y)/2-y)<20:
                            tick_paths.append(p.x)
                if len(tick_paths)==1:x=tick_paths[0]
                elif len(tick_paths)>1:raise ValueError('Ambiguous axis tick calibration')
                else:raise ValueError('No vector tick for printed numeric axis label')
                ticks.append((float(t),x))
        if len(ticks)<2:raise ValueError(f'Panel {pi+1}: only {len(ticks)} usable axis ticks')
        avg_v=statistics.mean(v for v,x in ticks);avg_x=statistics.mean(x for v,x in ticks)
        slope=sum((v-avg_v)*(x-avg_x) for v,x in ticks)/sum((v-avg_v)**2 for v,x in ticks)
        intercept=avg_x-slope*avg_v
        max_axis_residual=max(abs(x-intercept-slope*v) for v,x in ticks)
        if max_axis_residual>.025:raise ValueError(f'Panel {pi+1}: non-linear or misidentified tick positions')
        for marker,(source,term,v) in zip(g,expected[pi]):
            got=[(marker[k]-intercept)/slope for k in ('x','low_x','high_x')]
            want=[v[k] for k in ('estimate','ci95_low','ci95_high')]
            errors=[abs(a-b) for a,b in zip(got,want)]
            checks.append({'source':source,'estimand':term,'expected':want,'pdf_recovered':got,
                           'max_error':max(errors),'passed':max(errors)<.00008})
    return checks,page.get_text(),len(draws)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tex',type=Path,default=ROOT/'deliverables/latex/manuscript.tex')
    ap.add_argument('--figures',type=Path,default=ROOT/'deliverables/latex/figures')
    ap.add_argument('--baseline',type=Path,default=ROOT/'temp/visual_20261013_text_baseline/manuscript.tex')
    ap.add_argument('--stage',default='initial');args=ap.parse_args()
    r=json.loads((ROOT/'results/stats_verified_results.json').read_text(encoding='utf-8'))
    m=json.loads((ROOT/'results/round2_measurement_results.json').read_text(encoding='utf-8'))
    text=args.tex.read_text(encoding='utf-8');tt=tables(text);errors=[];tablecheck=[]
    cp=model(r['CEPS'],'primary_joint');ep=model(r['ECLS'],r['ECLS']['primary_model_label']);fp=model(r['TIMSS']['FIN'],'support_BSBGSSB')
    expected={}
    source=[('CEPS',cp),('ECLS K Grade 8',ep),('TIMSS Finland',fp)]
    names={'ZAF':'South Africa','KOR':'Korea','NOR':'Norway','SWE':'Sweden','POL':'Poland','FRA':'France','DNK':'Denmark','ITA':'Italy'}
    source += [('TIMSS '+names[c],r['TIMSS'][c]['models'][0]) for c in ('ZAF','KOR')]
    source += [('ICCS '+names[c],v['models'][0]) for c,v in r['ICCS'].items()]
    expected['tab1']=[(label,[outnumber(v[k]) for k in ('n','classes','schools')]) for label,v in source]
    expected['tab2']=[]
    for label,v,w,b,dom in [('Joint class perception',cp,'class_within','class_mean','class_support'),('Joint school belonging',cp,'class_school_within','class_school_mean','school_belonging_aggregated_to_class'),('Class items only',model(r['CEPS'],'class_only'),'class_within','class_mean','class_support')]:
        expected['tab2'] += [(label+' '+term,effect(e)) for term,e in zip(('within','between','contextual'),trio(v,w,b,dom))]
    expected['tab3']=[(v['label'],[outnumber(v['n']),outnumber(v['classes'])]+effect(v['contextual_associations']['class_support'])) for v in r['CEPS']['models'] if v['label']!='LOO_conditional_association']
    for v in m['CEPS']['models']:
        domain={'single_classmategood':'classmategood','single_classgood':'classgood','all_ordinal_controls_categorical':'class_support'}[v['label']]
        expected['tab3'].append((v['label'],[outnumber(v['n']),outnumber(v['classes'])]+effect(v['contextual_associations'][domain])))
    expected['tab4']=[]
    for label,v,w,b,dom in [('ECLS K Grade 8',ep,'support_within','support_mean','support'),('TIMSS Finland',fp,'support_within','support_mean','support')]+[('ICCS '+names[c],v['models'][0],'openness_within','openness_mean','class_openness') for c,v in r['ICCS'].items()]:
        expected['tab4'].append((label,[outnumber(v['n'])]+[x for e in trio(v,w,b,dom) for x in effect(e)]))
    for key,rows in expected.items():
        actual=tt[key][1]
        if len(actual)!=len(rows):errors.append(f'{key}: actual row count {len(actual)}, expected {len(rows)}')
        for ri,((label,values),(cells,tokens)) in enumerate(zip(rows,actual),1):
            got=[x for v in tokens for x in v]
            if key=='tab1':got=[x for v in tokens[1:4] for x in v]
            ok=values==got;tablecheck.append((key,ri,label,len(values),ok))
            if not ok:errors.append(f'{key} row {ri} {label}: {got} != {values}')
    current_body=body(text);btext=args.baseline.read_text(encoding='utf-8');baseline_body=body(btext)
    bsha=hashlib.sha256(normalized(baseline_body).encode()).hexdigest()
    if bsha!=INITIAL_NORMALIZED_BODY_HASH:errors.append('Baseline itself differs from independently captured initial normalized body hash')
    body_exact=current_body==baseline_body;body_whitespace=normalized(current_body)==normalized(baseline_body)
    if not body_whitespace:errors.append('Non-figure/table body changed beyond whitespace')
    expect_fig=[]
    for label,v,w,b,dom in [('CEPS',cp,'class_within','class_mean','class_support'),('ECLS K Grade 8',ep,'support_within','support_mean','support'),('TIMSS Finland',fp,'support_within','support_mean','support')]:
        expect_fig.append([(label,term,e) for term,e in zip(('within','between','between minus within'),trio(v,w,b,dom))])
    try:plot_checks,plot_text,draws=pdf_vectors(args.figures/'Figure_2.pdf',expect_fig)
    except Exception as e:errors.append('Figure 2 geometry: '+str(e));plot_checks=[];plot_text='';draws=0
    for p in plot_checks:
        if not p['passed']:errors.append('Figure 2 numerical mismatch: '+p['source']+' '+p['estimand'])
    annotation_text=plot_text.replace('−','-')
    annotations=re.findall(r'([-+]?\d+\.\d{3,4})\s*\[\s*([-+]?\d+\.\d{3,4})\s*,\s*([-+]?\d+\.\d{3,4})\s*\]',annotation_text)
    expected_annotations=[effect(v) for group in expect_fig for source,term,v in group]
    annotations_ok=not annotations or [list(a) for a in annotations]==expected_annotations
    if not annotations_ok:errors.append('Figure 2 printed estimate/CI annotations differ from verified values')
    counts={key:sum(n for t,i,l,n,ok in tablecheck if t==key) for key in expected}
    lines=[f'# Visual numerical review, 13 October 2026: {"PASS" if not errors else "FAIL"}',
           '',f'Stage: {args.stage}; UTC: {datetime.now(timezone.utc).isoformat()}',
           '', 'Read-only audit against the already verified aggregate results. No model was rerun and no production figure, table, prose or data file was modified. Table values were mapped independently to model/sample JSON fields; the figure production code was not imported. PDF marker and interval positions were recovered from vector paths using printed axis tick calibration.',
           '',f'Four tables: {len(tablecheck)} data rows, {sum(counts.values())} numeric values. Figure 2: {len(plot_checks)} marker/CI pairs, {3*len(plot_checks)} independently checked numerical coordinates. Printed estimate/CI annotation groups: {len(annotations)}; annotation equality={annotations_ok}.',
           '', '| Table | Numeric values | Result |','|---|---:|---|']
    for key,n in counts.items():lines.append(f'| {key} | {n} | {"PASS" if all(ok for t,i,l,nn,ok in tablecheck if t==key) else "FAIL"} |')
    lines += ['','## Figure 2 numerical audit','', '| Source | Estimand | Expected estimate | Expected CI lower | Expected CI upper | Maximum vector-derived error | Result |','|---|---|---:|---:|---:|---:|---|']
    for p in plot_checks:lines.append(f'| {p["source"]} | {p["estimand"]} | {p["expected"][0]:.12f} | {p["expected"][1]:.12f} | {p["expected"][2]:.12f} | {p["max_error"]:.9g} | {"PASS" if p["passed"] else "FAIL"} |')
    lines += ['','## Preservation and source identification','',f'- Figure/table-block-excluded document body: exact equality={body_exact}; equality after whitespace normalization={body_whitespace}.',
              f'- Independently captured initial normalized body SHA256: `{INITIAL_NORMALIZED_BODY_HASH}`.',
              '- An external parallel task changed only the abstract at 11:14:24 on 13 October. The parent confirmed this was outside the visual task and instructed preservation of that newest text. The fresh text baseline is therefore temp/visual_20261013_text_baseline/manuscript.tex (51910 bytes; SHA256 ec0969f47284b8a27e6e34a117b855d478360fbd2577a2a4665387439c6dfffe). The earlier 52119-byte baseline remains preserved and was not overwritten.',
              f'- Current manuscript SHA256: `{sha(args.tex)}`.',f'- Verified results SHA256: `{sha(ROOT/"results/stats_verified_results.json")}`.',
              f'- Round-two measurement results SHA256: `{sha(ROOT/"results/round2_measurement_results.json")}`.']
    for f in ('Figure_1.pdf','Figure_2.pdf'):lines.append(f'- {f} SHA256: `{sha(args.figures/f)}`.')
    lines += ['','## Numerical or label risks','']
    lines += ['- '+x for x in errors] if errors else ['No numerical discrepancy was found. Visual and semantic labels must also be inspected from the final native PDF renders before declaring final completion.']
    lines += ['','The primary CEPS joint model is the source for its panel. ECLS uses official C7SDQINT with the C7PW0/90 JK2 primary intervals; TIMSS Finland uses support_BSBGSSB with its 150-replicate JRR intervals. These source-specific raw units must remain in the panel labels and separate axes. The contextual point is the same-model between-minus-within estimate; no LOO coefficient belongs in this figure. Table 3 additionally depends on round2_measurement_results.json for its three measurement/categorical-control rows.']
    (ROOT/'results/visual_20261013_numeric_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'errors':errors,'table_rows':len(tablecheck),'table_numeric_values':sum(counts.values()),'plot_pairs':len(plot_checks),
                      'plot_max_error':max((p['max_error'] for p in plot_checks),default=None),'body_exact':body_exact,'body_whitespace':body_whitespace},indent=2))
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
