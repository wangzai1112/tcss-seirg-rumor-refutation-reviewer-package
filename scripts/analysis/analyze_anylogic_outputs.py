from __future__ import annotations

import argparse
import csv
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any


def find_package_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "results").exists() and (parent / "docs").exists():
            return parent
    return Path(__file__).resolve().parents[2]


ROOT = find_package_root()
DEFAULT_DATA_DIR = ROOT / "data" / "raw" / "anylogic_outputs"
DEFAULT_OUT_DIR = ROOT / "results" / "summary"
EXPECTED_FINAL_TIME = 180.0

STATE_COLUMNS = ["S", "E", "I1", "I2", "G1", "G2", "R"]
SCENARIO_COLUMNS = [
    "modelMode",
    "interventionStartTime",
    "enableOnlineIntervention",
    "enableOfflineIntervention",
    "kOffline",
    "kOnline",
    "pRewire",
    "initialOnlineSeeds",
    "initialOfflineSeeds",
    "onlineRate",
    "offlineRate",
    "onlineGovEffect",
    "offlineGovEffect",
    "latentTime",
    "forgetTime",
    "govForgetTime",
]

SUMMARY_FIELDS = [
    "runId",
    "rawFile",
    "seedId",
    *SCENARIO_COLUMNS,
    "rowCount",
    "durationHours",
    "runCompleted",
    "usedForScenarioStats",
    "duplicateSeedPolicy",
    "metricScope",
    "populationInitial",
    "populationFinal",
    "populationMin",
    "populationMax",
    "populationConstant",
    "I1Peak",
    "I1PeakTime",
    "I2Peak",
    "I2PeakTime",
    "totalInfectedPeak",
    "totalInfectedPeakTime",
    "EPeak",
    "EPeakTime",
    "G1Peak",
    "G1PeakTime",
    "G2Peak",
    "G2PeakTime",
    "cumulativeInfectedPersonHours_right",
    "cumulativeInfectedPersonHours_trapezoid",
    "finalS",
    "finalE",
    "finalI1",
    "finalI2",
    "finalG1",
    "finalG2",
    "finalR",
    "anylogicSummaryAvailable",
]

QUALITY_FIELDS = [
    "runId",
    "rawFile",
    "rowCount",
    "maxTime",
    "runCompleted",
    "expectedFinalTime",
    "medianDt",
    "minDt",
    "maxDt",
    "hasDuplicateTimes",
    "hasNegativeTimeStep",
    "populationConstant",
    "populationInitial",
    "populationMin",
    "populationMax",
    "qualityNote",
]

