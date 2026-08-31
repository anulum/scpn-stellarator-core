# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — device configuration container tests

"""Every branch of the device configuration container and its parsers.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from scpn_stellarator_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_stellarator_core.errors import DeviceConfigurationError
from scpn_stellarator_core.parameters import (
    CoilRealisation,
    OperationalLimits,
    StellaratorGeometry,
)

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)


def synthetic_configuration(
    identifier: str = "heliotron",
    kind: str = "helical",
    average_minor_radius_m: float = 0.5,
    volume_averaged_beta_percent: float = 3.0,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration with optional overrides."""
    return DeviceConfiguration(
        identifier=identifier,
        geometry=StellaratorGeometry(
            major_radius_m=5.0,
            average_minor_radius_m=average_minor_radius_m,
            field_periods=5,
            rotational_transform=1.0,
        ),
        coils=CoilRealisation(
            kind=kind,
            coil_count=2 if kind == "helical" else 50,
            auxiliary_coil_count=4,
        ),
        limits=OperationalLimits(
            field_on_axis_t=2.5,
            volume_averaged_beta_percent=volume_averaged_beta_percent,
            flat_top_duration_s=100.0,
        ),
        registry=REGISTRY,
    )


def test_registry_binding_rejects_bad_pins() -> None:
    """Malformed registry pins are rejected."""
    with pytest.raises(DeviceConfigurationError, match=r"registry\.version"):
        RegistryBinding(version="", digest_sha256="0" * 64)
    with pytest.raises(DeviceConfigurationError, match=r"registry\.digest_sha256"):
        RegistryBinding(version="1.0.0", digest_sha256="ZZ")


def test_all_owned_identifiers_construct() -> None:
    """Each owned identifier constructs with its matching coil class."""
    assert synthetic_configuration("heliotron", "helical").identifier == "heliotron"
    assert synthetic_configuration("torsatron", "helical").identifier == "torsatron"
    assert synthetic_configuration("stellarator", "modular").identifier == "stellarator"


def test_unowned_identifier_is_rejected() -> None:
    """Identifiers outside this repository's ownership are rejected."""
    with pytest.raises(DeviceConfigurationError, match="not owned"):
        synthetic_configuration("conventional_tokamak")


def test_helical_class_rejects_modular_coils() -> None:
    """Heliotron and torsatron identifiers require helical coils."""
    for identifier in ("heliotron", "torsatron"):
        with pytest.raises(DeviceConfigurationError, match="requires a helical"):
            synthetic_configuration(identifier, "modular")


def test_stellarator_class_rejects_helical_coils() -> None:
    """The modular stellarator identifier requires modular coils."""
    with pytest.raises(DeviceConfigurationError, match="requires a modular"):
        synthetic_configuration("stellarator", "helical")


def test_consistency_report_clean_and_findings() -> None:
    """The report is empty in-regime and precise out of regime."""
    assert synthetic_configuration().consistency_report() == ()
    low_aspect = synthetic_configuration(average_minor_radius_m=2.0)
    findings = low_aspect.consistency_report()
    assert len(findings) == 1
    assert findings[0].field == "geometry.aspect_ratio"
    high_beta = synthetic_configuration(volume_averaged_beta_percent=6.0)
    findings = high_beta.consistency_report()
    assert len(findings) == 1
    assert findings[0].field == "limits.volume_averaged_beta_percent"


def test_canonical_round_trip_and_digest() -> None:
    """Canonical bytes round-trip losslessly and digest deterministically."""
    configuration = synthetic_configuration()
    data = configuration.canonical_bytes()
    assert data.endswith(b"\n")
    restored = configuration_from_bytes(data)
    assert restored == configuration
    expected = hashlib.sha256(data).hexdigest()
    assert configuration.digest_sha256() == expected


def test_from_record_round_trip_all_classes() -> None:
    """All owned configuration classes round-trip through records."""
    for identifier, kind in (
        ("heliotron", "helical"),
        ("stellarator", "modular"),
        ("torsatron", "helical"),
    ):
        configuration = synthetic_configuration(identifier, kind)
        assert configuration_from_record(configuration.to_record()) == configuration


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (lambda _: "not-a-dict", "record: must be an object"),
        (lambda r: {**r, "extra": 1}, "unknown fields"),
        (lambda r: {**r, "geometry": None}, "geometry: must be an object"),
        (lambda r: {**r, "coils": []}, "coils: must be an object"),
        (lambda r: {**r, "limits": "x"}, "limits: must be an object"),
        (lambda r: {**r, "registry": 7}, "registry: must be an object"),
        (lambda r: {**r, "identifier": 3}, "identifier: must be a string"),
    ],
)
def test_from_record_shape_violations(mutate: Any, fragment: str) -> None:
    """Each record-shape violation is rejected with a precise message."""
    record = synthetic_configuration().to_record()
    with pytest.raises(DeviceConfigurationError, match=fragment):
        configuration_from_record(mutate(record))


def test_from_record_field_type_violations() -> None:
    """Nested field-type violations name the offending field."""
    record = synthetic_configuration().to_record()
    record["geometry"]["major_radius_m"] = "big"
    with pytest.raises(DeviceConfigurationError, match="major_radius_m: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["geometry"]["major_radius_m"] = True
    with pytest.raises(DeviceConfigurationError, match="major_radius_m: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["geometry"]["field_periods"] = 2.5
    with pytest.raises(DeviceConfigurationError, match="field_periods: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["geometry"]["field_periods"] = True
    with pytest.raises(DeviceConfigurationError, match="field_periods: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["coils"]["kind"] = 5
    with pytest.raises(DeviceConfigurationError, match="kind: must be a string"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["registry"]["version"] = None
    with pytest.raises(DeviceConfigurationError, match="version: must be a string"):
        configuration_from_record(record)


def test_from_bytes_rejects_invalid_documents() -> None:
    """Invalid UTF-8, invalid JSON, and non-finite literals are rejected."""
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"\xff\xfe")
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"{not json")
    record = synthetic_configuration().to_record()
    text = json.dumps(record).replace("5.0", "NaN", 1)
    with pytest.raises(DeviceConfigurationError, match="non-finite JSON literal"):
        configuration_from_bytes(text.encode("utf-8"))


def test_integer_accepted_where_number_expected() -> None:
    """Integral JSON numbers are accepted for real-valued fields."""
    record = synthetic_configuration().to_record()
    record["limits"]["field_on_axis_t"] = 3
    restored = configuration_from_record(record)
    assert restored.limits.field_on_axis_t == 3.0
