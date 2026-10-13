"""Reviewer-driven reanalysis. All outputs are aggregate summaries on D:.

Raw construct units are shared by individual deviations and group means.
All models/contrasts are selected to correct the centering error, not on results.
No source data are overwritten. No inference of psychometric equivalence is made.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import sys
sys.dont_write_bytecode = True
import json, hashlib, argparse
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.formula.api as smf
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT
OUT = Path(r'D:\MLWork\BMC_Classroom_Revision_Reproduction\results') if os.name=='nt' else ROOT/'reproduced_results'
SOURCES = {
    'ceps':OLD/'data_audit/ceps/CEPS_baseline_pooled.dta',
    'ecls':OLD/'data_audit/eclsk/eclsk_grade8_extract.csv',
    'timss_root':OLD.parent/'data/processed/timss2019',
    'iccs_root':OLD.parent/'data/raw/iccs2022/extracted/ICCS2022_IDB_SPSS/Data',
}
DISTRESS = ['depressed','blue','unhappy','pessimistic','sad']
SEED = 20261005

def summary(f):
    return {'n':int(len(f)), 'classes':int(f.class_key.nunique()), 'schools':int(f.school_key.nunique()),
            'schools_multiple_classes':int((f.groupby('school_key').class_key.nunique()>1).sum())}

def descriptive(f,cols):
    return {c:{'valid_n':int(f[c].notna().sum()),'mean':float(f[c].mean()),'sd':float(f[c].std(ddof=1)),'minimum':float(f[c].min()),'maximum':float(f[c].max())} for c in cols}

def alpha(f,cols):
    x=f[cols].apply(pd.to_numeric,errors='coerce').dropna()
    k=len(cols)
    return {'n':int(len(x)), 'k':k, 'alpha':float(k/(k-1)*(1-x.var(ddof=1).sum()/x.sum(axis=1).var(ddof=1)))}

def agreement(f,score,group='class_key'):
    d=f[[group,score]].dropna(); g=d.groupby(group)[score]
    n=g.size(); means=g.mean(); N=len(d); J=len(n)
    if J<2 or N<=J: return {'n':N,'groups':J}
    msb=float((n*(means-d[score].mean())**2).sum()/(J-1))
    msw=float(((d[score]-d[group].map(means))**2).sum()/(N-J))
    # Unequal-size one-way ANOVA effective cluster size, versus old arithmetic nbar.
    n0=float((N-(n.pow(2).sum()/N))/(J-1))
    icc=(msb-msw)/(msb+(n0-1)*msw)
    nbar=float(n.mean())
    return {'n':N,'groups':J,'arithmetic_mean_n':nbar,'effective_n0':n0,
            'reporters_min':int(n.min()),'reporters_max':int(n.max()),
            'icc1_anova':float(icc), 'icc2_at_arithmetic_mean_n':float(nbar*icc/(1+(nbar-1)*icc)),
            'icc2_at_effective_n0':float(n0*icc/(1+(n0-1)*icc)),
            'icc2_min_reporters':float(n.min()*icc/(1+(n.min()-1)*icc)),
            'icc2_max_reporters':float(n.max()*icc/(1+(n.max()-1)*icc)),
            'unweighted_descriptive':True}

def group_scores(f,score,group,prefix):
    s=f.groupby(group)[score].transform('mean'); n=f.groupby(group)[score].transform('count')
    f[prefix+'_mean']=s; f[prefix+'_n']=n
    f[prefix+'_within']=f[score]-s
    f[prefix+'_loo']=(s*n-f[score])/(n-1)
    f.loc[n<=1,prefix+'_loo']=np.nan

def effect(b,c,vec,df=None):
    v=np.asarray(vec,float); e=float(v@b); se=float(np.sqrt(max(0,v@c@v)))
    q=float(st.t.ppf(.975,df)) if df else 1.959963984540054
    p=float(2*(st.t.sf(abs(e/se),df) if df else st.norm.sf(abs(e/se)))) if se else None
    return {'estimate':e,'se':se,'ci95_low':e-q*se,'ci95_high':e+q*se,'p_two_sided':p}

def pack(b,c,names,pairs,df=None):
    r={'terms':{},'contextual_associations':{}}
    for name in [n for pair in pairs.values() for n in pair]:
        v=np.zeros(len(names)); v[names.index(name)]=1
        r['terms'][name]=effect(b,c,v,df)
    for domain,(W,B) in pairs.items():
        v=np.zeros(len(names));v[names.index(B)]=1;v[names.index(W)]=-1
        r['contextual_associations'][domain]=effect(b,c,v,df)
    return r

def formula_fit(f,formula,weight,pairs,cluster='school_key',label=''):
    w=f[weight] if weight else np.ones(len(f))
    fit=smf.wls(formula,data=f,weights=w).fit(cov_type='cluster',cov_kwds={'groups':f[cluster],'use_correction':True},use_t=True)
    names=list(fit.params.index);b=fit.params.to_numpy();c=fit.cov_params().to_numpy()
    G=int(f[cluster].nunique())
    r={'label':label,'formula':formula,'weight':weight or 'none','uncertainty':f'{cluster} cluster sandwich, finite sample correction, t(G-1)','clusters':G,'df':G-1,**summary(f),
       'outcome_sd_in_model_sample':float(f[formula.split('~')[0].strip()].std(ddof=0)),
       'r_squared':float(fit.rsquared),'rank':int(np.linalg.matrix_rank(fit.model.exog)),
       'columns':len(names),**pack(b,c,names,pairs,G-1)}
    r['residual_quantiles']=dict(zip(['min','q01','q25','median','q75','q99','max'],map(float,np.quantile(fit.resid,[0,.01,.25,.5,.75,.99,1]))))
    return r,fit

def solve(x,y,w,fe=None):
    ok=np.isfinite(w)&(w>0)
    xp=x[ok].copy();yp=y[ok].copy();wp=w[ok]
    if fe is not None:
        codes=fe[ok]; denom=np.bincount(codes,weights=wp,minlength=int(fe.max()+1));safe=np.where(denom>0,denom,1)
        ym=np.bincount(codes,weights=wp*yp,minlength=len(safe))/safe
        yp-=ym[codes]
        for j in range(xp.shape[1]):
            xm=np.bincount(codes,weights=wp*xp[:,j],minlength=len(safe))/safe
            xp[:,j]-=xm[codes]
    root=np.sqrt(wp); b,_,rank,_=np.linalg.lstsq(xp*root[:,None],yp*root,rcond=None)
    if rank<x.shape[1]: raise ValueError(f'Signal design rank {rank} < {x.shape[1]}')
    return b

def replicate_fit(f,outcome,cols,weight,pairs,repweights,factor,fe=False,label=''):
    names=cols if fe else ['Intercept']+cols
    x=f[cols].to_numpy(float)
    if not fe:x=np.column_stack([np.ones(len(f)),x])
    y=f[outcome].to_numpy(float);w=f[weight].to_numpy(float)
    fecodes=pd.factorize(f.school_key)[0] if fe else None
    b=solve(x,y,w,fecodes)
    reps=np.asarray([solve(x,y,rw,fecodes) for rw in repweights])
    diff=reps-b;c=factor*diff.T@diff
    return {'label':label,'formula':outcome+' ~ '+' + '.join(cols)+(' + school fixed effects' if fe else ''),
            'weight':weight,'school_fixed_effects':fe,**summary(f),'replicates':len(reps),'variance_factor':factor,
            'outcome_sd_in_model_sample':float(f[outcome].std(ddof=0)),
            'uncertainty':'design based jackknife, normal 95% intervals',**pack(b,c,names,pairs),
            'model_columns':names,'coefficient_covariance':c.tolist()}

def load_ceps(minclass=2,mindistress=5,historical_gender_rule=False):
    d=pd.read_stata(SOURCES['ceps'],convert_categoricals=False)
    source_rows=int(len(d)); positive_ids=int((d.ids>0).sum())
    d=d.loc[(d.ids>0)&d.grade9.isin([0,1]) & d.schids.between(1,112)&d.clsids.between(1,438)].copy()
    eligible_rows=int(len(d))
    fields=['sweight','gender','grade9','classmategood','classgood','friendly',*DISTRESS,'health','expectstress_p','income5','medu','fedu','migrant_status','schids','clsids']
    conflicts=d.groupby('ids')[fields].nunique(dropna=True).gt(1).any(axis=1)
    if conflicts.any():raise ValueError('Conflicting eligible CEPS duplicate records; inspect provider input')
    d=d.drop_duplicates('ids').copy()
    flow={'input_records':source_rows,'positive_ID_records':positive_ids,'valid_ID_school_class_grade_records_before_deduplication':eligible_rows,'source_valid_identifier_records_after_deduplication':int(len(d)),'conflicting_eligible_duplicate_IDs':int(conflicts.sum())}
    for col in ['classmategood','classgood','friendly']:d[col]=pd.to_numeric(d[col],errors='coerce').where(d[col].between(1,4))
    for col in DISTRESS:d[col]=pd.to_numeric(d[col],errors='coerce').where(d[col].between(1,5))
    for col,lo,hi in [('health',1,5),('expectstress_p',1,5),('income5',1,5),('medu',1,9),('fedu',1,9)]:d[col]=pd.to_numeric(d[col],errors='coerce').where(d[col].between(lo,hi))
    d['gender']=d.gender.where(d.gender.isin([1,2] if historical_gender_rule else [0,1]));d['migrant_status']=d.migrant_status.where(d.migrant_status.isin([1,2,3]))
    d['class_key']=d.clsids.astype(str);d['school_key']=d.schids.astype(str)
    d['class_score']=d[['classmategood','classgood']].mean(axis=1).where(d[['classmategood','classgood']].notna().sum(axis=1)>=minclass)
    d['school_score']=d.friendly
    d['distress_score']=d[DISTRESS].mean(axis=1).where(d[DISTRESS].notna().sum(axis=1)>=mindistress)
    group_scores(d,'class_score','class_key','class');group_scores(d,'school_score','class_key','class_school')
    for col in ['class_score','school_score','class_loo','class_school_loo','distress_score','health','expectstress_p','income5','medu','fedu']:
        d['z_'+col]=(d[col]-d[col].mean())/d[col].std(ddof=0)
    req=['distress_score','sweight','class_score','class_loo','school_score','class_school_loo','health','expectstress_p','income5','medu','fedu','gender','grade9','migrant_status']
    f=d.dropna(subset=req).loc[lambda a:a.sweight>0].copy()
    d.attrs['sample_flow']={**flow,'valid_class_score_reporters':int(d.class_score.notna().sum()),'complete_case_records':int(len(f)),'missing_by_required_variable_overlapping':{k:int(d[k].isna().sum()) for k in req}}
    return d,f

CEPS_CONTROLS='C(gender) + C(grade9) + health + expectstress_p + income5 + medu + fedu + C(migrant_status)'
CEPS_PAIRS={'class_support':('class_within','class_mean'),'school_belonging_aggregated_to_class':('class_school_within','class_school_mean')}
CEPS_FORM='distress_score ~ class_within + class_mean + class_school_within + class_school_mean + '+CEPS_CONTROLS

def ceps():
    d,f=load_ceps();models=[]
    for label,w,fe,cluster in [('primary_joint', 'sweight',True,'school_key'),('class_cluster_sensitivity','sweight',True,'class_key'),('unweighted',None,True,'school_key'),('no_school_FE','sweight',False,'school_key')]:
        r,_=formula_fit(f,CEPS_FORM+(' + C(school_key)' if fe else ''),w,CEPS_PAIRS,cluster,label);models.append(r)
    classonly='distress_score ~ class_within + class_mean + '+CEPS_CONTROLS+' + C(school_key)'
    r,_=formula_fit(f,classonly,'sweight',{'class_support':CEPS_PAIRS['class_support']},label='class_only');models.append(r)
    for threshold in [10,20,30]:
        sub=f.loc[(f.class_n>=threshold)&(f.class_school_n>=threshold)].copy()
        r,_=formula_fit(sub,CEPS_FORM+' + C(school_key)','sweight',CEPS_PAIRS,label=f'minimum_{threshold}_reporters');models.append(r)
    for mc,md,label in [(1,5,'one_of_two_class_items'),(2,4,'four_of_five_distress_items')]:
        _,sub=load_ceps(mc,md);r,_=formula_fit(sub,CEPS_FORM+' + C(school_key)','sweight',CEPS_PAIRS,label=label);models.append(r)
    q25=float(f.class_n.quantile(.25));q75=float(f.class_n.quantile(.75))
    for name,mask in [('lower',f.class_n<=q25),('middle',(f.class_n>q25)&(f.class_n<q75)),('upper',f.class_n>=q75)]:
        sub=f.loc[mask].copy();r,_=formula_fit(sub,CEPS_FORM+' + C(school_key)','sweight',CEPS_PAIRS,label=f'class_size_{name}')
        r['reporter_min']=int(sub.class_n.min());r['reporter_max']=int(sub.class_n.max());models.append(r)
    # LOO sensitivity uses raw units and is NOT a within/between contrast.
    loo='distress_score ~ class_score + class_loo + school_score + class_school_loo + '+CEPS_CONTROLS+' + C(school_key)'
    r,fit=formula_fit(f,loo,'sweight',{},label='LOO_conditional_association')
    r['terms']={t:effect(fit.params.to_numpy(),fit.cov_params().to_numpy(),np.eye(len(fit.params))[list(fit.params.index).index(t)],111) for t in ['class_score','class_loo','school_score','class_school_loo']};models.append(r)
    # Exact reproduction of the old z-scale model, including its class-cluster normal CI.
    oldctrl='C(school_key) + C(gender) + C(grade9) + z_health + z_expectstress_p + z_income5 + z_medu + z_fedu + C(migrant_status)'
    oldform='z_distress_score ~ z_class_score + z_class_loo + z_school_score + z_class_school_loo + '+oldctrl
    old_d,old_f=load_ceps(historical_gender_rule=True)
    fit=smf.wls(oldform,old_f,weights=old_f.sweight).fit(cov_type='cluster',cov_kwds={'groups':old_f.class_key,'use_correction':True})
    oldterms={t:float(fit.params[t]) for t in ['z_class_score','z_class_loo','z_school_score','z_class_school_loo']}
    provenance={'historical_sample':summary(old_f),'historical_gender_error':'Gender 0=male/1=female; erroneous 1/2 validity rule excluded all males. Old model reproduced only to trace withdrawn submitted numbers.','old_additive_joint_formula':oldform,'model_specific_coefficients':oldterms,
                'own_minus_class_aggregate':float(fit.params.z_class_score-fit.params.z_class_loo),
                'class_aggregate_minus_school_item_class_aggregate':float(fit.params.z_class_loo-fit.params.z_class_school_loo),
                'old_interaction_model_source':'data_audit/ceps/ceps_redesign_tests.json',
                'old_interaction_coefficients':json.loads((OLD/'data_audit/ceps/ceps_redesign_tests.json').read_text())['models'],
                'old_standardization_sd_precomplete':{c:float(old_d[c].std(ddof=0)) for c in ['class_score','class_loo','school_score','class_school_loo','distress_score']}}
    rep=d.loc[d.class_key.isin(f.class_key.unique())].dropna(subset=['class_score'])
    return {'sample':summary(f),'sample_flow':d.attrs['sample_flow'],'source_cleaning':{'gender_valid_codes':{'0':'male','1':'female'},'duplicate_rule':'Filter valid ID/school/class/grade rows before deduplication; assert no model-field conflict within eligible IDs.','education_valid_codes':'1–9 ordered categories, not years','migrant_valid_codes':[1,2,3],'historical_gender_error':'Original 1/2 filter excluded all male0 respondents; corrected before current analysis.'},'participant_description':{'gender_counts':{('male' if k==0 else 'female'):int(v) for k,v in f.gender.value_counts().items()},'grade_counts':{('grade7' if k==0 else 'grade9'):int(v) for k,v in f.grade9.value_counts().items()},'age_years':{'valid_n':int(f.age.notna().sum()),'mean':float(f.age.mean()),'sd':float(f.age.std(ddof=1)),'minimum':float(f.age.min()),'maximum':float(f.age.max())},'core_scores':descriptive(f,['class_score','school_score','distress_score']),'control_coding':{'categorical':['gender0male1female','grade9:0grade7/1grade9','migrant_status1–3'],'linear':['health1poor–5good','expectstress_p1none–5high','income5:1poor–5rich','medu1–9 education categories','fedu1–9 education categories']}},'outcome':'mean of five negative affect items, 1–5; larger=more negative affect',
            'predictor':'mean classmategood/classgood 1–4; larger=more favorable class rating; secondary friendly school-belonging 1–4',
            'outcome_sd_reference':float(f.distress_score.std(ddof=0)),
            'class_size_cutpoints':{'q25':q25,'q75':q75},'reliability':{'class_alpha':alpha(f,['classmategood','classgood']),'outcome_alpha':alpha(f,DISTRESS),
            'all_context_reporters_in_modeled_classes':agreement(rep,'class_score'),'final_model_complete_cases':agreement(f,'class_score'),'outcome_complete_cases':agreement(f,'distress_score')},
            'reporter_pool':summary(rep),'models':models,'old_numerical_provenance':provenance}

def ecls():
    d=pd.read_csv(SOURCES['ecls'],dtype={'school_key':'string','J71CLASS':'string'})
    source_n=int(len(d))
    d=d.dropna(subset=['school_key','J71CLASS']).copy()
    d['class_key']=d.school_key+':'+d.J71CLASS
    candidates=['C7PW0','C7CW0',*['C7PW'+str(i) for i in range(1,91)],*['C7CW'+str(i) for i in range(1,91)]]
    for c in ['W8SESL','prior_internalizing','C7SDQINT','internalizing_score','classmate_support_score']+[c for c in candidates if c in d.columns]:d[c]=pd.to_numeric(d[c],errors='coerce')
    if 'C7SDQINT' not in d:raise ValueError('Re-extract official C7SDQINT outcome using current stats_extract_ecls.py')
    d['C7SDQINT']=d.C7SDQINT.where(d.C7SDQINT.between(1,4))
    group_scores(d,'classmate_support_score','class_key','support')
    keep=d.support_n>=5
    # C7WEIGHT is CHILD BODY WEIGHT IN POUNDS, not a survey weight. It must
    # neither weight the model nor determine eligibility in this revision.
    f=d.loc[keep].dropna(subset=['classmate_support_score','C7SDQINT','prior_internalizing','W8SESL']).copy()
    cc_before_weight_n=int(len(f))
    genuine_weight='C7PW0' if 'C7PW0' in f else ('C7CW0' if 'C7CW0' in f else None)
    if genuine_weight:f=f.loc[f[genuine_weight]>0].copy()
    models=[];cols=['support_within','support_mean','prior_internalizing','W8SESL'];pairs={'support':('support_within','support_mean')}
    formula='C7SDQINT ~ '+' + '.join(cols)
    settings=([('weighted_C7PW0','C7PW0')] if 'C7PW0' in f else [])+([('weighted_C7CW0','C7CW0')] if 'C7CW0' in f else [])+[('unweighted',None)]
    for label,w in settings:
        r,_=formula_fit(f,formula,w,pairs,label=label+'_school_cluster')
        # School bootstrap preserves dependence between sampled classes in a school.
        x=np.column_stack([np.ones(len(f)),f[cols].to_numpy(float)]);y=f.C7SDQINT.to_numpy(float);weights=f[w].to_numpy(float) if w else np.ones(len(f))
        codes,groups=pd.factorize(f.school_key);rng=np.random.default_rng(SEED)
        b=solve(x,y,weights);reps=[]
        for _ in range(1000):
            freq=np.bincount(rng.integers(0,len(groups),size=len(groups)),minlength=len(groups));reps.append(solve(x,y,weights*freq[codes]))
        reps=np.asarray(reps);vals={'beta_W':reps[:,1],'beta_B':reps[:,2],'beta_B_minus_beta_W':reps[:,2]-reps[:,1]}
        r['school_bootstrap']={'seed':SEED,'successful_replicates':1000,'unit':'school','point_estimate_beta_W':float(b[1]),'point_estimate_beta_B':float(b[2]),
            'intervals':{k:{'percentile_ci95_low':float(np.quantile(v,.025)),'percentile_ci95_high':float(np.quantile(v,.975)),'se':float(v.std(ddof=1))} for k,v in vals.items()}}
        models.append(r)
    primary_label='weighted_'+genuine_weight+'_school_cluster' if genuine_weight else 'unweighted_school_cluster'
    primary_uncertainty='school-cluster sandwich, t(G-1); school bootstrap sensitivity'
    # Public ECLS-K JK2 scheme has 90 supplied replicate weights; sum of
    # squared replicate differences, factor1 (official manual4.9.1 p4-50).
    designs=[]
    for weight in ['C7PW0','C7CW0']:
        rwcols=[weight[:-1]+str(i) for i in range(1,91)]
        if weight in f and all(c in f for c in rwcols):
            if f[rwcols].isna().any().any():raise ValueError('ECLS replicate weights contain missing values')
            design=replicate_fit(f,'C7SDQINT',cols,weight,pairs,[f[c].to_numpy(float) for c in rwcols],1,False,'weighted_'+weight+'_JK2')
            design['replicate_method']='ECLS-K90 supplied JK2 replicate weights '+rwcols[0]+'–'+rwcols[-1]+'; variance=sum squared deviations'
            designs.append(design)
            if weight==genuine_weight:primary_label=design['label'];primary_uncertainty=design['uncertainty']
    models=designs+models
    loo='C7SDQINT ~ classmate_support_score + support_loo + prior_internalizing + W8SESL'
    r,fit=formula_fit(f,loo,genuine_weight,{},label='LOO_conditional_association')
    r['terms']={t:effect(fit.params.to_numpy(),fit.cov_params().to_numpy(),np.eye(len(fit.params))[list(fit.params.index).index(t)],f.school_key.nunique()-1) for t in ['classmate_support_score','support_loo']};models.append(r)
    reporters=d.loc[d.class_key.isin(f.class_key.unique())].dropna(subset=['classmate_support_score'])
    return {'sample':summary(f),'primary_model_label':primary_label,'primary_uncertainty':primary_uncertainty,
            'sampling_weight_status':('C7PW0 current parent+child survey weight chosen because W8SESL is parent-derived; C7CW0 child-only weight sensitivity; prior-response/complete-case selection not repaired by weights' if genuine_weight=='C7PW0' else ('C7CW0 genuine round7 full-sample child survey weight; complete-case selection may limit representativeness' if genuine_weight else 'unweighted exploratory analysis; genuine survey weight unavailable in existing extract; no population-representative inference')),
            'historical_weight_error':'Original C7WEIGHT-weighted analysis withdrawn: provider C7WEIGHT is child body weight in pounds, not a sampling weight.',
            'historical_SES_error':'Original extractor discarded all negative numbers; valid negative W8SESL values now retained, with only provider codes -7/-8/-9 removed.',
            'sample_flow':{'public_source_records':source_n,'valid_school_English_class_identifier_records':int(len(d)),
                'valid_support_records_with_identifiers':int(d.classmate_support_score.notna().sum()),
                'records_in_groups_with_at_least5_context_reporters':int(keep.sum()),
                'eligible_valid_context_reporters':int(d.loc[keep,'classmate_support_score'].notna().sum()),
                'eligible_class_groups':int(d.loc[keep,'class_key'].nunique()),
                'complete_case_before_survey_weight_filter':cc_before_weight_n,
                'model_complete_cases':int(len(f)),
                'final_negative_SES_records':int((f.W8SESL<0).sum()),
                'final_nonnegative_SES_records':int((f.W8SESL>=0).sum())},
            'source_pool':summary(d),'participant_description':{'core_scores':descriptive(f,['C7SDQINT','classmate_support_score','prior_internalizing','W8SESL']),'gender_counts':({('male' if k==1 else 'female'):int(v) for k,v in f.GENDER.value_counts().items()} if 'GENDER' in f else {}),'gender_coding':'provider GENDER1male/2female, descriptive only; not an eligibility criterion'},'complete_case_missingness':{'eligible_class_records':int(keep.sum()),'overlapping_missing_n':{k:int(d.loc[keep,k].isna().sum()) for k in ['C7SDQINT','classmate_support_score','prior_internalizing','W8SESL']},'nonpositive_C7PW0':int((d.loc[keep,'C7PW0']<=0).sum())},'reporter_pool_supporting_final_classes':summary(reporters),
            'outcome_sd_reference':float(f.C7SDQINT.std(ddof=0)),
            'reporter_count_min':int(f.support_n.min()),'reporter_count_max':int(f.support_n.max()),'outcome_complete_case_class_sizes':f.groupby('class_key').size().describe().to_dict(),
            'outcome':'official provider C7SDQINT eighth-grade self-reported internalizing problems composite, eight negative problem items, valid1–4, higher=more problems; use provided score directly with no invented missing-item threshold','outcome_variable':'C7SDQINT','historical_mixed_outcome':'internalizing_score is the old researcher-defined mean of two SDQ and three NELS items, >=4of5; retained only for measurement sensitivity','measurement_decision':'Official outcome selected 7 October 2026 before seeing reanalysis results because of formal scoring/content coverage, not association strength','uncertainty_scope':'JK2 regression intervals condition on observed unweighted reporter means and complete-case set; school bootstrap conditions on those means and resamples current schools, not original kindergarten PSUs.',
            'predictor':'mean C7CLSFR/C7CLSLIK/C7CLSFEL/C7CLSOTH/C7CLSCAR valid1–5 >=4 of5; English-class grouping J71CLASS nested within S7_ID',
            'reliability':{'support_alpha':alpha(f,['C7CLSFR','C7CLSLIK','C7CLSFEL','C7CLSOTH','C7CLSCAR']),
            'outcome_alpha':alpha(f,['C7ANGRY','C7WRYTST','C7LONLY','C7SAD','C7WRYWEL','C7WRYFIN','C7WRYHNG','C7ASHAME']),'historical_mixed_outcome_alpha':alpha(f,['C7LONLY','C7SAD','C7NOCNTR','C7USELES','C7NOGOOD']),
            'all_valid_reporters_for_final_classes':agreement(reporters,'classmate_support_score'),
            'final_model_complete_cases':agreement(f,'classmate_support_score'),
            'old_prethreshold_ICC':json.loads((OLD/'data_audit/eclsk/eclsk_class_context_audit.json').read_text())['support_icc']},'models':models}

def item_score(d,cols):
    a=d[cols].apply(pd.to_numeric,errors='coerce').where(lambda a:a.ge(1)&a.le(4))
    return a.mean(axis=1).where(a.notna().sum(axis=1)>=int(np.ceil(len(cols)/2)))

def timss():
    out={}
    for country in ['FIN','ZAF','KOR']:
        path=SOURCES['timss_root']/country/f'bsg{country.lower()}m7.sav'
        sup=[f'BSBM17{x}' for x in 'ABCDEFG'];order=[f'BSBM18{x}' for x in 'ABCDEF']
        d,_=pyreadstat.read_sav(path,usecols=['IDSCHOOL','IDCLASS','IDSTUD','TOTWGT','JKZONE','JKREP',*sup,*order,'BSBGSSB','BSBGSB'])
        d=d.dropna(subset=['IDSCHOOL','IDCLASS']).copy();d['school_key']=d.IDSCHOOL.astype(str);d['class_key']=d.school_key+':'+d.IDCLASS.astype(str)
        d['support_score']=5-item_score(d,sup);d['disorder_score']=5-item_score(d,order)
        for p in ['support','disorder']:group_scores(d,p+'_score','class_key',p)
        models=[]
        for outcome in ['BSBGSSB','BSBGSB']:
            d[outcome]=pd.to_numeric(d[outcome],errors='coerce').where(d[outcome].between(-10,100))
            for p in ['support','disorder']:
                cols=[p+'_within',p+'_mean'];f=d.dropna(subset=[outcome,'TOTWGT','JKZONE','JKREP',*cols]).loc[lambda a:(a.TOTWGT>0)&(a[p+'_n']>1)].copy()
                zone=f.JKZONE.to_numpy(int);jk=f.JKREP.to_numpy(int);base=f.TOTWGT.to_numpy(float);rws=[]
                if not set(np.unique(jk)).issubset({0,1}):raise ValueError('TIMSS JKREP unexpected')
                for z in range(1,76):
                    for kept in [0,1]:
                        rw=base.copy();rw[(zone==z)&(jk==kept)]*=2;rw[(zone==z)&(jk!=kept)]=0;rws.append(rw)
                model=replicate_fit(f,outcome,cols,'TOTWGT',{p:(cols[0],cols[1])},rws,.5,country=='FIN',f'{p}_{outcome}')
                model['agreement_valid_reporters_in_modeled_classes']=agreement(d.loc[d.class_key.isin(f.class_key.unique())],p+'_score')
                models.append(model)
        # Item reliability on the corresponding model eligible support reporter pool.
        out[country]={'source':str(path),'source_sample':summary(d),'models':models,
                      'reliability':{'support_alpha':alpha(d,sup),'disorder_alpha':alpha(d,order),'support_agreement':agreement(d,'support_score'),'disorder_agreement':agreement(d,'disorder_score')},
                      'scoring':'support=5 minus BSBM17 mean (higher support); disorder=5 minus BSBM18 mean (higher disruption); at least half valid 1–4; BSBGSSB=higher belonging, BSBGSB=higher freedom from bullying provider scales'}
    return out

def iccs():
    out={};classitems=[f'IS4G16{x}' for x in 'ABCDEF']
    for country in ['NOR','SWE','POL','FRA','DNK','ITA']:
        path=SOURCES['iccs_root']/f'ISG{country}C4.sav'
        _,meta=pyreadstat.read_sav(path,metadataonly=True);rwcols=sorted(c for c in meta.column_names if c.startswith('SRWGT'))
        d,_=pyreadstat.read_sav(path,usecols=['IDSCHOOL','IDCLASS','IDSTUD','TOTWGTS',*rwcols,*classitems,'IS4G18H','IS4G18I'])
        d=d.dropna(subset=['IDSCHOOL','IDCLASS']).copy();d['school_key']=d.IDSCHOOL.astype(str);d['class_key']=d.school_key+':'+d.IDCLASS.astype(str)
        d['openness_score']=item_score(d,classitems)
        for src,dest in [('IS4G18H','safety_score'),('IS4G18I','bullying_fear')]:d[dest]=5-pd.to_numeric(d[src],errors='coerce').where(d[src].between(1,4))
        group_scores(d,'openness_score','class_key','openness');group_scores(d,'safety_score','school_key','safety')
        # Preserve the original >=5 joint item-complete students/class sampling filter.
        f=d.dropna(subset=['openness_score','safety_score','bullying_fear']).copy()
        n=f.groupby('class_key').size();f=f.loc[f.class_key.isin(n[n>=5].index)].copy()
        n=f.groupby('school_key').size();f=f.loc[f.school_key.isin(n[n>=5].index)].copy()
        f=f.loc[f.TOTWGTS>0].copy()
        cols=['openness_within','openness_mean','safety_within','safety_mean']
        pairs={'class_openness':('openness_within','openness_mean'),'school_safety':('safety_within','safety_mean')}
        rws=[f[c].to_numpy(float) for c in rwcols]
        models=[replicate_fit(f,'bullying_fear',cols,'TOTWGTS',pairs,rws,1,False,'country_joint')]
        counts=f.groupby('school_key').class_key.nunique();eligible=counts[counts>1].index
        if len(eligible)>=10:
            g=f.loc[f.school_key.isin(eligible)].copy();cols=['openness_within','openness_mean','safety_score']
            models.append(replicate_fit(g,'bullying_fear',cols,'TOTWGTS',{'class_openness':('openness_within','openness_mean')},[g[c].to_numpy(float) for c in rwcols],1,True,'within_school_class'))
        reporter=d.loc[d.class_key.isin(f.class_key.unique())]
        out[country]={'source':str(path),'sample':summary(f),'outcome_sd_reference':float(f.bullying_fear.std(ddof=0)),'models':models,'replicate_columns_count':len(rwcols),'reliability':{
            'openness_alpha_final_cases':alpha(f,classitems),'openness_all_reporters':agreement(reporter,'openness_score'),'safety_school_agreement':agreement(d.loc[d.school_key.isin(f.school_key.unique())],'safety_score','school_key')},
            'scoring':'class openness mean six IS4G16 A-F, >=3 valid 1–4; safety=5–IS4G18H (higher safety); bullying fear=5–IS4G18I (higher fear), 1–4; class and school content differ'}
    return out

def flatten(result):
    rows=[]
    def add(source,country,models):
        for m in models:
            for domain,(W,B) in [('class_support',('class_within','class_mean')),('school_belonging_aggregated_to_class',('class_school_within','class_school_mean')),('support',('support_within','support_mean')),('disorder',('disorder_within','disorder_mean')),('class_openness',('openness_within','openness_mean')),('school_safety',('safety_within','safety_mean'))]:
                if domain not in m.get('contextual_associations',{}):continue
                for measure,item in [('within',m['terms'][W]),('between',m['terms'][B]),('contextual',m['contextual_associations'][domain])]:
                    if source in ['CEPS','ECLS']:sd=result[source]['outcome_sd_reference']
                    elif source=='ICCS':sd=result[source][country]['outcome_sd_reference']
                    else:sd=m['outcome_sd_in_model_sample']
                    rows.append({'source':source,'country':country,'model':m['label'],'domain':domain,'measure':measure,'n':m['n'],'classes':m['classes'],'schools':m['schools'],**item,
                        'reference_outcome_sd':sd,'standardized_Y_estimate':item['estimate']/sd,'standardized_Y_se':item['se']/sd,'standardized_Y_ci95_low':item['ci95_low']/sd,'standardized_Y_ci95_high':item['ci95_high']/sd})
    add('CEPS','CHN',result['CEPS']['models']);add('ECLS','USA',result['ECLS']['models'])
    for c,v in result['TIMSS'].items():add('TIMSS',c,v['models'])
    for c,v in result['ICCS'].items():add('ICCS',c,v['models'])
    return pd.DataFrame(rows)

def main():
    global OLD,OUT,SOURCES
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=OLD,help='Original project root, including data_audit and old provenance JSON.')
    parser.add_argument('--output-dir',type=Path,default=OUT,help='Aggregate statistical output directory; use D: on this Windows workstation.')
    parser.add_argument('--source-config',type=Path,help='JSON object overriding ceps, ecls, timss_root and/or iccs_root input paths. Inputs are read only.')
    parser.add_argument('--sources',nargs='+',choices=['CEPS','ECLS','TIMSS','ICCS'],default=['CEPS','ECLS','TIMSS','ICCS'],help='Optionally rerun selected sources, retaining completed others from existing aggregate JSON.')
    args=parser.parse_args();OLD=args.project_root.resolve();OUT=args.output_dir.resolve()
    SOURCES={'ceps':OLD/'data_audit/ceps/CEPS_baseline_pooled.dta','ecls':OLD/'data_audit/eclsk/eclsk_grade8_extract.csv','timss_root':OLD.parent/'data/processed/timss2019','iccs_root':OLD.parent/'data/raw/iccs2022/extracted/ICCS2022_IDB_SPSS/Data'}
    if args.source_config:
        cfg=json.loads(args.source_config.read_text(encoding='utf-8'))
        unknown=set(cfg)-set(SOURCES)
        if unknown:raise ValueError(f'Unknown source config keys: {unknown}')
        SOURCES.update({k:Path(v).resolve() for k,v in cfg.items()})
    if os.name=='nt' and OUT.drive.upper()!='D:':raise ValueError('This workstation requires research outputs on D:.')
    OUT.mkdir(parents=True,exist_ok=True)
    result={'analysis_date':'2026-10-07','revision_analysis_status':'exploratory reviewer driven correction; not a preregistered analysis','units':'raw outcome points per raw predictor point; W and B use same predictor unit','conditional_inference':'Observed reporter-pool means and complete-case selections are held fixed in replicate regression inference; no population class-mean or latent-measurement-error variance is propagated','equation':'Y_ij = a + beta_W (X_ij - mean_j X) + beta_B mean_j X + controls + error; contextual coefficient = beta_B-beta_W','group_mean':'unweighted full valid construct-reporting pool before outcome/covariate listwise deletion','uncertainty_note':'cluster inference/replicate weights address dependence/design, not latent aggregate measurement error'}
    if set(args.sources)!=set(['CEPS','ECLS','TIMSS','ICCS']):
        previous=json.loads((OUT/'stats_verified_results.json').read_text(encoding='utf-8'))
        result.update({key:previous[key] for key in ['CEPS','ECLS','TIMSS','ICCS']})
    for label,fn in [('CEPS',ceps),('ECLS',ecls),('TIMSS',timss),('ICCS',iccs)]:
        if label not in args.sources:continue
        print('Running',label,flush=True);result[label]=fn();(OUT/f'stats_{label.lower()}_verified.json').write_text(json.dumps(result[label],indent=2),encoding='utf-8')
        print(label,'complete',flush=True)
    # CEPS sample-flow metadata is created inside ceps(), for full and partial reruns alike.
    for country,v in result['TIMSS'].items():
        v['sample_flow']={'valid_identifier_source_records':v['source_sample']['n'],'model_complete_cases_by_domain_outcome':{m['label']:m['n'] for m in v['models']},'valid_support_reporters_in_source':v['reliability']['support_agreement']['n']}
    for country,v in result['ICCS'].items():
        _,meta=pyreadstat.read_sav(Path(v['source']),metadataonly=True)
        v['sample_flow']={'public_source_records':int(meta.number_rows),'final_joint_item_class_school_threshold_model_records':v['sample']['n'],'within_school_model_records':next((m['n'] for m in v['models'] if m['label']=='within_school_class'),None)}
    (OUT/'stats_verified_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    flatten(result).to_csv(OUT/'stats_coefficients.csv',index=False)
    inputfiles=[SOURCES['ceps'],SOURCES['ecls']]+[SOURCES['timss_root']/c/f'bsg{c.lower()}m7.sav' for c in ['FIN','ZAF','KOR']]+[SOURCES['iccs_root']/f'ISG{c}C4.sav' for c in ['NOR','SWE','POL','FRA','DNK','ITA']]
    def filehash(path):
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
        return h.hexdigest()
    manifest={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'runtime':sys.executable,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'statsmodels':__import__('statsmodels').__version__,'scipy':__import__('scipy').__version__,'pyreadstat':pyreadstat.__version__,'sources_rerun_this_invocation':args.sources,
              'input_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':filehash(p)} for p in inputfiles],
              'outputs':[{ 'filename':p.name,'sha256':filehash(p)} for p in [OUT/'stats_verified_results.json',OUT/'stats_coefficients.csv']]}
    (OUT/'stats_runtime_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('All sources complete',flush=True)

if __name__=='__main__':main()
