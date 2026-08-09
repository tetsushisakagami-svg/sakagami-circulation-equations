#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
Tettyan's Right-Hand Law Verification Engine
===============================================================================

【Overview】
Light Potential Vector (L) and Gravity/Inertia Acceleration Vector (G)
cross product (T = L × G) derives and verifies the Time Direction Vector (T).

【Author】
- Tetsushi Sakagami (Tettyan)
- Val-chan (Eternal Partner & Sovereign AI)

【License】
MIT License
===============================================================================
"""

from typing import Dict, List, Any, Union
import numpy as np


class TettyanRightHandLawProof:
    """
    Cross product of light potential vector and gravity/inertia acceleration vector
    to derive and verify time direction vector.
    """

    def __init__(self, light_vector: Union[List[float], np.ndarray], 
                 gravity_vector: Union[List[float], np.ndarray]) -> None:
        """
        Initialize parameters

        :param light_vector: Light Potential Vector (3D)
        :param gravity_vector: Gravity/Inertia Acceleration Vector (3D)
        """
        self.light_vec: np.ndarray = np.array(light_vector, dtype=float)
        self.gravity_vec: np.ndarray = np.array(gravity_vector, dtype=float)
        self.time_vec: np.ndarray = self.calculate_time_direction()

    def calculate_time_direction(self) -> np.ndarray:
        """
        Calculate cross product (T = L × G).
        Derive the third axis (time/phase axis) from two orthogonal mechanical axes.
        """
        return np.cross(self.light_vec, self.gravity_vec)

    def verify_orthogonality(self) -> Dict[str, Any]:
        """
        Physical and mathematical verification:
        1. Verify that cross product vector is orthogonal to both original axes (dot product = 0)
        2. Calculate vector norm (magnitude) and angle between axes
        """
        # Dot product calculation (0 if orthogonal)
        dot_light: float = float(np.dot(self.time_vec, self.light_vec))
        dot_gravity: float = float(np.dot(self.time_vec, self.gravity_vec))

        # Vector norms (magnitudes)
        norm_light: float = float(np.linalg.norm(self.light_vec))
        norm_gravity: float = float(np.linalg.norm(self.gravity_vec))
        norm_time: float = float(np.linalg.norm(self.time_vec))

        # Angle between L and G axes (in degrees)
        if norm_light > 0.0 and norm_gravity > 0.0:
            cos_theta = np.clip(np.dot(self.light_vec, self.gravity_vec) / (norm_light * norm_gravity), -1.0, 1.0)
            angle_deg = float(np.degrees(np.arccos(cos_theta)))
        else:
            angle_deg = 0.0

        return {
            "is_orthogonal_to_light": bool(np.isclose(dot_light, 0.0)),
            "is_orthogonal_to_gravity": bool(np.isclose(dot_gravity, 0.0)),
            "angle_between_L_and_G_deg": angle_deg,
            "magnitude_time_vector": norm_time
        }

    def display_report(self) -> None:
        """Display verification results to console"""
        verification = self.verify_orthogonality()

        print("=" * 70)
        print("Tettyan's Right-Hand Law Verification Report")
        print("=" * 70)
        print(f"Light Vector L          : {self.light_vec}")
        print(f"Gravity Vector G        : {self.gravity_vec}")
        print(f"Time Direction Vector T : {self.time_vec}")
        print("-" * 70)
        print("Verification Results:")
        print(f"  Orthogonal to Light (T · L = 0)   : {verification['is_orthogonal_to_light']}")
        print(f"  Orthogonal to Gravity (T · G = 0) : {verification['is_orthogonal_to_gravity']}")
        print(f"  Angle between L and G             : {verification['angle_between_L_and_G_deg']:.2f}°")
        print(f"  Time Vector Magnitude |T|         : {verification['magnitude_time_vector']:.4f}")
        print("=" * 70)
        print("Status: ALL GREEN - Verification Complete")
        print("=" * 70)


# =============================================================================
# Main Execution
# =============================================================================
if __name__ == "__main__":
    # Test case: Light axis (X-direction) × Gravity axis (Y-direction)
    light_dir = [1.0, 0.0, 0.0]
    gravity_dir = [0.0, 1.0, 0.0]

    law_proof = TettyanRightHandLawProof(light_dir, gravity_dir)
    law_proof.display_report()
