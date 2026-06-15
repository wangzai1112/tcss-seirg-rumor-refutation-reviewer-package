# Compact Mean-Field Equal-Strength and Budget-Matched Pathway Check

This supplement is an equation-level directional check under the compact SEIRG mean-field equations. It is not a 30-seed AnyLogic ABM rerun and should not be used to replace the main pathway-strength scenario comparison in the manuscript.

The check keeps the same timing anchor (`Tg=30 h`) and compares equal-strength dual allocations plus budget-matched allocations with `alpha1 + alpha2 = 0.20`.

| Scenario | alpha1 | alpha2 | Budget | Peak | Peak change (%) | Burden | Burden change (%) | RE(Tg) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_refutation_reference | 0.00 | 0.00 | 0.00 | 0.1901 | 0.00 | 13.4353 | 0.00 | 1.8449 |
| reported_unequal_dual_0p05_0p15 | 0.05 | 0.15 | 0.20 | 0.1091 | 42.58 | 6.2737 | 53.30 | 1.1393 |
| equal_weak_dual_0p05_0p05 | 0.05 | 0.05 | 0.10 | 0.1181 | 37.88 | 7.5365 | 43.91 | 1.2410 |
| equal_strong_dual_0p15_0p15 | 0.15 | 0.15 | 0.30 | 0.1091 | 42.61 | 3.5122 | 73.86 | 0.7519 |
| budget_online_only_0p20_0p00 | 0.20 | 0.00 | 0.20 | 0.1091 | 42.61 | 5.4210 | 59.65 | 0.8997 |
| budget_dual_0p15_0p05 | 0.15 | 0.05 | 0.20 | 0.1091 | 42.60 | 4.4715 | 66.72 | 0.8536 |
| budget_equal_dual_0p10_0p10 | 0.10 | 0.10 | 0.20 | 0.1091 | 42.59 | 4.8225 | 64.11 | 0.9362 |
| budget_dual_0p05_0p15 | 0.05 | 0.15 | 0.20 | 0.1091 | 42.58 | 6.2737 | 53.30 | 1.1393 |
| budget_offline_only_0p00_0p20 | 0.00 | 0.20 | 0.20 | 0.1345 | 29.25 | 9.7723 | 27.26 | 1.5736 |

Interpretation boundary: these deterministic mean-field results only test the direction of allocation effects in the compact equations. A submission-ready pathway ranking should be based on equal-strength or budget-matched ABM reruns under the documented AnyLogic statechart.
