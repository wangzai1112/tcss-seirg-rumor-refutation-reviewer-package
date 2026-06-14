# 真实数据处理说明

生成日期：2026-06-12

本目录用于把公开真实数据转换为 SEIRG 谣言传播模型可使用的代理曲线、时间锚点和外部可观测性检查输入。当前 reviewer package 仅保留可公开审稿的聚合/派生文件：CHECKED 日尺度聚合与 `I1(t)` 代理曲线、OxCGRT 中国公共信息时间线和候选锚点、访问日志、登记表与处理说明。为降低第三方数据再分发风险，本包不再分发 CHECKED 原始 JSON/文本、CHECKED 逐微博规范化记录、OxCGRT 完整 compact national 原始 CSV、IFCN/Poynter 原始数据库或页面快照。源数据应按原平台许可从原始提供方获取。

## 0. 当前已生成文件

| 文件 | 状态 | 用途 |
|---|---|---|
| `public_real_data_source_access_log_20260612.csv` | 已生成 | 记录 CHECKED、OxCGRT、CoronaVirusFacts/IFCN 的访问状态、快照哈希和访问时间 |
| `public_real_data_source_access_summary_20260612.json` | 已生成 | 汇总 3 个公开源的核验结果 |
| `OxCGRT_compact_national_v1.csv` | 不随 reviewer package 再分发 | OxCGRT final compact national 数据按源仓库说明为 CC BY 4.0；本包只保留中国派生时间线和锚点 |
| `oxcgrt_chn_public_information_timeline.csv` | 已生成，1096 行 | 中国 `H1_Public information campaigns`、政府响应指数和相关指标日尺度时间线 |
| `oxcgrt_chn_candidate_intervention_anchors.csv` | 已生成，10 行 | 候选干预锚点，包括 `H1` 首次达到阈值和政府响应指数跃升点 |
| `checked_microblog_records_normalized.csv` | 不随 reviewer package 再分发 | CHECKED 逐微博派生记录；本包只保留日尺度聚合和 `I1(t)` 代理曲线 |
| `checked_daily_timeseries_by_label.csv` | 已生成，301 行 | 按日期和标签聚合的互动强度时间序列 |
| `checked_fake_i1_proxy_for_calibration.csv` | 已生成，91 行 | 用于标定 `I1(t)` 的虚假信息线上传播代理曲线 |
| `calibration_curve_fit_summary.csv` | 已生成，14 个场景 | 仿真曲线与 CHECKED 代理曲线的 RMSE、MAE、峰时误差 |
| `calibration_curve_fit_report.md` | 已生成 | 真实数据代理曲线形状比较结果和写作边界 |
| `真实数据登记模板.csv` | 已生成 | 登记数据源、许可、模型映射和能否再分发 |
| `source_snapshot_*.txt` | 不随 reviewer package 再分发 | 页面快照不作为审稿包公开材料；本包保留访问日志和来源登记 |

## 1. 推荐数据组合

| 数据源 | 用途 | 对应模型含义 | 当前处理脚本 |
|---|---|---|---|
| CHECKED Chinese COVID-19 fake news dataset | 构造中文微博谣言传播强度曲线 | `I1(t)` 线上传播者或传播行为强度代理 | `scripts/prepare_checked_timeseries.py` |
| OxCGRT final `covid-policy-dataset` | 构造政府/公共信息干预时间线 | `T` 干预启动时点、外部干预强度代理 | `scripts/prepare_oxcgrt_intervention_timeline.py` |
| CoronaVirusFacts / IFCN / Poynter fact-check 数据 | 构造事实核查/辟谣事件时间线 | `G1(t)` 或 authority/fact-checking intervention 代理 | `scripts/prepare_factcheck_timeline.py` |
| AnyLogic 仿真输出 + 真实传播曲线 | 比较真实曲线与仿真场景的归一化形状误差 | 校准/外部可观测性检查入口 | `scripts/calibrate_simulation_to_real_data.py` |

## 2. CHECKED 处理

本轮已从 CHECKED 公开仓库读取 `dataset/` 并完成处理。为避免将第三方原始文本记录打包再分发，临时克隆目录已删除，仅保留聚合/规范化 CSV 和处理日志。处理时仓库提交记录为 `ff3055c4a3c1ebeac80a1e94050490048dfe583f`。

若后续需要重新复现，可下载 CHECKED 后，假设本地目录为：

```text
/path/to/CHECKED/dataset/
```

执行：

```bash
python3 scripts/prepare_checked_timeseries.py \
  --checked-dataset-dir /path/to/CHECKED/dataset \
  --out-dir 'SCI一区升级规划/真实数据处理'
```

重新处理时会生成：

- `checked_microblog_records_normalized.csv`：逐条微博的日期、标签和互动计数；该文件不随 reviewer package 再分发。
- `checked_daily_timeseries_by_label.csv`：按日期和真假标签聚合的传播强度；该文件随 reviewer package 提供。
- `checked_fake_i1_proxy_for_calibration.csv`：用于校准 `I1(t)` 的 fake 谣言传播代理曲线；该文件随 reviewer package 提供。

本轮处理结果：

