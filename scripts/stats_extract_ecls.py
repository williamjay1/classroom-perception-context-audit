"""Extract ECLS-K Grade8 fields and genuine full/replicate survey weights.

Read-only input catalog. Output is PRIVATE case-level working data on D:.
Do not include this output in any public revision/archive package.
The provider raw catalog has explicit decimal marks; float parsing preserves
those values, consistent with its supplied SPSS decimal formats.
"""
import argparse,json,re,hashlib
from pathlib import Path
import numpy as np
import pandas as pd

DEFAULT_RAW=Path(r'F:\AcademicData\BMC_Classroom_Revision\raw\eclsk\childk8p.dat')
DEFAULT_SYNTAX=Path(r'F:\AcademicData\BMC_Classroom_Revision\raw\eclsk\ECLSK_Kto8_child_SPSS.sps')
DEFAULT_OUT=Path(r'D:\MLWork\BMC_Classroom_Revision_Reproduction\datasets\ecls_grade8_survey_extract.csv')
SUPPORT=['C7CLSFR','C7CLSLIK','C7CLSFEL','C7CLSOTH','C7CLSCAR']
OUTCOME=['C7LONLY','C7SAD','C7NOCNTR','C7USELES','C7NOGOOD']
SDQ_ITEMS=['C7ANGRY','C7WRYTST','C7LONLY','C7SAD','C7WRYWEL','C7WRYFIN','C7WRYHNG','C7ASHAME']
WEIGHTS=['C7CW0','C7PW0']+[f'C7CW{i}' for i in range(1,91)]+[f'C7PW{i}' for i in range(1,91)]
FIELDS=['GENDER','CHILDID','S7_ID','J71CLASS','J72CLASS','C5SDQINR','W8SESL',*SUPPORT,*OUTCOME,'C7SDQINT',*SDQ_ITEMS,*WEIGHTS]
FIELDS=list(dict.fromkeys(FIELDS))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--child-file',type=Path,default=DEFAULT_RAW);p.add_argument('--syntax-file',type=Path,default=DEFAULT_SYNTAX);p.add_argument('--output',type=Path,default=DEFAULT_OUT)
    p.add_argument('--reference-extract',type=Path,help='Optional original private extract for matched numerical verification; never redistributed.')
    p.add_argument('--audit-output',type=Path,default=Path(r'D:\MLWork\BMC_Classroom_Revision_Reproduction\results\stats_ecls_survey_extraction_audit.json'))
    args=p.parse_args()
    if args.output.exists():raise FileExistsError('Use a new output version; existing derived extract is preserved.')
    rec=0;loc={}
    for line in args.syntax_file.read_text(encoding='utf-8',errors='replace').splitlines():
        m=re.match(r'^/(\d+)$',line.strip())
        if m:rec=int(m.group(1))
        m=re.match(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s+(\d+)-(\d+)',line)
        if m and m.group(1) in FIELDS:loc[m.group(1)]=(rec,int(m.group(2)),int(m.group(3)))
    if set(FIELDS)-set(loc):raise ValueError(f'Missing syntax fields: {set(FIELDS)-set(loc)}')
    rows=[]
    with args.child_file.open('rb') as fh:
        while True:
            first=fh.readline()
            if not first:break
            block=[first.rstrip(b'\r\n')]+[fh.readline().rstrip(b'\r\n') for _ in range(14)]
            row={}
            for name,(r,s,e) in loc.items():
                v=block[r-1][s-1:e].decode('ascii').strip()
                if not v:row[name]=np.nan
                elif name in ['CHILDID','S7_ID','J71CLASS','J72CLASS']:row[name]=v if v not in ['-1','-7','-8','-9'] else np.nan
                else:
                    val=float(v)
                    # SES is standardized and its ordinary negative values
                    # are VALID. Only its provider missing codes are removed.
                    if name=='W8SESL':row[name]=val if val not in [-7,-8,-9] else np.nan
                    else:row[name]=val if val>=0 else np.nan
            rows.append(row)
    d=pd.DataFrame(rows);d=d.rename(columns={'S7_ID':'school_key','C5SDQINR':'prior_internalizing'})
    for c in SUPPORT:d[c]=d[c].where(d[c].between(1,5))
    for c in set(OUTCOME+SDQ_ITEMS):d[c]=d[c].where(d[c].between(1,4))
    d['C7SDQINT']=d.C7SDQINT.where(d.C7SDQINT.between(1,4))
    d['GENDER']=d.GENDER.where(d.GENDER.isin([1,2]))
    d['classmate_support_score']=d[SUPPORT].mean(axis=1).where(d[SUPPORT].notna().sum(axis=1)>=4)
    d['internalizing_score']=d[OUTCOME].mean(axis=1).where(d[OUTCOME].notna().sum(axis=1)>=4)
    args.output.parent.mkdir(parents=True,exist_ok=True);d.to_csv(args.output,index=False)
    report={'rows':len(d),'distinct_CHILDID':d.CHILDID.nunique(),'syntax_sha256':hashlib.sha256(args.syntax_file.read_bytes()).hexdigest(),'syntax_source':str(args.syntax_file),'private_output':str(args.output),'variables_and_locators':loc,
        'genuine_sampling_weight':'C7PW0 current parent+child survey weight; C7CW0 child-only sensitivity','replicate_weights_per_family':90,
        'C7CW0_valid_positive_n':int((d.C7CW0>0).sum()),'C7PW0_valid_positive_n':int((d.C7PW0>0).sum()),
        'C7SDQINT_valid_n':int(d.C7SDQINT.notna().sum()),'official_SDQ_items':SDQ_ITEMS,'official_SDQ_score_rule':'Read provider composite directly; valid1–4; negative missing codes removed; no invented minimum-item rule','official_SDQ_complete8_n':int(d[SDQ_ITEMS].notna().all(axis=1).sum()),'official_SDQ_vs_complete8_mean_max_abs_difference':float((d.loc[d[SDQ_ITEMS].notna().all(axis=1),'C7SDQINT']-d.loc[d[SDQ_ITEMS].notna().all(axis=1),SDQ_ITEMS].mean(axis=1)).abs().max()),
        'W8SESL_valid_n':int(d.W8SESL.notna().sum()),'W8SESL_valid_negative_n':int((d.W8SESL<0).sum()),
        'W8SESL_missing_codes':[-7,-8,-9],
        'weight_quantiles':d.loc[d.C7CW0>0,'C7CW0'].quantile([0,.25,.5,.75,1]).to_dict()}
    if args.reference_extract:
        old=pd.read_csv(args.reference_extract);merged=d.merge(old,on='CHILDID',suffixes=('_new','_old'),validate='one_to_one')
        report['old_extract_comparison']={c:{'common_valid_n':int(merged[[c+'_new',c+'_old']].dropna().shape[0]),'max_abs_numeric_difference':float((merged[c+'_new']-merged[c+'_old']).abs().max())} for c in ['classmate_support_score','internalizing_score','prior_internalizing','W8SESL']}
    args.audit_output.parent.mkdir(parents=True,exist_ok=True)
    args.audit_output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'rows':len(d),'weight_valid':report['C7CW0_valid_positive_n'],'comparison':report.get('old_extract_comparison','not requested')},indent=2))
if __name__=='__main__':main()
