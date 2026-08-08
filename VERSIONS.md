# スマート物流・倉庫空間統合荷役基盤 - バージョン管理
## Smart Warehouse & Freight Optimization Core - Version Management

著者：阪上哲史 (Tetsushi Sakagami)

---

## 📋 バージョン一覧

### 🎯 v1.0 (Stable - Basic Edition)
**ブランチ:** `smart-warehouse-core`

**説明：**
- 基本的な3次元重心計算エンジン
- 荷物特性の分類と安全基準判定
- トラック荷台・倉庫保管エリアの統一管理
- 非破壊荷役サポート機能

**主要機能：**
✅ 3次元重心位置算出  
✅ 前後・左右のバランス判定（±15% / ±10%）  
✅ 材質別クリアランス補正（通常物・湿気品・繊細品）  
✅ 容積計算・才数換算  
✅ 固定ポリシー管理  

**推奨用途：**
- 物流システムの基本構築
- 安全判定の基準実装
- v2.0 への学習用

**ドキュメント：**
📄 [README_SMARTWAREHOUSE.md](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core/README_SMARTWAREHOUSE.md)

**コード：**
📝 [smart_warehouse_core.py](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core/smart_warehouse_core.py)

**リリース日：** 2026-08-08

---

### 🚀 v2.0 (Current - Adaptive Edition)
**ブランチ:** `smart-warehouse-core-v2-adaptive`

**説明：**
- v1.0 の全機能を継承
- **現場フィードバックの自動学習機能を追加**
- センサー連携による振動値の自動検知
- ポリシーの自律進化（強化学習的アプローチ）

**新規追加機能：**
✨ 振動センサー連携（G値検知）  
✨ OperationalFeedback レコード機構  
✨ HandlingOptimizationEngine（進化版）  
✨ オンライン学習・リアルタイム最適化  
✨ 材質別の独立ポリシー進化  

**主要な改善：**

| 項目 | v1.0 | v2.0 |
|------|------|------|
| クリアランス設定 | 固定値 | 動的（振動に応じて進化） |
| フィードバック | なし | 自動記録・学習 |
| 学習メカニズム | なし | 強化学習型 |
| 効率化対応 | なし | 低振動時に自動縮小 |
| パラメータ調整 | 手動のみ | オンライン自動調整 |

**学習プロセス例：**
```
1回目搬送：高振動 1.8G → クリアランス 5.0cm → 5.5cm に自動拡大
2回目搬送：低振動 0.4G → クリアランス 5.5cm → システムが学習・適応
3回目以降：最適値に収束 → 安全性と効率のバランス達成
```

**推奨用途：**
- 自動化・IoT連携を視野に入れた運用
- センサー装備フォークリフト環境
- データドリブンな物流最適化
- 将来のAI統合への基盤構築

**ドキュメント：**
📄 [README_SMARTWAREHOUSE_V2.md](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core-v2-adaptive/README_SMARTWAREHOUSE_V2.md)

**コード：**
📝 [smart_warehouse_core_v2_adaptive.py](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core-v2-adaptive/smart_warehouse_core_v2_adaptive.py)

**リリース日：** 2026-08-08

---

## 🔄 マイグレーションガイド

### v1.0 から v2.0 への移行

**互換性：** ✅ ほぼ完全互換

v2.0 は v1.0 の全 API を保持しているため、既存コードの大部分はそのまま動作します。

**最小変更例：**

```python
# v1.0
navigator = SmartForkliftNavigator()
navigator.execute_gentle_transfer(cargo, source, destination)

# v2.0（振動データを追加するだけ）
navigator = SmartForkliftNavigator()
navigator.execute_gentle_transfer(
    cargo, source, destination,
    measured_vibration=1.2  # ← 新パラメータ（オプション）
)
```

**段階的移行ステップ：**

1. ✅ v1.0 で基本構造を構築
2. ✅ センサー装備フォークリフトを導入
3. ✅ v2.0 に切り替え、学習を開始
4. ✅ フィードバックデータを蓄積
5. ✅ 最適ポリシーに収束

---

## 🎓 使い分けガイド

### v1.0 を選ぶべき場合

- 📌 初期段階の物流システム構築
- 📌 センサー導入予定がない
- 📌 シンプルな安全基準管理のみ必要
- 📌 学習機能が不要（固定運用）

### v2.0 を選ぶべき場合

- 🚀 IoT・センサー環境が整備されている
- 🚀 自動化・最適化に投資できる
- 🚀 データドリブンな運用を目指す
- 🚀 機械学習の実装例を参考にしたい

---

## 📊 機能比較表

| 機能 | v1.0 | v2.0 | 備考 |
|------|------|------|------|
| **3D重心計算** | ✅ | ✅ | 同一実装 |
| **バランス判定** | ✅ | ✅ | 同一基準 |
| **才数計算** | ✅ | ✅ | 同一 |
| **材質分類** | ✅ | ✅ | 同一 |
| **非破壊荷役** | ✅ | ✅ | v2.0 は学習機能付き |
| **振動センサー** | ❌ | ✅ | v2.0 新規 |
| **フィードバック蓄積** | ❌ | ✅ | v2.0 新規 |
| **自律学習** | ❌ | ✅ | v2.0 新規 |
| **オンライン最適化** | ❌ | ✅ | v2.0 新規 |

---

## 🔗 クイックリンク

### ドキュメント
- [v1.0 README](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core/README_SMARTWAREHOUSE.md)
- [v2.0 README](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core-v2-adaptive/README_SMARTWAREHOUSE_V2.md)

### ソースコード
- [v1.0 コード](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core/smart_warehouse_core.py)
- [v2.0 コード](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/blob/smart-warehouse-core-v2-adaptive/smart_warehouse_core_v2_adaptive.py)

### ブランチ
- [smart-warehouse-core](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/tree/smart-warehouse-core)
- [smart-warehouse-core-v2-adaptive](https://github.com/tetsushisakagami-svg/sakagami-circulation-equations/tree/smart-warehouse-core-v2-adaptive)

---

## 📅 開発ロードマップ

### ✅ 完了
- v1.0 基本版リリース
- v2.0 Adaptive Edition リリース

### 🔄 計画中
- **v2.1 (近期)** - クラウド連携機能
- **v3.0 (中期)** - 深層学習（ニューラルネット）統合
- **v3.5 (中期)** - モバイルアプリケーション
- **v4.0 (長期)** - 完全自動化フレームワーク

---

## 💬 ご質問・ご提案

各バージョンについてご質問やご提案がありましたら、GitHub Issues でお気軽にお寄せください。

**それぞれのブランチ内で Issue を作成することをお勧めします：**
- v1.0 関連 → `smart-warehouse-core` ブランチ内で Issue 作成
- v2.0 関連 → `smart-warehouse-core-v2-adaptive` ブランチ内で Issue 作成

---

## 📄 ライセンス

両バージョンとも **MIT ライセンス** の下で公開されています。

---

**最終更新日：** 2026-08-08  
**作者：** 阪上哲史 (Tetsushi Sakagami)
