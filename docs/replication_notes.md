# Replication notes

The course data dictionary defines the core variables and `STATUS2` codes. It
also defines `PA1` as the northeastern Philadelphia suburbs and `PA2` as the
Easton area. The original paper documents the regional construction used in
the geographic specifications: New Jersey is divided into North, Central, and
South, while eastern Pennsylvania is divided into the Allentown--Easton area
and the northern suburbs of Philadelphia. Accordingly, `NORTHJ=1` identifies a
store in northern New Jersey; together with `SOUTHJ` and `CENTRALJ`, it forms
the three New Jersey region indicators. For Pennsylvania stores these New
Jersey indicators are zero. The published-style specifications use `SOUTHJ`,
`CENTRALJ`, `NORTHJ`, and `PA1`, with the `PA2`/Easton category as the omitted
reference group.

The original paper also defines the New Jersey shore exclusion used in the
robustness analysis. `SHORE=1` identifies a store in a town along the New
Jersey shore; the paper's corresponding robustness row excludes 35 such
stores because they may have a different seasonal employment pattern. Thus
`SHORE` is not a core regression control and is used only for the explicitly
labelled geographic-exclusion robustness check.

The paper supports the economic/geographic interpretation of `NORTHJ` and
`SHORE`. For full computational reproducibility, any available town-level
mapping used to construct the public indicators should still be documented;
the analysis does not infer a town boundary that is absent from the supplied
data.

The original `SHEET` identifier is duplicated for two observations. The
workflow preserves the raw value and creates `store_id_unique` for local
diagnostics and future merges; no row is dropped because of the duplicate.

The raw input is not committed. A clean checkout must receive the course
provided `public.csv` through the documented input path before running the
analysis. The generated `data/processed/analysis_panel.csv` is a local
derived file and is ignored by Git until the researcher confirms that its
redistribution is permitted.
