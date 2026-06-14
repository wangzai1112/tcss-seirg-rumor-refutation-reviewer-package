#!/usr/bin/env python3
"""Build the SCI v3 full-rerun queue.

This keeps the original master's-thesis experiment matrix as a reproducibility
rerun and appends three baseline families requested for SCI-level comparison.
The generated queue is intentionally conservative: it preserves all columns in
the existing AnyLogic runner queue and adds metadata columns used by later
analysis scripts.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "SCI一区升级规划"
SOURCE_QUEUE = PLAN_DIR / "待跑实验队列.csv"
OUT_QUEUE = PLAN_DIR / "全量重跑实验队列_SCI_v3.csv"
OUT_NOTE = PLAN_DIR / "全量重跑实验队列_SCI_v3_说明.md"

BATCH_ID = "SCI_V3_FULL_RERUN_20260613"
SEEDS = range(1, 31)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def base_from_existing(row: dict[str, str]) -> dict[str, str]:
    new_row = dict(row)
    new_row.update(
        {
            "queueId": f"V3-{row.get('queueId', '').strip()}",
            "batchId": BATCH_ID,
            "modelMode": "0",
            "modelModeName": "coupled_seirg_full",
            "baselineFamily": "full_model",
            "rerunScope": "master_thesis_full_rerun",
            "requiresModelModeSupport": "false",
            "analysisRole": "primary_reproduction",
            "plannedUse": "复现硕士论文既有场景，并作为 SCI v3 主模型比较基准。",
            "replacementForHistory": "true",
        }
    )
    return new_row


def baseline_template(
    family_code: str,
    family_name: str,
    mode: str,
    timing_label: str,
    start_time: int,
    intervention_on: bool,
) -> dict[str, str]:
    scenario_id = f"{family_code}_{timing_label}"
    if family_code == "B1":
        scenario_name = f"传统 SEIR {timing_label}"
        k_online, k_offline = "10", "0"
        online_rate, offline_rate = "35.0", "0.0"
        initial_online, initial_offline = "20", "0"
        p_rewire = "0.0"
    elif family_code == "B2":
        scenario_name = f"单层网络 SEIR {timing_label}"
        k_online, k_offline = "10", "0"
        online_rate, offline_rate = "35.0", "0.0"
        initial_online, initial_offline = "20", "0"
        p_rewire = "0.1"
    else:
        scenario_name = f"无 G 状态/无耦合模型 {timing_label}"
        k_online, k_offline = "6", "4"
        online_rate, offline_rate = "35.0", "5.0"
        initial_online, initial_offline = "10", "10"
        p_rewire = "0.1"

    return {
        "priority": "0",
        "scenarioGroup": "SCI_v3_baseline",
        "scenarioId": scenario_id,
        "scenarioName": scenario_name,
        "interventionStartTime": str(start_time),
        "enableOnlineIntervention": str(intervention_on).lower(),
        "enableOfflineIntervention": str(intervention_on).lower(),
        "kOffline": k_offline,
        "kOnline": k_online,
        "pRewire": p_rewire,
        "initialOnlineSeeds": initial_online,
        "initialOfflineSeeds": initial_offline,
        "onlineRate": online_rate,
        "offlineRate": offline_rate,
        "onlineGovEffect": "0.05",
        "offlineGovEffect": "0.15",
        "latentTime": "2.0",
        "forgetTime": "5.0",
        "govForgetTime": "3.0",
        "expectedFinalTime": "180",
        "paperUse": "SCI v3 基线比较",
        "notes": family_name,
        "batchId": BATCH_ID,
        "modelMode": mode,
        "modelModeName": family_name,
        "baselineFamily": family_code,
        "rerunScope": "new_sci_baseline",
        "requiresModelModeSupport": "true",
        "analysisRole": "baseline_comparison",
        "plannedUse": "与完整耦合 SEIRG 模型在同一指标体系下比较，检验新增结构是否真正贡献结果。",
        "replacementForHistory": "false",
    }


def make_baseline_rows() -> list[dict[str, str]]:
    families = [
        ("B1", "traditional_seir", "1"),
        ("B2", "single_layer_network_seir", "2"),
        ("B3", "no_g_no_coupling", "3"),
    ]
    timings = [
        ("T0_no_intervention", 30, False),
        ("T15_intervention", 15, True),
        ("T30_intervention", 30, True),
        ("T60_intervention", 60, True),
    ]
    rows: list[dict[str, str]] = []
    for family_code, family_name, mode in families:
        for timing_label, start_time, intervention_on in timings:
            template = baseline_template(
                family_code, family_name, mode, timing_label, start_time, intervention_on
            )
            for seed in SEEDS:
                row = dict(template)
                row["queueId"] = f"V3-{family_code}-{timing_label}-seed{seed:02d}"
                row["seedId"] = str(seed)
                rows.append(row)
    return rows


def main() -> None:
    old_rows = read_csv(SOURCE_QUEUE)
    rerun_rows = [base_from_existing(row) for row in old_rows]
    baseline_rows = make_baseline_rows()
    rows = rerun_rows + baseline_rows

    all_fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in all_fields:
                all_fields.append(key)

    write_csv(OUT_QUEUE, rows, all_fields)

    counts = Counter(row["rerunScope"] for row in rows)
    baseline_counts = Counter(row["baselineFamily"] for row in rows)
    note = f"""# SCI v3 全量重跑实验队列说明

生成时间：2026-06-13

## 队列定位

这份队列把原硕士论文已经设计的实验全部重新纳入同一批次，并新增三类基线模型。后续论文中的主结果、基线比较、统计检验和消融分析都应以 `batchId={BATCH_ID}` 的结果为准；原先结果只作为历史记录和交叉核查，不再直接作为最终 SCI 版的唯一证据。

## 规模

- 总行数：{len(rows)}
- 原硕士实验全量重跑：{counts.get('master_thesis_full_rerun', 0)}
- 新增 SCI 基线实验：{counts.get('new_sci_baseline', 0)}
- B1 传统 SEIR：{baseline_counts.get('B1', 0)}
- B2 单层网络 SEIR：{baseline_counts.get('B2', 0)}
- B3 无 G 状态/无耦合模型：{baseline_counts.get('B3', 0)}

## AnyLogic 需要先补的模型开关

新增基线行依赖 `modelMode` 参数：

- `0`：完整耦合 SEIRG 模型，复现原论文实验。
- `1`：传统 SEIR，仅保留总体 S-E-I-R 转移。
- `2`：单层网络 SEIR，保留网络接触但去掉线上/线下双层拆分。
- `3`：无 G 状态/无耦合模型，保留 I1/I2 双空间但禁用 G1/G2 和层间耦合。

在 AnyLogic 工程没有增加该参数前，只能先跑 `requiresModelModeSupport=false` 的旧实验重跑行；三类基线必须等模型结构开关补齐后再跑。

## 结果使用原则

1. 同一场景至少保留 30 个随机种子。
2. 统计表统一使用均值、SD、95% CI、Welch t、p 值、效应量和多重比较修正。
3. 主文只放关键比较，完整队列和逐 seed 结果放公开仓库。
4. 如果某个基线不能直接表达政府干预，只保留“参数等价的直接退出/免疫加速”版本，并在论文中明确边界。
"""
    OUT_NOTE.write_text(note, encoding="utf-8")
    print(f"Wrote {OUT_QUEUE} ({len(rows)} rows)")
    print(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
