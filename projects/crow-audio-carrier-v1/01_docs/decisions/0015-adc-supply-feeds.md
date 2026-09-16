---
id: "0015"
date: 2026-09-08
status: accepted
---
# 0015 — bounded west ADC feeds with retained return topology

Accepted as authored-source progress only. NOT ROUTE-READY, layout sealed,
release ready, orderable or safe to energize. ROOT authored and screened these
changes; fresh independent schematic/placement/routed-release reviews remain.

## Context

Start from clean549a4e793ba7f42cd971e25d96cdbbdd36f708ea. Before source
edits,11:02:36Z inventory binds1,204 tracked carrier files/102,471,546 bytes.
Git preserves the recoverable baseline; ignored transients are not censused.
No BOARD constructor/load/save, generation, route prep/import, checkpoint or
review rebinding occurs in this source investigation.

Both ADC5/ADC9 bypass groups lacked a1.20mm/.25mm full-width local entry.
Add one F.Cu feed per group through the existing VMID capacitor inter-pad
corridor to an explicit1.20mm entry outside the capacitor rows. Each new
feed contains six0.18mm straight primitives/6.938221894mm, wholly contained
in its named width area. The north and south full-width entries respectively
run from[91.3,62.4] to[91.3,60.5] and[91.3,77.6] to[91.3,79.5].
These are local trunk entries, not completed connections to the LDO or all
other3V3 pads. Generic rail ownership remains unchanged.

Reopen seven existing banks only: ADC2/3/5/8/9/10/11. Move the four CFG
drops to clear the feed corridor and shorten their source leaves. Retire two
obsolete0.05mm-long0.60mm cap-side nubs; their former local-entry purpose is
superseded by the continuous feed/full-width entry, and native contact is
preserved. Move the south supply knee0.05mm left. All65 other banks remain
exact, including all15 peripheral power banks and all VMID capacitor return
branches. All part positions, electrical pin/net identity, class/current/
fabrication limits and the physical stack remain unchanged.

## Options

- Retain the549a source: preserves existing geometry but leaves two local
  supply groups without full-width entries. Not selected.
- Feed through the native capacitor gaps while preserving all GND geometry:
  H1-H4 progressively resolve pad/CFG conflicts, but the south GND bend
  still conflicts with the candidate feed. Rejected raw attempts retained.
- Adjust that GND bend: H5 resolves the copper conflicts, but expanded drill
  coverage exposes the old GND_A8 drop's physical-pad gap. Not adopted.
- Move the same GND_A8 drop onto the existing return-spine vertex: H6 clears
  the expanded checks while preserving actual capacitor-to-GND_A topology.
  Selected; the extra return length requires later realized return review.

## Decision

Adopt only H6's seven-bank source delta, two explicit cap-gap clearance
scopes and two bounded feed-width scopes. Preserve the exact current/fab/
layer contract and all other source banks; require complete local contact,
expanded physical drill clearance and all downstream review/release gates.

## Measured clearance, not an assumed land pattern

The first hypothesis assumed0.875mm-wide0603 pads. The actual native library
lands are0.900mm wide on1.550mm centres. Their0.650mm gap leaves0.235mm
clearance on each side of a centred0.180mm trace. Native shape bisection
measures all eight trace-to-pad gaps independently; no circular pad model is
used. A0.24mm proposed rule fails all eight, as the regression reconstructs.

Adopt explicit0.230mm clearance only for3V3_ADC inside the two named F.Cu
capacitor-gap areas. This is a documented local design-clearance change from
ordinary0.25mm, not an unchanged-clearance claim. The0.127mm fabrication
floor, all class floors and all sixteen previous scoped clearances remain
exact. Full1.20mm entries retain0.25mm clearance independently of rule-area
overlap. Native nominal margins do not certify fabrication yield or solder
mask registration. Four new rule areas bring totals to33 width scopes and
18 clearance scopes; width and clearance areas have distinct purposes.

## Ground return correction

The existing Cirrus CS530x layout guidance remains the source: VMID capacitor
grounds return to the nearest GND_A pin; each GND_A has its own plane drop,
not a direct connection to the exposed paddle. No vendor copper is imported.

Shift ADC8's intermediate GND bend from[91.6,70.75] to[91.6,70.68] to
clear the south feed. Expanding the native screen to this bank also exposes
its older drill-to-C_VDDA2_10N.2 gap of0.090mm, below the conservative0.255mm
physical-pad-hole screen (including same-net pads). This is a source-screen
finding, not a claimed result from native PCB DRC.

Relocate that0.50/0.20mm GND via from[90.55,71.0] to[89.8,71.5], an
existing vertex on the VMID2 ground spine. The real F.Cu contact graph still
joins ADC8, both VMID2 capacitor grounds, the10nF bypass ground and its own
via. It does not join ADC6 or EP49 through an imaginary plane edge. All
other GND banks, the GND_A6 drop, and unsplit inner-plane intent stay exact.
Actual filled return geometry, current cutsets and impedance remain owed.

