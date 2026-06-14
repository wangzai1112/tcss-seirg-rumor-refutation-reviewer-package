#!/usr/bin/env python3
"""Create SCI v3 global sensitivity designs for AnyLogic reruns.

The design is split into:
- Morris screening: broad, cheaper screening of many parameters.
- LHS confirmation: denser sampling for robustness checks after screening.

The CSVs use the same parameter column names as the existing AnyLogic queue so
they can be adapted into the GUI runner once the modelMode metadata is added.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path


def find_package_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "results").exists() and (parent / "docs").exists():
            return parent
    return Path(__file__).resolve().parents[2]


ROOT = find_package_root()
OUT_DIR = ROOT / "results" / "designs"
SPACE_CSV = OUT_DIR / "global_sensitivity_parameter_space_v3.csv"
MORRIS_CSV = OUT_DIR / "morris_design_v3.csv"
LHS_CSV = OUT_DIR / "lhs_design_v3.csv"
PROTOCOL_MD = OUT_DIR / "global_sensitivity_protocol_v3.md"

RNG = random.Random(20260613)
SEEDS = [1, 7, 13, 19, 25]

PARAMETERS = [
    ("onlineRate", 20.0, 50.0, "线上传播速率"),
    ("offlineRate", 2.0, 10.0, "线下传播速率"),
    ("onlineGovEffect", 0.02, 0.12, "线上辟谣干预强度"),
    ("offlineGovEffect", 0.05, 0.35, "线下辟谣干预强度"),
    ("latentTime", 1.0, 5.0, "潜伏时间"),
    ("forgetTime", 3.0, 20.0, "传播者退出/遗忘时间"),
    ("govForgetTime", 1.5, 8.0, "辟谣干预状态退出时间"),
    ("pRewire", 0.01, 0.30, "网络重连概率"),
    ("kOnline", 4.0, 10.0, "线上平均接触度"),
    ("kOffline", 2.0, 8.0, "线下平均接触度"),
    ("interventionStartTime", 10.0, 60.0, "干预启动时刻"),
]

DEFAULTS = {
    "priority": "S",
    "scenarioGroup": "SCI_v3_global_sensitivity",
    "enableOnlineIntervention": "true",
    "enableOfflineIntervention": "true",
    "initialOnlineSeeds": "10",
    "initialOfflineSeeds": "10",
    "expectedFinalTime": "180",
    "paperUse": "SCI v3 全局敏感性分析",
    "notes": "modelMode=0 完整耦合 SEIRG 模型；用于验证结论对参数扰动的稳健性。",
    "batchId": "SCI_V3_GLOBAL_SENSITIVITY_20260613",
    "modelMode": "0",
    "modelModeName": "coupled_seirg_full",
    "baselineFamily": "full_model",
    "requiresModelModeSupport": "false",
    "analysisRole": "global_sensitivity",
}


def scale(name: str, unit_value: float) -> float:
    low, high = next((lo, hi) for p, lo, hi, _desc in PARAMETERS if p == name)
    value = low + unit_value * (high - low)
    if name in {"kOnline", "kOffline", "interventionStartTime"}:
        return round(value)
    return round(value, 4)


def row_from_unit_values(design: str, sample_id: str, seed: int, unit_values: dict[str, float]) -> dict[str, str]:
    row = dict(DEFAULTS)
    row["queueId"] = f"{design}-{sample_id}-seed{seed:02d}"
    row["scenarioId"] = f"{design}_{sample_id}"
    row["scenarioName"] = f"{design} 参数样本 {sample_id}"
    row["seedId"] = str(seed)
    row["sensitivityDesign"] = design
    row["sensitivitySampleId"] = sample_id
    row["sensitivitySeedReplicate"] = str(seed)
    for name, _low, _high, _desc in PARAMETERS:
        row[name] = str(scale(name, unit_values[name]))
    return row


def latin_hypercube(n: int) -> list[dict[str, float]]:
    columns: dict[str, list[float]] = {}
    for name, _low, _high, _desc in PARAMETERS:
        values = [(i + RNG.random()) / n for i in range(n)]
        RNG.shuffle(values)
        columns[name] = values
    return [{name: columns[name][i] for name, *_ in PARAMETERS} for i in range(n)]


def morris_design(trajectories: int = 20, levels: int = 6) -> list[dict[str, float]]:
    delta = levels / (2.0 * (levels - 1.0))
    grid = [i / (levels - 1.0) for i in range(levels)]
    rows: list[dict[str, float]] = []
    for _trajectory in range(trajectories):
        current = {
            name: RNG.choice([g for g in grid if g <= 1.0 - delta])
            for name, *_ in PARAMETERS
        }
        rows.append(dict(current))
        order = [name for name, *_ in PARAMETERS]
        RNG.shuffle(order)
        for name in order:
            current[name] = min(1.0, current[name] + delta)
            rows.append(dict(current))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with SPACE_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["parameter", "low", "high", "description", "default_or_current_reference"])
        for name, low, high, desc in PARAMETERS:
            writer.writerow([name, low, high, desc, DEFAULTS.get(name, "")])

    morris_rows: list[dict[str, str]] = []
    for idx, unit_values in enumerate(morris_design(), start=1):
        sample_id = f"M{idx:03d}"
        for seed in SEEDS:
            morris_rows.append(row_from_unit_values("MORRIS", sample_id, seed, unit_values))
    write_csv(MORRIS_CSV, morris_rows)

    lhs_rows: list[dict[str, str]] = []
    for idx, unit_values in enumerate(latin_hypercube(160), start=1):
        sample_id = f"L{idx:03d}"
        for seed in SEEDS:
            lhs_rows.append(row_from_unit_values("LHS", sample_id, seed, unit_values))
    write_csv(LHS_CSV, lhs_rows)

    protocol = f"""# SCI v3 全局敏感性方案

