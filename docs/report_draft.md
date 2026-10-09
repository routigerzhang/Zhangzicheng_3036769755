# Draft empirical report: Card and Krueger (1994)

> Status: working draft generated from the reproducible workflow. It should be reviewed against the original paper, the course rubric, and the researcher’s own interpretation before submission.

## 1. Research question and motivation

This project replicates Card and Krueger’s (1994) question: did New Jersey’s April 1, 1992 increase in the statutory minimum wage from $4.25 to $5.05 reduce employment at fast-food restaurants? The economic mechanism is theoretically ambiguous. A higher wage floor raises labor costs and could reduce employment, but firms may adjust through prices, turnover, hours, effort, or monopsony-related channels. The paper’s empirical contribution is to compare New Jersey restaurants exposed to the increase with restaurants in eastern Pennsylvania, where the minimum wage remained $4.25.

## 2. Data, sample, and variable construction

The replication uses the supplied public survey data: 410 restaurants, including 331 in New Jersey and 79 in Pennsylvania. Restaurants were surveyed before the policy change in February–March 1992 and again in November–December 1992. The assigned replication covers Tables 2–4 and Figure 1; the restricted data needed for Table 1 are not used.

Full-time-equivalent employment is defined as `EMPFT + 0.5 * EMPPT + NMGRS`. Permanent closures are coded as zero post-period employment. Temporary, renovation, highway-construction, and mall-fire closures are missing in the main post-period outcome and are set to zero only in the explicit closure-coding sensitivity check. The Table 4 analysis requires observed pre- and post-period FTE employment, baseline wage, and post-period wage unless the restaurant permanently closed; this yields 357 observations.

The treatment-intensity variable is `GAP = max(0, (5.05 - WAGE_ST) / WAGE_ST)` for New Jersey and zero for Pennsylvania. It measures the proportional wage increase implied by the statutory change relative to the restaurant’s starting wage.

## 3. Empirical design

The core reduced-form comparison is a difference-in-differences design:

`(NJ after - NJ before) - (PA after - PA before)`.

The identifying assumption is parallel trends: absent the New Jersey policy, employment changes in the two nearby comparison regions would have been similar. The design is attractive because the states are geographically adjacent and the survey spans the policy change, but the data contain only one pre-period, so the assumption cannot be tested with event-study-style pre-trends.

## 4. Core replication results

The unbalanced Table 3 DiD estimate is **2.75 FTE employees** (SE 1.34), extremely close to the published value of 2.76. The balanced-sample estimate is 2.75, and the temporary-closures-as-zero sensitivity estimate is 2.51. These estimates do not support a negative employment effect in this sample; they indicate that New Jersey employment increased relative to eastern Pennsylvania.

In the Table 4 reduced-form regression, the New Jersey indicator is **2.33** (SE 1.19). The continuous treatment-intensity specification estimates a GAP coefficient of **15.65** (SE 6.08). The main coefficients are close to the original paper’s reported values, with the region-control specification showing the largest but still modest numerical difference. The replication comparison is documented in `outputs/tables/replication_comparison.csv`.

## 5. Independent extension: ownership heterogeneity

The extension asks whether the employment response differs between company-owned and franchise stores. The model adds `GAP × CO_OWNED` to the chain and region controls. The GAP coefficient for franchise stores is 17.08; the interaction is -14.46; and the implied GAP effect for company-owned stores is 2.61. The interaction is not interpreted as definitive evidence of heterogeneous treatment effects: its uncertainty is substantial, and the design has only two survey waves. The economically responsible conclusion is that the point estimates suggest a possible ownership difference, but the data do not establish it precisely.

## 6. Robustness and validation

The workflow includes alternative part-time weights of 0.4 and 0.6, exclusion of Shore stores, a restriction to stores with at most two first-wave call attempts, leave-one-chain-out estimates, an explicit temporary-closure coding check, and a 2,000-draw permutation diagnostic that preserves the number of treated stores. The leave-one-chain-out NJ-dummy estimates are: Burger King: 1.51; KFC: 3.06; Roy Rogers: 2.42; Wendy's: 2.05. The temporary-closure sensitivity is 2.51; the permutation p-value for the baseline NJ-dummy coefficient is 0.050. These checks are diagnostics around the baseline design, not independent proof of identification.

Validation checks confirm the expected 410-by-46 input shape, the 357-observation Table 4 sample, and the close match between the headline replication coefficients and the original paper. The generated tables, figure, processed panel, and validation file are produced by a single command after the input data are placed in the documented location.

## 7. Limitations

Several limitations matter for interpretation. First, the study has one pre-treatment survey wave, limiting direct assessment of parallel trends. Second, restaurant employment is survey-reported and may contain measurement error. Third, closure coding and missing post-period values can affect the estimand, which is why the workflow reports alternative coding explicitly. Fourth, the sample is concentrated in four fast-food chains and two neighboring regions in 1992; external validity to other industries, locations, or later minimum-wage changes is limited. Finally, some regional indicators in the public file are not fully defined in the supplied data dictionary, so their use should be documented and checked against the original paper before final submission.

## 8. Conclusion

The replication recovers the central Card–Krueger finding: the 1992 New Jersey minimum-wage increase is not associated with a decline in fast-food employment relative to eastern Pennsylvania in the supplied public data. The result is numerically stable across the main closure and sample checks. The ownership extension is useful as a motivated exploratory analysis, but its interaction estimate should be presented as suggestive rather than conclusive. The final submission should pair this report draft with the code, input-access instructions, AI-use disclosure, and a short explanation of any remaining implementation differences from the original paper.
