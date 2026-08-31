<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Stellarator Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane of the roadmap is the device configuration model — the
typed, validated parameter surface for the three stellarator-class
registry configurations this repository owns (`heliotron`,
`stellarator`, `torsatron`). Landing it requires the same two decisions
the family's pilot (the tokamak device core) ratified: the claim
boundary, and the meaning of the repository-level `evidence_maturity`
field once per-capability states exist.

## Decision

1. The package `scpn_stellarator_core` implements the device
   configuration model as frozen, strictly typed value objects:
   three-dimensional stellarator geometry (major/average-minor radius,
   toroidal field periods, external rotational transform), the coil
   realisation, and operational limits, composed under exactly one owned
   registry identifier.
2. Claim boundary — the capability claims ONLY: internal-consistency
   validation of parameter sets, physically standard derived estimates
   with documented applicability bounds, canonical serialisation with
   SHA-256 digest, and binding to the pinned SPO reactor registry
   version and digest. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Coil-realisation invariant (hard): `heliotron` and `torsatron`
   configurations require a continuous-helical-coil realisation, the
   modular `stellarator` class requires a modular-coil realisation —
   the classical distinction of the stellarator family (L. Spitzer,
   Phys. Fluids 1 (1958) 253; K. Uo, J. Phys. Soc. Japan 16 (1961)
   1380). An identifier that contradicts its coil class is rejected.
4. Advisory estimates, reported by `consistency_report()` and never
   clamped: aspect ratio below 3 is flagged (outside the classical
   large-aspect-ratio stellarator regime), and volume-averaged beta
   above 5 % is flagged (above the routinely sustained stellarator
   values, cf. LHD ⟨β⟩ ≈ 5 %; Sakakibara et al., Nucl. Fusion 55
   (2015) 083020). Rotational transform is bounded to (0, 2] as a model
   bound.
5. Repository-level `evidence_maturity` = the highest state claimed by
   any entry in `capabilities`; per-capability states are the
   authoritative claim surface (family ADR 0002 semantics, identical to
   the pilot).
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (diagnostic semantics with three-dimensional flux/Boozer
  conventions, safety envelope) build on these types; maturity advances
  per capability only with the evidence the family standard requires.