## Width and conditional current accounting

Source totals:72 banks/201 straight primitives/20 vias, with five vias
relocated and none added. West pin-to-cap subtotal becomes3.698251073mm/
four items. Combined west narrow copper is17.574694861mm/sixteen items;
the unchanged non-west3V3 subtotal is20.266753550mm/eighteen items. Whole
3V3 is37.841448411mm/34 items, setting an upward-rounded power-wave
ceiling of37.841449mm/34. HOLD stays27.372221053mm/27, SW0.9mm/one,
and each FILT positive bank4.500392796mm/three. Exact per-net tests remain
necessary; the shared ceiling is not a per-net permission to grow copper.

CFG1/5 each become2.732988328mm/three items, CFG2/4 each1.999713755mm/
three. Tighten the control ceiling to2.732989mm/three; widths stay0.18mm
locally and0.20mm for ordinary control continuation.

Using nominal35um copper, rho85=2.1643958e-8 ohm-m and R=rho*L/(w*t):

| Complete local narrowed supply branch | Length mm/items | R mOhm | Loss at assumed0.15A mW | Conditional loss at full2.5A mW |
|---|---:|---:|---:|---:|
| ADC5 |8.889980657/8 |30.541963 |0.687194 |190.887270 |
| ADC9 |8.684714204/8 |29.836760 |0.671327 |186.479751 |

The0.15A values use the existing normal leaf allocation, not a measured
load or new datasheet guarantee. Full2.5A is charged to each branch
independently: no sharing credit. These estimates do not establish ampacity,
temperature rise, permissible fault duration, current limiting or safe
energization. Keep the2.5A design bound and0.20A first-power HOLD.

## Consequences

MEASURED11:23:15Z full source suite155/155 PASS. Seven new tests cover
native cap gaps, explicit scope, continuous entry/cap reach, ground return,
bounded lengths/extents and exact preservation. Hostiles reconstruct an
over-tight gap rule, disconnected feed, old via site and runaway leaf.

MEASURED11:24:06Z ADC127,156/regulator49,659/digital21,831 native
comparisons clear;19/19 other clock entries retained. Rules8/8 and netrefs
367/367 PASS. Exact-input source-shadow remains205 owners/159 generic.
MEASURED11:25:26Z all71/71 local power groups have entry witnesses over the
same96 pads; peripheral43,860 comparisons and15/15 contacts remain clear.

Six immutable geometry attempts are retained:10,4,4,2,1,0 findings.
H3's equal count changed finding families; H4 improved, so no three-attempt
plateau was hidden. H5 expanded coverage to the old GND bank/drill; H6
resolved that finding. Final screening covers90 ADC primitives/13 vias.
The five rejected candidates are not adopted or labelled geometry PASS.

Next: exposed-pad thermal/common-plane return, remaining source intent and
all analog endpoints; fresh generated-source admission and independent
reviews; bounded routing; actual filled-board/thermal/SI and release checks.
Carrier remains stale/unrouted/unreleased. Pod release and parent holds are
unchanged. TOP77, physical/sourcing limits and both-child-seals plus fresh
exact-base/head P-PUBLISH before main remain. Public information only; no
upload, account, purchase, energization or main push.

## 2026-09-08 amendment — executable electrical identity

The 14:00:52Z full producer generated a fresh schematic and native netlist,
then stopped at E-ADR because no electrical invariant cited this decision.
Append 24 pin-on-net declarations in `03_src/rules/electrical_invariants.yaml`:
both LDO output lands, both west analog supply pins, their four bypass
capacitors, both analog ground pins, and both VMID output/capacitor banks.
This preserves existing electrical intent; no TSX, placement or copper source
changes are made by this amendment.

MEASURED 14:10:14Z: E-INV passes 105/105 assertions on the newly generated
native netlist. The new `test_adc_feed_invariants.py` suite was first run
against the uncorrected declarations: all five tests failed, including active
topology coverage at 4/5. With the declarations present, all five pass and
every one of the 24 pins independently rejects both a wrong-net mutation and
a missing-pin mutation (48 deliberate defects). The tests read this board's
live native netlist intentionally, so later regeneration must preserve these
identities rather than an obsolete byte snapshot.

These assertions do not prove shortest return paths, separate physical plane
drops, local feed dimensions, current capacity or realized board connectivity.
`test_adc_feed_source.py` remains the native source-geometry complement; actual
saved/filled-board checks and independent reviews remain mandatory. In
particular, common GND net membership does not establish which copper path
current takes. No physical qualification or release/order hold is cleared.


## Proposed ADC2 pour-reservation correction — 2026-09-13

