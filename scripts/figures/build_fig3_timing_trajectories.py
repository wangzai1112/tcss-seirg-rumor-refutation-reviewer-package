from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "anylogic_outputs"
SUMMARY = ROOT / "data" / "processed" / "simulation" / "summary_from_raw.csv"
FIG_DIR = ROOT / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


SCENARIOS = [
    ("No intervention", 30.0, False, False, "#4B5563", "-"),
    ("Dual T=15", 15.0, True, True, "#2563EB", "-"),
    ("Dual T=30", 30.0, True, True, "#D97706", "-"),
    ("Dual T=60", 60.0, True, True, "#059669", "-"),
]


def selected_runs(summary: pd.DataFrame, tg: float, online: bool, offline: bool) -> pd.DataFrame:
    mask = (
        (summary["modelMode"] == 0)
        & (summary["interventionStartTime"].astype(float) == tg)
        & (summary["enableOnlineIntervention"].astype(bool) == online)
        & (summary["enableOfflineIntervention"].astype(bool) == offline)
        & (summary["kOnline"] == 6)
        & (summary["kOffline"] == 4)
        & (summary["pRewire"].round(3) == 0.1)
        & (summary["initialOnlineSeeds"] == 10)
        & (summary["initialOfflineSeeds"] == 10)
        & (summary["onlineRate"].round(3) == 35.0)
        & (summary["offlineRate"].round(3) == 5.0)
        & (summary["onlineGovEffect"].round(3) == 0.05)
        & (summary["offlineGovEffect"].round(3) == 0.15)
        & (summary["latentTime"].round(3) == 2.0)
        & (summary["forgetTime"].round(3) == 30.0)
        & (summary["govForgetTime"].round(3) == 4.0)
        & (summary["usedForScenarioStats"].astype(bool))
        & (summary["runCompleted"].astype(bool))
    )
    runs = summary.loc[mask, ["rawFile", "seedId"]].drop_duplicates("seedId")
    if len(runs) != 30:
        raise RuntimeError(
            f"Expected 30 selected runs for Tg={tg}, online={online}, "
            f"offline={offline}; found {len(runs)}."
        )
    return runs


def scenario_timeseries(runs: pd.DataFrame, label: str) -> pd.DataFrame:
    pieces = []
    for _, row in runs.iterrows():
        path = RAW_DIR / row["rawFile"]
        df = pd.read_csv(path, encoding="utf-8-sig")
        keep = df[["time", "I1", "I2"]].copy()
        keep["active_spreaders"] = keep["I1"] + keep["I2"]
        keep["seedId"] = int(row["seedId"])
        keep["scenario"] = label
        pieces.append(keep[["scenario", "seedId", "time", "active_spreaders"]])
    all_runs = pd.concat(pieces, ignore_index=True)
    return (
        all_runs.groupby(["scenario", "time"], as_index=False)
        .agg(
            mean_active=("active_spreaders", "mean"),
            sd_active=("active_spreaders", "std"),
            n=("seedId", "nunique"),
        )
        .sort_values(["scenario", "time"])
    )


def main() -> None:
    summary = pd.read_csv(SUMMARY, encoding="utf-8-sig")
    outputs = []
    for label, tg, online, offline, _, _ in SCENARIOS:
        outputs.append(scenario_timeseries(selected_runs(summary, tg, online, offline), label))
    plot_df = pd.concat(outputs, ignore_index=True)
    plot_df.to_csv(FIG_DIR / "source_data_fig3_timing_trajectories.csv", index=False)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.4,
            "axes.titlesize": 7.6,
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.6,
            "legend.fontsize": 6.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.7,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 300,
        }
    )

    fig, ax = plt.subplots(figsize=(3.42, 2.12))
    for label, tg, _, _, color, linestyle in SCENARIOS:
        d = plot_df[plot_df["scenario"] == label]
        ax.plot(
            d["time"],
            d["mean_active"],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=1.55 if label == "No intervention" else 1.35,
        )
        if label != "No intervention":
            ax.axvline(tg, color=color, linewidth=0.65, linestyle=(0, (3, 2)), alpha=0.55)

    ax.set_xlim(0, 180)
    ax.set_ylim(0, None)
    ax.set_xlabel("Simulation time (h)")
    ax.set_ylabel(r"Mean active spreaders ($I_1+I_2$)")
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.5)
    ax.legend(loc="upper right", ncol=1, handlelength=1.7, borderaxespad=0.2)
    ax.text(16, ax.get_ylim()[1] * 0.92, r"$T_g$", fontsize=6.4, color="#6B7280")
    fig.tight_layout(pad=0.25)
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"fig3_timing_trajectories.{ext}", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
