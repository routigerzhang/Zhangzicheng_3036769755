# Card and Krueger (1994) replication

This project reproduces the course-assigned results from Card and Krueger's
study of the 1992 New Jersey minimum-wage increase and adds an exploratory
ownership-heterogeneity extension.

## Input data

The course-provided `public.csv` is not committed to this repository. Place it
in `data/raw/` or provide its absolute path to the script. The input must have
410 rows and 46 columns.

## Run

From this project directory:

```powershell
python src/run_analysis.py --input "C:\path\to\public.csv"
```

The workflow creates:

- `outputs/tables/table2.csv`: key means by state and survey wave;
- `outputs/tables/table3.csv`: employment levels, changes, and DiD comparisons;
- `outputs/tables/table4.csv`: reduced-form employment models;
- `outputs/tables/replication_comparison.csv`: selected published-versus-replicated coefficients;
- `outputs/tables/extension_ownership_heterogeneity.csv`: GAP interacted with company ownership;
- `outputs/tables/robustness_checks.csv`: alternative part-time weights, sample exclusions, leave-one-chain-out estimates, closure coding, and permutation inference;
- `outputs/figures/figure1.png`: starting-wage distributions;
- `outputs/Card_Krueger_Empirical_Report.docx`: formatted empirical report for submission;
- `outputs/tables/validation_checks.csv`: sample counts and headline checks;
- `docs/ai_use_disclosure.md`: completed AI-use disclosure draft for final researcher review;
- `data/processed/analysis_panel.csv`: locally generated derived analysis data.

The processed row-level file is ignored by Git for the same reason as the raw
input. Keep it locally for review and document the access rules before any
public submission.

## Main definitions

FTE employment is `EMPFT + 0.5 * EMPPT + NMGRS`.

The treatment-intensity variable is:

```text
GAP = 0                                  for Pennsylvania
GAP = max(0, (5.05 - WAGE_ST) / WAGE_ST) for New Jersey
```

Permanent closures (`STATUS2 == 3`) have post-period FTE set to zero.
Renovation, highway-construction, and mall-fire closures (`STATUS2` in
`{2, 4, 5}`) are missing in the main employment outcome and set to zero only
in the corresponding sensitivity row of Table 3.

The Table 4 sample follows the published result: both FTE values and the
baseline wage must be available; the post-period wage is required except for
permanently closed stores, because `GAP` uses the baseline wage. This produces
the published sample size of 357 observations in the supplied data.

## Extension

The extension asks whether the employment response to the minimum-wage shock
differs between company-owned and franchise stores. It estimates `GAP`,
`CO_OWNED`, and `GAP * CO_OWNED`, controlling for chain and region indicators.
The interaction is descriptive and should be interpreted with the limited
sample size and two-wave design in mind.

## Robustness checks

The robustness file treats the published NJ-dummy specification as the
reference and reports changes in the FTE construction, geographic and survey
follow-up exclusions, leave-one-chain-out estimates, the temporary-closure
coding sensitivity, and a randomization-inference diagnostic. The permutation
test preserves the observed number of New Jersey stores and uses a fixed seed
for reproducibility; it is reported as a diagnostic rather than as a substitute
for the difference-in-differences identifying assumption.

## Reproducibility and AI disclosure

The final report is provided in DOCX format and records the input source,
sample rules, closure coding, deviations from the original paper, and checks
used to validate the generated tables and figure. Review
`docs/ai_use_disclosure.md` against the actual project history before
submission. Regional variable definitions are documented in
`docs/replication_notes.md`: `PA1` and `PA2` come from the course data
dictionary, while the New Jersey region indicators and the `SHORE` exclusion
are documented from the original paper. Confirm the final report format,
town-level mapping documentation if available, data-redistribution decision,
GitHub URL, and clean-checkout reproduction test against the course portal.
