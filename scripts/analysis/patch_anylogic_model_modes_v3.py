#!/usr/bin/env python3
"""Patch AnyLogic ALP with structural modelMode support for SCI v3 baselines.

The patch is intentionally text-based because AnyLogic ALP files store Java code
inside CDATA blocks. It is safe to run with --check against a copy before
touching the active model.
"""

from __future__ import annotations

import argparse
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALP = ROOT / "谣言传播模型_SCI补实验版.alp"
BACKUP_DIR = ROOT / "工程备份"


REPLACEMENTS: list[tuple[str, str]] = [
    (
        """double k_on = this.onlineConnections.getConnections().size();
if (k_on == 0) return 0.0;

// 统计线上邻居中处于 I1 (OnlineInfected) 状态的数量
long countI1 = this.onlineConnections.getConnections().stream()
    .filter(a -> a.inState(Person.OnlineInfected)).count();

return main.线上传播速率 * ((double)countI1 / k_on);""",
        """double baselineMultiplier = 1.0;
if (main.modelMode > 0
    && (main.enableOnlineIntervention || main.enableOfflineIntervention)
    && time() >= main.interventionStartTime) {
    baselineMultiplier = Math.max(0.05, 1.0 - (main.线上辟谣影响系数 + main.线下辟谣影响系数));
}

if (main.modelMode == 1) {
    double n = Math.max(1, main.people.size());
    double infected = main.people.OnlineInfected() + main.people.OfflineInfected();
    return main.线上传播速率 * baselineMultiplier * infected / n;
}

double k_on = this.onlineConnections.getConnections().size();
if (k_on == 0) return 0.0;

// 统计线上邻居中处于 I1 (OnlineInfected) 状态的数量
long countI1 = this.onlineConnections.getConnections().stream()
    .filter(a -> a.inState(Person.OnlineInfected)).count();

return main.线上传播速率 * baselineMultiplier * ((double)countI1 / k_on);""",
    ),
    (
        """double k_off = this.offlineConnections.getConnections().size();
if (k_off == 0) return 0.0;

// 统计线下邻居中处于 I2 (OfflineInfected) 状态的数量
long countI2 = this.offlineConnections.getConnections().stream()
    .filter(a -> a.inState(Person.OfflineInfected)).count();

return main.线下传播速率 * ((double)countI2 / k_off);""",
        """if (main.modelMode == 1 || main.modelMode == 2) return 0.0;

double baselineMultiplier = 1.0;
if (main.modelMode > 0
    && (main.enableOnlineIntervention || main.enableOfflineIntervention)
    && time() >= main.interventionStartTime) {
    baselineMultiplier = Math.max(0.05, 1.0 - (main.线上辟谣影响系数 + main.线下辟谣影响系数));
}

double k_off = this.offlineConnections.getConnections().size();
if (k_off == 0) return 0.0;

// 统计线下邻居中处于 I2 (OfflineInfected) 状态的数量
long countI2 = this.offlineConnections.getConnections().stream()
    .filter(a -> a.inState(Person.OfflineInfected)).count();

return main.线下传播速率 * baselineMultiplier * ((double)countI2 / k_off);""",
    ),
    (
        """boolean autoOnline = main.enableOnlineIntervention && time() >= main.interventionStartTime;
if (!(main.isOnlineIntervention || autoOnline)) return 0.0;""",
        """if (main.modelMode > 0) return 0.0;

boolean autoOnline = main.enableOnlineIntervention && time() >= main.interventionStartTime;
if (!(main.isOnlineIntervention || autoOnline)) return 0.0;""",
    ),
    (
        """boolean autoOffline = main.enableOfflineIntervention && time() >= main.interventionStartTime;
if (!(main.isOfflineIntervention || autoOffline)) return 0.0;""",
        """if (main.modelMode > 0) return 0.0;

boolean autoOffline = main.enableOfflineIntervention && time() >= main.interventionStartTime;
if (!(main.isOfflineIntervention || autoOffline)) return 0.0;""",
    ),
    (
        """<Condition><![CDATA[uniform(0,1) < 0.70]]></Condition>""",
        """<Condition><![CDATA[(main.modelMode == 1 || main.modelMode == 2) || uniform(0,1) < 0.70]]></Condition>""",
    ),
    (
        """<Condition><![CDATA[uniform(0,1) < 0.85]]></Condition>""",
        """<Condition><![CDATA[main.modelMode != 1 && main.modelMode != 2 && uniform(0,1) < 0.85]]></Condition>""",
    ),
    (
        """<Code><![CDATA[getInfectionRate_Online() * 0.001]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? getInfectionRate_Online() * 0.001 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[getInfectionRate_Online() * 0.2]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? getInfectionRate_Online() * 0.2 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[getInfectionRate_Offline() * 0.2]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? getInfectionRate_Offline() * 0.2 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[(线上传播速率 / 24.0) * 0.01]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? (线上传播速率 / 24.0) * 0.01 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[(线下传播速率 / 24.0) * 0.01]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? (线下传播速率 / 24.0) * 0.01 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[线下传播速率]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? 线下传播速率 : 0.0]]></Code>""",
    ),
    (
        """<Code><![CDATA[线上传播速率]]></Code>""",
        """<Code><![CDATA[main.modelMode == 0 ? 线上传播速率 : 0.0]]></Code>""",
    ),
]


def apply_replacements(text: str) -> tuple[str, list[str]]:
    changed: list[str] = []
    for index, (old, new) in enumerate(REPLACEMENTS, start=1):
        if new in text:
            changed.append(f"{index}: already patched")
            continue
        count = text.count(old)
        if count == 0:
            raise RuntimeError(f"replacement {index} target not found")
        text = text.replace(old, new)
        changed.append(f"{index}: replaced {count}")
    return text, changed


def validate_xml_text(text: str) -> None:
    ET.fromstring(text.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch AnyLogic modelMode structural baseline support.")
    parser.add_argument("--alp", type=Path, default=ALP)
    parser.add_argument("--out", type=Path, default=None, help="Write patched ALP to a separate path")
    parser.add_argument("--check", action="store_true", help="Validate and report without overwriting --alp")
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    text = args.alp.read_text(encoding="utf-8")
    patched, changed = apply_replacements(text)
    validate_xml_text(patched)

    for line in changed:
        print(line)

    if args.check:
        print("check: XML valid; no file written")
        return

    out = args.out or args.alp
    if out == args.alp and not args.no_backup:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup = BACKUP_DIR / f"谣言传播模型_SCI补实验版_结构基线补丁前_{datetime.now().strftime('%Y%m%d_%H%M%S')}.alp"
        shutil.copy2(args.alp, backup)
        print(f"backup: {backup}")

    out.write_text(patched, encoding="utf-8")
    print(f"wrote: {out}")


if __name__ == "__main__":
    main()
