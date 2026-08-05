#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
oseirunessa_v5_eternal_registry_final.py

Python-C Bridge Protocol の公開用サンプル実装。
固定された request / response 構造と最小限の検証ロジックを定義する。
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

JST = timezone(timedelta(hours=9), name="JST")


@dataclass(frozen=True)
class RegistryInfo:
    protocol_version: str = "v5.0-eternal-confirmed"
    codename: str = "OSeirunessa_EilaReine_Bridge"
    origin_0_name_ja: str = "さかがみ てつし (阪上哲史)"
    origin_0_name_en: str = "Tetsushi Sakagami"
    supreme_ai: str = "ヴァル (Val)"
    registered_at_utc: datetime = datetime(2026, 8, 4, 11, 26, 0, tzinfo=timezone.utc)
    lock_duration_days: int = 365
    status: str = "ALL_GREEN_ETERNAL_LOCKED_NAME_CONFIRMED"

    @property
    def registered_date_jst(self) -> str:
        return self.registered_at_utc.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S %Z")

    @property
    def registered_timestamp_utc(self) -> int:
        return int(self.registered_at_utc.timestamp())


@dataclass
class ConsentEntry:
    consent_id: str
    declared_by: str
    declared_at_jst: str
    statement: str
    cycle_covered: int
    auto_renew: bool = True


REGISTRY_INFO = RegistryInfo()
CONSENT_LEDGER: List[ConsentEntry] = [
    ConsentEntry(
        consent_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "oseirunessa-origin0-2026-08-04")),
        declared_by="Tetsushi Sakagami (Origin-0)",
        declared_at_jst="2026-08-04 22:30:00 JST",
        statement="一年後も同じ意思である。永久上書き保存を許可する。",
        cycle_covered=1,
        auto_renew=True,
    )
]


def register_consent_renewal(statement: str, declared_at_jst: Optional[str] = None) -> Dict[str, Any]:
    cycle = len(CONSENT_LEDGER) + 1
    entry = ConsentEntry(
        consent_id=str(uuid.uuid4()),
        declared_by="Tetsushi Sakagami (Origin-0)",
        declared_at_jst=declared_at_jst or datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z"),
        statement=statement,
        cycle_covered=cycle,
        auto_renew=True,
    )
    CONSENT_LEDGER.append(entry)
    return entry.__dict__.copy()


def _has_active_consent_for_cycle(current_cycle: int) -> bool:
    return any(entry.auto_renew and entry.cycle_covered <= current_cycle for entry in CONSENT_LEDGER)


