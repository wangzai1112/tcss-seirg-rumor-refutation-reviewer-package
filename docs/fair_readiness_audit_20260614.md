# FAIR and Repository Readiness Audit

Audit date: 2026-06-14  
Package root: `SCI一区升级规划/public_release_template`

## Current Evidence Inventory

| Item | Current evidence | Status |
|---|---:|---|
| Raw AnyLogic CSV exports | 7,047 files in `data/raw/anylogic_outputs/` | Present |
| Processed simulation files | 20 files in `data/processed/simulation/` | Present |
| External plausibility-check processing files | 16 files in `data/processed/external_validation/` | Present |
| Manuscript figure/source files | 39 files in `results/figures/` | Present |
| Statistical-test tables | `complete_stat_tests_current.csv/md` in `results/tables/` | Present |
| Experiment design files | main queue, Chapter 5 supplemental queue, LHS, Morris, parameter space | Present |
| Scripts | 11 core analysis scripts in `scripts/analysis/` | Present |
| AnyLogic model | `anylogic_model/rumor_model_sci_v3_current.alp` | Present |
| File manifest | `docs/file_manifest_sha256.csv`, 7,169 files | Present |

## FAIR Check

| Principle | Check result | Remaining action |
|---|---|---|
| Findable | Package has structured folders, README, data dictionary, citation metadata, SHA256 file manifest, and reviewer-access repository metadata. | Mint a DOI from the same release later if required by the journal. |
| Accessible | Files are prepared for the public reviewer-access repository at `https://github.com/wangzai1112/tcss-seirg-rumor-refutation-reviewer-package`. Raw AnyLogic exports and processed outputs are included. | Test the repository URL after push. |
| Interoperable | Core data are CSV, Markdown, PNG, SVG, and AnyLogic `.alp`. Variable definitions are documented in `docs/data_dictionary.md`. | AnyLogic model requires proprietary AnyLogic software; note this dependency in final archive. |
| Reusable | Raw/processed separation, scripts, model notes, source-data files, external-data logs, and checksums are provided. | Original scripts and documentation use MIT; replace any third-party restricted file with download instructions if required. |

## Submission Blocking Items

- No DOI is assigned in this package; the reviewer-access GitHub URL is used for submission review.
- Third-party data redistribution rights must be confirmed before public release.
- AnyLogic execution requires a licensed local AnyLogic installation.
- External data support proxy construction, trend anchoring, timing checks, and plausibility analysis only; they should not be described as causal validation.

## Non-Blocking Notes

- The current statistical subset contains 900 runs marked `usedForScenarioStats=true`.
- Model-mode baselines are present in the run summary with 120 statistics-used rows each for `modelMode=1`, `modelMode=2`, and `modelMode=3`.
- The package includes both PNG and SVG figures. SVG should be preferred for editable vector submission where allowed.
- After any future AnyLogic rerun, regenerate `summary_from_raw.csv`, `complete_stat_tests_current.csv`, figures, and `docs/file_manifest_sha256.csv`.

## Recommended Archive Metadata

| Field | Suggested value |
|---|---|
| Title | Coupled online-offline rumor propagation and rumor-refutation intervention simulation package |
| Creators | Sun Guohao; add adviser/co-author names if required |
| Resource type | Dataset and software |
| Keywords | rumor propagation; coupled online-offline network; SEIRG; rumor-refutation intervention; public-information intervention; AnyLogic; misinformation |
| Version | v0.6-thesis-sci-upgrade-20260614 |
| Licence | MIT for original scripts/documentation; third-party data remain under source terms |
| Related identifier | Link to thesis/manuscript when available |

## 中文核对

- 当前 reviewer package 已具备可复现包的基本结构，原创脚本/文档已按 MIT 准备，并使用 GitHub reviewer-access URL；如期刊要求 DOI，可从同一去敏 release 生成。
- 第三方数据不能默认开放再分发；若源许可不清楚，应只保留处理脚本、下载说明和校验信息。
- AnyLogic 模型文件可以归档，但运行环境依赖 AnyLogic 软件本身，这一点需要在方法和仓库说明里保留。
