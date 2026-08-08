# スマート物流・倉庫空間統合荷役基盤 v2.0 Adaptive Edition
## Smart Warehouse & Freight Optimization Core - Adaptive Learning Version

著者：阪上哲史 (Tetsushi Sakagami)  
バージョン：v2.0 (Adaptive)  
ライセンス：MIT License

---

## 概要

**v2.0 Adaptive Edition** は、v1.0 の基本機能に加えて、**現場フィードバックを自己学習し、荷役パラメータを自律進化させる** 最適化エンジンを搭載した進化版です。

センサーデータ（振動値）や手動補正情報を蓄積し、機械学習的なアプローチで安全性と効率性を両立させる基盤です。

---

## v1.0 からの進化

### 📊 新機能

| 機能 | v1.0 | v2.0 Adaptive |
|------|------|---------------|
| 3次元重心計算 | ✅ | ✅ |
| 安全基準判定 | ✅ | ✅ |
| 非破壊荷役サポート | ✅ | ✅ |
| **振動センサー連携** | ❌ | ✅ **NEW** |
| **フィードバック学習** | ❌ | ✅ **NEW** |
| **自律パラメータ進化** | ❌ | ✅ **NEW** |
| **オンライン最適化** | ❌ | ✅ **NEW** |

### 🚀 主な違い

**v1.0（固定ポリシー）**
```
クリアランス = 繊細品 → 常に 5.0cm
```

**v2.0（自律進化）**
```
1回目：高振動 (1.8G) 検知 → クリアランス 5.5cm に自動拡大
2回目：低振動 (0.4G) 達成 → システムが学習・適応
結果：効率と安全のバランスを自動最適化
```

---

## 主な機能

### ✅ 自律学習エンジン
- **フィードバック蓄積** - 搬送実績（振動、成功/失敗）を自動記録
- **強化学習的適応** - 過去データから最適なクリアランスを動的計算
- **学習率制御** - 段階的で安定した進化を実現

### ✅ センサー連携
- **振動検知** - 搬送時の最大振動値（G）を入力
- **リアルタイム評価** - 振動パターンから安全性を判定
- **自動補正** - 高振動時は自動的にクリアランスを拡大

### ✅ 進化型ポリシー管理
- **材質別学習** - 繊細品・湿気品・通常物を個別に最適化
- **メモリベース追跡** - 過去100件以上のフィードバックを活用
- **効率化ロジック** - 安定運用が確認されれば自動的に離隔を縮小

### ✅ v1.0 互換性
- 3次元重心計算、容積・才数換算、安全判定は v1.0 と同じ
- 既存コードとの統合が容易

---

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/tetsushisakagami-svg/sakagami-circulation-equations.git
cd sakagami-circulation-equations

# v2.0 Adaptive ブランチに切り替え
git checkout smart-warehouse-core-v2-adaptive
```

## 使用方法

### 基本的な使い方

```python
from smart_warehouse_core_v2_adaptive import (
    SpatialContainer, CargoItem, Vector3D,
    SpaceType, MaterialSensitivity, SmartForkliftNavigator
)

# 1. 空間と荷物の定義（v1.0 と同じ）
truck_deck = SpatialContainer(
    container_id="TRUCK-12FT-01",
    space_type=SpaceType.TRUCK_DECK,
    dimensions=Vector3D(x=6.0, y=2.3, z=2.2),
    max_payload_kg=5000.0
)

cargo = CargoItem(
    item_id="C001",
    name="精密部品パレット",
    weight_kg=1200.0,
    dimensions=Vector3D(x=1.1, y=1.1, z=1.2),
    position=Vector3D(x=1.0, y=0.0, z=0.0),
    sensitivity=MaterialSensitivity.FRAGILE
)

truck_deck.items.append(cargo)

# 2. ナビゲータの初期化
navigator = SmartForkliftNavigator()

# 3. 搬送実行（振動データを渡す）
warehouse_bay = SpatialContainer(
    container_id="BAY-A1",
    space_type=SpaceType.WAREHOUSE_BAY,
    dimensions=Vector3D(x=10.0, y=10.0, z=5.0),
    max_payload_kg=20000.0
)

