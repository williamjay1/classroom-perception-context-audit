# Visual numerical review, 13 October 2026: PASS

Stage: final_candidate; UTC: 2026-10-13T03:25:04.156829+00:00

Read-only audit against the already verified aggregate results. No model was rerun and no production figure, table, prose or data file was modified. Table values were mapped independently to model/sample JSON fields; the figure production code was not imported. PDF marker and interval positions were recovered from vector paths using printed axis tick calibration.

Four tables: 44 data rows, 220 numeric values. Figure 2: 9 marker/CI pairs, 27 independently checked numerical coordinates. Printed estimate/CI annotation groups: 9; annotation equality=True.

| Table | Numeric values | Result |
|---|---:|---|
| tab1 | 33 | PASS |
| tab2 | 27 | PASS |
| tab3 | 80 | PASS |
| tab4 | 80 | PASS |

## Figure 2 numerical audit

| Source | Estimand | Expected estimate | Expected CI lower | Expected CI upper | Maximum vector-derived error | Result |
|---|---|---:|---:|---:|---:|---|
| CEPS | within | -0.120042910905 | -0.144806724953 | -0.095279096857 | 1.59934109e-08 | PASS |
| CEPS | between | -0.096122849388 | -0.283690032965 | 0.091444334189 | 2.35033385e-08 | PASS |
| CEPS | between minus within | 0.023920061517 | -0.158771306441 | 0.206611429475 | 2.24178345e-08 | PASS |
| ECLS K Grade 8 | within | -0.093207843537 | -0.136771579845 | -0.049644107230 | 1.30805664e-08 | PASS |
| ECLS K Grade 8 | between | -0.048712192753 | -0.116242007756 | 0.018817622251 | 5.94164436e-09 | PASS |
| ECLS K Grade 8 | between minus within | 0.044495650785 | -0.040547802497 | 0.129539104067 | 1.57220053e-08 | PASS |
| TIMSS Finland | within | 1.263001064408 | 1.169852902515 | 1.356149226301 | 1.21241447e-07 | PASS |
| TIMSS Finland | between | 0.787554305434 | 0.417518221239 | 1.157590389629 | 1.74737526e-07 | PASS |
| TIMSS Finland | between minus within | -0.475446758974 | -0.857664818130 | -0.093228699817 | 4.8080261e-08 | PASS |

## Preservation and source identification

- Figure/table-block-excluded document body: exact equality=True; equality after whitespace normalization=True.
- Independently captured initial normalized body SHA256: `d1bbe3a6ceccea390622c254332bda23345f2fbe71b45da7f33e663cbbe18d3f`.
- An external parallel task changed only the abstract at 11:14:24 on 13 October. The parent confirmed this was outside the visual task and instructed preservation of that newest text. The fresh text baseline is therefore temp/visual_20261013_text_baseline/manuscript.tex (51910 bytes; SHA256 ec0969f47284b8a27e6e34a117b855d478360fbd2577a2a4665387439c6dfffe). The earlier 52119-byte baseline remains preserved and was not overwritten.
- Current manuscript SHA256: `a3d9dc66857673c4f5dc4a50b9116f0c7388432efba1c9c0ce7ef933a9fb32e0`.
- Verified results SHA256: `09ef4aeaf5f99f1740d723e6635abf347facbbae41fcf97d796b45f4a8bcc8bc`.
- Round-two measurement results SHA256: `74cb6049fd5be28e5d063d344ff50343381c66d4befe09801339096336d3a72e`.
- Figure_1.pdf SHA256: `f4999fc29475b59946e3022f06fdcc4a4171ad45027acccd084816c8bb0b537c`.
- Figure_2.pdf SHA256: `1a13efb0028e5a00c1ff92551dc2626b46d016adbb61982b3b4629a70023a9fb`.

## Numerical or label risks

No numerical discrepancy was found. Final native rendering and semantic verification is recorded below.

The primary CEPS joint model is the source for its panel. ECLS uses official C7SDQINT with the C7PW0/90 JK2 primary intervals; TIMSS Finland uses support_BSBGSSB with its 150-replicate JRR intervals. These source-specific raw units must remain in the panel labels and separate axes. The contextual point is the same-model between-minus-within estimate; no LOO coefficient belongs in this figure. Table 3 additionally depends on round2_measurement_results.json for its three measurement/categorical-control rows.

## Final native render and semantic preservation checks

- manuscript.tex: figure/table-block-excluded body is byte-for-byte equal after file newline decoding; all six float captions and all four complete table notes are unchanged. The marked text retains its original blue markup outside these blocks.
- manuscript_marked.tex: figure/table-block-excluded body is byte-for-byte equal after file newline decoding; all six float captions and all four complete table notes are unchanged. The marked text retains its original blue markup outside these blocks.
- Both final candidate figure PDFs were rendered locally and inspected through the native image tool. Panel/row labels, raw-unit axes, negative-affect/internalizing/belonging outcomes, same-model contextual contrast and the separate LOO sensitivity label are correct. No causal/measurement-validity arrow or substituted LOO contrast is introduced.
- Figure 2 contains nine source-appropriate printed estimate/CI annotation triples. Their 27 displayed values agree with the verified rounded numbers, independently of the geometric test.
- The new table groups preserve the joint class perception, joint school-belonging and class-items-only model order. Table 3 preserves all sixteen specifications. The interval brackets in the final table macro change presentation only.
- The initial assessment found no substantive statistical label error. The external concurrent abstract update was retained under the parent's explicit instruction; it was not caused by this visual task. Final candidate numeric and semantic review: PASS.

Marked counterpart: the numeric token matrices of all four candidate marked tables are exactly identical to the independently checked clean tables (220 corresponding values, without adding these duplicate occurrences to the unique 220-value count).
