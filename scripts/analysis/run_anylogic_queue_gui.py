from __future__ import annotations

import argparse
import csv
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "SCI一区升级规划" / "待跑实验队列.csv"
DATA_DIR = ROOT / "AnyLogic输出数据"
APPLY_SCRIPT = ROOT / "scripts" / "apply_anylogic_queue_row.py"
AX_PRESS = ROOT / "scripts" / "gui_tools" / "ax_press"
ANYLOGIC_BUNDLE_ID = "com.anylogic.AnyLogic"

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
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
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


def load_queue(path: Path = QUEUE) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    return {row["queueId"]: row for row in rows if row.get("queueId")}


def row_matches(parameter_row: dict[str, str], queue_row: dict[str, str]) -> bool:
    for field in MATCH_FIELDS:
        if field not in queue_row or queue_row.get(field, "") == "":
            continue
        if field not in parameter_row or parameter_row.get(field, "") == "":
            if field == "modelMode" and norm(queue_row.get(field, "")) == "0":
                continue
            return False
        if norm(parameter_row.get(field, "")) != norm(queue_row.get(field, "")):
            return False
    return True


def accept_external_change_prompt() -> None:
    script = r'''
tell application "AnyLogic" to activate
delay 0.5
tell application "System Events"
  tell process "AnyLogic"
    repeat 20 times
      if exists window "模型改变了" then
        click button "是(Y)" of window "模型改变了"
        exit repeat
      end if
      delay 0.2
    end repeat
  end tell
end tell
'''
    subprocess.run(["osascript"], input=script, text=True, check=True)


def trigger_anylogic_run(force_build: bool = False) -> None:
    accept_external_change_prompt()
    if not force_build:
        time.sleep(0.4)
        press_run_shortcut()
        return

    if AX_PRESS.exists():
        try:
            press_anylogic_button("构建模型", attempts=1, timeout=6.0)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        time.sleep(1.5)
        press_run_shortcut()
        return

    script = r'''
tell application "AnyLogic" to activate
delay 4
tell application "System Events"
  key code 98
  delay 1.5
  key code 96
end tell
'''
    subprocess.run(["osascript"], input=script, text=True, check=True)


def press_run_shortcut() -> None:
    script = r'''
tell application "AnyLogic" to activate
delay 0.2
tell application "System Events"
  key code 96
end tell
'''
    subprocess.run(["osascript"], input=script, text=True, check=True)


def press_anylogic_button(title_substring: str, attempts: int = 3, timeout: float = 10.0) -> None:
    last_error: subprocess.CalledProcessError | subprocess.TimeoutExpired | None = None
    for attempt in range(1, attempts + 1):
        try:
            subprocess.run(
                [str(AX_PRESS), ANYLOGIC_BUNDLE_ID, "press", title_substring],
                cwd=ROOT,
                check=True,
                timeout=timeout,
            )
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            last_error = error
            if attempt < attempts:
                accept_external_change_prompt()
                time.sleep(1.0)
    if last_error is not None:
        raise last_error


def find_matching_run(queue_row: dict[str, str], started_at: float) -> tuple[Path, Path, Path] | None:
    parameter_files = sorted(DATA_DIR.glob("parameter_master_*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    for parameter_file in parameter_files:
        if parameter_file.stat().st_mtime + 1 < started_at:
            continue
        for row in read_csv(parameter_file):
            if not row_matches(row, queue_row):
                continue
            run_id = row.get("runId", "")
            raw = DATA_DIR / f"raw_timeseries_{run_id}.csv"
            summary = DATA_DIR / f"summary_metrics_{run_id}.csv"
            if raw.exists() and summary.exists():
                return parameter_file, raw, summary
    return None


def find_matching_raw(queue_row: dict[str, str], started_at: float) -> Path | None:
    parameter_files = sorted(DATA_DIR.glob("parameter_master_*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    for parameter_file in parameter_files:
        if parameter_file.stat().st_mtime + 1 < started_at:
            continue
        for row in read_csv(parameter_file):
            if not row_matches(row, queue_row):
                continue
            run_id = row.get("runId", "")
            raw = DATA_DIR / f"raw_timeseries_{run_id}.csv"
            if raw.exists():
                return raw
    return None


def run_complete(raw: Path, summary: Path, expected_final_time: float) -> bool:
    raw_rows = read_csv(raw)
    summary_rows = read_csv(summary)
    if not raw_rows or not summary_rows:
        return False
    max_time = max(float(row.get("time", "0") or 0) for row in raw_rows)
    return max_time >= expected_final_time - 1e-9


def run_queue_id(
    queue_id: str,
    queue_row: dict[str, str],
    timeout: float,
    queue_path: Path,
    no_backup: bool = False,
    quiet_apply: bool = False,
) -> tuple[bool, str]:
    started_at = time.time()
    apply_cmd = ["python3", str(APPLY_SCRIPT), queue_id, "--queue", str(queue_path)]
    if no_backup:
        apply_cmd.append("--no-backup")
    if quiet_apply:
        subprocess.run(apply_cmd, cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    else:
        subprocess.run(apply_cmd, cwd=ROOT, check=True)
    trigger_anylogic_run(force_build=True)

    expected_final_time = float(queue_row.get("expectedFinalTime") or 180)
    deadline = time.time() + timeout
    last_seen = ""
    retried = False
    while time.time() < deadline:
        match = find_matching_run(queue_row, started_at)
        if match:
            _, raw, summary = match
            last_seen = raw.name
            if run_complete(raw, summary, expected_final_time):
                return True, raw.name
        raw = find_matching_raw(queue_row, started_at)
        if raw:
            last_seen = raw.name
        elif not retried and time.time() - started_at > 12:
            trigger_anylogic_run(force_build=True)
            retried = True
        time.sleep(1)
    return False, last_seen or "no matching output"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run selected AnyLogic queue rows through the local GUI.")
    parser.add_argument("queue_ids", nargs="+", help="Queue IDs such as E0-3-seed01")
    parser.add_argument("--queue", type=Path, default=QUEUE, help="Queue CSV path")
    parser.add_argument("--timeout", type=float, default=60.0, help="Seconds to wait for each completed CSV run")
    parser.add_argument("--no-parameter-backups", action="store_true", help="Do not create an ALP backup before each queue row")
    parser.add_argument("--quiet-apply", action="store_true", help="Suppress verbose parameter-diff output from apply_anylogic_queue_row.py")
    args = parser.parse_args()

    queue = load_queue(args.queue)
    for queue_id in args.queue_ids:
        if queue_id not in queue:
            raise SystemExit(f"Unknown queueId: {queue_id}")
        ok, detail = run_queue_id(
            queue_id,
            queue[queue_id],
            args.timeout,
            args.queue,
            args.no_parameter_backups,
            args.quiet_apply,
        )
        status = "completed" if ok else "timeout"
        print(f"{queue_id}: {status} - {detail}", flush=True)
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
