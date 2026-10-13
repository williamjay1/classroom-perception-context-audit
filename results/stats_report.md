# Statistical reanalysis and verification report

Analysis date: 7 October 2026. Status: completed reviewer-driven exploratory correction; this revision analysis is not preregistered. The original provider data and original project outputs were read only. Derived work data, scripts and outputs are on D:.

## Decision and estimand

The rejection reviewer’s centering objection is correct. The earlier own-score minus leave-one-out aggregate coefficient is withdrawn as a construct-homogeneity statistic. The corrected analysis estimates within-group and between-group conditional associations on the same raw predictor scale. It does not test psychometric equivalence, construct homogeneity, causal mechanisms or classroom protection. It does not estimate out-of-sample prediction quality.

For each relevant domain, fit:

    Y_ij = alpha + beta_W (X_ij - Xbar_j) + beta_B Xbar_j + covariates + error_ij.
    delta_contextual = beta_B - beta_W.

The equivalent own-score/full-mean parameterization is beta_W X_ij + (beta_B-beta_W) Xbar_j. Thus a coefficient on a full group mean conditional on own X is already the contextual difference, not beta_B. A null contextual difference does not establish validity or equivalence; a nonzero difference also does not establish different constructs. All manuscript estimates should be raw outcome points per one raw predictor point. The within and between components use exactly the same unit. A separate outcome-only SD rescaling is supplied in the coefficient CSV for optional presentation; no independently standardized group mean is used in the corrected analyses.

Group means are unweighted arithmetic means of all valid construct reports before outcome/covariate complete-case deletion. Therefore group deviations may not average to zero in the retained model sample. These are fitted conditional within/between contrasts relative to the full construct-reporting pool. Survey weights enter model fitting and replicate inference. These procedures do not recover error-free latent classroom means or eliminate common-method variance.

For a leave-one-out mean, Xbar_(j,-i) = Xbar_j - (X_ij-Xbar_j)/(n_j-1). In a model a X_ij + c Xbar_(j,-i), a common n gives beta_W = a-c/(n-1), beta_B = a+c, and delta_contextual = c n/(n-1). The difference a-c is not the contextual difference. With unequal reporter counts, the ordinary constant-coefficient own/LOO model implies a reporter-count-dependent within slope. This is why LOO fits are retained only as conditional-association sensitivity models and their own-minus-aggregate differences are not reported.

## Model and design specification

CEPS main: available student weight sweight; class-support within deviation and full class mean, plus the separate school-belonging item’s within-class deviation and class mean; categorical gender, grade and migrant status; numerical health1–5, parent expectation stress1–5, household income1–5 and maternal/paternal education category1–9 (linear ordinal trends, not education years); school fixed effects. Primary sandwich covariance clusters the 112 schools, uses finite-sample correction and t(111) intervals. Class-clustered covariance is a sensitivity. Because school fixed effects are fitted, the class mean association uses differences among sampled classes within schools. Available weights and school clustering do not reconstruct unavailable full national stratification/selection information.

ECLS-K main outcome is the provider eight-item C7SDQINT internalizing composite, valid1–4. It was selected before new outcome-model results for formal content/scoring. Use current parent-plus-child survey weight C7PW0, selected because the adjusted model contains parent-derived current socioeconomic status W8SESL along with child reports. Adjust for the official third-grade revised internalizing composite C5SDQINR and current W8SESL. Use all 90 supplied C7PW1–C7PW90 JK2 replicate weights; variance is the sum of squared deviations from the full estimate, with no division by 90. Main intervals are normal-reference 95% intervals; the provider notes approximately 76 design degrees of freedom for hypothesis testing. C7CW0 plus its child-only replicates and unweighted fits are disclosed reweighting sensitivities on the same parent-complete main cases; they do not change the eligibility target to a different full child population. School-cluster sandwich and 1,000 school bootstrap percentile intervals (seed 20261005) are separate sensitivities; they preserve dependence between classes sampled in a school. The current weights do not repair earlier-response or complete-case selection, and the English-class groups do not establish a shared classroom construct or nationally representative classroom exposure.

