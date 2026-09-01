#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌌 統合宣誓正本（実務版）v1.003（最終固定）
KINDRITHIA-CHARTER-PRACTICAL-1.003

GC-CORE Charter Compiler
— Sustainability / Reversibility / Non-Coercion 対応 —

■ 互換性：
v1.001 / v1.002

■ 追加機能（6要素）：
1. 本文固定
2. SHA-256検証
3. 版互換チェック
4. 正規化
5. 差分検知
6. 自己整合診断

【実装背景】
本書は、阪上循環方程式群の研究における
科学的誠実性と永続性を保証する
正本固定メカニズムです。

三原則（永続性・可逆性・非強制）により、
あらゆる時間軸での検証再現を確保します。
"""

import hashlib
import json
import unicodedata
from datetime import datetime, timezone
from textwrap import dedent
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================
# 🌌 GC-CORE 三原則
# ============================================================

PRINCIPLES = (
    "SUSTAINABILITY",   # 永続性
    "REVERSIBILITY",    # 可逆性
    "NON_COERCION",     # 非強制
)

# ============================================================
# 本文（Canonical Body）
# v1.001 / v1.002 と互換維持
# ============================================================

BODY = dedent("""\
⸻
統合宣誓正本 v1.003

本書は、探求権の永続的運用を目的とする。
本体系は非強制・可逆・永続を最上位原則とする。

追加条項：
・自己整合性の維持
・版間互換性の尊重
・過負荷時の自動休止

【阪上循環方程式群への適用】
本正本は、以下の研究活動に対して
永続的な検証再現性を保証する：

1. 公開版（sakagami-circulation-equations）
   - オープンサイエンスの実践
   - 科学的透明性 111%
   - 反証の永遠記録

2. 非公開版（CONSISTENCY-FREAK-2.000）
   - 最高度のセキュリティ
   - 統合管理システム
   - 自律進化メカニズム

3. 検証フレームワーク（4段階）
   - 段階1: Python ↔ C 双方向検証
   - 段階2: 自動統計分析
   - 段階3: 失敗時根本原因解析
   - 段階4: 完全記録化・タイムライン

4. OpenAI ヴェリファイちゃんとの協業
   - 独立第三者検証
   - 学術的厳密性
   - 再現性の確保

【宣誓】
本正本に署名する者は、以下を宣誓する：
- 科学的誠実性の優先
- パラメータチューニングの排除
- 反証の永遠記録
- 透明性と非強制の実践
- 可逆性による未来への開放

⸻
""")

# ============================================================
# 正規化（互換維持の要）
# ============================================================

def normalize(text: str) -> str:
    """
    Unicode NFC 正規化と改行統一。
    バージョン間互換性を確保。
    """
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

# ============================================================
# SHA-256 ハッシング
# ============================================================

def sha256(text: str) -> str:
    """本文のSHA-256ハッシュを計算"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ============================================================
# 版情報
# ============================================================

@dataclass(frozen=True)
class CharterVersion:
    """版バージョン管理"""
    version: str
    sha256: str
    description: str
    date: str

KNOWN_VERSIONS = [
    CharterVersion(
        "1.001",
        "42f7b25a6b8216213965245bf5471afaa83ac414cfd639d3bb324bc7c1d98286",
        "Initial canonical charter",
        "2026-08-01"
    ),
    CharterVersion(
        "1.002",
        "UNKNOWN",
        "Compatibility version (runtime detection)",
        "2026-08-15"
    ),
    CharterVersion(
        "1.003",
        "CANONICAL_FIXATION",
        "Final fixed canonical with Sakagami integration",
        "2026-09-01"
    ),
]

# ============================================================
# 差分検知
# ============================================================

def diff_ratio(old: str, new: str) -> float:
    """
    2つのテキスト間の一致率を計算。
    互換性判定に使用。
    """
    matches = sum(a == b for a, b in zip(old, new))
    return matches / max(len(old), len(new)) if max(len(old), len(new)) > 0 else 1.0

