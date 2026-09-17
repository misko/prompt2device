subject: crow-audio-carrier-v1 v0.1.8-2026-09-16 exact release
review_stage: release
review_kind: redteam_layout
reviewer_identity: /root/carrier_release_layout_v018
context: FRESH-INDEPENDENT-FINAL
completed_at: 2026-09-16T17:58:00-07:00
source_commit: cc14bc442b14c412a82da708d11346a00a8a9615
design_verdict: SOUND
order_verdict: FIRST-ARTICLE-ONLY
board_sha256: 45ff675971600c279c1d1e34e1610a08426b144f8435349037919a2328987e26

# Crow carrier v0.1.8 final adversarial layout review

The exact carrier is SOUND for immutable first-article release. The authenticated replay accepts 622/622 prelayout inputs and ends LAYOUT SEALED. Native and independently extracted archive DRC both pass 0 violations / 0 unconnected / 0 parity. Route acceptance is 7 PASS / 2 N-A, analog copper is 155/155, both governed clock/TDM groups have zero vias, and via ampacity is 54/54.

All 340 footprints are on F.Cu: 306 fitted SMD placements, 27 manual THT parts, three fiducials and four mounting holes. BOM and CPL contain the same 306 unique references. Body clearance covers 333 fitted envelopes with zero overlaps and zero foreign-pad conflicts. Pad separation passes at the 0.090 mm floor; the tightest pad-to-outline margin is 2.26 mm.

All 601 vias are graded. Exactly twelve 0.60/0.30 mm sites are filled and capped: nine under U_ADC EP49, two under U_LDO EP15, and one in C_ADC_CM6P pad 2. The other 589 vias remain ordinary and unfilled. Protected and ordinary drill families are disjoint.

P0: 0. Previous stale receipts, assembly snapshot, connector approval, archive library path and sourcing checkpoint are closed. P1: supervised uploader/CAM verification remains mandatory. P2: loaded mechanical, electrical and thermal first-article tests remain owed.