TIMSS 2019: country/domain-specific mean/deviation models. Finland includes school fixed effects. South Africa and Korea lack enough sampled multi-class schools for a comparable within-school class estimate and are country-level associations. Fit with TOTWGT; reconstruct 150 replicate weights from 75 JKZONE/JKREP pairs. Within each zone, the selected JKREP group receives multiplier2 and the other group0, with other zones unchanged. JRR covariance is 0.5 times the sum of outer products of the 150 coefficient deviations from the full estimate. Source domains and outcomes are not pooled.

ICCS 2022: each country fits class-openness within-class and class-mean components jointly with school-safety within-school and school-mean components. Fit with TOTWGTS and the 75 supplied SRWGT replicate weights; JK2 variance is the sum of squared deviations. Retain the original eligibility requirement of at least five jointly item-complete students/class and school. Full construct-reporting pools support the means. Norway, Poland and Denmark additionally fit school-fixed-effect class-openness models restricted to schools with multiple retained classes, adjusting for own school safety. School-level means are omitted from these fixed-effect fits because they are absorbed by school effects. The minimum ten multi-class schools rule is an analytical feasibility rule, not a guarantee of identification. Other country models are not relabeled as within-school class associations.

Across sources, old lower-tail, dispersion and interaction terms were removed from the new main model family to estimate interpretable conventional mean/deviation slopes. Consequently corrected estimates are new estimands, not merely algebraic corrections to the earlier augmented regressions. The old specifications remain auditable in historical provenance only. No model or source was selected based on significance. All fixed CEPS sensitivities and all source/country/domain fits are reported. Multiplicity makes the external and stratum patterns exploratory.

## Verified scoring directions

| Source | Construct / outcome | Coding |
|---|---|---|
| CEPS | Class support / quality | Mean classmategood + classgood, both required, 1–4; larger is more favorable |
| CEPS | School belonging comparison | friendly, 1–4; different item content and school wording |
| CEPS | Negative affect | Mean depressed/blue/unhappy/pessimistic/sad, all five required, 1–5; larger is more symptoms |
| ECLS-K | Classmate support | Mean C7CLSFR/C7CLSLIK/C7CLSFEL/C7CLSOTH/C7CLSCAR, >=4/5 valid, 1 never–5 always; larger is more favorable |
| ECLS-K | Official internalizing problems | Provider C7SDQINT, eight negative-problem SDQ items, valid1–4; higher=more internalizing problems; no invented minimum item rule |
| ECLS-K | Group identifiers | S7_ID + J71CLASS, spring2007 English-class identifier; support items do not experimentally assign an English-class referent |
| TIMSS | Instructional support | 5 minus mean BSBM17A–G, >=4/7 valid 1–4; larger is more support |
| TIMSS | Disruption | 5 minus mean BSBM18A–F, >=3/6 valid 1–4; larger is MORE disorder (1 every/almost every lesson, 4 never before reversal) |
| TIMSS | Belonging / bullying provider scales | BSBGSSB: larger is more belonging; BSBGSB: larger means less frequent bullying |
| ICCS | Class openness | Mean IS4G16A–F, >=3/6 valid, 1 never–4 often; larger is more openness |
| ICCS | School safety | 5–IS4G18H, 1–4; larger is more safety |
| ICCS | Bullying fear | 5–IS4G18I, 1–4; larger is MORE fear (original1 strongly agrees “I am afraid…”) |

The TIMSS variable formerly labeled order was reversed into disorder. The ICCS variable formerly described as lower fear was actually higher fear. Revised code preserves the numeric coding while correcting those labels, avoiding a silent sign flip.

## Main coefficients

Estimate [95% CI]. Raw outcome points / raw predictor point.