GROUP_FIELDS = [
    *SCENARIO_COLUMNS,
    "nRuns",
    "nCompleted",
    "nUniqueSeedsCompleted",
    "nUsedForStats",
    "duplicateCompletedRunsIgnored",
    "usedCompletedOnly",
    "meanI1Peak",
    "sdI1Peak",
    "meanI1PeakTime",
    "meanI2Peak",
    "sdI2Peak",
    "meanI2PeakTime",
    "meanTotalInfectedPeak",
    "sdTotalInfectedPeak",
    "meanCumulativeRight",
    "sdCumulativeRight",
    "meanCumulativeTrapezoid",
    "sdCumulativeTrapezoid",
    "meanFinalR",
    "sdFinalR",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_intish(value: Any, default: int = 0) -> int:
    return int(round(as_float(value, float(default))))


def fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    if value is None:
        return ""
    return str(value)


def run_id_from_raw_path(path: Path) -> str:
    name = path.name
    prefix = "raw_timeseries_"
    suffix = ".csv"
    if name.startswith(prefix) and name.endswith(suffix):
        return name[len(prefix) : -len(suffix)]
    return path.stem


def run_order_value(row: dict[str, Any]) -> int:
    run_id = str(row.get("runId", ""))
    try:
        return int(run_id.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0


def first_peak(rows: list[dict[str, Any]], series_name: str) -> tuple[float, float]:
    best_value = -1.0
    best_time = 0.0
    for row in rows:
        value = as_float(row.get(series_name))
        if value > best_value:
            best_value = value
            best_time = as_float(row.get("time"))
    return max(best_value, 0.0), best_time


def first_total_peak(rows: list[dict[str, Any]]) -> tuple[float, float]:
    best_value = -1.0
    best_time = 0.0
    for row in rows:
        value = as_float(row.get("I1")) + as_float(row.get("I2"))
        if value > best_value:
            best_value = value
            best_time = as_float(row.get("time"))
    return max(best_value, 0.0), best_time


def area_under_infected_curve(rows: list[dict[str, Any]]) -> tuple[float, float]:
    right_sum = 0.0
    trapezoid_sum = 0.0
    for previous, current in zip(rows, rows[1:]):
        previous_time = as_float(previous.get("time"))
        current_time = as_float(current.get("time"))
        dt = current_time - previous_time
        if dt <= 0:
            continue
        previous_infected = as_float(previous.get("I1")) + as_float(previous.get("I2"))
        current_infected = as_float(current.get("I1")) + as_float(current.get("I2"))
        right_sum += current_infected * dt
        trapezoid_sum += (previous_infected + current_infected) * dt / 2.0
    return right_sum, trapezoid_sum


def merge_parameters(raw_row: dict[str, str], param_row: dict[str, str] | None) -> dict[str, str]:
    merged = dict(raw_row)
    if param_row:
        for key, value in param_row.items():
            if value != "":
                merged[key] = value
    return merged


def analyze_raw_file(
    path: Path,
    parameter_by_run: dict[str, dict[str, str]],
    anylogic_summary_runs: set[str],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    raw_rows = read_csv(path)
    run_id = raw_rows[0].get("runId", "") if raw_rows else run_id_from_raw_path(path)
    if not raw_rows:
        quality = {
            "runId": run_id,
            "rawFile": path.name,
            "rowCount": 0,
            "maxTime": "",
            "runCompleted": "false",
            "expectedFinalTime": EXPECTED_FINAL_TIME,
            "qualityNote": "empty raw_timeseries file",
        }
        return None, quality

    rows = sorted(raw_rows, key=lambda item: as_float(item.get("time")))
    first = rows[0]
    last = rows[-1]
    params = merge_parameters(last, parameter_by_run.get(run_id))

    times = [as_float(row.get("time")) for row in rows]
    dts = [b - a for a, b in zip(times, times[1:])]
    positive_dts = [dt for dt in dts if dt > 0]
    max_time = max(times)
    run_completed = max_time >= EXPECTED_FINAL_TIME - 1.0e-9

    populations = [
        sum(as_float(row.get(column)) for column in STATE_COLUMNS)
        for row in rows
    ]
    population_constant = (
        max(populations) - min(populations) <= 1.0e-9 if populations else False
    )

    i1_peak, i1_peak_time = first_peak(rows, "I1")
    i2_peak, i2_peak_time = first_peak(rows, "I2")
    e_peak, e_peak_time = first_peak(rows, "E")
    g1_peak, g1_peak_time = first_peak(rows, "G1")
    g2_peak, g2_peak_time = first_peak(rows, "G2")
    total_peak, total_peak_time = first_total_peak(rows)
    cumulative_right, cumulative_trapezoid = area_under_infected_curve(rows)

    summary = {
        "runId": run_id,
        "rawFile": path.name,
        "seedId": params.get("seedId", ""),
        "rowCount": len(rows),
        "durationHours": max_time,
        "runCompleted": run_completed,
        "metricScope": "full_0_180h" if run_completed else "partial_debug_run",
        "populationInitial": populations[0],
        "populationFinal": populations[-1],
        "populationMin": min(populations),
        "populationMax": max(populations),
        "populationConstant": population_constant,
        "I1Peak": i1_peak,
        "I1PeakTime": i1_peak_time,
        "I2Peak": i2_peak,
        "I2PeakTime": i2_peak_time,
        "totalInfectedPeak": total_peak,
        "totalInfectedPeakTime": total_peak_time,
        "EPeak": e_peak,
        "EPeakTime": e_peak_time,
        "G1Peak": g1_peak,
        "G1PeakTime": g1_peak_time,
        "G2Peak": g2_peak,
        "G2PeakTime": g2_peak_time,
        "cumulativeInfectedPersonHours_right": cumulative_right,
        "cumulativeInfectedPersonHours_trapezoid": cumulative_trapezoid,
        "finalS": as_intish(last.get("S")),
        "finalE": as_intish(last.get("E")),
        "finalI1": as_intish(last.get("I1")),
        "finalI2": as_intish(last.get("I2")),
        "finalG1": as_intish(last.get("G1")),
        "finalG2": as_intish(last.get("G2")),
        "finalR": as_intish(last.get("R")),
        "anylogicSummaryAvailable": run_id in anylogic_summary_runs,
    }
    for column in SCENARIO_COLUMNS:
        value = params.get(column, "")
        if column == "modelMode" and str(value).strip() == "":
            value = "0"
        summary[column] = value

    quality_note = []
    if not run_completed:
        quality_note.append("simulation did not reach 180h")
    if not population_constant:
        quality_note.append("state population total changed")
    if any(dt < 0 for dt in dts):
        quality_note.append("negative time step")
    if len(set(times)) != len(times):
        quality_note.append("duplicate time values")

    quality = {
        "runId": run_id,
        "rawFile": path.name,
        "rowCount": len(rows),
        "maxTime": max_time,
        "runCompleted": run_completed,
        "expectedFinalTime": EXPECTED_FINAL_TIME,
        "medianDt": statistics.median(positive_dts) if positive_dts else "",
        "minDt": min(positive_dts) if positive_dts else "",
        "maxDt": max(positive_dts) if positive_dts else "",
        "hasDuplicateTimes": len(set(times)) != len(times),
        "hasNegativeTimeStep": any(dt < 0 for dt in dts),
        "populationConstant": population_constant,
        "populationInitial": populations[0],
        "populationMin": min(populations),
        "populationMax": max(populations),
        "qualityNote": "; ".join(quality_note) if quality_note else "ok",
    }
    return summary, quality


def build_parameter_table(parameter_files: list[Path]) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows: list[dict[str, str]] = []
    by_run: dict[str, dict[str, str]] = {}
    for path in parameter_files:
        for row in read_csv(path):
            run_id = row.get("runId", "")
            if not run_id:
                continue
            row = dict(row)
            row["parameterFile"] = path.name
            rows.append(row)
            by_run[run_id] = row
    return rows, by_run


def find_anylogic_summary_runs(summary_files: list[Path]) -> set[str]:
    run_ids: set[str] = set()
    for path in summary_files:
        for row in read_csv(path):
            if row.get("runId"):
                run_ids.add(row["runId"])
    return run_ids


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def build_group_summary(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in summary_rows:
        key = tuple(fmt(row.get(column, "")) for column in SCENARIO_COLUMNS)
        grouped.setdefault(key, []).append(row)

    group_rows: list[dict[str, Any]] = []
    for key, rows in sorted(grouped.items()):
        completed = [row for row in rows if str(row.get("runCompleted")).lower() == "true"]
        used_rows = [row for row in rows if str(row.get("usedForScenarioStats")).lower() == "true"]
        if not used_rows:
            used_rows = completed if completed else rows

        def nums(column: str) -> list[float]:
            return [as_float(row.get(column)) for row in used_rows]

        group_row = {column: value for column, value in zip(SCENARIO_COLUMNS, key)}
        group_row.update(
            {
                "nRuns": len(rows),
                "nCompleted": len(completed),
                "nUniqueSeedsCompleted": len({fmt(row.get("seedId", "")) for row in completed}),
                "nUsedForStats": len(used_rows),
                "duplicateCompletedRunsIgnored": max(0, len(completed) - len({fmt(row.get("seedId", "")) for row in completed})),
                "usedCompletedOnly": bool(completed),
                "meanI1Peak": mean(nums("I1Peak")),
                "sdI1Peak": sample_sd(nums("I1Peak")),
                "meanI1PeakTime": mean(nums("I1PeakTime")),
                "meanI2Peak": mean(nums("I2Peak")),
                "sdI2Peak": sample_sd(nums("I2Peak")),
                "meanI2PeakTime": mean(nums("I2PeakTime")),
                "meanTotalInfectedPeak": mean(nums("totalInfectedPeak")),
                "sdTotalInfectedPeak": sample_sd(nums("totalInfectedPeak")),
                "meanCumulativeRight": mean(nums("cumulativeInfectedPersonHours_right")),
                "sdCumulativeRight": sample_sd(nums("cumulativeInfectedPersonHours_right")),
                "meanCumulativeTrapezoid": mean(nums("cumulativeInfectedPersonHours_trapezoid")),
                "sdCumulativeTrapezoid": sample_sd(nums("cumulativeInfectedPersonHours_trapezoid")),
                "meanFinalR": mean(nums("finalR")),
                "sdFinalR": sample_sd(nums("finalR")),
            }
        )
        group_rows.append(group_row)
    return group_rows


def mark_statistical_runs(summary_rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in summary_rows:
        key = tuple(fmt(row.get(column, "")) for column in SCENARIO_COLUMNS)
        grouped.setdefault(key, []).append(row)

    for rows in grouped.values():
        completed = [row for row in rows if str(row.get("runCompleted")).lower() == "true"]
        candidates = completed if completed else rows
        latest_by_seed: dict[str, dict[str, Any]] = {}
        for row in candidates:
            seed = fmt(row.get("seedId", ""))
            current = latest_by_seed.get(seed)
            if current is None or run_order_value(row) >= run_order_value(current):
                latest_by_seed[seed] = row

        selected_ids = {row.get("runId") for row in latest_by_seed.values()}
        duplicate_seed_counts: dict[str, int] = {}
        for row in candidates:
            seed = fmt(row.get("seedId", ""))
            duplicate_seed_counts[seed] = duplicate_seed_counts.get(seed, 0) + 1

        for row in rows:
            selected = row.get("runId") in selected_ids
            row["usedForScenarioStats"] = selected
            if selected:
                if duplicate_seed_counts.get(fmt(row.get("seedId", "")), 0) > 1:
                    row["duplicateSeedPolicy"] = "used latest run for this seed"
                else:
                    row["duplicateSeedPolicy"] = "unique seed run"
            elif str(row.get("runCompleted")).lower() != "true":
                row["duplicateSeedPolicy"] = "partial/debug run excluded"
            else:
                row["duplicateSeedPolicy"] = "older duplicate seed run excluded"


def write_readme(out_dir: Path, summary_rows: list[dict[str, Any]], quality_rows: list[dict[str, Any]]) -> None:
    completed = sum(1 for row in summary_rows if str(row.get("runCompleted")).lower() == "true")
    partial = len(summary_rows) - completed
    lines = [
        "# AnyLogic 实验结果汇总说明",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 文件说明",
        "",
        "- `summary_from_raw.csv`：从 `raw_timeseries_*.csv` 重新计算的单次运行指标，是后续论文表格优先采用的数据源。",
        "- `scenario_group_summary.csv`：按干预时点、干预开关、网络参数和传播参数分组后的均值/标准差表；同一场景同一 seed 重复运行时，只采用最新完整运行。",
        "- `run_quality_audit.csv`：每个 raw 文件的完整性检查，重点看是否跑满 180h、时间步是否正常、总人数是否守恒。",
        "- `parameter_runs.csv`：AnyLogic 导出的参数主表，保留每次运行的参数记录。",
        "- `fig_timeseries_completed_runs.svg`：已跑满 180h 的 I1/I2 时间序列预览图，由 `scripts/plot_anylogic_results.py` 生成。",
        "- `fig_scenario_peak_comparison.svg`：场景峰值对比预览图，由 `scripts/plot_anylogic_results.py` 生成。",
        "- `paper_table_priority1_current.csv/.md`：论文可用的当前有效 seed 均值、标准差和 95%CI 表，由 `scripts/build_paper_stat_tables.py` 生成；跑满 30 seed 后会同步生成 `paper_table_priority1_30seed.csv/.md`。",
        "- `intervention_effects_vs_baseline.csv/.md`：相对无干预基准情景的降幅、Cohen's d 和 Welch t 统计量表，由 `scripts/build_paper_stat_tables.py` 生成。",
        "- `paper_result_sentences_current.md`：可回填论文实验结果部分的文字草稿，由 `scripts/build_paper_stat_tables.py` 生成；跑满 30 seed 后会同步生成 `paper_result_sentences_30seed.md`。",
        "",
        "## 指标口径",
        "",
        "- `I1Peak` / `I2Peak`：线上/线下传播者数量的首次最大值。",
        "- `I1PeakTime` / `I2PeakTime`：对应首次达峰时间，单位为 hour。",
        "- `totalInfectedPeak`：`I1 + I2` 的首次最大值。",
        "- `cumulativeInfectedPersonHours_right`：与 AnyLogic 当前 summary 写法一致，使用右端矩形法累加 `(I1 + I2) * dt`。",
        "- `cumulativeInfectedPersonHours_trapezoid`：使用梯形法计算的稳健性口径，可作为补充分析。",
        "- `runCompleted=false`：该运行未达到 180h，只能作为调试结果，不能直接进入论文主表。",
        "- `usedForScenarioStats=true`：该运行进入场景均值/标准差统计；同一参数组合下同一 seed 的旧重复运行会被排除。",
        "",
        "## 当前数据状态",
        "",
        f"- 已识别 raw 运行数：{len(summary_rows)}",
        f"- 跑满 180h 的运行数：{completed}",
        f"- 未跑满 180h 的调试运行数：{partial}",
        "",
        "## 后续要求",
        "",
        "- 论文主表只使用 `runCompleted=true` 且 `usedForScenarioStats=true` 的运行。",
        "- priority=1 主实验要求每个核心场景至少 30 个 seed；若只完成部分 seed，应在论文中明确写成阶段性预实验。",
        "- 每次补跑后重新执行 `python3 scripts/analyze_anylogic_outputs.py`，不要手工复制表格数值。",
        "- 需要更新图时，再执行 `python3 scripts/plot_anylogic_results.py`。",
        "- 需要更新论文表格和结果段落时，再执行 `python3 scripts/build_paper_stat_tables.py`。",
    ]

    if any(row.get("qualityNote") not in ("ok", "") for row in quality_rows):
        lines.extend(
            [
                "",
                "## 质量提醒",
                "",
                "当前存在未跑满或需复查的运行，请先查看 `run_quality_audit.csv`。",
            ]
        )

    (out_dir / "README_实验结果说明.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_rows(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, str]]:
    return [{field: fmt(row.get(field, "")) for field in fields} for row in rows]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze AnyLogic CSV outputs.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    data_dir = args.data_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(data_dir.glob("raw_timeseries_*.csv"))
    parameter_files = sorted(data_dir.glob("parameter_master_*.csv"))
    anylogic_summary_files = sorted(data_dir.glob("summary_metrics_*.csv"))

    parameter_rows, parameter_by_run = build_parameter_table(parameter_files)
    anylogic_summary_runs = find_anylogic_summary_runs(anylogic_summary_files)

    summary_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    for path in raw_files:
        summary, quality = analyze_raw_file(path, parameter_by_run, anylogic_summary_runs)
        if summary:
            summary_rows.append(summary)
        quality_rows.append(quality)

    mark_statistical_runs(summary_rows)
    group_rows = build_group_summary(summary_rows)

    parameter_fields = sorted({key for row in parameter_rows for key in row.keys()})
    if parameter_rows and "runId" in parameter_fields:
        parameter_fields.remove("runId")
        parameter_fields = ["runId", *parameter_fields]

    write_csv(out_dir / "summary_from_raw.csv", normalize_rows(summary_rows, SUMMARY_FIELDS), SUMMARY_FIELDS)
    write_csv(out_dir / "run_quality_audit.csv", normalize_rows(quality_rows, QUALITY_FIELDS), QUALITY_FIELDS)
    write_csv(out_dir / "scenario_group_summary.csv", normalize_rows(group_rows, GROUP_FIELDS), GROUP_FIELDS)
    if parameter_fields:
        write_csv(out_dir / "parameter_runs.csv", parameter_rows, parameter_fields)
    else:
        write_csv(out_dir / "parameter_runs.csv", [], ["runId"])
    write_readme(out_dir, summary_rows, quality_rows)

    print(f"Raw runs analyzed: {len(summary_rows)}")
    print(f"Completed 180h runs: {sum(1 for row in summary_rows if row.get('runCompleted'))}")
    print(f"Runs used for scenario stats: {sum(1 for row in summary_rows if row.get('usedForScenarioStats'))}")
    print(f"Output directory: {out_dir}")


if __name__ == "__main__":
    main()
