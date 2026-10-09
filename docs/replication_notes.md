# Replication notes

The course data dictionary defines the core variables and `STATUS2` codes. It
also defines `PA1` as the northeastern Philadelphia suburbs and `PA2` as the
Easton area. The supplied CSV contains `NORTHJ` and `SHORE`, but those two
fields are not defined in the supplied data dictionary. The core replication
does not use `SHORE` as a control. The code uses `SOUTHJ`, `CENTRALJ`,
`NORTHJ`, and `PA1` as region controls in the published-style specifications,
with the `PA2`/Easton category as the omitted reference group. `SHORE` is used
only for an explicitly labelled geographic-exclusion robustness check.

Before submission, confirm the exact definitions of `NORTHJ` and `SHORE`
against the original paper or source codebook and reproduce that documentation
in the empirical report. The definitions of `PA1` and `PA2` are already
documented in the supplied data dictionary. If the source codebook for
`NORTHJ` or `SHORE` cannot be recovered, retain the robustness result as a
data-provided indicator check and state this limitation explicitly rather than
assigning an unsupported geographic interpretation.

The original `SHEET` identifier is duplicated for two observations. The
workflow preserves the raw value and creates `store_id_unique` for local
diagnostics and future merges; no row is dropped because of the duplicate.

The raw input is not committed. A clean checkout must receive the course
provided `public.csv` through the documented input path before running the
analysis. The generated `data/processed/analysis_panel.csv` is a local
derived file and is ignored by Git until the researcher confirms that its
redistribution is permitted.