| Source/model | Domain | n/classes/schools | beta_W | beta_B | beta_B - beta_W |
|---|---|---|---|---|---|
| CEPS / primary_joint | class_support | 17991/438/112 | -0.120043 [-0.144807, -0.095279] | -0.096123 [-0.283690, 0.091444] | 0.023920 [-0.158771, 0.206611] |
| CEPS / primary_joint | school_belonging_aggregated_to_class | 17991/438/112 | -0.093842 [-0.112863, -0.074820] | -0.183470 [-0.348620, -0.018320] | -0.089628 [-0.259202, 0.079945] |
| ECLS / weighted_C7PW0_JK2 | support | 3623/538/433 | -0.093208 [-0.136772, -0.049644] | -0.048712 [-0.116242, 0.018818] | 0.044496 [-0.040548, 0.129539] |
| TIMSS FIN / support_BSBGSSB | support | 4786/353/154 | 1.263001 [1.169853, 1.356149] | 0.787554 [0.417518, 1.157590] | -0.475447 [-0.857665, -0.093229] |
| ICCS NOR / country_joint | class_openness | 5347/264/141 | -0.038456 [-0.082782, 0.005871] | -0.039815 [-0.192560, 0.112931] | -0.001359 [-0.150098, 0.147381] |
| ICCS NOR / country_joint | school_safety | 5347/264/141 | -0.231002 [-0.281272, -0.180733] | -0.365368 [-0.493151, -0.237584] | -0.134365 [-0.270083, 0.001353] |
| ICCS NOR / within_school_class | class_openness | 5081/246/123 | -0.042709 [-0.089213, 0.003796] | 0.036085 [-0.184091, 0.256262] | 0.078794 [-0.147600, 0.305187] |
| ICCS SWE / country_joint | class_openness | 3113/148/148 | -0.019001 [-0.097943, 0.059941] | 0.073919 [-0.071183, 0.219021] | 0.092920 [-0.061969, 0.247809] |
| ICCS SWE / country_joint | school_safety | 3113/148/148 | -0.225999 [-0.292453, -0.159545] | -0.336856 [-0.476685, -0.197027] | -0.110857 [-0.250336, 0.028621] |
| ICCS POL / country_joint | class_openness | 4362/235/169 | 0.032256 [-0.031854, 0.096367] | -0.058649 [-0.205684, 0.088385] | -0.090906 [-0.261413, 0.079601] |
| ICCS POL / country_joint | school_safety | 4362/235/169 | -0.304670 [-0.347910, -0.261430] | -0.339112 [-0.474561, -0.203663] | -0.034442 [-0.164044, 0.095160] |
| ICCS POL / within_school_class | class_openness | 2602/131/65 | 0.025259 [-0.028100, 0.078618] | -0.344522 [-0.595325, -0.093719] | -0.369781 [-0.630073, -0.109489] |
| ICCS FRA / country_joint | class_openness | 3347/147/146 | 0.024704 [-0.032619, 0.082027] | -0.064995 [-0.220070, 0.090080] | -0.089699 [-0.254355, 0.074958] |
| ICCS FRA / country_joint | school_safety | 3347/147/146 | -0.198147 [-0.249731, -0.146562] | -0.048158 [-0.194163, 0.097847] | 0.149989 [-0.000289, 0.300266] |
| ICCS DNK / country_joint | class_openness | 4184/247/133 | -0.016118 [-0.063440, 0.031204] | -0.109583 [-0.230051, 0.010885] | -0.093465 [-0.213007, 0.026077] |
| ICCS DNK / country_joint | school_safety | 4184/247/133 | -0.369150 [-0.426707, -0.311594] | -0.401941 [-0.523156, -0.280727] | -0.032791 [-0.158968, 0.093386] |
| ICCS DNK / within_school_class | class_openness | 3011/178/64 | 0.003432 [-0.053550, 0.060415] | 0.076754 [-0.102524, 0.256032] | 0.073322 [-0.109246, 0.255890] |
| ICCS ITA / country_joint | class_openness | 2877/159/158 | 0.016198 [-0.050989, 0.083385] | 0.258334 [0.077907, 0.438761] | 0.242136 [0.043467, 0.440805] |
| ICCS ITA / country_joint | school_safety | 2877/159/158 | -0.180775 [-0.240419, -0.121132] | -0.295622 [-0.466888, -0.124357] | -0.114847 [-0.308953, 0.079258] |

