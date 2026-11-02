# Integrated successor assembly controls

LS43 author candidate — not yet adopted or independently accepted. Applies to
the LS43 source-bound carrier/pod native copies of accepted LS42 placement and 38 selected model/part
identities. No component, footprint, population or electrical substitution is
authorized. This consolidates the LS41 proposals; it does not change historical
receipts or claim performed manufacturing/inspection.

## Common acceptance method

Measure against one registered finished-board datum using multiple native
copper/footprint features, with known metrology uncertainty. A measurement whose
uncertainty crosses a limit fails; do not recenter a component envelope after
observing a protrusion. Retain exact component/PCB lot, board serial, datum,
fixture, method and result. Procurement must transmit the complete final limits
and obtain fabricator/assembler agreement before ordering or execution. A
supplier refusal or failed article returns to the causal design owner; it does
not authorize a waiver, reaming, component trimming or undocumented substitution.

Before soldering, verify correct numbered contacts/polarity and free compatible
insertion. After soldering and fixture removal inspect actual final pose,
seating, joints and required clearances. Electrical continuity alone proves
neither seating nor joint retention. No physical results are supplied here.

## Incoming whole occupied packages

The following exact parts must fit their declared model boxes relative to the
numbered-contact datum, including all terminations, flash and burr. XY is native
footprint-local; Z is above the termination seating plane. These four boxes are
designer reject limits, not invented maker maximum tolerances.

| MPN | X mm | Y mm | Z mm |
|---|---|---|---|
| C2012X7R1V225K125AE | -1.25..1.25 | -0.75..0.75 | 0..1.65 |
| MMBT3906LT1G | -1.32..1.32 | -1.67..1.67 | 0..1.45 |
| SP0504BAHTG | -1.50..1.50 | -1.775..1.775 | 0..1.45 |
| CB3LV-3I-12M288000 | -3.60..3.60 | -2.60..2.60 | 0..2.00 |

Use optical dimensional/height inspection with uncertainty appropriate to these
boundaries. All other exact model envelopes remain subject to their retained
maker facts and independent model judgments; this table does not accept them
by omission. No body may be cropped to make a clearance image pass.

## Installed occupancy

Overall per-part outer cap: contact-datum radial XY displacement <=0.10 mm and
total rigid 3D axis-angle deviation <=1 degree from native pose. Neither quantity
is a per-axis allowance. Common coordinate registration is not a second
independent part displacement. All applicable contact, board seating, finished
mount and connector-specific limits below are conjunctive restrictions, not
additional error allowances. In particular, the general cap cannot authorize
board penetration, lifted required contacts or a plug outside its service region.

The current LS43 XY-only calculation must check all9,918 pairs under
the general cap, conditional on the declared occupied envelopes. Historical
LS41 minimum0.12294359mm is a comparison, not a current input binding. This is
only external-neighbor evidence. Preserve actual land overlap, correct maker
orientation, solder-contact and seating requirements independently. Process
capability and incoming/finished metrology remain pre-execution holds.

## Free-lead manual parts

| Ref | Section maximum mm | Finished plated hole mm | Combined prepared lead-to-hole center error mm | Actual external annulus minimum mm |
|---|---|---|---|---|
| Pod MIC1 | rectangle0.50x0.47 | 0.82..1.03 | 0.05 | 0.13 |
| Pod BZ1 | round diameter0.90 | 1.52..1.73 | 0.10 | 0.13 |
| Carrier U10 | rectangle0.60x0.30 | 0.92..1.13 | 0.10 | 0.13 |

Each center-error limit is combined AFTER permitted free-lead preparation and
includes actual pitch, hole location and body pose. Do not add an uncounted maker
pitch tolerance. The source/native-bound section checks give positive radial
clearances0.016889/0.210000/0.024590 mm; they are not rigid maximum-pitch proofs.
The U10 largest hole and smallest nominal land leave0.185mm before copper/hole
edge error, hence only0.055mm for their combined loss at the0.13mm actual ring
limit. Inspect all applicable copper layers/no breakout and required net
clearances, not only a top-side photograph or a via-only design rule.

Prepare only supported free lead length away from seals/cases; do not transfer
forming loads into the package, damage plating or force insertion. No unvalidated
forming near a seal/case, pin thinning or bending a rigid connector is permitted.
Require free insertion and correctly seated cases before hand soldering. Retain
the existing acoustic-part solder/handling limits. An operation needing unsupported
forming strength must stop for review. Inspect solder wetting and retention
separately; positive section clearance is not a solder-process qualification.

## PJ-102AH mount

Retain the three nominal1.60-mm round drills. Finished opening diameter must be
1.60..1.73mm. The complete actual center pattern must satisfy the maker top-view
PCB dimensions in one datum: two successive3.00+/-0.05-mm spacings,4.70+/-0.05-mm
transverse offset and indicated common alignments/orientation. Preserve numbered
mapping1=(0,0),2=(0,6),3=(4.7,3) under the documented rigid orientation. This is
not permission for independent per-hole errors whose differential sums exceed
the maker pattern. Absolute body/pattern registration must also meet installed
pose and connector-service controls.

