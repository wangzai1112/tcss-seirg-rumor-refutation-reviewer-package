# Pathway-Strength Supplementary Check Queue

Date: 2026-06-15

Status: design queue only; not used in the submitted main results.

The current manuscript reports online-only, offline-only, and dual-track pathway scenarios under unequal refutation-strength fields (`onlineGovEffect=0.05`, `offlineGovEffect=0.15`). Those results are therefore interpreted as pathway-strength scenario comparisons rather than equal-strength pathway rankings.

To separate pathway allocation from refutation-strength allocation, the following supplementary runs are recommended if additional AnyLogic batch execution is available. All rows should use the same model mode, population, network settings, timing anchor (`Tg=30`), horizon, seed IDs 1--30, and output metrics as the reported M0 pathway scenarios.

| Queue ID | Online enabled | Offline enabled | onlineGovEffect | offlineGovEffect | Budget sum | Intended contrast |
|---|---:|---:|---:|---:|---:|---|
| budget_online_020_000 | true | false | 0.20 | 0.00 | 0.20 | Online-only under full fixed budget |
| budget_dual_015_005 | true | true | 0.15 | 0.05 | 0.20 | Dual-track, online-skewed allocation |
| budget_dual_010_010 | true | true | 0.10 | 0.10 | 0.20 | Dual-track, equal allocation |
| budget_dual_005_015 | true | true | 0.05 | 0.15 | 0.20 | Dual-track, reported allocation anchor |
| budget_offline_000_020 | false | true | 0.00 | 0.20 | 0.20 | Offline-only under full fixed budget |
| equal_weak_dual_005_005 | true | true | 0.05 | 0.05 | 0.10 | Equal-strength weak dual-track check |
| equal_strong_dual_015_015 | true | true | 0.15 | 0.15 | 0.30 | Equal-strength strong dual-track check |

If these runs are executed, the supplementary table should report the same paired cumulative-burden and paired peak-difference summaries used in the main manuscript. Until then, the manuscript should retain the bounded wording that the reported pathway results are conditional on unequal refutation-strength fields.
