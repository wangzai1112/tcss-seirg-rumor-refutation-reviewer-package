#!/usr/bin/env python3
"""Lightweight mean-field SEIRG reference implementation.

This script is an equation-level reproducibility aid. It is not used to
produce the manuscript's AnyLogic agent-based simulation results. The goal is
to let reviewers inspect the direction of the SEIRG state flows, the timing
switch h(t; Tg), and the R0-style indicators with only the Python standard
library.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "results" / "summary"


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
    delta: float = 0.010
    alpha1: float = 0.050
    alpha2: float = 0.120
    mu1: float = 0.020
    mu2: float = 0.025
    rho: float = 0.006
    tg: float = 30.0
    dt: float = 0.05
    horizon: float = 120.0


def r0(p: Params) -> float:
    return p.theta * p.beta1 * p.k1 / p.gamma1 + (1.0 - p.theta) * p.beta2 * p.k2 / p.gamma2


def effective_indicator(p: Params, s_tg: float) -> float:
    exit1 = p.gamma1 + p.alpha1
    exit2 = p.gamma2 + p.alpha2
    return s_tg * (p.theta * p.beta1 * p.k1 / exit1 + (1.0 - p.theta) * p.beta2 * p.k2 / exit2)


def step(state: tuple[float, ...], t: float, p: Params) -> tuple[float, ...]:
    s, e, i1, i2, r, g1, g2 = state
    h = 1.0 if t >= p.tg else 0.0
    force = (p.beta1 * p.k1 * i1 + p.beta2 * p.k2 * i2) * s
    ref1 = h * p.alpha1 * i1
    ref2 = h * p.alpha2 * i2
    g_exit1 = p.mu1 * g1 * i1
    g_exit2 = p.mu2 * g2 * i2

    ds = -force + p.delta * r
    de = force - p.sigma * e
    di1 = p.theta * p.sigma * e - p.gamma1 * i1 - ref1 - g_exit1
    di2 = (1.0 - p.theta) * p.sigma * e - p.gamma2 * i2 - ref2 - g_exit2
    dg1 = ref1 - p.rho * g1
    dg2 = ref2 - p.rho * g2
    dr = p.gamma1 * i1 + p.gamma2 * i2 + g_exit1 + g_exit2 + p.rho * (g1 + g2) - p.delta * r

    raw = (
        s + p.dt * ds,
        e + p.dt * de,
        i1 + p.dt * di1,
        i2 + p.dt * di2,
        r + p.dt * dr,
        g1 + p.dt * dg1,
        g2 + p.dt * dg2,
    )
    clipped = tuple(max(0.0, x) for x in raw)
    total = sum(clipped)
    return tuple(x / total for x in clipped)


def simulate(p: Params) -> list[dict[str, float]]:
    state = (0.990, 0.008, 0.001, 0.001, 0.0, 0.0, 0.0)
    rows: list[dict[str, float]] = []
    n_steps = int(p.horizon / p.dt)
    for idx in range(n_steps + 1):
        t = idx * p.dt
        s, e, i1, i2, r, g1, g2 = state
        rows.append(
            {
                "t": t,
                "S": s,
                "E": e,
                "I1": i1,
                "I2": i2,
                "R": r,
                "G1": g1,
                "G2": g2,
                "I_total": i1 + i2,
                "G_total": g1 + g2,
                "h": 1.0 if t >= p.tg else 0.0,
            }
        )
        if idx < n_steps:
            state = step(state, t, p)
    return rows


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    p = Params()
    rows = simulate(p)
    s_tg = min(rows, key=lambda row: abs(row["t"] - p.tg))["S"]
    peak = max(rows, key=lambda row: row["I_total"])
    burden = sum(row["I_total"] * p.dt for row in rows)
    write_csv(OUT_DIR / "mean_field_reference_trace.csv", rows)
    write_csv(
        OUT_DIR / "mean_field_reference_summary.csv",
        [
            {
                "R0": r0(p),
                "RE_Tg": effective_indicator(p, s_tg),
                "Tg": p.tg,
                "S_Tg": s_tg,
                "peak_I_total": peak["I_total"],
                "peak_time": peak["t"],
                "cumulative_I_person_time": burden,
                "note": "Equation-level reference only; not used for manuscript AnyLogic results.",
            }
        ],
    )
    print("Wrote", OUT_DIR / "mean_field_reference_trace.csv")
    print("Wrote", OUT_DIR / "mean_field_reference_summary.csv")


if __name__ == "__main__":
    main()
