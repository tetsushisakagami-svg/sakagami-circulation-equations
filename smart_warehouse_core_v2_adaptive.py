#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
物流・倉庫空間統合スマート荷役コアライブラリ
(Smart Warehouse & Freight Optimization Core - Adaptive Edition)

著者：阪上哲史 (Tetsushi Sakagami)
ライセンス：MIT License
バージョン：v2.0 (Adaptive)
================================================================
概要:
    トラック荷台(12ftコンテナ等)の動的重量バランス計算と、
    現場フィードバック（振動・歪み・手動補正）を蓄積・自己学習して
    クリアランスや搬送パラメータを自律適応（進化）させる最適化基盤。
================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# 1. 共通データ構造 (Data Classes)
# ============================================================

class SpaceType(Enum):
    """空間種別"""
    WAREHOUSE_BAY = "倉庫保管エリア"
    TRUCK_DECK = "トラック荷台"
    CONTAINER_12FT = "12ftコンテナ"


class MaterialSensitivity(Enum):
    """荷物の物理的特性レベル"""
    STANDARD = 0            # 通常物
    MOISTURE_SENSITIVE = 1  # 湿気影響あり (ダンボール強度低下等)
    FRAGILE = 2             # 緩衝・隙間確保必須 (精密・手荷役重視)


@dataclass
class Vector3D:
    """3次元位置・寸法ベクトル"""
    x: float  # 長さ (m)
    y: float  # 幅 (m)
    z: float  # 高さ (m)


@dataclass
class CargoItem:
    """荷物・パレットの統一データモデル"""
    item_id: str
    name: str
    weight_kg: float
    dimensions: Vector3D
    position: Vector3D  # 設置基準位置 (x, y, z)
    max_stack_weight_kg: float = 1000.0  # 許容耐圧(積層限界重量)
    sensitivity: MaterialSensitivity = MaterialSensitivity.STANDARD

    @property
    def volume_m3(self) -> float:
        """才数・容積計算用 (1 m3 ≈ 35.315 才)"""
        return self.dimensions.x * self.dimensions.y * self.dimensions.z

    @property
    def volume_sai(self) -> float:
        """才数換算"""
        return self.volume_m3 * 35.315


@dataclass
class SpatialContainer:
    """荷台・コンテナ・倉庫区画の空間データモデル"""
    container_id: str
    space_type: SpaceType
    dimensions: Vector3D
    max_payload_kg: float
    items: List[CargoItem] = field(default_factory=list)

    def calculate_total_weight(self) -> float:
        return sum(item.weight_kg for item in self.items)

    def calculate_center_of_gravity(self) -> Vector3D:
        """重心位置 (3次元) の算出"""
        total_w = self.calculate_total_weight()
        if total_w == 0:
            return Vector3D(self.dimensions.x / 2.0, self.dimensions.y / 2.0, 0.0)

        weighted_x = sum(item.weight_kg * (item.position.x + item.dimensions.x / 2.0) for item in self.items)
        weighted_y = sum(item.weight_kg * (item.position.y + item.dimensions.y / 2.0) for item in self.items)
        weighted_z = sum(item.weight_kg * (item.position.z + item.dimensions.z / 2.0) for item in self.items)

        return Vector3D(weighted_x / total_w, weighted_y / total_w, weighted_z / total_w)


# ============================================================
# 2. 自律進化・フィードバック学習エンジン (Adaptive Engine)
# ============================================================

@dataclass
class OperationalFeedback:
    """現場手荷役・センサー補正値のフィードバック記録"""
    timestamp: str
    item_id: str
    sensitivity: MaterialSensitivity
    vibration_detected: float   # 搬送時の最大振動値 (G)
    manual_clearance_cm: float  # 現場で手動補正されたクリアランス (cm)
    success: bool               # 荷崩れ・破損なく搬送できたか


class HandlingOptimizationEngine:
    """
    現場フィードバックを蓄積し、離隔距離(Clearance)や走行速度制御を
    強化学習的に進化・適応させるエンジン
    """

    def __init__(self):
        self.feedback_logs: List[OperationalFeedback] = []
        # 各特性ごとのベースライン離隔距離 (cm)
        self.adaptive_clearance_policy: Dict[MaterialSensitivity, float] = {
            MaterialSensitivity.STANDARD: 1.0,
            MaterialSensitivity.MOISTURE_SENSITIVE: 3.0,
            MaterialSensitivity.FRAGILE: 5.0
        }
        self.learning_rate: float = 0.1  # パラメータ適応率

    def record_and_evolve(self, feedback: OperationalFeedback) -> None:
        """
        過去の実行結果（振動、手動補正、成功判定）を記録し、
        今後の安全ポリシー（クリアランス規定値）を自律進化させる
        """
        self.feedback_logs.append(feedback)

        # 自律適応ロジック (フィードバックからのオンライン更新)
        current_policy = self.adaptive_clearance_policy[feedback.sensitivity]

        if not feedback.success or feedback.vibration_detected > 1.5:
            # 振動が大きい、または荷傷みリスクがあった場合：安全離隔を自動拡大 (進化)
            adjustment = max(feedback.manual_clearance_cm, current_policy * 1.2)
            new_policy = current_policy + self.learning_rate * (adjustment - current_policy)
            self.adaptive_clearance_policy[feedback.sensitivity] = round(new_policy, 2)
            print(f"🔄 [自律進化] {feedback.sensitivity.name} の安全クリアランスを {new_policy:.2f} cm に学習強化しました。")
        elif feedback.success and feedback.vibration_detected < 0.5:
            # 極めて安定している場合：無駄なデッドスペースを抑えるため微微減で効率化
            new_policy = max(1.0, current_policy - (self.learning_rate * 0.1))
            self.adaptive_clearance_policy[feedback.sensitivity] = round(new_policy, 2)

    def get_optimal_clearance(self, sensitivity: MaterialSensitivity) -> float:
        """学習結果に基づいた最適な離隔距離(cm)を取得"""
        return self.adaptive_clearance_policy.get(sensitivity, 2.0)


