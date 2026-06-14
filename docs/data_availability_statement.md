# Data and Code Availability

The AnyLogic simulation exports, experiment queues, processed run-level summaries, statistical-test tables, figure source data, and analysis scripts supporting the manuscript are included in this reproducibility package. The raw AnyLogic CSV exports are provided in `data/raw/anylogic_outputs/`. Processed simulation tables are provided in `data/processed/simulation/`, including `summary_from_raw.csv`, `paper_table_priority1_30seed.csv`, `run_quality_audit.csv`, and related manuscript table drafts. Statistical-test outputs are provided in `results/tables/complete_stat_tests_current.csv` and `results/tables/complete_stat_tests_current.md`. Experiment designs, including the SCI v3 full rerun queue, the Chapter 5 supplemental nine-scenario queue, LHS design, Morris design, and global-sensitivity parameter space, are provided in `results/designs/`.

The AnyLogic model file and model-mode patch notes are provided in `anylogic_model/`. Analysis scripts for queue construction, AnyLogic batch execution, run summarisation, statistical testing, sensitivity-design generation, and document integration are provided in `scripts/analysis/`. Manuscript-ready figures and their source tables are provided in `results/figures/`, including the redrawn 30-seed mean curves and the CHECKED external plausibility-check source data.

External plausibility checking uses the CHECKED Chinese COVID-19 fake-news dataset and Oxford COVID-19 Government Response Tracker (OxCGRT) public-information indicators. The reviewer package provides aggregate CHECKED proxy series, OxCGRT China public-information anchors, access logs, and processing documentation in `data/processed/external_validation/`; the directory name is retained for traceability with earlier drafts. These external data are used for trend anchoring, timing proxies, calibration aids, and plausibility checking. They are not used to claim a causal effect of real government policy. CHECKED raw JSON/text records, CHECKED microblog-level normalized records, full OxCGRT compact national CSV files, IFCN/Poynter raw database exports, and page snapshots are not redistributed in the reviewer package.

The current package includes a SHA256 file manifest at `docs/file_manifest_sha256.csv`. Original analysis scripts and documentation are released under the MIT License unless a file states otherwise. Data redistribution boundaries are described in `DATA_LICENSE_NOTICE.md`. The reviewer-access repository URL is `https://github.com/wangzai1112/tcss-seirg-rumor-refutation-reviewer-package`. A DOI can be minted later from the same release if required by the journal.

## Dataset-to-location mapping

| Evidence item | Repository location | Access route | Notes |
|---|---|---|---|
| Raw AnyLogic simulation exports | `data/raw/anylogic_outputs/` | public repository | 7,047 CSV files at the current package snapshot. |
| Processed simulation run summary | `data/processed/simulation/summary_from_raw.csv` | public repository | 2,349 run-level records; 900 records marked `usedForScenarioStats=true`. |
| Main experiment statistical tests | `results/tables/complete_stat_tests_current.csv` | public repository | 180 rows with mean, SD, 95% CI, Welch t, p values, effect sizes, and adjusted p values. |
| Manuscript tables and figure source data | `results/figures/`, `results/tables/`, `data/processed/simulation/` | public repository | Includes Chapter 5 redrawn curves and source-data tables. |
| Global sensitivity and Morris/LHS designs | `results/designs/` and `docs/global_sensitivity_protocol_v3.md` | public repository | Design files are provided; they are not completed global-sensitivity results until runs and post-processing are executed. |
| CHECKED external plausibility-check proxy | `data/processed/external_validation/checked_fake_i1_proxy_for_calibration.csv` and aggregate daily files | reused public source / aggregate derivative | Cite the original CHECKED dataset; raw JSON/text and microblog-level normalized records are not redistributed in the reviewer package. |
| OxCGRT public-information anchors | `data/processed/external_validation/oxcgrt_chn_public_information_timeline.csv` and `oxcgrt_chn_candidate_intervention_anchors.csv` | reused public source / processed derivative | Cite OxCGRT; the full compact national CSV is obtained from the OxCGRT source repository under CC BY 4.0 rather than redistributed here. |
| AnyLogic model and model patch notes | `anylogic_model/` | public repository, subject to software/tool restrictions | AnyLogic itself is proprietary software and is not redistributed. |
| Code scripts | `scripts/analysis/` | public repository | Final software licence must be confirmed before archival. |

## Repository and citation actions

- Use `https://github.com/wangzai1112/tcss-seirg-rumor-refutation-reviewer-package` as the reviewer-access repository URL.
- If a DOI-backed archive is required later, create a Zenodo, OSF, Figshare, institutional repository, or equivalent archive from the same sanitized release.
- Keep the MIT License for original scripts and documentation unless the institution requires another licence.
- Cite CHECKED and OxCGRT as reused public data sources in the manuscript reference list or data-availability section.
- Verify that third-party data files included in `data/processed/external_validation/` are permitted for redistribution; otherwise replace restricted files with download instructions, checksums where allowed, and processing scripts.

## Missing information / risk flags

- A DOI is not assigned in this reviewer package; the GitHub reviewer-access URL is active.
- AnyLogic model execution depends on a licensed AnyLogic installation.
- External data are used as proxies and external anchors, not as direct causal validation of public-information or policy effects.
- Before journal submission, rerun the scripts after any AnyLogic model edit and regenerate `docs/file_manifest_sha256.csv`.

## 中文核对

- 本版本使用 GitHub reviewer-access URL；如期刊后续要求 DOI，可用同一去敏 release 生成 Zenodo/OSF/Figshare DOI。
- 原创脚本和文档已按 MIT 许可准备；第三方数据不能随意套用自己的开源许可证。
- CHECKED 和 OxCGRT 只能作为外部趋势参照、时间锚点和可观测性检查，不能写成现实政策因果验证。
- AnyLogic 软件本身不能随仓库分发，只能分发模型文件、运行说明和导出数据。
