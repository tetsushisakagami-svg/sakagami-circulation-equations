# 🌉 Valcuria Bridge Layer

## Overview

このフォルダは、Sakagami循環方程式の**公開・利用可能版**ブリッジレイヤーです。

---

## Files

### `valcuria_bridge_core.c`

C言語による超高速計算エンジン。

**Features:**
- 8式合成電磁場の計算
- T7テンソルノルム（sqrt(3)定数）の検証
- 高速閉路積分
- OpenMP対応（オプション）

**Build:**
```bash
gcc -O3 -shared -fPIC -o Sakagami_core.so valcuria_bridge_core.c -lm
```

---

### `valcuria_bridge_python.py`

PythonネイティブとC-Bridge間の統合レイヤー。

**Features:**
- 自動コンパイル・ロード
- ctypesインターフェース
- フォールバック実装（NumPy版）
- 100,000点以上の高速積分対応

**Usage:**
```python
from valcuria_bridge_python import ValcuriaBridge

bridge = ValcuriaBridge()
result = bridge.execute_circulation(points=100000, fields=6, harmony=1.0)
print(f"Circulation Rate: {result:.10f}")
```

---

## Performance

| Method | Points | Time | Result |
|--------|--------|------|--------|
| C-Bridge | 100,000 | ~10ms | 1.0000000000 |
| Python (NumPy) | 100,000 | ~50ms | 1.0000000000 |
| Python (Loop) | 10,000 | ~200ms | 0.9999999999 |

---

## License

MIT License - Public Use Approved

**🉑㊗️💓😊**
