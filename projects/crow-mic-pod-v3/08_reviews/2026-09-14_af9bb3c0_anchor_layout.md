review_stage: pre-route
review_kind: layout
reviewer: Codex /root/pod_r3_layout_review anchor-final
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
parts_sha256: d0d0026dd67cbfaa98176799ea34ea3bfde384675d74d58d8cf8f0c88e41fd89
design_rules_sha256: 8224767829768bcdb9193037489f6ae931c60cb4b0e25c1e1744ff1e2198512d
prepared_board_sha256: 491f29e59de9c1b0a76107eb3452c8460847e481974e2b114b36a5e1f15a5c65
route_yaml_sha256: 1ee39bb6c0d935c0409e9f203cad666f5c0dfe3de4645b628467af0d7e516102
completed_at: 2026-09-14T04:55:36.942529+00:00

# Fresh pod anchor-restoration pre-route layout review

## Verdict

SOUND for the exact regenerated placement, prepared board and routing source. The three audio routing-anchor vias are restored as explicit off-pad transitions, the unused PRE_OUT stub remains absent, and the previously accepted short R13-to-TP6 canonical geometry is again the authored target. `via_janitor` runs immediately after exact chain canonicalization and removes only vias that have same-net copper on fewer than two layers. The T-junction splitter is now centerline/tolerance limited, leaving cap-overlap correction solely to exact source declarations.

This review admits the placement and routing source at the pre-route boundary. It does not assert that the next stochastic route will realize the source, accept post-route copper, waive any DRC row, mint a release, or authorize an order.

## Bound subject

The placement board is SHA-256 `af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938`; the normalized electrical netlist is `b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff`; and the complete part-record digest is `d0d0026dd67cbfaa98176799ea34ea3bfde384675d74d58d8cf8f0c88e41fd89`. The current semantic design-rule digest is `8224767829768bcdb9193037489f6ae931c60cb4b0e25c1e1744ff1e2198512d`. It binds route source `1ee39bb6c0d935c0409e9f203cad666f5c0dfe3de4645b628467af0d7e516102` and prepared board `491f29e59de9c1b0a76107eb3452c8460847e481974e2b114b36a5e1f15a5c65`.

The reviewed post-dispatch stitch implementation is `f7101cc07c322a16e6b04b5f5784895be970ad7c39f30110fe4f481dd2d9429b`. This is the current image with `split_t_junctions` restricted to `centerline distance <= tol`; no earlier wider copper-cap interpretation is relied upon.

## Placement and assembly side

All 31 fitted SMD footprints are on F.Cu and none is on B.Cu. All 44 native footprints retain their accepted positions and orientations. Fresh top and bottom renders confirm component-side assembly, unobstructed J1 mating access, clear mounting holes and probe access, and a bottom side containing only through-hole lands and mounting holes. The board identity, RJ45 pin legend, NOT ETHERNET / NOT POE warning, power/probe labels, balanced-audio polarity and MK1 landing polarity remain readable.

## Restored routing anchors

The prepared board contains 14 vias. Five are intentional pre-route anchors whose B.Cu consumption remains a routing obligation:

- AUDIO_P at (49.6, 34.25) mm is 0.8875 mm from U3.3 centre. With the 0.675 x 0.350 mm source pad and 0.600 mm via, its pad-copper-to-annulus gap is 0.250 mm. Native clearance to the nearest foreign F.Cu shape is 0.371817 mm and to foreign B.Cu is 1.863299 mm.
- AUDIO_N at (47.288, 36.25) mm is 1.000000 mm from U3.5 centre, giving a 0.525 mm pad-to-annulus gap. Native foreign clearance is 1.099815 mm on F.Cu and 2.250 mm on B.Cu.
- AUDIO_N at (62.913, 34.7) mm is 1.300000 mm from R13.2 centre, giving a 0.300 mm pad-to-annulus gap. Native foreign clearance is 1.229176 mm on F.Cu and 4.693351 mm on B.Cu.
- OUTP_DRV at (55.0, 36.0) mm retains its reviewed 0.260 mm R12.1 dogbone. Its segment/via foreign F.Cu clearances are 1.183/2.100 mm.
- MIC_BIAS at (66.0, 39.0) mm retains its reviewed 0.500 mm R3.2 dogbone. Its segment/via foreign F.Cu clearances are 1.062/2.100 mm.

