# Replication notes

The course data dictionary defines the core variables and `STATUS2` codes.
The supplied CSV also contains `NORTHJ` and `SHORE`; these fields should be
documented from the original source codebook before using them in a final
report. The code uses `SOUTHJ`, `CENTRALJ`, `NORTHJ`, and `PA1` as region
controls, with the `PA2`/Easton category as the omitted reference group.

The original `SHEET` identifier is duplicated for two observations. The
workflow preserves the raw value and creates `store_id_unique` for local
diagnostics and future merges.

