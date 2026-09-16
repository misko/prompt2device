# Changelog

## v0.1.2 — transport-safe publication successor — 2026-09-16

- Rebound the byte-identical carrier fabrication, source, STEP, schematic,
  render, and review payload to clean source commit `2f162256` after GitHub
  rejected the aggregate development-history pack.
- Fresh independent docs-only review: SOUND / DO-NOT-ORDER. Exact rehearsal
  3/3 PASS; all sourcing and physical-validation holds remain.

Released: v0.1.2-2026-09-16

## v0.1.1 — manifest packaging correction — 2026-09-16

- Removed the phantom manifest entry for an ignored KiCad session file absent from the published archive. All actual fabrication, source, STEP, schematic and connector render bytes are unchanged.
- Fresh independent docs-only review: SOUND / DO-NOT-ORDER. Exact docs-only rehearsal: 3/3 required checks PASS; sourcing remains declared blocked.
- Retains FIRST-ARTICLE-ONLY, both sourcing shortages and all physical/order holds. Supersedes v0.1.0-2026-09-16 without editing its existing payloads.

Released: v0.1.1-2026-09-16

## v0.1.0 — initial routed engineering release — 2026-09-16

- Completed the authenticated 19-wave route and final stitch on the four-layer
  carrier. Native DRC is 0 violations / 0 unconnected / 0 parity findings;
  analog copper is 155/155 and all required route-acceptance checks pass.
- Preserved the two single-layer digital contracts with zero vias. Qualified
  601/601 realized vias, including 12 explicitly filled and copper-capped
  via-in-pad sites and 54/54 declared current-transfer banks.
- Exported the exact Gerber, drill, BOM, CPL, drawings, STEP model and final
  RJ45 oblique views. All 300 assembled SMD placements are top-side.
- Sealed as FIRST-ARTICLE-ONLY / DO-NOT-ORDER. Current catalog evidence blocks
  C7452883 (LT3041ADE#TRPBF, stock 0) and C53283916 (TMUX2821DSGR, stock 16
  versus 40 required for five boards); physical and order-time checks remain
  in `DEFICIENCIES.md` and the first-article plan.

Released: v0.1.0-2026-09-16

## Unreleased current-topology source checkpoint — 2026-09-09

- Full carrier source suite passes 309/309, zero failures/errors. Current
  analog paths include every independent filter shunt; power validation uses
  ADR0025, and superseded ADR0023/0024 no longer claim live topology ownership.
- Replaced whole-tree historical inversions with scoped ADC, clock, package,
  power and thermal preservation checks, retaining actual geometry and hostile
  controls. Removed the unused startup_delta helper; Git preserves its history.
  Silkscreen checks now use all333 current native-library footprints.
- Connected the existing power/protection checker to both rebuild drivers.
  A RED/GREEN shell regression proves all three command guards stop downstream
  execution on failure. The actual old TPS native netlist is rejected.
- Source-layout policy, early electrical, module-first, schema-reader and
  bound-provenance preflights pass. Separate checkpoint portability tests are
  24/26: two still reference the obsolete OPA1656 generated cohort. Fresh
  conductor regeneration, not restoration of retired parts, is the next action.
- This is a source checkpoint, not a release. Native board/pod unchanged;
  routing, exact native reviews and release acceptance remain owed.

## Unreleased shared-rail physical-source integration — 2026-09-09

- ADR0025 implements333 components/937 pins with shared ADC/amplifier3V3,
  LT3041, passive reference dividers and32 independent filter shunts.
- Corrected colliding shunt placements, regulator input-capacitor placement,
  dual output-capacitor arrangement and16 input-resistor orientations.
  Six other support placements accommodate the enlarged repeated cells.
- Rebound exact OPA/TMUX/LT/reference layout rules. TPS7A9201DSKR and
  WSLP1206R0500FEA dossiers remain resolvable but are superseded; only their
  obsolete board-specific constraints were retired. Primary PDFs, extracted
  manufacturer facts, pin identities and supplier codes were preserved.
