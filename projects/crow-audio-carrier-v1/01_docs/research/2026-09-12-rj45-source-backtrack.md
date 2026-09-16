# RJ45 source backtrack — implementation preparation

Status: source-author proposal; exact parts and independent source acceptance
are pending. Carrier directive D8, pod D6 and parent D3 authorize the change.
This record does not change the executable interface or accept a PCB.

The parent owns `03_src/rules/spoke_interface.yaml`; both child copies must
remain byte-identical. The proposed ordinary straight-through eight-contact
map is:

| RJ45 contact | Signal |
|---|---|
| 1, 3, 7 | Protected +12 V for that pod |
| 2, 6, 8 | Power return / GND |
| 5 | AUDIO+ |
| 4 | AUDIO− |
| Metal shield | Carrier chassis; isolated from pod signal ground |

The blue pair carries audio. Each remaining pair carries one positive and one
return conductor. Parallel the three power conductors on each PCB. Retire the
active spoke WAGO joins, Belden 8503 pigtails and Micro-Fit field-crimp process
after the new complete assembly is selected. Their historical dossiers and
sealed dependencies are retained. J9 power input and J10/J11 digital headers
are separate interfaces.

## Source changes that must travel together

1. Parent contract and `check_spoke_interface.py`: exact jack/cord identities,
   eight physical paths per spoke, all three parallel conductors per rail,
   shield handling, complete hot-loop budget and 64 cross-board signal/power
   paths. Existing conductor counting by Micro-Fit cavity 1/2 must be changed
   to count the three distinct positive/return contacts. Do not copy the
   producer's pin map into a self-approving checker.
2. Both TSX sources, exact part dossiers and source-owned KiCad footprints:
   replace the four-contact spoke component with eight contacts and explicitly
   accounted shield lands. Manufacturer geometry, pin-view winding, PCB
   anchor and model axes must agree. Every shell land must be included in
   the electrical/physical census; no duplicate-pad exception by accident.
3. Both `check_spoke_implementation.py` files and focused tests: new exact
   contract digest, MPN, footprint and all physical pins, independently read
   from generated schematic/PCB. Reject a missing parallel conductor, audio
   reversal, shield-to-GND connection, wrong connector and extra connector.
   Preserve the existing inverse-census and stale-subject checks.
4. Both floorplans, electrical invariants, model registration and connector
   service/phase contracts: new mating plane, body, pegs, shield lands, plug
   boot/grip and cable bend. Preserve all-neighbors-populated service and
   explicit physical qualification. The actual carrier bank pitch is 32 mm,
   not the initial research brief's approximate 40 mm. Pod outline is 60 by
   40 mm. Do not reuse a Micro-Fit pad-1 anchor as an RJ45 anchor blindly.
5. Carrier requirements, power tree, assembly and coupon configuration, plus
   both first-article procedures: use the RJ45 measurement plane and exact
   manual-solder operation. PCB labels must identify pod audio/+12 V and
   distinguish the ports from Ethernet/PoE.
6. Pod connector-to-clamp protection and realized-route contract:
   `check_realized_routes.py`, `route.yaml` and associated tests currently
   start AUDIO+ at J1.3; it moves to J1.5. Existing source-seeded coordinates
   depend on the old footprint. Re-author those segments and peg keepouts
   from new geometry, maintaining connector-first clamp order and the 4.2 mm
   path limit. The previous promoted pod chain is obsolete for this revision.
7. New ADRs and cross-references: supersede the old connector decision
   prospectively, update architecture/brief decision registers and all active
   claims. Keep the original decisions and immutable pod release unchanged.

## Admission and verification sequence

Freeze the exact complete jack/cord assembly and electrical/thermal argument
before native generation. Review the source change with a fresh available
reviewer. Run targeted known-bad regressions and all affected source checks
before expensive schematic renewal. Preserve all previous checkpoint bytes
before retiring any guard; use the normal full conductor for changed TSX.

Accept newly generated schematic topology/readability first, then regenerate
placement and its ordinary assembly/locator/model/render artifacts. Fresh
exact pin, connector orientation, visual and layout reviews must judge those
bytes. Preserve LAYOUT-001's closed record and three spent diagnostic attempts.
The connector revision does not authorize another diagnostic under that ID.

After accepted placement, use isolated ordinary routing, then complete DRC
including every unconnected item, protection ordering, return paths, analog
matching, current/thermal and all existing release gates. The carrier remains
unrouted and the prior pod release remains the old Micro-Fit implementation.

## Sourcing constraints under examination

The cable must be factory terminated, shielded, copper and 15 m without field
crimping or cutting. A 50 ft cord is 15.24 m and exceeds the present 15 m
contract. Retain the 75 °C hot-loop calculation and 2.2 ohm finished-loop
ceiling at 0.10 A. The pod brief admits operation from -30 to +70 °C; the old
cable's -40 °C property is not itself a separate user temperature requirement.
A replacement cable must still support the admitted installation envelope.

Outdoor jacket/weather claims, indoor protected-installation proposals and
physical roof qualification are distinct. Conduit alone does not prove a dry
environment. Manufacturer resistance fields with ambiguous conductor-versus-
loop wording must be screened conservatively; a connector contact-resistance
allocation is a design budget until supported or measured.


## Source completion checkpoint — 2026-09-12T17:08:14.085718+00:00

Preferred cord proposal: HARTING09484747743150, exactly15m, Cat6A PUR shielded factoryDualBoot plugs; published -40..80C. Exact cableBOM094560006000301 and plugBOM0948CON47P8BK. Manufacturer maximum pair-loop DCR290ohm/km produces2.1125ohm at15m with3parallelpairs,1.25hotfactor and0.300ohm contactallocation. The plug drawing is approx45mm long,13.3mmwide,13.8mmhigh, nominalcable6.7mm. Dimensions need tolerance/physicalqualification; IP20plugs remain enclosed. Sourceoriginals/rootreopening are retained in journal/168cb286ee392f49e1ec95ab9e66077b0069bb63ca653665095a3d7262204160.tar.gz.

Manufacturer KiCad library rev26c supplies exact jack footprints/models. Initial jack report's geometry table is rejected:615008160221 rowsare4.0mm, not3.3mm. Correctproposedmap5AUDIO+/4AUDIO-. Itsbody extends7.09mmpastoddrow, so topESDoutsidebody cannotmeettheexisting4.2mmvia-freeprefix. Independentcomparison of221 withU3bottom against121 alltop plusa completechassisbond is pending. Do notsilentlyrelaxdistance, clamporder, all-criticalpathlayerchecks, or claim mechanicalfit fromcatalogdimensions.
