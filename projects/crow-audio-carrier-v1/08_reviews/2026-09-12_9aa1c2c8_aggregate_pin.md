# Pre-route pin review — unchanged PCB pin scope after Cat harness revision

review_stage: pre-route
review_kind: pin
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: 9aa1c2c821a31129176a8b519b9a211d78dfc011adb997a64470c03d0726891f
parts_sha256: e2f7a9284d65bc07a61f336c1d3eb7e0eb381b9efaca2e90e52ca91e6c1c7eb0
design_rules_sha256: 0637fdb2d3f5ab247c301147ad6ed875343674c225e5036a2bb1935bd025cec3
source_commit: 4793527e8645e2e58dd3061bb2eb64b591e69ccb
reviewer: root aggregation of preserved independent pin judgments with exact native scope transfer
context-given: prior fresh manufacturer-derived pin groups and corrections; complete native and dossier equivalence; no new full pin-review claim
completed_at: 2026-09-12T00:59:33.949144+00:00
date: 2026-09-12

All333 assembled references retain their prior independently established pin judgments. The previous exact aggregation is [2026-09-11_9aa1c2c8_aggregate_pin.md](2026-09-11_9aa1c2c8_aggregate_pin.md), SHA256 775f26c79fcde976ed82a51c13fb7537d9eb7567445c457f1b48a2f3041eb225, on board9aa1c2c821a31129176a8b519b9a211d78dfc011adb997a64470c03d0726891f. Its original fresh manufacturer-derived groups, Littelfuse/Diodes/Yageo corrections and physical limits remain binding.

Root loaded both saved native boards and compared complete keyed records for340 footprints/1002 physical pad objects: every footprint origin, angle, layer, value, FPID, assembly attribute; every pad number, position, size, net, angle, shape, corner radius, drill, type, layer set and mask/paste override. Zero records differ. This is exact equality, not counts alone. Proof and generating command are retained as06_build/pre_route/cat_pin_transfer.json and in the new evidence bundle.

Every one of the84 previous part.yaml files is byte-identical. The only three additions are221-415,7939A and8503, each explicitly none_off_board, with no matching current PCB component. Thus the parts digest changes without changing any fitted part's manufacturer pin authority. The independently accepted Cat schematic delta additionally proves333components/937memberships/220partitions/42NC unchanged; witness SHA2566a43038cab9545b2d92775c6f8cf1f6bdaf131d5a181974c673b9641857ea166. The independently reviewed new harness contract retains Micro-Fit cavities1=+12V,2=GND,3=AUDIO+,4=AUDIO−.

The new cable, parallel conductor joins and single-wire power pigtails remain physical harness work. No fabricated crimp, installed polarity/continuity/keying, service-space, shield, hot-loop, analog, fault or thermal qualification is inferred. SOURCE admission and the separate repaired harness review do not replace first-article measurement. Existing human orientation approval remains separately bound. This record supplies only the inherited physical-pin lens; fresh render/layout, route, fabrication and release acceptance remain owed. DO-NOT-ORDER remains.