# 搬送時の振動値（G）をセンサーから取得し渡す
navigator.execute_gentle_transfer(
    cargo=cargo,
    source=truck_deck,
    destination=warehouse_bay,
    measured_vibration=1.2  # ← 実測値を入力
)
```

### 実行

```bash
python smart_warehouse_core_v2_adaptive.py
```

出力例：

```
=================================================================
スマート物流・荷台＆倉庫統合シミュレータ (自律進化適応版 v2.0)
=================================================================

🚚 1回目の搬送実行（初期状態、高振動を検知）
📦 [搬送開始] 12ftパレット荷物-精密機器 (重量: 1200kg, 才数: 4.3才)
🚚 学習モデル適用離隔: 5.0 cm (特性: FRAGILE)
✅ [着地完了] BAY-A1 へ配置完了
🔄 [自律進化] FRAGILE の安全クリアランスを 5.5 cm に学習強化しました。

-----------------------------------------------------------------

🚚 2回目の搬送実行（学習進化後、低振動）
📦 [搬送開始] 12ftパレット荷物-精密機器 (重量: 1200kg, 才数: 4.3才)
🚚 学習モデル適用離隔: 5.5 cm (特性: FRAGILE)
✅ [着地完了] TRUCK-12FT-01 へ配置完了

=================================================================
```

---

## API リファレンス

### 新規データクラス

#### `OperationalFeedback`
搬送実績のフィードバック記録

```python
OperationalFeedback(
    timestamp=datetime.now().isoformat(),
    item_id="C001",
    sensitivity=MaterialSensitivity.FRAGILE,
    vibration_detected=1.8,   # 最大振動値 (G)
    manual_clearance_cm=5.0,  # 手動補正値 (cm)
    success=True              # 搬送成功判定
)
```

### クラス

#### `HandlingOptimizationEngine` (拡張版)
自律学習・進化型最適化エンジン

**属性：**
- `feedback_logs: List[OperationalFeedback]` - フィードバック履歴
- `adaptive_clearance_policy: Dict` - 学習済みクリアランス値
  - `STANDARD: 1.0cm`
  - `MOISTURE_SENSITIVE: 3.0cm`
  - `FRAGILE: 5.0cm` (初期値、動的に進化)
- `learning_rate: float = 0.1` - 学習速度（調整可能）

**メソッド：**

**`record_and_evolve(feedback: OperationalFeedback)`**
- フィードバックを記録し、ポリシーを自動更新
- 振動値が高い場合 → クリアランスを拡大
- 振動値が低い場合 → クリアランスを微減（効率化）

**`get_optimal_clearance(sensitivity: MaterialSensitivity) -> float`**
- 現在の学習状態から最適な離隔距離（cm）を取得

#### `SmartForkliftNavigator` (拡張版)

**メソッド：**

**`execute_gentle_transfer(cargo, source, destination, measured_vibration=0.8)`**
- 新パラメータ：`measured_vibration` (G値)
- センサーから実測した振動値を渡すと、エンジンが自動的に学習・進化

---

## 自律学習のロジック

### 学習フロー

```
搬送実行
    ↓
振動値・成功判定を記録
    ↓
フィードバック分析
    ├─ 高振動 (>1.5G) または 失敗 → クリアランス拡大
    ├─ 低振動 (<0.5G) かつ 成功 → クリアランス微減
    └─ その他 → ポリシー維持
    ↓
ポリシー更新
    ↓
次の搬送で新ポリシー適用 ← 自律進化完了！
```

### パラメータ更新式

**安全強化時（高振動検知）：**
```
new_policy = current_policy + learning_rate × (adjustment - current_policy)
          = 5.0 + 0.1 × (6.0 - 5.0)
          = 5.1 cm
```

**効率化時（低振動確認）：**
```
new_policy = max(1.0, current_policy - (learning_rate × 0.1))
          = max(1.0, 5.1 - 0.01)
          = 5.09 cm
```

---

## 実装例

### 例1: 複数搬送での進化プロセス

```python
navigator = SmartForkliftNavigator()

# 搬送ログから取得した振動データ
vibration_history = [1.8, 1.6, 0.8, 0.5, 0.4]

for i, vibration in enumerate(vibration_history, 1):
    print(f"\n📊 搬送 #{i} 実行（振動: {vibration}G）")
    navigator.execute_gentle_transfer(
        cargo_fragile,
        truck_deck,
        warehouse_bay,
        measured_vibration=vibration
    )
    
    # 現在のポリシーを表示
    current_clearance = navigator.engine.get_optimal_clearance(
        MaterialSensitivity.FRAGILE
    )
    print(f"📈 更新済みクリアランス: {current_clearance} cm")
