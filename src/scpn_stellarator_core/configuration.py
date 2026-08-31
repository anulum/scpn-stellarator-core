# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — device configuration container

"""Device configuration container bound to the SPO reactor registry.

A :class:`DeviceConfiguration` composes validated geometry, coil
realisation, and operational limits under exactly one of the three
registry identifiers this repository owns. The coil-class invariant
follows the classical family distinction — continuous helical windings
for the heliotron/torsatron line (K. Uo, J. Phys. Soc. Japan 16 (1961)
1380), modular non-planar coils for the modular stellarator line
(L. Spitzer, Phys. Fluids 1 (1958) 253) — and an identifier that
contradicts its coil class is rejected. Serialisation is canonical
(sorted keys, no NaN or infinity accepted anywhere) and the SHA-256
digest of those bytes identifies the exact parameter set. The registry
binding is a data pin only — this package never imports SCPN Phase
Orchestrator code.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Final

from scpn_stellarator_core.errors import DeviceConfigurationError
from scpn_stellarator_core.parameters import (
    CoilRealisation,
    OperationalLimits,
    StellaratorGeometry,
)

OWNED_CONFIGURATIONS: Final = ("heliotron", "stellarator", "torsatron")
HELICAL_CONFIGURATIONS: Final = ("heliotron", "torsatron")
CLASSICAL_MIN_ASPECT_RATIO: Final = 3.0
ROUTINE_MAX_BETA_PERCENT: Final = 5.0
HEX_DIGEST: Final = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class RegistryBinding:
    """Pin to one SPO reactor registry release.

    Parameters
    ----------
    version
        Registry release version; non-empty.
    digest_sha256
        Registry digest as 64 lowercase hexadecimal characters.

    Raises
    ------
    DeviceConfigurationError
        If either pin component is malformed.
    """

    version: str
    digest_sha256: str

    def __post_init__(self) -> None:
        """Validate the registry pin.

        Raises
        ------
        DeviceConfigurationError
            If either pin component is malformed.
        """
        if not self.version:
            raise DeviceConfigurationError("registry.version: must be non-empty")
        if HEX_DIGEST.fullmatch(self.digest_sha256) is None:
            raise DeviceConfigurationError(
                "registry.digest_sha256: must be 64 lowercase hexadecimal "
                f"characters, got {self.digest_sha256!r}"
            )


@dataclass(frozen=True, slots=True)
class ConsistencyFinding:
    """One internal-consistency finding on a device configuration.

    Parameters
    ----------
    field
        Dotted field path the finding refers to.
    message
        Human-readable statement of the inconsistency.
    """

    field: str
    message: str


@dataclass(frozen=True, slots=True)
class DeviceConfiguration:
    """Validated stellarator-class device configuration.

    Parameters
    ----------
    identifier
        SPO registry configuration identifier; one of ``heliotron``,
        ``stellarator``, or ``torsatron``.
    geometry
        Validated three-dimensional geometry.
    coils
        Validated coil realisation.
    limits
        Validated operational limits.
    registry
        Pin to the SPO reactor registry release the identifier belongs
        to.

    Raises
    ------
    DeviceConfigurationError
        If the identifier is not owned by this repository or contradicts
        its coil-realisation class.
    """

    identifier: str
    geometry: StellaratorGeometry
    coils: CoilRealisation
    limits: OperationalLimits
    registry: RegistryBinding

    def __post_init__(self) -> None:
        """Validate identifier ownership and the coil-class invariant.

        Raises
        ------
        DeviceConfigurationError
            If the identifier is not owned by this repository or
            contradicts its coil-realisation class.
        """
        if self.identifier not in OWNED_CONFIGURATIONS:
            raise DeviceConfigurationError(
                f"identifier: {self.identifier!r} is not owned by "
                f"SCPN-STELLARATOR-CORE; owned: {OWNED_CONFIGURATIONS!r}"
            )
        if self.identifier in HELICAL_CONFIGURATIONS and self.coils.kind != "helical":
            raise DeviceConfigurationError(
                f"identifier: {self.identifier} requires a helical coil "
                f"realisation, got {self.coils.kind!r}"
            )
        if self.identifier == "stellarator" and self.coils.kind != "modular":
            raise DeviceConfigurationError(
                "identifier: stellarator requires a modular coil "
                f"realisation, got {self.coils.kind!r}"
            )

    def consistency_report(self) -> tuple[ConsistencyFinding, ...]:
        """Report physics-consistency findings without failing.

        Returns
        -------
        tuple of ConsistencyFinding
            Advisory findings from the documented estimates; empty when
            the declared operating point sits in the classical regime.
            Findings are advisory instruments, not machine claims.
        """
        findings: list[ConsistencyFinding] = []
        aspect_ratio = self.geometry.aspect_ratio
        if aspect_ratio < CLASSICAL_MIN_ASPECT_RATIO:
            findings.append(
                ConsistencyFinding(
                    field="geometry.aspect_ratio",
                    message=(
                        f"aspect ratio {aspect_ratio:.3f} is below the "
                        "classical stellarator regime bound "
                        f"{CLASSICAL_MIN_ASPECT_RATIO:.1f}"
                    ),
                )
            )
        beta = self.limits.volume_averaged_beta_percent
        if beta > ROUTINE_MAX_BETA_PERCENT:
            findings.append(
                ConsistencyFinding(
                    field="limits.volume_averaged_beta_percent",
                    message=(
                        f"volume-averaged beta {beta:.2f} % exceeds the "
                        "routinely sustained stellarator value "
                        f"{ROUTINE_MAX_BETA_PERCENT:.1f} % (LHD-class)"
                    ),
                )
            )
        return tuple(findings)

    def to_record(self) -> dict[str, Any]:
        """Project the configuration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Nested record with every declared parameter.
        """
        return {
            "identifier": self.identifier,
            "geometry": {
                "major_radius_m": self.geometry.major_radius_m,
                "average_minor_radius_m": self.geometry.average_minor_radius_m,
                "field_periods": self.geometry.field_periods,
                "rotational_transform": self.geometry.rotational_transform,
            },
            "coils": {
                "kind": self.coils.kind,
                "coil_count": self.coils.coil_count,
                "auxiliary_coil_count": self.coils.auxiliary_coil_count,
            },
            "limits": {
                "field_on_axis_t": self.limits.field_on_axis_t,
                "volume_averaged_beta_percent": (
                    self.limits.volume_averaged_beta_percent
                ),
                "flat_top_duration_s": self.limits.flat_top_duration_s,
            },
            "registry": {
                "version": self.registry.version,
                "digest_sha256": self.registry.digest_sha256,
            },
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the configuration canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact parameter set.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _require_mapping(record: dict[str, Any], field: str) -> dict[str, Any]:
    """Return one required mapping field of a record.

    Parameters
    ----------
    record
        Parent mapping under inspection.
    field
        Key that must hold a mapping.

    Returns
    -------
    dict[str, Any]
        The nested mapping.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a mapping.
    """
    value = record.get(field)
    if not isinstance(value, dict):
        raise DeviceConfigurationError(f"{field}: must be an object")
    return value


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a real number.

    Returns
    -------
    float
        The numeric value; booleans are rejected.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a real number.
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DeviceConfigurationError(f"{field}: must be a number, got {value!r}")
    return float(value)


def _integer(record: dict[str, Any], field: str) -> int:
    """Return one required integer field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold an integer.

    Returns
    -------
    int
        The integer value; booleans are rejected.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not an integer.
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise DeviceConfigurationError(f"{field}: must be an integer, got {value!r}")
    return value


