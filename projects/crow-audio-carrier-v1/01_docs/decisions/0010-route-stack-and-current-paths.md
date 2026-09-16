# ADR-0010 — exact route ownership, public stack and bounded ADC launches

Date: 2026-09-08. Status: PARTIAL source correction; NOT ROUTE-READY.
No generated-board, thermal, SI, fabrication or release PASS is asserted.
ADR-0007 prototype scope and ADR-0009 electrical/current/state obligations
remain binding. This decision changes no component, pin, net topology or
physical qualification hold. Root independent source adoption remains owed.

## Exact membership and consumer authority

The native source still has 299 refs, 868 pin memberships and 205 nets:
164 connected nonground, common GND, and 40 intentional unused-pin nets.
Every connected net now has exactly one literal class. Class populations are
POD_POWER 11, POWER_TRANSIENT 8, POWER_CONTROL 25, BOOTSTRAP 1,
QUIET_POWER 11, ANALOG_AUDIO 96, ADC_CLOCK 12, GROUND 1. No unsupported glob,
ghost FILT1N/FILT2N net, or implicit class fallback is retained.

There are 163 generic-wave nets, one complete deterministic nonground net
(LDO_A_FILT, U_ADC.7 to C_LDO_A.1), one zone-owned GND, and 40 explicit NCs.
Partial prep fanout on 3V3_ADC/GND is not a second complete-net owner. Existing
wave/ownership consumers and shadow authority compilation verify this exact
partition; their success does not authorize routing. Shadow stack authority
does not replace floorplan.board.stackup, the actual physical emitter input.

POWER_CONTROL explicitly retains 0.25 mm clearance for MCH_3V3_SENSE,
TDM_SENSE_G and TDM_OE_N moved out of ADC_CLOCK. BUCK_BST is its own local
bootstrap switching-loop class: U_BUCK.6 to C_BUCK_BST.1, through that capacitor
to the switching-node side. It is not a quiet interlock or DC distribution net.

## Public four-layer candidate, not a fabrication allocation

