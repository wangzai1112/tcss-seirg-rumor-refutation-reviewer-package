# Release Notes: v0.7.3-tcss-reviewer-20260615

This release aligns the reviewer-access package with the TCSS manuscript version that reports paired common-seed comparisons as the primary M0 scenario comparison.

## Changes

- Added `scripts/analysis/build_paired_seed_comparisons_m0.py`, a standard-library Python script that rebuilds paired common-seed differences from `data/processed/simulation/summary_from_raw.csv`.
- Added `results/tables/paired_seed_comparisons_m0.csv` and `results/tables/paired_seed_comparisons_m0.md`.
- Updated `README.md`, `CITATION.cff`, and `docs/data_availability_statement.md` to document the paired-seed output.
- Retained Welch tests, BH-FDR, Holm correction, and Hedges g as robustness summaries in `results/tables/complete_stat_tests_current.*`.
- Retained the data-licence boundary: MIT applies only to original scripts and documentation; third-party and platform-derived data remain under source terms.

## Remaining External Actions

- A Zenodo, OSF, Figshare, or institutional DOI has not yet been minted.
- If a DOI is required for journal submission, archive this sanitized release and update `CITATION.cff`, `README.md`, and the manuscript data-availability statement with the DOI.
- Morris and Latin-hypercube files remain design queues, not completed global sensitivity results.