- Added two filled/capped LT EP15 vias, short GND7/10/11 bonds, exact IN/OUT,
  OUTS/SET paths and isolated capacitor-terminal quiet returns; four separate
  ordinary capacitor-ground drops. Assembly process names both thermal hosts.
- Revalidated and readmitted eight unchanged ADC/clock/reset supply branches;
  added eight amplifier-to-own-bypass branches on shared3V3. Every one of79
  power-entry groups has a local full-width witness, covering116 actual pads.
- Current95 focused tests pass, including353 adjacencies and60 affected
  footprints against333 fitted instances. Final305-test suite remains red
  with42 failures/14 errors. Reconciled local regulator/thermal/ground/power
  tests retain hostile geometry controls; cross-leg capacitors are now rejected
  even under a renamed reference. No physical qualification is claimed.
- Remaining analog-path checker, legacy power-validator and ADR ownership
  integration plus obsolete historical fixtures precede source admission.
  Native regeneration, filled returns, routed current/thermal/stability review
  and release remain owed. No commit, release, publication or order in this step.

## Unreleased precision-reference correction — 2026-09-09

- ADR0024 reuses four exact 0.1 percent RT0603BRD0710KL/C95204 dividers,
  preserving nominal 10k values and all connections. Existing anchors pass
  the larger-footprint geometry checks without relaxed limits.
- Full source suite passes 267/267; actual old-source RED catches the
  conditional initial DC margin defect. Installed leakage, temperature,
  lifetime and transient behavior are not qualified by this screen.
- Fresh read-only power review retains OPA2320 and narrows the next decision
  to partial-supply isolation and reference backdrive. No isolation replacement
  or all-state source acceptance is claimed. CAR-F12 stays REASSESS, 4/6.
- Native and pod unchanged; no routed carrier, release, publication or order.

## Unreleased amplifier/reference source correction — 2026-09-09

- ADR0023 adopts nine OPA2320AIDR packages on existing5V_OPA, adds two10k
  retained-reference input limiters and changes both output isolators to1k.
  Exact primary dossiers and targeted public two-distributor selection
  evidence are retained. The retired carrier OPA1656 dossier has no sealed
  carrier dependency; other boards and the pod are unchanged.
- Final source regressions pass264/264, including14 new adoption/protection
  tests and native-library geometry for the corrected reference section.
  Source has325 components,923 physical pins and228 nets including NCs.
- Fresh candidate review recommended implementation with obligations, not
  source/native acceptance. Startup/restart, retained charge/reference
  loading, actual filter behavior and feed-current duration remain open.
  The Cirrus performance deviation and unchanged signal/spoke requirements
  are explicit. Native remains stale/unrouted; no release/tag/push/order.

Released: no

## Unreleased schematic review acceptance — 2026-09-08

- Adopted both exact1353d047 independent witnesses verbatim; schematic
  PR-REVIEW passes2/2. The PDF lens inspected19/19 ordinary and19/19 detailed
  pages,299 references and40 NCs; no P0/P1 findings, one P2 print-size note.
- Independent whole-design equivalence covers299 components,205 nets,
  868 native node owners and871 physical-pin occurrences. Only U_ADC/U_RST2
  unit-pin serialization ordering differs from77d25f0d. Full ratings judgment
  remains inherited; no physical qualification was closed.
- Root verified368/368 frozen inputs and all subject hashes; closed the five
  prior presentation findings. Mandatory fresh handoff precedes generation of
  a current PCB. No carrier release, routing, main push or order is claimed.

Released: no

## Unreleased schematic ink-clearance correction — 2026-09-08

- Separated source-owned reset straps, supply plates, NC endpoints and hidden
  supervisor ties; reserved a lower reset-pulse corridor. All 19 final PDF
  pages and cited details were author-viewed; independent acceptance is owed.
- Added 9 project tests covering full label envelopes, NC/body contacts,
  near-coincident strokes and valid crossings. The old candidate produces 17
  findings; the delivered candidate produces zero. The screen explicitly does
  not model every reference/value glyph or replace PDF review.