At each actual compliant center the finished circle contains a nominal maker
1.00x1.60 rounded capsule. This supports standard-interface insertion compatibility
without inventing stamped-terminal thickness. It does not prove arbitrary pin
geometry or solder equivalence. The ordinary JLC negative hole allowance does
NOT guarantee the specified1.60 minimum; explicit process agreement and lot
metrology are mandatory. If infeasible, backtrack to the maker plated-slot
pattern through the owning native/fabrication gates.

Require actual continuous annulus>=0.30mm on all applicable copper layers, no
breakout and required net clearances. Pad1 is square and pads2/3 circular;
their2.60-mm minimum nominal span leaves0.435mm at the largest hole before
registration/etch, hence0.135mm combined loss at the finished0.30-mm criterion.

Hand-solder all three terminals, including NC switch terminal3. Fixture the
correctly oriented fully seated case through solidification; inspect after
fixture release. No forcing, reaming or tilting to hide a mismatch. The enlarged
round opening requires a qualified manual process: wetted lead/barrel and both
external lands, no bridge/crack/lifted copper, >=75% through-thickness solder
fill. The fill percentage is a designer prototype criterion, not a quoted maker
or IPC standard. Confirm a verifiable inspection/process-coupon method for
hidden fill before execution; surface appearance alone is insufficient.

Before accepting hardware, qualify selected PP3-002A insertion/withdrawal on a
representatively supported board without a separate fixture carrying jack load.
Maker mating-force range0.3..3kg is approximately up to29.4N, not a demonstrated
board-joint rating. Require no position change beyond limits, cracked joints,
lifted copper or lost continuity after the agreed normal-mating load test.
Maker500g terminal-strength entry is not an additive board-retention rating.
No retained source establishes performed joint strength; that remains a named
physical qualification gate of this otherwise source-compatible mount.

## RJHSE-5080 mount and underside scope

Use the retained X080RevA exact5-variant recommended eight-contact/two-peg
pattern, not the shielded variant. Require finished contact holes0.89+/-0.05mm
and peg holes3.25+/-0.05mm. The nominal sizes come from the recommended pattern;
these +/-0.05mm finished ranges are designer reject limits, not claimed maker
or ordinary-fabricator tolerances. Require the complete indicated maker center
pattern and datum tolerances. Do not reinterpret a BASIC center as an independent housing
+/-0.015-inch tolerance. Reconcile purchased revision before fabrication/assembly;
an incompatible revision requires design review. Native nominal matching does
not establish finished-hole metrology or actual supplier capability.

Inspect compatible undamaged insertion, full seating, correct contact mapping,
all required solder joints and retention. Do not force/trim compliant pegs or
invent their private dimensions. The model's4mm peg depth is illustrative, not
a physical maximum or permission to claim a floor clearance.

No unselected roof surface, enclosure, standoff, screw/nut/washer, support or
other hardware may occupy the below-board connector/free-lead zones. Actual
underside XY occupancy must remain within its reviewed finite column limit,
including any prepared lead paths; no projection can be silently omitted. Use
the exact per-reference native-frame rectangles in
`06_build/recovery/ls43-fit/checks.json` under `underside`: each nominal complete model XY
rectangle is expanded by its stated per-reference finite pose displacement.
For unknown peg depth this is an independently inspected DESIGN-OWNED installed
projection limit, not an inference from rotating an infinitely long peg. Preserve
the official U3 STEP XY proxy and stricter no-protruding-pool rule. A
length unknown but confined to a disjoint column cannot cause another modeled
component collision, but cannot establish enclosure/floor clearance. Installation
hardware and weather enclosure remain separately selected/reviewed deployment
work, not excluded from the eventual rooftop device by this bare-board scope.

## Integrated connector service and board datum

These current service/seat limits supersede only the corresponding LS34/LS39
external service allocations. Preserve exact accessory identities, wiring,
electrical limits and all LS33 module pool/registration/relief/contact controls.
Historical nominal access prisms in the scene are screening evidence, not the
entire finite service proof. Evaluate the following full corridors against the
actual current board and every nonowner. Intended internal engagement is limited
to the named standard interface, never a whole-component collision exemption.

Use the registered finished-board frame with nominal top Z0. In connector
service/seat zones require the complete finished top surface, including copper,
finish, mask and local warp, Z<=+0.05mm. This is a designer inspection limit, not
a claim of ordinary fabricator capability. At DC/RJ support points require case
datum elevation0..0.10mm, actual support gap0..0.05mm, no penetration, rocking,
debris or forced seating. The general pose cap and all mount constraints remain
conjunctive. A finite feasible witness is local top Z0.025, case datum Z0.04,
small nonzero in-plane/yaw deviations and sufficiently small roll/pitch; it is
not proof of process capability or a license to force a particular component.

