# 持続可能環境・資源循環統合制御コアライブラリ
## Eco-Circulation & Resource Optimization Core

著者：阪上哲史 (Tetsushi Sakagami)  
バージョン：v1.0 (Basic Edition)  
ライセンス：MIT License

---

## 概要

**環境保全&資源循環スマート基盤** は、気候変動リスクと資源消費データをリアルタイムで解析し、地域コミュニティにおけるエネルギー分散最適化と資源再循環（リサイクル・自動保全）を自律的に制御するシステム基盤です。

### 🌍 対応する課題

- 🌱 **気候変動への適応** - CO₂濃度、温度、湿度のリアルタイム監視
- ⚡ **再生可能エネルギーの最適配分** - 太陽光・風力・小水力・バイオマスの統合管理
- ♻️ **資源循環と自動保全** - 水資源、有機廃棄物、希少金属の効率的再利用
- 🏘️ **地域レジリエンス向上** - コミュニティ単位での自立・分散型システム構築

---

## 主な機能

### ✅ 環境モニタリング
- **リアルタイム計測** - CO₂濃度、土壌水分、気温、日射量を自動監視
- **環境健全性診断** - 計測データから健全性スコア（0-100）を算出
- **保全アラート** - 灌水・緑化・排出削減などのアクションを自動提案

### ✅ マイクログリッド最適化
- **再エネ発電量の追跡** - 太陽光・風力・水力などの発電リアルタイム管理
- **需給バランス自動制御** - 余剰電力の蓄電・分配、不足時の補給を自動判断
- **水素生成・資源プラント連携** - 余剰エネルギーの有効活用

### ✅ 資源循環マネジメント
- **水資源最適化** - 土壌水分に応じた灌水スケジューリング
- **有機廃棄物・堆肥化** - 廃棄物から栄養豊富な堆肥への自動転換
- **希少金属・電子部品回収** - 廃棄物からの有価物抽出と再利用
- **梱包材料の循環** - 物流資材の再利用スケジュール管理

---

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/tetsushisakagami-svg/sakagami-circulation-equations.git
cd sakagami-circulation-equations

# eco-circulation-core ブランチに切り替え
git checkout eco-circulation-core
```

## 使用方法

### 基本的な使い方

```python
from eco_circulation_core import (
    EnvironmentalNode, EnergyGridStatus,
    EcoCirculationEngine
)

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
    current_generation_kw=1200.0,  # 発電量
    current_demand_kw=850.0,       # 需要
    storage_capacity_percent=88.0   # 蓄電池残量
)

# 3. エンジンの実行
engine = EcoCirculationEngine()

# 環境診断
env_result = engine.evaluate_environmental_health(monitoring_node)
print(f"環境健全性: {env_result['health_score']}")
print(f"アクション: {env_result['action_required']}")

# グリッド最適化
grid_result = engine.optimize_microgrid_distribution(local_grid)
print(f"制御指示: {grid_result['control_instruction']}")
```

### 実行

```bash
python eco_circulation_core.py
```

出力例：

```
=================================================================
持続可能環境・資源循環統合制御シミュレーション
=================================================================
対象地域          : 近郊保全緑地ドメイン (ENV-NODE-001)
環境健全性スコア  : 65.0 / 100.0
推論アクション    : IRRIGATION_AND_GREENING
-----------------------------------------------------------------
電力グリッドID    : GRID-WEST-01
エネルギー収支    : 350.0 kW
制御指示          : 余剰電力 350.0 kW を地域蓄電池へ充電指示
=================================================================
```

---

## API リファレンス

### データクラス

#### `EnvironmentalNode`
地域環境モニタリングノードの状態を表現

**属性：**
- `node_id: str` - ノード識別子（例：ENV-NODE-001）
- `region_name: str` - 対象地域名
- `co2_ppm: float` - CO₂濃度（ppm）
- `soil_moisture_percent: float` - 土壌水分（%）
- `temperature_celsius: float` - 気温（℃）
- `solar_irradiance_kw_m2: float` - 日射量（kW/m²）

#### `EnergyGridStatus`
地域スマートグリッドの状態を表現

**属性：**
- `grid_id: str` - グリッド識別子（例：GRID-WEST-01）
- `current_generation_kw: float` - 現在発電量（kW）
- `current_demand_kw: float` - 現在需要（kW）
- `storage_capacity_percent: float` - 蓄電池残量（%）

**プロパティ：**
- `energy_balance_kw: float` - エネルギー収支（発電 - 需要）

### クラス

#### `EcoCirculationEngine`
環境計測とエネルギー最適化のメインエンジン

**メソッド：**

**`evaluate_environmental_health(node: EnvironmentalNode) -> Dict`**
- 環境ノードの健全性を診断
- 返値：
  - `health_score` (0-100) - 環境健全性スコア
  - `action_required` - 推奨アクション（IRRIGATION_AND_GREENING / MONITORING_NORMAL）
  - `is_stable` - 安定状態か判定（True: score >= 80）

**`optimize_microgrid_distribution(grid: EnergyGridStatus) -> Dict`**
- マイクログリッドの最適配分を計算
- 返値：
  - `balance_kw` - エネルギー収支（kW）
  - `storage_status` - 蓄電池状態（%）
  - `control_instruction` - 制御指示（テキスト）

---

## ライセンス

このプロジェクトは **MIT ライセンス** の下で公開されています。

---

## 作者・連絡先

- **阪上哲史 (Tetsushi Sakagami)**
- GitHub: [@tetsushisakagami-svg](https://github.com/tetsushisakagami-svg)

ご質問や改善提案は、GitHub Issues でお気軽にお寄せください。💓😊
