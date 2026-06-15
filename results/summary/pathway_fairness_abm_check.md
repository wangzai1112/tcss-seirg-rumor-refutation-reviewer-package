# Supplementary Table S1. Budget-Matched ABM Pathway Fairness Check

This supplementary table reports completed 30-seed AnyLogic M0 runs at `Tg=30` under the same population, network, propagation, state-duration, and common-seed settings as the main pathway scenarios. The check separates the reported pathway-strength comparison from a same-budget allocation check. It is a model-internal sensitivity check, not a real-world pathway ranking.

| Scenario | alpha1/alpha2 | n | Peak mean (SD) | Peak change | Burden mean (SD) | Burden change | Burden reduction | Paired burden diff. 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| No intervention baseline | reference | 30 | 863.97 (18.79) | 0.00 | 41216.73 (867.24) | 0.00 | 0.00% | [0.00, 0.00] |
| Budget-matched online-only | 0.20 / 0.00 | 30 | 862.83 (20.30) | -1.13 | 29077.67 (843.07) | -12139.07 | 29.45% | [-12620.16, -11657.97] |
| Budget-matched equal dual | 0.10 / 0.10 | 30 | 862.77 (20.45) | -1.20 | 31326.43 (880.68) | -9890.30 | 24.00% | [-10306.63, -9473.97] |
| Reported dual-track anchor | 0.05 / 0.15 | 30 | 862.87 (20.34) | -1.10 | 31061.70 (908.54) | -10155.03 | 24.64% | [-10646.94, -9663.13] |
| Budget-matched offline-only | 0.00 / 0.20 | 30 | 862.90 (20.26) | -1.07 | 29771.00 (834.37) | -11445.73 | 27.77% | [-11894.65, -10996.82] |

Interpretation boundary: under this parameterization, the budget-matched ordering differs from the unequal-strength pathway table. The online-only `0.20/0.00` allocation yields the largest cumulative-burden reduction in this check, followed by offline-only `0.00/0.20`, the reported `0.05/0.15` dual-track anchor, and equal-dual `0.10/0.10`. Therefore, the main pathway table should be read as a pathway-strength scenario comparison. This finding remains conditional on the implemented contact structure, propagation rates, statechart triggers, and `Tg=30`; it does not provide a pathway ranking outside this model setting.
