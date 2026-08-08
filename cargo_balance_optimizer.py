#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
トラック荷役・12ftコンテナ重量バランスシミュレータ
(Cargo Load & Axle Balance Optimizer)

著者：阪上哲史 (Tetsushi Sakagami)
ライセンス：MIT License
================================================================
概要:
    トラック荷台および12ftコンテナ両積み等の積載作業において、
    前後・左右の重量バランスおよび最大積載量に対する余裕度を
    数値計算・グラフィック判定する安全運行支援ライブラリ。
================================================================
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CargoItem:
    """荷物データ構造"""
    name: str
    weight_kg: float
    position_x_m: float  # 前後位置（車両前方を0mとする）
    position_y_m: float  # 左右位置（中央を0m、右を正、左を負とする）


class CargoBalanceSimulator:
    """荷台重量バランスおよび安全限界評価クラス"""

    def __init__(self, max_payload_kg: float, deck_length_m: float, deck_width_m: float):
        self.max_payload_kg = max_payload_kg
        self.deck_length_m = deck_length_m
        self.deck_width_m = deck_width_m
        self.items: List[CargoItem] = []

    def add_cargo(self, name: str, weight_kg: float, pos_x: float, pos_y: float) -> None:
        """荷物の追加"""
        if pos_x < 0 or pos_x > self.deck_length_m:
            raise ValueError(f"位置 X ({pos_x}m) が荷台の長さ範囲外です。")
        if abs(pos_y) > (self.deck_width_m / 2.0):
            raise ValueError(f"位置 Y ({pos_y}m) が荷台の幅範囲外です。")
        
        self.items.append(CargoItem(name, weight_kg, pos_x, pos_y))

    def calculate_total_weight(self) -> float:
        """総積載重量の計算"""
        return sum(item.weight_kg for item in self.items)

    def calculate_center_of_gravity(self) -> Tuple[float, float]:
        """重心位置（X: 前後, Y: 左右）の算出"""
        total_weight = self.calculate_total_weight()
        if total_weight == 0:
            return (self.deck_length_m / 2.0, 0.0)

        weighted_x = sum(item.weight_kg * item.position_x_m for item in self.items)
        weighted_y = sum(item.weight_kg * item.position_y_m for item in self.items)

        cg_x = weighted_x / total_weight
        cg_y = weighted_y / total_weight
        return (cg_x, cg_y)

    def evaluate_safety_status(self) -> dict:
        """安全基準評価の判定"""
        total_weight = self.calculate_total_weight()
        cg_x, cg_y = self.calculate_center_of_gravity()
        
        # 許容範囲の設定（重心が荷台中央からどれくらい偏っているか）
        center_x = self.deck_length_m / 2.0
        x_offset = abs(cg_x - center_x)
        y_offset = abs(cg_y)

        is_weight_safe = total_weight <= self.max_payload_kg
        is_balance_safe = (x_offset <= self.deck_length_m * 0.15) and (y_offset <= self.deck_width_m * 0.1)

        return {
            "total_weight_kg": total_weight,
            "weight_capacity_rate": (total_weight / self.max_payload_kg) * 100.0,
            "center_of_gravity_x_m": cg_x,
            "center_of_gravity_y_m": cg_y,
            "is_weight_safe": is_weight_safe,
            "is_balance_safe": is_balance_safe,
            "overall_status": "良好 (SAFE)" if (is_weight_safe and is_balance_safe) else "要再調整 (WARNING)"
        }


def main():
    print("=" * 60)
    print("トラック荷役・重量バランスシミュレータ")
    print("=" * 60)

    # 12ftコンテナ積載等を想定したパラメータ（例：最大積載量 5,000kg、荷台長 6.0m、幅 2.3m）
    sim = CargoBalanceSimulator(max_payload_kg=5000.0, deck_length_m=6.0, deck_width_m=2.3)

    # 荷物の積み込み例 (12ftコンテナ2個積み想定)
    sim.add_cargo(name="12ftコンテナ-前棟", weight_kg=2200.0, pos_x=1.8, pos_y=0.0)
    sim.add_cargo(name="12ftコンテナ-後棟", weight_kg=2300.0, pos_x=4.2, pos_y=0.05)

    # 評価実行
    result = sim.evaluate_safety_status()

    print(f"総積載重量      : {result['total_weight_kg']:.1f} kg / {sim.max_payload_kg:.1f} kg ({result['weight_capacity_rate']:.1f}%)")
    print(f"重心位置 (前後) : 荷台前頭から {result['center_of_gravity_x_m']:.2f} m (荷台長: {sim.deck_length_m}m)")
    print(f"重心位置 (左右) : 荷台中央から {result['center_of_gravity_y_m']:.2f} m (＋:右偏重 / －:左偏重)")
    print("-" * 60)
    print(f"判定結果        : {result['overall_status']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
