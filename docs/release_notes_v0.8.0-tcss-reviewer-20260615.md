# Release Notes: v0.8.0-tcss-reviewer-20260615

This release adds the completed budget-matched ABM pathway-fairness check requested for the TCSS submission package.

## Changes

- Added 90 completed AnyLogic M0 runs for the `Tg=30` budget-matched pathway check:
  - online-only `onlineGovEffect/offlineGovEffect = 0.20/0.00`;
  - equal-dual `0.10/0.10`;
  - offline-only `0.00/0.20`.
- Retained the reported dual-track `0.05/0.15` scenario as the main pathway-strength anchor.
- Added `scripts/analysis/build_pathway_fairness_abm_check.py`.
- Added `results/summary/pathway_fairness_abm_check.csv` and `.md`.
- Added `results/designs/pathway_fairness_abm_queue_20260615.csv`.
- Expanded `docs/seirg_transition_specification.md` into an ABM transition table that separates statechart triggers from compact mean-field and threshold-indicator roles.
- Updated README, data-availability notes, and package metadata to v0.8.0.

## Interpretation Boundary

The completed ABM check shows that the budget-matched ordering differs from the unequal-strength pathway table. Under the documented M0 settings, online-only `0.20/0.00` yields a 29.45% cumulative-burden reduction, offline-only `0.00/0.20` yields 27.77%, the reported dual-track `0.05/0.15` anchor yields 24.64%, and equal-dual `0.10/0.10` yields 24.00%. The main pathway table should therefore be read as a pathway-strength scenario comparison, not as an equal-strength pathway ranking.

## Double-Blind Review Note

GitHub URLs expose account-level metadata. For double-blind review, use an anonymized archive uploaded through the journal submission system. The public GitHub release should be disclosed only when the journal review policy permits it.
