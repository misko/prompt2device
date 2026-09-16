# Changelog

## v0.2.4 — rule-rationale correction — 2026-09-16

Released: `07_releases/v0.2.4-2026-09-16/`.

- Correct the D1 invariant rationale to name the realized S1M part while
  proving every executable invariant field is unchanged.
- Preserve the v0.2.3 board, fabrication payload, STEP, schematic, connector
  views and routing evidence byte-for-byte.
- Exact rule-prose rehearsal passes 3/3. Authenticated JLC allocation and
  physical first-article work remain BLOCKED-SOURCING / DO-NOT-ORDER.

## v0.2.3 — manifest packaging correction — 2026-09-16

Released: `07_releases/v0.2.3-2026-09-16/`.

- Removed a phantom manifest entry for an ignored KiCad session file that was
  never present in the Git release tree.
- Preserved every engineering, fabrication, source, STEP, schematic, render,
  review and stock-evidence payload from v0.2.2 byte-for-byte.
- Exact docs-only rehearsal: 3/3 seal-required checks PASS. All allocation,
  physical first-article and DO-NOT-ORDER holds remain.

## v0.2.2 — configured stock-surplus successor — 2026-09-16

Released: `07_releases/v0.2.2-2026-09-16/`.

- Set the source-owned public catalog stock surplus to 150 units. Fresh
  evidence clears all 22 coded machine-BOM rows for ten boards plus surplus.
- Preserve the exact v0.2.1 board, fabrication payload, STEP, schematic,
  connector views and routing evidence byte-for-byte; bind refreshed release
  reviews and deficiency records to the successor archive.
- Exact assembly-policy rehearsal: 3/3 seal-required checks PASS. Authenticated
  JLCPCB allocation and physical first-article work remain DO-NOT-ORDER holds.

## v0.2.1 — transport-safe publication successor — 2026-09-16

Released: `07_releases/v0.2.1-2026-09-16/`.

- Rebound the byte-identical pod fabrication, source, STEP, schematic, and
  connector-view payload to clean source commit `2f162256` after GitHub
  rejected the aggregate development-history pack.
- Fresh independent fix-pass reports rebind all four release lenses to the
  same board hash. Exact rehearsal 3/3 PASS; all sourcing and first-article
  holds remain.

## v0.2.0 — 2026-09-16

Released: `07_releases/v0.2.0-2026-09-15/` (candidate directory retained from initial staging).

- Replace the former Micro-Fit interface with the exact manually fitted Würth 615008160221 RJ45 and straight-through Cat6 Crow power/audio pin assignment; NOT ETHERNET /NOT POE.
- Keep every fitted SMD on top:31 automated placements on a60×40mm board.
- Complete protected power/audio routing,22/22 critical paths and native/standalone DRC0/0/0.
- Ship32/32 modeled bodies, reviewed source/fab/PDFs and four independent final SOUND reviews.
- Required release rehearsal3/3 PASS; exact JLC allocation and all physical first-article tests remain unverified. FIRST-ARTICLE-ONLY /DO-NOT-ORDER.

## v0.1.0 — 2026-09-03

- Commissioned a fresh crow microphone pod v3 design.
- Froze the parent-identical four-wire spoke interface and exact Molex/Belden
  identities.
- Selected protected 12 V input, TPS7A4901 quiet 5 V rail, PUI electret front
  end and OPA1679 active-balanced line driver.
- Match the capsule's characterized 3 V / 2.2 kΩ condition with a 3.9 kΩ /
  100 µF supply filter and reduce differential gain to 18/11 V/V after the
  carrier OPA1656 common-mode audit. This targets 0.653 Vrms nominal and
  0.923 Vrms at the capsule's +3 dB sensitivity corner
  at 110 dB SPL, rather than depending on a barely compliant load/gain model.
- Set the first pod PCBA request to ten boards: eight installed plus two
  matched spares.
- Reached the governed `J-PCBA-PRELAYOUT` checkpoint with 40/40 source,
  schematic, netlist and board references; the 22 exact-code request rows scale
  correctly to ten boards. Placement remains blocked on a live JLC response.
- Closed the first-power population card over 33 explicit installed references
  and the TPS7A4901 exposed pad; literal ranges, net names and pin names are no
  longer accepted as component evidence. Protection/topology ADR coverage is
  now non-vacuous.
- Separated the F1 cold-resistance and D1 diode-mode checks, and corrected the
  worst-leg headroom calculation without changing its safety conclusion.
- Replaced the high-leakage SS14 reverse block with a public-data-bound
  1N4007(M7)SMA plus 4.7 kΩ/1206 pull-down, upgraded both 100 Ω output
  resistors to 125 mW 0805 parts, and included TPS7A49 feedback-current corners.
- Recorded first-article, sourcing, connector, enclosure and cable qualification
  holds; release remains DO NOT ORDER.
- Routed and layout-sealed the exact 60 x 40 mm pod board. Native DRC is
  0/0/0, the realized-route checker passes 22/22, the public twin resolves
  31/31 fitted bodies, and four independent final review lenses report SOUND
  with P0/P1/P2 = 0/0/0.
- Sealed `v0.1.0-2026-09-03` as a design release with a complete fabrication
  archive and `BLOCKED-SOURCING` order verdict. Public catalog evidence is
  retained as a negative filter; authenticated JLCPCB allocation and placement
  preview remain mandatory before payment.

Released: `v0.1.0-2026-09-03` — DESIGN PASS / SOURCING BLOCKED
