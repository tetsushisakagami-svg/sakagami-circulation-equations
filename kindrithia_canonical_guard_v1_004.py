#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
KINDRITHIA Canonical Guard v1.004
Fail-Closed Canonical Manifest Verifier
===============================================================================

目的
----
KINDRITHIA-CHARTER-PRACTICAL-1.003 の本文を、

1. Unicode NFC正規化
2. 改行統一
3. SHA-256固定
4. Manifest自体のSHA-256固定
5. 完全一致以外はFAIL-CLOSED
6. 検証結果をJSON記録

によって検証する。

重要
----
- v1.003本文そのものは変更しない。
- "UNKNOWN" や "CANONICAL_FIXATION" をハッシュ代わりに使わない。
- status文字列だけで正本判定しない。
- GitHub commit、SHA-256、本文ハッシュの一致から判定する。
- SHA-256は改変検出の補助であり、永続性そのものを保証しない。
- OpenAI公式認証や独立第三者認証を主張しない。
===============================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import unicodedata

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1.004"
PRODUCT_NAME = "KINDRITHIA Canonical Guard"

CANONICAL_ID = (
    "KINDRITHIA-CHARTER-PRACTICAL-1.003"
)

MANIFEST_SCHEMA = (
    "kindrithia-canonical-manifest-v1"
)

MAX_FILE_BYTES = 8 * 1024 * 1024


# =============================================================================
# 1. Utilities
# =============================================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )


def normalize_text(text: str) -> str:
    """
    Unicode NFC、改行、末尾改行を統一する。
    """

    normalized = unicodedata.normalize(
        "NFC",
        text,
    )

    normalized = normalized.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    normalized = normalized.rstrip("\n") + "\n"

    return normalized


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(
        text.encode("utf-8")
    )


def stable_json(data: Any) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def read_limited_text(path: Path) -> str:
    raw = path.read_bytes()

    if len(raw) > MAX_FILE_BYTES:
        raise ValueError(
            f"file exceeds {MAX_FILE_BYTES} bytes: {path}"
        )

    return raw.decode("utf-8")


def atomic_write_text(
    path: Path,
    text: str,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    encoded = text.encode("utf-8")

    if len(encoded) > MAX_FILE_BYTES:
        raise ValueError(
            "refusing oversized output"
        )

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=str(path.parent),
    )

    temporary_path = Path(
        temporary_name
    )

    try:
        with os.fdopen(
            fd,
            "wb",
        ) as stream:

            stream.write(encoded)
            stream.flush()
            os.fsync(
                stream.fileno()
            )

        os.replace(
            temporary_path,
            path,
        )

    finally:
        temporary_path.unlink(
            missing_ok=True
        )


# =============================================================================
# 2. Manifest
# =============================================================================

@dataclass(frozen=True)
class CanonicalManifest:
    schema: str
    canonical_id: str
    charter_version: str

    body_sha256: str
    body_bytes_normalized: int

    source_commit_sha: str
    created_at: str

    principles: tuple[str, ...]
    declared_status: str

    openai_official_certification: str
    independent_replication: str
    physical_validation: str


def validate_commit_sha(
    commit_sha: str,
) -> str:
    """
    Gitの完全SHA-1形式、40桁の16進数だけを受理する。
    """

    value = commit_sha.strip().lower()

    if len(value) != 40:
        raise ValueError(
            "source commit SHA must contain 40 hex characters"
        )

    if any(
        character not in "0123456789abcdef"
        for character in value
    ):
        raise ValueError(
            "source commit SHA contains non-hex characters"
        )

    return value


