#!/usr/bin/env python3
"""Compact mean-field pathway allocation check for the SEIRG supplement.

This script is intentionally equation-level. It is not a replacement for the
30-seed AnyLogic ABM comparisons reported in the main manuscript. Its purpose is
to document equal-strength and budget-matched alpha allocations under the compact
SEIRG equations so the pathway-strength caveat can be inspected reproducibly.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "results" / "summary"
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Params:
    beta1: float = 0.055
    beta2: float = 0.040
    k1: float = 6.0
    k2: float = 4.0
    sigma: float = 0.20
    theta: float = 0.72
    gamma1: float = 0.11
    gamma2: float = 0.08
    mu1: float = 0.020
    mu2: float = 0.025
    rho: float = 0.25
    delta: float = 0.010
    alpha1: float = 0.0
    alpha2: float = 0.0
    tg: float = 30.0
    horizon: float = 180.0
    dt: float = 0.05


def rhs(y: tuple[float, float, float, float, float, float, float], t: float, p: Params):
    s, e, i1, i2, g1, g2, r = y
    h = 1.0 if t >= p.tg else 0.0
    lam = p.beta1 * p.k1 * i1 + p.beta2 * p.k2 * i2
    ds = -lam * s + p.delta * r
    de = lam * s - p.sigma * e
    di1 = p.theta * p.sigma * e - (p.gamma1 + h * p.alpha1 + p.mu1 * g1) * i1
    di2 = (1.0 - p.theta) * p.sigma * e - (p.gamma2 + h * p.alpha2 + p.mu2 * g2) * i2
    dg1 = h * p.alpha1 * i1 - p.rho * g1
    dg2 = h * p.alpha2 * i2 - p.rho * g2
    dr = (
        p.gamma1 * i1
        + p.gamma2 * i2
        + p.mu1 * g1 * i1
        + p.mu2 * g2 * i2
        + p.rho * g1
        + p.rho * g2
        - p.delta * r
    )
    return ds, de, di1, di2, dg1, dg2, dr


def add_scaled(y, dy, scale):
    return tuple(max(0.0, y_i + scale * dy_i) for y_i, dy_i in zip(y, dy))


def rk4_step(y, t, p: Params):
    dt = p.dt
    k1 = rhs(y, t, p)
    k2 = rhs(add_scaled(y, k1, dt / 2.0), t + dt / 2.0, p)
    k3 = rhs(add_scaled(y, k2, dt / 2.0), t + dt / 2.0, p)
    k4 = rhs(add_scaled(y, k3, dt), t + dt, p)
    y_next = tuple(
        max(0.0, y_i + dt * (a + 2.0 * b + 2.0 * c + d) / 6.0)
        for y_i, a, b, c, d in zip(y, k1, k2, k3, k4)
    )
    total = sum(y_next)
    return tuple(v / total for v in y_next)


def effective_re(y, p: Params) -> float:
    s, _e, _i1, _i2, g1, g2, _r = y
    exit1 = p.gamma1 + p.alpha1 + p.mu1 * g1
    exit2 = p.gamma2 + p.alpha2 + p.mu2 * g2
    return s * (p.theta * p.beta1 * p.k1 / exit1 + (1.0 - p.theta) * p.beta2 * p.k2 / exit2)


def simulate(p: Params):
    y = (0.98, 0.0, 0.01, 0.01, 0.0, 0.0, 0.0)
    t = 0.0
    peak = y[2] + y[3]
    peak_time = 0.0
    burden = 0.0
    y_tg = y
    while t < p.horizon - 1e-12:
        burden += (y[2] + y[3]) * p.dt
        if y[2] + y[3] > peak:
            peak = y[2] + y[3]
            peak_time = t
        if t <= p.tg < t + p.dt:
            y_tg = y
        y = rk4_step(y, t, p)
        t += p.dt
    return {
        "peak_i_total": peak,
        "peak_time_h": peak_time,
        "cumulative_i_person_time_norm": burden,
        "re_tg_directional": effective_re(y_tg, p),
    }


def fmt(x: float, n: int = 4) -> str:
    return f"{x:.{n}f}"


def main():
    base = Params()
    scenarios = [
        ("no_refutation_reference", 0.00, 0.00, "reference"),
        ("reported_unequal_dual_0p05_0p15", 0.05, 0.15, "reported unequal dual"),
        ("equal_weak_dual_0p05_0p05", 0.05, 0.05, "equal-strength dual"),
        ("equal_strong_dual_0p15_0p15", 0.15, 0.15, "equal-strength dual"),
        ("budget_online_only_0p20_0p00", 0.20, 0.00, "budget-matched online-only"),
        ("budget_dual_0p15_0p05", 0.15, 0.05, "budget-matched dual"),
        ("budget_equal_dual_0p10_0p10", 0.10, 0.10, "budget-matched dual"),
        ("budget_dual_0p05_0p15", 0.05, 0.15, "budget-matched dual"),
        ("budget_offline_only_0p00_0p20", 0.00, 0.20, "budget-matched offline-only"),
    ]
    rows = []
    baseline_metrics = None
    for name, a1, a2, family in scenarios:
        p = replace(base, alpha1=a1, alpha2=a2)
        metrics = simulate(p)
        if baseline_metrics is None:
            baseline_metrics = metrics
        peak_change = (
            (baseline_metrics["peak_i_total"] - metrics["peak_i_total"])
            / baseline_metrics["peak_i_total"]
            * 100.0
        )
        burden_change = (
            (
                baseline_metrics["cumulative_i_person_time_norm"]
                - metrics["cumulative_i_person_time_norm"]
            )
            / baseline_metrics["cumulative_i_person_time_norm"]
            * 100.0
        )
        rows.append(
            {
                "scenario": name,
                "family": family,
                "alpha1_online": fmt(a1, 2),
                "alpha2_offline": fmt(a2, 2),
                "alpha_budget_sum": fmt(a1 + a2, 2),
                "peak_i_total": fmt(metrics["peak_i_total"]),
                "peak_time_h": fmt(metrics["peak_time_h"], 2),
                "peak_change_pct_vs_reference": fmt(peak_change, 2),
                "cumulative_i_person_time_norm": fmt(metrics["cumulative_i_person_time_norm"]),
                "burden_change_pct_vs_reference": fmt(burden_change, 2),
                "re_tg_directional": fmt(metrics["re_tg_directional"]),
            }
        )

    csv_path = OUT_DIR / "mean_field_pathway_budget_check.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = OUT_DIR / "mean_field_pathway_budget_check.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Compact Mean-Field Equal-Strength and Budget-Matched Pathway Check\n\n")
        f.write(
            "This supplement is an equation-level directional check under the compact SEIRG "
            "mean-field equations. It is not a 30-seed AnyLogic ABM rerun and should not be "
            "used to replace the main pathway-strength scenario comparison in the manuscript.\n\n"
        )
        f.write(
            "The check keeps the same timing anchor (`Tg=30 h`) and compares equal-strength "
            "dual allocations plus budget-matched allocations with `alpha1 + alpha2 = 0.20`.\n\n"
        )
        f.write("| Scenario | alpha1 | alpha2 | Budget | Peak | Peak change (%) | Burden | Burden change (%) | RE(Tg) |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            f.write(
                f"| {row['scenario']} | {row['alpha1_online']} | {row['alpha2_offline']} | "
                f"{row['alpha_budget_sum']} | {row['peak_i_total']} | "
                f"{row['peak_change_pct_vs_reference']} | "
                f"{row['cumulative_i_person_time_norm']} | "
                f"{row['burden_change_pct_vs_reference']} | {row['re_tg_directional']} |\n"
            )
        f.write(
            "\nInterpretation boundary: these deterministic mean-field results only test the "
            "direction of allocation effects in the compact equations. A submission-ready "
            "pathway ranking should be based on equal-strength or budget-matched ABM reruns "
            "under the documented AnyLogic statechart.\n"
        )

    print(csv_path)
    print(md_path)


if __name__ == "__main__":
    main()
