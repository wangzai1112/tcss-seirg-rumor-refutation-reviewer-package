# Release Notes: v0.7.9-tcss-reviewer-20260615

This release tightens reviewer-facing materials for the TCSS submission package.

## Changes

- Added `scripts/analysis/mean_field_pathway_budget_check.py`.
- Added `results/summary/mean_field_pathway_budget_check.csv` and `.md`.
- Clarified that auxiliary `E -> G_l` and cross-channel `G_l` triggers are part of the reported ABM statechart when triggered, but are excluded from the compact mean-field equations and from the derivation of `R0`, `R0^G`, and `RE(t;Tg)`.
- Updated package metadata and Data Availability notes for the equation-level equal-strength / budget-matched pathway check.

## Interpretation Boundary

The new pathway-allocation check is deterministic and equation-level. It is not a 30-seed AnyLogic ABM rerun and should not be used to replace the main pathway-strength scenario comparison. Its role is to make the equal-strength and budget-matched caveat inspectable without overstating pathway ranking.

## Double-Blind Review Note

GitHub URLs expose account-level metadata. For double-blind review, use an anonymized archive uploaded through the journal submission system. The public GitHub release should be disclosed only when the journal review policy permits it.
