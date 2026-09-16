review_stage: pre-route
review_kind: layout
reviewer: Codex /root/pod_r12_layout_review
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
design_rules_sha256: eea86c5464dfd8e042080fd26b91999228eb3c41ff1aff8b7e3b0521c41ac795
prepared_board_sha256: 13600b88c64eed8c4d040f9c8f43e26927f3973191fd855df5100495c37a308a
completed_at: 2026-09-14T04:03:40.108722+00:00

# Fresh independent R12 seed layout review

## Verdict

SOUND for the exact deterministic OUTP_DRV pre-route seed. The current board placement is unchanged, and the prepared board adds one 0.26 mm F.Cu segment from R12.1 toward a 0.60/0.30 mm through-via at (55.0, 36.0) mm. The seed has no hard clearance, short, drill, pad-overlap, side-policy, or readability defect. This verdict admits the seed as pre-route geometry; it does not accept a completed route or production order.

## Exact measurements

R12.1 is a 1.025 x 1.400 mm F.Cu round-rect pad centered at (56.0875, 36.0) mm. The realized segment begins at (56.087, 36.0), only 0.0005 mm from pad center, and runs to the via center at (55.0, 36.0). Its centerline remains inside R12.1 for 0.512 mm to the pad's left edge, so pad-to-track contact is positive and unambiguous.

The via annulus is intentionally off-pad. R12.1 copper to via-annulus edge is 0.275 mm; R12.1 copper to drill edge is 0.425 mm. The 0.15 mm annulus exactly meets the declared minimum. The same-net 0.26 mm segment bridges the pad-to-via gap.

Using KiCad native effective shapes over every foreign pad, track and via, the nearest foreign F.Cu clearance from the seed segment is 1.183 mm to R12.2/AUDIO_P, giving 1.033 mm margin over the declared 0.15 mm clearance. The seed via's nearest foreign F.Cu clearance is 2.100 mm to the same pad, giving 1.950 mm margin. On B.Cu its nearest foreign copper primitive is 5.076486 mm away. The via is 16.0 mm from the nearest board edge.

A fresh all-severity KiCad DRC of the exact prepared board returned zero hard physical clearance/short/drill findings and zero schematic-parity findings. It reports one expected seed-specific via_dangling warning because the through-via currently has copper only on F.Cu; consuming that anchor is a routing obligation. The board remains pre-route with 53 unconnected-item rows. The other DRC warnings are 44 local-library-configuration rows, four existing dangling-track rows, and four other prepared dangling vias.

## Side policy and readability

All 44 footprints remain on F.Cu and none is on B.Cu. The new component-side copper is F.Cu; the through-via necessarily has annuli on both copper layers and does not create bottom-side assembly. No footprint, reference, value, caption, courtyard, or connector datum moved, so the accepted placement and readability geometry is unchanged.

## Evidence and limits

measurements.json binds the exact current board, normalized netlist, current semantic design-rule digest, route source, checker, prepared board, geometry, native clearances and DRC classification. r0-current-drc.json is a fresh direct KiCad report against that prepared-board hash.

The downstream router must connect the B.Cu side of the anchor and ultimately close every unconnected item under the normal post-route gate. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.
