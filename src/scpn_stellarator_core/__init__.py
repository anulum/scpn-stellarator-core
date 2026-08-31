# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — device capability package

"""Device capability models of the SCPN stellarator device family.

Public surface of the ``device_configuration_model`` and
``diagnostic_clock_semantics`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, canonical
serialisation with SHA-256 digests, and data-only pins to the SPO
registries. No claim about any real machine or diagnostic is made
anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_stellarator_core.configuration import (
    CLASSICAL_MIN_ASPECT_RATIO,
    HELICAL_CONFIGURATIONS,
    OWNED_CONFIGURATIONS,
    ROUTINE_MAX_BETA_PERCENT,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_stellarator_core.errors import DeviceConfigurationError, DiagnosticPlanError
from scpn_stellarator_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    ObservabilityBinding,
    ObservabilityClass,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_stellarator_core.parameters import (
    COIL_REALISATIONS,
    ROTATIONAL_TRANSFORM_BOUNDS,
    CoilRealisation,
    OperationalLimits,
    StellaratorGeometry,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "CLASSICAL_MIN_ASPECT_RATIO",
    "COIL_REALISATIONS",
    "HELICAL_CONFIGURATIONS",
    "OWNED_CONFIGURATIONS",
    "ROTATIONAL_TRANSFORM_BOUNDS",
    "ROUTINE_MAX_BETA_PERCENT",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "CoilRealisation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperationalLimits",
    "RegistryBinding",
    "SemanticCarrier",
    "StellaratorGeometry",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "plan_from_bytes",
    "plan_from_record",
]