PROPOSED source-boundary correction following the independent D-BACK
SOUND / REASSESS_ARCHITECTURE verdict. The earlier claims and measurements
above remain historical. C_VDDA2_10N.2 already physically joins the protected
VMID2 return through the unchanged C_VMID2_470N.2 seed; full-connection-only
is rejected because ambient-plane participation could bypass that return.

Replace only ADC_VMID2_RETURN_POUR.points with the KiCad integer-coordinate
set union of its existing polygon and x89.99–91.05 / y70.94–72.06mm. This
rectangle is the actual F.Cu ground land bounding box x90.24–90.80 /
y71.19–71.81mm expanded by the existing 0.25mm zone clearance. The whole
old reserved area is retained at native integer precision. The named area
stays F.Cu-only, deny:pours; explicit tracks and vias remain permitted.
All separate via reservations, the U_ADC.8 designated 0.50/0.20mm drop at
(89.8,71.5), and the three U_ADC.8 / C_VMID2_470N.2 / C_VMID2_4U7.2 seed
banks remain unchanged. Two existing 0.18mm ADC2 supply segments intersect
the added area; their permissive width/clearance scopes and copper remain
unchanged. No other F.Cu pad bounding box intersects the added rectangle.

The source regression in test_adc_feed_source.py grades the native polygon
coverage, pour-only semantics, and designated seed/drop ownership, including
known-bad partial-pad and lost-return cases. All placements, pad overrides
(32 source / 33 existing native full GND pads, including all 14 prior
additions), minimum resolved spokes2, and width/current/clearance floors
remain unchanged. The 0.50mm thermal gap/spoke settings are not reduced.

This source proposal is not placement DRC, filled return-graph, thermal,
assembly, or release qualification. Independent exact-source review and
separate native-budget admission are required before any regeneration;
CAR-TOP-ONLY-SMD remains cumulative4/4closed. A later admitted proof must
grade placement DRC before prep, then prepared+filled DRC and every existing
quiet-return cut/control. No new PCB is generated or adopted here.


## Proposed exact ADC2 pad-to-zone mode — 2026-09-13

Preserve the existing dedicated ADC2 seed/via return by declaring only
`C_VDDA2_10N.2`, guarded by `on_net: GND`, as `zone_connection: none`.
The generic `BoardBuilder.place_parts` consumer maps the exact `full`,
`thermal`, and `none` strings to native local pad modes. A present unknown
or malformed mode is an error even when its ref, pad, or net selector does
not match. An absent mode preserves library/inherited or previously applied
settings, including clearance-only overrides. Existing generic glob and net
selectors remain supported; the carrier's separate census requires exact
refs/pads and independently preserves all 32 FULL targets plus this one NONE
target. NONE disables zone connection at this land; it does not prove or
prevent track/via connectivity elsewhere along the return.

The candidate-five native refusal remains blocking. The inherited thermal
mode's expanded test contour intersects the clipped pour boundary despite
no actual pad-to-pour contact. Making the intended no-zone policy explicit
addresses that source representation; no changed-mode placement outcome is
claimed. The failed placement contains zero tracks and 11 thermal vias,
with 44 via-layer nodes in the independent graph; the designated prepared
ADC2 seed via is still absent. The earlier zero-vias prose is corrected by
the independent review's retained via-count erratum. Five product native
candidates remain spent; this amendment does not admit candidate six.

Selected maintained tests call the actual consumer with isolated native
footprints and pads, fake Add/GetFootprints ownership, and native getters.
The pre-fix consumer is RED because NONE remains inherited and a typo is
accepted; the corrected consumer is GREEN for all three modes, inheritance,
clearance-only behavior, generic selectors and invalid values. The old
project census is RED against the new exact NONE declaration. The updated
source census includes positive, missing/mode-swap, wrong-net, duplicate,
broad-selector, conflicting-pattern and declared realized-return blind-spot
controls. These source tests do not certify physical connectivity.

No reservation vertices, ADC_WEST_LOCAL xmin 89.35, placement, route seed,
via reservation/drop, CM exchange, ESD pad4 FULL mode, regulator host or
quiet-return intent changes. Global thermal gap, spoke width, minimum
resolved spokes, clearances, widths/current floors, rules, budgets, gates
and allowances retain their existing authority without new numeric bounds.

Fresh independent source review, complete source schema/numeric-provenance
preflight and applicable full tests remain required before any separately
admitted product-native work. The existing BOARD-based pad/side witness is
still owed. At the ordinary placement boundary, regenerate exact pad modes,
settings and regions and classify full-severity native DRC before prep;
all remaining placement separation, feasibility/policy, escape and tier
checks remain owed. Only after the required earlier gates pass may separately
authorized prep/fill establish the complete target-to-U_ADC.8/VMID2/drop path,
absence of ambient shortcuts, owner/drop cut disconnection, all four VMID
proofs, quiet-return proofs, paddle separation and complete raw DRC
classification. NONE alone is never a replacement for those graph/cut
proofs. No physical, release or order hold is cleared.
