# Final author candidate4 — outward power jack

Frozen native: `candidate4/native/pcb/carrier/carrier.kicad_pcb`.
SHA256 `1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1`.
Exact source r9 SHA256 `ddc5f5b1c3cba999db77b1e2a0a8dd24f004579ec825ccec991169a0af3aa099`.
Candidate4 is a native engineering deliverable awaiting independent acceptance,
not manufacturing approval, release or purchase authority.

## Pose and mechanical scope

J1 is180° at anchor(188,14.7). Pin1 VIN12=(188,14.7), pin2 GND=(188,8.7),
pin3 NC switch=(183.3,11.7). Nominal body center=(188,8.2), mouth planeY1.0,
facing native-Y outward. This retains the maker pin mapping, not a mirrored or
net-swapped approximation. Body nominal boundsX183.5..192.5,Y1.0..15.4.

The maker TOP VIEW's mouth-to-switch10.7 plus switch-to-pin1 3.0 establishes
mouth local+Y13.7; the14.4-depth body occupies localY[-0.7,13.7]. A bare180°
rotation around the original pin1 would be wrong: the origin must relocate.
Maker drawing, units, tolerances and retained hash are in `AUTHOR-REPORT.md`.

Independent reviewer identified candidate3's D1 worstcase gap as too fragile;
parent explicitly authorized a distinct-cause mechanical robustness repair:
move J1 0.5mm toward the edge, from anchorY15.2 to14.7. The move increases rear
body-to-D1 margin and moves mouth fromY1.5 to1.0. This was NOT a third blind
cooling repair. Independent reviewer owns the final tolerance/cable/access
calculation; no generic render/model establishes physical compatibility here.
Round drilled-hole substitution, vendor solder/retention/process review,
enclosure/accessory fit and physical qualification holds remain unwaived.

## Native service preservation

`candidate4/native-evidence.json` records native before/after pads, tracks,
zones, ground-return samples and numerical checks. Preservation results:

- 142 footprints retained; only J1 changed. Other 141 footprints are raw-node
  identical, including the TI clock area.
- 185 vias, complete layer/stackup setup, outline/recesses, graphical nodes,
  all1347 common track items, schematic/project/libraries/resources unchanged.
- Eight local VIN/FUSED segments replaced by 11 at retained 0.8mm F.Cu width;
  no added vias or narrower current path. See patch-record and native evidence.
- VIN route: (188,14.7)→(182.5,14.7)→(179.5,11.7)→F1.1(179.5,9.455).
- FUSED main and left cooling branch remain as documented in candidate3 history.
  The cooling polygon retains its top-rightY5.5 extension, without changing
  connection rules or weakening a keepout.

Filled FUSED copper is now ONE continuous polygon216.184474mm², versus original
206.407582mm². The moved VIN trace no longer divides it into two polygons.
The D3-adjacent rectangle[186,16.9,199,22.5] has EXACTLY the original filled
area71.974517mm². The existing12V output cooling zone remains232.785124mm².
These preserve direct D3 spreading and increase overall FUSED area; they do not
prove a new junction-to-ambient rating. Retain the existing D3 power/thermal
sensitivity and qualification obligations.

Each inner GND plane remains one18585.956869mm² polygon. J1 pin2 retains all
four45° thermal spokes into each plane, with all12/12 radial samples per plane
at1.05,1.6,2.0mm in the respective continuous fill, before and after. All other
ground vias, pads and escapes are unchanged. This is concrete shared-return
inspection in addition to the opens check, not a DC-open-only argument.

VIN authored length18.170→11.988mm; FUSED total19.404→44.101mm (includes redundant
cooling branch). Native35µm copper,0.8mm width and100°C sensitivity give a
pessimistic combined trace resistance45.392mΩ, drop30.867mV at retained680mA,
and45.392mW at1A. The FUSED estimate sums both branches as series and ignores
parallel zone copper, intentionally overestimating trace contribution. Contact,
fuse/diode losses, stack tolerances and IPC ampacity are not established by this
estimate. No fuse increase, demand reduction or power requirement change.

## Strict checks and exact replay

`candidate4/drc.json` is freshly refilled/saved native KiCad10.0.4, all-severity,
all-track, native schematic-parity: zero violations, opens, parity and ignored
checks. `candidate4/routing-geometry.json` has zero drill/SMD and annulus-gap
findings under inherited explicit0.15mm allocation. No exclusions were added.

Reproduce in a new directory:

```sh
/usr/bin/python3 projects/crow-array/order-readiness/power-jack-r10/author_power_jack.py --output reproduce-final --preserve-cooling --jack-anchor-y 14.7
/usr/bin/python3 projects/crow-array/order-readiness/power-jack-r10/inspect_power_jack.py reproduce-final
```

`replay4-complete` was generated from exact r9 by the final script, passes the
same strict checks and has BYTE-IDENTICAL native SHA256 to candidate4. Producer
checks actively reject ignored checks, violations, opens, parity and geometry
findings. Per-input resource hashes are in each patch record.

Earlier diagnostics/candidate1..3 remain preserved. Their limitations and two
bounded cooling repairs are recorded in `AUTHOR-REPORT.md`; they are not the
final handoff. Candidate4/replay4 initially hit a report-schema assertion
(ignored_checks is an empty list, not integer0), AFTER clean CLI completion;
the producer assertion was corrected without changing native bytes, and
`replay4-complete` cleanly verifies the corrected end-to-end script.

No r9, STATUS, quote package, skill, repository ref or external JLC state was
changed by this author. Parent owns derivative packaging/renders and independent
mechanical, electrical/thermal and promotion decisions.
