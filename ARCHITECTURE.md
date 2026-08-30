<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Stellarator Core — Architecture summary
-->

# Architecture summary

`SCPN-STELLARATOR-CORE` is the device-family owner for stellarator-class
fusion systems (stellarator, heliotron, torsatron) inside the SCPN Reactor
Systems Research Group. The repository is currently `architecture_only`: it
defines the device boundary, its ecosystem contracts, and the validation
tooling that enforces both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns stellarator plant and
experiment truth — configuration policy for externally generated rotational
transform (modular, helical, and continuous-helical coil realisations),
long-pulse/steady-state lifecycle semantics, three-dimensional diagnostic
and clock declarations, actuator-response boundaries, safety-envelope
declarations, and the device-owned CONTROL adapter specification. Solver
mathematics — including the current 3-D equilibrium and stellarator solver
surfaces — stays in `SCPN-FUSION-CORE`; typed semantics stay in
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection keeps the
final veto; portfolio presentation belongs to `SCPN-STUDIO`, towards which
this project is `not_federated`.
