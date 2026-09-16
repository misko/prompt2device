review_kind: bounded-critical-path-policy
reviewer: Codex /root/pod_r3_layout_review
context: FRESH
verdict: SOUND
order_verdict: DO-NOT-ORDER
board_candidate_sha256: c31674e1824c7a4a8e6d02a638c9bb15a480031ee1efa90a63aa0734e38a24f5
proposed_config_sha256: 006cf4787882d3bdfb19e4b6c6566a80e42bfdcdc05620c46671bdb87a433130
completed_at: 2026-09-14T04:41:00Z

# R13.2 to TP6.1 maximum-length review

## Verdict

SOUND as a bounded design-rule correction: raising the R13.2-to-TP6.1 F.Cu maximum from 5.0 mm to 9.0 mm is technically acceptable and is not an electrical gate bypass. No placement change is required. The source should replace the generic `why: AUDIO- probe branch` with the actual reviewed basis so that the new number is not mistaken for an unexplained candidate-fitting relaxation.

This review accepts only the 9.0 mm bound for this post-clamp probe branch. It does not accept the routed board, its remaining dangling-copper warnings, release readiness, or an order.

## Electrical role

R13 is the 100 ohm series source resistor on the negative active-balanced output. R13.2, TP6.1, U3.5 and J1.4 are on AUDIO_N. TP6 is a bare 1.5 mm test pad with no fitted load. The critical-path prefix separately requires J1.4 to reach the U3.5 ESD clamp before either TP6.1 or R13.2. The candidate preserves that prefix, so increasing the R13-to-TP6 probe-branch limit does not lengthen or bypass the connector-to-clamp path.

The project declares AUDIO_P/AUDIO_N as low-impedance audio outputs, not controlled-impedance nets, with no delay target. The exact system fixture is a 15 m cable with 1.353 nF conductor-to-conductor capacitance and a calculated 588 kHz source/cable pole from the two 100 ohm series resistors. An 8.781 mm PCB branch is less than 0.06% of the cable length. Its 3.831 mm length excess over the 4.950 mm AUDIO_P probe branch is too small to create a material audio-band delay, copper-resistance, or capacitive imbalance relative to the 100 ohm sources, resistor tolerance, and 15 m cable. Cable stability, CMRR and EMC remain first-article measurements; the 9 mm rule does not claim those tests complete.

## Geometry and alternatives

The current R13.2-to-TP6.1 pad-centre separation is only 3.500022 mm. The longer realized length is a clearance-driven detour around the independently routed PRE_OUT region, not distance caused by arbitrary remote testpoint placement. The fresh checker rerun measures 8.781118 mm, entirely on F.Cu with zero vias, leaving 0.218882 mm below a 9.0 mm ceiling. It also confirms the connector-side U3.5 prefix remains dominant before both TP6.1 and R13.2.

The attempted direct 3.3 mm path is not an admissible alternative: the v8 native DRC records an AUDIO_N/PRE_OUT track crossing and two associated clearance failures, including 0.0317 mm and 0.0483 mm actual clearances against the 0.1500 mm requirement. The attempted TP6 relocation to (59.7, 37.1) mm is also inadmissible because the placement producer finds fixed-courtyard overlaps with both R12 and R13. Those failures support retaining the accepted placement and the clean detour.

The v9 DRC has zero unconnected items and no clearance or tracks-crossing finding. Its 44 library-configuration warnings, three pre-existing dangling audio vias and one PRE_OUT dangling-track warning are separate post-route cleanup obligations. They neither justify nor invalidate this length-bound decision.

## Gate provenance

Repository history shows the 5.0 mm values for TP5 and TP6 were introduced together with the terse labels `AUDIO+ probe branch` and `AUDIO- probe branch`. No component requirement, signal-integrity calculation, cable requirement, or ADR in the inspected project derives a 5.0 mm maximum. It is therefore a conservative routing heuristic, not a source-authoritative electrical ceiling. Correcting that heuristic after a native-clean route proves 5 mm unnecessarily restrictive is legitimate when independently reviewed and recorded.

The recommended source wording is equivalent to:

`why: post-clamp low-impedance AUDIO- probe branch; 9 mm admits the shortest native-clean F.Cu detour around PRE_OUT at the accepted placement; no via or delay target; exact-cable CMRR/EMC remains first-article scope`

The layer must remain F.Cu, the branch must remain via-free, the clamp-first prefix must continue to pass, and the normal native DRC/post-route gates must remain unchanged. Under those conditions, 9.0 mm is a meaningful narrow ceiling rather than an open-ended waiver.
