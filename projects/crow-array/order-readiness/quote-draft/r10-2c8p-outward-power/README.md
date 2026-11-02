# Crow r10 — outward carrier power jack; quote only

This revision replaces the carrier's inward PJ-102AH pose and affected input
power copper. Use the **new carrier Gerbers AND CPL together**, never an r9
board with r10 placement. No parts, schematic connectivity, population or job
quantities change. Pod fabrication, BOM, CPL and native files are byte-identical
to r9. The previous r9 package remains intact.

## Files and quantities

| Job | Fabricate | Assemble | Matched upload files |
| --- | ---: | ---: | --- |
| Carrier | 5 | 2 | `carrier-gerbers.zip`, `carrier-bom.csv`, `carrier-cpl.csv` |
| Pod | 10 | 8 | `pod-gerbers.zip`, `pod-bom.csv`, `pod-cpl.csv` |

BOM/CPL quantities describe one board. The unchanged totals are 476 factory SMT
and 28 factory through-hole placements; home installation is 2 Picos, 2 TI
LMK6CE012288CDLFR oscillators, 8 microphones and 8 buzzers. X1 remains required,
but deliberately excluded from factory uploads; C4 remains factory fitted.

The native power-jack anchor/pin1 is (188,14.7)mm at 180 degrees. Pin2/GND is
(188,8.7); unused pin3 is (183.3,11.7). The body center/CPL XY is now
(188,-8.2)mm. The mouth faces native -Y, toward the top edge. Do not infer a
vendor's placement angle from the native number alone: pin1 and the asymmetric
pin3 pattern must register to the actual new holes and preview.

## Engineering scope and retained holds

`engineering/power-jack-r10/review.json` and its bound evidence describe the
independent **affected repair** review. `checks/` contains fresh native DRC,
schematic parity and ERC. This is not new full-board stage acceptance or a
production release. `qualification.json` remains historical r8 clock evidence;
it is NOT an r10 mechanical acceptance. Earlier outward-mouth/access claims
for the r9 jack were wrong and must not be reused.

The enlarged round jack holes still differ from maker-recommended slots.
Finished hole/terminal fit, retention, localized soldering, seating, first-article
verification and factory acceptance remain open. Diagnostic render solids are
not exact manufacturer CAD. The plug review covers the documented straight
PP3-002A envelope, not arbitrary bulky/right-angle plugs or an enclosure.

Corrected DC plug service corridor (native mm) is X182.65..193.35,
Y-36.5..3.1, Z0.95..12.15 above nominal PCB top. Under the reviewed body and
installed-pose caps, the closest jack-to-D1 separation is at least0.536912mm
and plug-to-finished-board gap at least0.90mm. Preserve the specified radial
0.10mm/total1-degree installed pose limits; these are conditional geometric
bounds, not measurements of an assembled unit. Keep supports/enclosure hardware
out of the jack's below-board terminal columns.

Retain finished jack holes1.60..1.73mm, actual annulus>=0.30mm, controlled seating,
localized soldering of ALL THREE terminals including NC, >=75% through-fill
qualification, process/lot inspection agreement and representative supported
mating/retention qualification up to the retained29.4N force bound. These
manufacturing requirements still need agreement and physical verification.

Retain all prior stack, stencil, no-unqualified-wash, LUTE reflow, TRACO seating,
Pico D1-only removal, rail/finished-edge/underside inspection and bring-up controls.
Carrier JLC04161H-7628A and pod JLC04161H-7628 must be reconciled in the jobs.
Local correct RJ mouth directions do not close JLC model/placement registration.
Old portal previews and the $391.09 combined preliminary quote are superseded
for this changed carrier and are not production approval.

Home-clock work and bring-up instructions remain in
`engineering/R9-HISTORICAL-INSTRUCTIONS.md`; only its old upload/revision and
power-jack geometry claims are superseded. No home parts may be omitted from
the finished system.

## Next browser steps (not performed by generating this package)

1. Verify locally: `python3 projects/crow-array/order-readiness/r10_quote.py verify`.
2. Preserve old drafts. For a new carrier quote upload the matched r10 set and
   set 5 fabricated/2 assembled. The pod remains 10 fabricated/8 assembled.
   Do not upload HOME placement lists as factory files.
3. Check all exact manufacturer/MPN/package matches and every reference, not
   portal row counters. Existing `r9-merged-bom-candidates/*-merged-v2.csv` are
   equivalent identity-grouped BOM alternatives only; never use old carrier CPL
   or Gerbers with them. Keep all required factory parts in scope.
4. Obtain new placement previews. Check power-jack numbered terminals against
   the new holes and outward mouth; check every RJ pin1/locator peg and outward
   mouth. Keep **Do not confirm automatically**. A visually rotated model alone
   is not proof its physical pin mapping matches the CPL.
5. Reconcile the remaining manufacturing controls and itemized PCB, SMT/THT,
   component/setup, sourcing, shipping and tax costs. Confirm exact stock and
   gross attrition quantities before any later purchase decision.
6. Stop before purchase, payment, reservation, noncancelable sourcing or a
   manufacturing commitment. No vendor message or browser changes are made
   by this local engineering/package task.
