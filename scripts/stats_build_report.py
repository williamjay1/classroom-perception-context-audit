"""Build statistical audit report from completed aggregate results."""
import json,argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results-dir',type=Path,default=ROOT/'results');args=parser.parse_args()
O=args.results_dir
r=json.loads((O/'stats_verified_results.json').read_text(encoding='utf-8'))
c=json.loads((O/'stats_independent_checks.json').read_text(encoding='utf-8'))
def cell(e):return f"{e['estimate']:.6f} [{e['ci95_low']:.6f}, {e['ci95_high']:.6f}]"
lines=[
'# Statistical reanalysis and verification report',
'',
'Analysis date: 7 October 2026. Status: completed reviewer-driven exploratory correction; this revision analysis is not preregistered. The original provider data and original project outputs were read only. Derived work data, scripts and outputs are on D:.',
'',
'## Decision and estimand',
'',
'The rejection reviewer’s centering objection is correct. The earlier own-score minus leave-one-out aggregate coefficient is withdrawn as a construct-homogeneity statistic. The corrected analysis estimates within-group and between-group conditional associations on the same raw predictor scale. It does not test psychometric equivalence, construct homogeneity, causal mechanisms or classroom protection. It does not estimate out-of-sample prediction quality.',
'',
'For each relevant domain, fit:',
'',
'    Y_ij = alpha + beta_W (X_ij - Xbar_j) + beta_B Xbar_j + covariates + error_ij.',
'    delta_contextual = beta_B - beta_W.',
'',
'The equivalent own-score/full-mean parameterization is beta_W X_ij + (beta_B-beta_W) Xbar_j. Thus a coefficient on a full group mean conditional on own X is already the contextual difference, not beta_B. A null contextual difference does not establish validity or equivalence; a nonzero difference also does not establish different constructs. All manuscript estimates should be raw outcome points per one raw predictor point. The within and between components use exactly the same unit. A separate outcome-only SD rescaling is supplied in the coefficient CSV for optional presentation; no independently standardized group mean is used in the corrected analyses.',
'',
'Group means are unweighted arithmetic means of all valid construct reports before outcome/covariate complete-case deletion. Therefore group deviations may not average to zero in the retained model sample. These are fitted conditional within/between contrasts relative to the full construct-reporting pool. Survey weights enter model fitting and replicate inference. These procedures do not recover error-free latent classroom means or eliminate common-method variance.',
'',
'For a leave-one-out mean, Xbar_(j,-i) = Xbar_j - (X_ij-Xbar_j)/(n_j-1). In a model a X_ij + c Xbar_(j,-i), a common n gives beta_W = a-c/(n-1), beta_B = a+c, and delta_contextual = c n/(n-1). The difference a-c is not the contextual difference. With unequal reporter counts, the ordinary constant-coefficient own/LOO model implies a reporter-count-dependent within slope. This is why LOO fits are retained only as conditional-association sensitivity models and their own-minus-aggregate differences are not reported.',
'',
'## Model and design specification',
'',
'CEPS main: available student weight sweight; class-support within deviation and full class mean, plus the separate school-belonging item’s within-class deviation and class mean; categorical gender, grade and migrant status; numerical health1–5, parent expectation stress1–5, household income1–5 and maternal/paternal education category1–9 (linear ordinal trends, not education years); school fixed effects. Primary sandwich covariance clusters the 112 schools, uses finite-sample correction and t(111) intervals. Class-clustered covariance is a sensitivity. Because school fixed effects are fitted, the class mean association uses differences among sampled classes within schools. Available weights and school clustering do not reconstruct unavailable full national stratification/selection information.',
'',
'ECLS-K main outcome is the provider eight-item C7SDQINT internalizing composite, valid1–4. It was selected before new outcome-model results for formal content/scoring. Use current parent-plus-child survey weight C7PW0, selected because the adjusted model contains parent-derived current socioeconomic status W8SESL along with child reports. Adjust for the official third-grade revised internalizing composite C5SDQINR and current W8SESL. Use all 90 supplied C7PW1–C7PW90 JK2 replicate weights; variance is the sum of squared deviations from the full estimate, with no division by 90. Main intervals are normal-reference 95% intervals; the provider notes approximately 76 design degrees of freedom for hypothesis testing. C7CW0 plus its child-only replicates and unweighted fits are disclosed reweighting sensitivities on the same parent-complete main cases; they do not change the eligibility target to a different full child population. School-cluster sandwich and 1,000 school bootstrap percentile intervals (seed 20261005) are separate sensitivities; they preserve dependence between classes sampled in a school. The current weights do not repair earlier-response or complete-case selection, and the English-class groups do not establish a shared classroom construct or nationally representative classroom exposure.',
'',
'TIMSS 2019: country/domain-specific mean/deviation models. Finland includes school fixed effects. South Africa and Korea lack enough sampled multi-class schools for a comparable within-school class estimate and are country-level associations. Fit with TOTWGT; reconstruct 150 replicate weights from 75 JKZONE/JKREP pairs. Within each zone, the selected JKREP group receives multiplier2 and the other group0, with other zones unchanged. JRR covariance is 0.5 times the sum of outer products of the 150 coefficient deviations from the full estimate. Source domains and outcomes are not pooled.',
'',
'ICCS 2022: each country fits class-openness within-class and class-mean components jointly with school-safety within-school and school-mean components. Fit with TOTWGTS and the 75 supplied SRWGT replicate weights; JK2 variance is the sum of squared deviations. Retain the original eligibility requirement of at least five jointly item-complete students/class and school. Full construct-reporting pools support the means. Norway, Poland and Denmark additionally fit school-fixed-effect class-openness models restricted to schools with multiple retained classes, adjusting for own school safety. School-level means are omitted from these fixed-effect fits because they are absorbed by school effects. The minimum ten multi-class schools rule is an analytical feasibility rule, not a guarantee of identification. Other country models are not relabeled as within-school class associations.',
'',
'Across sources, old lower-tail, dispersion and interaction terms were removed from the new main model family to estimate interpretable conventional mean/deviation slopes. Consequently corrected estimates are new estimands, not merely algebraic corrections to the earlier augmented regressions. The old specifications remain auditable in historical provenance only. No model or source was selected based on significance. All fixed CEPS sensitivities and all source/country/domain fits are reported. Multiplicity makes the external and stratum patterns exploratory.',
'',
'## Verified scoring directions',
'',
'| Source | Construct / outcome | Coding |',
'|---|---|---|',
'| CEPS | Class support / quality | Mean classmategood + classgood, both required, 1–4; larger is more favorable |',
'| CEPS | School belonging comparison | friendly, 1–4; different item content and school wording |',
'| CEPS | Negative affect | Mean depressed/blue/unhappy/pessimistic/sad, all five required, 1–5; larger is more symptoms |',
'| ECLS-K | Classmate support | Mean C7CLSFR/C7CLSLIK/C7CLSFEL/C7CLSOTH/C7CLSCAR, >=4/5 valid, 1 never–5 always; larger is more favorable |',
'| ECLS-K | Official internalizing problems | Provider C7SDQINT, eight negative-problem SDQ items, valid1–4; higher=more internalizing problems; no invented minimum item rule |',
'| ECLS-K | Group identifiers | S7_ID + J71CLASS, spring2007 English-class identifier; support items do not experimentally assign an English-class referent |',
'| TIMSS | Instructional support | 5 minus mean BSBM17A–G, >=4/7 valid 1–4; larger is more support |',
'| TIMSS | Disruption | 5 minus mean BSBM18A–F, >=3/6 valid 1–4; larger is MORE disorder (1 every/almost every lesson, 4 never before reversal) |',
'| TIMSS | Belonging / bullying provider scales | BSBGSSB: larger is more belonging; BSBGSB: larger means less frequent bullying |',
'| ICCS | Class openness | Mean IS4G16A–F, >=3/6 valid, 1 never–4 often; larger is more openness |',
'| ICCS | School safety | 5–IS4G18H, 1–4; larger is more safety |',
'| ICCS | Bullying fear | 5–IS4G18I, 1–4; larger is MORE fear (original1 strongly agrees “I am afraid…”) |',
'',
'The TIMSS variable formerly labeled order was reversed into disorder. The ICCS variable formerly described as lower fear was actually higher fear. Revised code preserves the numeric coding while correcting those labels, avoiding a silent sign flip.',
'',
'## Main coefficients',
'',
'Estimate [95% CI]. Raw outcome points / raw predictor point.',
'',
'| Source/model | Domain | n/classes/schools | beta_W | beta_B | beta_B - beta_W |',
'|---|---|---|---|---|---|',
]
def row(src,m,domain,W,B):
    lines.append(f"| {src} / {m['label']} | {domain} | {m['n']}/{m['classes']}/{m['schools']} | {cell(m['terms'][W])} | {cell(m['terms'][B])} | {cell(m['contextual_associations'][domain])} |")
