import pytest

from sakagami_core_validation_suite import (
    ConsistencyError,
    SakagamiCoreValidator,
    ValidationConfig,
    _measure_residuals,
)

SMALL = dict(mesh_grid=(24, 24, 24), output_certificate=False)


def test_residuals_are_measured_and_pass():
    r = _measure_residuals(ValidationConfig(**SMALL))
    assert set(r) == {"gauss", "div_b", "continuity", "poisson", "energy"}
    assert all(v < 1e-6 for v in r.values())


def test_residuals_are_deterministic():
    cfg = ValidationConfig(**SMALL)
    assert _measure_residuals(cfg) == _measure_residuals(cfg)


def test_impossible_tolerance_fails():
    cfg = ValidationConfig(gauss_tolerance=1e-30, **SMALL)
    with pytest.raises(ConsistencyError):
        SakagamiCoreValidator(cfg).validate_residuals()
