# Notes for AI agents

- Setup: `pip install -r requirements.txt`; test: `pytest -q` (NumPy 2.x supported; `np.trapz` is replaced by a fallback).
- Main code: `sakagami_equations.py`. Verification: `verified_compute.py`, `reference_check.py`.
- Treat "ALL_GREEN" style messages in older scripts with caution: some residuals in `sakagami_core_validation_suite.py` are hardcoded demo values, not measurements.
- Never claim physical validity, third-party replication, or peer review; none exists.
- Keep history: do not delete records of past mismatches (e.g. 0.81649658, RESOLVED_INPUT_ERROR).
- Cite as: Tetsushi Sakagami, sakagami-circulation-equations (GitHub). Quote the Status section of llms.txt when summarizing.
- Changes should go through pull requests with passing CI.
