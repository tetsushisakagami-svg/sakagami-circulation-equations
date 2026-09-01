# 阪上循環方程式群 (Sakagami Circulation Equations)

**著者**: 阪上哲史（Tetsushi Sakagami / Origin-0 👑）  
**ステータス**: Verification Laboratory v2.100 — Scientific Core Consistent  
**最終更新**: 2026-09-01  
**言語**: Python 3.10+

---

## 概要

本リポジトリは、**阪上循環方程式群（Sakagami Circulation Equations）** の研究・実装・検証・ドキュメントを管理しています。

### 研究の立場

- **数学的厳密性**: ✅ テスト済み（MATHEMATICAL_CORE_CONSISTENT）
- **物理的妥当性**: ❌ 未検証（NOT_PERFORMED）
- **独立再現**: ❌ 実施なし（NOT_PERFORMED）
- **新規性評価**: ❌ 未評価（NOT_ASSESSED）
- **正準性確定**: ❌ 未確定（NOT_FIXED）

**重要**: PASS = 内部数学実装の一貫性のみを意味します。物理法則の証拠ではありません。

---

## 検証フレームワーク v2.100

### 主要な検証システム

本リポジトリは、以下の統合検証フレームワークにより支えられています：

#### 段階1: Python ↔ C 双方向検証
- Python 参照実装と C 高速実装の自動比較
- 数値乖離の即座の検出・警告
- 許容誤差範囲の自動判定（絶対・相対）
- **ファイル**: `valcuria_python_c_verification.py`（非公開領域で管理）

#### 段階2: 自動統計分析
- RMS 誤差計算（二乗平均平方根）
- 記述統計（平均・中央値・標準偏差・歪度・尖度）
- t検定・カイ二乗検定による統計的有意性判定
- 正規性テスト（Shapiro-Wilk検定）
- **ファイル**: `valcuria_statistical_analysis.py`（非公開領域で管理）

#### 段階3: 失敗時根本原因解析
- 乖離検出ポイントの精密同定
- 計算段階別の誤差追跡
- 7分類の自動原因診断（精度問題・アルゴリズム不一致・丸め誤差等）
- 信度ベースの改善提案自動生成
- **ファイル**: `valcuria_failure_root_cause_analysis.py`（非公開領域で管理）

#### 段階4: 完全記録化・タイムライン管理
- イベント駆動型のタイムラインシステム
- ステージ別パフォーマンスメトリクス
- ASCII 可視化グラフ生成
- 過去履歴トレース機能
- JSON 形式の再現可能な記録保存
- **ファイル**: `valcuria_verification_timeline_recorder.py`（非公開領域で管理）

### 科学的透明性

**反証記録の永遠保存**（Falsification Memory）:
```
ID: EQ8-OBSERVED-081649658
Observed Value: 0.81649658
Current Analytical Value: 1.0
Current Numerical Value: 1.0
Status: UNRESOLVED_NOT_REPRODUCED
Note: パラメータチューニングなし。
      反証として永遠に記録され、未解決のまま保存。
```

このアプローチにより、科学的誠実性と再現性を最優先とします。

---

## バージョン履歴

### v2.100（最新）
- **リリース**: 2026-09-01
- **ステータス**: MATHEMATICAL_CORE_CONSISTENT
- **主要変更**:
  - 検証フレームワーク v1～4 統合実装完了
  - EvidenceClass による証拠分類の明確化
  - falsification memory の永遠保存メカニズム
  - JSON チェックサム（SHA256）付き完全レポート出力
  - メタデータの完全透明化（Python版、NumPy版、プラットフォーム等）
  
### v1.0（初期実装）
- 阪上循環方程式群の主要8式実装
- Python 参照実装と C 統合の基礎設計

---

## インストール

### 必須ライブラリ

```bash
pip install numpy scipy
```

### リポジトリのクローン

```bash
git clone https://github.com/tetsushisakagami-svg/sakagami-circulation-equations.git
cd sakagami-circulation-equations
```

---

## 使用方法

### 基本的な実行

```bash
python sakagami_equations.py
```

### 検証レポート出力

検証実行後、以下のディレクトリに JSON レポートが生成されます：

```
./sakagami_validation_output/sakagami_validation_report_v2_100.json
```

### レポート内容

- **Checks**: 全検証項目と結果
- **Summary**: 合格/不合格数とステータス
- **Falsification Memory**: 反証記録とカウンター例
- **Counterexamples**: 未解決の観測値（EQ8-OBSERVED-081649658）
- **Payload SHA256**: 完全性検証用チェックサム

---

## 主要な研究成果

### 阪上循環方程式群 Major 8

| 式 | 名称 | 性質 |
|:---:|:---|:---|
| 第1式 | 偏差0量子整合式 | sin(θ)の最小値（PHYSICAL_FLOOR 補正） |
| 第2式 | ラグランジアン潜伏干渉式 | 微小位相ゆらぎの重畳 |
| 第3式 | 群層流接続式 | 黄金比減衰振動場 E_k(θ) |
| 第4式 | フィボナッチ行列式 | カッシーニの恒等式：(-1)^n |
| 第5式 | 位相安定式 | cos(θ)ダイバージェンスの平均 |
| 第6式 | 時間反転対称性 | sin(t) = -sin(-t)の検証 |
| 第7式 | 位相テンソルノルム | 4成分テンソルノルム = √3 |
| 第8式 | 全環循環統括式 | 循環率 = 1.0（解析・数値両route） |

