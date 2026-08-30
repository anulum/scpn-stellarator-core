<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Stellarator Core — CONTROL adapter specification
-->

# CONTROL adapter specification

**Adapter identifier:** `scpn-stellarator-core.control-adapter`  
**Contract version:** `0.1.0-spec` (specification only — **no implementation
exists**)  
**Consumer:** `SCPN-CONTROL` plugin protocol

This document is the device-owned contract through which a future
stellarator adapter would supply device truth to the SCPN control plane.
Publishing this specification creates no capability and no claim: an
implementation may appear only with the replay fixtures and evidence the
reactor family standard requires for `control_research_ready`, and it enters
CONTROL only through CONTROL's installed public contract with real-surface
tests.

## Authority model (non-negotiable semantics)

1. The adapter **supplies declarations and observations; it never
   actuates**. It exposes no verb that writes to plant hardware.
2. `SCPN-CONTROL` alone admits observations and forms `ControlAction`
   values. The adapter cannot construct, forward, or replay a
   `ControlAction`.
3. SPO semantic output consumed alongside adapter data is `review_only`
   (`actionable = false`); the adapter must not re-label it.
4. Independent machine protection retains the final veto on every plant
   path. The adapter declares the safety envelope; it does not implement
   protection and must not be treated as a protection layer.
5. Every adapter payload carries provenance (source, clock identity,
   contract version); CONTROL rejects payloads without it.

## Contract surfaces

### 1. Observation schema (device → CONTROL)

Declared per diagnostic channel:

- channel identifier and physical quantity with SI unit;
- coordinate convention declared per channel — laboratory frame, 3-D
  flux-surface label from the declared equilibrium, or Boozer-type
  straight-field-line coordinates — and spatial layout (scalar, profile
  over normalised toroidal flux, or 3-D map);
- sampling clock identity and timestamp semantics (long-pulse and
  steady-state time bases, including slow drift channels);
- uncertainty representation (declared per channel; absent uncertainty is an
  explicit `unquantified` marker, never an implied zero);
- validity and quality flags with fail-closed semantics: a payload failing
  validation is rejected in admission, never repaired downstream.

### 2. State schema (device → CONTROL)

- discharge lifecycle phase (`field_ramp`, `initiation`, `heating`,
  `sustainment`, `termination`, `terminated`, `collapsed`) with monotonic
  transition semantics; `collapsed` records a radiative or density-limit
  collapse as device truth;
- configuration identity: which registry configuration (`stellarator`,
  `heliotron`, or `torsatron`), which coil-set realisation, and which
  configuration policy revision produced the discharge;
- device availability state for control research (simulation, replay, HIL;
  live plant states are out of scope for this contract version).

### 3. Actuator-capability declaration (device → CONTROL)

For each actuator class (main field coil set, helical/modular coil
currents, trim and island-control coils, electron-cyclotron and
neutral-beam heating and localised current-drive systems, gas and pellet
fuelling, divertor controls):

- declared capability envelope (bounds, slew limits, latency class) as
  device truth for CONTROL's admission checks;
- explicit marker `direct_actuation: false` — the declaration describes what
  the plant could accept from a certified path; it is not a command surface
  and the adapter provides no command transport.

### 4. Safety-envelope declaration (device → CONTROL and protection review)

- machine-readable operational envelope (density, heating power, coil
  current and force bounds, divertor load bounds, and their applicability
  domains);
- declared radiative/density-limit collapse hazard semantics at device
  level;
- statement of the independent machine-protection boundary this envelope is
  subordinate to.

### 5. Replay fixtures contract (evidence)

An implementation must ship replay fixtures that exercise every schema above
through CONTROL's real admission path: nominal long-pulse discharges,
boundary-of-envelope cases, invalid-payload rejections, and clock-mismatch
rejections. Fixtures are versioned with the adapter and their digests
recorded; HIL evidence is additionally required before
`control_research_ready` may be declared.

## Versioning rules

- `0.x` specification versions may change with a recorded revision note in
  this file and a manifest update in the same commit.
- From the first implemented `1.0.0`, changes follow semantic
  compatibility: breaking schema changes require a major version, a
  translation path or governed deprecation, and re-run producer/consumer
  evidence on both sides.
- The manifest (`reactor-domain.json` → `control_adapter`) always records
  the exact contract version; validator and drift checks keep the two files
  in agreement.
