#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既知の数学的恒等式との照合チェック（Reference Check）

阪上循環方程式群の各式が依拠している、学術的に確立した恒等式・定理と
一致するかを、独立した方法（整数の厳密計算、解析解、別解像度）で検証し、
結果を JSON Lines 形式でログに追記する。

注意:
- 検証できるのは「各式の数値実装が、引用した既知の恒等式と一致するか」まで。
- 式そのものの物理的妥当性や、新規性の証明ではない。
- 定義値（定数の選び方など）で、既知の定数との対応が確認できないものは
  status を "UNVERIFIED" として残す（合格扱いにしない）。
"""

import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List

import numpy as np

from sakagami_equations import SakagamiEquationsBridge

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "reference_check.jsonl"
TOL = 1e-9


def _fib_matrix_power(n: int):
    """整数のみで [[1,1],[1,0]]^n を計算（誤差なし）。"""
    result = [[1, 0], [0, 1]]
    base = [[1, 1], [1, 0]]

    def mul(a, b):
        return [
            [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
            [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]],
        ]

    for _ in range(n):
        result = mul(result, base)
    return result


def check_cassini(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第4式: カッシーニの恒等式 det([[1,1],[1,0]]^n) = (-1)^n を整数で直接確認。"""
    bad: List[int] = []
    for n in range(1, 61):
        m = _fib_matrix_power(n)
        det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        if det != (-1) ** n or model.eq4_sakagami_matrix_det(n) != det:
            bad.append(n)
    return {
        "reference": "Cassini's identity (Cassini, 1680): F(n+1)F(n-1) - F(n)^2 = (-1)^n",
        "detail": "n=1..60 を整数行列の行列式で厳密確認し、第4式の返り値と一致",
        "passed": not bad,
        "mismatches": bad,
    }


