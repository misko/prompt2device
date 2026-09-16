---
id: 0002
date: 2026-09-01
status: superseded-by-0006
---
# 0002 — Channel-count study without foreclosing a multiscale array

> **P2 scope note:** This proposal remains unaccepted. The later requirement
> for 3D evidence reopens the channel allocation. Eight, twelve and sixteen are
> now neutral candidates until the roof envelope and identity/overlap use case
> close Q1/Q5. See the
> [dimensionality/identity/PoE addendum](../reports/2026-09-01-dimensionality-identity-and-poe-addendum.md).

> **P5/P6 disposition:** The user subsequently permitted a planar branch,
> removed simultaneous-source separation from acceptance and corrected the
> study aperture to 8 m diameter. ADR 0006 supersedes this neutral noncoplanar
> count study with a planar eight-channel study while preserving the requirement
> to survey and simulate before accepting coordinates.

## Context
More microphones improve redundancy, support multiple spatial scales and can
add elevation information, but every channel adds an outdoor pod, cable,
protection cell, ADC input, calibration burden and enclosure. The roof geometry
and required localization result are not yet known.

## Options
- **Eight channels: five outer plus three raised** — lowest-cost noncoplanar
  experiment, but weakest pair/channel redundancy.
- **Twelve channels: eight outer plus four raised/inner** — preserves the
  perimeter while adding a second plane; requires proving a partially populated
  second TDM lane.
- **Sixteen-channel multiscale array** — combines an inner compact cluster with
  eight roof-scale positions; highest research leverage and complexity.
- **Six-channel legacy hexagon** — cheapest reference topology, but leaves two
  available channels unused, is planar and provides less redundancy.

## Decision
Keep eight, twelve and sixteen channels as neutral candidates. Do not select a
first-article count or coordinates until Q1/Q5 define the roof envelope,
identity signature and simultaneous-source requirement. In every candidate,
use surveyed noncoplanar positions and evaluate mild nonperiodicity rather than
locking a visually perfect ring.

## Consequences
The central carrier must capture every selected channel simultaneously. No
8/12/16-channel compatibility claim exists until a candidate interface control
document locks clock authority, frame/slot/word format, module image identity,
unused-slot behavior, power and connector budgets and passes exact-mode bench
capture. A planar build cannot claim robust three-dimensional localization.
Wide spacing will spatially alias at upper crow-call frequencies, so
localization must be broadband, near-field and evidence-driven rather than
based on a single unambiguous tone.