def _string(record: dict[str, Any], field: str) -> str:
    """Return one required string field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a string.

    Returns
    -------
    str
        The string value.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a string.
    """
    value = record.get(field)
    if not isinstance(value, str):
        raise DeviceConfigurationError(f"{field}: must be a string, got {value!r}")
    return value


def configuration_from_record(record: Any) -> DeviceConfiguration:
    """Build a validated configuration from a decoded record.

    Parameters
    ----------
    record
        Decoded JSON object in the shape produced by
        :meth:`DeviceConfiguration.to_record`.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the record shape or any value violates the model.
    """
    if not isinstance(record, dict):
        raise DeviceConfigurationError("record: must be an object")
    known = {"identifier", "geometry", "coils", "limits", "registry"}
    unknown = sorted(set(record) - known)
    if unknown:
        raise DeviceConfigurationError(f"record: unknown fields {unknown!r}")
    geometry = _require_mapping(record, "geometry")
    coils = _require_mapping(record, "coils")
    limits = _require_mapping(record, "limits")
    registry = _require_mapping(record, "registry")
    return DeviceConfiguration(
        identifier=_string(record, "identifier"),
        geometry=StellaratorGeometry(
            major_radius_m=_number(geometry, "major_radius_m"),
            average_minor_radius_m=_number(geometry, "average_minor_radius_m"),
            field_periods=_integer(geometry, "field_periods"),
            rotational_transform=_number(geometry, "rotational_transform"),
        ),
        coils=CoilRealisation(
            kind=_string(coils, "kind"),
            coil_count=_integer(coils, "coil_count"),
            auxiliary_coil_count=_integer(coils, "auxiliary_coil_count"),
        ),
        limits=OperationalLimits(
            field_on_axis_t=_number(limits, "field_on_axis_t"),
            volume_averaged_beta_percent=_number(
                limits, "volume_averaged_beta_percent"
            ),
            flat_top_duration_s=_number(limits, "flat_top_duration_s"),
        ),
        registry=RegistryBinding(
            version=_string(registry, "version"),
            digest_sha256=_string(registry, "digest_sha256"),
        ),
    )


def configuration_from_bytes(data: bytes) -> DeviceConfiguration:
    """Build a validated configuration from canonical JSON bytes.

    Parameters
    ----------
    data
        UTF-8 JSON document; NaN and infinity literals are rejected.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the document is not valid strict JSON or violates the model.
    """

    def _reject_constant(literal: str) -> float:
        raise DeviceConfigurationError(
            f"record: non-finite JSON literal {literal!r} is rejected"
        )

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeviceConfigurationError(f"record: invalid JSON document: {exc}") from exc
    return configuration_from_record(record)