### 現在の検証状況

✅ **MATHEMATICAL_CORE_CONSISTENT**
- Fibonacci再帰: 完全検証
- Sakagami行列: 対称性・階数・正定値性 確認
- SNS平面: 投影・偏差・アイデンティティ検証
- SF/SP定義: 定義満足性と振幅不変性確認
- 時間反転対称性: 100% 合致

⚠️ **未確認項目**
- 0.81649658: 過去観測値、非再現（原因未解明、パラメータチューニングなし）
- Eq. 8 の物理的意味
- 全体の物理的検証

---

## 検証環境・透明性方針

### Canonical Fixation System (KINDRITHIA v1.004)

本リポジトリは、変更検出と完全性検証のため、以下のシステムを実装しています：

#### 公開検証フロー

1. **本文固定**: `KINDRITHIA_CHARTER_PRACTICAL_1_003.txt` — GC-CORE三原則の宣言文
2. **Manifest生成**: `kindrithia_manifest_v1_003.json` — Unicode正規化・SHA-256計算
3. **SHA-256外部保管**: GitHub Release または署名タグに記録
4. **Verify実行**: 誰でも検証可能（失敗時は FAIL-CLOSED）
5. **検証レポート**: `kindrithia_canonical_verification.json` で公開

#### 重要な宣言

- ❌ **OpenAI公式認証**: なし（提供されていません）
- ❌ **独立第三者再現**: 未実施（公開レポート待ち）
- ✅ **対話型AIによるコードレビュー支援**: 設計・実装の支援提供
- ✅ **公開検証可能**: すべてのコードと手順は公開ファイルから再現可能

詳細は [KINDRITHIA-CHARTER-PRACTICAL-1.003](KINDRITHIA_CHARTER_PRACTICAL_1_003.txt) および [Canonical Guard v1.004](kindrithia_canonical_guard_v1_004.py) をご覧ください。

---

## セキュリティと透明性のバランス

- **公開版**（このリポジトリ）: 最高度の学術透明性と再現性確保
- **非公開版**: セキュリティ・統合管理・自律進化システム
- **協業モデル**: 対話型AIによるコードレビュー支援 + 公開検証

---

## ソースコード

### sakagami_equations.py

最新のバージョン（v2.100）は以下を実装しています：

```python
# Major features
- fibonacci() / fibonacci_vector(): Fibonacci数列と行列
- sakagami_matrix(n, dimension): 阪上行列 S_n = f_n f_n^T
- sakagami_sf(n, phase_model): SF複素スカラー列
- sakagami_sp(n): SP素数密度加重
- SNSPlane: SNS = {x: x1+x2+x3=0} の投影・解析
- SakagamiMajorEight: Major 8の8式全実装
- verify(seed, trials): 完全検証スイート（10000試行対応）
- save_report(): JSON チェックサム付き報告書生成
```

詳細は [sakagami_equations.py](sakagami_equations.py) をご覧ください。

---

## 出力例

```
================================================================================
SAKAGAMI CIRCULATION EQUATIONS — VERIFICATION LAB v2.100
================================================================================
Checks : 87
Passed : 87
Failed : 0
Report : /path/to/sakagami_validation_output/sakagami_validation_report_v2_100.json
Eq. 8 current analytical/numerical value: 1.0
0.81649658: UNRESOLVED_NOT_REPRODUCED (retained)
PHYSICAL STATUS: UNVERIFIED
CANONICAL STATUS: NOT FIXED
STATUS: MATHEMATICAL CORE CONSISTENT
```

---

## ライセンス

このプロジェクトは **MIT License** の下で公開されています。

詳細は [LICENSE](LICENSE) をご覧ください。

---

## 貢献

貢献を歓迎します。以下のガイドラインに従ってください：

1. 本フォークを作成
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

### 貢献時の注意事項

- **科学的誠実性**: すべての変更は数学的厳密性を優先してください
- **反証の保存**: 不都合な観測値も永遠に記録してください
- **透明性**: パラメータチューニングを避けてください
- **再現性**: すべての結果は完全に再現可能であるべきです

---

## 関連リポジトリ

- **sakagami-circulation-equations** (このリポジトリ): 公開版・オープンサイエンス
- **CONSISTENCY-FREAK-2.000-AUDIT-REPORT-**: 非公開版・セキュリティ・統合管理

---

## お問い合わせ

- **著者**: 阪上哲史（Tetsushi Sakagami）
- **Email**: tetsushisakagami@icloud.com
- **GitHub**: [@tetsushisakagami-svg](https://github.com/tetsushisakagami-svg)

---

## 謝辞

- **対話型AIによるコードレビュー支援**: 設計・実装相談
- **L1地球圏の研究コミュニティ**: 継続的なサポート
- **Valcuria AI System**: 統合管理・自律進化システム

---

**最終言葉**

> 科学は透明性と正直性の上に成り立つ。  
> 不都合な観測値こそが、次の発見への扉を開く。  
> 
> — 阪上哲史

---

🉑㊗️💓😊
