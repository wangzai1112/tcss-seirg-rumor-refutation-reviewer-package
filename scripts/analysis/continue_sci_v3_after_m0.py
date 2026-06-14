from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "SCI一区升级规划"
QUEUE = PLAN_DIR / "全量重跑实验队列_SCI_v3.csv"
LOG_DIR = PLAN_DIR / "运行日志"
PUBLIC_DIR = PLAN_DIR / "public_release_template"
RENDER_SCRIPT = Path("/Users/hao/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py")
FINAL_DOCX = ROOT / "00_论文最终材料_2026-06-13" / "01_最终论文" / "硕士论文_SCI_v3完整基线回填版.docx"
FINAL_QA_DIR = ROOT / "00_论文最终材料_2026-06-13" / "04_格式审查" / "render_final_baseline"
FINAL_AUDIT_DIR = ROOT / "00_论文最终材料_2026-06-13" / "04_格式审查" / "完整基线回填版结构审查"
SMOKE_IDS = [
    "V3-B1-T0_no_intervention-seed01",
    "V3-B2-T0_no_intervention-seed01",
    "V3-B3-T0_no_intervention-seed01",
]


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd: list[str], log, check: bool = True) -> subprocess.CompletedProcess[str]:
    line = " ".join(cmd)
    print(f"[{timestamp()}] $ {line}", flush=True)
    log.write(f"\n[{timestamp()}] $ {line}\n")
    log.flush()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log.write(proc.stdout)
    log.flush()
    print(proc.stdout.strip(), flush=True)
    if check and proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {line}")
    return proc


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def norm(value: str) -> str:
    text = str(value).strip()
    if text.lower() in {"true", "false"}:
        return text.lower()
    try:
        number = float(text)
    except ValueError:
        return text
    return f"{number:.8f}".rstrip("0").rstrip(".")


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


def row_key(row: dict[str, str]) -> tuple[str, ...]:
    values: list[str] = []
    for field in MATCH_FIELDS:
        value = row.get(field, "")
        if field == "modelMode" and str(value).strip() == "":
            value = "0"
        values.append(norm(value))
    return tuple(values)


def completed_keys() -> set[tuple[str, ...]]:
    keys: set[tuple[str, ...]] = set()
    data_dir = ROOT / "AnyLogic输出数据"
    for parameter_file in data_dir.glob("parameter_master_M*.csv"):
        for row in read_csv(parameter_file):
            run_id = row.get("runId", "")
            if not run_id:
                continue
            raw = data_dir / f"raw_timeseries_{run_id}.csv"
            summary = data_dir / f"summary_metrics_{run_id}.csv"
            if raw.exists() and summary.exists():
                keys.add(row_key(row))
    return keys


def missing_counts() -> tuple[int, int]:
    rows = read_csv(QUEUE)
    done = completed_keys()
    m0_missing = 0
    all_missing = 0
    for row in rows:
        missing = row_key(row) not in done
        if not missing:
            continue
        all_missing += 1
        if str(row.get("requiresModelModeSupport", "")).strip().lower() != "true":
            m0_missing += 1
    return m0_missing, all_missing


def copy_public_outputs() -> None:
    files = [
        (PLAN_DIR / "实验结果汇总" / "summary_from_raw.csv", PUBLIC_DIR / "results" / "summary" / "summary_from_raw.csv"),
        (PLAN_DIR / "实验结果汇总" / "run_quality_audit.csv", PUBLIC_DIR / "results" / "summary" / "run_quality_audit.csv"),
        (PLAN_DIR / "统计检验_v3" / "complete_stat_tests_current.csv", PUBLIC_DIR / "results" / "tables" / "complete_stat_tests_current.csv"),
        (PLAN_DIR / "统计检验_v3" / "complete_stat_tests_current.md", PUBLIC_DIR / "results" / "tables" / "complete_stat_tests_current.md"),
        (ROOT / "谣言传播模型_SCI补实验版.alp", PUBLIC_DIR / "anylogic_model" / "rumor_model_sci_v3_current.alp"),
        (FINAL_DOCX, PUBLIC_DIR / "results" / "summary" / "硕士论文_SCI_v3完整基线回填版.docx"),
    ]
    for source, target in files:
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Continue SCI v3 workflow after the active M0 AnyLogic batch exits.")
    parser.add_argument("--wait-pid", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-failures", type=int, default=8)
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"sci_v3_after_m0_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with log_path.open("w", encoding="utf-8") as log:
        print(f"log: {log_path}", flush=True)
        log.write(f"wait_pid={args.wait_pid}\n")
        while process_exists(args.wait_pid):
            m0_missing, all_missing = missing_counts()
            msg = f"[{timestamp()}] waiting for M0 batch; m0_missing={m0_missing}; all_missing={all_missing}"
            print(msg, flush=True)
            log.write(msg + "\n")
            log.flush()
            time.sleep(60)

        m0_missing, all_missing = missing_counts()
        log.write(f"[{timestamp()}] initial wait finished; m0_missing={m0_missing}; all_missing={all_missing}\n")
        log.flush()

        if m0_missing:
            run([
                sys.executable,
                "scripts/run_sci_v3_queue_batch.py",
                "--timeout",
                str(args.timeout),
                "--max-failures",
                str(args.max_failures),
            ], log)

        run([sys.executable, "scripts/analyze_anylogic_outputs.py"], log)
        run([sys.executable, "scripts/build_complete_statistical_tests_v3.py"], log)

        run([sys.executable, "scripts/patch_anylogic_model_modes_v3.py", "--check"], log)
        run([sys.executable, "scripts/patch_anylogic_model_modes_v3.py"], log)

        for queue_id in SMOKE_IDS:
            run([
                sys.executable,
                "scripts/run_anylogic_queue_gui.py",
                queue_id,
                "--queue",
                str(QUEUE),
                "--timeout",
                str(args.timeout),
                "--quiet-apply",
                "--no-parameter-backups",
            ], log)

        run([
            sys.executable,
            "scripts/run_sci_v3_queue_batch.py",
            "--include-baselines",
            "--timeout",
            str(args.timeout),
            "--max-failures",
            str(args.max_failures),
        ], log)

        run([sys.executable, "scripts/analyze_anylogic_outputs.py"], log)
        run([sys.executable, "scripts/build_complete_statistical_tests_v3.py"], log)
        run([sys.executable, "scripts/apply_sci_v3_docx_updates.py"], log)
        run([sys.executable, "scripts/apply_sci_v3_baseline_results_to_docx.py"], log)
        run([sys.executable, "scripts/audit_thesis_docx.py", "--docx", str(FINAL_DOCX), "--out-dir", str(FINAL_AUDIT_DIR)], log)
        if RENDER_SCRIPT.exists():
            run([sys.executable, str(RENDER_SCRIPT), str(FINAL_DOCX), "--output_dir", str(FINAL_QA_DIR), "--emit_pdf"], log)
        else:
            log.write(f"[{timestamp()}] render script missing: {RENDER_SCRIPT}\n")
            log.flush()
        copy_public_outputs()
        final_m0_missing, final_all_missing = missing_counts()
        done = f"[{timestamp()}] done; m0_missing={final_m0_missing}; all_missing={final_all_missing}"
        print(done, flush=True)
        log.write(done + "\n")


if __name__ == "__main__":
    main()
