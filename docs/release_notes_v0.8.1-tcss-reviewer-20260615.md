# Release Notes: v0.8.1-tcss-reviewer-20260615

This maintenance release aligns the reviewer package with the final minor-revision manuscript edits after the budget-matched ABM pathway-fairness check.

## Changes

- Renamed the budget-matched pathway-fairness summary as Supplementary Table S1.
- Clarified that Supplementary Table S1 reports burden mean, standard deviation, paired burden difference, and 95% confidence interval for the same-budget pathway check.
- Revised `docs/seirg_transition_specification.md` so the ABM transition table explicitly separates:
  - whether each route is active in reported M0 ABM outputs;
  - whether each route is included in equations (8)--(14);
  - whether each route enters the reproduction indicators.
- Updated package metadata to `v0.8.1-tcss-reviewer-20260615`.
- Regenerated the SHA256 file manifest.

## Interpretation Boundary

The scientific content is unchanged from v0.8.0. The package still supports a model-internal simulation study. The pathway results remain conditional on the documented M0 settings and should not be read as an equal-strength real-world pathway ranking or causal policy-effect estimate.
