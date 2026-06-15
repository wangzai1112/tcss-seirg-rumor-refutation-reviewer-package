#!/usr/bin/env python3
"""Build paired common-seed comparisons for the M0 main scenarios.

This script reads data/processed/simulation/summary_from_raw.csv, selects the
completed M0 runs used for scenario statistics, and compares each main M0
scenario with the no-intervention baseline using the same seed IDs.

The output is intended to complement the Welch-test table. It uses paired
differences because the manuscript scenarios reuse seed IDs 1--30.
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "data" / "processed" / "simulation" / "summary_from_raw.csv"
OUT_CSV = ROOT / "results" / "tables" / "paired_seed_comparisons_m0.csv"
OUT_MD = ROOT / "results" / "tables" / "paired_seed_comparisons_m0.md"
OUT_PEAK_CSV = ROOT / "results" / "tables" / "paired_peak_comparisons_m0.csv"
OUT_PEAK_MD = ROOT / "results" / "tables" / "paired_peak_comparisons_m0.md"

METRICS = ("cumulativeInfectedPersonHours_right", "totalInfectedPeak")

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
        "Dual-track, T=15",
        {
            **BASE_PARAMS,
            "interventionStartTime": 15.0,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
        },
    ),
    (
        "Dual-track, T=30",
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
        },
    ),
    (
        "Dual-track, T=60",
        {
            **BASE_PARAMS,
            "interventionStartTime": 60.0,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
        },
    ),
    (
        "Online-only",
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": False,
        },
    ),
    (
        "Offline-only",
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": False,
            "enableOfflineIntervention": True,
        },
    ),
    (
        "Weak dual-track",
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
            "onlineGovEffect": 0.02,
            "offlineGovEffect": 0.05,
        },
    ),
    (
        "Strong dual-track",
        {
            **BASE_PARAMS,
            "enableOnlineIntervention": True,
            "enableOfflineIntervention": True,
            "onlineGovEffect": 0.10,
            "offlineGovEffect": 0.30,
        },
    ),
]


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_row(row: dict[str, str]) -> dict[str, object]:
    parsed: dict[str, object] = dict(row)
    for key in (
        "modelMode",
        "seedId",
        "kOnline",
        "kOffline",
    ):
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
    for key in ("enableOnlineIntervention", "enableOfflineIntervention", "runCompleted", "usedForScenarioStats"):
        parsed[key] = parse_bool(row[key])
    return parsed


def matches(row: dict[str, object], params: dict[str, object]) -> bool:
    for key, expected in params.items():
        actual = row[key]
        if isinstance(expected, float):
            if abs(float(actual) - expected) > 1e-9:
                return False
        else:
            if actual != expected:
                return False
    return bool(row["runCompleted"]) and bool(row["usedForScenarioStats"])


def by_seed(rows: list[dict[str, object]], params: dict[str, object]) -> dict[int, dict[str, object]]:
    selected = [row for row in rows if matches(row, params)]
    output: dict[int, dict[str, object]] = {}
    for row in selected:
        seed = int(row["seedId"])
        if seed in output:
            raise ValueError(f"Duplicate selected run for seed {seed} and params {params}")
        output[seed] = row
    return output


def paired_summary(label: str, metric: str, baseline: dict[int, dict[str, object]], scenario: dict[int, dict[str, object]]) -> dict[str, object]:
    seeds = sorted(set(baseline) & set(scenario))
    if not seeds:
        raise ValueError(f"No matched seeds for {label}")
    diffs = [float(scenario[seed][metric]) - float(baseline[seed][metric]) for seed in seeds]
    n = len(diffs)
    mean = statistics.fmean(diffs)
    sd = statistics.stdev(diffs) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    tcrit = 2.045229642 if n == 30 else 1.96
    ci_low = mean - tcrit * se
    ci_high = mean + tcrit * se
    paired_t = mean / se if se else math.inf
    return {
        "scenario": label,
        "metric": metric,
        "n": n,
        "meanDiff": mean,
        "sdDiff": sd,
        "ci95Low": ci_low,
        "ci95High": ci_high,
        "pairedT": paired_t,
    }


def write_markdown(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Paired Common-Seed Comparisons for M0",
        "",
        "Differences are scenario minus no-intervention baseline within the same seed ID.",
        "Negative values indicate lower cumulative burden or peak under the scenario.",
        "",
        "| Scenario | Metric | n | Mean diff. | SD diff. | 95% CI | Paired t |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {metric} | {n} | {meanDiff:.2f} | {sdDiff:.2f} | [{ci95Low:.2f}, {ci95High:.2f}] | {pairedT:.2f} |".format(**row)
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_peak_outputs(rows: list[dict[str, object]]) -> None:
    peak_rows = [row for row in rows if row["metric"] == "totalInfectedPeak"]
    with OUT_PEAK_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["scenario", "n", "meanPeakDiff", "sdPeakDiff", "ci95Low", "ci95High", "pairedT"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in peak_rows:
            writer.writerow(
                {
                    "scenario": row["scenario"],
                    "n": row["n"],
                    "meanPeakDiff": row["meanDiff"],
                    "sdPeakDiff": row["sdDiff"],
                    "ci95Low": row["ci95Low"],
                    "ci95High": row["ci95High"],
                    "pairedT": row["pairedT"],
                }
            )

    lines = [
        "# Paired Peak-Difference Comparisons for M0",
        "",
        "Differences are scenario peak minus no-intervention peak within the same seed ID.",
        "Negative values indicate lower total active-spreader peak under the scenario.",
        "",
        "| Scenario | n | Mean peak diff. | SD diff. | 95% CI | Paired t |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for row in peak_rows:
        lines.append(
            "| {scenario} | {n} | {meanDiff:.2f} | {sdDiff:.2f} | [{ci95Low:.2f}, {ci95High:.2f}] | {pairedT:.2f} |".format(**row)
        )
    OUT_PEAK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    with SUMMARY.open(newline="", encoding="utf-8-sig") as f:
        rows = [parse_row(row) for row in csv.DictReader(f)]

    baseline = by_seed(rows, BASE_PARAMS)
    if len(baseline) != 30:
        raise ValueError(f"Expected 30 baseline seeds, found {len(baseline)}")

    output: list[dict[str, object]] = []
    for label, params in SCENARIOS:
        scenario = by_seed(rows, params)
        if len(scenario) != 30:
            raise ValueError(f"Expected 30 seeds for {label}, found {len(scenario)}")
        for metric in METRICS:
            output.append(paired_summary(label, metric, baseline, scenario))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["scenario", "metric", "n", "meanDiff", "sdDiff", "ci95Low", "ci95High", "pairedT"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
    write_markdown(output)
    write_peak_outputs(output)
    print(OUT_CSV)
    print(OUT_MD)
    print(OUT_PEAK_CSV)
    print(OUT_PEAK_MD)


if __name__ == "__main__":
    main()
