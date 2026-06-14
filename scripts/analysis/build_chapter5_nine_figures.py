from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any


def find_package_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "results").exists() and (parent / "docs").exists():
            return parent
    return Path(__file__).resolve().parents[2]


ROOT = find_package_root()
LOCAL_DEPS = ROOT / ".codex_local_pydeps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


SUMMARY = ROOT / "results" / "summary" / "summary_from_raw.csv"
RAW_DIR = ROOT / "data" / "raw" / "anylogic_outputs"
OUT_DIR = ROOT / "results" / "figures" / "第五章九情景重绘"


SCENARIOS = [
    {
        "figure": "5.2",
        "stem": "图5-2_基准情景_30seed均值",
        "cn": "基准情景",
        "en": "Benchmark scenario",
        "params": {"interventionStartTime": "30", "enableOnlineIntervention": "false", "enableOfflineIntervention": "false"},
        "states": ["S", "E", "I1", "I2", "R"],
    },
    {
        "figure": "5.3.1",
        "stem": "图5-3-1_双轨辟谣干预T15_30seed均值",
        "cn": "双轨辟谣干预 T=15",
        "en": "Dual-track rumor-refutation intervention, T=15",
        "params": {"interventionStartTime": "15", "enableOnlineIntervention": "true", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G1", "G2", "R"],
    },
    {
        "figure": "5.3.2",
        "stem": "图5-3-2_双轨辟谣干预T30_30seed均值",
        "cn": "双轨辟谣干预 T=30",
        "en": "Dual-track rumor-refutation intervention, T=30",
        "params": {"interventionStartTime": "30", "enableOnlineIntervention": "true", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G1", "G2", "R"],
    },
    {
        "figure": "5.3.3",
        "stem": "图5-3-3_双轨辟谣干预T60_30seed均值",
        "cn": "双轨辟谣干预 T=60",
        "en": "Dual-track rumor-refutation intervention, T=60",
        "params": {"interventionStartTime": "60", "enableOnlineIntervention": "true", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G1", "G2", "R"],
    },
    {
        "figure": "5.3.4",
        "stem": "图5-3-4_线下单维辟谣干预T15_30seed均值",
        "cn": "线下单维辟谣干预 T=15",
        "en": "Offline single-track rumor-refutation intervention, T=15",
        "params": {"interventionStartTime": "15", "enableOnlineIntervention": "false", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G2", "R"],
    },
    {
        "figure": "5.3.5",
        "stem": "图5-3-5_线下单维辟谣干预T30_30seed均值",
        "cn": "线下单维辟谣干预 T=30",
        "en": "Offline single-track rumor-refutation intervention, T=30",
        "params": {"interventionStartTime": "30", "enableOnlineIntervention": "false", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G2", "R"],
    },
    {
        "figure": "5.3.6",
        "stem": "图5-3-6_线下单维辟谣干预T60_30seed均值",
        "cn": "线下单维辟谣干预 T=60",
        "en": "Offline single-track rumor-refutation intervention, T=60",
        "params": {"interventionStartTime": "60", "enableOnlineIntervention": "false", "enableOfflineIntervention": "true"},
        "states": ["S", "E", "I1", "I2", "G2", "R"],
    },
    {
        "figure": "5.3.7",
        "stem": "图5-3-7_线上单维辟谣干预T15_30seed均值",
        "cn": "线上单维辟谣干预 T=15",
        "en": "Online single-track rumor-refutation intervention, T=15",
        "params": {"interventionStartTime": "15", "enableOnlineIntervention": "true", "enableOfflineIntervention": "false"},
        "states": ["S", "E", "I1", "I2", "G1", "R"],
    },
    {
        "figure": "5.3.8",
        "stem": "图5-3-8_线上单维辟谣干预T30_30seed均值",
        "cn": "线上单维辟谣干预 T=30",
        "en": "Online single-track rumor-refutation intervention, T=30",
        "params": {"interventionStartTime": "30", "enableOnlineIntervention": "true", "enableOfflineIntervention": "false"},
        "states": ["S", "E", "I1", "I2", "G1", "R"],
    },
    {
        "figure": "5.3.9",
        "stem": "图5-3-9_线上单维辟谣干预T60_30seed均值",
        "cn": "线上单维辟谣干预 T=60",
        "en": "Online single-track rumor-refutation intervention, T=60",
        "params": {"interventionStartTime": "60", "enableOnlineIntervention": "true", "enableOfflineIntervention": "false"},
        "states": ["S", "E", "I1", "I2", "G1", "R"],
    },
]


STATE_LABELS = {
    "S": "S 未知者",
    "E": "E 潜伏者",
    "I1": "I1 线上传播者",
    "I2": "I2 线下传播者",
    "G1": "G1 线上辟谣干预状态",
    "G2": "G2 线下辟谣干预状态",
    "R": "R 免疫者",
}

STATE_COLORS = {
    "S": "#4D4D4D",
    "E": "#0072B2",
    "I1": "#D55E00",
    "I2": "#CC79A7",
    "G1": "#009E73",
    "G2": "#56B4E9",
    "R": "#E69F00",
}

SCENARIO_FIELDS = [
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

BASELINE_VALUES = {
    "modelMode": "0",
    "kOffline": "4",
    "kOnline": "6",
    "pRewire": "0.1",
    "initialOnlineSeeds": "10",
    "initialOfflineSeeds": "10",
    "onlineRate": "35",
    "offlineRate": "5",
    "onlineGovEffect": "0.05",
    "offlineGovEffect": "0.15",
    "latentTime": "2",
    "forgetTime": "30",
    "govForgetTime": "4",
}


def norm(value: Any) -> str:
    text = str(value).strip()
    if text.lower() in {"true", "false"}:
        return text.lower()
    try:
        return f"{float(text):.8f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def load_summary() -> pd.DataFrame:
    df = pd.read_csv(SUMMARY, dtype=str).fillna("")
    df = df[df["usedForScenarioStats"].str.lower() == "true"].copy()
    for field in SCENARIO_FIELDS:
        df[f"_{field}"] = df[field].map(norm)
    return df


def matching_runs(summary: pd.DataFrame, params: dict[str, str]) -> pd.DataFrame:
    merged = dict(BASELINE_VALUES)
    merged.update(params)
    mask = pd.Series(True, index=summary.index)
    for field, value in merged.items():
        mask &= summary[f"_{field}"] == norm(value)
    runs = summary[mask].copy()
    if len(runs) != 30:
        raise SystemExit(f"expected 30 used runs for {params}, got {len(runs)}")
    return runs


def load_mean_timeseries(runs: pd.DataFrame, states: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for _, row in runs.iterrows():
        raw_path = RAW_DIR / row["rawFile"]
        df = pd.read_csv(raw_path, usecols=["time", *states])
        df["seedId"] = row["seedId"]
        frames.append(df)
    long = pd.concat(frames, ignore_index=True)
    mean = long.groupby("time", as_index=False)[states].mean()
    return mean.sort_values("time")


def style_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Songti SC",
                "STSong",
                "Heiti SC",
                "Arial Unicode MS",
                "DejaVu Sans",
            ],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "legend.frameon": False,
        }
    )


def plot_scenario(scenario: dict[str, Any], runs: pd.DataFrame, mean: pd.DataFrame) -> tuple[Path, dict[str, Any]]:
    states = scenario["states"]
    fig, ax = plt.subplots(figsize=(6.6, 4.4), constrained_layout=False)
    for state in states:
        ax.plot(
            mean["time"],
            mean[state],
            label=STATE_LABELS[state],
            linewidth=1.8,
            color=STATE_COLORS[state],
        )

    ax.set_xlim(0, 180)
    ax.set_xlabel("时间 / h")
    ax.set_ylabel("人数")
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.7)
    handles, labels = ax.get_legend_handles_labels()
    fig.suptitle(
        f"{scenario['cn']}（30 seed 均值曲线）",
        x=0.105,
        y=0.98,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.56, 0.93), ncol=3, fontsize=8)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.13, top=0.76)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUT_DIR / f"{scenario['stem']}.png"
    svg = OUT_DIR / f"{scenario['stem']}.svg"
    fig.savefig(png, dpi=600, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)

    metrics = {
        "figure": scenario["figure"],
        "scenario": scenario["cn"],
        "n": len(runs),
        "I1_peak_mean": f"{runs['I1Peak'].astype(float).mean():.2f}",
        "I2_peak_mean": f"{runs['I2Peak'].astype(float).mean():.2f}",
        "total_peak_mean": f"{runs['totalInfectedPeak'].astype(float).mean():.2f}",
        "cumulative_mean": f"{runs['cumulativeInfectedPersonHours_right'].astype(float).mean():.2f}",
        "png": str(png.relative_to(ROOT)),
        "svg": str(svg.relative_to(ROOT)),
    }
    return png, metrics


def write_stats(rows: list[dict[str, Any]]) -> None:
    fields = ["figure", "scenario", "n", "I1_peak_mean", "I2_peak_mean", "total_peak_mean", "cumulative_mean", "png", "svg"]
    csv_path = OUT_DIR / "第五章九情景图_30seed统计.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    md = OUT_DIR / "第五章九情景图_30seed统计.md"
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    style_matplotlib()
    summary = load_summary()
    rows: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        runs = matching_runs(summary, scenario["params"])
        mean = load_mean_timeseries(runs, scenario["states"])
        _, metrics = plot_scenario(scenario, runs, mean)
        rows.append(metrics)
    write_stats(rows)
    print(f"wrote {len(rows)} figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
