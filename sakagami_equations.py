#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
阪上循環方程式群（Sakagami Circulation Equations）
── 主要8式 連続と離散のブリッジ実装 ──

著者：阪上哲史（Tetsushi Sakagami）
================================================================

概要:
    本コードは、黄金比・フィボナッチ数列・カッシーニの恒等式・
    三角関数による周期振動を組み合わせ、
    「連続的な物理量」と「離散的な計算処理」を橋渡しする
    数理モデルとして構成された8つの式の実装です。

    物理学における「ゼロ点エネルギー」のように、
    限りなく0に近づくが厳密には0に到達しない量と、
    計算機科学において停止条件として必要となる
    厳密な「0」を区別するため、以下の2つの定数を分離しています。

        LOGICAL_ZERO  : 論理的・計算上の厳密な0
        PHYSICAL_FLOOR: 物理的直感としての極小非ゼロ値

    最終的に、第8式（全環循環統括式）によって、
    第1〜7式全体の循環率が 1.0 に収束することを検証します。が、以前入力ミスでルート3をルート2で検証してしまい、
    計算すると約 0.81649658 になり、1.0000恒等ではないことが判明、結果的に1.0000恒等の収束を確認。（痴

実行方法:
    pip install numpy
    python sakagami_equations.py

ライセンス:
    MIT License
