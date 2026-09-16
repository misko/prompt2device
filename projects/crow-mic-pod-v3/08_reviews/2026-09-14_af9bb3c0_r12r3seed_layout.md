review_stage: pre-route
review_kind: layout
reviewer: Codex /root/pod_r3_layout_review
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
design_rules_sha256: d5b3fb88a0300059a60a2e2874514f34957702cf2bb334acd78c221a1611c5b3
prepared_board_sha256: 2c7bd6ac83c538be78e3f1413e60c7eba4be33a9369ff7a525ec280218a374e7
completed_at: 2026-09-14T04:11:50.125311+00:00

# Fresh independent deterministic-exit layout review

## Verdict

SOUND for the exact prepared pre-route board and the combined deterministic R12.1/OUTP_DRV and R3.2/MIC_BIAS exits. Both seeds make positive same-net pad contact, put their via annuli outside their source pads, satisfy the declared width and fabrication floors, and leave ample native effective-shape clearance to foreign copper and the board edge. No footprint or assembly side changed. This verdict admits only the prepared source geometry; it does not accept a completed route, release, or order.

## Bound artifacts

The current placement board is SHA-256 `af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938`. The normalized electrical netlist is `b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff`; its raw export hash is intentionally not used because the checker removes export-time and source-path churn. The semantic design-rule digest is `d5b3fb88a0300059a60a2e2874514f34957702cf2bb334acd78c221a1611c5b3`. The exact route source is `bec9d821cccb3c7e431010700b1185d807eb7a5bbb99ac9179f072cad43f20a3`, and its prepared `r0.kicad_pcb` is `2c7bd6ac83c538be78e3f1413e60c7eba4be33a9369ff7a525ec280218a374e7`.

## R12.1 / OUTP_DRV

R12.1 is a 1.025 x 1.400 mm F.Cu round-rect pad centered at (56.0875, 36.0) mm. The realized 0.260 mm F.Cu segment starts at (56.087, 36.0) mm, 0.0005 mm from pad center, and ends at the 0.600/0.300 mm through-via at (55.0, 36.0) mm. Its centerline remains within the source pad for 0.512 mm, establishing positive contact.

The pad-copper to via-annulus gap is 0.275 mm and the pad-copper to drill gap is 0.425 mm. The same-net segment bridges the copper gap; the via is outside the pad rather than via-in-pad. KiCad native effective shapes measure 1.183 mm from the segment to the nearest foreign F.Cu copper, R12.2/AUDIO_P, and 2.100 mm from the via annulus to the same limiter. On B.Cu, the nearest foreign copper is an AUDIO_P via at 5.076486 mm. The via annulus has 15.650 mm to the nearest Edge.Cuts shape.

The 0.260 mm width exceeds the BALANCED_AUDIO 0.250 mm source floor. The 0.600/0.300 mm via exactly meets the declared `jlc_2layer_default` minimum diameter and drill, with a 0.150 mm annulus.

## R3.2 / MIC_BIAS

R3.2 is a 1.025 x 1.400 mm F.Cu round-rect pad centered at (64.9125, 39.0) mm. The realized 0.500 mm F.Cu segment starts at (64.912, 39.0) mm, 0.0005 mm from pad center, and ends at the 0.600/0.300 mm through-via at (66.0, 39.0) mm. Its centerline remains within the source pad for 0.512 mm, again establishing positive contact.

The pad-copper to via-annulus gap is 0.275 mm and the pad-copper to drill gap is 0.425 mm. The same-net segment bridges that gap, so this is an ordinary off-pad dogbone. Native effective shapes measure 1.062 mm from the segment to the nearest foreign F.Cu copper, R3.1/5V_QUIET, and 2.100 mm from the via annulus to that limiter. The nearest foreign B.Cu copper is an AUDIO_N via at 4.693351 mm. The new via is also comfortably separated from the nearby R4/C8/R5 region; R4 is the nearest footprint origin at 3.041 mm, while R4 is same-net MIC_BIAS copper and does not create a clearance conflict. The via annulus has 13.650 mm to the nearest Edge.Cuts shape.

The 0.500 mm width exceeds the QUIET_POWER 0.400 mm source floor. Its via exactly meets the same standard-tier 0.600/0.300 mm fabrication floor and retains a 0.150 mm annulus.

## Assembly side and readability

All 31 SMD footprints are on F.Cu and none is on B.Cu. All 44 footprints, including board-only and through-hole items, retain F.Cu placement. The new tracks are on F.Cu; the through-vias necessarily span both copper layers and do not add bottom-side assembly. The source change adds copper only, so no footprint, courtyard, connector datum, reference, value, or caption moved. The already accepted component-side readability geometry therefore remains unchanged.

## Fresh DRC classification

A fresh KiCad 10.0.4 all-severity DRC with zone refill and schematic parity against a hash-identical temporary copy of the prepared board returned code 0, zero schematic-parity findings, and zero clearance, short, drill, or track-width findings. It reports 53 warning-level violations and 33 unconnected items because this artifact is intentionally pre-route:

- 44 `lib_footprint_issues`: each says the current CLI configuration lacks the named footprint library; these are environment/library-lookup warnings and do not identify a physical geometry defect.
- 4 existing `track_dangling` warnings.
- 5 `via_dangling` warnings. Two are exactly the reviewed source anchors at (55.0, 36.0) and (66.0, 39.0) mm; the other three are existing prepared routing anchors.

The two reviewed via warnings are expected at this stage because their F.Cu dogbones exist before the stochastic route consumes the B.Cu endpoints. They remain downstream routing obligations. A completed route must eliminate every unconnected item and pass the normal post-route DRC; this review does not waive any item.

## Evidence and limits

`measurements.json` contains the independently computed artifact digests, native geometry distances, footprint-side census, and DRC classification. `r0-current-drc-parity.json` is the direct KiCad report, and `measure.py` records the independent native-shape measurement method. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.
