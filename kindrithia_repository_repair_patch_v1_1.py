#!/usr/bin/env python3
"""KINDRITHIA repository repair patch v1.1.

Conservative, local-only repair tool for sakagami-circulation-equations.
Dry-run is the default. Use --apply to write changes. This tool repairs
documentation/integrity metadata; it does not certify mathematics or physics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_SOURCE = (
    "README.md",
    "sakagami_equations.py",
    "kindrithia_charter_practical_v1_003.py",
    "KINDRITHIA_CHARTER_PRACTICAL_1_003.txt",
    "kindrithia_canonical_guard_v1_004.py",
    "kindrithia_canonical_finalize_v1_005.py",
)
GENERATED = (
    "kindrithia_manifest_v1_003.json",
    "kindrithia_canonical_verification.json",
    "kindrithia_manifest_sha256.txt",
)

MIT_LICENSE = """MIT License

Copyright (c) 2026 Tetsushi Sakagami

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

REPLACEMENTS = {
    "README.md": (
        ("反証記録の永遠保存", "反証記録の継続保管方針（保存期間の保証ではなし）"),
        ("正準性", "正準性"),
        ("透明性 111%", "透明性方針を明示"),
        ("HARMONY: PERFECT", "HARMONY: POLICY_DECLARED"),
    ),
    "kindrithia_system_status_report_v1_0.py": (
        ("PERMANENTLY RETAINED", "RETENTION_POLICY_ACTIVE"),
        ("retention: ETERNAL", "retention: POLICY_DECLARED_NO_DURATION_GUARANTEE"),
        ("NEVER_APPLIED", "NOT_APPLIED_IN_CURRENT_VALIDATION"),
        ("SCIENTIFIC_INTEGRITY: MAXIMUM", "SCIENTIFIC_INTEGRITY_POLICY: DECLARED"),
        ("SECURITY: MAXIMUM", "SECURITY_STATUS: NOT_INDEPENDENTLY_AUDITED"),
        ("TRANSPARENCY: 111%", "TRANSPARENCY_POLICY: DECLARED"),
        ("HARMONY: PERFECT", "HARMONY: POLICY_DECLARED"),
    ),
}


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    message: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def load_json(path: Path, findings: list[Finding]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings.append(Finding("ERROR", "INVALID_JSON", path.name, str(exc)))
        return None


def validate_generated(root: Path, findings: list[Finding]) -> str:
    paths = {name: root / name for name in GENERATED}
    present = {name: path.exists() for name, path in paths.items()}
    if not any(present.values()):
        findings.append(Finding(
            "INFO", "GENERATED_FILES_PENDING", ".",
            "v1.005生成物は未作成です。finalize実行後に再検査してください。",
        ))
        return "READY_TO_FINALIZE"
    if not all(present.values()):
        missing = ", ".join(name for name, ok in present.items() if not ok)
        findings.append(Finding("ERROR", "PARTIAL_GENERATED_SET", ".", missing))
        return "HOLD"

    manifest_path = paths[GENERATED[0]]
    report_path = paths[GENERATED[1]]
    anchor_path = paths[GENERATED[2]]
    manifest_hash = sha256_file(manifest_path)
    anchor_text = anchor_path.read_text(encoding="utf-8").strip().lower()
    if not HEX64.fullmatch(anchor_text):
        findings.append(Finding("ERROR", "INVALID_ANCHOR", anchor_path.name,
                                "外部固定用候補は64文字SHA-256である必要があります。"))
    elif anchor_text != manifest_hash:
        findings.append(Finding("ERROR", "ANCHOR_MISMATCH", anchor_path.name,
                                "anchorとmanifest実体のSHA-256が一致しません。"))

    manifest = load_json(manifest_path, findings)
    report = load_json(report_path, findings)
    if isinstance(manifest, dict):
        for key, value in manifest.items():
            if "sha256" in key.lower() and isinstance(value, str) and not HEX64.fullmatch(value.lower()):
                findings.append(Finding("ERROR", "MALFORMED_SHA256", manifest_path.name, key))
    if isinstance(report, dict):
        checks = report.get("checks")
        if not isinstance(checks, dict) or not checks or not all(v is True for v in checks.values()):
            findings.append(Finding("ERROR", "FAILED_OR_MISSING_CHECKS", report_path.name,
                                    "verification checksが全てtrueではありません。"))
        if report.get("status") != "CANONICAL_INTEGRITY_CONFIRMED":
            findings.append(Finding("ERROR", "UNCONFIRMED_STATUS", report_path.name,
                                    "canonical integrity statusが未確認です。"))
        scope = report.get("scope", {})
        expected = {
            "physical_validation": "NOT_PERFORMED",
            "independent_replication": "NOT_PERFORMED",
            "openai_official_certification": "NONE_CONFIRMED",
        }
        for key, value in expected.items():
            if scope.get(key) != value:
                findings.append(Finding("ERROR", "EPISTEMIC_SCOPE_DRIFT", report_path.name,
                                        f"{key} must be {value}"))
    return "HOLD" if any(x.severity == "ERROR" for x in findings) else "CANONICAL_INTEGRITY_CONFIRMED"


def run(root: Path, apply: bool, report_path: Path) -> int:
    root = root.resolve()
    findings: list[Finding] = []
    changes: list[dict[str, Any]] = []
    if not root.is_dir():
        raise SystemExit(f"repository root not found: {root}")

    for name in REQUIRED_SOURCE:
        if not (root / name).is_file():
            findings.append(Finding("ERROR", "MISSING_REQUIRED_SOURCE", name, "必須ファイルがありません。"))

    planned: dict[Path, bytes] = {}
    license_path = root / "LICENSE"
    if not license_path.exists():
        planned[license_path] = MIT_LICENSE.encode("utf-8")
        findings.append(Finding("WARNING", "LICENSE_MISSING", "LICENSE", "MIT LICENSEを追加予定です。"))

    for relative, rules in REPLACEMENTS.items():
        path = root / relative
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = original
        for old, new in rules:
            # Idempotence: some Japanese replacements contain the old token
            # (e.g. 正準性 inside 半正準性).
            if new not in updated:
                updated = updated.replace(old, new)
        if updated != original:
            planned[path] = updated.encode("utf-8")

    # Never erase the past observation record; require explicit falsification memory.
    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in root.rglob("*") if p.is_file() and p.suffix in {".py", ".md", ".json"}
        and ".kindrithia_repair_backup" not in p.parts
    )
    if "0.81649658" in combined and "RESOLVED_INPUT_ERROR" not in combined:
        findings.append(Finding("ERROR", "FALSIFICATION_MEMORY_INCOMPLETE", ".",
                                "0.81649658をRESOLVED_INPUT_ERROR（入力ミスで解決済み）として記録を保持してください。"))

    generated_status = validate_generated(root, findings)
    backup_dir: Path | None = None
    if apply and planned:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = root / ".kindrithia_repair_backup" / stamp
        for path, data in planned.items():
            before = sha256_file(path) if path.exists() else None
            if path.exists():
                destination = backup_dir / path.relative_to(root)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
            atomic_write(path, data)
            changes.append({"path": str(path.relative_to(root)), "before_sha256": before,
                            "after_sha256": sha256_file(path)})
    else:
        for path, data in planned.items():
            changes.append({"path": str(path.relative_to(root)),
                            "before_sha256": sha256_file(path) if path.exists() else None,
                            "planned_sha256": sha256_bytes(data)})

    errors = sum(x.severity == "ERROR" for x in findings)
    status = "HOLD" if errors else ("PATCH_APPLIED" if apply else "DRY_RUN_READY")
    payload = {
        "schema": "kindrithia-repository-repair-v1",
        "patch_version": VERSION,
        "generated_at": utc_now(),
        "mode": "APPLY" if apply else "DRY_RUN",
        "repository": str(root),
        "status": status,
        "generated_artifact_status": generated_status,
        "changes": changes,
        "findings": [asdict(x) for x in findings],
        "backup_directory": str(backup_dir) if backup_dir else None,
        "epistemic_scope": {
            "mathematical_core": "SEPARATE_TEST_EXECUTION_REQUIRED",
            "physical_validation": "NOT_PERFORMED",
            "independent_replication": "NOT_PERFORMED",
            "openai_official_certification": "NONE_CONFIRMED",
        },
    }
    payload["payload_sha256"] = sha256_bytes(stable_json(payload))
    atomic_write(report_path.resolve(), json.dumps(payload, ensure_ascii=False, indent=2,
                                                    allow_nan=False).encode("utf-8") + b"\n")
    print(f"MODE   : {payload['mode']}")
    print(f"STATUS : {status}")
    print(f"CHANGES: {len(changes)}")
    print(f"ERRORS : {errors}")
    print(f"REPORT : {report_path.resolve()}")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="バックアップ後に補修を適用")
    parser.add_argument("--report", type=Path, default=Path("kindrithia_repair_report.json"))
    args = parser.parse_args()
    return run(args.repository, args.apply, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
