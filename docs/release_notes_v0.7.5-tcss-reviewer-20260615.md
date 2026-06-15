# Release Notes: v0.7.5-tcss-reviewer-20260615

This release aligns the reviewer package with the current 10-page TCSS manuscript draft.

## Changes

- Added the compact timing-trajectory figure used as manuscript Fig. 3.
- Added `results/figures/source_data_fig3_timing_trajectories.csv`.
- Added `scripts/figures/build_fig3_timing_trajectories.py` for package-relative regeneration of Fig. 3.
- Clarified that additional exposed-agent and cross-channel refutation triggers are AnyLogic implementation-level extensions, not explicit mean-field terms.
- Updated package version metadata and regenerated the SHA256 file manifest.

## Boundary

No new AnyLogic simulations are introduced in this release. The new trajectory figure is regenerated from the existing 30 common-seed M0 timing-scenario exports already marked as `usedForScenarioStats=true`.
