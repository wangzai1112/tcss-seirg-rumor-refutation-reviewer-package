# Global Sensitivity Execution Status

Date: 2026-06-14

The package contains completed local sensitivity/ablation evidence and prepared global-sensitivity designs. These should be kept distinct in the manuscript and repository metadata.

## Completed Local Sensitivity

`data/processed/simulation/priority2_sensitivity_progress.csv` reports 7 scenarios and 180/180 completed seeds. These results support local sensitivity and ablation claims around the `T=30` dual-track reference scenario.

## Prepared Global-Sensitivity Designs

The following files are provided for reproducibility and future execution:

- `results/designs/global_sensitivity_parameter_space_v3.csv`: 11-parameter range definition.
- `results/designs/morris_design_v3.csv`: 1200-row Morris design queue.
- `results/designs/lhs_design_v3.csv`: 800-row Latin-hypercube design queue.
- `docs/global_sensitivity_protocol_v3.md`: execution and reporting protocol.

These are design/protocol files, not completed global-sensitivity results. A formal Morris or LHS result requires AnyLogic execution, run-quality audit, post-processing, and parameter-effect summary tables.

## Manuscript Boundary

The manuscript may report local sensitivity and ablation results. It should not claim completed global sensitivity analysis until executed outputs and post-processed effect statistics are added.