# ============================================================
# 3. 統合ナビゲーション & 荷役シミュレータ
# ============================================================

class SmartForkliftNavigator:
    """自律走行・安全着荷プロトタイプエンジン"""

    def __init__(self, forklift_id: str = "FL-01"):
        self.forklift_id = forklift_id
        self.current_position = Vector3D(0.0, 0.0, 0.0)
        self.engine = HandlingOptimizationEngine()

    def evaluate_space_and_load(self, target_space: SpatialContainer) -> Dict[str, Any]:
        """荷台・保管庫の安全判定"""
        total_weight = target_space.calculate_total_weight()
        cg = target_space.calculate_center_of_gravity()
        
        weight_safe = total_weight <= target_space.max_payload_kg
        
        center_x = target_space.dimensions.x / 2.0
        center_y = target_space.dimensions.y / 2.0
        x_offset = abs(cg.x - center_x)
        y_offset = abs(cg.y - center_y)

        balance_safe = (x_offset <= target_space.dimensions.x * 0.15) and (y_offset <= target_space.dimensions.y * 0.10)

        return {
            "container_id": target_space.container_id,
            "total_weight_kg": total_weight,
            "capacity_usage_percent": (total_weight / target_space.max_payload_kg) * 100.0,
            "center_of_gravity": (round(cg.x, 2), round(cg.y, 2), round(cg.z, 2)),
            "is_weight_safe": weight_safe,
            "is_balance_safe": balance_safe,
            "status": "SAFE" if (weight_safe and balance_safe) else "ATTENTION"
        }

    def execute_gentle_transfer(self, cargo: CargoItem, source: SpatialContainer, destination: SpatialContainer, measured_vibration: float = 0.8) -> bool:
        """非破壊・自律学習連動の荷役処理"""
        # 学習済みエンジンから動的な離隔補正量を取得
        clearance_cm = self.engine.get_optimal_clearance(cargo.sensitivity)

        print(f"📦 [搬送開始] {cargo.name} (重量: {cargo.weight_kg}kg, 才数: {cargo.volume_sai:.1f}才)")
        print(f"🚚 学習モデル適用離隔: {clearance_cm:.1f} cm (特性: {cargo.sensitivity.name})")
        
        # 移動処理
        if cargo in source.items:
            source.items.remove(cargo)
        destination.items.append(cargo)

        print(f"✅ [着地完了] {destination.container_id} へ配置完了")

        # 現場からの挙動データをフィードバックしてエンジンを学習・進化させる
        feedback = OperationalFeedback(
            timestamp=datetime.now().isoformat(),
            item_id=cargo.item_id,
            sensitivity=cargo.sensitivity,
            vibration_detected=measured_vibration,
            manual_clearance_cm=clearance_cm,
            success=True
        )
        self.engine.record_and_evolve(feedback)

        return True


# ============================================================
# 4. 実行サンプル
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("スマート物流・荷台＆倉庫統合シミュレータ (自律進化適応版 v2.0)")
    print("=" * 65)

    truck_deck = SpatialContainer(
        container_id="TRUCK-12FT-01",
        space_type=SpaceType.TRUCK_DECK,
        dimensions=Vector3D(x=6.0, y=2.3, z=2.2),
        max_payload_kg=5000.0
    )

    cargo_fragile = CargoItem(
        item_id="C001",
        name="12ftパレット荷物-精密機器",
        weight_kg=1200.0,
        dimensions=Vector3D(x=1.1, y=1.1, z=1.2),
        position=Vector3D(x=1.0, y=0.0, z=0.0),
        sensitivity=MaterialSensitivity.FRAGILE
    )

    truck_deck.items.append(cargo_fragile)
    navigator = SmartForkliftNavigator()

    warehouse_bay = SpatialContainer(
        container_id="BAY-A1",
        space_type=SpaceType.WAREHOUSE_BAY,
        dimensions=Vector3D(x=10.0, y=10.0, z=5.0),
        max_payload_kg=20000.0
    )

    # 1回目の搬送（初期学習状態）
    print("\n🚚 1回目の搬送実行（初期状態、高振動を検知）")
    navigator.execute_gentle_transfer(cargo_fragile, truck_deck, warehouse_bay, measured_vibration=1.8)
    
    print("-" * 65)
    # 2回目の同種荷物搬送（1回目の高振動フィードバックを受けてクリアランスが拡大進化）
    print("\n🚚 2回目の搬送実行（学習進化後、低振動）")
    navigator.execute_gentle_transfer(cargo_fragile, warehouse_bay, truck_deck, measured_vibration=0.4)
    print("=" * 65)