Every via is 0.600/0.300 mm, meeting the standard fabrication tier, and every quoted clearance exceeds the 0.150 mm rule. None is via-in-pad. The unused PRE_OUT segment from (55.025, 52.81) to (53.5, 52.81) mm is absent.

## Prepared-board DRC

A fresh KiCad 10.0.4 all-severity DRC with zone refill and schematic parity on a hash-identical copy of r0 reports zero clearance, short, drill, width or parity findings. It contains 33 expected pre-route unconnected items and 52 warnings:

- 44 environment-only footprint-library lookup warnings;
- five `via_dangling` warnings exactly at the five intentional audio/power routing anchors listed above;
- three ordinary source-launch `track_dangling` warnings on MIC_AC, OUTP_FB and VREF.

Those opens are not waived. The next route must consume them or the cleanup and post-route gates must reject/remove them according to their declared contracts.

## Canonical geometry and TP6

The canonicalization contains four exact F.Cu edits on AUDIO_P, AUDIO_N, OUTP_DRV and MIC_BIAS, replacing 20 uniquely identified net/layer/width/endpoint segments with seven exact segments. The AUDIO_N declaration is the previously demonstrated local geometry: it collapses the (60.1/60.2) micro-zigzag into the vertical (60.2, 35.2) to (60.2, 36.8) segment and gives the R13 contact an exact endpoint at (62.913, 34.7). This is the source family that realized the native-clean 8.781118 mm R13.2-to-TP6.1 F.Cu path, below the independently justified 9.0 mm ceiling.

The canonicalizer remains fail-closed: each old segment must match uniquely by net, layer, width and exact unordered endpoints with no replacement present, or the already-applied replacement must be wholly present with no old geometry. Partial, duplicate or stale candidates abort. No proximity search can transfer these edits to a different stochastic result.

## Cleanup contract

`via_janitor` is explicitly pass 1, immediately after pass 0 `canonicalize_chains` and before deduplication or later stitch additions. For each via it gathers same-net attachments by copper overlap on each layer, same-net pads, and declared same-net zone layers. A via with fewer than two served layers is removed as a nonfunctional hole; a via with a real layer transition is retained. This criterion is appropriate for the three restored audio anchors because AUDIO_P/AUDIO_N have no zones: only actual same-net track/pad copper can give them a second served layer. R12/MIC anchors likewise survive only if routing consumes their transition. Any zone-outline over-credit on other nets remains visible to the independent filled-copper/native post-route gate and is not waived here.

The revised `split_t_junctions` now skips exact track endpoints, vias and pad anchors, and splits only an unrepresented same-net endpoint whose perpendicular centreline distance is within the configured 0.05 mm tolerance. It no longer adds half the track width. Therefore a mere copper-cap overlap cannot be recast as a graph vertex; the exact canonicalization list must own such candidate-specific corrections. This directly addresses the method defect exposed by v14.

## Routability and limits

The restored-anchor source and short AUDIO_N canonical family previously demonstrated complete native connectivity, physical clearance and 22/22 critical-path/prefix satisfaction before the later experimental top-edge subject regressed to 65.548811 mm. The v14 subject and verdict are not reused or restamped here. The current source explicitly returns to the short geometry and adds the cleanup ordering needed for its restored transition vias.

Normal routing must now prove the exact current stochastic output, followed by canonicalization, janitor cleanup, T-junction splitting, generated rules last, zero non-library DRC violations, zero unconnected items, zero parity issues, and 22/22 critical-path acceptance. This pre-route review does not predict those results.

FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.
