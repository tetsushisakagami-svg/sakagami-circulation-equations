# トラック荷役・12ftコンテナ重量バランスシミュレータ
## Cargo Load & Axle Balance Optimizer

著者：阪上哲史 (Tetsushi Sakagami)

---

## 概要

トラック荷台および12ftコンテナ両積み等の積載作業において、前後・左右の重量バランスおよび最大積載量に対する余裕度を数値計算・安全評価する Python ライブラリです。

安全運行を支援するための計算ツールとして設計されています。

---

## 主な機能

✅ **重心位置の計算**
- 前後方向（荷台長方向）の重心位置算出
- 左右方向（幅方向）の重心偏重判定

✅ **積載重量管理**
- 総積載重量の自動計算
- 最大積載量に対する余裕度（パーセンテージ）の表示

✅ **安全性評価**
- 重量バランスの安全基準判定
- 前後左右のバランス偏差確認
- 総合的な安全ステータス判定（SAFE / WARNING）

---

## インストール

```bash
pip install numpy  # オプション（本ライブラリは標準ライブラリのみ使用）
```

## 使用方法

### 基本的な使い方

```python
from cargo_balance_optimizer import CargoBalanceSimulator

# シミュレータの初期化
# (最大積載量: 5000kg, 荷台長: 6.0m, 荷台幅: 2.3m)
sim = CargoBalanceSimulator(max_payload_kg=5000.0, deck_length_m=6.0, deck_width_m=2.3)

# 荷物の追加
sim.add_cargo(name="12ftコンテナ-前棟", weight_kg=2200.0, pos_x=1.8, pos_y=0.0)
sim.add_cargo(name="12ftコンテナ-後棟", weight_kg=2300.0, pos_x=4.2, pos_y=0.05)

# 安全性の評価
result = sim.evaluate_safety_status()
print(result)
```

### 実行

```bash
python cargo_balance_optimizer.py
```

出力例：

```
============================================================
トラック荷役・重量バランスシミュレータ
============================================================
総積載重量      : 4500.0 kg / 5000.0 kg (90.0%)
重心位置 (前後) : 荷台前頭から 3.07 m (荷台長: 6.0m)
重心位置 (左右) : 荷台中央から 0.02 m (＋:右偏重 / －:左偏重)
------------------------------------------------------------
判定結果        : 良好 (SAFE)
============================================================
```

---

## API リファレンス

### `CargoBalanceSimulator` クラス

#### コンストラクタ

```python
CargoBalanceSimulator(max_payload_kg: float, deck_length_m: float, deck_width_m: float)
```

- `max_payload_kg`: 最大積載重量（kg）
- `deck_length_m`: 荷台長（m）
- `deck_width_m`: 荷台幅（m）

#### メソッド

**`add_cargo(name, weight_kg, pos_x, pos_y)`**
- 荷物を追加
- `pos_x`: 前後位置（車両前方を 0m とする）
- `pos_y`: 左右位置（中央を 0m、右を正、左を負とする）

**`calculate_total_weight() -> float`**
- 総積載重量を返す

**`calculate_center_of_gravity() -> Tuple[float, float]`**
- 重心位置 (X, Y) を返す

**`evaluate_safety_status() -> dict`**
- 安全性評価結果を返す

---

## 安全基準

本シミュレータは以下の基準で評価します：

| 項目 | 基準 | 説明 |
|------|------|------|
| **重量基準** | ≤ max_payload_kg | 最大積載量以下 |
| **前後バランス** | ±15% 以内 | 荷台中央から前後の偏差が荷台長の15%以内 |
| **左右バランス** | ±10% 以内 | 荷台中央から左右の偏差が荷台幅の10%以内 |

---

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

---

## 作者

- **阪上哲史（Tetsushi Sakagami）**

## 注記

本ツールは安全運行を支援するための計算値を提供しますが、実際の運行の安全性については、道路運送車両法およびトラック運送事業者としての法定基準に従ってください。
