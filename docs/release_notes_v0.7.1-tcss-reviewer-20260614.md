# Release Notes: v0.7.1-tcss-reviewer-20260614

Date: 2026-06-14

This release updates the sanitized TCSS reviewer-access package after the v0.7 hardening pass.

## Changes Since v0.7

- Added `docs/seirg_transition_specification.md`, a compact SEIRG transition-equation specification aligned with the manuscript's Model Formulation and Theoretical Analysis sections.
- Updated README, data-availability, reproducibility guide, FAIR audit, and citation metadata to reference the transition specification.
- Regenerated `docs/file_manifest_sha256.csv`; the manifest now contains 7,169 file entries.
- Retained the boundary that Morris and Latin-hypercube files are design queues/protocols, not completed global sensitivity results.
- Retained the data-licence boundary: MIT applies only to original scripts and documentation; third-party and platform-derived data remain under source terms.

## Repository Boundary

The package supports review of the reported AnyLogic simulations and model specification. It does not redistribute AnyLogic software and does not provide causal evidence about real-world policy effectiveness.
