# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Stellarator Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the three owned registry identifiers, the
coil-class invariant enforced by the configuration model, and the
declared field-period/rotational-transform geometry — never from any
equilibrium solver. The right-hand text panel states only facts backed
by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — flux-surface cross-sections rotating across
  half a field period (used by ``README.md``).
- ``repo_header_coil_invariant.png`` — modular non-planar coils versus
  the continuous helical winding, the enforced coil-class split.
- ``repo_header_rotational_transform.png`` — field lines of declared
  slope iota-bar on the unrolled magnetic surface.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:  # pragma: no cover - typing aid only
    from numpy.typing import NDArray

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100
FIELD_PERIODS = 5

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configurations", "stellarator · heliotron · torsatron"),
    ("Coil-Class Invariant", "modular vs helical, enforced in code"),
    ("Configuration Model", "geometry · coils · limits, SHA-256 canon"),
    ("Diagnostics & Clocks", "fail-closed vs pinned SPO catalogue"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def rotating_section(
    toroidal_angle: float,
    samples: int = 400,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return a stylised stellarator boundary at ``toroidal_angle``.

    The elongation direction rotates with the toroidal angle at the
    declared field-period count — the visual signature of the
    three-dimensional confinement family this repository owns.
    """
    theta = np.linspace(0.0, 2.0 * np.pi, samples)
    rotation = FIELD_PERIODS * toroidal_angle / 2.0
    elongation = 0.55 + 0.45 * np.cos(2.0 * (theta - rotation))
    radius = (1.0 + 0.28 * np.cos(theta - 3.0 * rotation)) * np.sqrt(elongation + 0.35)
    return radius * np.cos(theta), 1.35 * radius * np.sin(theta)


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.74,
        "STELLARATOR",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.685,
        "CORE",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.625,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.585, 0.585], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.525
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def generate_rotating_sections() -> None:
    """Generate ``repo_header.png``: sections across half a field period."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 2.6)
    angles = np.linspace(0.0, np.pi / FIELD_PERIODS, 4)
    centres = [1.55, 3.85, 6.15, 8.45]
    for angle, centre in zip(angles, centres, strict=True):
        grid_x = np.linspace(centre - 1.5, centre + 1.5, 120)
        grid_z = np.linspace(-2.2, 2.2, 120)
        mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
        rho = np.sqrt(((mesh_x - centre) / 1.1) ** 2 + (mesh_z / 1.5) ** 2)
        ax.contourf(
            mesh_x,
            mesh_z,
            np.exp(-rho * 2.2),
            levels=20,
            cmap=_glow_cmap(),
            alpha=0.55,
        )
        bound_x, bound_z = rotating_section(angle)
        for fraction in np.linspace(0.25, 1.0, 6):
            outermost = fraction == 1.0
            ax.plot(
                centre + bound_x * fraction,
                bound_z * fraction,
                color=CYAN,
                lw=1.9 if outermost else 0.6,
                alpha=0.95 if outermost else 0.32,
            )
        ax.plot(centre, 0, ".", color=MAGENTA, ms=4, alpha=0.9)
        degrees = angle * 180.0 / np.pi
        ax.text(
            centre,
            -2.38,
            f"φ = {degrees:.0f}°",
            color=PROBE,
            fontsize=8.5,
            fontfamily="monospace",
            ha="center",
            alpha=0.9,
        )
    ax.annotate(
        "",
        xy=(9.55, 1.9),
        xytext=(0.45, 1.9),
        arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 1.0, "alpha": 0.6},
    )
    ax.text(
        5.0,
        2.15,
        f"one half field period · N_fp = {FIELD_PERIODS}",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Rotating Sections, Owned Truth")
    _save(fig, plt, "repo_header.png")


def generate_coil_invariant() -> None:
    """Generate ``repo_header_coil_invariant.png``: the coil-class split."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    segment = np.linspace(-0.9, 0.9, 200)
    ax.plot(
        1.0 + 2.4 * (segment + 0.9) / 1.8,
        0.55 * np.sin(2.2 * segment),
        color=STEEL,
        lw=14,
        alpha=0.25,
        solid_capstyle="round",
    )
    for index, along in enumerate(np.linspace(-0.75, 0.75, 6)):
        centre_x = 1.0 + 2.4 * (along + 0.9) / 1.8
        theta = np.linspace(0.0, 2.0 * np.pi, 200)
        wobble = 0.16 * np.sin(3.0 * theta + 1.7 * index)
        coil_x = (
            centre_x
            + (0.55 + wobble) * 0.45 * np.cos(theta)
            + 0.55 * np.sin(2.2 * along) * 0.2
        )
        coil_z = (0.95 + wobble) * np.sin(theta) + 0.55 * np.sin(2.2 * along)
        ax.plot(coil_x, coil_z, color=CYAN, lw=1.8, alpha=0.85)
    ax.text(
        2.2,
        2.65,
        "modular non-planar coils",
        color="#99bbdd",
        fontsize=9.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        2.2,
        -2.75,
        "stellarator · Spitzer, Phys. Fluids 1 (1958) 253",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot(
        5.8 + 2.4 * (segment + 0.9) / 1.8,
        0.55 * np.sin(2.2 * segment),
        color=STEEL,
        lw=14,
        alpha=0.25,
        solid_capstyle="round",
    )
    along = np.linspace(0.0, 1.0, 900)
    for phase in (0.0, np.pi):
        base = 0.55 * np.sin(2.2 * (along * 1.8 - 0.9))
        wind_z = base + 0.95 * np.sin(2.0 * np.pi * 2.5 * along + phase)
        wind_x = 5.8 + 2.4 * along + 0.20 * np.cos(2.0 * np.pi * 2.5 * along + phase)
        ax.plot(wind_x, wind_z, color=MAGENTA, lw=1.8, alpha=0.9)
    ax.text(
        7.0,
        2.65,
        "continuous helical winding",
        color="#ffaaff",
        fontsize=9.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        7.0,
        -2.75,
        "heliotron/torsatron · Uo, JPSJ 16 (1961) 1380",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot([4.55, 4.55], [-2.35, 2.4], color=STEEL, lw=0.8, alpha=0.4)
    ax.text(
        4.55,
        -3.05,
        "coil class contradicting its identifier is rejected",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )
    _text_panel(fig, "Three Identifiers, One Coil Invariant")
    _save(fig, plt, "repo_header_coil_invariant.png")


def generate_rotational_transform() -> None:
    """Generate ``repo_header_rotational_transform.png``: iota winding."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    for grid_x in np.linspace(0.4, 9.6, 21):
        ax.plot([grid_x, grid_x], [0.8, 9.2], color=STEEL, lw=0.5, alpha=0.22)
    for grid_y in np.linspace(0.8, 9.2, 11):
        ax.plot([0.4, 9.6], [grid_y, grid_y], color=STEEL, lw=0.5, alpha=0.22)

    iota_bar = 0.618
    span = 9.2 - 0.8
    styles = [
        (CYAN, 0.95, 1.7),
        ("#66d4ff", 0.55, 1.0),
        ("#3399cc", 0.4, 1.0),
        (MAGENTA, 0.8, 1.7),
    ]
    for offset_index, (colour, alpha, lw) in enumerate(styles):
        phi = np.linspace(0.4, 9.6, 2000)
        theta = 0.8 + offset_index * 1.9 + iota_bar * (phi - 0.4) * (span / 9.2)
        theta = 0.8 + np.mod(theta - 0.8, span)
        wraps = np.abs(np.diff(theta)) > span / 2.0
        masked = theta.copy()
        masked[1:][wraps] = np.nan
        ax.plot(phi, masked, color=colour, lw=lw, alpha=alpha)

    for period in range(FIELD_PERIODS + 1):
        tick_x = 0.4 + period * (9.2 / FIELD_PERIODS)
        ax.plot([tick_x, tick_x], [0.55, 0.8], color=PROBE, lw=1.2, alpha=0.8)
    ax.text(
        5.0,
        0.22,
        f"toroidal angle φ · {FIELD_PERIODS} field periods",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        0.28,
        5.0,
        "poloidal angle θ",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        va="center",
        rotation=90,
    )
    ax.text(
        5.0,
        9.55,
        "ῑ (iota-bar): externally produced, validated here",
        color=PROBE,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    _text_panel(fig, "Rotational Transform As Declared Data")
    _save(fig, plt, "repo_header_rotational_transform.png")


if __name__ == "__main__":
    generate_rotating_sections()
    generate_coil_invariant()
    generate_rotational_transform()
