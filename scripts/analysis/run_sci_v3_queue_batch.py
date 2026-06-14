#!/usr/bin/env python3
"""Robust unattended runner for the SCI v3 AnyLogic queue."""

from __future__ import annotations

import argparse
import csv
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "SCI一区升级规划" / "全量重跑实验队列_SCI_v3.csv"
DATA_DIR = ROOT / "AnyLogic输出数据"
RUN_SCRIPT = ROOT / "scripts" / "run_anylogic_queue_gui.py"
LOG_DIR = ROOT / "SCI一区升级规划" / "运行日志"

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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def norm(value: Any) -> str:
    text = str(value).strip()
    lower = text.lower()
    if lower in {"true", "false"}:
        return lower
    try:
        number = float(text)
    except ValueError:
        return text
    return f"{number:.8f}".rstrip("0").rstrip(".")


def row_matches(parameter_row: dict[str, str], queue_row: dict[str, str]) -> bool:
    for field in MATCH_FIELDS:
        if field not in queue_row or queue_row.get(field, "") == "":
            continue
        if field == "modelMode" and parameter_row.get(field, "").strip() == "":
            parameter_value = "0"
        else:
            parameter_value = parameter_row.get(field, "")
        if field not in parameter_row or parameter_row.get(field, "") == "":
            if field != "modelMode":
                return False
        if norm(parameter_value) != norm(queue_row.get(field, "")):
            return False
    return True


def completed_queue_ids(rows: list[dict[str, str]]) -> set[str]:
    done: set[str] = set()
    candidates = {row.get("queueId", ""): row for row in rows}
    parameter_files = sorted(DATA_DIR.glob("parameter_master_M*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    for parameter_file in parameter_files:
        for parameter_row in read_csv(parameter_file):
            for queue_id, queue_row in candidates.items():
                if queue_id in done:
                    continue
                if row_matches(parameter_row, queue_row):
                    run_id = parameter_row.get("runId", "")
                    raw = DATA_DIR / f"raw_timeseries_{run_id}.csv"
                    summary = DATA_DIR / f"summary_metrics_{run_id}.csv"
                    if raw.exists() and summary.exists():
                        done.add(queue_id)
    return done


def select_rows(rows: list[dict[str, str]], include_baselines: bool, only_missing: bool, limit: int | None) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if include_baselines or str(row.get("requiresModelModeSupport", "")).lower() != "true"
    ]
    if only_missing:
        done = completed_queue_ids(selected)
        selected = [row for row in selected if row.get("queueId") not in done]
    if limit is not None:
        selected = selected[:limit]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SCI v3 AnyLogic queue rows unattended.")
    parser.add_argument("--queue", type=Path, default=QUEUE)
    parser.add_argument("--include-baselines", action="store_true", help="Also run modelMode>0 baseline rows")
    parser.add_argument("--all", action="store_true", help="Run even rows that already have matching M* outputs")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-failures", type=int, default=5)
    args = parser.parse_args()

    rows = read_csv(args.queue)
    selected = select_rows(rows, args.include_baselines, not args.all, args.limit)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"sci_v3_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    failures = 0

    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"queue={args.queue}\nselected={len(selected)}\n")
        log.flush()
        print(f"log: {log_path}", flush=True)
        print(f"selected: {len(selected)}", flush=True)
        for index, row in enumerate(selected, start=1):
            queue_id = row["queueId"]
            cmd = [
                "python3",
                str(RUN_SCRIPT),
                queue_id,
                "--queue",
                str(args.queue),
                "--timeout",
                str(args.timeout),
                "--quiet-apply",
                "--no-parameter-backups",
            ]
            print(f"[{index}/{len(selected)}] {queue_id}", flush=True)
            log.write(f"\n[{index}/{len(selected)}] {queue_id}\n")
            log.flush()
            proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log.write(proc.stdout)
            log.flush()
            print(proc.stdout.strip(), flush=True)
            if proc.returncode != 0:
                failures += 1
                log.write(f"FAILED returncode={proc.returncode}\n")
                log.flush()
                if failures >= args.max_failures:
                    raise SystemExit(f"Stopped after {failures} failures. See {log_path}")

    print(f"done with failures={failures}. log={log_path}")


if __name__ == "__main__":
    main()
