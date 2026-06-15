# Release Notes: v0.7.4-tcss-reviewer-20260615

This maintenance release aligns the equation-level SEIRG reference documentation with the AnyLogic statechart used in the reviewer package.

## Changes

- Clarified that the compact refutation-state exit flow is `G1/G2 -> R`, followed by `R -> S`.
- Documented additional ABM implementation routes in which exposed agents or cross-channel contacts may enter `G1/G2` under online/offline refutation triggers.
- Updated `scripts/analysis/mean_field_reference_seirg.py` and regenerated the corresponding mean-field reference summary and trace.

## Scope

This release does not change the AnyLogic raw simulation exports, processed thirty-seed summaries, paired-seed statistics, structural-baseline results, or manuscript figure/table source data. The change is a documentation and equation-level reference alignment with the existing ABM statechart.
