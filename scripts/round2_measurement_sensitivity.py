"""Fixed-design, reviewer-driven measurement/ordinal-adjustment sensitivities.
All choices were selected before their new results. Main results are preserved.
No source data are modified. Outputs contain aggregate coefficients only.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
import stats_reanalysis as a

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,default=a.OLD)
    p.add_argument('--output-dir',type=Path,default=a.OUT)
    p.add_argument('--source-config',type=Path)
    args=p.parse_args();a.OLD=args.project_root.resolve();a.OUT=args.output_dir.resolve()
    a.SOURCES={'ceps':a.OLD/'data_audit/ceps/CEPS_baseline_pooled.dta','ecls':a.OLD/'data_audit/eclsk/eclsk_grade8_extract.csv','timss_root':a.OLD.parent/'data/processed/timss2019','iccs_root':a.OLD.parent/'data/raw/iccs2022/extracted/ICCS2022_IDB_SPSS/Data'}
    if args.source_config:a.SOURCES.update({k:Path(v).resolve() for k,v in json.loads(args.source_config.read_text('utf-8')).items()})
    d,f=a.load_ceps();ceps=[]
    pool=d.loc[d.class_score.notna()].copy()
    for item in ['classmategood','classgood']:
        a.group_scores(pool,item,'class_key','item')
        sub=f.copy();sub['item_within']=pool.loc[sub.index,'item_within'];sub['item_mean']=pool.loc[sub.index,'item_mean']
        assert len(sub)==len(f) and sub[['item_within','item_mean']].notna().all().all()
        pairs={item:('item_within','item_mean'),'school_belonging_aggregated_to_class':a.CEPS_PAIRS['school_belonging_aggregated_to_class']}
        formula='distress_score ~ item_within + item_mean + class_school_within + class_school_mean + '+a.CEPS_CONTROLS+' + C(school_key)'
        r,_=a.formula_fit(sub,formula,'sweight',pairs,label='single_'+item)
        r['paired_terms']=pairs;r['predictor']=item;r['reporter_pool_rule']='Use the exact two-item-complete source reporter pool from the primary class-score definition, then form item-specific means; main analytic sample held fixed.'
        r['reporter_pool']=a.summary(pool);ceps.append(r)
    ordinal='C(gender)+C(grade9)+C(migrant_status)+'+'+'.join('C('+k+')' for k in ['health','expectstress_p','income5','medu','fedu'])
    formula='distress_score ~ class_within + class_mean + class_school_within + class_school_mean + '+ordinal+' + C(school_key)'
    r,_=a.formula_fit(f,formula,'sweight',a.CEPS_PAIRS,label='all_ordinal_controls_categorical');ceps.append(r)
    e=pd.read_csv(a.SOURCES['ecls'],dtype={'school_key':'string','J71CLASS':'string'}).dropna(subset=['school_key','J71CLASS']).copy()
    e['class_key']=e.school_key+':'+e.J71CLASS;e['C7SDQINT']=e.C7SDQINT.where(e.C7SDQINT.between(1,4));a.group_scores(e,'classmate_support_score','class_key','support')
    main=e.loc[e.support_n>=5].dropna(subset=['classmate_support_score','C7SDQINT','prior_internalizing','W8SESL']);main=main.loc[main.C7PW0>0]
    common=main.dropna(subset=['internalizing_score']).copy()
    cols=['support_within','support_mean','prior_internalizing','W8SESL'];pairs={'support':('support_within','support_mean')}
    ecls=[]
    for outcome,label in [('C7SDQINT','official_internalizing_common_sample'),('internalizing_score','historical_mixed5_common_sample')]:
        r=a.replicate_fit(common,outcome,cols,'C7PW0',pairs,[common['C7PW'+str(i)].to_numpy(float) for i in range(1,91)],1,False,label)
        r['paired_terms']=pairs;r['outcome_variable']=outcome;r['raw_units']='Raw outcome points per 1 support point; outcome content differs and coefficient differences are not a test of validity';ecls.append(r)
    for m in ceps+ecls:
        for domain,ct in m['contextual_associations'].items():
            W,B=m.get('paired_terms',a.CEPS_PAIRS)[domain]
            assert abs(ct['estimate']-(m['terms'][B]['estimate']-m['terms'][W]['estimate']))<1e-10
    result={'decision_date':'2026-10-07','status':'Exploratory fixed-design measurement sensitivities; not preregistered; choices made before inspecting these results','CEPS':{'fixed_primary_sample':a.summary(f),'models':ceps},'ECLS':{'official_primary_sample':a.summary(main),'common_outcome_sample':a.summary(common),'official_sample_without_mixed_score_n':int(len(main)-len(common)),'models':ecls,'block_decision':'Separate two-SDQ/three-NELS block regressions omitted: provider-complete scale plus same-sample original composite is the direct and bounded measurement comparison.'},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.OUT.mkdir(parents=True,exist_ok=True);(a.OUT/'round2_measurement_results.json').write_text(json.dumps(result,indent=2),'utf-8')
    rows=[]
    for source in ['CEPS','ECLS']:
        for m in result[source]['models']:
            for domain,ct in m['contextual_associations'].items():
                if source=='ECLS':W,B='support_within','support_mean'
                elif domain=='class_support':W,B='class_within','class_mean'
                elif domain=='school_belonging_aggregated_to_class':W,B='class_school_within','class_school_mean'
                else:W,B='item_within','item_mean'
                for kind,x in [('within',m['terms'][W]),('between',m['terms'][B]),('contextual',ct)]:rows.append({'source':source,'model':m['label'],'domain':domain,'measure':kind,'n':m['n'],'classes':m['classes'],'schools':m['schools'],**x})
    pd.DataFrame(rows).to_csv(a.OUT/'round2_measurement_coefficients.csv',index=False)
    print(json.dumps({s:{m['label']:m['contextual_associations'] for m in result[s]['models']} for s in ['CEPS','ECLS']},indent=2))
if __name__=='__main__':main()
