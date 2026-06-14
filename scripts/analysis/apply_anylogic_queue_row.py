from __future__ import annotations

import argparse
import csv
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALP = ROOT / "谣言传播模型_SCI补实验版.alp"
QUEUE = ROOT / "SCI一区升级规划" / "待跑实验队列.csv"
BACKUP_DIR = ROOT / "工程备份"

QUEUE_TO_ALP = {
    "modelMode": "modelMode",
    "seedId": "seedId",
    "interventionStartTime": "interventionStartTime",
    "enableOnlineIntervention": "enableOnlineIntervention",
    "enableOfflineIntervention": "enableOfflineIntervention",
    "kOffline": "kOffline",
    "kOnline": "kOnline",
    "pRewire": "pRewire",
    "initialOnlineSeeds": "initialOnlineSeeds",
    "initialOfflineSeeds": "initialOfflineSeeds",
    "onlineRate": "线上传播速率",
    "offlineRate": "线下传播速率",
    "onlineGovEffect": "线上辟谣影响系数",
    "offlineGovEffect": "线下辟谣影响系数",
    "latentTime": "潜伏时间",
    "forgetTime": "遗忘时间",
    "govForgetTime": "辟谣者遗忘时间",
}


def read_queue(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def find_row(rows: list[dict[str, str]], queue_id: str) -> dict[str, str]:
    for row in rows:
        if row.get("queueId") == queue_id:
            return row
    raise SystemExit(f"queueId not found: {queue_id}")


def normalize_value(value: str) -> str:
    value = str(value).strip()
    if value.lower() in {"true", "false"}:
        return value.lower()
    return value


def update_parameter_default(text: str, parameter_name: str, value: str) -> tuple[str, str]:
    name_re = re.escape(f"<Name><![CDATA[{parameter_name}]]></Name>")
    pattern = re.compile(
        rf"(?P<head><Variable Class=\"Parameter\">(?:(?!<Variable Class=\"Parameter\">).)*?{name_re}"
        rf"(?:(?!<Variable Class=\"Parameter\">).)*?<DefaultValue Class=\"CodeValue\">\s*<Code><!\[CDATA\[)"
        rf"(?P<old>.*?)"
        rf"(?P<tail>\]\]></Code>)",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"parameter default not found in ALP: {parameter_name}")
    old = match.group("old")
    new_text = text[: match.start("old")] + value + text[match.end("old") :]
    return new_text, old


def build_updates(row: dict[str, str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for queue_key, alp_name in QUEUE_TO_ALP.items():
        if queue_key in row and row[queue_key] != "":
            updates[alp_name] = normalize_value(row[queue_key])
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply one experiment-queue row to AnyLogic parameter defaults.")
    parser.add_argument("queue_id", help="queueId from SCI一区升级规划/待跑实验队列.csv, e.g. E0-2-seed01")
    parser.add_argument("--alp", type=Path, default=ALP)
    parser.add_argument("--queue", type=Path, default=QUEUE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    row = find_row(read_queue(args.queue), args.queue_id)
    updates = build_updates(row)
    text = args.alp.read_text(encoding="utf-8")
    old_values: dict[str, Any] = {}
    new_text = text
    for parameter_name, value in updates.items():
        try:
            new_text, old = update_parameter_default(new_text, parameter_name, value)
        except SystemExit:
            if parameter_name == "modelMode" and value in {"", "0"}:
                continue
            raise
        old_values[parameter_name] = old

    print(f"queueId: {args.queue_id}")
    print(f"scenario: {row.get('scenarioId')} {row.get('scenarioName')}")
    for parameter_name, value in updates.items():
        if parameter_name in old_values:
            print(f"  {parameter_name}: {old_values[parameter_name]} -> {value}")
        else:
            print(f"  {parameter_name}: skipped -> {value}")

    if args.dry_run:
        print("dry-run: ALP not modified")
        return

    if not args.no_backup:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / f"谣言传播模型_SCI补实验版_队列参数切换前_{stamp}.alp"
        shutil.copy2(args.alp, backup)
        print(f"backup: {backup}")

    args.alp.write_text(new_text, encoding="utf-8")
    print(f"updated: {args.alp}")


if __name__ == "__main__":
    main()
