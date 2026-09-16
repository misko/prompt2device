---
id: "0020"
date: 2026-09-08
status: accepted
---
# 0020 — Pad-only clearance scopes for retained package lands

## Context

After the eight solid-GND source corrections, native filled DRC on the
disposable placement subject reports 15 clearance findings: eight U_ESD1–8
NC2/IO1 pairs, six adjacent U_CLK pairs, and Q_IN source3/gate4. These are
same-footprint, different-net fixed lands, not inter-component collisions.
The physical floor remains 0.127mm and ordinary route/stitch isolation 0.25mm.

Primary documents were reopened on 2026-09-08 and their land drawings viewed:

- [TI TPD2E2U06 SLLSEG9C](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf),
  DRL pin table p.3 and DRL0005A land example PDF p.18: 0.50mm pitch,
  0.67×0.30mm example lands and 1.48mm row centers. The retained KiCad
  SOT-553 lands are **not identical to that example**: 0.675×0.350mm at
  1.425mm row centers. Their measured adjacent gap is 0.150mm. NC pads
  remain real floating pads; none is deleted, grounded or renamed.
- [TI SN74LVC3G34 SCES366L](https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf),
  DCU pin table p.3 and DCU0008A land example PDF p.20: 0.50mm pitch,
  0.85×0.30mm lands and 3.10mm row centers. The retained KiCad VSSOP-8
  lands are **not identical to that example**: 1.25×0.35mm at 2.80mm row
  centers, giving 0.150mm adjacent gaps. Both TI example drawings explicitly
  permit alternate IPC-7351 designs; this is not a claim that TI specified
  the retained KiCad dimensions or qualified their assembly yield.
- [Diodes DMP6023LFG DS37204 Rev.2-2](https://www.diodes.com/datasheet/download/DMP6023LFG.pdf),
  p.5 suggested land drawing: C=0.650mm, X2=0.420mm and G=0.230mm.
  The native PowerDI3333 source/gate lands retain those local dimensions;
  the measured source3/gate4 gap is 0.230mm. The fused drain land is unchanged.

The committed PDFs remain the exact identities declared by their part
dossiers. Native geometry, not the vendor drawing, owns the measured CAD
gap; vendor facts establish package identity and distinguish recommendations
from the retained alternative. No manufacturability or voltage qualification
is inferred merely from a clean rule report.

## Options

- Lower entire netclass clearances: rejected; unrelated routing would lose
  isolation margin without an electrical or geometric reason.
- Remove NC lands or arbitrarily trim pads: rejected; that changes assembly
  geometry or physical pin identity to suppress a report.
- Replace both TI footprints with their exact example lands: feasible as a
  separate footprint/assembly revision, but unnecessary for these above-floor
  gaps. It changes row positions, toe/heel geometry, source launches and the
  reviewed package/model boundary. This decision retains the existing lands
  rather than claiming an unmeasured solderability improvement.
- Area-plus-net rules covering all copper items: rejected for package-only
  intent. KiCad's item-overlap semantics could also match long tracks or vias.
- Exact net-pair, pad-only rules in tight areas: selected; expresses the
  intrinsic land gaps without changing copper, route floors or topology.

## Decision

Add 15 `PKG_PAD_*` permissive F.Cu areas in `floorplan.yaml`, each touching
exactly its two named pads, and 15 matching `scoped_clearances` in `nets.yaml`.
Use symmetric singleton `nets_a`/`nets_b`, `pads_only: true`, and the measured
nominal gap (0.15mm for the TI packages; 0.23mm for Q_IN).

The generic emitter adds `A.Type == 'Pad' && B.Type == 'Pad'` to the existing
two-sided area and net-pair predicates. Non-boolean values are refused;
absent/false retains legacy behavior. `tier_preflight` cannot use pad-only or
malformed entries to justify reduced router clearance. No `.kicad_dru` is
hand-authored, and no DRC severity is suppressed.

## Consequences

Source tests independently load native lands and require all 15 exact areas,
net pairs, gap values, pad-only guards and evidence. Widened regions, foreign
pad membership, wrong nets and missing guards fail. Every other floorplan,
route and net-rule datum is compared with the prior source. Historical source
comparisons exclude only this later delta; the new tests own its full scope.

The native control test `tests/t2_scoped_pad_clearance.py` builds independent
fixtures and invokes real KiCad DRC. Correct and reversed pad pairs pass;
wrong-net, outside-area, one-sided-area and below-local-floor pairs fail.
Tight track/pad and via/pad pairs fail with the guard and disappear with the
exact pre-fix emitter. Filled-zone clearance stays unchanged in both arms;
that arm does not discriminate the old emitter.

The saved carrier experiment now reports 0 violations / 498 opens / 0 parity.
Independent comparison reopens both filled subjects: all 309 footprint poses,
936 raw pad geometries/modes, 877 netted-pad connected-component memberships,
9 vias and 55 existing rule areas are unchanged. All four filled copper layers
have zero added/removed Boolean area. Exactly the previous 15 failing pad
pairs populate the new areas, with no foreign pad admitted.

Re-run source properties with `/usr/bin/python3 -B -m unittest discover -s
projects/crow-audio-carrier-v1/03_src/tests -p test_package_clearances.py` and
native controls with `/usr/bin/python3 -B tests/t2_scoped_pad_clearance.py`.
The associated research report binds exact candidate and comparison hashes.
These nominal CAD gaps are not etch/soldermask tolerance qualification or a
system surge, insulation, assembly-yield or first-article claim.

The canonical PCB remains the previous unrouted subject until the full
conductor regenerates it and fresh exact-subject reviews accept it. Silk
ownership/readability, routing all 498 connections, final 0/0/0, fabrication,
release reviews and seal remain owed. TOP77/0.20A, sourcing and all physical
holds remain unchanged; DO NOT ORDER.