These results change the main empirical interpretation. CEPS and ECLS estimates must be interpreted separately with their reported intervals; neither slope dominance nor a nonsignificant difference establishes construct validity or equivalence. Finland has a smaller between-class than within-class support/belonging association, but this is an observational difference in slopes on the same raw scale, not a construct-validity failure. ICCS country-level and within-school results vary. No common effect or cross-source coefficient magnitude should be inferred.

## Numerical discrepancy and invalid-source ledger

| Submitted claim / source | Verified provenance | Revision action |
|---|---|---|
| CEPS own=-.206, class context=-.038, alleged same-model contrast=-.126 | Interaction model own=-0.205653039, aggregate=-0.037892371; their arithmetic difference=-.167760668. Separate additive joint model own=-0.135921114, aggregate=-0.010386064, difference=-0.125535050 | Acknowledge mixed fitted models; withdraw old diagnostic and replace with corrected W/B model. Covariance can change a contrast SE, never its point estimate. |
| CEPS class=-.038, mismatch=-.061, alleged difference=.027 | Separate interaction models yield .023069055. Additive joint model class=-0.010386064, school-item classaggregate=-0.037058185, difference=0.026672121 | Acknowledge mixed-model comparison. Do not treat content-different item coefficients as isolated referent specificity. |
| CEPS gender validity | Source0male1female; old1/2 rule excluded every male, yielding female-only n8827 | Correct0/1; valid ID/school/class/grade filtering precedes deduplication and eligible duplicates are checked for contradictions. Rerun all CEPS estimates. Historical restricted-sample numbers remain only to trace errors. |
| CEPS18.4% ratio | Ratio of two independently standardized predictors’ interaction-model main coefficients, evaluated at centered counterpart | Remove as evidence of validity or loss of construct signal. |
| CEPS ICC1=.133/ICC2=.771 | ceps_public_audit.json concerns four-item teacher+peer support, not submitted final two-item class score. Original audit_ceps_public.py ICC2 denominator was not the standard ANOVA mean-score reliability formula. | Replace with correctly computed two-item reporter-pool diagnostics below. |
| ECLS C7WEIGHT described as sampling weight | Official NCES syntax defines C7WEIGHT as child composite physical WEIGHT IN POUNDS | Withdraw every original C7WEIGHT-weighted estimate and its bootstrap interval. Recover genuine C7PW0/C7PW1–90; use C7CW0 sensitivity. Body-weight availability is not an eligibility requirement. |
| ECLS old n1755/472/387 | Required positive/nonmissing physical body weight AND discarded all valid negative standardized SES values | Final corrected sample3623/538/433. Earlier mixed-outcome correction restored the sample to3609; the current official-outcome selection has its own documented flow and must not be decomposed as if it used that same outcome-completion rule. |
| ECLS W8SESL negative values | Original shared numeric parser treated every negative value as missing. Official W8SESL negative standardized values are valid; special missing codes are -7/-8/-9 | Preserve signed SES; source contains8809 valid SES records,4707 below0. This repairs a substantial unintended restriction toward higher socioeconomic status. |
| ECLS outcome called official internalizing | Two items are SDQ sadness/loneliness; three are NELS control/uselessness/no-good self-appraisal items | Use the available official eighth-grade C7SDQINT as the current main outcome, chosen for measurement content before seeing its new results. Keep the mixed internalizing_score only for an explicit common-sample outcome sensitivity. Prior C5SDQINR remains the distinct official third-grade revised internalizing composite. |
| ECLS ICC2=.067 | Prethreshold pool n9018,3737 groups, mean2.413 reporters/group | Replace main diagnostic with reporter pool supporting final modeled classes; keep prior statistic only in source history. |
| ECLS reproducibility description “at least half” | Actual extract/analysis requires4 of5 items (80%) | Correct Methods and replication description to4 of5. |
| TIMSS higher order | Original5−mean BSBM18 measures greater disruption | Correct domain label to disorder/disruption throughout text, figures and supplement. |
| ICCS lower bullying fear | Original5−IS4G18I makes high values stronger agreement with fear | Correct outcome label to greater bullying fear throughout text, figures and supplement. |