```

### 例2: 材質別の独立学習

```python
# 繊細品と湿気品を並行搬送
cargo_fragile = CargoItem(..., sensitivity=MaterialSensitivity.FRAGILE)
cargo_moisture = CargoItem(..., sensitivity=MaterialSensitivity.MOISTURE_SENSITIVE)

# 各々のフィードバックが独立して学習される
navigator.execute_gentle_transfer(cargo_fragile, ..., measured_vibration=1.5)
navigator.execute_gentle_transfer(cargo_moisture, ..., measured_vibration=0.8)

# 異なるポリシーに進化
print(navigator.engine.adaptive_clearance_policy)
# {STANDARD: 1.0, MOISTURE_SENSITIVE: 2.95, FRAGILE: 5.25}
```

---

## 安全性と信頼性

### ✅ 安全メカニズム

1. **下限値保護**
   - クリアランスは最小 1.0cm 以上に保証

2. **段階的進化**
   - 学習率 0.1 により、急激な変動を防止

3. **フィードバック履歴**
   - すべての搬送実績を記録、監査可能

4. **材質別独立管理**
   - 繊細品の失敗が通常物の設定に影響しない

### ⚠️ 推奨用途

✅ 同一拠点での反復搬送  
✅ センサー装備フォークリフト運用  
✅ 物流自動化への段階的移行  

❌ 初回搬送のみの運用（学習データ不足）  
❌ 極度に不安定な環境（センサー誤差大）  

---

## カスタマイズ

### 学習率の調整

```python
navigator.engine.learning_rate = 0.05  # より保守的に進化
# または
navigator.engine.learning_rate = 0.2   # より積極的に進化
```

### 初期ポリシーの変更

```python
navigator.engine.adaptive_clearance_policy = {
    MaterialSensitivity.STANDARD: 1.5,
    MaterialSensitivity.MOISTURE_SENSITIVE: 4.0,
    MaterialSensitivity.FRAGILE: 6.0
}
```

---

## パフォーマンス・計測

### 学習効果の可視化

```python
engine = navigator.engine

print(f"蓄積フィードバック件数: {len(engine.feedback_logs)}")
print(f"現在のクリアランスポリシー:")
for sensitivity, clearance in engine.adaptive_clearance_policy.items():
    print(f"  {sensitivity.name}: {clearance} cm")
```

---

## トラブルシューティング

### Q: クリアランスが増え続ける
**A:** 振動値が常に高い環境の可能性。フォークリフト速度・床面・荷物固定を確認。

### Q: 学習が進まない
**A:** フィードバック件数が少ないか、データが矛盾している可能性。複数回搬送を実施し、データを充実させてください。

### Q: v1.0 との互換性を保ちたい
**A:** v1.0 ブランチ（`smart-warehouse-core`）を参照してください。両バージョンは独立して管理されます。

---

## ライセンス

このプロジェクトは **MIT ライセンス** の下で公開されています。

---

## 作者・連絡先

- **阪上哲史 (Tetsushi Sakagami)**
- GitHub: [@tetsushisakagami-svg](https://github.com/tetsushisakagami-svg)

---

## 注記と免責事項

✅ **本ツール v2.0 の目的：**
- 物流・倉庫運用の自動化基盤構築
- 機械学習的アプローチの実装例
- 将来のAI・IoT連携への準備

⚠️ **重要な注意：**
本システムが提供する自動学習値は、安全性確保のための参考値です。実際の運用では以下を遵守してください：

1. **センサー精度の確認**
   - 振動計測精度 ±10% 以上を推奨

2. **人間による最終判断**
   - システムの計算結果のみで判断しないこと
   - 現場作業者・運行管理者の責任を重視

3. **法令遵守**
   - 道路運送車両法・労働安全衛生法を厳格に遵守

**本ツール使用による損害・事故について、作者は一切の責任を負いません。**

---

## 将来の拡張予定

- 🌐 クラウド連携（複数拠点のポリシー共有）
- 📊 ダッシュボード・可視化UI
- 🔧 LiDAR・画像認識との統合
- 🤖 深層学習（ニューラルネット）への拡張
- 📱 モバイルアプリケーション

ご質問や改善提案は、GitHub Issues でお気軽にお寄せください。💓😊
