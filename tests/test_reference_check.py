import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reference_check as rc  # noqa: E402


class ReferenceCheckTests(unittest.TestCase):
    def test_no_mismatch_and_log_written(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "ref.jsonl"
            s = rc.run_reference_check(log_file=log)
            self.assertEqual(s["mismatch"], 0)
            self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), len(rc.CHECKS))

    def test_unverified_is_not_counted_as_match(self):
        with tempfile.TemporaryDirectory() as d:
            s = rc.run_reference_check(log_file=Path(d) / "r.jsonl")
            self.assertGreaterEqual(s["unverified"], 1)
            self.assertEqual(s["match"] + s["unverified"] + s["mismatch"], len(rc.CHECKS))


if __name__ == "__main__":
    unittest.main()
