# Release Notes: v0.7.7-tcss-reviewer-20260615

Date: 2026-06-15

This release adds final reviewer-facing documentation after the pathway-strength, ABM-boundary, sensitivity-table, and reference-metadata audit.

## Added

- `docs/pathway_strength_supplement_queue.md` and `results/designs/pathway_strength_supplement_queue.csv`, documenting equal-strength and budget-matched pathway checks as a design queue only.
- `docs/reference_verification_20260615_final.md` and `.csv`, documenting the final 2025/2026 reference metadata check.

## Updated

- `docs/seirg_transition_specification.md` now separates ABM implementation routes, compact mean-field equation roles, and whether each route is used in deriving reproduction indicators.
- `docs/file_manifest_sha256.csv` was regenerated after the documentation update.
- `README.md`, `CITATION.cff`, and the Zenodo DOI plan now point to this release tag.

## Unchanged

- No new AnyLogic simulation outputs are introduced in this release.
- The reported main results, paired seed comparisons, paired peak comparisons, statistical-test tables, figures, and processed simulation summaries are unchanged.
- The global sensitivity files remain design/protocol files, not completed global-sensitivity results.
