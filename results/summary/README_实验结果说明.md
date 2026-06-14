# AnyLogic 实验结果汇总说明

生成时间：2026-06-14T02:46:27

## 文件说明

- `summary_from_raw.csv`：从 `raw_timeseries_*.csv` 重新计算的单次运行指标，是后续论文表格优先采用的数据源。
- `scenario_group_summary.csv`：按干预时点、干预开关、网络参数和传播参数分组后的均值/标准差表；同一场景同一 seed 重复运行时，只采用最新完整运行。
- `run_quality_audit.csv`：每个 raw 文件的完整性检查，重点看是否跑满 180h、时间步是否正常、总人数是否守恒。
- `parameter_runs.csv`：AnyLogic 导出的参数主表，保留每次运行的参数记录。
- `fig_timeseries_completed_runs.svg`：已跑满 180h 的 I1/I2 时间序列预览图，由 `scripts/plot_anylogic_results.py` 生成。
- `fig_scenario_peak_comparison.svg`：场景峰值对比预览图，由 `scripts/plot_anylogic_results.py` 生成。
- `paper_table_priority1_current.csv/.md`：论文可用的当前有效 seed 均值、标准差和 95%CI 表，由 `scripts/build_paper_stat_tables.py` 生成；跑满 30 seed 后会同步生成 `paper_table_priority1_30seed.csv/.md`。
- `intervention_effects_vs_baseline.csv/.md`：相对无干预基准情景的降幅、Cohen's d 和 Welch t 统计量表，由 `scripts/build_paper_stat_tables.py` 生成。
- `paper_result_sentences_current.md`：可回填论文实验结果部分的文字草稿，由 `scripts/build_paper_stat_tables.py` 生成；跑满 30 seed 后会同步生成 `paper_result_sentences_30seed.md`。

## 指标口径

- `I1Peak` / `I2Peak`：线上/线下传播者数量的首次最大值。
- `I1PeakTime` / `I2PeakTime`：对应首次达峰时间，单位为 hour。
- `totalInfectedPeak`：`I1 + I2` 的首次最大值。
- `cumulativeInfectedPersonHours_right`：与 AnyLogic 当前 summary 写法一致，使用右端矩形法累加 `(I1 + I2) * dt`。
- `cumulativeInfectedPersonHours_trapezoid`：使用梯形法计算的稳健性口径，可作为补充分析。
- `runCompleted=false`：该运行未达到 180h，只能作为调试结果，不能直接进入论文主表。
- `usedForScenarioStats=true`：该运行进入场景均值/标准差统计；同一参数组合下同一 seed 的旧重复运行会被排除。

## 当前数据状态

- 已识别 raw 运行数：2349
- 跑满 180h 的运行数：1679
- 未跑满 180h 的调试运行数：670

## 后续要求

- 论文主表只使用 `runCompleted=true` 且 `usedForScenarioStats=true` 的运行。
- priority=1 主实验要求每个核心场景至少 30 个 seed；若只完成部分 seed，应在论文中明确写成阶段性预实验。
- 每次补跑后重新执行 `python3 scripts/analyze_anylogic_outputs.py`，不要手工复制表格数值。
- 需要更新图时，再执行 `python3 scripts/plot_anylogic_results.py`。
- 需要更新论文表格和结果段落时，再执行 `python3 scripts/build_paper_stat_tables.py`。

## 质量提醒

当前存在未跑满或需复查的运行，请先查看 `run_quality_audit.csv`。
