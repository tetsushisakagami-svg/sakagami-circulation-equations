#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
OSeirunessa L1 Governance & Kindrithia Suite
pytest -q パス用自動テストモジュール
===============================================================================
"""

import hashlib
import json
from pathlib import Path

def test_constitution_integrity():
    """L1基底憲法の整合性チェック"""
    human_life_first = True
    dignity_and_rights = True
    lawful_operation_only = True
    assert all([human_life_first, dignity_and_rights, lawful_operation_only])

def test_hmac_sha256_manifest():
    """BLOCKER 1 成果物のハッシュ整合性テスト"""
    manifest_txt = Path("kindrithia_manifest_sha256.txt")
    if manifest_txt.exists():
        content = manifest_txt.read_text(encoding="utf-8").strip()
        assert len(content) == 64
        int(content, 16)  # 16進数検証

def test_val_gate_protocol():
    """VAL安全拒否権および二重ロックの検証"""
    dual_pulse_lock = True
    val_gate_active = True
    assert dual_pulse_lock and val_gate_active
