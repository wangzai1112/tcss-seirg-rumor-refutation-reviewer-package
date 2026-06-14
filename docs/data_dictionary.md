# Data Dictionary

## Simulation Queue Columns

| Column | Meaning |
|---|---|
| `queueId` | Unique run identifier in the experiment queue. |
| `batchId` | Experiment batch identifier. |
| `scenarioId` | Scenario-level identifier shared by the 30 random seeds. |
| `scenarioName` | Human-readable scenario name. |
| `seedId` | Random seed used by the AnyLogic run. |
| `modelMode` | Model structure switch: 0 full coupled SEIRG, 1 traditional SEIR, 2 single-layer network SEIR, 3 no-G/no-coupling model. |
| `interventionStartTime` | Intervention start time in simulation hours. |
| `enableOnlineIntervention` | Whether online intervention is enabled. |
| `enableOfflineIntervention` | Whether offline intervention is enabled. |
| `kOnline`, `kOffline` | Average contact degree in online/offline spaces. |
| `onlineRate`, `offlineRate` | Online/offline propagation rates used in the simulation model. |
| `onlineGovEffect`, `offlineGovEffect` | Online/offline rumor-refutation intervention transition strengths used in the SEIRG model. |

## Result Columns

| Column | Meaning |
|---|---|
| `I1Peak` | Peak number of online spreaders. |
| `I1PeakTime` | Time at which `I1Peak` occurs. |
| `I2Peak` | Peak number of offline spreaders. |
| `I2PeakTime` | Time at which `I2Peak` occurs. |
| `totalInfectedPeak` | Peak value of `I1 + I2`. |
| `cumulativeInfectedPersonHours_right` | Cumulative spreader person-hours using right-endpoint aggregation. |
| `G1Peak`, `G2Peak` | Peak values of online/offline rumor-refutation intervention states. `G1` and `G2` are model states, not government departments or real counts of governed individuals. |
| `finalS`, `finalE`, `finalI1`, `finalI2`, `finalG1`, `finalG2`, `finalR` | Final state values at the end of the simulation horizon. |

## Model State Terminology

| Symbol | Canonical manuscript term | Meaning |
|---|---|---|
| `S` | 未知者 | Individuals who have not entered the rumor-spreading chain in the model. |
| `E` | 潜伏者 | Individuals exposed to the rumor but not yet active spreaders. |
| `I1` | 线上传播者 | Spreaders mainly active in the online propagation layer. |
| `I2` | 线下传播者 | Spreaders mainly active in the offline/contact propagation layer. |
| `R` | 免疫者/退出者 | Individuals who have stopped spreading or are treated as removed/immune in the model. |
| `G1` | 线上辟谣干预状态 | Model state entered after online rumor-refutation intervention, such as authoritative clarification, platform prompts, or online fact-checking. |
| `G2` | 线下辟谣干预状态 | Model state entered after offline rumor-refutation intervention, such as community explanation or offline clarification. |

Use `rumor-refutation intervention state` for `G1/G2` in English documentation. The full list of canonical and retired wording is maintained in `terminology_ledger_20260614.md`.

## Statistical Columns

| Column | Meaning |
|---|---|
| `mean` | Mean across random seeds. |
| `sd` | Sample standard deviation across random seeds. |
| `ci95Low`, `ci95High` | 95% confidence interval based on normal approximation. |
| `welchT`, `welchDf`, `pValue` | Welch two-sample t-test result against the no-intervention baseline. |
| `cohenD`, `hedgesG` | Standardized effect sizes. |
| `pBHByMetric`, `pHolmByMetric` | Multiple-comparison adjusted p-values within the same metric family. |
