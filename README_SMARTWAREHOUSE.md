# スマート物流・倉庫空間統合荷役基盤
## Smart Warehouse & Freight Optimization Core

著者：阪上哲史 (Tetsushi Sakagami)

---

## 概要

トラック荷台（12ftコンテナ等）の動的重量バランス計算と、倉庫・保管庫（固定空間）における自動フォークリフト等の経路・積層安全計算を一元管理する統合データモデルおよび自律進化型最適化基盤です。

物流センター、倉庫運用、トラック積載作業における **安全性と効率性** を両立させるための計算エンジンとして設計されています。

---

## 主な機能

### ✅ 統合空間管理
- **トラック荷台** の3次元荷重バランス計算
- **倉庫保管エリア** の積層安全性評価
- **12ftコンテナ** の容積・重量最適化

### ✅ 荷物特性の考慮
- 標準物、湿気感応物、繊細品の分類
- 材質別の積層限界重量（耐圧）管理
- 才数（立方メートル）換算による効率計算

### ✅ 3次元重心計算
- 前後（X）方向の重心位置算出
- 左右（Y）方向の偏荷重判定
- 高さ（Z）方向の積層バランス評価

### ✅ 自動安全判定
- 総積載重量の収容量チェック
- 偏荷重基準（前後±15%、左右±10%）の自動判定
- 総合ステータス判定（SAFE / ATTENTION）

### ✅ 非破壊荷役サポート
- 繊細品・湿気品に対する自動クリアランス補正
- フォークリフト操作の最適化提示
- 現場フィードバックの記録と学習

---

## インストール

本ライブラリは Python 3.8 以上で動作します。標準ライブラリのみを使用しているため、追加のインストール不要です。

```bash
# リポジトリをクローン
git clone https://github.com/tetsushisakagami-svg/sakagami-circulation-equations.git
cd sakagami-circulation-equations

# smart-warehouse-core ブランチに切り替え
git checkout smart-warehouse-core
```

## 使用方法

### 基本的な使い方

```python
from smart_warehouse_core import (
    SpatialContainer, CargoItem, Vector3D,
    SpaceType, MaterialSensitivity, SmartForkliftNavigator
)

# 1. トラック荷台の定義
truck_deck = SpatialContainer(
    container_id="TRUCK-12FT-01",
    space_type=SpaceType.TRUCK_DECK,
    dimensions=Vector3D(x=6.0, y=2.3, z=2.2),  # 長さ × 幅 × 高さ
    max_payload_kg=5000.0
)

# 2. 荷物の定義（精密部品の例）
cargo = CargoItem(
    item_id="C001",
    name="精密部品パレット",
    weight_kg=1200.0,
    dimensions=Vector3D(x=1.1, y=1.1, z=1.2),
    position=Vector3D(x=1.0, y=0.0, z=0.0),
    sensitivity=MaterialSensitivity.FRAGILE
)

truck_deck.items.append(cargo)

# 3. フォークリフトナビゲータによる評価
navigator = SmartForkliftNavigator()
result = navigator.evaluate_space_and_load(truck_deck)

print(f"安全判定: {result['status']}")
print(f"容量使用率: {result['capacity_usage_percent']:.1f}%")
print(f"重心位置: {result['center_of_gravity']}")
```

### 実行

```bash
python smart_warehouse_core.py
```

出力例：

```
=================================================================
スマート物流・荷台＆倉庫統合シミュレータ (GitHub公開用基盤)
=================================================================
対象空間        : TRUCK-12FT-01
総積載重量      : 2000.0 kg (40.0%)
重心位置 (x,y,z): (2.83, 0.0, 0.85) m
安全判定        : SAFE
-----------------------------------------------------------------
📦 [搬送開始] 12ftパレット荷物-精密部品 (重量: 1200kg, 才数: 4.1才)
🚚 離隔補正: 5.0 cm を適用して移動中...
✅ [非破壊着地完了] BAY-A1 へ配置完了
=================================================================
```

---

## API リファレンス

### データクラス

#### `Vector3D`
3次元空間の位置・寸法を表現します。

```python
Vector3D(x=6.0, y=2.3, z=2.2)  # 長さ × 幅 × 高さ（単位: m）
```

#### `CargoItem`
荷物・パレットの統一データモデル

```python
CargoItem(
    item_id="C001",
    name="荷物名称",
    weight_kg=1200.0,
    dimensions=Vector3D(...),
    position=Vector3D(...),
    max_stack_weight_kg=1000.0,  # 積層限界重量
    sensitivity=MaterialSensitivity.FRAGILE  # 荷物特性
)
```

**プロパティ：**
- `volume_m3`: 容積（立方メートル）
- `volume_sai`: 才数換算（1m³ ≈ 35.315才）

#### `SpatialContainer`
荷台・コンテナ・倉庫区画の空間データモデル

```python
SpatialContainer(
    container_id="TRUCK-12FT-01",
    space_type=SpaceType.TRUCK_DECK,
    dimensions=Vector3D(x=6.0, y=2.3, z=2.2),
    max_payload_kg=5000.0
)
```

**メソッド：**
- `calculate_total_weight()` → 総積載重量（kg）
- `calculate_center_of_gravity()` → 重心位置（x, y, z）

### クラス

#### `SmartForkliftNavigator`
自律走行・安全着荷プロトタイプエンジン

```python
navigator = SmartForkliftNavigator(forklift_id="FL-01")
```

**メソッド：**