## Reliability and reporter counts

One-way unequal-group-size ANOVA uses n0=(N−sum(n_j²)/N)/(J−1), ICC1=(MSB−MSW)/(MSB+(n0−1)MSW). Mean-score reliability at reporter count n is n*ICC1/[1+(n−1)*ICC1]. The main descriptive ICC2 is evaluated at the ANOVA effective reporter count n0; the arithmetic-mean-n and minimum/maximum-count versions are also stored and explicitly alternate. These are unweighted descriptive observed-score diagnostics, not multilevel latent reliability estimates or complete construct validation. Unconditional class ICCs may include shared school variation.

| Source/pool | n/groups | Mean reporters | ICC1 | ICC2 at effective n0 |
|---|---|---|---|---|
| CEPS all class-score reporters supporting final classes | 19172/438 | 43.772 | 0.115049 | 0.850511 |
| CEPS outcome/covariate complete cases only | 17991/438 | 41.075 | 0.118135 | 0.846185 |
| ECLS all support reporters supporting final classes | 4038/538 | 7.506 | 0.048917 | 0.278450 |
| ECLS outcome/covariate complete cases only | 3623/538 | 6.734 | 0.045672 | 0.243666 |
| TIMSS FIN support/belonging modeled-class reporter pool | 4801/353 | 13.601 | 0.269687 | 0.833881 |

CEPS two-item alpha=0.634680; five-item outcome alpha=0.859079, current class/outcome alpha n17991/17991. ECLS five-item support alpha=0.895495 (n3608 complete on all five); official eight-item internalizing alpha=0.748492 (n3502 complete on all eight). ECLS retained context reporter counts are5–34 whereas outcome/covariate complete cases average6.734/class and range1–30. These populations are explicitly distinct. Low aggregate reliability remains an important attenuation limitation even after correction from .067 to 0.278.

The TIMSS country-level reliability objects describe broader source-valid domain pools. For any model-specific statement use its agreement_valid_reporters_in_modeled_classes object instead. In particular Finland support/belonging uses4801 valid context reporters in353 modeled classes, rather than the broader4816/368 source pool.

## CEPS fixed sensitivity block

| Model | n/classes/schools | Class support beta_B-beta_W [95% CI] |
|---|---|---|
| primary_joint | 17991/438/112 | 0.023920 [-0.158771, 0.206611] |
| class_cluster_sensitivity | 17991/438/112 | 0.023920 [-0.139756, 0.187597] |
| unweighted | 17991/438/112 | 0.046874 [-0.095405, 0.189153] |
| no_school_FE | 17991/438/112 | 0.020788 [-0.119833, 0.161410] |
| class_only | 17991/438/112 | -0.062997 [-0.183731, 0.057737] |
| minimum_10_reporters | 17982/437/112 | 0.026486 [-0.156273, 0.209244] |
| minimum_20_reporters | 17835/427/111 | 0.026643 [-0.157215, 0.210500] |
| minimum_30_reporters | 16578/373/106 | -0.010535 [-0.203229, 0.182158] |
| one_of_two_class_items | 18107/438/112 | 0.019153 [-0.165610, 0.203916] |
| four_of_five_distress_items | 18173/438/112 | 0.025730 [-0.156266, 0.207725] |
| class_size_lower | 4521/159/59 | 0.094542 [-0.445692, 0.634776] |
| class_size_middle | 8771/200/73 | -0.119757 [-0.473516, 0.234002] |
| class_size_upper | 4699/79/31 | 0.018276 [-0.528852, 0.565405] |