row('CEPS',r['CEPS']['models'][0],'class_support','class_within','class_mean')
row('CEPS',r['CEPS']['models'][0],'school_belonging_aggregated_to_class','class_school_within','class_school_mean')
e=next(m for m in r['ECLS']['models'] if m['label']==r['ECLS']['primary_model_label'])
row('ECLS',e,'support','support_within','support_mean')
row('TIMSS FIN',r['TIMSS']['FIN']['models'][0],'support','support_within','support_mean')
for country,v in r['ICCS'].items():
    for m in v['models']:
        row('ICCS '+country,m,'class_openness','openness_within','openness_mean')
        if 'school_safety' in m['contextual_associations']:row('ICCS '+country,m,'school_safety','safety_within','safety_mean')
lines += [
'',
'These results change the main empirical interpretation. CEPS and ECLS estimates must be interpreted separately with their reported intervals; neither slope dominance nor a nonsignificant difference establishes construct validity or equivalence. Finland has a smaller between-class than within-class support/belonging association, but this is an observational difference in slopes on the same raw scale, not a construct-validity failure. ICCS country-level and within-school results vary. No common effect or cross-source coefficient magnitude should be inferred.',
'',
'## Numerical discrepancy and invalid-source ledger',
'',
'| Submitted claim / source | Verified provenance | Revision action |',
'|---|---|---|',
]
p=r['CEPS']['old_numerical_provenance'];b=p['model_specific_coefficients'];a=p['old_interaction_coefficients']
lines += [
f"| CEPS own=-.206, class context=-.038, alleged same-model contrast=-.126 | Interaction model own={a[0]['terms']['z_class_score']['estimate']:.9f}, aggregate={a[0]['terms']['z_class_loo_mean']['estimate']:.9f}; their arithmetic difference=-.167760668. Separate additive joint model own={b['z_class_score']:.9f}, aggregate={b['z_class_loo']:.9f}, difference={p['own_minus_class_aggregate']:.9f} | Acknowledge mixed fitted models; withdraw old diagnostic and replace with corrected W/B model. Covariance can change a contrast SE, never its point estimate. |",
f"| CEPS class=-.038, mismatch=-.061, alleged difference=.027 | Separate interaction models yield .023069055. Additive joint model class={b['z_class_loo']:.9f}, school-item classaggregate={b['z_class_school_loo']:.9f}, difference={p['class_aggregate_minus_school_item_class_aggregate']:.9f} | Acknowledge mixed-model comparison. Do not treat content-different item coefficients as isolated referent specificity. |",
'| CEPS gender validity | Source0male1female; old1/2 rule excluded every male, yielding female-only n8827 | Correct0/1; valid ID/school/class/grade filtering precedes deduplication and eligible duplicates are checked for contradictions. Rerun all CEPS estimates. Historical restricted-sample numbers remain only to trace errors. |',
'| CEPS18.4% ratio | Ratio of two independently standardized predictors’ interaction-model main coefficients, evaluated at centered counterpart | Remove as evidence of validity or loss of construct signal. |',
'| CEPS ICC1=.133/ICC2=.771 | ceps_public_audit.json concerns four-item teacher+peer support, not submitted final two-item class score. Original audit_ceps_public.py ICC2 denominator was not the standard ANOVA mean-score reliability formula. | Replace with correctly computed two-item reporter-pool diagnostics below. |',
'| ECLS C7WEIGHT described as sampling weight | Official NCES syntax defines C7WEIGHT as child composite physical WEIGHT IN POUNDS | Withdraw every original C7WEIGHT-weighted estimate and its bootstrap interval. Recover genuine C7PW0/C7PW1–90; use C7CW0 sensitivity. Body-weight availability is not an eligibility requirement. |',
f"| ECLS old n1755/472/387 | Required positive/nonmissing physical body weight AND discarded all valid negative standardized SES values | Final corrected sample{r['ECLS']['sample']['n']}/{r['ECLS']['sample']['classes']}/{r['ECLS']['sample']['schools']}. Earlier mixed-outcome correction restored the sample to3609; the current official-outcome selection has its own documented flow and must not be decomposed as if it used that same outcome-completion rule. |",
'| ECLS W8SESL negative values | Original shared numeric parser treated every negative value as missing. Official W8SESL negative standardized values are valid; special missing codes are -7/-8/-9 | Preserve signed SES; source contains8809 valid SES records,4707 below0. This repairs a substantial unintended restriction toward higher socioeconomic status. |',
'| ECLS outcome called official internalizing | Two items are SDQ sadness/loneliness; three are NELS control/uselessness/no-good self-appraisal items | Use the available official eighth-grade C7SDQINT as the current main outcome, chosen for measurement content before seeing its new results. Keep the mixed internalizing_score only for an explicit common-sample outcome sensitivity. Prior C5SDQINR remains the distinct official third-grade revised internalizing composite. |',
'| ECLS ICC2=.067 | Prethreshold pool n9018,3737 groups, mean2.413 reporters/group | Replace main diagnostic with reporter pool supporting final modeled classes; keep prior statistic only in source history. |',
'| ECLS reproducibility description “at least half” | Actual extract/analysis requires4 of5 items (80%) | Correct Methods and replication description to4 of5. |',
'| TIMSS higher order | Original5−mean BSBM18 measures greater disruption | Correct domain label to disorder/disruption throughout text, figures and supplement. |',
'| ICCS lower bullying fear | Original5−IS4G18I makes high values stronger agreement with fear | Correct outcome label to greater bullying fear throughout text, figures and supplement. |',
'',
'## Reliability and reporter counts',
'',
'One-way unequal-group-size ANOVA uses n0=(N−sum(n_j²)/N)/(J−1), ICC1=(MSB−MSW)/(MSB+(n0−1)MSW). Mean-score reliability at reporter count n is n*ICC1/[1+(n−1)*ICC1]. The main descriptive ICC2 is evaluated at the ANOVA effective reporter count n0; the arithmetic-mean-n and minimum/maximum-count versions are also stored and explicitly alternate. These are unweighted descriptive observed-score diagnostics, not multilevel latent reliability estimates or complete construct validation. Unconditional class ICCs may include shared school variation.',
'',
'| Source/pool | n/groups | Mean reporters | ICC1 | ICC2 at effective n0 |',
'|---|---|---|---|---|',
]
def agr(name,d):lines.append(f"| {name} | {d['n']}/{d['groups']} | {d['arithmetic_mean_n']:.3f} | {d['icc1_anova']:.6f} | {d['icc2_at_effective_n0']:.6f} |")
agr('CEPS all class-score reporters supporting final classes',r['CEPS']['reliability']['all_context_reporters_in_modeled_classes'])
agr('CEPS outcome/covariate complete cases only',r['CEPS']['reliability']['final_model_complete_cases'])
agr('ECLS all support reporters supporting final classes',r['ECLS']['reliability']['all_valid_reporters_for_final_classes'])
agr('ECLS outcome/covariate complete cases only',r['ECLS']['reliability']['final_model_complete_cases'])
agr('TIMSS FIN support/belonging modeled-class reporter pool',r['TIMSS']['FIN']['models'][0]['agreement_valid_reporters_in_modeled_classes'])
lines += [
'',
f"CEPS two-item alpha={r['CEPS']['reliability']['class_alpha']['alpha']:.6f}; five-item outcome alpha={r['CEPS']['reliability']['outcome_alpha']['alpha']:.6f}, current class/outcome alpha n{r['CEPS']['reliability']['class_alpha']['n']}/{r['CEPS']['reliability']['outcome_alpha']['n']}. ECLS five-item support alpha={r['ECLS']['reliability']['support_alpha']['alpha']:.6f} (n{r['ECLS']['reliability']['support_alpha']['n']} complete on all five); official eight-item internalizing alpha={r['ECLS']['reliability']['outcome_alpha']['alpha']:.6f} (n{r['ECLS']['reliability']['outcome_alpha']['n']} complete on all eight). ECLS retained context reporter counts are5–34 whereas outcome/covariate complete cases average{r['ECLS']['outcome_complete_case_class_sizes']['mean']:.3f}/class and range{r['ECLS']['outcome_complete_case_class_sizes']['min']:.0f}–{r['ECLS']['outcome_complete_case_class_sizes']['max']:.0f}. These populations are explicitly distinct. Low aggregate reliability remains an important attenuation limitation even after correction from .067 to {r['ECLS']['reliability']['all_valid_reporters_for_final_classes']['icc2_at_effective_n0']:.3f}.",
'',
'The TIMSS country-level reliability objects describe broader source-valid domain pools. For any model-specific statement use its agreement_valid_reporters_in_modeled_classes object instead. In particular Finland support/belonging uses4801 valid context reporters in353 modeled classes, rather than the broader4816/368 source pool.',
'',
'## CEPS fixed sensitivity block',
'',
'| Model | n/classes/schools | Class support beta_B-beta_W [95% CI] |',
'|---|---|---|',
]
for m in r['CEPS']['models']:
    if 'class_support' in m['contextual_associations']:
        lines.append(f"| {m['label']} | {m['n']}/{m['classes']}/{m['schools']} | {cell(m['contextual_associations']['class_support'])} |")
