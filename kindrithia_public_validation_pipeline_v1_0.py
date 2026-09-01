#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KINDRITHIA Public Validation Pipeline v1.0.

Implements the five ordered gates for the public repository:
  1. Generate three artifacts from a real commit.
  2. Verify the 64-character Manifest SHA-256 with Canonical Guard.
  3. Run public pytest tests.
  4. Install a GitHub Actions verification workflow.
  5. Create a signed tag and GitHub Release containing the external anchor.

Default mode is dry-run. Local writes require --apply; GitHub publication also
requires --publish. This establishes reproducible integrity checking only. It
does not certify physical validity, novelty, independent replication, or any
OpenAI endorsement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

VERSION = "1.0"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

BODY = "KINDRITHIA_CHARTER_PRACTICAL_1_003.txt"
MANIFEST = "kindrithia_manifest_v1_003.json"
ANCHOR = "kindrithia_manifest_sha256.txt"
REPORT = "kindrithia_canonical_verification.json"
FINALIZER = "kindrithia_canonical_finalize_v1_005.py"
GUARD = "kindrithia_canonical_guard_v1_004.py"
WORKFLOW = ".github/workflows/verify.yml"

WORKFLOW_TEXT = """name: Public Validation

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; else pip install pytest numpy scipy; fi
      - name: Compile public Python files
        run: python -m compileall -q .
      - name: Run pytest
        run: python -m pytest -q
      - name: Verify canonical artifacts
        shell: bash
        run: |
          test -f kindrithia_manifest_v1_003.json
          test -f kindrithia_manifest_sha256.txt
          test -f kindrithia_canonical_verification.json
          anchor="$(tr -d '\\r\\n' < kindrithia_manifest_sha256.txt)"
          [[ "$anchor" =~ ^[0-9a-f]{64}$ ]]
          python kindrithia_canonical_guard_v1_004.py verify \\
            --body KINDRITHIA_CHARTER_PRACTICAL_1_003.txt \\
            --manifest kindrithia_manifest_v1_003.json \\
            --expected-manifest-sha256 "$anchor" \\
            --report /tmp/kindrithia_ci_verification.json
      - name: Check epistemic scope
        run: |
          python - <<'PY'
          import json
          from pathlib import Path
          p = json.loads(Path('/tmp/kindrithia_ci_verification.json').read_text())
          assert p['status'] == 'CANONICAL_INTEGRITY_CONFIRMED'
          assert all(p['checks'].values())
          scope = p['scope']
          assert scope['physical_validation'] == 'NOT_PERFORMED'
          assert scope['independent_replication'] == 'NOT_PERFORMED'
          assert scope['openai_official_certification'] == 'NONE_CONFIRMED'
          assert scope['guaranteed_eternal_storage'] is False
          PY
"""


class PipelineError(RuntimeError):
    pass


@dataclass
class StepResult:
    number: int
    name: str
    status: str
    detail: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(command: Sequence[str], cwd: Path, *, capture: bool = False) -> str:
    completed = subprocess.run(
        list(command), cwd=cwd, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout or "command failed").strip()
        raise PipelineError(f"{' '.join(command)}: {detail}")
    return (completed.stdout or "").strip()


def require_program(name: str) -> None:
    if shutil.which(name) is None:
        raise PipelineError(f"required program not found: {name}")


def require_clean_worktree(root: Path) -> None:
    dirty = run(["git", "status", "--porcelain"], root, capture=True)
    if dirty:
        raise PipelineError("working tree is not clean; commit or stash changes first")


def current_commit(root: Path) -> str:
    value = run(["git", "rev-parse", "HEAD"], root, capture=True).lower()
    if not HEX40.fullmatch(value):
        raise PipelineError("HEAD is not a full 40-character Git commit SHA")
    run(["git", "cat-file", "-e", f"{value}^{{commit}}"], root)
    return value


def read_anchor(root: Path) -> str:
    value = (root / ANCHOR).read_text(encoding="utf-8").strip().lower()
    if not HEX64.fullmatch(value):
        raise PipelineError(f"{ANCHOR} must contain exactly one 64-character SHA-256")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def validate_report(root: Path) -> None:
    data = json.loads((root / REPORT).read_text(encoding="utf-8"))
    if data.get("status") != "CANONICAL_INTEGRITY_CONFIRMED":
        raise PipelineError("canonical report status is not confirmed")
    checks = data.get("checks")
    if not isinstance(checks, dict) or not checks or not all(v is True for v in checks.values()):
        raise PipelineError("canonical report does not contain all-PASS checks")
    scope = data.get("scope", {})
    required_scope = {
        "physical_validation": "NOT_PERFORMED",
        "independent_replication": "NOT_PERFORMED",
        "openai_official_certification": "NONE_CONFIRMED",
        "guaranteed_eternal_storage": False,
    }
    for key, expected in required_scope.items():
        if scope.get(key) != expected:
            raise PipelineError(f"epistemic scope mismatch: {key} must be {expected!r}")


def check_required(root: Path) -> None:
    for relative in (BODY, FINALIZER, GUARD):
        if not (root / relative).is_file():
            raise PipelineError(f"required file missing: {relative}")