- All 77 project, 13 renderer and 45 converter tests pass. Native ERC reports
  0 errors and 2076 retained warnings. Public-only prelayout resume reverified
  the exact 51-code request and 368-file census; no allocation is claimed.
- Author full-tree comparison preserves 299 components, 205 nets and 868 pins;
  only export date/UUIDs and U_RST2 pin-list ordering differ. Fresh exact-PDF
  and electrical-equivalence reviews are required. Parts, rules, stale PCB and
  pinned old bridge remain unchanged; no layout or release is claimed.

Released: no

## Unreleased schematic ground-clearance correction — 2026-09-08

- Current TPS7A92/held-supply and external-VMID prototype source contains 299
  components; the independent 77d25f0d electrical review accepted its conditional
  laboratory scope. Its power, analog and physical qualifications remain owed.
- Corrected source-owned ground, wire, reference and ADC configuration-label
  clearance on the 19-page schematic. Added 6 project regressions; all 68 project,
  13 renderer and 45 converter tests pass. Final native ERC: 0 errors/2054 warnings.
- Preserved all 299 components/205 nets/868 pin entries and parts/rules identity.
  ADC unit-pin serialization order changes the owning netlist fingerprint;
  fresh exact-PDF review and an independent electrical-equivalence rebind are
  required before schematic acceptance. No prior witness hash was rewritten.
- Preserved the stale 213-footprint PCB and old pinned schematic bridge.
  No new placement, route, physical qualification or order is claimed.

Released: no

## Prototype lifecycle and route-contract corrections — 2026-09-07

- Adopted user-accepted ADR-0007: public-data design can proceed before physical
  first-article measurements; connector coupon is optional. Both drivers retain
  truthful FULL/INCOMPLETE receipts and still reject unknown identities or stale
  evidence. Ordering, testing and outdoor production remain separate boundaries.
- Corrected layer-role declarations, added exact-net analog ESD topology checks
  for all eight channels, and declared main-trunk routing ownership.
- Raised route widths to the existing power/reference floors; constrained
  clocks to the top layer above the continuous ground plane; corrected route
  and rescue clearance settings and removed unsafe via-size normalization.
- Placement/routability now passes five predicates with two explicit N-A;
  placement policy passes four with one N-A; pad separation passes. Native
  placement DRC and model coverage still require source corrections; no route
  or carrier release is claimed.
- Fresh independent reviews found ADC-page rendering overlaps and insufficient
  MCH clock pull-down strength at specified input leakage. These are retained
  as design blockers for the next source correction, not physical-test deferrals.

## Unreleased first-article candidate — 2026-09-01

- Commissioned the carrier as a separate single-board project.
- Selected one CS5308P-DN, hardware TDM8, hardware reset pulse, AN0556 Figure 2 input cells, and buffered VMID.
- Kept Pi 5, PoE/Ethernet, USB data, and MCHStreamer off board.
- Froze the parent spoke identity pending the parent’s final extended contract hash.
- Declared DO-NOT-ORDER holds; no release has been sealed or fabricated.
- Corrected the south J5-J8 pad-1 anchors by the exact 9.0 mm rotated-body offset, aligning them with J1-J4 and clearing H3/FID3.
- Expanded the shared placement collision gate to cover fixed board-only mounting-hole and fiducial courtyards, with regression fixtures for both classes.
- Refreshed the public JLC/LCSC catalog screen: 39/39 exact codes meet build quantity 5; authenticated assembly allocation remains outstanding.
- Added a source-bound connector coupon producer/verifier and generated the exact full-outline, connector-only fabrication/evidence handoff. Coupon geometry and DRC pass; the blank physical receipt remains deliberately INCOMPLETE at 0/20 observations.
- Confirmed from current public JLCPCB manufacturer documentation that the coupon's exact 4-layer FR-4, 150 x 100 mm, 1.6 mm, green/white, lead-free-HASL selections are offered; no upload, quote, CAM acceptance, allocation, or order is implied.
