# Paired Peak-Difference Supplement

Date: 2026-06-15

This table reports paired total-spreader peak differences for the M0 main scenarios. Each row compares a scenario against the no-intervention M0 baseline using matched seed IDs 1--30. The metric is

```text
Delta Peak_j = Peak_{j, scenario} - Peak_{j, no intervention}.
```

Negative values indicate a lower total-spreader peak than the matched no-intervention baseline. These peak summaries complement the paired cumulative-burden differences reported in the manuscript.

| Scenario | n | Mean Delta Peak | SD | 95% CI low | 95% CI high | Paired t |
|---|---:|---:|---:|---:|---:|---:|
| Dual-track, T=15 | 30 | -134.43 | 26.17 | -144.21 | -124.66 | -28.13 |
| Dual-track, T=30 | 30 | -1.10 | 3.27 | -2.32 | 0.12 | -1.84 |
| Dual-track, T=60 | 30 | 0.00 | 0.00 | 0.00 | 0.00 | Inf |
| Online-only | 30 | -0.63 | 2.01 | -1.38 | 0.12 | -1.73 |
| Offline-only | 30 | -1.07 | 3.20 | -2.26 | 0.13 | -1.82 |
| Weak dual-track | 30 | -0.57 | 1.92 | -1.29 | 0.15 | -1.61 |
| Strong dual-track | 30 | -1.33 | 3.96 | -2.81 | 0.15 | -1.84 |

The exact zero for `Dual-track, T=60` reflects the exported paired peak metric under the common-seed runs at the reported precision: the total-spreader maximum has already formed before the T=60 refutation switch in each matched pair.