The exact public [JLC impedance table](https://jlcpcb.com/impedance), recovered
unauthenticated on 2026-09-08, identifies JLC04161H-7628:

| Layer/material | Thickness mm | Relative permittivity |
|---|---:|---:|
| F.Cu | 0.035 | — |
| 7628 prepreg | 0.21040 | 4.4 |
| In1.Cu, common GND | 0.0152 | — |
| Core | 1.065 | 4.6 |
| In2.Cu, common GND | 0.0152 | — |
| 7628 prepreg | 0.21040 | 4.4 |
| B.Cu | 0.035 | — |

Arithmetic is 1.5862 mm copper plus dielectric against nominal 1.6 mm.
The emitter's 0.02 mm reconciliation tolerance is not a manufacturing tolerance.
The exact table's 0.0152 mm inner copper governs, not generic 0.0175 mm
half-ounce rounding. Public soldermask C1/C3 is 1.2 mil, C2 0.6 mil, Er 3.8.
The physical schema accepts one mask thickness, so 0.01524 mm records C2 only;
actual nonuniform mask must enter future SI analysis. No finish/order is chosen.
Loss tangent 0.020 is an explicit engineering placeholder because the table
does not allocate a material SKU/DF; unrelated laminate typical values are not
silently attached to this stack. Actual material, tolerances, plating and
controlled-impedance allocation remain manufacturer/ordering and later test work.

F.Cu signals reference In1 GND and B.Cu signals reference In2 GND. Add In2 to
the existing same-net GND zone declaration and match the shadow reference role.
No split inner ground or new power pour is introduced. The exact adjacency
denominator is preserved; no rail is declared poured to evade IC/cap obligations.

## Width, current and paired via boundaries

Keep POWER_TRANSIENT's 2.5 A bound. The existing external 1 oz/10 C source
helper requires 1.0630368549 mm; use 1.20 mm F.Cu bulk, not the old 0.80 mm
class floor or 0.60 mm wave. POD_POWER keeps 0.60 mm for its 1 A screen,
12V_PROTECTED's 1.20 mm override and prior explicit distribution/drop obligations.
QUIET_POWER's 0.35 mm floor retains the 0.30 A engineering allocation.
These are model/source consistency screens, not realized thermal/current proof.

All seven explicit common/stitch/seed via configurations now pair 0.50 mm
diameter with 0.20 mm drill: 0.15 mm annulus exceeds the 0.13 mm source floor.
At nominal 1.6 mm the aspect ratio is 8; at the public nominal-thickness +10%
screen it is 8.8, below the selected 10:1 capability. Stitch pitch 0.75 mm
gives 0.55 mm hole separation and 0.25 mm copper gap. Preserve the 0.50 mm
hole-to-hole floor and nudge-only repair; do not introduce smaller families.
See [JLC public capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/).
These geometric bounds do not certify a finished-hole plating allocation or
barrel ampacity. No high-current series layer-transfer bank is authored.

Ordinary taps.connections can automatically fall back to two vias even with
F.Cu intent; there is no allow_hop:false boundary and its via search defers hole
spacing. Therefore no ordinary high-current tap is added as a substitute for
current-transfer proof. A future bank must establish the genuine series boundary,
parallel current shares and finished-hole assumptions; counting nearby same-net
vias with via_ampacity_check is not by itself that proof.

## Adopted west-ADC sub-batch and limited placement correction

Only these three fixed poses change, in mm/degrees:

| Reference | Before x,y,rotation | After x,y,rotation |
|---|---|---|
| C_LDO_A | 90.6,70.0,180 | 89.8,70.0,180 |
| C_VDDA1_4U7 | 87.35,68.7,180 | 87.45,68.4,180 |
| C_VDDA2_4U7 | 87.35,71.3,180 | 87.45,71.6,180 |

The westward LDO capacitor move creates two outward independent GND_A drops;
the companion 4.7 uF moves remove the resulting courtyard collision. All other
296 expanded poses, all 11 connector datums, repeat banks, model bindings,
outline, mounting holes and fabrication floors remain unchanged. Existing exact
cap-to-ADC pin spans become 2.4830677, 4.9275374 and 4.8621626 mm respectively,
all within their unchanged 5 mm source proximity limit. The H3c candidate has
567 retained copper comparisons without conflict, plus body/courtyard and moved
foreign-pad screens; this is not generated P-LAND/DRC. Durable source tests also
screen reverse foreign-courtyard-to-moved-pad interference.

Nine exact prep banks are authored. U_ADC.5/.9 each leaves at 0.18 mm to its
same-net bypass side; aggregate 0.18 mm length is 4.10 mm. Two 0.60 mm extensions
of 0.45/0.50 mm move the 1.20 mm feed entries clear of new return copper.
U_ADC.7 has a complete 0.18 mm local path to C_LDO_A.1, owned only by prep.
U_ADC.6/.8 each has an outward 0.18 mm route and its own 0.50/0.20 ground via
at [91.6,69.5] and [90.55,71.0]. Their respective VMID 470 nF and 4.7 uF
capacitor grounds connect to these plane drops; most is 0.30 mm, with one
short northern 0.18 mm dogleg to clear the internal-LDO capacitor.

The ADC_WEST_LOCAL F.Cu area [89.5,67.7,93.6,72.35] scopes only 3V3_ADC,
LDO_A_FILT and GND to a 0.18 mm floor / 0.20 mm clearance. Every narrow item is
short and wholly inside it; item-overlap rule semantics are not a pointwise
license for long thin routes. Wider local returns and via geometry were screened
at 0.25 mm. The power wave retains 1.20 mm nominal and limits subnominal copper
to 5.05 mm / eight segments per net, minimum 0.18 mm, with automatic tap neckdown
disabled. The consumer measures wave output, not necessarily final copper after
taps/stitch/import. Exact final same-bound remeasurement remains owed, including
proof that each thin branch is a leaf and generic routing did not re-enter it.
KRT preserves original segment identities, but its single-ended endpoint selection
can consider all segment endpoints; source seeds alone do not ban re-entry.

At the unchanged normal aggregate ADC allocation of 0.15 A, a 2.25 mm x
0.18 mm x 0.035 mm copper leaf using rho85=2.1643958e-8 ohm-m is 7.730 milliohm,
1.1595 mV drop and 0.1739 mW. At 2.5 A that same leaf dissipates 48.31 mW:
no short-circuit duration or qualified thermal/fault withstand is invented.
The 0.60 mm extensions are approximately 0.464/0.515 milliohm, or 2.90/3.22 mW
at 2.5 A. The retained full source bound is not lowered to fit the pin row.
Normal branch accounting supports this source candidate; fault, startup,
current-sharing, EP/plane spreading and realized branch topology remain limits.

## Physical ground and public Cirrus reconciliation

The retained [Cirrus datasheet](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf),
July-2025 layout guideline and exact evaluation drawings are the primary basis.
The [official evaluation archive](https://statics.cirrus.com/pubs/software/DC5302P_4P_4S_8P_8S-ADC_Schematic_Layout.zip)
shows R351/R434 as zero ohms on negative filter returns, not nonzero series
resistors. Carrier FILTxN physical pins 44/17 remain directly GND; no ghost net
or electrical change is introduced. Only that stale parts-notes sentence changes.

GND_A6/8 must reach the common plane independently from the paddle while their
VMID returns reach those local grounds. A finite top-only track/via/pour keepout
[93.46,69.6,93.69,70.8] blocks the immediate straight paddle bridge. It is not
an inner-plane split, a board-wide digital moat or proof of every possible
top-pour path. Common ground under the package remains. Other GND_D pins,
FILTxN egress, exposed-pad thermal connections, actual zone-fill paths and
outer-ground stitching remain explicit next source/generated obligations.

## Digital SI and analog return budget

The twelve ADC_CLOCK nets are the three MCH input clocks, their three buffered
and three ADC-side series sections, and the three TDM sections. Three DC sense/OE
controls are not transmission lines merely because the old class included them.
Cirrus's 50 ohm digital recommendation is an intent, not proof from a class name.
Set F-only 0.36 mm bulk; bare finite-thickness Hammerstad/Jensen analysis gives
50.92205 ohm for W=.36,H=.2104,T=.035,Er4.4. At W=.18 it gives71.04307 ohm.
The [Qucs technical note](https://qucs.sourceforge.net/tech/node75.html) is the
analytical reference. This excludes mask, coplanar top GND, etch tolerance,
dispersion and launch/plane discontinuities: no actual field-solved or guaranteed
50 ohm result is claimed. Source stack and explicit path inventory make the
next geometry-specific solve actionable; no new solver dependency was installed.

Two existing copper_length_audit groups cover every physical endpoint of all
twelve nets, including the three input pull-down branches and each series
resistor/active-device boundary. They report actual path lengths and reject vias,
without imposing false equal-length matching between dissimilar clocks. Active
device/package delay is separate. The ADC_DIGITAL_RETURN existing projection
check binds F.Cu/In1.Cu/GND to these twelve exact nets: 0.25 mm projected foreign
track margin and 0.50 mm foreign-via copper margin, budgeting the 0.25 mm zone
antipad plus 0.25 mm residual reference margin. That consumer excludes the listed
signals and GND; it does not prove pad/hole clearance, complete filled-plane
continuity or per-net route reach. Those remain separately owed.

Analog classes retain exact pair/feedback topology and 0.20 mm copper. The
Cirrus input-trace 0.5 ohm DCR recommendation is trace copper, not the intentional
10 ohm series component; rho85 and nominal copper permit roughly161.7 mm of
0.20 mm trace before pad/joint allocations. Actual ordered traces, branch
geometry, pair symmetry and uninterrupted return must be measured after routing.

## Retained rejections and next owning work

H1 fixed-placement GND via had 0.175 mm pad clearance and 0.060 mm clearance
to the neighboring power seed. H2's westward C_LDO_A move cleared copper but
collided with both nearby 4.7 uF courtyards. H3a's three-pose candidate cleared
bodies, but its VMID return passed only 0.1784368 mm from C_LDO_A.1 against
0.25 mm. H3b's narrow dogleg improved that; H3c added and rescreened the wider
feed entries against all new returns/holes. All rejected artifacts remain.

The next four U_CLK.2/.3/.6/.7 launch hypothesis had 41 comparisons and two
wide-entry failures: U_CLK.3 to U_CLK.4 gap0.141039 mm and U_CLK.6 to U_CLK.5
gap0.223000 mm against0.25 mm. None of those clock seeds is adopted. Its
U_CLK.2 endpoint also approaches the same-net series-resistor pad, so any future
candidate must explicitly distinguish partial from complete deterministic ownership.

Next source author must extend/redirect those two bulk entries, close remaining
ADC clock/data, VDDIO, FILT positive and LDO_D launches, and bind low-current IC
taps separately from true series U_BUCK/U_LDO power exits. Root's full diagnostic
found22/185 nonground non-ADC IC lands below bulk width at conservative uniform
0.25 clearance: U_CLK.2/.3/.6/.7, U_BUCK.5, U_LDO.1/.2/.9, U_AUDIO.4,
U_CLK.8, U_ISO1..8.8, U_PWR.3/.4, U_RST2.2/.8. These are actionable hypotheses,
not native resolved-rule gate failures. Do not claim routing ready merely because
an exact partition or scoped subset is static-green. Subsequent source completion,
independent adoption, combined generation, fresh same-hash reviews and owning
physical/route gates remain required. All DO-NOT-ORDER, TOP77, first-power0.20 A,
service, sourcing, publication and qualification holds remain unchanged.
