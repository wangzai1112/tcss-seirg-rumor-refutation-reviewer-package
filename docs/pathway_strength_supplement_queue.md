# Pathway-Strength Supplementary Check Status

Date: 2026-06-15

Status: the core budget-matched ABM subset has been executed as a supplementary check; remaining allocation variants are retained as future design options.

The current manuscript reports online-only, offline-only, and dual-track pathway scenarios under unequal refutation-strength fields (`onlineGovEffect=0.05`, `offlineGovEffect=0.15`). Those results are therefore interpreted as pathway-strength scenario comparisons rather than equal-strength pathway rankings.

To separate pathway allocation from refutation-strength allocation, a supplementary 30-seed AnyLogic ABM check was executed for the fixed-budget rows listed below. All completed rows use the same model mode, population, network settings, timing anchor (`Tg=30`), horizon, seed IDs 1--30, and output metrics as the reported M0 pathway scenarios. The generated table is `pathway_fairness_abm_check.csv/.md`.

| Queue ID | Online enabled | Offline enabled | onlineGovEffect | offlineGovEffect | Budget sum | Intended contrast |
|---|---:|---:|---:|---:|---:|---|
| budget_online_020_000 | true | false | 0.20 | 0.00 | 0.20 | Completed 30-seed online-only fixed-budget check |
| budget_dual_010_010 | true | true | 0.10 | 0.10 | 0.20 | Completed 30-seed equal-allocation fixed-budget check |
| budget_dual_005_015 | true | true | 0.05 | 0.15 | 0.20 | Existing reported allocation anchor |
| budget_offline_000_020 | false | true | 0.00 | 0.20 | 0.20 | Completed 30-seed offline-only fixed-budget check |
| budget_dual_015_005 | true | true | 0.15 | 0.05 | 0.20 | Future optional online-skewed allocation |
| equal_weak_dual_005_005 | true | true | 0.05 | 0.05 | 0.10 | Future optional weak equal-strength check |
| equal_strong_dual_015_015 | true | true | 0.15 | 0.15 | 0.30 | Future optional strong equal-strength check |

The completed fixed-budget check shows that the pathway ordering changes when the same total refutation-strength budget is imposed. Under the documented M0 settings, online-only `0.20/0.00` has the largest cumulative-burden reduction among the completed budget-matched rows. The manuscript should therefore retain the bounded wording that the reported pathway table is a pathway-strength scenario comparison, not a universal or equal-strength pathway ranking.
