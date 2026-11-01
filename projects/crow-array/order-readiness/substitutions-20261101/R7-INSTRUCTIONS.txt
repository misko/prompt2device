# Crow r7 — stocked fuse/regulator, quote only

Not production approval. No purchases, reservations, supplier contacts or
manufacturing commitments. Engineering desk qualification passed for this
controlled prototype quote; factory process acceptance and physical tests have
not been performed. See qualification.json for decisions, sources and limits.

Fabricate 5 carriers / assemble 2. Fabricate 10 pods / assemble 8.
Upload BOM/CPL files for ONE board each; set quantities in JLC separately.
478 SMT + 28 factory THT + 18 home placements, unchanged.
Home: 2 original SC0915 Picos (controlled D1-only removal), 8 microphones,
8 buzzers. JLC: 24 RJ jacks, 2 power jacks and 2 regulators plus all SMT.

## Changes from r6

| Original | Reviewed replacement | Installed need |
|---|---|---:|
| Littelfuse 1206L010/30WR | LUTE 1206L010/30NR / C7542926 | 24: carrier F101..F108 x2, pod F1 x8 |
| RECOM R-78E5.0-0.5 | TRACO POWER TSR 1-2450 / C6886877 | 2: carrier U10 |

CTS CB3LV-3I-12M288000 is UNCHANGED. Its exact Global Sourcing/consignment
route remains open. All four accepted r6 identity changes are retained.
Reported Nov 1 regular-catalog orderable stock: LUTE 33,897 and TRACO 167;
not a reservation, warehouse date, live job match or promised lead time.
Do not transfer old Littelfuse attrition/MOQ to LUTE. Need is 24 + actual
replacement-specific allowances, not automatically 28 or 30.

U10 copper/drills/pins/anchor/rotation are unchanged. Its nominal BODY center
changes: native (184.530,36.250) mm; CPL (184.530,-36.250), rotation 0,
Top. Pins 1 VIN, 2 GND, 3 VOUT left-to-right; body extends mainly native -Y.
Both the carrier CPL and THT verification table use this center. Do not mix r6
carrier CPL with r7 BOM. Only this CPL row changes. Pod CPL is unchanged.
Both Gerber ZIPs are byte-identical to r6: no copper, mask, paste, silkscreen,
outline or drill change. U10 native fabrication/courtyard graphics and footprint
identifier are corrected; the incorrect RECOM 3D model is removed. No qualified
replacement 3D render/full-assembly release is claimed by this quote package.

## Required process and acceptance controls

- LUTE: qualified reflow within its maker curve; preserve reviewed lands/paste.
  No whole-board wave, routine hot-air/hand PTC rework, or unqualified solvent
  wash/coating. Confirm factory compatibility; quarantine process deviations.
- TRACO: manufacturer's specified wave limit is 265 C / 10 s. Request a localized
  compatible THT process. JLC's Wave label is NOT proof that its hand-solder
  process is equivalent. Obtain that compatibility before production. Do not
  expose the rest of the populated board or home-installed acoustic parts to
  whole-board wave/wash to satisfy this row.
- U10: finished holes .92..1.13 mm; prepared lead/hole combined center error
  <=.10 mm; actual external annulus >=.13 mm. Support only free lead length;
  no load into case, damaged plating, forced insertion or unvalidated forming.
  Maximum body 12.2 x 8.0 x 10.6 mm; measured body-center displacement <=.10 mm,
  total rotation/tilt <=1 degree. Preserve seated/underside/solder inspection.
- These controls supplement, not replace, full retained first-run stackup,
  precision-outline, stencil/mask, hole/seat, Pico and connector requirements.
  Existing assembly-property labels describe the requested work split, not a
  manufacturer approval of generic hand soldering.
- Keep first-article hot-load, startup/fault recovery, input-fuse inrush, USB
  backfeed, ripple/audio and thermal tests. No new OVP or higher input fuse is
  authorized. These tests are not claimed complete by desk qualification.

## MacBook steps

1. Verify locally with `python3 projects/crow-array/order-readiness/r7_quote.py verify`.
2. Use carrier-bom.csv + carrier-cpl.csv together; likewise the two pod files.
   Saved drafts are still r6 until deliberately updated. Record revision and
   preserve quantities 5/2 and 10/8. Recheck ALL matches after uploading: JLC
   has previously reset unrelated rows or chosen the wrong manufacturer.
3. Match LUTE C7542926 and TRACO C6886877 exactly. Retain CTS, ADC and capacitors
   at their specified identities. No YLPTEC match, omitted part or Do not place.
4. Record replacement-specific gross quantities, stock pool, fees and usable
   dates. Keep CTS sourcing separate. Do not Add/pay/reserve or enter a
   noncancelable pre-order route just to obtain information.
5. Obtain complete previews and check U10 physical center, pin order and pose;
   retain no-auto-confirm production-file/placement preferences. Do not approve
   production or previews under quote-only authority.
6. Resolve exact process compatibility above and existing stackup/rails holds.
   Carrier JLC04161H-7628A acknowledgement (1.5542 mm +/-10%) stays unresolved;
   pod JLC04161H-7628, added rails/no-depanel and finished edges need review.
7. Capture itemized fabrication, SMT/THT, component, setup, sourcing, delivery
   and taxes. Stop if a complete quote requires a purchase/reservation or vendor
   contact; report the missing fields. No vendor message is authorized here.

This r7 payload does not inherit production acceptance from the original release.
The previous release, r5 and r6 remain untouched. The qualification is a primary
agent review; no independent adversarial review is asserted.