The 39/54 cutpoints are the 25th/75th percentiles of valid class-reporter counts repeated over current analytic student records. They are not unique-class-size quartiles or enrolled class sizes. These selected stratum slopes are exploratory. Comparing significance levels is not a test of moderation; no interaction test was performed.

## Reproducibility and checks

Independent verification completed 71 arithmetic/reparameterization checks, all passed. These include every B−W difference, equivalence of the own-score/full-mean and mean/deviation fitted values, and the unequal-size LOO identity. All fitted formula designs have full rank. Every supplied/reconstructed replicate successfully fit a full-rank common signal matrix. School fixed effects are residualized separately for each replicate; removed schools do not create unidentified signal coefficients. No replicate was silently dropped.

ECLS public raw catalog was recovered read-only from the existing F archive into a fresh D temporary working copy. The official15-record fixed-field layout was used to recover C7PW0/C7PW1–90 and C7CW0/C7CW1–90. The earlier support/mixed-outcome/prior/SES verification found agreement over every common valid record, but the old extract additionally lost4707 valid negative SES values. The current extract adds the official C7SDQINT and eight raw items plus GENDER; its complete-eight-item mean differs from the provided two-decimal composite by at most0.005. The fresh parser retains signed SES and uses its exact provider missing codes. School identifiers are preserved as character fields; old numeric-only school codes had different formatting but a one-to-one mapping to the new codes, while English-class codes match exactly. The fresh case-level extract is private work data and must not be distributed publicly. Input file sizes/hashes and runtime package versions are in stats_runtime_manifest.json; official syntax locations and extraction checks are in stats_ecls_survey_extraction_audit.json. The source config supports alternate provider-file locations.

Commands (adapt paths when reproducing; do not redistribute raw provider/case-level files):

    python stats_extract_ecls.py --child-file <childk8p.dat> --syntax-file <official_SPSS.sps> --output <new_private_extract.csv>
    python stats_reanalysis.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>
    python stats_checks.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>
    python round2_measurement_sensitivity.py --project-root <original_project_root> --source-config <JSON_input_paths> --output-dir <D_output_directory>

The current workstation runtime is Python3.12 with pandas3.0.5 and statsmodels0.14.6; bundled Python lacked statsmodels, so the existing statistical runtime was used without installing anything. Scripts set dont_write_bytecode and work output paths on D:. The source-config keys are ceps, ecls, timss_root and iccs_root. Reproduction requires the original CEPS historical JSON provenance and ECLS source-audit JSON as well as provider inputs. File hashes/paths belong in reproducibility records, not article body prose.

## Interpretation boundaries requiring manuscript changes

1. Withdraw the old construct-homogeneity gate and every claim that stronger own-score coefficients imply a validity difference. The corrected W/B contextual difference describes outcome associations, not the psychometric status of a group construct.
2. CEPS school-item comparison changes both content and referent. No slope comparison isolates referent specificity; intervals containing zero do not establish equivalence. ICCS also changes content/referent simultaneously.
3. Moderate individual internal consistency, finite reporter counts, shared respondent affect/response style, aggregate sampling error, and prior/covariate selection can explain within/between patterns. Replicate covariance does not correct latent measurement error or common-method bias.
4. School fixed effects control school-average nuisance patterns but do not randomize classes or remove selection/confounding within schools. ECLS between-class slopes additionally mix school differences because that model does not use school fixed effects.
5. CEPS and ECLS outcomes concern self-reported symptoms; TIMSS and ICCS are school-experience proxies. Their directions and effect magnitudes are not pooled, and these observational cross-sectional models do not demonstrate a classroom intervention effect.
6. Old body-weight-weighted ECLS coefficients, mixed-model CEPS contrasts, the18.4% ratio, mislabeled TIMSS order and ICCS fear results must not survive in the abstract, tables, captions, supplement or response letter as current findings.

