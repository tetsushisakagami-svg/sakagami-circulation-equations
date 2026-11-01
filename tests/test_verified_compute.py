import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import verified_compute as vc  # noqa: E402


class VerifiedComputeTests(unittest.TestCase):
    def test_analytic_reference_is_one(self):
        self.assertAlmostEqual(vc.analytic_circulation_rate(), 1.0, places=12)

    def test_suite_verified_with_defaults(self):
        report = vc.run_verified_suite()
        self.assertTrue(report["all_verified"])
        for r in report["results"]:
            self.assertEqual(r["status"], "VERIFIED")
            self.assertLessEqual(r["abs_error"], r["tolerance"])

    def test_report_is_json_serializable(self):
        json.dumps(vc.run_verified_suite())

    def test_impossible_tolerance_fails_honestly(self):
        # 許容誤差を厳しくすると、実測誤差に基づいて FAILED になる（固定PASSではない）
        res = vc.verify_circulation_rate(num_points=100, tolerance=1e-20)
        self.assertEqual(res.status, "FAILED")

    def test_invalid_inputs_rejected(self):
        for bad in (0, -5, 10, 1.5, "100", True, None, vc.MAX_POINTS + 1):
            with self.assertRaises(vc.InvalidInputError):
                vc.verify_circulation_rate(num_points=bad)
        for bad in (0, 1, -1, "x", True, None):
            with self.assertRaises(vc.InvalidInputError):
                vc.verify_circulation_rate(tolerance=bad)


if __name__ == "__main__":
    unittest.main()
