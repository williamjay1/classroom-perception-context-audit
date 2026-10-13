"""Independent arithmetic, reparameterization and provider-label audit."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys
sys.dont_write_bytecode=True
import json,argparse
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import pyreadstat
import stats_reanalysis as a

checks=[]
def record(label,value,tolerance=1e-9):
    checks.append({'check':label,'absolute_error':float(abs(value)),'tolerance':tolerance,'pass':bool(abs(value)<tolerance)})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=a.OLD);p.add_argument('--output-dir',type=Path,default=a.OUT);p.add_argument('--source-config',type=Path);args=p.parse_args()
    a.OLD=args.project_root.resolve();a.OUT=args.output_dir.resolve()
    a.SOURCES={'ceps':a.OLD/'data_audit/ceps/CEPS_baseline_pooled.dta','ecls':a.OLD/'data_audit/eclsk/eclsk_grade8_extract.csv','timss_root':a.OLD.parent/'data/processed/timss2019','iccs_root':a.OLD.parent/'data/raw/iccs2022/extracted/ICCS2022_IDB_SPSS/Data'}
    if args.source_config:a.SOURCES.update({k:Path(v).resolve() for k,v in json.loads(args.source_config.read_text(encoding='utf-8')).items()})
    p=a.OUT/'stats_verified_results.json';r=json.loads(p.read_text(encoding='utf-8'))
    for src in ['CEPS','ECLS']:
        models=r[src]['models']
        for m in models:
            for dom,ct in m.get('contextual_associations',{}).items():
                W,B={'class_support':('class_within','class_mean'),'school_belonging_aggregated_to_class':('class_school_within','class_school_mean'),'support':('support_within','support_mean')}[dom]
                record(f'{src}/{m["label"]}/{dom}: B-W arithmetic',ct['estimate']-(m['terms'][B]['estimate']-m['terms'][W]['estimate']))
    for src in ['TIMSS','ICCS']:
        for country,v in r[src].items():
            for m in v['models']:
                for dom,ct in m['contextual_associations'].items():
                    W,B={'support':('support_within','support_mean'),'disorder':('disorder_within','disorder_mean'),'class_openness':('openness_within','openness_mean'),'school_safety':('safety_within','safety_mean')}[dom]
                    record(f'{src}/{country}/{m["label"]}/{dom}: B-W arithmetic',ct['estimate']-(m['terms'][B]['estimate']-m['terms'][W]['estimate']))
    pool,f=a.load_ceps()
    labels_ceps=pd.io.stata.StataReader(a.SOURCES['ceps']).value_labels().get('gender',{})
    record('CEPS source labels 0male/1female',0 if labels_ceps.get(0)=='male' and labels_ceps.get(1)=='female' else 1)
    record('CEPS includes both valid sex codes',0 if set(f.gender.unique())=={0,1} else 1)
    record('CEPS source and fitted sample counts agree',len(f)-r['CEPS']['sample']['n'])
    record('CEPS education valid category ranges',0 if f.medu.between(1,9).all() and f.fedu.between(1,9).all() else 1)
    record('CEPS migrant category ranges',0 if f.migrant_status.isin([1,2,3]).all() else 1)
    e=pd.read_csv(a.SOURCES['ecls'],dtype={'school_key':'string','J71CLASS':'string'}).dropna(subset=['school_key','J71CLASS']).copy()
    e['class_key']=e.school_key+':'+e.J71CLASS;a.group_scores(e,'classmate_support_score','class_key','support')
    ef=e.loc[e.support_n>=5].dropna(subset=['classmate_support_score','C7SDQINT','prior_internalizing','W8SESL']);ef=ef.loc[ef.C7PW0>0]
    record('ECLS official composite range1–4',0 if ef.C7SDQINT.between(1,4).all() else 1)
    record('ECLS official main eligible sample count',len(ef)-r['ECLS']['sample']['n'])
    record('ECLS primary outcome and proper parent weight',0 if r['ECLS']['outcome_variable']=='C7SDQINT' and r['ECLS']['primary_model_label']=='weighted_C7PW0_JK2' else 1)
    # Distinct parameterization using own score + full mean yields same fits and contextual coefficient.
    conventional=a.CEPS_FORM+' + C(school_key)'
    rawown='distress_score ~ class_score + class_mean + school_score + class_school_mean + '+a.CEPS_CONTROLS+' + C(school_key)'
    x=smf.wls(conventional,f,weights=f.sweight).fit()
    y=smf.wls(rawown,f,weights=f.sweight).fit()
    record('CEPS full mean vs within/between fitted values',np.max(abs(x.fittedvalues-y.fittedvalues)),1e-8)
    record('CEPS equivalent full-mean contextual coefficient',y.params.class_mean-(x.params.class_mean-x.params.class_within))
    record('CEPS equivalent school-item class-mean contextual coefficient',y.params.class_school_mean-(x.params.class_school_mean-x.params.class_school_within))
    # LOO identity across all unequal sampled class sizes is exact.
    record('LOO algebra mean - within/(n-1)',np.max(abs(f.class_loo-(f.class_mean-f.class_within/(f.class_n-1)))),1e-12)
    old=r['CEPS']['old_numerical_provenance'];b=old['model_specific_coefficients']
    record('Old joint model -0.125535 arithmetic',old['own_minus_class_aggregate']-(b['z_class_score']-b['z_class_loo']))
    record('Old joint model 0.026672 arithmetic',old['class_aggregate_minus_school_item_class_aggregate']-(b['z_class_loo']-b['z_class_school_loo']))
    labels={}
    for kind,path,cols in [
       ('TIMSS',a.SOURCES['timss_root']/'FIN/bsgfinm7.sav',['BSBM17A','BSBM18A','BSBGSSB','BSBGSB']),
       ('ICCS',a.SOURCES['iccs_root']/'ISGNORC4.sav',['IS4G16A','IS4G18H','IS4G18I'])]:
        _,meta=pyreadstat.read_sav(path,metadataonly=True)
        labels[kind]={c:{'label':meta.column_names_to_labels[c],'value_labels':meta.variable_value_labels.get(c)} for c in cols}
    out={'checks':checks,'all_passed':all(c['pass'] for c in checks),'provider_label_audit':labels}
    (a.OUT/'stats_independent_checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(checks),'all_passed':out['all_passed']},indent=2))
    if not out['all_passed']:raise ValueError('Numerical verification failed')
if __name__=='__main__':main()
