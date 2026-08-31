# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — stellarator parameter model

"""Validated parameter objects of a stellarator-class configuration.

The model bounds documented here are modelling-domain bounds of this
repository, not claims about any real machine: the external rotational
transform is accepted in ``(0, 2]`` and the field-period count must be a
positive integer, which covers the published stellarator, heliotron, and
torsatron design space while rejecting unphysical inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_stellarator_core.errors import DeviceConfigurationError

ROTATIONAL_TRANSFORM_BOUNDS: Final = (0.0, 2.0)
COIL_REALISATIONS: Final = ("helical", "modular")


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class StellaratorGeometry:
    """Three-dimensional stellarator geometry parameters.

    Parameters
    ----------
    major_radius_m
        Plasma major radius ``R0`` in metres; strictly positive.
    average_minor_radius_m
        Effective (flux-surface averaged) minor radius ``a`` in metres;
        strictly positive and strictly smaller than ``major_radius_m``.
    field_periods
        Number of toroidal field periods ``N_fp``; at least one.
    rotational_transform
        Externally produced rotational transform ``iota-bar`` at the
        edge; accepted in ``(0, 2]`` as a model bound (vacuum transform
        of published stellarator-class configurations).

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or outside its model bound.
    """

    major_radius_m: float
    average_minor_radius_m: float
    field_periods: int
    rotational_transform: float

    def __post_init__(self) -> None:
        """Validate every geometric invariant.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or outside its model bound.
        """
        require_positive("major_radius_m", self.major_radius_m)
        require_positive("average_minor_radius_m", self.average_minor_radius_m)
        if self.average_minor_radius_m >= self.major_radius_m:
            raise DeviceConfigurationError(
                "average_minor_radius_m: must be strictly smaller than "
                f"major_radius_m ({self.average_minor_radius_m!r} >= "
                f"{self.major_radius_m!r})"
            )
        if self.field_periods < 1:
            raise DeviceConfigurationError(
                f"field_periods: must be at least 1, got {self.field_periods!r}"
            )
        low, high = ROTATIONAL_TRANSFORM_BOUNDS
        require_finite("rotational_transform", self.rotational_transform)
        if not low < self.rotational_transform <= high:
            raise DeviceConfigurationError(
                f"rotational_transform: must be within ({low}, {high}], "
                f"got {self.rotational_transform!r}"
            )

    @property
    def aspect_ratio(self) -> float:
        """Aspect ratio ``A = R0 / a`` of the validated configuration.

        Returns
        -------
        float
            Ratio of major to average minor radius; always greater than
            one.
        """
        return self.major_radius_m / self.average_minor_radius_m


@dataclass(frozen=True, slots=True)
class CoilRealisation:
    """Coil realisation of a stellarator-class configuration.

    Parameters
    ----------
    kind
        Coil-set class: ``helical`` (continuous helical windings of the
        heliotron/torsatron line) or ``modular`` (discrete non-planar
        coils of the modular stellarator line).
    coil_count
        Number of principal field coils; at least one.
    auxiliary_coil_count
        Number of auxiliary (planar/trim) coils; zero or more.

    Raises
    ------
    DeviceConfigurationError
        If the kind is unknown or a count violates its lower bound.
    """

    kind: str
    coil_count: int
    auxiliary_coil_count: int

    def __post_init__(self) -> None:
        """Validate the coil-realisation invariants.

        Raises
        ------
        DeviceConfigurationError
            If the kind is unknown or a count violates its lower bound.
        """
        if self.kind not in COIL_REALISATIONS:
            raise DeviceConfigurationError(
                f"kind: must be one of {COIL_REALISATIONS!r}, got {self.kind!r}"
            )
        if self.coil_count < 1:
            raise DeviceConfigurationError(
                f"coil_count: must be at least 1, got {self.coil_count!r}"
            )
        if self.auxiliary_coil_count < 0:
            raise DeviceConfigurationError(
                "auxiliary_coil_count: must be non-negative, "
                f"got {self.auxiliary_coil_count!r}"
            )


@dataclass(frozen=True, slots=True)
class OperationalLimits:
    """Declared operating-point limits of a stellarator configuration.

    Parameters
    ----------
    field_on_axis_t
        Magnetic field on axis ``B0`` in tesla; strictly positive.
    volume_averaged_beta_percent
        Declared volume-averaged plasma beta in percent; accepted in
        ``(0, 10]`` as a model bound.
    flat_top_duration_s
        Declared flat-top duration in seconds; non-negative (stellarator
        confinement needs no plasma current, so long pulses are natural,
        but the declaration itself carries no endurance claim).

    Raises
    ------
    DeviceConfigurationError
        If any limit is non-finite or outside its model bound.
    """

    field_on_axis_t: float
    volume_averaged_beta_percent: float
    flat_top_duration_s: float

    def __post_init__(self) -> None:
        """Validate every declared limit.

        Raises
        ------
        DeviceConfigurationError
            If any limit is non-finite or outside its model bound.
        """
        require_positive("field_on_axis_t", self.field_on_axis_t)
        require_finite(
            "volume_averaged_beta_percent", self.volume_averaged_beta_percent
        )
        if not 0.0 < self.volume_averaged_beta_percent <= 10.0:
            raise DeviceConfigurationError(
                "volume_averaged_beta_percent: must be within (0, 10], "
                f"got {self.volume_averaged_beta_percent!r}"
            )
        require_finite("flat_top_duration_s", self.flat_top_duration_s)
        if self.flat_top_duration_s < 0.0:
            raise DeviceConfigurationError(
                "flat_top_duration_s: must be non-negative, "
                f"got {self.flat_top_duration_s!r}"
            )
