# Release Notes: v0.7.6-tcss-reviewer-20260615

Date: 2026-06-15

This release hardens the TCSS reviewer package after the final pre-submission audit.

## Changes

- Added `results/tables/paired_peak_comparisons_m0.csv` and `.md`, a peak-only extract from the paired common-seed M0 comparisons.
- Updated `scripts/analysis/build_paired_seed_comparisons_m0.py` so it regenerates both the full paired comparison table and the peak-only table.
- Expanded `docs/seirg_transition_specification.md` with AnyLogic contact-layer construction notes, including the offline regular ring-lattice channel, online Watts-Strogatz channel, online rewiring probability, initial seed allocation, and implementation-level transition routes.
- Updated `results/figures/fig5_weibo_g1_plausibility.pdf` and `.png` so peak-day offset and post-`Tg` share are plotted in separate panels with separate units.
- Updated README, data-availability notes, and `CITATION.cff` to reflect the v0.7.6 package state.

## Interpretation Boundaries

- The new paired peak table is computed from existing run-level outputs; no new AnyLogic simulations are claimed.
- The package still treats Morris and Latin-hypercube files as design/execution queues, not completed global-sensitivity results.
- A DOI has not been minted in this environment. Zenodo/OSF/Figshare DOI insertion remains an external submission step.
