review_stage: pre-route
review_kind: layout
reviewer: Codex /root/pod_r3_layout_review final
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
design_rules_sha256: 9131add75637cc1950219d1f8d431d1338220cc81df30d5bb73f4db933a88bfb
prepared_board_sha256: 81490c84fd135efc445349d10049003e4603415c5d93696f9eabee86f502f536
completed_at: 2026-09-14T04:43:38.265470+00:00

# Fresh final pod pre-route layout review

## Verdict

SOUND for the exact current placement, semantic route source, and prepared board. The unchanged placement keeps every fitted SMD on F.Cu, retains clear assembly and probe access, and has demonstrated routability. The prepared copper is physically legal and now omits the unused PRE_OUT stub and three obsolete audio vias. The two necessary R12.1 and R3.2 dogbones remain legal. The declared post-route chain canonicalization is exact, narrow, fail-closed on stale geometry, and followed by the ordinary stitch gate. The reviewed 9.0 mm TP6 branch ceiling is technically coherent with this placement.

This is pre-route layout acceptance only. It does not accept a completed route, waive dangling copper, mint a release, or authorize an order.

## Bound subject

The placement board is SHA-256 `af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938`. The normalized electrical netlist is `b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff`. The exact semantic design-rule digest is `9131add75637cc1950219d1f8d431d1338220cc81df30d5bb73f4db933a88bfb`, including the deterministic seed geometry, the R13.2-to-TP6.1 limit and rationale, and the stitch canonicalization declaration. The exact route source is `5761d087a20ae821ff40041ebb2cd801f4f7a9fc3d3a978f8d73295655491d2a`; its prepared board is `81490c84fd135efc445349d10049003e4603415c5d93696f9eabee86f502f536`.

## Placement and assembly side

All 31 SMD footprints are on F.Cu and none is on B.Cu. All 44 native footprints, including through-hole, testpoint and board-only identities, retain F.Cu placement. Fresh top and bottom 3D renders confirm that the fitted population is accessible from the component side; the bottom view contains only through-hole lands and mounting holes. No component, connector datum, courtyard, caption, reference or value moved from the prior accepted placement.

The top render remains legible at normal board scale: board identity, NOT ETHERNET / NOT POE warning, J1 pin legend, power/protection probe labels, AUDIO+/AUDIO- labels and capsule-landing polarity are visible without a newly introduced component collision. J1 remains at the edge with its mating direction unobstructed; the four mounting holes remain clear.

## Prepared copper

The prepared board contains 81 deterministic tracks: 75 F.Cu and six B.Cu, plus 11 through-vias. Every realized minimum track width meets its declared source class. The audio and quiet-analog minima are 0.260 mm against 0.250 mm floors, MIC_BIAS is 0.500 mm against its 0.400 mm floor, and the protected-input trunks are 0.500 mm.

The source cleanup is present exactly. The unused PRE_OUT segment from (55.025, 52.81) to (53.5, 52.81) mm is absent. The obsolete AUDIO_P via at (49.6, 34.25), AUDIO_N via at (47.2875, 36.25), and AUDIO_N via at (62.913, 34.7) mm are absent from r0. Their adjacent F.Cu launch tracks remain intentionally available for the router to consume, so removing the vias does not change pin/net identity.

The required escape anchors remain present:

- R12.1/OUTP_DRV uses a 0.260 mm F.Cu segment from the pad centre toward a 0.600/0.300 mm via at (55.0, 36.0) mm. The pad-to-annulus gap is 0.275 mm, bridged by the same-net segment. Native effective-shape clearance is 1.183 mm from the segment and 2.100 mm from the via to the nearest foreign F.Cu copper; the via has 5.507372 mm to foreign B.Cu and 15.650 mm to Edge.Cuts.
- R3.2/MIC_BIAS uses a 0.500 mm F.Cu segment toward a 0.600/0.300 mm via at (66.0, 39.0) mm. It has the same 0.275 mm pad-to-annulus gap and positive same-net bridge. Native clearance is 1.062 mm from the segment and 2.100 mm from the via to the nearest foreign F.Cu copper; the via has 5.671067 mm to foreign B.Cu and 13.650 mm to Edge.Cuts.

Both source segments begin 0.0005 mm from their exact pad centres due only to KiCad coordinate quantization, leaving 0.512 mm of centerline inside each source pad. Both via annuli are outside their pads and meet the standard 0.600/0.300 mm fabrication tier.

## Fresh prepared-board DRC

A fresh KiCad 10.0.4 all-severity DRC with zone refill and schematic parity on a hash-identical copy of r0 reports zero clearance, short, drill, width or parity findings. It contains 33 unconnected items, as expected before routing, and 52 warning-level violations:

- 44 environment-only footprint-library lookup warnings;
- six source-launch `track_dangling` warnings on MIC_AC, AUDIO_P, two AUDIO_N endpoints, OUTP_FB and VREF;
- two `via_dangling` warnings exactly at the reviewed OUTP_DRV and MIC_BIAS escape anchors.

The obsolete prepared vias and PRE_OUT stub generate no warning because they are absent. All remaining opens are downstream routing obligations; none is waived here.

## TP6 detour and routability

R13.2 and TP6.1 are only 3.500022 mm apart by pad centre, but PRE_OUT occupies the direct F.Cu corridor. The rejected direct route crossed PRE_OUT and produced 0.0317 mm and 0.0483 mm clearances against the 0.1500 mm rule. Moving TP6 to (59.7, 37.1) mm was also correctly rejected by pinned-courtyard overlaps with R12 and R13.

The reviewed alternative is an 8.781118 mm F.Cu, zero-via detour beneath the 9.0 mm ceiling. TP6 is an unloaded test pad on low-impedance AUDIO_N after the 100 ohm source resistor; the connector-to-U3 clamp-first prefix remains separately enforced. This board-scale detour is immaterial beside the exact 15 m cable and has no controlled-impedance or delay target. The source rationale correctly retains exact-cable CMRR/EMC as first-article scope. A fresh checker rerun against the v9 candidate passes all 22 critical-path and prefix obligations.

## Canonicalization scope

The stitch declaration contains four exact edits on AUDIO_P, AUDIO_N, OUTP_DRV and MIC_BIAS. All are F.Cu and use 0.260 mm for the audio nets or 0.500 mm for MIC_BIAS, meeting their net floors. In total it replaces 20 exact router segments with seven segments that collapse overlapping, cap-only, sub-width or misregistered microchains onto shared vertices.

The consumer identifies every old segment by net, layer, width and exact unordered endpoints. It accepts only a unique complete old set with no replacement present, or an already complete replacement with no old geometry. A missing, duplicated or partial subject aborts as stale. It performs no nearest-neighbour search and cannot silently apply these coordinates to a different router result. The normal downstream stitch gate remains in the pass sequence.

The v9 native evidence confirms the declared geometry yields zero unconnected items and no clearance or tracks-crossing finding; the realized critical-path checker passes 22/22. Its three dangling audio vias and one PRE_OUT dangling track remain explicit downstream cleanup rather than acceptance evidence. This layout verdict therefore admits the canonicalization mechanism and exact geometry while leaving completed-route cleanliness to the owning post-route gates.

## Evidence and limits

`measurements-base.json` records independent native-shape measurements, hashes, the assembly-side census and DRC classification. `source-audit.json` records the prepared-copper inventory, removed/required identities, and canonicalization schema census. `r0-drc-parity.json` is direct KiCad output. Fresh top and bottom renders bind the visual inspection. The separate bounded 9.0 mm decision is preserved at `/tmp/pod-r13-tp6-length-review/report.md` and is consistent with this full review.

FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.
