subject: crow-audio-carrier-v1 isolated fuse-land-pin-review
date: 2026-09-11
reviewer: /root/carrier_fuse_land_pin_review (fresh independent source judgment)
context-given: frozen input packet; envelope SHA256 ab7ff74202d0038b42d709ca202ad108b8786e92937b122ea41d41cf544fbb55
source_commit: db86586129445c88b37d0a6a9ba52d6cec19d0b8 plus enumerated uncommitted source packet
board_sha256: 9cc82becb56a74eff2fa20a4a1b9a64c132e2b05c1e7f2ac413059fe055d9f48
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
scope: Limited source review; original verdict and limitations below. No canonical placement or release acceptance.
original_report_sha256: 595db597c2080a488b002f47c36114602f0c968f08c57719d27efeffce018306

# Fresh exact F1..F8 source land/pin and local-clearance review

## Verdict

**PASS for this isolated diagnostic source projection.** The exact Littelfuse family land, exact `/60` maximum body, all 16 fuse-pad identities/nets, both implemented footprint orientations, all eight local physical-clearance sweeps, and all eight owning-net F-to-J copper gaps agree with the supplied authorities and limits. This is not canonical-board placement approval, routing approval, model-registration closure, release approval, or physical/thermal qualification.

## Source authority and implemented land

The supplied PDF bytes (`a18b5cee...fb974`) were freshly rendered and visually inspected at pages 6 and 7. Page 6 gives the 1812L family recommended land as two **1.78 x 3.15 mm** rectangles separated by a **3.45 mm inner gap**, hence a **5.23 mm center pitch**. The exact `1812L035/60` dimensional row gives maximum body A x B x C = **4.73 x 3.41 x 1.80 mm**. Page 7 lists exact ordering number **1812L035/60MR**, tape-and-reel, quantity 1000.

The source footprint implements pad 1 at local x=-2.615 mm and pad 2 at local x=+2.615 mm, each 1.78 x 3.15 mm, matching that land exactly. Both are rectangular F.Cu/F.Paste/F.Mask pads with zero local/effective mask expansion and zero paste margin in the native board. F.Fab is the 4.73 x 3.41 mm maximum body. F.CrtYd is 7.52 x 3.92 mm. Its minimum source clearance is **0.255 mm**: vertically from the maximum body and horizontally from copper; the other body/copper directions are larger. The source 3D envelope also encodes 4.73 x 3.41 x 1.80 mm and is expressly dimension-derived rather than manufacturer CAD.

## Pin identity, orientation, and coordinates

The native board, native netlist, and TSX agree for all 16 pads: pin 1 is `12V_PROTECTED`; pin 2 is `12V_PODn`. TSX independently contains the exact -2.615/+2.615 mm pad centres, 1.78 x 3.15 mm sizes, and the stated connections. Native netlist coverage is 8/8 pin-1 nodes on `12V_PROTECTED` and one exact F*n*.2 node on each corresponding `12V_PODn`.

| Ref | Footprint origin / rotation | Pin 1 physical centre / net | Pin 2 physical centre / net |
|---|---:|---|---|
| F1 | (29.150, 36.500), 0° | (26.535, 36.500) / 12V_PROTECTED | (31.765, 36.500) / 12V_POD1 |
| F2 | (61.150, 36.500), 0° | (58.535, 36.500) / 12V_PROTECTED | (63.765, 36.500) / 12V_POD2 |
| F3 | (93.150, 36.500), 0° | (90.535, 36.500) / 12V_PROTECTED | (95.765, 36.500) / 12V_POD3 |
| F4 | (125.150, 36.500), 0° | (122.535, 36.500) / 12V_PROTECTED | (127.765, 36.500) / 12V_POD4 |
| F5 | (51.850, 103.500), 180° | (54.465, 103.500) / 12V_PROTECTED | (49.235, 103.500) / 12V_POD5 |
| F6 | (83.850, 103.500), 180° | (86.465, 103.500) / 12V_PROTECTED | (81.235, 103.500) / 12V_POD6 |
| F7 | (115.850, 103.500), 180° | (118.465, 103.500) / 12V_PROTECTED | (113.235, 103.500) / 12V_POD7 |
| F8 | (147.850, 103.500), 180° | (150.465, 103.500) / 12V_PROTECTED | (145.235, 103.500) / 12V_POD8 |