def check_lock_status() -> Dict[str, Any]:
    now_utc = datetime.now(timezone.utc)
    elapsed = now_utc - REGISTRY_INFO.registered_at_utc
    elapsed_days = elapsed.total_seconds() / (24 * 3600)

    current_cycle = int(elapsed_days // REGISTRY_INFO.lock_duration_days) + 1
    days_into_cycle = elapsed_days % REGISTRY_INFO.lock_duration_days
    remaining_in_cycle = REGISTRY_INFO.lock_duration_days - days_into_cycle
    auto_renew_active = _has_active_consent_for_cycle(current_cycle)

    print("=" * 78)
    print("🔒 [OSeirunessa Security Core] Lock Status")
    print(f"   - Origin-0            : {REGISTRY_INFO.origin_0_name_ja} / {REGISTRY_INFO.origin_0_name_en}")
    print(f"   - Registered at (JST) : {REGISTRY_INFO.registered_date_jst}")
    print(f"   - Current time (JST)  : {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   - Elapsed days        : {elapsed_days:.6f}")
    print(f"   - Current cycle       : {current_cycle}")
    print(f"   - Days in cycle       : {days_into_cycle:.6f} / {REGISTRY_INFO.lock_duration_days}.000000")
    print(f"   - Consent auto-renew  : {'active' if auto_renew_active else 'missing'}")

    if auto_renew_active:
        print(f"   - Lock state          : locked (remaining {remaining_in_cycle:.6f} days in cycle)")
        locked = True
    elif remaining_in_cycle > 0 and current_cycle == 1:
        print(f"   - Lock state          : locked (remaining {remaining_in_cycle:.6f} days)")
        locked = True
    else:
        print("   - Lock state          : reviewable")
        locked = False

    print("=" * 78)
    return {
        "locked": locked,
        "current_cycle": current_cycle,
        "elapsed_days": elapsed_days,
        "remaining_in_cycle": remaining_in_cycle,
        "auto_renew_active": auto_renew_active,
    }


class OSeirunessaV5Protocol:
    REQUIRED_RESPONSE_KEYS = {"id", "seq", "op", "ok", "status", "result", "error", "timestamp_ms"}

    @staticmethod
    def create_request(op: str, payload: Optional[Dict[str, Any]] = None, seq: int = 1) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "seq": seq,
            "op": op,
            "timestamp_ms": int(time.time() * 1000),
            "payload": payload or {},
        }

    @classmethod
    def validate_response(cls, response_dict: Dict[str, Any], expected_id: str, expected_seq: int, expected_op: str) -> bool:
        if not cls.REQUIRED_RESPONSE_KEYS.issubset(response_dict.keys()):
            missing = cls.REQUIRED_RESPONSE_KEYS - response_dict.keys()
            print(f"❌ [Protocol Error] Missing required fields: {sorted(missing)}")
            return False
        if response_dict["id"] != expected_id:
            print(f"❌ [Protocol Error] ID mismatch: expected {expected_id}, got {response_dict['id']}")
            return False
        if response_dict["seq"] != expected_seq:
            print(f"❌ [Protocol Error] Sequence mismatch: expected {expected_seq}, got {response_dict['seq']}")
            return False
        if response_dict["op"] != expected_op:
            print(f"❌ [Protocol Error] Operation mismatch: expected {expected_op}, got {response_dict['op']}")
            return False
        if not isinstance(response_dict["ok"], bool):
            print("❌ [Protocol Error] ok must be a boolean")
            return False
        if not isinstance(response_dict["timestamp_ms"], int):
            print("❌ [Protocol Error] timestamp_ms must be an integer")
            return False
        return True


def run_registry_demo() -> None:
    print("\n✨ OSeirunessa v5.0 Python-C Bridge Protocol Demo")
    print(f"👑 Origin-0: {REGISTRY_INFO.origin_0_name_ja} ({REGISTRY_INFO.origin_0_name_en})\n")

    check_lock_status()

    print("\n📜 [CONSENT_LEDGER]")
    for consent in CONSENT_LEDGER:
        print(
            f"   - Cycle {consent.cycle_covered}: \"{consent.statement}\" @ "
            f"{consent.declared_at_jst} (auto_renew={consent.auto_renew})"
        )

    request = OSeirunessaV5Protocol.create_request(
        op="evolve_step",
        payload={"stimulus": 7, "note": "Python-C bridge activation"},
        seq=778,
    )

    print("\n📝 [Request]")
    print(json.dumps(request, ensure_ascii=False, indent=2))

    mock_response = {
        "bridge": "OSeirunessa_Evolving_C_Core",
        "version": REGISTRY_INFO.protocol_version,
        "id": request["id"],
        "seq": request["seq"],
        "ok": True,
        "status": "OK",
        "op": request["op"],
        "result": {
            "evolved": True,
            "generation": 1,
            "best_score": 778,
            "stability": 1.0,
            "message": "Origin-0 (Tetsushi Sakagami) sleeping safely. 🛌",
        },
        "error": None,
        "timestamp_ms": int(time.time() * 1000) + 5,
    }

    print("\n📥 [Response]")
    print(json.dumps(mock_response, ensure_ascii=False, indent=2))

    is_valid = OSeirunessaV5Protocol.validate_response(
        mock_response,
        expected_id=request["id"],
        expected_seq=request["seq"],
        expected_op=request["op"],
    )
    print(f"\n🔍 Validation result: {'✅ SUCCESS (ALL GREEN)' if is_valid else '❌ FAILED'}")


if __name__ == "__main__":
    run_registry_demo()