- 输入记录：2104 条。
- 按标签日尺度聚合：301 行。
- fake 传播代理曲线：91 行。
- 与 14 个仿真场景进行归一化形状比较后，最佳匹配场景为“短潜伏短遗忘”，RMSE 为 0.3017，MAE 为 0.1420，峰时误差为 -0.3500。

写作边界：

- `normalized_I1_proxy` 是传播强度代理，不等于真实传播者人数。
- CHECKED 是微博数据，主要支撑线上层 `I1(t)` 的代理曲线和可观测性检查，不能直接验证线下层 `I2(t)`。
- CHECKED README 提醒数据仅用于学术研究，正式投稿前需要确认引用和许可证表述。

## 3. OxCGRT 处理

Reviewer package 不包含 `OxCGRT_compact_national_v1.csv` 完整原始文件。若需重新复现 OxCGRT 处理，应先按 OxCGRT 源仓库许可下载该文件，再执行：

```bash
python3 scripts/prepare_oxcgrt_intervention_timeline.py \
  --input-csv 'SCI一区升级规划/真实数据处理/OxCGRT_compact_national_v1.csv' \
  --country-code CHN \
  --out-dir 'SCI一区升级规划/真实数据处理'
```

也可以用脚本直接下载公开 final CSV：

```bash
python3 scripts/prepare_oxcgrt_intervention_timeline.py \
  --download \
  --country-code CHN \
  --out-dir 'SCI一区升级规划/真实数据处理'
```

输出：

- `oxcgrt_chn_public_information_timeline.csv`：中国公共信息干预和政策响应时间线。
- `oxcgrt_chn_candidate_intervention_anchors.csv`：候选干预启动时点，包括首次达到 `H1_Public information campaigns >= 2` 和政府响应指数跃升点。

本轮处理结果：

- 中国时间线：1096 行。
- 候选干预锚点：10 个。
- `H1_Public information campaigns >= 2` 的首次候选锚点为 2020-01-15。

写作边界：

- OxCGRT 是 COVID-19 政策响应数据，不是专门的谣言治理数据。
- 论文中应写作 `public information / policy intervention proxy`，不要写成“真实谣言治理强度”。
- `H1_Public information campaigns` 可作为 `T` 的现实时间锚点，但不能单独证明政策导致谣言传播下降。

## 4. Fact-check 数据处理

将 CoronaVirusFacts、IFCN、Poynter 或同类 fact-check 数据另存为 CSV 后执行：

```bash
python3 scripts/prepare_factcheck_timeline.py \
  --input-csv /path/to/factcheck.csv \
  --date-column published_date \
  --country-contains China \
  --keyword covid \
  --out-dir 'SCI一区升级规划/真实数据处理'
```

如果脚本无法自动识别日期列，需要显式传入 `--date-column`。

输出：

- `factcheck_daily_intervention_timeline.csv`：每日 fact-check/辟谣数量和累计数量。
- `factcheck_timeline_metadata.csv`：输入文件、识别列、过滤条件和保留行数。

写作边界：

- fact-check 数据是事实核查/辟谣代理，不能直接等同政府行为。
- 若事实核查机构不是政府部门，建议写作 `authority/fact-checking intervention`。
- 如果许可不允许再分发原始数据，只能发布处理后聚合时间线和数据来源说明。

## 5. 与 AnyLogic / 论文的连接方式

建议按以下顺序接入：

1. 用 CHECKED 构造 `I1(t)` 代理曲线，先做峰值时间、传播持续时间和归一化曲线形状比较。
2. 用 OxCGRT `H1_Public information campaigns` 或响应指数变化点解释 `T=15/30/60` 的现实含义。
3. 用 fact-check 时间线解释 `G1/G2` 状态的现实代理，不把它写成完整外部验证或政府因果效应。
4. 使用 `RMSE`、`MAE`、峰值误差、达峰时间误差评估模型输出与真实曲线的贴合程度。
5. 若真实数据只支持线上传播，论文必须明确 `I2` 是潜变量或情景层，不能声称已被真实数据直接验证。

## 6. 真实曲线与仿真曲线校准

当前已生成 `checked_fake_i1_proxy_for_calibration.csv` 并完成标定。若需重新计算，执行：

```bash
python3 scripts/calibrate_simulation_to_real_data.py \
  --real-timeseries 'SCI一区升级规划/真实数据处理/checked_fake_i1_proxy_for_calibration.csv' \
  --signal I1 \
  --out-dir 'SCI一区升级规划/真实数据处理'
```

输出：

- `calibration_curve_fit_summary.csv`：每个已完成 AnyLogic 场景与真实曲线的归一化形状误差。
- `calibration_curve_fit_report.md`：最匹配场景、RMSE、MAE、峰时误差和解释边界。

解释边界：

- 当前校准脚本默认比较归一化时间和归一化传播强度，适合做曲线形状比较。
- 它不能证明仿真人数规模与真实传播人数一致。
- 如果真实数据只来自 CHECKED，则主要支持 `I1(t)` 代理曲线的形状比较和可观测性检查，不能直接验证 `I2(t)`。
- 正式论文应同时报告最佳匹配、失败案例和参数解释，不能只展示最好的结果。
