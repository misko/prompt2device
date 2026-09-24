# Connector fit-only coupon scope — Terra review

**Status: nonqualifying preparation only.**  This is a review of the proposed
fit-only use of the noncanonical partial-port fixture; it is neither a coupon
design release nor physical evidence.  It does not change the FULL predicate.

## Subject and binding

The only usable geometry snapshot is
`skills/kicad-pcb/scripts/tests/fixtures/crow_usb_partial_port/board.kicad_pcb`,
SHA-256
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.
The fixture README calls it noncanonical.  Direct native inspection finds all
eleven connector footprints at the intended field poses and a four-line,
220.0 by 120.0 mm `Edge.Cuts` rectangle (20,20 to 240,140); it finds **no
mounting-hole footprint**.  Thus it is not a candidate PCB with accepted
outline, mounting, enclosure, or process authority.

A fit-only prototype may only claim pad/footprint fit if it copies, without
translation or reflection, the following from that exact hash:

| Refs | Exact native footprint / pose | Exact fitted identity and mate/cable for the screen |
| --- | --- | --- |
| J1–J8 | `Wurth_615008160221_RJ45`, positions (50 + 22*n, 26.86), 0 degrees | Wurth 615008160221; Telegartner 100009141 selected by `connector_assemblies.yaml` |
| J_PWR | `Molex_43650-0200`, (30,29.42), 0 degrees | 43650-0200; 43645-0200 with two 43030-0038, and 226206-1022 only if its selected-harness record is included |
| J_USB | `GCT_USB4215_03_A`, (230,22.995), 180 degrees | USB4215-03-A; ASSMANN WSW A-USB31C-20A-100 |
| J_JTAG | `Samtec_FTSH_105_01_L_DV_K`, (228,50), 90 degrees | FTSH-105-01-L-DV-K; FFSD-05-D-06.00-01-N |

For each copied footprint, parity means reference, side, rotation, all pad
numbers, XY centers, sizes, drills/slot geometry, copper/mask/paste layers,
and footprint outline are byte-derived from this source board.  The four
edge lines and the 1.63 mm nominal fixture stack are likewise copied only as
fixture properties.  Do not add mounting holes, restraint features, a panel,
or enclosure geometry and then describe them as carrier geometry.  A small
per-connector coupon cannot screen simultaneous service; a fit screen needs
the complete eleven-connector field and the copied edge loop.

There is a source-identity trap to resolve before manufacture: the older
connector census calls J_USB `USB4105-GF-A-120` and names a previous
Weidmuller spoke mate, whereas the current contract and this fixture use
USB4215-03-A and Telegartner 100009141.  This review follows the current
`connector_assemblies.yaml` / qualification-plan selection.  The prototype
manifest must repeat those identities rather than silently mixing the older
census with the current geometry.

The retained public manufacturer drawings establish the part identities and
native land/hole patterns: Wurth 615008160221 rev 001.003, GCT USB4215 drawing
A, Molex 436501000-SD rev D8, and Samtec FTSH-DV footprint rev H.  They do not
establish the carrier's realized mounting, enclosure or cable route.

## What it can screen

When the exact connectors and mates are populated, a complete-field
fit-only prototype can record formative, negative-or-diagnostic observations:

| FULL target family (19 total) | Fit-only screen possible | What remains unproved |
| --- | --- | --- |
| `spoke_rj45.interface` (J1–J8) | Each exact plug can be inserted to apparent full seating; eight simultaneous plug bodies/cable starts can be observed against the copied connector field. | Carrier registration, enclosure collision, mating-plane acceptance and any FULL interface credit. |
| `usb_device.interface`, `external_power.interface`, `debug_jtag.interface` | Apparent complete engagement/polarization and immediate connector-to-connector collision can be observed with the specified mate. | Carrier/enclosure exposure, service clearance and FULL interface credit. |
| `spoke_rj45_service`, `usb_device_service`, `external_power_service`, `debug_jtag_service` | Grip/latch access and neighbor disturbance can be explored with all eleven connector mates populated; record failures as early design feedback. | The governed per-group service transition, component/enclosure neighbors, reaction restraint and service acceptance. |
| three `cable` targets (USB, power, JTAG; RJ45 cable behavior is within its profile observations) | Initial cable exit and cable-to-cable interference in the copied field can be photographed.  The JTAG ribbon's selected signed ±Y exit can be chosen experimentally. | Installed route, straight run, first controlled bend/radius, strain relief, far-end support and enclosure clearance. |
| four `reaction` targets | A gross failure can be discovered during gentle manual mating. | Any reaction result: the fixture has no governed adjacent mounting restraints, and its joints/stack are not the accepted carrier process. |
| four registration targets | Raw connector-to-fixture-edge and seating measurements may be rehearsed. | Carrier mating-plane-to-outline/process stack, contributor stack, and a derived exposure/setback allowance. |

Accordingly, the prototype can inform the *form* of every interface/service
check and can expose a clear negative fit result.  It closes **zero of the 19
FULL targets**.  It may not be used to infer a passing reaction, tolerance,
installed-route, enclosure, cycle, force, deflection, or service-clearance
result.

## Required record label

Any artifact should be labeled `FIT-ONLY / NONCANONICAL / NO FULL CREDIT`, bind
the fixture hash and the exact connector/mate/cable lot manifest, and retain
photos plus raw observations.  It must state that the current `connector_assembly`
FULL gate remains `INCOMPLETE` with 19 physical unknowns.  A later governed
coupon or candidate board must be re-bound to its accepted native PCB,
outline, mounting method, assembly stack and intended enclosure before it can
test the qualification-plan load cases.
