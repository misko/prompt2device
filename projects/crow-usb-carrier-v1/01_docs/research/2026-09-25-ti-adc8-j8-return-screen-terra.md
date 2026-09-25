# ADC8 cap/J8 pocket return-path feasibility screen

**Disposition: a physically clear future GND-via location exists, but the current board proves neither its connection nor an ADC8 return path. No exclusive pocket is source-authorized yet.** This is a native-geometry screen on the source-generated integrated board, not routing, P1, or P2 evidence.

## Bound inputs and rule authority

The board is `01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/candidate.kicad_pcb`, SHA-256 `0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`. It retains all 27 fixed references, including J8. Source declares `analog_ch8=[179,42,201,84]` and `usb_vbus_sense=[195,62,220,82]` mm. The zone declaration is a solid GND `In1.Cu` zone with 0.15-mm clearance and 0.20-mm minimum thickness; the saved zone is **unfilled**. The ordinary via family is 0.60-mm diameter / 0.30-mm drill and the native default different-net clearance is 0.15 mm. The 0.20-mm filled/capped POFV family is reserved for U_LDO and U_ISO B2 sites and is not a general ADC8 return via.

`C_ADC_AC8N1` at `(198.00,60.05)` is a *series signal* capacitor: pad 1 is `ISO8N` at `(196.20,60.05)` and pad 2 is `ADC8N` at `(199.80,60.05)`. It has no GND pad. Its full checker envelope is `[195.205,58.305,200.795,61.795]` mm. A GND via cannot be a direct cap return; at most it may stitch a *subsequently filled* reference plane under a routed ADC8 signal.

## Conservative native-via screen

I sampled 0.05-mm centers for an ordinary 0.60-mm GND via inside the current analog rectangle below the USB y=62 boundary. A center was admitted only if the via copper remained inside `[179,42,201,62]`, had at least 0.15 mm to all non-GND native pad bounding boxes, and its 0.60-mm copper did not intersect any checker `_physical_envelope` (body/courtyard, excluding text).

The nearest admitted center to `C_ADC_AC8N1.2` is **`(199.80,58.00)` mm**, 2.050 mm center-to-center from that signal pad. It clears the cap envelope; it is a possible later GND-plane stitching *site*, subject to actual route and zone-fill DRC. The superficially nearer copper-only location `(198.65,60.05)` is 1.150 mm from `ADC8N` but lies within the cap courtyard, so it is rejected for a physical-pocket screen. A via immediately east or north of the ADC8N pad cannot fit: the 0.60-mm via needs center x >= 200.95 or y >= 61.95 to keep the required 0.15-mm copper gap, while exclusive containment limits its center to x <= 200.70 and y <= 61.70.

This does not make the 2.050-mm site a valid return. The zone has no filled polygon, there is no trace from either ADC8 endpoint, and the source P1 analog-boundary demand is explicitly F.Cu. A via cannot silently transfer that signal demand to In1.Cu or substitute for the required continuous filled In1 reference below its future F.Cu route.

## J8 and ownership result

Fixed J8 is not the local copper obstacle. Its full envelope ends at y=34.495 mm, 23.810 mm south of the cap envelope. Its GND pads 2, 6, and 8 are 29.653069, 30.635700, and 31.315359 mm from `C_ADC_AC8N1.2`, respectively. They cannot establish a local return by proximity.

J8 nevertheless matters to authority: it is an `analog_ch8` functional member whose fixed connector envelope lies outside the channel's primary y=42..84 rectangle and overlaps the USB-side planning area. Functional ownership may span disconnected occupied physical cells under the current checker; it does not require a transit strip. But branch endpoint validation still uses the primary `regions[block]`, not `physical_cell_id`. The unchanged global census (115 outside-primary references; 139 foreign-planning references across 150 incidences) therefore cannot prove an exclusive ADC8 pocket or a handoff from J8 to the local cell.

## Required next test

The next coupled source candidate must declare the primary-region/physical-cell relationship for the J8 connector pocket and the ADC8 component pocket, then route the exact `ADC8N` endpoint from `C_ADC_AC8N1.2` on F.Cu while preserving a filled continuous In1.Cu GND reference. It must add a GND via only after full-profile DRC validates its real clearance and show the filled zone is connected where the route crosses. Re-run the owner census and branch check with that source model. Until then the 2.050-mm coordinate is a bounded geometry candidate only; it earns no capacity, return, P1, or P2 credit.

## Reproduction

The screen read the candidate with PCBNew and used the checker `_physical_envelope`, all native pad bounding boxes, the source zone/rule values above, and the stated 0.05-mm grid. It made no PCB, source, zone-fill, or route edit.