The 180° instances correctly reverse physical left/right while preserving logical pad numbers and nets.

## Exhaustive local-clearance results

KiCad 10.0.4 supplied the transformed courtyard and effective pad polygons. The review measured each fuse courtyard against all 339 other same-side component courtyards and against all 959 foreign F.Cu effective pad polygons. That copper set comes from 1,002 board pad objects; after removing the fuse's own two pads, 41 remaining objects have no F.Cu polygon, so each per-fuse physical-pad denominator is 1,000 objects and its copper-polygon denominator is 959. Every footprint has a usable same-side courtyard. The exact maximum-body polygon was also checked against the same 959 foreign copper-pad polygons.

| Ref | Nearest other courtyard (339 checked) | Fuse-courtyard to nearest foreign F.Cu pad (959 polygons / 1,000 objects) | Max-body to nearest foreign F.Cu pad (959 polygons) | F*n*.2 to J*n*.1 owning-net copper gap (limit 4.5 mm) |
|---|---:|---:|---:|---:|
| F1 | C_A1P, 0.350 mm | C_A1P.1, 2.859 mm | C_A1P.1, 4.015 mm | 4.006 mm, PASS |
| F2 | C_A2P, 0.350 mm | C_A2P.1, 2.859 mm | C_A2P.1, 4.015 mm | 4.006 mm, PASS |
| F3 | C_A3P, 0.350 mm | C_A3P.1, 2.859 mm | C_A3P.1, 4.015 mm | 4.006 mm, PASS |
| F4 | C_A4P, 0.350 mm | C_A4P.1, 2.859 mm | C_A4P.1, 4.015 mm | 4.006 mm, PASS |
| F5 | C_A5P, 0.350 mm | C_A5P.1, 2.859 mm | C_A5P.1, 4.015 mm | 4.006 mm, PASS |
| F6 | C_A6P, 0.350 mm | C_A6P.1, 2.859 mm | C_A6P.1, 4.015 mm | 4.006 mm, PASS |
| F7 | C_A7P, 0.350 mm | C_A7P.1, 2.859 mm | C_A7P.1, 4.015 mm | 4.006 mm, PASS |
| F8 | C_A8P, 0.350 mm | C_A8P.1, 2.859 mm | C_A8P.1, 4.015 mm | 4.006 mm, PASS |

No courtyard overlap, maximum-body/foreign-pad contact, or fuse-envelope/foreign-pad contact was found. The F-to-J copper gaps have about **0.494 mm** margin to the 4.5 mm engineering ceiling. A native top render was visually inspected and shows the four 0° fuses above and four 180° fuses below in their intended channel-local placements.

## Thermal judgment and limits

Relative to the supplied old-hash native comparison, each land changed from 1.125 x 3.40 mm (3.825 mm²) to 1.78 x 3.15 mm (5.607 mm²), a **46.6% pad-area increase**, while pitch increased from 4.275 to 5.23 mm and each footprint moved 0.85 mm outward. The larger solder/copper contact can conduct more heat into the board and therefore can alter PPTC hold/trip behavior and reset time; the Littelfuse curves do not qualify this board-specific copper, airflow, ambient, repeated-trip history, or assembly process. The clean source-land and clearance result therefore leaves physical thermal/fault and assembly qualification owed. No existing fault test is claimed.

## Scope

This review accepts only the supplied regenerated diagnostic board's F1..F8 source land/pin/local-clearance evidence. It does not accept any absent mechanism, global placement, routing, catalog allocation, model registration, canonical source change, or release.
