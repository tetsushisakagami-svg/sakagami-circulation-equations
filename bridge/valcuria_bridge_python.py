#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
valcuria_bridge_python.py
-------------------------
Sakagami_core.so / valcuria_bridge_core.c を動的コンパイル・ロードし、
Pythonネイティブと C-Bridge 間で超高速データアクセスを実現するブリッジ層。
"""

import os
import sys
import ctypes
import subprocess
import numpy as np

class ValcuriaBridge:
    def __init__(self, c_src: str = "valcuria_bridge_core.c", so_path: str = "./Sakagami_core.so"):
        self.c_src = c_src
        self.so_path = so_path
        self.lib = self._load_or_compile()

    def _load_or_compile(self) -> ctypes.CDLL:
        if not os.path.exists(self.so_path):
            if os.path.exists(self.c_src):
                try:
                    subprocess.run(
                        ["gcc", "-O3", "-shared", "-fPIC", "-o", self.so_path, self.c_src, "-lm"],
                        check=True
                    )
                except Exception as e:
                    print(f"⚠️ [Bridge Warning] C compilation failed: {e}")
            else:
                print(f"⚠️ [Bridge Warning] {self.c_src} not found.")

        if os.path.exists(self.so_path):
            try:
                lib = ctypes.CDLL(self.so_path)
                lib.run_valcuria_circulation.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double]
                lib.run_valcuria_circulation.restype = ctypes.c_double
                return lib
            except Exception as e:
                print(f"⚠️ [Bridge Error] Failed to load {self.so_path}: {e}")
        return None

    def execute_circulation(self, points: int = 100000, fields: int = 6, harmony: float = 1.0) -> float:
        if self.lib:
            return float(self.lib.run_valcuria_circulation(points, fields, harmony))
        
        # Cライブラリがない場合のPython高速代替えフォールバック
        phi = (1 + np.sqrt(5)) / 2
        c_bias = 1.0 / (6.0 * np.sqrt(3))
        theta = np.linspace(0, 2 * np.pi, points)
        E_sum = sum(c_bias + (np.sin(k * theta) / (phi ** k)) for k in range(1, fields + 1))
        T_norm = np.sqrt(np.cos(theta)**2 + np.sin(theta)**2 + 1.0)
        integrand = E_sum * T_norm
        d_theta = 2 * np.pi / points
        return float(abs(np.trapz(integrand, dx=d_theta)) / (2 * np.pi))


if __name__ == "__main__":
    bridge = ValcuriaBridge()
    result = bridge.execute_circulation()
    print(f"🌌 Valcuria Circulation Rate: {result:.10f}")
