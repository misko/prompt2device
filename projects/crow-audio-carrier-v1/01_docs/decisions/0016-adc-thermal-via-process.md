---
id: "0016"
date: 2026-09-08
status: accepted
---
# 0016 — explicit ADC thermal vias and a disjoint fabrication process

Accepted as source intent only. ROOT authored and screened it; this is not an
independent review, generated-board acceptance, thermal qualification or an
order authorization.

## Context

The clean baseline is bfe61d4ee04ba57984947b790d9f9195ec66c72a. The
11:40:16Z inventory binds 1,312 tracked carrier subjects / 103,476,554 bytes.
The native source census finds 299 footprints, 868 copper pads and 20 seed
vias. None of those vias is inside an undrilled component pad. ADC49 is a
4.6 x 4.6 mm GND exposed land with no thermal drops. LDO11 already has two
external drops; neither is a via-in-pad. No existing via needs reclassification.

Cirrus's general QFN note describes ground-connected thermal arrays with
approximately 0.33 mm holes and 0.74–1.27 mm spacing. It is September 2014
Rev 2.5 Wolfson guidance, not the dimensional authority for CS5308P-DN; its
other package examples are not copied. It discusses open vias and paste
segmentation, and does not mandate the filled/capped process chosen here.
[Cirrus WAN_0118, pp4,8](https://statics.cirrus.com/pubs/appNote/WAN_0118_Rev_2.5.pdf).

JLC's August 18, 2026 help page permits epoxy-filled/capped via-in-pad and
selection by hole diameter in order remarks. Ink plugging is not suitable
inside pads. This is public feasibility evidence, not a quoted four-layer
price, selected order option or allocation receipt.
[JLCPCB via covering, accessed September 8, 2026](https://jlcpcb.com/help/article/pcb-via-covering).

## Options

- No local array: leaves the exposed-pad source obligation unresolved.
- Open ordinary 0.20 mm holes under the paddle: no controlled solder-wicking
  protection and conflicts with the existing V-PROCESS requirement. Rejected.
- Protect some 0.20 mm vias but leave others ordinary: native flags alone
  do not survive a Gerber handoff; the owning drill-family selector cannot
  distinguish the processes. Rejected.
- Nine 0.60/0.30 mm vias with epoxy fill and copper cap, while all existing
  0.50/0.20 mm seed vias remain ordinary: selected. Adds process/cost review
  at ordering but gives the fabricator an unambiguous source requirement.

## Decision

Use the existing generic `floorplan.yaml thermal_vias.fields` capability:
ADC49, 3 x 3 grid on 1.00 mm pitch, local x/y in {-1,0,1} mm, centred at
[96,70] mm. Each true F.Cu-to-B.Cu via has 0.60 mm copper / 0.30 mm drill,
with item-level filling and capping enabled. The nominal annulus is 0.15 mm,
adjacent hole-edge gap 0.70 mm, and 1.60/0.30 thickness-to-drill ratio 5.333.
These are nominal geometric arithmetic, not manufacturing yield or thermal
resistance bounds. Nonconductive epoxy is not credited as a copper heat path.

Declare the protected 0.30 mm and ordinary 0.20 mm drill families in
`rules/assembly.yaml`, plus generated order wording and mandatory uploader
confirmation. None of the 107 native component-drill entries shares 0.30 mm.
Do not fill component lead holes. Keep all ordinary route/stitch via recipes,
all 72 seed banks / 201 primitives / 20 seed vias, physical stack, part poses,
net identity, class/current limits and existing scopes unchanged.

The footprint remains library-linked and byte-identical. Its native ADC49
land already requests solid zone connection; its nine separate paste windows
stay unchanged. The new documented source field is not an undocumented
thermal-via footprint substitution. Actual stencil/profile acceptance and
exposed-joint inspection remain order/first-article obligations.

Enable `route.forbid_new_via_in_pad`: the existing per-wave guard compares
each KRT output with its input, retaining reviewed source vias but rejecting
new in-pad escapes. This guard is not a stitch/process certificate. Final
source-authority and V-PROCESS checks must still verify every actual via,
including after import, stitch and save.

## Consequences

The first geometry hypothesis clears all tested native shapes. A diagnostic
JSON serialization error was repaired without changing geometry; both raw
runs are retained. The new source checker grades all four physical copper
layers, full via/drill shapes, existing seeds/vias, component/mounting holes,
keepouts and all 36 new hole pairs. The only allowed in-pad host is the exact
ADC49 rectangle, with the entire copper annulus contained inside it. Same-net
ground pads are not blanket-exempt from drill clearance. Existing 20-via
in-pad census remains empty. New fields are explicitly counted separately
from the legacy route-seed-only via helpers.

Hostile regressions reject missing drops, a foreign supply-pad site, adjacent
holes too close, an unfilled protected field and overlapping process families.
The actual unchanged baseline fails missing-drop coverage. Test-harness
accessor correction and final test evidence are recorded in the source report.

No top-layer shortcut is added to GND_A6/8 or GND_D30. Their existing separate
drops, VMID returns and local paddle-gap exclusions remain exact; both inner
GND planes remain unsplit. True filled-plane contact, return impedance,
thermal spreading and temperature still require the generated/routed board.
No BOARD was constructed/loaded/saved and no producer, router, checkpoint,
review or release output was changed here. Continue analog/source intent,
then fresh generation and owning reviews before routing. Retain all TOP77,
0.20 A first-power HOLD, sourcing/physical and no-main-until-both-child-seals
plus fresh exact-base/head P-PUBLISH requirements.