def build_manifest(
    body_path: Path,
    source_commit_sha: str,
) -> CanonicalManifest:

    body = normalize_text(
        read_limited_text(
            body_path
        )
    )

    commit_sha = validate_commit_sha(
        source_commit_sha
    )

    return CanonicalManifest(
        schema=MANIFEST_SCHEMA,

        canonical_id=CANONICAL_ID,
        charter_version="1.003",

        body_sha256=sha256_text(body),

        body_bytes_normalized=len(
            body.encode("utf-8")
        ),

        source_commit_sha=commit_sha,
        created_at=utc_now(),

        principles=(
            "SUSTAINABILITY",
            "REVERSIBILITY",
            "NON_COERCION",
        ),

        declared_status=(
            "CANONICAL_CANDIDATE_PINNED"
        ),

        openai_official_certification=(
            "NONE_CONFIRMED"
        ),

        independent_replication=(
            "NOT_PERFORMED"
        ),

        physical_validation=(
            "NOT_PERFORMED"
        ),
    )


def manifest_text(
    manifest: CanonicalManifest,
) -> str:

    return json.dumps(
        asdict(manifest),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"


# =============================================================================
# 3. Pin operation
# =============================================================================

def pin(
    body_path: Path,
    manifest_path: Path,
    source_commit_sha: str,
) -> int:

    if manifest_path.exists():
        raise RuntimeError(
            "FAIL-CLOSED: manifest already exists; "
            "refusing silent replacement"
        )

    manifest = build_manifest(
        body_path,
        source_commit_sha,
    )

    serialized = manifest_text(
        manifest
    )

    atomic_write_text(
        manifest_path,
        serialized,
    )

    manifest_sha256 = sha256_text(
        serialized
    )

    print("=" * 78)
    print(f"{PRODUCT_NAME} v{VERSION}")
    print("=" * 78)

    print(
        "Canonical ID :",
        manifest.canonical_id,
    )

    print(
        "Body SHA-256 :",
        manifest.body_sha256,
    )

    print(
        "Manifest SHA :",
        manifest_sha256,
    )

    print(
        "Source commit:",
        manifest.source_commit_sha,
    )

    print()
    print(
        "NEXT ACTION:"
    )

    print(
        "Store the Manifest SHA-256 outside this file, "
        "for example in a protected GitHub release, "
        "signed tag, or protected CI variable."
    )

    print()
    print(
        "Do not describe this as OpenAI certification "
        "or independent replication."
    )

    return 0


# =============================================================================
# 4. Verification
# =============================================================================

def load_manifest(
    manifest_path: Path,
) -> CanonicalManifest:

    raw = read_limited_text(
        manifest_path
    )

    data = json.loads(
        raw
    )

    required = {
        "schema",
        "canonical_id",
        "charter_version",
        "body_sha256",
        "body_bytes_normalized",
        "source_commit_sha",
        "created_at",
        "principles",
        "declared_status",
        "openai_official_certification",
        "independent_replication",
        "physical_validation",
    }

    missing = required - set(
        data
    )

    unknown = set(
        data
    ) - required

    if missing:
        raise RuntimeError(
            f"manifest fields missing: {sorted(missing)}"
        )

    if unknown:
        raise RuntimeError(
            f"unknown manifest fields: {sorted(unknown)}"
        )

    data["principles"] = tuple(
        data["principles"]
    )

    manifest = CanonicalManifest(
        **data
    )

    if manifest.schema != MANIFEST_SCHEMA:
        raise RuntimeError(
            "manifest schema mismatch"
        )

    if manifest.canonical_id != CANONICAL_ID:
        raise RuntimeError(
            "canonical ID mismatch"
        )

    validate_commit_sha(
        manifest.source_commit_sha
    )

    return manifest


def verify(
    body_path: Path,
    manifest_path: Path,
    expected_manifest_sha256: str,
    report_path: Path,
) -> int:

    manifest_raw = read_limited_text(
        manifest_path
    )

    actual_manifest_sha256 = sha256_text(
        manifest_raw
    )

    expected = (
        expected_manifest_sha256
        .strip()
        .lower()
    )

    if len(expected) != 64:
        raise RuntimeError(
            "FAIL-CLOSED: expected manifest SHA-256 "
            "must contain 64 hex characters"
        )

    manifest_hash_valid = (
        actual_manifest_sha256
        == expected
    )

    manifest = load_manifest(
        manifest_path
    )

    normalized_body = normalize_text(
        read_limited_text(
            body_path
        )
    )

    actual_body_sha256 = sha256_text(
        normalized_body
    )

    body_hash_valid = (
        actual_body_sha256
        == manifest.body_sha256
    )

    body_length_valid = (
        len(
            normalized_body.encode("utf-8")
        )
        == manifest.body_bytes_normalized
    )

    principles_valid = (
        manifest.principles
        == (
            "SUSTAINABILITY",
            "REVERSIBILITY",
            "NON_COERCION",
        )
    )

    passed = all(
        (
            manifest_hash_valid,
            body_hash_valid,
            body_length_valid,
            principles_valid,
        )
    )

    report = {
        "schema":
            "kindrithia-canonical-verification-v1",

        "guard_version":
            VERSION,

        "canonical_id":
            CANONICAL_ID,

        "verified_at":
            utc_now(),

        "source_commit_sha":
            manifest.source_commit_sha,

        "checks": {
            "manifest_sha256":
                manifest_hash_valid,

            "body_sha256":
                body_hash_valid,

            "body_length":
                body_length_valid,

            "gc_core_principles":
                principles_valid,
        },

        "expected_manifest_sha256":
            expected,

        "actual_manifest_sha256":
            actual_manifest_sha256,

        "expected_body_sha256":
            manifest.body_sha256,

        "actual_body_sha256":
            actual_body_sha256,

        "status": (
            "CANONICAL_INTEGRITY_CONFIRMED"
            if passed
            else "FAIL_CLOSED"
        ),

        "scope": {
            "mathematical_core":
                "SEPARATE_VALIDATION_REQUIRED",

            "physical_validation":
                "NOT_PERFORMED",

            "independent_replication":
                manifest.independent_replication,

            "openai_official_certification":
                manifest.openai_official_certification,

            "guaranteed_eternal_storage":
                False,
        },
    }

    unsigned_report = stable_json(
        report
    )

    report[
        "report_sha256"
    ] = sha256_text(
        unsigned_report
    )

    atomic_write_text(
        report_path,

        json.dumps(
            report,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
    )

    print("=" * 78)
    print(f"{PRODUCT_NAME} v{VERSION}")
    print("=" * 78)

    for name, result in report[
        "checks"
    ].items():

        print(
            f"{name:24s}: "
            f"{'PASS' if result else 'FAIL'}"
        )

    print()
    print(
        "STATUS:",
        report["status"],
    )

    print(
        "REPORT:",
        report_path.resolve(),
    )

    return 0 if passed else 1


# =============================================================================
# 5. CLI
# =============================================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Pin or verify "
            "KINDRITHIA-CHARTER-PRACTICAL-1.003"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    pin_parser = subparsers.add_parser(
        "pin",
        help="Create the first immutable-candidate manifest",
    )

    pin_parser.add_argument(
        "--body",
        type=Path,
        required=True,
    )

    pin_parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
    )

    pin_parser.add_argument(
        "--source-commit",
        required=True,
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help="Fail-closed verification",
    )

    verify_parser.add_argument(
        "--body",
        type=Path,
        required=True,
    )

    verify_parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
    )

    verify_parser.add_argument(
        "--expected-manifest-sha256",
        default=os.environ.get(
            "KINDRITHIA_MANIFEST_SHA256"
        ),
    )

    verify_parser.add_argument(
        "--report",
        type=Path,
        default=Path(
            "kindrithia_canonical_verification.json"
        ),
    )

    return parser


def main() -> int:

    args = build_parser().parse_args()

    try:
        if args.command == "pin":
            return pin(
                args.body,
                args.manifest,
                args.source_commit,
            )

        if not args.expected_manifest_sha256:
            raise RuntimeError(
                "FAIL-CLOSED: provide "
                "--expected-manifest-sha256 or set "
                "KINDRITHIA_MANIFEST_SHA256"
            )

        return verify(
            args.body,
            args.manifest,
            args.expected_manifest_sha256,
            args.report,
        )

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        return 2


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
