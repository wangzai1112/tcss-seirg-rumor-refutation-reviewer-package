#!/usr/bin/env python3
"""Build complete statistical tables for the current AnyLogic result summary.

Outputs are designed for the SCI v3 upgrade: mean, SD, 95% CI, Welch t-test,
p-value, Cohen's d, Hedges' g, and BH/Holm multiple-comparison corrections.
The script does not require scipy; it computes Student-t tail probabilities by
numerical integration, which is accurate enough for the 30-seed comparison
tables used here.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev


def find_package_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "results").exists() and (parent / "docs").exists():
            return parent
    return Path(__file__).resolve().parents[2]


ROOT = find_package_root()
SUMMARY = ROOT / "results" / "summary" / "summary_from_raw.csv"
QUEUE = ROOT / "results" / "designs" / "全量重跑实验队列_SCI_v3.csv"
SUPPLEMENTAL_QUEUES = [
    ROOT / "results" / "designs" / "第五章九情景补充队列_20260613.csv",
]
OUT_DIR = ROOT / "results" / "tables"
OUT_CSV = OUT_DIR / "complete_stat_tests_current.csv"
OUT_MD = OUT_DIR / "complete_stat_tests_current.md"

MATCH_FIELDS = [
    "modelMode",
    "seedId",
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

METRICS = [
    ("I1Peak", "线上传播者峰值", "lower"),
    ("I2Peak", "线下传播者峰值", "lower"),
    ("totalInfectedPeak", "总传播者峰值", "lower"),
    ("cumulativeInfectedPersonHours_right", "累计传播者人时", "lower"),
    ("G1Peak", "线上辟谣干预状态峰值", "context"),
    ("G2Peak", "线下辟谣干预状态峰值", "context"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm_bool(value: str) -> str:
    return str(value).strip().lower()


def norm_number(value: str) -> str:
    value = str(value).strip()
    if value == "":
        return ""
    try:
        number = float(value)
    except ValueError:
        return value
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.10g}"


def key_for(row: dict[str, str]) -> tuple[str, ...]:
    values: list[str] = []
    for field in MATCH_FIELDS:
        value = row.get(field, "")
        if field == "modelMode" and str(value).strip() == "":
            value = "0"
        if field.startswith("enable"):
            values.append(norm_bool(value))
        else:
            values.append(norm_number(value))
    return tuple(values)


def model_mode(meta: dict[str, str]) -> str:
    value = norm_number(meta.get("modelMode", "0"))
    return value if value != "" else "0"


def existing_queues() -> list[Path]:
    queues = [QUEUE]
    queues.extend(path for path in SUPPLEMENTAL_QUEUES if path.exists())
    return queues


def load_queue_index() -> dict[tuple[str, ...], dict[str, str]]:
    index: dict[tuple[str, ...], dict[str, str]] = {}
    for queue_path in existing_queues():
        for row in read_csv(queue_path):
            index[key_for(row)] = row
    return index


def safe_float(value: str) -> float | None:
    try:
        if str(value).strip() == "":
            return None
        result = float(value)
    except ValueError:
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def t_pdf(x: float, df: float) -> float:
    log_coef = math.lgamma((df + 1.0) / 2.0) - math.lgamma(df / 2.0)
    log_coef -= 0.5 * (math.log(df) + math.log(math.pi))
    return math.exp(log_coef) * (1.0 + x * x / df) ** (-(df + 1.0) / 2.0)


def integrate_simpson(func, upper: float, df: float) -> float:
    if upper <= 0:
        return 0.0
    if upper > 60:
        upper = 60.0
    intervals = max(400, int(upper * 800))
    if intervals % 2 == 1:
        intervals += 1
    h = upper / intervals
    total = func(0.0, df) + func(upper, df)
    odd_sum = 0.0
    even_sum = 0.0
    for i in range(1, intervals):
        x = i * h
        if i % 2:
            odd_sum += func(x, df)
        else:
            even_sum += func(x, df)
    return h * (total + 4.0 * odd_sum + 2.0 * even_sum) / 3.0


def student_t_two_sided_p(t_value: float, df: float) -> float:
    if df <= 0 or math.isnan(t_value):
        return math.nan
    abs_t = abs(t_value)
    if abs_t == 0:
        return 1.0
    area = integrate_simpson(t_pdf, abs_t, df)
    cdf = 0.5 + area
    p = 2.0 * max(0.0, 1.0 - cdf)
    return min(1.0, max(0.0, p))


def welch(a: list[float], b: list[float]) -> tuple[float, float, float]:
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return math.nan, math.nan, math.nan
    m1, m2 = mean(a), mean(b)
    s1, s2 = stdev(a), stdev(b)
    v1, v2 = s1 * s1 / n1, s2 * s2 / n2
    denom = math.sqrt(v1 + v2)
    if denom == 0:
        return 0.0, math.inf, 1.0
    t_value = (m1 - m2) / denom
    df_num = (v1 + v2) ** 2
    df_den = 0.0
    if n1 > 1:
        df_den += (v1 * v1) / (n1 - 1)
    if n2 > 1:
        df_den += (v2 * v2) / (n2 - 1)
    df = df_num / df_den if df_den else math.inf
    p = student_t_two_sided_p(t_value, df) if math.isfinite(df) else 0.0
    return t_value, df, p


def cohen_d(a: list[float], b: list[float]) -> tuple[float, float]:
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return math.nan, math.nan
    s1, s2 = stdev(a), stdev(b)
    pooled_num = (n1 - 1) * s1 * s1 + (n2 - 1) * s2 * s2
    pooled_den = n1 + n2 - 2
    if pooled_den <= 0 or pooled_num == 0:
        return 0.0, 0.0
    pooled = math.sqrt(pooled_num / pooled_den)
    d = (mean(a) - mean(b)) / pooled
    correction = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    return d, d * correction


def ci95(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n < 2:
        return math.nan, math.nan
    m = mean(values)
    se = stdev(values) / math.sqrt(n)
    return m - 1.96 * se, m + 1.96 * se


def adjust_bh(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adjusted = [math.nan] * m
    prev = 1.0
    for rank_from_end, idx in enumerate(reversed(order), start=1):
        rank = m - rank_from_end + 1
        value = min(prev, pvals[idx] * m / rank)
        adjusted[idx] = min(1.0, value)
        prev = adjusted[idx]
    return adjusted


def adjust_holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adjusted = [math.nan] * m
    running = 0.0
    for rank, idx in enumerate(order, start=1):
        value = min(1.0, (m - rank + 1) * pvals[idx])
        running = max(running, value)
        adjusted[idx] = running
    return adjusted


def fmt(value: float | None, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, float) and math.isinf(value):
        return "inf"
    if abs(value) < 1e-4 and value != 0:
        return f"{value:.3e}"
    return f"{value:.{digits}f}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    queue_index = load_queue_index()
    planned_by_mode: dict[str, int] = defaultdict(int)
    planned_main_by_mode: dict[str, int] = defaultdict(int)
    planned_supplemental_by_mode: dict[str, int] = defaultdict(int)
    for queue_path in existing_queues():
        is_supplemental = queue_path != QUEUE
        for queue_row in read_csv(queue_path):
            mode = model_mode(queue_row)
            planned_by_mode[mode] += 1
            if is_supplemental:
                planned_supplemental_by_mode[mode] += 1
            else:
                planned_main_by_mode[mode] += 1

    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    scenario_meta: dict[str, dict[str, str]] = {}
    used_rows_by_mode: dict[str, int] = defaultdict(int)

    unmatched = 0
    for raw in read_csv(SUMMARY):
        if str(raw.get("usedForScenarioStats", "")).strip().lower() not in {"true", "1", "yes"}:
            continue
        queue_row = queue_index.get(key_for(raw))
        if not queue_row:
            unmatched += 1
            continue
        sid = queue_row.get("scenarioId", "").strip() or queue_row.get("queueId", "").strip()
        scenario_meta[sid] = queue_row
        used_rows_by_mode[model_mode(queue_row)] += 1
        for metric, _label, _direction in METRICS:
            value = safe_float(raw.get(metric, ""))
            if value is not None:
                grouped[sid][metric].append(value)

    baseline_candidates_by_mode: dict[str, list[str]] = defaultdict(list)
    for sid, meta in scenario_meta.items():
        if (
            norm_bool(meta.get("enableOnlineIntervention", "")) == "false"
            and norm_bool(meta.get("enableOfflineIntervention", "")) == "false"
        ):
            baseline_candidates_by_mode[model_mode(meta)].append(sid)

    baseline_by_mode: dict[str, str] = {}
    for mode, candidates in baseline_candidates_by_mode.items():
        baseline_id = ""
        for sid in candidates:
            name = scenario_meta[sid].get("scenarioName", "")
            if ("无" in name and "干预" in name) or "no_intervention" in sid:
                baseline_id = sid
                break
        if not baseline_id:
            baseline_id = sorted(candidates)[0]
        baseline_by_mode[mode] = baseline_id

    if not baseline_by_mode:
        raise RuntimeError("No no-intervention baseline scenario found")

    rows: list[dict[str, str]] = []
    p_index: dict[tuple[str, str], list[int]] = defaultdict(list)

    for sid in sorted(grouped):
        meta = scenario_meta[sid]
        mode = model_mode(meta)
        baseline_id = baseline_by_mode.get(mode)
        if not baseline_id:
            continue
        for metric, metric_label, direction in METRICS:
            values = grouped[sid].get(metric, [])
            if not values:
                continue
            n = len(values)
            metric_mean = mean(values)
            metric_sd = stdev(values) if n > 1 else math.nan
            ci_low, ci_high = ci95(values)
            baseline_values = grouped[baseline_id].get(metric, [])
            diff = metric_mean - mean(baseline_values) if baseline_values else math.nan
            reduction_pct = (
                (mean(baseline_values) - metric_mean) / mean(baseline_values) * 100.0
                if baseline_values and mean(baseline_values) != 0
                else math.nan
            )
            if sid == baseline_id:
                t_value = df = p_value = d = g = math.nan
            else:
                t_value, df, p_value = welch(values, baseline_values)
                d, g = cohen_d(values, baseline_values)

            row = {
                "modelMode": mode,
                "completedModeRuns": str(used_rows_by_mode.get(mode, 0)),
                "plannedModeRuns": str(planned_by_mode.get(mode, 0)),
                "modeComplete": str(
                    used_rows_by_mode.get(mode, 0) >= planned_by_mode.get(mode, 0)
                    and planned_by_mode.get(mode, 0) > 0
                ).lower(),
                "scenarioId": sid,
                "scenarioName": meta.get("scenarioName", ""),
                "scenarioGroup": meta.get("scenarioGroup", ""),
                "metric": metric,
                "metricLabel": metric_label,
                "metricDirection": direction,
                "n": str(n),
                "mean": fmt(metric_mean),
                "sd": fmt(metric_sd),
                "ci95Low": fmt(ci_low),
                "ci95High": fmt(ci_high),
                "baselineScenarioId": baseline_id,
                "baselineScenarioName": scenario_meta[baseline_id].get("scenarioName", ""),
                "differenceVsBaseline": fmt(diff),
                "reductionPctVsBaseline": fmt(reduction_pct),
                "welchT": fmt(t_value),
                "welchDf": fmt(df),
                "pValue": fmt(p_value, 6),
                "cohenD": fmt(d),
                "hedgesG": fmt(g),
                "pBHByMetric": "",
                "pHolmByMetric": "",
            }
            rows.append(row)
            if sid != baseline_id and not math.isnan(p_value):
                p_index[(mode, metric)].append(len(rows) - 1)

    for _metric_key, indexes in p_index.items():
        pvals = [float(rows[i]["pValue"]) for i in indexes]
        bh = adjust_bh(pvals)
        holm = adjust_holm(pvals)
        for idx, bh_value, holm_value in zip(indexes, bh, holm):
            rows[idx]["pBHByMetric"] = fmt(bh_value, 6)
            rows[idx]["pHolmByMetric"] = fmt(holm_value, 6)

    fieldnames = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    baseline_text = "；".join(
        f"M{mode}: {scenario_meta[sid].get('scenarioName', sid)}"
        for mode, sid in sorted(baseline_by_mode.items(), key=lambda item: int(item[0]))
    )
    coverage_text = "；".join(
        f"M{mode}: {used_rows_by_mode.get(mode, 0)}/{planned_by_mode.get(mode, 0)}"
        for mode in sorted(planned_by_mode, key=lambda value: int(value))
    )
    incomplete_modes = [
        mode
        for mode in sorted(planned_by_mode, key=lambda value: int(value))
        if used_rows_by_mode.get(mode, 0) < planned_by_mode.get(mode, 0)
    ]
    completion_warning = "、".join(f"M{mode}" for mode in incomplete_modes) if incomplete_modes else "无"
    primary_rows = [
        r
        for r in rows
        if r["metric"] in {"I1Peak", "I2Peak", "totalInfectedPeak", "cumulativeInfectedPersonHours_right"}
    ]
    is_complete = not incomplete_modes
    md_lines = [
        "# 完整统计检验表（SCI v3 全量 30 seed 结果）"
        if is_complete
        else "# 当前可用统计检验表（SCI v3 队列阶段性结果）",
        "",
        f"- 数据源：`{SUMMARY.relative_to(ROOT)}`",
        f"- 队列源：{'; '.join(f'`{path.relative_to(ROOT)}`' for path in existing_queues())}",
        f"- 队列完成度：{coverage_text}",
        f"- 主队列计划数：{'; '.join(f'M{mode}: {planned_main_by_mode.get(mode, 0)}' for mode in sorted(planned_by_mode, key=lambda value: int(value)))}",
        f"- 补充队列计划数：{'; '.join(f'M{mode}: {planned_supplemental_by_mode.get(mode, 0)}' for mode in sorted(planned_by_mode, key=lambda value: int(value)))}",
        f"- 对照基线：{baseline_text}",
        f"- 未匹配汇总行：{unmatched}",
        "- 检验口径：所有非基线场景均与同一模型模式下的无干预基准情景做 Welch t 检验；同一模型模式、同一指标族内给出 BH-FDR 与 Holm 修正。",
        "",
        "| 模型 | 场景 | 指标 | n | 均值 | SD | 95%CI | 相对基线降幅(%) | Welch t | p | BH-FDR | Hedges g |",
        "|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    if not is_complete:
        md_lines.insert(
            5,
            f"- 阶段性提醒：未完成模式为 {completion_warning}。含未完成模式的统计结果只用于过程审计，不能作为最终 30 seed 论文结论。",
        )
    for row in primary_rows:
        ci = f"[{row['ci95Low']}, {row['ci95High']}]"
        md_lines.append(
            "| M{mode} | {scenario} | {metric} | {n} | {mean} | {sd} | {ci} | {reduction} | {t} | {p} | {bh} | {g} |".format(
                mode=row["modelMode"],
                scenario=row["scenarioName"] or row["scenarioId"],
                metric=row["metricLabel"],
                n=row["n"],
                mean=row["mean"],
                sd=row["sd"],
                ci=ci,
                reduction=row["reductionPctVsBaseline"],
                t=row["welchT"],
                p=row["pValue"],
                bh=row["pBHByMetric"],
                g=row["hedgesG"],
            )
        )
    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV} ({len(rows)} rows)")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