**`evaluate_space_and_load(target_space)`**
- 荷台・保管庫の安全判定を実行
- 戻り値：`dict` 含む以下の情報
  - `container_id`: コンテナID
  - `total_weight_kg`: 総積載重量
  - `capacity_usage_percent`: 容量使用率（%）
  - `center_of_gravity`: 重心位置（x, y, z）
  - `is_weight_safe`: 重量基準の合否
  - `is_balance_safe`: バランス基準の合否
  - `status`: 総合判定（SAFE / ATTENTION）

**`execute_gentle_transfer(cargo, source, destination)`**
- 非破壊・減速接地荷役を実行
- 繊細品に対し自動的にクリアランスを補正
- 戻り値：`bool` 成功可否

---

## 安全基準と判定ロジック

本システムは以下の基準で自動評価します。

| 項目 | 基準 | 説明 |
|------|------|------|
| **重量基準** | ≤ max_payload_kg | 総積載重量が最大積載量以下 |
| **前後バランス** | ±15% 以内 | 重心がX方向で容器長の15%以内に収束 |
| **左右バランス** | ±10% 以内 | 重心がY方向で容器幅の10%以内に収束 |
| **積層限界** | ≤ max_stack_weight_kg | 各荷物の耐圧限界を超えない |
| **材質考慮** | 感応度別対応 | 湿気品・繊細品に対し自動補正 |

**判定結果：**
- ✅ **SAFE** - すべての基準を満たしており、安全な状態
- ⚠️ **ATTENTION** - 1つ以上の基準を満たさず、再調整が必要

---

## 荷物の物理的特性

### MaterialSensitivity 列挙型

```python
MaterialSensitivity.STANDARD          # 通常物（特別対応不要）
MaterialSensitivity.MOISTURE_SENSITIVE # 湿気品（ダンボール等）
MaterialSensitivity.FRAGILE            # 繊細品（精密機器等）
```

**自動対応：**
- 通常物：そのまま積載
- 湿気品：積層限界を保守的に設定
- 繊細品：自動的に5cm のクリアランス（非接触）を確保

---

## 拡張性とカスタマイズ

### HandlingOptimizationEngine

現場フィードバックを記録し、将来的に機械学習と統合可能な設計

```python
navigator.engine.record_manual_adjustment(
    item_id="C001",
    clearance_cm=5.0,
    note="現場で微調整を実施"
)
```

将来のバージョンでは、このログから積載パラメータを自動最適化する機能を追加予定です。

---

## 実装例

### 例1: 12ftコンテナ2個積み（トラック）

```python
# 荷台定義
truck = SpatialContainer(
    container_id="TRUCK-12FT-01",
    space_type=SpaceType.TRUCK_DECK,
    dimensions=Vector3D(x=6.0, y=2.3, z=2.2),
    max_payload_kg=5000.0
)

# 前棟コンテナ
cargo_front = CargoItem(
    item_id="CONTAINER-F",
    name="12ftコンテナ-前棟",
    weight_kg=2200.0,
    dimensions=Vector3D(x=1.1, y=2.3, z=2.0),
    position=Vector3D(x=1.8, y=0.0, z=0.0)
)

# 後棟コンテナ
cargo_rear = CargoItem(
    item_id="CONTAINER-R",
    name="12ftコンテナ-後棟",
    weight_kg=2300.0,
    dimensions=Vector3D(x=1.1, y=2.3, z=2.0),
    position=Vector3D(x=4.2, y=0.0, z=0.0)
)

truck.items.extend([cargo_front, cargo_rear])
result = navigator.evaluate_space_and_load(truck)
```

### 例2: 倉庫保管エリアでの積層計画

```python
warehouse = SpatialContainer(
    container_id="BAY-A1",
    space_type=SpaceType.WAREHOUSE_BAY,
    dimensions=Vector3D(x=10.0, y=10.0, z=5.0),
    max_payload_kg=20000.0
)

# 複数荷物の積層
for i, cargo in enumerate(cargo_list):
    warehouse.items.append(cargo)

result = navigator.evaluate_space_and_load(warehouse)
if result['status'] == 'SAFE':
    print("✅ 倉庫配置が安全です")
else:
    print("⚠️ 積層を再調整してください")
```

---

## ライセンス

このプロジェクトは **MIT ライセンス** の下で公開されています。

---

## 作者・連絡先

- **阪上哲史 (Tetsushi Sakagami)**
- GitHub: [@tetsushisakagami-svg](https://github.com/tetsushisakagami-svg)

---

## 注記と免責事項

✅ **本ツールの目的：**
- 物流・倉庫運用の安全性向上を支援
- 計算根拠を透明化し、作業者の判断をサポート
- 将来的なAI・自動化への基盤構築

⚠️ **重要な注意：**
本システムが提供する計算値は、安全性確保のための参考値です。実際の運用では以下を遵守してください：

1. **法定基準の遵守**
   - 道路運送車両法
   - 労働安全衛生法
   - 物流センター運用マニュアル

2. **専門家の判断**
   - 最終的な安全判定は、現場の運行管理者・フォークリフト技能者の責任です
   - システムの計算結果のみで判断しないこと

3. **定期的なメンテナンス**
   - センサー精度の確認
   - パラメータの見直し
   - ログの定期監査

**本ツール使用による損害・事故について、作者は一切の責任を負いません。**

---

## 将来の拡張予定

- 📊 センサー統合（LiDAR、荷重計）
- 🤖 機械学習による最適化
- 🌐 クラウド連携・リアルタイム監視
- 📱 モバイルアプリケーション
- 🏭 ERP システム統合

ご質問や機能提案は、GitHub Issues でお気軽にお寄せください。
