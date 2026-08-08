#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
物流・倉庫空間統合スマート荷役コアライブラリ
(Smart Warehouse & Freight Optimization Core)

著者：阪上哲史 (Tetsushi Sakagami)
ライセンス：MIT License
================================================================
概要:
    トラック荷台(12ftコンテナ等)の動的重量バランス計算と、
    倉庫・保管庫(固定空間)における自動フォークリフト等の経路・積層安全計算を
    一元管理する統合データモデルおよび自律進化型最適化基盤。
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
    STANDARD = 0       # 通常物
    MOISTURE_SENSITIVE = 1 # 湿気影響あり (ダンボール強度低下等)
    FRAGILE = 2            # 緩衝・隙間確保必須 (精密・手荷役重視)


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
# 2. 自律調整・フィードバックログ (Optimization & Feedback)
# ============================================================

@dataclass
class OperationalFeedback:
    """現場手荷役・センサー補正値のフィードバック記録"""
    timestamp: str
    item_id: str
    pressure_adjusted: bool
    clearance_applied_cm: float
    notes: str


class HandlingOptimizationEngine:
    """現場フィードバックを蓄積し、積載・搬送パラメータを適応させる基盤"""

    def __init__(self):
        self.feedback_logs: List[OperationalFeedback] = []

    def record_manual_adjustment(self, item_id: str, clearance_cm: float, note: str) -> None:
        """繊細物や湿気段ボールに対する手動微調整結果の学習記録"""
        log = OperationalFeedback(
            timestamp=datetime.now().isoformat(),
            item_id=item_id,
            pressure_adjusted=True,
            clearance_applied_cm=clearance_cm,
            notes=note
        )
        self.feedback_logs.append(log)


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
        
        # 偏荷重チェック（前後15%, 左右10%以内の偏差）
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

    def execute_gentle_transfer(self, cargo: CargoItem, source: SpatialContainer, destination: SpatialContainer) -> bool:
        """非破壊・減速接地荷役"""
        # 繊細品・湿気品に対する隙間（クリアランス）補正
        clearance = 0.0
        if cargo.sensitivity != MaterialSensitivity.STANDARD:
            clearance = 0.05  # 5cm の安全離隔
            self.engine.record_manual_adjustment(
                cargo.item_id, 
                clearance_cm=5.0, 
                note=f"感度レベル {cargo.sensitivity.name} に基づき非接触クリアランスを確保"
            )

        print(f"📦 [搬送開始] {cargo.name} (重量: {cargo.weight_kg}kg, 才数: {cargo.volume_sai:.1f}才)")
        print(f"🚚 離隔補正: {clearance * 100:.1f} cm を適用して移動中...")
        
        # 荷物の積み換え
        if cargo in source.items:
            source.items.remove(cargo)
        destination.items.append(cargo)

        print(f"✅ [非破壊着地完了] {destination.container_id} へ配置完了")
        return True


# ============================================================
# 4. 実行サンプル
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("スマート物流・荷台＆倉庫統合シミュレータ (GitHub公開用基盤)")
    print("=" * 65)

    # 1. 空間の定義（トラック荷台と倉庫エリア）
    truck_deck = SpatialContainer(
        container_id="TRUCK-12FT-01",
        space_type=SpaceType.TRUCK_DECK,
        dimensions=Vector3D(x=6.0, y=2.3, z=2.2),
        max_payload_kg=5000.0
    )

    # 2. 荷物の定義（耐圧・手荷役感度含む）
    cargo1 = CargoItem(
        item_id="C001",
        name="12ftパレット荷物-精密部品",
        weight_kg=1200.0,
        dimensions=Vector3D(x=1.1, y=1.1, z=1.2),
        position=Vector3D(x=1.0, y=0.0, z=0.0),
        sensitivity=MaterialSensitivity.FRAGILE
    )

    cargo2 = CargoItem(
        item_id="C002",
        name="ダンボール詰商品(湿気影響考慮)",
        weight_kg=800.0,
        dimensions=Vector3D(x=1.1, y=1.1, z=1.0),
        position=Vector3D(x=3.5, y=0.0, z=0.0),
        sensitivity=MaterialSensitivity.MOISTURE_SENSITIVE
    )

    truck_deck.items.extend([cargo1, cargo2])

    # 3. フォークリフトナビゲータによる評価と積載実行
    navigator = SmartForkliftNavigator()
    eval_result = navigator.evaluate_space_and_load(truck_deck)

    print(f"対象空間        : {eval_result['container_id']}")
    print(f"総積載重量      : {eval_result['total_weight_kg']} kg ({eval_result['capacity_usage_percent']:.1f}%)")
    print(f"重心位置 (x,y,z): {eval_result['center_of_gravity']} m")
    print(f"安全判定        : {eval_result['status']}")
    print("-" * 65)

    # 4. 個別荷役の実行
    warehouse_bay = SpatialContainer(
        container_id="BAY-A1",
        space_type=SpaceType.WAREHOUSE_BAY,
        dimensions=Vector3D(x=10.0, y=10.0, z=5.0),
        max_payload_kg=20000.0
    )
    
    navigator.execute_gentle_transfer(cargo1, source=truck_deck, destination=warehouse_bay)
    print("=" * 65)
