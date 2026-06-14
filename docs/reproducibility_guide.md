# Reproducibility Guide

## Required Software

- AnyLogic 8.9.8 or later compatible version.
- Python 3.11 or later.
- Python packages listed in `requirements.txt` for figure generation (`pandas`, `numpy`, `matplotlib`). The raw-output summary and statistical-test scripts use only the Python standard library.

## Recommended Workflow

1. Open the AnyLogic model under `anylogic_model/`.
2. Confirm that the model exposes all queue parameters, especially `modelMode`, `seedId`, and `enableCsvExport`.
3. Run the experiment queue for the target batch.
4. Place raw AnyLogic outputs under `data/raw/anylogic_outputs/`.
5. Run `python3 scripts/analysis/analyze_anylogic_outputs.py` to build `results/summary/summary_from_raw.csv`, `run_quality_audit.csv`, `scenario_group_summary.csv`, and `parameter_runs.csv`.
6. Run `python3 scripts/analysis/build_complete_statistical_tests_v3.py` to generate `results/tables/complete_stat_tests_current.csv` and `.md`.
7. Run `python3 scripts/analysis/build_global_sensitivity_design_v3.py` to regenerate the Morris/LHS design files in `results/designs/` when parameter ranges change.
8. Run `python3 scripts/analysis/mean_field_reference_seirg.py` for a standard-library equation-level SEIRG sanity check. This check is provided for transparency and does not replace the AnyLogic agent-based simulation runs used in the manuscript.
8. Install `requirements.txt`, then run `python3 scripts/analysis/build_chapter5_nine_figures.py` to regenerate the Chapter 5 mean-curve figures in `results/figures/第五章九情景重绘/`.
9. Compare the generated tables and figures with the manuscript.

## Acceptance Checks

- Every scenario used in the main manuscript has at least 30 completed random seeds.
- The main queue has 780/780 matched runs and the Chapter 5 supplemental queue has 120/120 matched runs.
- Queue metadata and raw output filenames can be matched without manual editing.
- Statistical tables include mean, SD, 95% CI, Welch t, p-value, effect size, and correction-adjusted p-values.
- External plausibility checking uses data not used for primary simulation comparison.
- Data and code availability statements match the actual repository content.
