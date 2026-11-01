#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検証付き演算モジュール（Verified Compute）

阪上循環方程式群（sakagami_equations.py）の数値計算結果を、
(1) 解析解との照合、(2) 解像度を上げたときの収束確認、
の2段階で検証し、実測した誤差とともに返す。

固定値の合否表示は行わない。status は実測誤差と許容誤差の比較で決まる。
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List

import numpy as np

from sakagami_equations import SakagamiEquationsBridge

DEFAULT_TOLERANCE = 1e-6
MIN_POINTS = 100
MAX_POINTS = 5_000_000


class InvalidInputError(ValueError):
    """入力値が不正な場合の例外。"""


@dataclass
class VerifiedResult:
    name: str
    value: float
    reference: float
    abs_error: float
    tolerance: float
    converged: bool
    status: str  # "VERIFIED" or "FAILED"
    num_points: int
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _validate_points(num_points: int) -> int:
    if isinstance(num_points, bool) or not isinstance(num_points, int):
        raise InvalidInputError("num_points must be an integer")
    if not (MIN_POINTS <= num_points <= MAX_POINTS):
        raise InvalidInputError(
            f"num_points must be between {MIN_POINTS} and {MAX_POINTS}"
        )
    return num_points


def _validate_tolerance(tolerance: float) -> float:
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise InvalidInputError("tolerance must be a number")
    if not (0 < tolerance < 1):
        raise InvalidInputError("tolerance must satisfy 0 < tolerance < 1")
    return float(tolerance)


def analytic_circulation_rate() -> float:
    """
    第8式の解析解。

    ∫0..2π sin(kθ) dθ = 0 (k は 1 以上の整数) なので
    循環率 = (1/2π) * (6 * c_bias) * √3 * 2π = 6 * (1/(6√3)) * √3 = 1
    """
    c_bias = 1.0 / (6.0 * np.sqrt(3))
    return float(6.0 * c_bias * np.sqrt(3))


def verify_circulation_rate(
    num_points: int = 10000,
    tolerance: float = DEFAULT_TOLERANCE,
) -> VerifiedResult:
    """第8式（循環率）を計算し、解析解と収束で検証する。"""
    num_points = _validate_points(num_points)
    tolerance = _validate_tolerance(tolerance)

    value = SakagamiEquationsBridge(num_points).eq8_holonomic_recirculation_integral()
    reference = analytic_circulation_rate()
    abs_error = abs(value - reference)

    # 点数を2倍にしても誤差が悪化しないことを確認する
    fine_points = min(num_points * 2, MAX_POINTS)
    fine_value = SakagamiEquationsBridge(fine_points).eq8_holonomic_recirculation_integral()
    fine_error = abs(fine_value - reference)
    converged = fine_error <= max(abs_error, tolerance)

    ok = bool(abs_error <= tolerance and converged and np.isfinite(value))
    return VerifiedResult(
        name="eq8_circulation_rate",
        value=float(value),
        reference=reference,
        abs_error=float(abs_error),
        tolerance=tolerance,
        converged=converged,
        status="VERIFIED" if ok else "FAILED",
        num_points=num_points,
        notes=f"fine_points={fine_points}, fine_error={fine_error:.3e}",
    )


def verify_tensor_norm(
    num_points: int = 10000,
    tolerance: float = DEFAULT_TOLERANCE,
) -> VerifiedResult:
    """第7式（テンソルノルム）が √3 で一定であることを検証する。"""
    num_points = _validate_points(num_points)
    tolerance = _validate_tolerance(tolerance)

    norms = SakagamiEquationsBridge(num_points).eq7_tensor_T7_norm()
    reference = float(np.sqrt(3))
    abs_error = float(np.max(np.abs(norms - reference)))
    ok = bool(abs_error <= tolerance and np.all(np.isfinite(norms)))
    return VerifiedResult(
        name="eq7_tensor_norm",
        value=float(np.mean(norms)),
        reference=reference,
        abs_error=abs_error,
        tolerance=tolerance,
        converged=True,
        status="VERIFIED" if ok else "FAILED",
        num_points=num_points,
    )


def verify_phase_stability(
    num_points: int = 10000,
    tolerance: float = DEFAULT_TOLERANCE,
) -> VerifiedResult:
    """第5式（位相場の発散平均）が 0 になることを検証する。"""
    num_points = _validate_points(num_points)
    tolerance = _validate_tolerance(tolerance)

    value = SakagamiEquationsBridge(num_points).eq5_phase_stability_div()
    abs_error = abs(value - 0.0)
    ok = bool(abs_error <= tolerance and np.isfinite(value))
    return VerifiedResult(
        name="eq5_phase_stability",
        value=float(value),
        reference=0.0,
        abs_error=float(abs_error),
        tolerance=tolerance,
        converged=True,
        status="VERIFIED" if ok else "FAILED",
        num_points=num_points,
    )


def run_verified_suite(
    num_points: int = 10000,
    tolerance: float = DEFAULT_TOLERANCE,
) -> Dict[str, Any]:
    """全検証を実行し、実測値だけから成るレポートを返す。"""
    results: List[VerifiedResult] = [
        verify_circulation_rate(num_points, tolerance),
        verify_tensor_norm(num_points, tolerance),
        verify_phase_stability(num_points, tolerance),
    ]
    return {
        "all_verified": all(r.status == "VERIFIED" for r in results),
        "results": [r.to_dict() for r in results],
    }


if __name__ == "__main__":
    import json
    import sys

    report = run_verified_suite()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["all_verified"] else 1)