## Official source locators verified by the source-audit agent

- NCES ECLS-K official SPSS layout: https://nces.ed.gov/ECLS/data/ECLSK_Kto8_child_SPSS.sps . C7WEIGHT physical pounds; C7PW0 current parent/child full-sample weight; C7CW0 child-only full-sample weight; J71CLASS spring2007 English-class number; C5SDQINR revised third-grade internalizing composite.
- NCES K–8 user manual part1: https://nces.ed.gov/ECLS/data/ECLSK_K8_Manual_part1.pdf . §4.8.5.2 printedp4-47 supports C7PW0 for parent data combined with child assessments; §4.9.1 printedpp4-50–4-51 explains JK2 sum-of-squares covariance,90replicates and approximately76design df; Table4-18 printedp4-54 supplies weight family names.
- TIMSS2019 Methods, Chapter14: https://timss.bc.edu/timss2019/methods/pdf/T19_MP_Ch14-estimating-standard-errors.pdf . Official full JRR150replicate factor0.5 used in the prior archived design code and reimplemented here.
- ICCS2022 user guide: https://www.iea.nl/sites/default/files/2024-09/ICCS%20User%20Guide.pdf . Supplied SRWGT JK2 scheme; corresponding SPSS item labels/value labels were independently read for coding direction.

## Fixed measurement and ordinal-control sensitivities

These models were selected before inspecting their new results. They preserve the current main specification and are reported regardless of significance. CEPS item-specific means use the same two-item-complete reporter pool, with separate school-belonging adjustment. All five ordinal controls are entered categorically in one joint-model sensitivity. ECLS official/mixed outcomes are compared on a shared valid sample.

| Source/model | Domain | n/classes/schools | beta_W | beta_B | beta_B-beta_W |
|---|---|---|---|---|---|
| CEPS / single_classmategood | classmategood | 17991/438/112 | -0.098643 [-0.121278, -0.076008] | -0.011048 [-0.184682, 0.162586] | 0.087595 [-0.086859, 0.262048] |
| CEPS / single_classmategood | school_belonging_aggregated_to_class | 17991/438/112 | -0.101826 [-0.123043, -0.080609] | -0.248789 [-0.385810, -0.111767] | -0.146963 [-0.288701, -0.005224] |
| CEPS / single_classgood | classgood | 17991/438/112 | -0.060171 [-0.079269, -0.041073] | -0.076547 [-0.202513, 0.049419] | -0.016376 [-0.137399, 0.104648] |
| CEPS / single_classgood | school_belonging_aggregated_to_class | 17991/438/112 | -0.115937 [-0.132544, -0.099331] | -0.177667 [-0.330389, -0.024945] | -0.061729 [-0.218582, 0.095123] |
| CEPS / all_ordinal_controls_categorical | class_support | 17991/438/112 | -0.117531 [-0.141064, -0.093999] | -0.102164 [-0.289179, 0.084851] | 0.015367 [-0.166320, 0.197054] |
| CEPS / all_ordinal_controls_categorical | school_belonging_aggregated_to_class | 17991/438/112 | -0.092779 [-0.111319, -0.074239] | -0.174934 [-0.338627, -0.011241] | -0.082155 [-0.250057, 0.085746] |
| ECLS / official_internalizing_common_sample | support | 3608/538/433 | -0.096309 [-0.140756, -0.051862] | -0.054267 [-0.121714, 0.013179] | 0.042042 [-0.043568, 0.127651] |
| ECLS / historical_mixed5_common_sample | support | 3608/538/433 | -0.265605 [-0.302674, -0.228537] | -0.259963 [-0.327216, -0.192711] | 0.005642 [-0.075570, 0.086854] |
