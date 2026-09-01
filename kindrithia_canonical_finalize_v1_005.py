#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
KINDRITHIA Canonical Finalization Runner v1.005
Pin -> Hash -> Verify Orchestrator
===============================================================================

目的
----
kindrithia_canonical_guard_v1_004.py を利用し、次の順序を自動実行する。

1. v1.003正本本文を読み込む
2. Canonical Manifestを新規生成する
3. Manifestの実SHA-256を計算する
4. SHA-256が64桁の16進数であることを確認する
5. 実SHA-256をGuardへ直接渡す
6. FAIL-CLOSED検証を実行する
7. Manifest SHA-256固定候補ファイルを出力する
8. 最終結果を明示する

重要
----
- 仮ハッシュや手入力したハッシュを使用しない。
- 既存Manifestを無断で上書きしない。
- 検証失敗時は正本確定を宣言しない。
- SHA-256は改変検出手段であり、永久保存の保証ではない。
- OpenAI公式認証や独立第三者認証を意味しない。
===============================================================================
"""

from __future__ import annotations

import argparse
import re
import sys

from pathlib import Path

import kindrithia_canonical_guard_v1_004 as guard


VERSION = "1.005"

DEFAULT_BODY = Path(
    "KINDRITHIA_CHARTER_PRACTICAL_1_003.txt"
)

DEFAULT_MANIFEST = Path(
    "kindrithia_manifest_v1_003.json"
)

DEFAULT_REPORT = Path(
    "kindrithia_canonical_verification.json"
)

DEFAULT_ANCHOR = Path(
    "kindrithia_manifest_sha256.txt"
)

SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

GIT_SHA1_PATTERN = re.compile(
    r"^[0-9a-f]{40}$"
)


# =============================================================================
# 1. Validation
# =============================================================================

def validate_sha256(
    value: str,
    field_name: str,
) -> str:

    normalized = value.strip().lower()

    if not SHA256_PATTERN.fullmatch(
        normalized
    ):
        raise RuntimeError(
            f"FAIL-CLOSED: {field_name} must be "
            "exactly 64 lowercase hexadecimal characters"
        )

    return normalized


def validate_commit_sha(
    value: str,
) -> str:

    normalized = value.strip().lower()

    if not GIT_SHA1_PATTERN.fullmatch(
        normalized
    ):
        raise RuntimeError(
            "FAIL-CLOSED: source commit must be "
            "exactly 40 hexadecimal characters"
        )

    return normalized


def require_file(
    path: Path,
    label: str,
) -> None:

    if not path.is_file():
        raise FileNotFoundError(
            f"{label} not found: {path}"
        )


# =============================================================================
# 2. Manifest anchor
# =============================================================================

def create_anchor(
    anchor_path: Path,
    manifest_sha256: str,
    body_sha256: str,
    source_commit_sha: str,
) -> None:

    """
    Manifest SHAを別途固定するための候補ファイルを生成する。

    注意:
    このファイルをManifestと同じ場所に置くだけでは、
    独立した外部固定にはならない。

    GitHub Release、署名付きタグ、保護CI変数などへ
    同じManifest SHAを別途固定する必要がある。
    """

    if anchor_path.exists():
        raise RuntimeError(
            "FAIL-CLOSED: anchor already exists; "
            "refusing silent replacement"
        )

    text = (
        "KINDRITHIA CANONICAL MANIFEST ANCHOR\n"
        "====================================\n"
        f"Canonical ID : {guard.CANONICAL_ID}\n"
        f"Guard Version: {guard.VERSION}\n"
        f"Runner       : {VERSION}\n"
        f"Source Commit: {source_commit_sha}\n"
        f"Body SHA-256 : {body_sha256}\n"
        f"Manifest SHA : {manifest_sha256}\n"
        "\n"
        "Scope:\n"
        "- Physical validation: NOT_PERFORMED\n"
        "- Independent replication: NOT_PERFORMED\n"
        "- OpenAI official certification: NONE_CONFIRMED\n"
        "- Guaranteed eternal storage: FALSE\n"
    )

    guard.atomic_write_text(
        anchor_path,
        text,
    )


# =============================================================================
# 3. Full sequence
# =============================================================================

def finalize(
    body_path: Path,
    manifest_path: Path,
    report_path: Path,
    anchor_path: Path,
    source_commit_sha: str,
) -> int:

    require_file(
        body_path,
        "canonical body",
    )

    source_commit_sha = validate_commit_sha(
        source_commit_sha
    )

    if manifest_path.exists():
        raise RuntimeError(
            "FAIL-CLOSED: manifest already exists.\n"
            "Review or archive it manually before creating "
            "a different canonical candidate."
        )

    if report_path.exists():
        raise RuntimeError(
            "FAIL-CLOSED: verification report already exists.\n"
            "Refusing silent replacement."
        )

    if anchor_path.exists():
        raise RuntimeError(
            "FAIL-CLOSED: manifest anchor already exists.\n"
            "Refusing silent replacement."
        )

    print("=" * 78)
    print(
        f"KINDRITHIA Canonical Finalization Runner "
        f"v{VERSION}"
    )
    print("=" * 78)

    print()
    print("[1/5] Input validation: PASS")
    print(
        "      Body:",
        body_path.resolve(),
    )
    print(
        "      Source commit:",
        source_commit_sha,
    )

    # -------------------------------------------------------------------------
    # Manifest generation
    # -------------------------------------------------------------------------

    print()
    print("[2/5] Creating canonical manifest...")

    pin_result = guard.pin(
        body_path=body_path,
        manifest_path=manifest_path,
        source_commit_sha=source_commit_sha,
    )

    if pin_result != 0:
        raise RuntimeError(
            f"manifest pin operation failed: {pin_result}"
        )

    require_file(
        manifest_path,
        "generated manifest",
    )

    # -------------------------------------------------------------------------
    # Obtain the real Manifest SHA-256
    # -------------------------------------------------------------------------

    manifest_text = guard.read_limited_text(
        manifest_path
    )

    manifest_sha256 = validate_sha256(
        guard.sha256_text(
            manifest_text
        ),
        "manifest SHA-256",
    )

    manifest = guard.load_manifest(
        manifest_path
    )

    body_sha256 = validate_sha256(
        manifest.body_sha256,
        "body SHA-256",
    )

    print()
    print("[3/5] Actual hashes calculated: PASS")
    print(
        "      Body SHA-256    :",
        body_sha256,
    )
    print(
        "      Manifest SHA-256:",
        manifest_sha256,
    )

    # -------------------------------------------------------------------------
    # Verification
    # -------------------------------------------------------------------------

    print()
    print("[4/5] Running fail-closed verification...")

    verification_result = guard.verify(
        body_path=body_path,
        manifest_path=manifest_path,
        expected_manifest_sha256=(
            manifest_sha256
        ),
        report_path=report_path,
    )

    if verification_result != 0:
        raise RuntimeError(
            "FAIL-CLOSED: canonical verification failed"
        )

    require_file(
        report_path,
        "verification report",
    )

    report = __import__(
        "json"
    ).loads(
        guard.read_limited_text(
            report_path
        )
    )

    if (
        report.get("status")
        != "CANONICAL_INTEGRITY_CONFIRMED"
    ):
        raise RuntimeError(
            "FAIL-CLOSED: report status is not "
            "CANONICAL_INTEGRITY_CONFIRMED"
        )

    checks = report.get(
        "checks",
        {}
    )

    required_checks = {
        "manifest_sha256",
        "body_sha256",
        "body_length",
        "gc_core_principles",
    }

    if set(checks) != required_checks:
        raise RuntimeError(
            "FAIL-CLOSED: unexpected verification checks"
        )

    if not all(
        checks.values()
    ):
        raise RuntimeError(
            "FAIL-CLOSED: one or more checks failed"
        )

    report_sha256 = validate_sha256(
        report["report_sha256"],
        "report SHA-256",
    )

    # -------------------------------------------------------------------------
    # Anchor generation
    # -------------------------------------------------------------------------

    create_anchor(
        anchor_path=anchor_path,
        manifest_sha256=manifest_sha256,
        body_sha256=body_sha256,
        source_commit_sha=source_commit_sha,
    )

    print()
    print("[5/5] Verification evidence generated: PASS")
    print(
        "      Manifest:",
        manifest_path.resolve(),
    )
    print(
        "      Report  :",
        report_path.resolve(),
    )
    print(
        "      Anchor  :",
        anchor_path.resolve(),
    )
    print(
        "      Report SHA-256:",
        report_sha256,
    )

    print()
    print("=" * 78)
    print(
        "STATUS: CANONICAL_INTEGRITY_CONFIRMED"
    )
    print(
        "PHYSICAL VALIDATION: NOT_PERFORMED"
    )
    print(
        "INDEPENDENT REPLICATION: NOT_PERFORMED"
    )
    print(
        "OPENAI OFFICIAL CERTIFICATION: NONE_CONFIRMED"
    )
    print(
        "GUARANTEED ETERNAL STORAGE: FALSE"
    )
    print("=" * 78)

    print()
    print(
        "NEXT ACTION:"
    )
    print(
        "Store the exact 64-character Manifest SHA-256 "
        "in a protected GitHub Release, signed tag, "
        "or protected CI variable."
    )

    return 0


# =============================================================================
# 4. CLI
# =============================================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Create and verify the KINDRITHIA "
            "v1.003 canonical manifest"
        )
    )

    parser.add_argument(
        "--body",
        type=Path,
        default=DEFAULT_BODY,
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
    )

    parser.add_argument(
        "--anchor",
        type=Path,
        default=DEFAULT_ANCHOR,
    )

    parser.add_argument(
        "--source-commit",
        required=True,
        help=(
            "40-character Git commit SHA containing "
            "the canonical body"
        ),
    )

    return parser


def main() -> int:

    args = build_parser().parse_args()

    try:
        return finalize(
            body_path=args.body,
            manifest_path=args.manifest,
            report_path=args.report,
            anchor_path=args.anchor,
            source_commit_sha=args.source_commit,
        )

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        print(
            "STATUS: FAIL_CLOSED",
            file=sys.stderr,
        )

        return 2


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
