#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
持続可能環境・資源循環統合制御コアライブラリ
(Eco-Circulation & Resource Optimization Core)

著者：阪上哲史 (Tetsushi Sakagami)
ライセンス：MIT License
================================================================
概要:
    気候変動リスクおよび資源消費データのリアルタイム解析を行い、
    地域コミュニティにおけるエネルギー分散最適化と資源再循環（リサイクル・
    自動保全）のスケジューリングを自律的に制御するシステム基盤。
================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
from typing import Any, Dict, List, Optional


# ============================================================
# 1. 領域・資源データモデル (Data Models)
# ============================================================

class EnergySourceType(Enum):
    """エネルギー源種別"""
    SOLAR = "太陽光"
    WIND = "風力"
    HYDRO = "小水力"
    RECYCLED_BIOMASS = "バイオマス・循環熱"


class ResourceCategory(Enum):
    """循環資源カテゴリー"""
    WATER = "水資源"
    ORGANIC_WASTE = "有機廃棄物・堆肥化資源"
    CRITICAL_METALS = "希少金属・電子部品"
    PACKAGING_MATERIAL = "梱包・物流資材"


@dataclass
class EnvironmentalNode:
    """地域環境モニタリングノード"""
    node_id: str
    region_name: str
    co2_ppm: float
    soil_moisture_percent: float
    temperature_celsius: float
    solar_irradiance_kw_m2: float


@dataclass
class EnergyGridStatus:
    """地域スマートグリッド状態"""
    grid_id: str
    current_generation_kw: float
    current_demand_kw: float
    storage_capacity_percent: float

    @property
    def energy_balance_kw(self) -> float:
        """余剰/不足エネルギーの算出"""
        return self.current_generation_kw - self.current_demand_kw


# ============================================================
# 2. 自律循環・気候適応最適化エンジン (Optimization Engine)
# ============================================================

class EcoCirculationEngine:
    """
    環境計測データとエネルギー収支に基づき、
    自動保全アクション（灌水・蓄電・資源回収）を決定する最適化エンジン
    """

    def __init__(self, target_sustainability_index: float = 0.95):
        self.target_index = target_sustainability_index
        self.action_logs: List[Dict[str, Any]] = []

    def evaluate_environmental_health(self, node: EnvironmentalNode) -> Dict[str, Any]:
        """環境状態の診断と保全アラートの算出"""
        needs_irrigation = node.soil_moisture_percent < 30.0
        high_emissions = node.co2_ppm > 450.0

        health_score = 100.0
        if needs_irrigation:
            health_score -= 20.0
        if high_emissions:
            health_score -= 15.0

        return {
            "node_id": node.node_id,
            "region": node.region_name,
            "health_score": max(0.0, health_score),
            "action_required": "IRRIGATION_AND_GREENING" if needs_irrigation else "MONITORING_NORMAL",
            "is_stable": health_score >= 80.0
        }

    def optimize_microgrid_distribution(self, grid: EnergyGridStatus) -> Dict[str, Any]:
        """再エネ蓄電および分散配送の最適化指示"""
        balance = grid.energy_balance_kw
        recommendation = ""

        if balance > 0:
            if grid.storage_capacity_percent < 95.0:
                recommendation = f"余剰電力 {balance:.1f} kW を地域蓄電池へ充電指示"
            else:
                recommendation = f"余剰電力 {balance:.1f} kW を水素生成・資源リサイクルプラントへ分配"
        else:
            recommendation = f"不足電力 {abs(balance):.1f} kW に対して蓄電・バイオマス発電からの補給を実施"

        return {
            "grid_id": grid.grid_id,
            "balance_kw": round(balance, 2),
            "storage_status": f"{grid.storage_capacity_percent:.1f}%",
            "control_instruction": recommendation
        }


# ============================================================
# 3. 実行サンプル (Execution Example)
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("持続可能環境・資源循環統合制御シミュレーション")
    print("=" * 65)

    # 1. 環境モニタリングノードの定義
    monitoring_node = EnvironmentalNode(
        node_id="ENV-NODE-001",
        region_name="近郊保全緑地ドメイン",
        co2_ppm=412.5,
        soil_moisture_percent=26.5,  # 散水が必要な状態
        temperature_celsius=24.0,
        solar_irradiance_kw_m2=0.85
    )

    # 2. マイクログリッド状態の定義
    local_grid = EnergyGridStatus(
        grid_id="GRID-WEST-01",
        current_generation_kw=1200.0,
        current_demand_kw=850.0,
        storage_capacity_percent=88.0
    )

    # 3. エンジンの実行
    engine = EcoCirculationEngine()

    env_result = engine.evaluate_environmental_health(monitoring_node)
    grid_result = engine.optimize_microgrid_distribution(local_grid)

    print(f"対象地域          : {env_result['region']} ({env_result['node_id']})")
    print(f"環境健全性スコア  : {env_result['health_score']:.1f} / 100.0")
    print(f"推論アクション    : {env_result['action_required']}")
    print("-" * 65)
    print(f"電力グリッドID    : {grid_result['grid_id']}")
    print(f"エネルギー収支    : {grid_result['balance_kw']} kW")
    print(f"制御指示          : {grid_result['control_instruction']}")
    print("=" * 65)
