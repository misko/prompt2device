# TMUX4827 perimeter pad clearance scope — engineering assessment

**Scope:** read-only assessment only.  No source, PCB, authority, or remote
state was changed.

## Decision

An exact, native-DRC-only **0.15 mm pad-pair clearance** for `7↔8` and `8↔9`
on exactly `U_ISO1..U_ISO8` is technically defensible.  It must be treated as
an intrinsic YBH0009 package-land exception, separate from the B2 POFV
profile.  It must not be expressed as a `QUIET_POWER` netclass change, a
GND/power waiver, an area-wide rule, or an all-item scoped clearance.

The rule value is exactly the generic different-net SMD-pad floor recorded in
the 2026-09-23 package/process reassessment.  It is also above the selected
`jlc_4layer_advanced` minimum space (0.09 mm).  It is at the generic 0.15-mm
floor with no margin, so this is a bounded source-rule decision, not a claim
of supplier assembly approval or fabrication yield margin.

## Evidence

* The authoritative native footprint is a 3x3, 0.40-mm-pitch grid.  Its
  perimeter pads 7, 8, and 9 are all circular Ø0.25 mm lands at
  `(-0.4,+0.4)`, `(0,+0.4)`, and `(+0.4,+0.4)` mm.  Each pair has nominal
  copper gap `0.40 - 0.125 - 0.125 = 0.150 mm`.
* `part.yaml` binds `7=S1B`, `8=VDD`, and `9=S2B`; the retained diagnostic
  coupon maps these to `FILTER_P`, `5V_LDO_HOLD`, and `FILTER_N`, respectively.
  Thus the two requested pairs are distinct-net low-voltage package lands,
  not GND and not a power-to-power/general power clearance class.
* The package record states TI's YBH0009-C02 0.40-mm grid and retained
  Ø0.25 perimeter lands.  The coupon documents the same geometry and reports
  native DRC clean; it is diagnostic geometry, not a Crow-board acceptance.
* The reassessment records public JLC generic 0.15-mm different-net SMD-pad
  spacing.  The public BGA material specifically supports the separate
  B2-via-to-neighbor-pad 0.10-mm relationship; it should not be used to widen
  this perimeter-land scope.

## Required narrow shape if implemented

Extend the existing TMUX-specific producer/checker, not generic
`scoped_clearances`.  For each of the eight exact references, emit only these
two rules (with both A/B orders):

* `A.Type == 'Pad' && B.Type == 'Pad'`
* same exact `Reference == U_ISOn`
* pad-number pair `{7,8}` or `{8,9}`
* `A.NetName != B.NetName`
* `clearance (min 0.15mm)`.

The independent checker should bind the exact 7/8/9 functions, Ø0.25 sizes,
0.40-mm centers, 0.15-mm edge gaps, and the exact U_ISO reference set.  Native
fixtures should prove the pair passes at 0.15, fails when its local rule is
removed under the `QUIET_POWER` 0.20-mm class, and that a nearby trace, via,
zone, different footprint, diagonal pair, or other pad pair remains subject
to ordinary rules.

This changes only copper spacing between the named stationary pads.  It does
not lower the 0.20-mm `QUIET_POWER` routing/isolation margin, track widths,
current capacity, voltage-domain/fault isolation, B2 POFV scope, or clearance
to any routed conductor.

## Limits

The current evidence supports exactly the two adjacent perimeter pairs.  It
does not support a generic all-TMUX, all-BGA, all-VDD, all-`FILTER_*`, or
netclass exemption.  Any claim of production/CAM/PCBA acceptance remains
outside this source assessment and under the existing order-time process.
