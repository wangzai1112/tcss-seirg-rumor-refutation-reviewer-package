# Reviewer Package Audit

Date: 2026-06-14

Repository URL: `https://github.com/wangzai1112/tcss-seirg-rumor-refutation-reviewer-package`

## Scope

This package is a sanitized reviewer-access reproducibility package for the TCSS-oriented manuscript draft. It includes model files, simulation exports, processed simulation summaries, statistical tests, figure source data, manuscript-supporting figures and tables, experiment queues, analysis scripts, documentation, and a SHA256 file manifest.

The package also includes a compact transition specification at `docs/seirg_transition_specification.md` and a lightweight standard-library Python mean-field reference implementation at `scripts/analysis/mean_field_reference_seirg.py`. These files support equation-level inspection of state flows and indicators but are not used to generate the manuscript's agent-based simulation results.

## Third-Party Data Boundary

The package does not redistribute CHECKED raw JSON/text records, CHECKED microblog-level normalized records, full OxCGRT compact national CSV files, IFCN/Poynter raw database exports, or page snapshots.

Included external-data derivatives are limited to aggregate or processed proxy files:

- `checked_daily_timeseries_by_label.csv`
- `checked_fake_i1_proxy_for_calibration.csv`
- `oxcgrt_chn_public_information_timeline.csv`
- `oxcgrt_chn_candidate_intervention_anchors.csv`
- source access logs and source registration metadata

The MIT License applies to original scripts and documentation only. Third-party source datasets remain governed by their original source terms.

## Sensitivity-Analysis Boundary

Local sensitivity and ablation runs are complete. Morris and Latin-hypercube files are design queues and protocols only; they are not reported as completed global sensitivity results.

## Claim Boundary

The package supports model-internal comparison of rumor-refutation intervention in a coupled online-offline SEIRG simulation. It does not provide causal evidence that real-world policy action reduced rumor propagation.