## 目的

该部分用于回答审稿人最常问的问题：第五章的结论是否只是某几组参数设定下的偶然结果。建议先跑 Morris 筛选，再跑 LHS 确认；如果计算资源充足，再把 Morris 排名前 5-6 个参数转入 Sobol 方差分解。

## 参数范围

参数范围见 `{SPACE_CSV.name}`。范围没有直接声称为真实政策区间，只作为模型参数稳健性检验的扰动区间。论文中应写明：敏感性分析检验的是模型结论在合理参数扰动下是否保持方向一致，而不是估计现实政策的精确因果效应。

## 设计文件

- `{MORRIS_CSV.name}`：Morris 筛选，{len(morris_rows)} 条 AnyLogic 运行记录。
- `{LHS_CSV.name}`：LHS 确认，{len(lhs_rows)} 条 AnyLogic 运行记录。

每个参数样本使用 {len(SEEDS)} 个随机种子：{', '.join(map(str, SEEDS))}。如果今晚机器时间不够，优先跑 Morris；LHS 可以在明天继续。

## 论文使用指标

主指标：

- 总传播者峰值
- 累计传播者人时
- 线上传播者峰值
- 线下传播者峰值

辅助指标：

- G1/G2 峰值
- 达峰时间
- 最终 R

## 分析口径

1. Morris 输出每个参数的平均绝对初等效应和效应标准差，用来判断“影响强弱”和“是否存在交互/非线性”。
2. LHS 输出参数-结果的秩相关、随机森林/线性模型重要性或偏相关，用来验证 Morris 排名是否稳定。
3. 如果 Morris 与 LHS 都显示干预启动时刻、传播速率和退出时间处在前列，论文可以更稳妥地说：模型结论主要由传播-退出-干预时机的共同作用决定，而不是单一参数预设。
4. 不要把敏感性结果写成现实政策因果估计。应写成“模型稳健性证据”。
"""
    PROTOCOL_MD.write_text(protocol, encoding="utf-8")

    print(f"Wrote {SPACE_CSV}")
    print(f"Wrote {MORRIS_CSV} ({len(morris_rows)} rows)")
    print(f"Wrote {LHS_CSV} ({len(lhs_rows)} rows)")
    print(f"Wrote {PROTOCOL_MD}")


if __name__ == "__main__":
    main()
