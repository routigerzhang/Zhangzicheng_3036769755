# AI-use disclosure

## Tool and timing

This project used OpenAI Codex as an AI-assisted research and programming
assistant during the project workflow on 2026-10-09. The researcher remains
responsible for the final data choices, code, statistical interpretation,
citations, and submitted report.

## Where AI assistance was used

AI assistance was used to:

- organize the end-to-end replication workflow from the course instructions;
- translate the paper's definitions into executable Python code;
- construct FTE employment, wage-gap, closure, region, and ownership variables;
- implement the assigned Tables 2–4 and Figure 1;
- implement the ownership-heterogeneity extension;
- add alternative part-time weights, sample exclusions, leave-one-chain-out
  checks, closure-coding sensitivity, and permutation inference;
- draft the README, replication notes, validation documentation, and report
  draft.

AI was not treated as an authority for the numerical results. The supplied
data, the original paper, and the course instructions were treated as the
primary sources.

## How AI-generated work was checked

The workflow was checked using several independent consistency checks:

- the input was verified to contain 410 observations and 46 columns;
- New Jersey and Pennsylvania counts were checked against the supplied data;
- the expected 357-observation Table 4 sample was verified;
- headline Table 3 and Table 4 coefficients were compared with the published
  values recorded in the replication comparison table;
- the ownership-extension coefficients and implied marginal effects were
  checked from the regression covariance matrix;
- alternative estimates were rerun from the same raw input with a fixed
  permutation seed;
- the Python script passed compilation checks and the generated outputs passed
  deterministic assertions;
- the generated wage-distribution figure was visually inspected.

## Important corrections and rejected interpretations

Several implementation choices were reviewed and corrected during the
workflow:

1. Binary variables in Table 2 were converted to percentage units so that the
   reported values are comparable to the paper's presentation.
2. Permanent closures were coded as zero post-period employment, while
   temporary, renovation, highway-construction, and mall-fire closures were
   left missing in the main outcome and set to zero only in the explicit
   sensitivity check.
3. The duplicated raw `SHEET` value was preserved, while a separate unique
   local identifier was created for diagnostics rather than silently dropping
   an observation.
4. The ownership interaction was not described as definitive evidence of
   heterogeneous treatment effects because its uncertainty is substantial and
   the design contains only two survey waves.
5. The permutation test was retained as a diagnostic and not presented as a
   replacement for the difference-in-differences identifying assumption.

## Remaining researcher responsibilities

Before submission, the researcher should verify the final interpretation
against the original paper, confirm the definitions of `NORTHJ` and `SHORE`
that are not fully documented in the supplied data dictionary, note that
`PA1` and `PA2` are defined in that dictionary, add the final bibliographic
references, decide whether the course data may be redistributed, and manually
review the final report formatting.