U3 instead retains LS33 actual castellated pad gaps0..0.15mm and gap spread
<=0.15mm, all four relief-hole/pool conditions, no bearing and no pool below
the carrier. Its support datum is0..0.20mm with the above finished-top bound.
The existing combined module-to-actual-hole radial0.10mm includes mount errors;
do not add another fit allowance. Additionally, both front A/B finished-hole
centers must each lie within radial0.05mm of their nominal board-datum position.
Thus the front A/B midpoint's absolute module anchor error is at most0.15mm;
the0.05 absolute-hole location and0.10 module-to-hole relationship are distinct.
For the USB transform, the0..0.20mm support-datum elevation applies at the front
A/B midpoint(165,3.55) as well as the module datum. Establish it from the four
existing perimeter contact windows at end castellations1/40 and20/21, whose
support-plane polygon contains that midpoint. Retain actual local flatness and
no-bearing checks; do not extrapolate a central-height measurement to the front
under1-degree tilt. This is the same seating bound, not an added allowance.

### DC service

Retain PJ-102AH + straight PP3-002A, center positive, barrel diameter5.5/bore2.1,
exposed length9.5+/-0.3mm, cover diameter<=8.5mm. Reserve native-frame
X182.90..193.10, Y-35.85..1.85, Z1.30..11.80mm. The entire nominal approach
path expanded0.85mm contains radial0.10/total1-degree displacement; upperZ
includes permitted0.10mm seating once. Finished board gap is>=1.25mm.
Only the selected barrel engages the named receptacle. Co-transforming the
compatible pair preserves relative engagement; a filled-housing envelope is not
a private cavity simulation. No right-angle boot, cable bend or enclosure fit.

### USB service

Retain original SC0915 Rev3 module with D1-only removal and controlled Tensility
10-02333/10-02351 micro-B accessory, boot<=10.1x6.3mm and exposed nose>=5.4mm.
Reserve X159.10..170.90, Y-35.85..1.25, Z-1.89..6.61mm. Source exterior-shell
rearY6.35 bounds nominal boot front atY0.95; this is not an internal stop depth.
With front anchor(165,3.55,0), radial0.15mm and total1degree, the directional
inward-Y bound is0.286957514mm; boot front<=1.236957514. UpperZ includes seat
0.20mm once. Preserve required finished clear rectangleX158.6..171.4/Y0..1.4,
inside radius<=0.60mm, edge error<=0.10mm, relief-hole-to-notch web>=0.45mm and
all-layer copper clearance>=0.25mm. Full corridor has0.50mm side/0.15mm back
clearance through the all-Z void. Only the selected USB nose engages its shell.

### RJ service, nine identical instances

Retain RJHSE-5080 + ASSMANN A-MO8/8-SRS-x bare8P8C (ASS7232COrev05): plug
width<=11.78mm, body height<=8.30mm, latch projection<=2.87mm, depth<=20.70mm;
cableOD4.5..5.5mm,24-26AWG stranded copper, insulation0.95+/-0.05mm. No CCA,
PoE/Ethernet attachment or bulky boots. Use the controlled slim latch-release
tool/access procedure; no finger-access or arbitrary-tool clearance claim.

For each service centerX (carrier11.555+18.7*n, n0..7; pod10.555), reserve
Xcenter+/-7.20, Y-20.70..1.97, Z-0.70..15.30mm. Nominal full front-face bounds
and allowed pose place the mouth withinY0.055744812..1.704255188. The certainly
exterior segment endsY0.05; only the selected own8P8C nose/latch interface
engages the mouth transition up toY1.71. Protect board and nonowners throughout
that interval. No numerical mated plug floor is assumed.

Each new native recess is nominal16.0mm wide,2.4mm deep,R0.5. Require finished
all-Z clear rectangleXcenter+/-7.30/Y0..2.30, edge error<=0.10mm, inside radius
<=0.60mm and actual finished peg-hole-to-recess web>=1.50mm. The service corridor
then has>=0.10mm lateral and>=0.33mm rear material clearance at every height.
Preserve both peg supports and all eight contacts; inspect case seating and
retention. Source-supported body overhang is not a peg/pad exemption. Verify
physical insertion/withdrawal and latch release on a representative supported
board before hardware acceptance, without a separate fixture bypassing jack
loads. No retention rating or performed qualification is claimed.

## Design versus execution

Source-bound design acceptance must resolve all model/board/interface claims
before issuing a receipt. Supplier agreement, dimensional inspection, vendor
rotation preview, actual solder/retention tests, firmware/audio and environmental
qualification remain separate, unperformed gates. DO-NOT-ORDER is not a waiver
for an unsupported dimension or known collision. Final recipient fabrication
instructions must carry this entire accepted successor, not contradictory old
controls. The accepted historical native boards and sealed v1 remain unchanged;
the LS43 copies carry the independently accepted LS42 outline revision.