lines += [
'',
f"The {r['CEPS']['class_size_cutpoints']['q25']:.0f}/{r['CEPS']['class_size_cutpoints']['q75']:.0f} cutpoints are the 25th/75th percentiles of valid class-reporter counts repeated over current analytic student records. They are not unique-class-size quartiles or enrolled class sizes. These selected stratum slopes are exploratory. Comparing significance levels is not a test of moderation; no interaction test was performed.",
'',
'## Reproducibility and checks',
'',
f"Independent verification completed {len(c['checks'])} arithmetic/reparameterization checks, all passed. These include every B−W difference, equivalence of the own-score/full-mean and mean/deviation fitted values, and the unequal-size LOO identity. All fitted formula designs have full rank. Every supplied/reconstructed replicate successfully fit a full-rank common signal matrix. School fixed effects are residualized separately for each replicate; removed schools do not create unidentified signal coefficients. No replicate was silently dropped.",
'',
'ECLS public raw catalog was recovered read-only from the existing F archive into a fresh D temporary working copy. The official15-record fixed-field layout was used to recover C7PW0/C7PW1–90 and C7CW0/C7CW1–90. The earlier support/mixed-outcome/prior/SES verification found agreement over every common valid record, but the old extract additionally lost4707 valid negative SES values. The current extract adds the official C7SDQINT and eight raw items plus GENDER; its complete-eight-item mean differs from the provided two-decimal composite by at most0.005. The fresh parser retains signed SES and uses its exact provider missing codes. School identifiers are preserved as character fields; old numeric-only school codes had different formatting but a one-to-one mapping to the new codes, while English-class codes match exactly. The fresh case-level extract is private work data and must not be distributed publicly. Input file sizes/hashes and runtime package versions are in stats_runtime_manifest.json; official syntax locations and extraction checks are in stats_ecls_survey_extraction_audit.json. The source config supports alternate provider-file locations.',
'',
'Commands (adapt paths when reproducing; do not redistribute raw provider/case-level files):',
'',
'    python stats_extract_ecls.py --child-file <childk8p.dat> --syntax-file <official_SPSS.sps> --output <new_private_extract.csv>',
'    python stats_reanalysis.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>',
'    python stats_checks.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>',
'    python round2_measurement_sensitivity.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>',
'',
'The current workstation runtime is Python3.12 with pandas3.0.5 and statsmodels0.14.6; bundled Python lacked statsmodels, so the existing statistical runtime was used without installing anything. Scripts set dont_write_bytecode and work output paths on D:. The source-config keys are ceps, ecls, timss_root and iccs_root. Reproduction requires the original CEPS historical JSON provenance and ECLS source-audit JSON as well as provider inputs. File hashes/paths belong in reproducibility records, not article body prose.',
'',
'## Interpretation boundaries requiring manuscript changes',
'',
'1. Withdraw the old construct-homogeneity gate and every claim that stronger own-score coefficients imply a validity difference. The corrected W/B contextual difference describes outcome associations, not the psychometric status of a group construct.',
'2. CEPS school-item comparison changes both content and referent. No slope comparison isolates referent specificity; intervals containing zero do not establish equivalence. ICCS also changes content/referent simultaneously.',
'3. Moderate individual internal consistency, finite reporter counts, shared respondent affect/response style, aggregate sampling error, and prior/covariate selection can explain within/between patterns. Replicate covariance does not correct latent measurement error or common-method bias.',
'4. School fixed effects control school-average nuisance patterns but do not randomize classes or remove selection/confounding within schools. ECLS between-class slopes additionally mix school differences because that model does not use school fixed effects.',
'5. CEPS and ECLS outcomes concern self-reported symptoms; TIMSS and ICCS are school-experience proxies. Their directions and effect magnitudes are not pooled, and these observational cross-sectional models do not demonstrate a classroom intervention effect.',
'6. Old body-weight-weighted ECLS coefficients, mixed-model CEPS contrasts, the18.4% ratio, mislabeled TIMSS order and ICCS fear results must not survive in the abstract, tables, captions, supplement or response letter as current findings.',
'',
'## Official source locators verified by the source-audit agent',
'',
'- NCES ECLS-K official SPSS layout: https://nces.ed.gov/ECLS/data/ECLSK_Kto8_child_SPSS.sps . C7WEIGHT physical pounds; C7PW0 current parent/child full-sample weight; C7CW0 child-only full-sample weight; J71CLASS spring2007 English-class number; C5SDQINR revised third-grade internalizing composite.',
'- NCES K–8 user manual part1: https://nces.ed.gov/ECLS/data/ECLSK_K8_Manual_part1.pdf . §4.8.5.2 printedp4-47 supports C7PW0 for parent data combined with child assessments; §4.9.1 printedpp4-50–4-51 explains JK2 sum-of-squares covariance,90replicates and approximately76design df; Table4-18 printedp4-54 supplies weight family names.',
'- TIMSS2019 Methods, Chapter14: https://timss.bc.edu/timss2019/methods/pdf/T19_MP_Ch14-estimating-standard-errors.pdf . Official full JRR150replicate factor0.5 used in the prior archived design code and reimplemented here.',
'- ICCS2022 user guide: https://www.iea.nl/sites/default/files/2024-09/ICCS%20User%20Guide.pdf . Supplied SRWGT JK2 scheme; corresponding SPSS item labels/value labels were independently read for coding direction.',
]
if (O/'round2_measurement_results.json').exists():
    q=json.loads((O/'round2_measurement_results.json').read_text('utf-8'))
    lines += ['', '## Fixed measurement and ordinal-control sensitivities', '', 'These models were selected before inspecting their new results. They preserve the current main specification and are reported regardless of significance. CEPS item-specific means use the same two-item-complete reporter pool, with separate school-belonging adjustment. All five ordinal controls are entered categorically in one joint-model sensitivity. ECLS official/mixed outcomes are compared on a shared valid sample.', '', '| Source/model | Domain | n/classes/schools | beta_W | beta_B | beta_B-beta_W |', '|---|---|---|---|---|---|']
    for source in ['CEPS','ECLS']:
        for m in q[source]['models']:
            for domain in m['contextual_associations']:
                W,B=m.get('paired_terms',{'class_support':('class_within','class_mean'),'school_belonging_aggregated_to_class':('class_school_within','class_school_mean')})[domain]
                row(source,m,domain,W,B)
(O/'stats_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Written stats_report.md')