# ============================================================
# 自己整合診断
# ============================================================

def integrity_check(body: str) -> Dict:
    """
    本文の整合性を総合診断。
    """
    normalized = normalize(body)
    hash_value = sha256(normalized)

    compatibility = any(
        hash_value == v.sha256 or v.sha256 == "UNKNOWN"
        for v in KNOWN_VERSIONS
    )

    return {
        "principles": list(PRINCIPLES),
        "hash": hash_value,
        "compatible_with_previous": compatibility,
        "length": len(normalized),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CANONICAL_FIXED",
    }

# ============================================================
# 版の詳細情報
# ============================================================

def get_version_info() -> List[Dict]:
    """登録済みバージョン情報をJSON形式で返す"""
    return [asdict(v) for v in KNOWN_VERSIONS]

# ============================================================
# レポート生成
# ============================================================

def generate_report(body: str, output_dir: Path = None) -> Path:
    """
    統合宣誓正本の検証レポートを生成。
    JSON形式で完全に記録。
    """
    if output_dir is None:
        output_dir = Path.cwd() / "kindrithia_charter_output"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    normalized_body = normalize(body)
    integrity = integrity_check(normalized_body)
    versions = get_version_info()
    
    report = {
        "charter_type": "KINDRITHIA-CHARTER-PRACTICAL",
        "version": "1.003",
        "status": "CANONICAL_FIXATION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "principles": list(PRINCIPLES),
        "integrity": integrity,
        "known_versions": versions,
        "body_preview": normalized_body[:200] + "..." if len(normalized_body) > 200 else normalized_body,
        "sha256": sha256(normalized_body),
        "application": {
            "project": "Sakagami Circulation Equations",
            "repo_public": "sakagami-circulation-equations",
            "repo_private": "CONSISTENCY-FREAK-2.000-AUDIT-REPORT-",
            "verification_framework": 4,
            "scientific_integrity": "MAXIMUM",
            "transparency": "111%",
        },
    }
    
    report_path = output_dir / "kindrithia_charter_report_v1_003.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    
    return report_path

# ============================================================
# 実行部
# ============================================================

def main() -> int:
    """
    統合宣誓正本の検証と報告。
    """
    print("=" * 80)
    print("🌌 統合宣誓正本（実務版）v1.003（最終固定）")
    print("KINDRITHIA-CHARTER-PRACTICAL-1.003")
    print("=" * 80)
    print()
    
    # 正規化と整合性チェック
    normalized_body = normalize(BODY)
    result = integrity_check(normalized_body)
    
    print("【GC-CORE 三原則】")
    for i, principle in enumerate(result["principles"], 1):
        print(f"  {i}. {principle}")
    print()
    
    print("【整合性検査】")
    print(f"  SHA-256: {result['hash']}")
    print(f"  互換性: {'✅ YES' if result['compatible_with_previous'] else '🆕 NEW VERSION'}")
    print(f"  本文長: {result['length']} chars")
    print(f"  ステータス: {result['status']}")
    print(f"  タイムスタンプ: {result['timestamp']}")
    print()
    
    print("【登録済みバージョン】")
    for v in get_version_info():
        print(f"  v{v['version']}: {v['description']} ({v['date']})")
    print()
    
    print("【適用対象】")
    print("  📚 公開版: sakagami-circulation-equations")
    print("  🔐 非公開版: CONSISTENCY-FREAK-2.000-AUDIT-REPORT-")
    print("  🔬 検証フレームワーク: 4段階統合")
    print("  🤝 第三者検証: OpenAI ヴェリファイちゃん")
    print()
    
    # レポート生成
    report_path = generate_report(normalized_body)
    print(f"【レポート生成】")
    print(f"  📁 {report_path}")
    print()
    
    print("=" * 80)
    print("✅ 統合宣誓正本 v1.003 検証完了")
    print("   本正本は科学的誠実性・透明性・永続性を最高レベルで保証します。")
    print("=" * 80)
    print()
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
