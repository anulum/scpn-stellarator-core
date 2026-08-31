<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Stellarator Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-STELLARATOR-CORE` is the device-family owner for stellarator-class
fusion systems in the SCPN Reactor Systems Research Group portfolio. The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_stellarator_core/`, design record ADR 0002,
evidence record `VALIDATION.md#device-configuration-model`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — toroidal magnetic confinement in
   intrinsically three-dimensional equilibria whose rotational transform is
   produced by external non-axisymmetric coils, with no or negligible net
   driven plasma current: the modular-coil `stellarator`
   (three-dimensional torus), the `heliotron` (helical-coil torus), and the
   `torsatron` (continuous-helical-coil torus). The three configurations
   share the 3-D equilibrium description, neoclassical-transport-dominated
   optimisation space, island/divertor edge topology, and current-free
   sustainment principle; they differ in coil realisation, which is a
   configuration parameter. Axisymmetric tokamaks (current-driven transform),
   RFP relaxed states, spheromaks, and FRC plasmas fail that sharing test
   and are excluded.
2. **Primary driver and energy delivery** — external steady-state coil
   systems (modular, helical, or continuous-helical, with trim and control
   coils) establishing the confining field, with plasma initiation and
   heating by electron-cyclotron, neutral-beam, and ion-cyclotron systems.
   There is no central-solenoid inductive current-drive lifecycle.
3. **Plant and shot lifecycle** — long-pulse to steady-state oriented
   operation: field energisation, plasma initiation, heating to the target
   regime, sustained operation, and controlled termination. The
   characteristic lifecycle hazard is radiative or density-limit collapse
   rather than the current-disruption chain of tokamak operation; its
   device-level semantics belong here while its solver physics stays with
   the solver owner.
4. **Diagnostic, reference-frame, and clock model** — declarations that are
   three-dimensional from the outset: flux-surface labels from 3-D
   equilibria, Boozer-type straight-field-line coordinate conventions,
   per-channel laboratory-frame geometry, and clock identities for
   steady-state-relevant time bases.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE` (which currently owns the shared 3-D
   equilibrium and stellarator solver surfaces), review-only semantics
   towards `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-STELLARATOR-CORE (device truth: 3-D configuration policy, lifecycle,
                       diagnostics/clocks, safety envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

Information flows outward from this repository as declarations and
contracts; nothing flows from this repository to an actuator.

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; schema
  changes are versioned and unknown schemas are rejected by consumers.
- The Studio descriptor is derived deterministically from the manifest and
  embeds the manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at version
  `0.1.0-spec`; an implementation may appear only with replay fixtures and
  the evidence the reactor family standard requires.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`; a
  registry upgrade is a reviewed contract change, never a silent re-pin.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate — the
stellarator-specific plant workflows currently living with the solver owner
are the first anticipated candidates — ratification of an SPO
`ControlIntent`-class contract, or Studio federation after a real capability
passes producer and consumer gates. Each arrives as a versioned,
evidence-bound contract change recorded in a new ADR.