def check_golden_ratio(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第3式の φ: 黄金比 φ^2 = φ + 1、およびビネの公式で F(n) と一致。"""
    phi = model.phi
    err_eq = abs(phi**2 - (phi + 1))
    fibs = [0, 1]
    for _ in range(40):
        fibs.append(fibs[-1] + fibs[-2])
    max_binet_err = max(abs(round((phi**n - (-phi) ** (-n)) / np.sqrt(5)) - fibs[n]) for n in range(1, 41))
    return {
        "reference": "Golden ratio: phi^2 = phi + 1; Binet's formula F(n) = (phi^n - (-phi)^-n)/sqrt(5)",
        "detail": f"|phi^2-(phi+1)|={err_eq:.2e}, Binetとn=1..40の不一致={max_binet_err}",
        "passed": bool(err_eq < TOL and max_binet_err == 0),
    }


def check_pythagorean_tensor(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第7式: cos^2+sin^2=1 により、ノルムが sqrt(3) で一定。"""
    norms = model.eq7_tensor_T7_norm()
    err = float(np.max(np.abs(norms - np.sqrt(3))))
    return {
        "reference": "Pythagorean trigonometric identity: sin^2 + cos^2 = 1",
        "detail": f"max|norm - sqrt(3)| = {err:.2e}",
        "passed": bool(err < TOL),
    }


def check_odd_function(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第6式: sin は奇関数。多数の点で第6式が True を返すか確認。"""
    vals = np.linspace(-10, 10, 2001)
    ok = all(model.eq6_time_reversal_symmetry(float(v)) for v in vals)
    return {
        "reference": "sin is an odd function: sin(-x) = -sin(x)",
        "detail": "x in [-10,10] の2001点",
        "passed": bool(ok),
    }


def check_trig_orthogonality(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第3・8式: ∫0..2π sin(kθ)dθ = 0（三角関数の直交性）を、第3式と別の解像度で確認。"""
    theta = np.linspace(0, 2 * np.pi, 200001)
    worst = max(abs(float(np.trapezoid(np.sin(k * theta), theta) if hasattr(np, "trapezoid") else np.trapz(np.sin(k * theta), theta))) for k in range(1, 7))
    return {
        "reference": "Orthogonality of trigonometric functions: integral of sin(k*theta) over [0, 2*pi] = 0",
        "detail": f"k=1..6, max|integral| = {worst:.2e}",
        "passed": bool(worst < TOL),
    }


def check_derivative_of_cos(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第5式: d/dθ cos θ = -sin θ、およびその周期平均が 0。"""
    theta = model.theta
    num = np.gradient(np.cos(theta), theta)
    err = float(np.max(np.abs(num[1:-1] + np.sin(theta[1:-1]))))
    mean_val = model.eq5_phase_stability_div()
    return {
        "reference": "d/dtheta cos(theta) = -sin(theta); periodic mean of derivative = [cos(2pi)-cos(0)]/(2pi) = 0",
        "detail": f"内部点の最大差={err:.2e} (離散化誤差), 第5式の平均={mean_val:.2e}",
        "passed": bool(err < 1e-6 and abs(mean_val) < TOL),
    }


def check_eq8_by_construction(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """第8式: 解析解は 6*c_bias*sqrt(3)。sin 項は直交性で消えるので定数項のみで決まる。"""
    analytic = float(Fraction(6, 1) * (1.0 / (6.0 * np.sqrt(3))) * np.sqrt(3))
    value = model.eq8_holonomic_recirculation_integral()
    err = abs(value - analytic)
    return {
        "reference": "Orthogonality + definition of c_bias: result = 6 * c_bias * sqrt(3)",
        "detail": (
            f"数値={value:.12f}, 解析解={analytic:.12f}, 差={err:.2e}。"
            "注意: 結果が1になるのは c_bias=1/(6*sqrt(3)) という定数の選び方によるもので、"
            "独立した法則から導かれた値ではない（定義による構成）。"
        ),
        "passed": bool(err < TOL),
    }


def check_c_bias_origin(model: SakagamiEquationsBridge) -> Dict[str, Any]:
    """c_bias=1/(6√3) と、既知の正六角形の定数との対応は確認できない。"""
    return {
        "reference": "正六角形の面積 (3*sqrt(3)/2)*s^2 などとの対応（コメントの『正六角形の面積定数由来』）",
        "detail": (
            f"c_bias={model.c_bias:.12f}。1/(6*sqrt(3)) = 1/(4*A)（A=単位正六角形の面積 3*sqrt(3)/2）"
            "という関係はあるが、これを標準的な既知法則として引用できる根拠は確認できていない。"
        ),
        "passed": None,
    }


CHECKS: List[Callable[[SakagamiEquationsBridge], Dict[str, Any]]] = [
    check_cassini,
    check_golden_ratio,
    check_pythagorean_tensor,
    check_odd_function,
    check_trig_orthogonality,
    check_derivative_of_cos,
    check_eq8_by_construction,
    check_c_bias_origin,
]


def run_reference_check(num_points: int = 10000, log_file: Path = LOG_FILE) -> Dict[str, Any]:
    model = SakagamiEquationsBridge(num_points)
    now = datetime.now(timezone.utc).isoformat()
    entries = []
    for fn in CHECKS:
        try:
            res = fn(model)
            status = "UNVERIFIED" if res["passed"] is None else ("MATCH" if res["passed"] else "MISMATCH")
        except Exception as exc:  # 検証自体の失敗も記録する
            res = {"reference": "-", "detail": f"{type(exc).__name__}: {exc}", "passed": False}
            status = "ERROR"
        entries.append({"timestamp": now, "check": fn.__name__, "status": status, **res})

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")

    summary = {
        "timestamp": now,
        "match": sum(e["status"] == "MATCH" for e in entries),
        "mismatch": sum(e["status"] in ("MISMATCH", "ERROR") for e in entries),
        "unverified": sum(e["status"] == "UNVERIFIED" for e in entries),
        "entries": entries,
    }
    return summary


if __name__ == "__main__":
    s = run_reference_check()
    for e in s["entries"]:
        print(f"[{e['status']:10}] {e['check']}: {e['detail']}")
    print(f"\nMATCH={s['match']} MISMATCH/ERROR={s['mismatch']} UNVERIFIED={s['unverified']}")
    print(f"log: {LOG_FILE}")
    sys.exit(1 if s["mismatch"] else 0)
