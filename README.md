# Additional file 2: analysis code and aggregate results

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23340448.svg)](https://doi.org/10.5281/zenodo.23340448)


Reproducibility package for **Classroom perceptions and adolescent wellbeing at individual and classroom levels**. Reviewer-prompted revision; exploratory and **not preregistered**. No raw provider data, participant records or private working extracts are included.

## Contents

- `scripts/`: five executable Python scripts for field extraction, reanalysis, independent checks and report generation.
- `results/`: final aggregate JSON/CSV, independent checks, the original-runtime/input hash manifest with private paths omitted, a nonidentifying extraction audit and statistical report.
- `data_audit/ceps/ceps_redesign_tests.json` and `data_audit/eclsk/eclsk_class_context_audit.json`: historical aggregate records for tracing withdrawn numbers, not current results or preregistrations. Keep this directory layout: the code reads it relative to `--project-root`.
- `config/input_paths.example.json`: fictional public paths; replace with your own locations.
- `documentation/`: provider/source notes and item content map.
- `figures/`: optional SVG figures of estimands and verified aggregate coefficients.
- `package_manifest.json`: checksums of the packaged files, original-code/output checksums and distribution-only changes.

## Runtime

The analysis used Python 3.12.10, numpy 2.5.1, pandas 3.0.5, scipy 1.18.0, statsmodels 0.14.6 and pyreadstat 1.3.6. `requirements.txt` records these exact package versions. If an environment needs dependencies, run `python -m pip install -r requirements.txt` in that environment. No installation or analysis is performed automatically by this package. Set BLAS thread counts to 1 for comparable small regression runtimes. GPU hardware is unnecessary.

The five documented CLI interfaces were verified with `--help` in the packaged copies. Distribution edits replace workstation-private defaults only; statistical logic is unchanged. Round2 repaired verified CEPS source coding and adopted the available official ECLS outcome. Package default/path edits preserve the current verified code logic and aggregate values.

## Minimal provider inputs

Acquire these files yourself and retain the originals read only:

1. CEPS `CEPS_baseline_pooled.dta`, the pooled derivative identified in SOURCE_NOTES.md.
2. ECLS NCES public `childk8p.dat`, expanded from its original split archive, and official `ECLSK_Kto8_child_SPSS.sps`. If expanding an archive, write a fresh working copy on D:; the extractor can read an existing expanded read-only file on F: or D:. Generate a new private CSV using the command below. The extractor refuses to replace an existing output CSV.
3. TIMSS directories containing `FIN/bsgfinm7.sav`, `ZAF/bsgzafm7.sav`, `KOR/bsgkorm7.sav`.
4. ICCS `ISGNORC4.sav`, `ISGSWEC4.sav`, `ISGPOLC4.sav`, `ISGFRAC4.sav`, `ISGDNKC4.sav`, `ISGITAC4.sav` in one directory.
5. The two historical aggregate JSON inputs are already included under `data_audit/`.

The source config's four keys are `ceps`, `ecls`, `timss_root`, `iccs_root`. Set all four to avoid reliance on legacy fallbacks. On the authors' Windows convention, provider raw materials are stored on F: and derived CSVs/results on D:. The reanalysis explicitly enforces D: output on Windows. Other systems accept ordinary paths: edit the config and substitute platform-specific command paths. No public example points to the authors' private data locations.

## Reproduce all sources

Extract this package into a new D: directory, for example `D:\MLWork\BMC_Classroom_Revision_Reproduction\package`, and run the following PowerShell commands from that directory. Adjust the raw input paths, then edit or copy `config/input_paths.example.json` before running. Choose a new extract name if the example CSV already exists, and update the `ecls` config key to match.

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'

python -B scripts/stats_extract_ecls.py --child-file 'F:\AcademicData\BMC_Classroom_Revision\raw\eclsk\childk8p.dat' --syntax-file 'F:\AcademicData\BMC_Classroom_Revision\raw\eclsk\ECLSK_Kto8_child_SPSS.sps' --output 'D:\MLWork\BMC_Classroom_Revision_Reproduction\datasets\ecls_grade8_survey_extract.csv' --audit-output 'D:\MLWork\BMC_Classroom_Revision_Reproduction\results\stats_ecls_survey_extraction_audit.json'

python -B scripts/stats_reanalysis.py --project-root . --source-config config/input_paths.example.json --output-dir 'D:\MLWork\BMC_Classroom_Revision_Reproduction\results'

python -B scripts/stats_checks.py --project-root . --source-config config/input_paths.example.json --output-dir 'D:\MLWork\BMC_Classroom_Revision_Reproduction\results'

python -B scripts/round2_measurement_sensitivity.py --project-root . --source-config config/input_paths.example.json --output-dir 'D:\MLWork\BMC_Classroom_Revision_Reproduction\results'

python -B scripts/stats_build_report.py --results-dir 'D:\MLWork\BMC_Classroom_Revision_Reproduction\results'
```

`--reference-extract` is optional for comparing an older private ECLS extraction; it is unnecessary for fresh reproduction and no older private extraction is included. `--sources` is an optional local partial-rerun feature, but complete reproduction should use the default all-source command above in a fresh result directory. Packaged JSON source paths are deliberately anonymized: do not use them as input paths for a partial rerun. Supply actual provider locations through the config and complete all-source run.

## ECLS extraction and inference rules

The extractor reads 15 physical records per child and official field positions from SPSS syntax. Raw decimal marks are parsed directly without an extra decimal division. It preserves school/class character identifiers and recovers the support/outcome fields, third-grade C5SDQINR, signed W8SESL, C7PW0/C7CW0 and 90 replicate weights for each family. Ordinary negative W8SESL values are valid; only −7/−8/−9 are missing. **C7WEIGHT is physical child weight in pounds and is never an analysis weight or current eligibility rule.** The current main outcome is the official eight-item C7SDQINT internalizing composite, selected before new outcome-model results. `internalizing_score` remains the distinct historical mixed two-SDQ/three-NELS score, used only in a common-sample measurement comparison. The extractor also reads GENDER for descriptions; it does not determine analytic eligibility.

Primary ECLS inference uses genuine C7PW0 and 90 C7PW JK2 replicates, variance equal to the sum of squared replicate deviations and normal 95% intervals. C7CW0 is a child-weight reweighting sensitivity on the same parent-complete main cases, not a different population-eligibility analysis. School sandwich and bootstrap intervals are separately labeled sensitivities; the school bootstrap uses 1000 resamples and seed 20261005. JK2 intervals condition on observed unweighted reporter means and the complete-case set. School bootstrap resamples current schools, not the original kindergarten sampling PSUs. Prior response selection and population-aggregate/latent measurement error are not corrected by these weights or intervals.

## Added fixed measurement checks

`round2_measurement_results.json` contains CEPS two separately fitted single-item mean/deviation models, each retaining the17,991-person main sample, common two-item-complete reporter pool, school-belonging adjustment, weighting and school-cluster inference. One joint sensitivity makes all five ordinal controls categorical. ECLS compares official C7SDQINT and the historical mixed five-item outcome on their shared3,608-person valid sample with the same controls/C7PW JK2 method. `round2_measurement_coefficients.csv` is their aggregate coefficient table; `paired_terms` maps each domain to its W/B fields. No model/outcome is selected by statistical significance. `round2_ceps_provider_comparison.json` records that eligible canonical model/age fields and ID sets match the old input, and all reproduced historical parameters match the preserved prior provenance exactly.

## Output schema and main entries

`stats_verified_results.json` has `CEPS`, `ECLS`, `TIMSS`, `ICCS` and estimand/unit metadata. CEPS/ECLS contain `models` arrays; TIMSS/ICCS contain country objects, each with `models`. Models identify formula, weights, sample counts and uncertainty. `terms` and `contextual_associations` provide estimate, SE, lower/upper 95% bounds and two-sided p. The contextual difference is beta_B minus beta_W in the same model with its covariance. LOO entries have own/peer conditional coefficients and no homogeneity contrast.

Use CEPS `primary_joint`; ECLS `primary_model_label = weighted_C7PW0_JK2`; TIMSS FIN `support_BSBGSSB`. Report all ICCS countries/domains and eligible within-school fits as exploratory. ECLS primary provider-JK2 bounds are in the normal term/contrast fields; alternative school-bootstrap bounds are in `school_bootstrap` objects on school-cluster models.

`stats_coefficients.csv` contains aggregate model effects only. Raw outcome points per original predictor point are the manuscript default; optional `standardized_Y_*` columns scale the outcome only. Within/between predictors have the same raw increment. Do not pool surveys or compare different outcome-scale magnitudes. Reporter ICC(2) values for the article use `icc2_at_effective_n0`, not separately the arithmetic group size. The final ECLS sample is 3623 / 538 classes / 433 schools, with 4038 support reporters supporting those modeled classes.

The original runtime manifest retains input sizes/hashes and versions. Its output hashes identify the original audited bytes before path redaction; `package_manifest.json` identifies public packaged bytes. The aggregate CSV is byte-identical to the audited CSV, and all numeric JSON fields are unchanged. An actual rerun will record your own local paths and hashes; do not redistribute a rerun's private working data or unredacted local config.

## Added in this version: figure, table and verification pipeline

The four result tables and both figures were re-set for the manuscript page width. The changes are presentational only; no statistical analysis was rerun and no estimate changed.

- `scripts/visual_20261013_figures.py` builds Figure 1 (four estimand panels) and Figure 2 (three vertical forest panels) from the frozen aggregate estimates, using the SciencePlots science/nature styles adapted to the manuscript text width. It writes vector PDF and SVG plus a 1200 dpi PNG for each figure.
- `scripts/figstyle.py` is the house style module the figure script imports, shipped here so the figures build without any external skill directory.
- `scripts/visual_20261013_tables.py` writes the four replacement table blocks (`tables/tables_nature.tex`) and an audit manifest. It reads the existing tables and never edits the manuscript.
- `scripts/visual_20261013_numeric_check.py` is a read-only check of the four tables and of the Figure 2 vector PDF: every point estimate and interval endpoint is compared with `results/stats_verified_results.json`.
- `scripts/visual_20261013_export_audit.py` records figure export properties such as page size, fonts and embedded raster count.
- `scripts/visual_20261013_integrate.py`, `visual_20261013_compile.py` and `visual_20261013_publish.py` apply the verified blocks to a candidate copy, compile it and publish it after checksum checks.
- `scripts/audit_displayed_values.py` counts and checks every displayed numeric value in the manuscript and the supplementary tables under a single tokenizer rule.
- `results/visual_20261013_*.json` and the two `*_review.md` files are the audit artifacts of that pipeline (the review files are the original working notes).
- `figures/` carries PDF, SVG and a 1200 dpi PNG for both figures; `tables/tables_nature.tex` carries the four tables.

## Paths

Every script resolves the package root from its own location, so the archive runs after extraction. `config/input_paths.example.json` lists the provider files with fictional paths: copy it, replace the paths with your own locations, and keep the provider data read only. `MIKTEX_BIN` can override the LaTeX binary directory used by `visual_20261013_compile.py`.
