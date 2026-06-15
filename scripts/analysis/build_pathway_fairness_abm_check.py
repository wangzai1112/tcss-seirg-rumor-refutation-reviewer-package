#!/usr/bin/env python3
"""Build the budget-matched ABM pathway fairness supplement.

The main manuscript pathway table uses unequal refutation-strength fields
(`onlineGovEffect=0.05`, `offlineGovEffect=0.15`). This supplement reads the
recomputed AnyLogic summary table and reports a same-budget ABM check at
Tg=30, using the same seed IDs and network settings as the main M0 runs.
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "results" / "summary" / "summary_from_raw.csv"
OUT_CSV = ROOT / "results" / "summary" / "pathway_fairness_abm_check.csv"
OUT_MD = ROOT / "results" / "summary" / "pathway_fairness_abm_check.md"

METRICS = ("totalInfectedPeak", "cumulativeInfectedPersonHours_right")

BASE_PARAMS = {
    "modelMode": 0,
    "interventionStartTime": 30.0,
    "enableOnlineIntervention": False,
    "enableOfflineIntervention": False,
    "kOnline": 6,
    "kOffline": 4,
    "pRewire": 0.10,
    "onlineRate": 35.0,
    "offlineRate": 5.0,
    "onlineGovEffect": 0.05,
    "offlineGovEffect": 0.15,
    "latentTime": 2.0,
    "forgetTime": 30.0,
    "govForgetTime": 4.0,
}

SCENARIOS = [
    (
        "No intervention baseline",
        "reference",
        0.00,
        0.00,
        BASE_PARAMS,
    ),
    (
        "Budget-matched online-only",
        "0.20 / 0.00",
        0.20,
        0.00,
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "onlineGovEffect": 0.20,
            "offlineGovEffect": 0.00,
        },
    ),
    (
        "Budget-matched equal dual",
        "0.10 / 0.10",
        0.10,
        0.10,
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
            "onlineGovEffect": 0.10,
            "offlineGovEffect": 0.10,
        },
    ),
    (
        "Reported dual-track anchor",
        "0.05 / 0.15",
        0.05,
        0.15,
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
        },
    ),
    (
        "Budget-matched offline-only",
        "0.00 / 0.20",
        0.00,
        0.20,
        {
            **BASE_PARAMS,
            "enableOfflineIntervention": True,
            "onlineGovEffect": 0.00,
            "offlineGovEffect": 0.20,
        },
    ),
]


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_row(row: dict[str, str]) -> dict[str, object]:
    parsed: dict[str, object] = dict(row)
    for key in ("modelMode", "seedId", "kOnline", "kOffline"):
        parsed[key] = int(float(row[key]))
    for key in (
        "interventionStartTime",
        "pRewire",
        "onlineRate",
        "offlineRate",
        "onlineGovEffect",
        "offlineGovEffect",
        "latentTime",
        "forgetTime",
        "govForgetTime",
        *METRICS,
    ):
        parsed[key] = float(row[key])
    for key in (
        "enableOnlineIntervention",
        "enableOfflineIntervention",
        "runCompleted",
        "usedForScenarioStats",
    ):
        parsed[key] = parse_bool(row[key])
    return parsed


def matches(row: dict[str, object], params: dict[str, object]) -> bool:
    if not bool(row["runCompleted"]) or not bool(row["usedForScenarioStats"]):
        return False
    for key, expected in params.items():
        actual = row[key]
        if isinstance(expected, float):
            if abs(float(actual) - expected) > 1e-9:
                return False
        elif actual != expected:
            return False
    return True


def select_by_seed(rows: list[dict[str, object]], params: dict[str, object]) -> dict[int, dict[str, object]]:
    selected = [row for row in rows if matches(row, params)]
    by_seed: dict[int, dict[str, object]] = {}
    for row in selected:
        seed = int(row["seedId"])
        if seed in by_seed:
            raise ValueError(f"Duplicate selected run for seed {seed}: {params}")
        by_seed[seed] = row
    if len(by_seed) != 30:
        missing = sorted(set(range(1, 31)) - set(by_seed))
        raise ValueError(f"Expected 30 seeds for {params}, found {len(by_seed)}; missing={missing}")
    return by_seed


def mean_sd(values: list[float]) -> tuple[float, float]:
    return statistics.fmean(values), statistics.stdev(values) if len(values) > 1 else 0.0


def paired_ci(diffs: list[float]) -> tuple[float, float, float, float]:
    n = len(diffs)
    mean = statistics.fmean(diffs)
    sd = statistics.stdev(diffs) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    tcrit = 2.045229642 if n == 30 else 1.96
    return mean, sd, mean - tcrit * se, mean + tcrit * se


def fmt(value: float) -> str:
    return f"{value:.2f}"


def build_rows(rows: list[dict[str, object]]) -> list[dict[str, Any]]:
    baseline = select_by_seed(rows, BASE_PARAMS)
    baseline_peak = [float(row["totalInfectedPeak"]) for row in baseline.values()]
    baseline_burden = [float(row["cumulativeInfectedPersonHours_right"]) for row in baseline.values()]
    baseline_peak_mean, _ = mean_sd(baseline_peak)
    baseline_burden_mean, _ = mean_sd(baseline_burden)

    output: list[dict[str, Any]] = []
    for label, allocation, alpha1, alpha2, params in SCENARIOS:
        selected = select_by_seed(rows, params)
        seeds = sorted(selected)
        peaks = [float(selected[seed]["totalInfectedPeak"]) for seed in seeds]
        burdens = [float(selected[seed]["cumulativeInfectedPersonHours_right"]) for seed in seeds]
        peak_mean, peak_sd = mean_sd(peaks)
        burden_mean, burden_sd = mean_sd(burdens)
        peak_diffs = [peaks[index] - float(baseline[seed]["totalInfectedPeak"]) for index, seed in enumerate(seeds)]
        burden_diffs = [
            burdens[index] - float(baseline[seed]["cumulativeInfectedPersonHours_right"])
            for index, seed in enumerate(seeds)
        ]
        peak_diff, peak_diff_sd, peak_ci_low, peak_ci_high = paired_ci(peak_diffs)
        burden_diff, burden_diff_sd, burden_ci_low, burden_ci_high = paired_ci(burden_diffs)
        output.append(
            {
                "scenario": label,
                "alpha1_alpha2": allocation,
                "onlineGovEffect": alpha1,
                "offlineGovEffect": alpha2,
                "n": len(seeds),
                "peak_mean": peak_mean,
                "peak_sd": peak_sd,
                "peak_change_vs_baseline": peak_mean - baseline_peak_mean,
                "peak_reduction_pct": (baseline_peak_mean - peak_mean) / baseline_peak_mean * 100.0,
                "paired_peak_diff_mean": peak_diff,
                "paired_peak_diff_sd": peak_diff_sd,
                "paired_peak_diff_ci95_low": peak_ci_low,
                "paired_peak_diff_ci95_high": peak_ci_high,
                "burden_mean": burden_mean,
                "burden_sd": burden_sd,
                "burden_change_vs_baseline": burden_mean - baseline_burden_mean,
                "burden_reduction_pct": (baseline_burden_mean - burden_mean) / baseline_burden_mean * 100.0,
                "paired_burden_diff_mean": burden_diff,
                "paired_burden_diff_sd": burden_diff_sd,
                "paired_burden_diff_ci95_low": burden_ci_low,
                "paired_burden_diff_ci95_high": burden_ci_high,
            }
        )
    return output


def write_csv(rows: list[dict[str, Any]]) -> None:
    fields = [
        "scenario",
        "alpha1_alpha2",
        "onlineGovEffect",
        "offlineGovEffect",
        "n",
        "peak_mean",
        "peak_sd",
        "peak_change_vs_baseline",
        "peak_reduction_pct",
        "paired_peak_diff_mean",
        "paired_peak_diff_sd",
        "paired_peak_diff_ci95_low",
        "paired_peak_diff_ci95_high",
        "burden_mean",
        "burden_sd",
        "burden_change_vs_baseline",
        "burden_reduction_pct",
        "paired_burden_diff_mean",
        "paired_burden_diff_sd",
        "paired_burden_diff_ci95_low",
        "paired_burden_diff_ci95_high",
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Budget-Matched ABM Pathway Fairness Check",
        "",
        "This supplementary table reports completed 30-seed AnyLogic M0 runs at `Tg=30` under the same population, network, propagation, state-duration, and common-seed settings as the main pathway scenarios. The check separates the reported pathway-strength comparison from a same-budget allocation check. It is a model-internal sensitivity check, not a real-world pathway ranking.",
        "",
        "| Scenario | alpha1/alpha2 | n | Peak mean (SD) | Peak change | Burden mean (SD) | Burden change | Burden reduction | Paired burden diff. 95% CI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {alpha1_alpha2} | {n} | {peak_mean} ({peak_sd}) | {peak_change_vs_baseline} | {burden_mean} ({burden_sd}) | {burden_change_vs_baseline} | {burden_reduction_pct}% | [{paired_burden_diff_ci95_low}, {paired_burden_diff_ci95_high}] |".format(
                scenario=row["scenario"],
                alpha1_alpha2=row["alpha1_alpha2"],
                n=row["n"],
                peak_mean=fmt(row["peak_mean"]),
                peak_sd=fmt(row["peak_sd"]),
                peak_change_vs_baseline=fmt(row["peak_change_vs_baseline"]),
                burden_mean=fmt(row["burden_mean"]),
                burden_sd=fmt(row["burden_sd"]),
                burden_change_vs_baseline=fmt(row["burden_change_vs_baseline"]),
                burden_reduction_pct=fmt(row["burden_reduction_pct"]),
                paired_burden_diff_ci95_low=fmt(row["paired_burden_diff_ci95_low"]),
                paired_burden_diff_ci95_high=fmt(row["paired_burden_diff_ci95_high"]),
            )
        )
    lines.extend(
        [
            "",
            "Interpretation boundary: under this parameterization, the budget-matched ordering differs from the unequal-strength pathway table. The online-only `0.20/0.00` allocation yields the largest cumulative-burden reduction in this check, followed by offline-only `0.00/0.20`, the reported `0.05/0.15` dual-track anchor, and equal-dual `0.10/0.10`. Therefore, the main pathway table should be read as a pathway-strength scenario comparison. This finding remains conditional on the implemented contact structure, propagation rates, statechart triggers, and `Tg=30`; it does not provide a pathway ranking outside this model setting.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    with SUMMARY.open(newline="", encoding="utf-8-sig") as handle:
        rows = [parse_row(row) for row in csv.DictReader(handle)]
    output = build_rows(rows)
    write_csv(output)
    write_markdown(output)
    print(OUT_CSV)
    print(OUT_MD)


if __name__ == "__main__":
    main()
