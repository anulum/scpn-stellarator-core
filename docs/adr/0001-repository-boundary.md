<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Stellarator Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. Stellarator-class devices previously
had no dedicated device home; the shared solver laboratory owns the 3-D
equilibrium and stellarator solver surfaces. A boundary decision was needed
on which configurations this repository owns, what it excludes, and how it
relates to the solver, semantic, control, presentation, and
machine-protection layers.

## Decision

1. `SCPN-STELLARATOR-CORE` owns exactly three registry configurations:
   `stellarator`, `heliotron`, and `torsatron`. All three produce rotational
   transform with external non-axisymmetric coils and no driven-current
   lifecycle, share the 3-D equilibrium and diagnostic model, the
   steady-state-oriented lifecycle, and one solver/evidence/control
   contract; the coil realisation (modular, helical, continuous-helical) is
   a configuration parameter, not a repository boundary.
2. The repository owns device-level truth only: configuration policy,
   lifecycle semantics, three-dimensional diagnostic/reference-frame/clock
   declarations, actuator-response model boundaries, the safety-envelope
   declaration, and the device-owned CONTROL adapter specification.
3. Solver mathematics — including the current stellarator, VMEC-class 3-D
   equilibrium, and free-boundary surfaces — remains in `SCPN-FUSION-CORE`
   until an exact surface passes the family migration gate. No solver code
   is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One combined toroidal-confinement repository** (tokamaks +
  stellarators): rejected — the transform-generation principle, coil
  topology, current-drive lifecycle, and 3-D diagnostic model differ on
  surfaces 1, 2, 3, and 4.
- **Separate repositories per coil realisation** (stellarator vs heliotron
  vs torsatron): rejected — all five boundary surfaces are substantially
  shared; the split would triplicate every contract for a coil-layout
  difference.
- **Absorbing the existing stellarator solver code at scaffold time**:
  rejected — it forks mathematical ownership before parity evidence exists
  and violates the migration gate; the architecture record instead names
  those workflows as the first anticipated migration candidates.

## Consequences

- Downstream consumers get one stable identity per stellarator-family
  configuration and a manifest to bind against.
- Stellarator-specific plant workflows in the solver laboratory have a
  declared future home, reachable only through the migration gate.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future ADR
  records any such change here.
