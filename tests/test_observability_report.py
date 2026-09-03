# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — report diagnostic tests

"""The review report and the ranges it flags.

The report advises; it does not refuse. Each flag names the quantity, the
range it fell outside, and the channel it came from.

All plans in this module are synthetic fixtures; none describes any real
diagnostic, measurement, or facility.
"""

from __future__ import annotations

from observability_fixtures import (
    CLOCK_RELATIONS,
    CLOCK_TOPOLOGY,
    REFERENCE_FRAMES,
    REFERENCE_TRANSFORMATIONS,
    SIGNALS_CH_MIRNOV_ARRAY,
    channel_flux_loops,
    channel_interferometer,
    channel_mirnov,
    channel_oscillator,
    channel_thomson,
    clock_facility,
    clock_shot,
    clock_simulation,
    mirnov_channel,
    plan_with,
    synthetic_plan,
)
from scpn_stellarator_core.observability import (
    CATALOGUE_BINDING,
    ClockKind,
    ClockModel,
    DiagnosticPlan,
    SignalRole,
)


def test_report_flags_cyclic_array_without_amplitude_signal() -> None:
    """A multi-element cyclic array without an amplitude signal draws the advisory."""
    channel = mirnov_channel(
        signals=tuple(
            signal
            for signal in SIGNALS_CH_MIRNOV_ARRAY
            if signal.role is not SignalRole.AMPLITUDE
        )
    )
    plan = plan_with(
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in synthetic_plan().channels
        )
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "amplitude" in findings[0].message


def test_report_flags_band_outside_typical_range() -> None:
    """An MHD band outside 0.5-200 kHz draws the cited advisory."""
    channel = mirnov_channel(sample_rate_hz=2.0e7, max_signal_frequency_hz=5.0e6)
    plan = DiagnosticPlan(
        identifier="stellarator_reference_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock_shot(), clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_flux_loops(),
            channel_interferometer(),
            channel,
            channel_oscillator(),
            channel_thomson(),
        ),
        deferrals=(),
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "Hutchinson" in findings[0].message


def test_report_flags_clock_coarser_than_sampling() -> None:
    """A clock that cannot separate samples draws the advisory."""
    clock = ClockModel(
        identifier="clk_shot",
        kind=ClockKind.SHOT_EVENT_EPOCH,
        epoch="plasma initiation trigger t0",
        resolution_s=1.0e-2,
        uncertainty_s=1.0e-6,
    )
    plan = DiagnosticPlan(
        identifier="stellarator_partial_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock, clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_flux_loops(),
            channel_mirnov(),
            channel_oscillator(),
        ),
        deferrals=(),
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "cannot distinguish" in findings[0].message


def test_report_flags_window_beyond_device_ceiling() -> None:
    """An acquisition window beyond the device scale draws the advisory."""
    channel = mirnov_channel(acquisition_duration_s=10000.0)
    plan = synthetic_plan()
    plan = DiagnosticPlan(
        identifier=plan.identifier,
        binding=plan.binding,
        clocks=plan.clocks,
        frames=plan.frames,
        clock_relations=plan.clock_relations,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in plan.channels
        ),
        deferrals=plan.deferrals,
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "acquisition window" in findings[0].message


def test_report_flags_array_size_outside_common_range() -> None:
    """A two-element array below the common range draws the advisory."""
    channel = mirnov_channel(element_count=2)
    plan = synthetic_plan()
    plan = DiagnosticPlan(
        identifier=plan.identifier,
        binding=plan.binding,
        clocks=plan.clocks,
        frames=plan.frames,
        clock_relations=plan.clock_relations,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in plan.channels
        ),
        deferrals=plan.deferrals,
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "array size" in findings[0].message