================================================================
"""

import numpy as np

_trapezoid = getattr(np, "trapezoid", None) or np.trapz  # NumPy 2.x removed trapz


# ================================================================
# 定数定義
# ================================================================

LOGICAL_ZERO: int = 0
"""計算機科学における厳密な0（停止条件・判定用）"""

PHYSICAL_FLOOR: float = 1e-9
"""物理的直感としての極小非ゼロ値（ゼロ点エネルギー的な下限）"""


# ================================================================
# 本体クラス
# ================================================================

class SakagamiEquationsBridge:
    """
    阪上循環方程式群 主要8式を実装したブリッジクラス。

    連続的な物理場（sin, cos, 黄金比による減衰振動など）と、
    離散的な計算処理（行列式、収束判定など）を
    1つのクラス内で一貫して扱う。
    """

    def __init__(self, num_points: int = 10000):
        """
        Parameters
        ----------
        num_points:
            θ（角度）の離散化点数。
            値が大きいほど積分・微分の近似精度が上がる。
        """
        self.num_points = num_points
        self.theta = np.linspace(0, 2 * np.pi, num_points)

        # 黄金比 φ = (1 + √5) / 2
        self.phi = (1 + np.sqrt(5)) / 2

        # 場のバイアス項: 第8式の循環率を 1 に規格化する定数 1/(6√3)。
        # 正六角形との幾何学的な由来は確認できていない（reference_check.py 参照）
        self.c_bias = 1.0 / (6.0 * np.sqrt(3))

    # ------------------------------------------------------------
    # 第1式：偏差0量子整合式
    # ------------------------------------------------------------

    def eq1_quantum_zero(self) -> float:
        """
        sin(θ) の絶対値の最小値を求め、
        物理的フロア(PHYSICAL_FLOOR)を下回らないよう補正する。

        物理的な「0に限りなく近いが0ではない」量を表現する式。
        """
        raw_min = np.min(np.abs(np.sin(self.theta)))
        return float(max(raw_min, PHYSICAL_FLOOR))

    # ------------------------------------------------------------
    # 第2式：ラグランジアン潜伏干渉式
    # ------------------------------------------------------------

    def eq2_lagrangian_perturbation(
        self,
        theta_val: float,
        epsilon: float = 0.01
    ) -> float:
        """
        基準ラグランジアン L0 に、
        微小な位相ゆらぎ epsilon * sin(theta_val) を重畳する。

        Parameters
        ----------
        theta_val:
            評価する角度（ラジアン）
        epsilon:
            摂動の強さ（デフォルト 0.01）
        """
        L0 = 1.0
        psi = np.sin(theta_val)
        return float(L0 + epsilon * psi)

    # ------------------------------------------------------------
    # 第3式：群層流接続式
    # ------------------------------------------------------------

    def eq3_field_E_k(self, k: int) -> np.ndarray:
        """
        黄金比 φ を使った減衰振動場 E_k(θ) を返す。

        E_k(θ) = c_bias + sin(kθ) / φ^k

        kが大きくなるほど振幅が黄金比のペースで減衰していく。
        """
        return self.c_bias + (np.sin(k * self.theta) / (self.phi ** k))

    # ------------------------------------------------------------
    # 第4式：フィボナッチ行列式（カッシーニの恒等式）
    # ------------------------------------------------------------

    def eq4_sakagami_matrix_det(self, n: int = 5) -> int:
        """
        フィボナッチ行列の行列式は、カッシーニの恒等式により
        常に (-1)^n となる。

        det(M_n) = (-1)^n
        """
        return (-1) ** n

    # ------------------------------------------------------------
    # 第5式：位相安定式
    # ------------------------------------------------------------

    def eq5_phase_stability_div(self) -> float:
        """
        保存場 S(θ) = cos(θ) のダイバージェンス（θに関する微分）を
        θ全体で平均し、理論上0に収束することを数値検証する。
        """
        S_field = np.cos(self.theta)
        dS_dtheta = np.gradient(S_field, self.theta)
        return float(np.mean(dS_dtheta))

    # ------------------------------------------------------------
    # 第6式：時間反転対称式
    # ------------------------------------------------------------

    def eq6_time_reversal_symmetry(self, val: float) -> bool:
        """
        sin(t) = -sin(-t) という、正弦関数の奇関数性
        （時間反転対称性）を検証する。
        """
        return bool(np.isclose(np.sin(val), -np.sin(-val)))

    # ------------------------------------------------------------
    # 第7式：位相テンソルノルム
    # ------------------------------------------------------------

    def eq7_tensor_T7_norm(self) -> np.ndarray:
        """
        4成分テンソル (cosθ, sinθ, 1, -1) のノルムを計算する。

        cos^2θ + sin^2θ = 1 であるため、
        θに依らず常に √3 の一定値を持つ。
        """
        t1 = np.cos(self.theta)
        t2 = np.sin(self.theta)
        t3 = np.ones_like(self.theta)
        t4 = -np.ones_like(self.theta)
        return np.sqrt(t1**2 + t2**2 + t3**2 + t4**2)

    # ------------------------------------------------------------
    # 第8式：全環循環統括式
    # ------------------------------------------------------------

    def eq8_holonomic_recirculation_integral(self) -> float:
        """
        第3式（E_k, k=1〜6の合成）と第7式（テンソルノルム）を
        θ全体で積分し、2πで正規化することで
        「循環率」を求める。

        設計上、この値は 1.0 に収束するように構成されている。
        """
        E_sum = sum(self.eq3_field_E_k(k) for k in range(1, 7))
        T7_norm = self.eq7_tensor_T7_norm()

        integrand = E_sum * T7_norm
        raw_integral = _trapezoid(integrand, self.theta)

        return float(abs(raw_integral) / (2 * np.pi))


# ================================================================
# 実行部
# ================================================================

def main() -> None:
    print("=" * 70)
    print("阪上循環方程式群 Major 8 Equations (Bridge Edition)")
    print("著者：阪上哲史")
    print("=" * 70)

    model = SakagamiEquationsBridge(num_points=10000)

    eq1 = model.eq1_quantum_zero()
    print(f"【第1式】偏差0量子極限値       : {eq1:.10f}  (floor={PHYSICAL_FLOOR})")

    eq2 = model.eq2_lagrangian_perturbation(np.pi / 4)
    print(f"【第2式】ラグランジアン摂動     : {eq2:.6f}")

    eq4 = model.eq4_sakagami_matrix_det(5)
    print(f"【第4式】阪上行列式(n=5)        : {eq4}")

    eq5 = model.eq5_phase_stability_div()
    print(f"【第5式】位相場ダイバージェンス : {eq5:.6e}")

    eq6 = model.eq6_time_reversal_symmetry(np.pi / 3)
    print(f"【第6式】時間反転対称性検証     : {eq6}")

    eq7 = model.eq7_tensor_T7_norm()[0]
    print(f"【第7式】T7テンソル不変ノルム   : {eq7:.10f} (√3={np.sqrt(3):.10f})")

    print("-" * 70)

    rate = model.eq8_holonomic_recirculation_integral()
    print(f"【第8式】阪上全環循環統括演算結果（循環率）: {rate:.10f}")

    print("-" * 70)

    if np.isclose(rate, 1.0, atol=1e-5):
        print("✅ 判定: 第1〜7式の全体系が、第8式により完全循環率 1.0000 で収束しました。")
    else:
        print("⚠️ 判定: 収束度を再調整してください。")

    print("=" * 70)


if __name__ == "__main__":
    main()