def execute(root: Path, apply: bool, publish: bool, tag: str) -> list[StepResult]:
    results: list[StepResult] = []
    require_program("git")
    check_required(root)
    commit = current_commit(root)

    if not apply:
        results.extend([
            StepResult(1, "Generate artifacts", "PLANNED", f"source commit {commit}"),
            StepResult(2, "Guard verification", "PLANNED", "requires generated 64-char anchor"),
            StepResult(3, "Public pytest", "PLANNED", "python -m pytest -q"),
            StepResult(4, "GitHub Actions", "PLANNED", WORKFLOW),
            StepResult(5, "Signed tag and Release", "PLANNED", tag),
        ])
        return results

    require_clean_worktree(root)

    # 1. Generate once. A later --publish run reuses the committed artifacts;
    # silently replacing an existing canonical set is forbidden.
    artifact_paths = [root / name for name in (MANIFEST, ANCHOR, REPORT)]
    existence = [path.exists() for path in artifact_paths]
    if any(existence) and not all(existence):
        raise PipelineError("partial canonical artifact set; restore or remove it explicitly")
    if not any(existence):
        run([sys.executable, FINALIZER, "--source-commit", commit], root)
    for relative in (MANIFEST, ANCHOR, REPORT):
        if not (root / relative).is_file():
            raise PipelineError(f"finalizer did not generate {relative}")
    anchor = read_anchor(root)
    if sha256_file(root / MANIFEST) != anchor:
        raise PipelineError("Manifest bytes do not match the external anchor")
    generation_mode = "reused existing committed artifacts" if all(existence) else "generated"
    results.append(StepResult(1, "Generate artifacts", "PASS",
                              f"{generation_mode}; Manifest SHA-256 {anchor}"))

    # 2. Verify from the external anchor, not from an embedded status string.
    run([
        sys.executable, GUARD, "verify", "--body", BODY,
        "--manifest", MANIFEST, "--expected-manifest-sha256", anchor,
        "--report", REPORT,
    ], root)
    validate_report(root)
    results.append(StepResult(2, "Guard verification", "PASS", "all checks passed"))

    # 3. Tests are a separate gate from canonical document integrity.
    if not (root / "tests").is_dir():
        raise PipelineError("public tests/ directory is missing")
    run([sys.executable, "-m", "pytest", "-q"], root)
    results.append(StepResult(3, "Public pytest", "PASS", "pytest completed successfully"))

    # 4. Install the reproducible workflow locally. Branch protection remains a
    # GitHub repository setting and must be enabled after its first green run.
    workflow_path = root / WORKFLOW
    if workflow_path.exists() and workflow_path.read_text(encoding="utf-8") != WORKFLOW_TEXT:
        raise PipelineError(f"refusing to overwrite existing different workflow: {WORKFLOW}")
    atomic_write(workflow_path, WORKFLOW_TEXT)
    results.append(StepResult(4, "GitHub Actions", "PASS", f"installed {WORKFLOW}"))

    if not publish:
        results.append(StepResult(5, "Signed tag and Release", "PENDING",
                                  "commit generated files/workflow, obtain a green CI run, then rerun with --publish"))
        return results

    # Publishing is intentionally blocked while generated local changes are
    # uncommitted, preventing a tag from pointing at the wrong tree.
    require_clean_worktree(root)
    require_program("gh")
    run(["git", "verify-commit", "HEAD"], root)
    existing = run(["git", "tag", "--list", tag], root, capture=True)
    if existing:
        raise PipelineError(f"tag already exists: {tag}")
    message = f"KINDRITHIA canonical Manifest SHA-256: {anchor}"
    run(["git", "tag", "-s", tag, "-m", message], root)
    run(["git", "push", "origin", tag], root)
    notes = (
        "Canonical integrity anchor\n\n"
        f"Manifest SHA-256: `{anchor}`\n\n"
        "Scope: physical validation NOT_PERFORMED; independent replication "
        "NOT_PERFORMED; OpenAI official certification NONE_CONFIRMED."
    )
    run(["gh", "release", "create", tag, ANCHOR, MANIFEST, REPORT,
         "--verify-tag", "--title", "KINDRITHIA v1.003 canonical fixation",
         "--notes", notes], root)
    results.append(StepResult(5, "Signed tag and Release", "PASS", tag))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="run local generation, verification and workflow install")
    parser.add_argument("--publish", action="store_true", help="create and push signed tag and GitHub Release")
    parser.add_argument("--tag", default="v1.003-canonical-fixed")
    parser.add_argument("--json-report", type=Path, default=None,
                        help="report path (default: repository .git directory)")
    args = parser.parse_args()
    if args.publish and not args.apply:
        parser.error("--publish requires --apply")

    root = args.repository.resolve()
    try:
        results = execute(root, args.apply, args.publish, args.tag)
        status = "COMPLETE" if all(x.status == "PASS" for x in results) else (
            "LOCAL_GATES_COMPLETE_PUBLICATION_PENDING" if args.apply else "DRY_RUN"
        )
        exit_code = 0
    except (PipelineError, OSError, json.JSONDecodeError) as exc:
        results = [StepResult(0, "Pipeline", "FAIL_CLOSED", str(exc))]
        status = "FAIL_CLOSED"
        exit_code = 1

    payload = {
        "schema": "kindrithia-public-validation-pipeline-v1",
        "version": VERSION,
        "generated_at": utc_now(),
        "repository": str(root),
        "status": status,
        "steps": [asdict(item) for item in results],
        "scope": {
            "physical_validation": "NOT_PERFORMED",
            "independent_replication": "NOT_PERFORMED",
            "openai_official_certification": "NONE_CONFIRMED",
            "guaranteed_eternal_storage": False,
        },
    }
    if args.json_report is None:
        report_path = root / ".git" / "kindrithia_public_validation_pipeline_report.json"
    else:
        report_path = args.json_report if args.json_report.is_absolute() else root / args.json_report
    atomic_write(report_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"STATUS: {status}")
    for item in results:
        print(f"[{item.status:12}] {item.number}. {item.name}: {item.detail}")
    print(f"REPORT: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
