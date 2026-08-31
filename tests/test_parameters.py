# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — parameter model tests

"""Every validation branch of the stellarator parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_stellarator_core.errors import DeviceConfigurationError
from scpn_stellarator_core.parameters import (
    CoilRealisation,
    OperationalLimits,
    StellaratorGeometry,
    require_finite,
    require_positive,
)


def synthetic_geometry(**overrides: Any) -> StellaratorGeometry:
    """Build a valid synthetic geometry with optional field overrides."""
    values: dict[str, Any] = {
        "major_radius_m": 5.0,
        "average_minor_radius_m": 0.5,
        "field_periods": 5,
        "rotational_transform": 1.0,
    }
    values.update(overrides)
    return StellaratorGeometry(**values)


def synthetic_limits(**overrides: float) -> OperationalLimits:
    """Build valid synthetic limits with optional field overrides."""
    values: dict[str, float] = {
        "field_on_axis_t": 2.5,
        "volume_averaged_beta_percent": 3.0,
        "flat_top_duration_s": 100.0,
    }
    values.update(overrides)
    return OperationalLimits(**values)


def test_valid_geometry_and_aspect_ratio() -> None:
    """A valid configuration constructs and derives its aspect ratio."""
    geometry = synthetic_geometry()
    assert geometry.aspect_ratio == pytest.approx(10.0)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"major_radius_m": 0.0}, "major_radius_m"),
        ({"average_minor_radius_m": -1.0}, "average_minor_radius_m"),
        ({"average_minor_radius_m": 5.0}, "strictly smaller than"),
        ({"average_minor_radius_m": 6.0}, "strictly smaller than"),
        ({"field_periods": 0}, "field_periods"),
        ({"rotational_transform": 0.0}, "rotational_transform"),
        ({"rotational_transform": 2.1}, "rotational_transform"),
        ({"rotational_transform": math.nan}, "rotational_transform"),
    ],
)
def test_invalid_geometry_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each geometric invariant violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_geometry(**overrides)


def test_transform_bound_is_inclusive_at_two() -> None:
    """The rotational-transform upper model bound is inclusive."""
    assert synthetic_geometry(rotational_transform=2.0).rotational_transform == 2.0


def test_valid_coil_realisations() -> None:
    """Both documented coil classes construct with their counts."""
    helical = CoilRealisation(kind="helical", coil_count=2, auxiliary_coil_count=4)
    modular = CoilRealisation(kind="modular", coil_count=50, auxiliary_coil_count=0)
    assert helical.kind == "helical"
    assert modular.auxiliary_coil_count == 0


@pytest.mark.parametrize(
    ("kind", "coil_count", "auxiliary", "fragment"),
    [
        ("saddle", 2, 0, "kind"),
        ("helical", 0, 0, "coil_count"),
        ("modular", 10, -1, "auxiliary_coil_count"),
    ],
)
def test_invalid_coil_realisation_is_rejected(
    kind: str, coil_count: int, auxiliary: int, fragment: str
) -> None:
    """Each coil-realisation violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        CoilRealisation(
            kind=kind, coil_count=coil_count, auxiliary_coil_count=auxiliary
        )


def test_valid_limits_construct() -> None:
    """A valid limit declaration constructs unchanged."""
    limits = synthetic_limits()
    assert limits.field_on_axis_t == 2.5


def test_beta_bound_is_inclusive_at_ten() -> None:
    """The beta model bound is inclusive at ten percent."""
    assert (
        synthetic_limits(volume_averaged_beta_percent=10.0).volume_averaged_beta_percent
        == 10.0
    )


def test_zero_flat_top_is_valid() -> None:
    """A zero flat-top duration is representable."""
    assert synthetic_limits(flat_top_duration_s=0.0).flat_top_duration_s == 0.0


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"field_on_axis_t": 0.0}, "field_on_axis_t"),
        ({"volume_averaged_beta_percent": 0.0}, "volume_averaged_beta_percent"),
        ({"volume_averaged_beta_percent": 10.5}, "volume_averaged_beta_percent"),
        ({"volume_averaged_beta_percent": math.nan}, "volume_averaged_beta_percent"),
        ({"flat_top_duration_s": -1.0}, "flat_top_duration_s"),
        ({"flat_top_duration_s": math.inf}, "flat_top_duration_s"),
    ],
)
def test_invalid_limits_are_rejected(
    overrides: dict[str, float], fragment: str
) -> None:
    """Each limit violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_limits(**overrides)
