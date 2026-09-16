review_stage: pre-route
review_kind: pin
reviewer: /root/pod_r3_pin_review fresh independent read-only reviewer
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
netlist_sha256: b4edc879929e85fb35953e06f24ca6f8ade42b14d777b7751cbda47bc84aadff
parts_sha256: d0d0026dd67cbfaa98176799ea34ea3bfde384675d74d58d8cf8f0c88e41fd89
design_rules_sha256: 9131add75637cc1950219d1f8d431d1338220cc81df30d5bb73f4db933a88bfb
route_yaml_sha256: 5761d087a20ae821ff40041ebb2cd801f4f7a9fc3d3a978f8d73295655491d2a
r0_sha256: 81490c84fd135efc445349d10049003e4603415c5d93696f9eabee86f502f536
completed_at: 2026-09-14T04:44:13Z

# Pod final pre-route pin and source review

## Verdict

SOUND for the exact pre-route pin, source-escape, connector, and population scope. I independently rebuilt the board/pad census and rule hashes from the live artifacts. The current prepared board preserves all 44 placement-board footprints, values, library identities, pad numbers and nets, positions, orientations, and mounted sides. The route-policy changes since the prior placement review do not alter a pin, pad, component, netlist node, footprint, or mounted side.

This verdict accepts the exact current source geometry and rules for continued routing. It does not accept a completed route, the post-route canonicalized result, fabrication outputs, physical qualification, release readiness, or ordering.

## Exact source geometry

| Source | Native pad identity | Prepared source geometry | Governing floor | Result |
|---|---|---|---|---|
| R12.1 | OUTP_DRV; R12=100 ohm; center (56.0875,36.0) mm; 1.025 x 1.4 mm pad | 0.26 mm F.Cu segment to a 0.60/0.30 mm via at (55.0,36.0) | BALANCED_AUDIO minimum 0.25 mm | PASS |
| R3.2 | MIC_BIAS; R3=3.9 kohm; center (64.9125,39.0) mm; 1.025 x 1.4 mm pad | 0.50 mm F.Cu segment to a 0.60/0.30 mm via at (66.0,39.0) | QUIET_POWER minimum 0.40 mm | PASS |

Each via annulus begins 0.275 mm beyond its source-pad copper edge and the declared segment bridges that space continuously. The nearest other pad copper is 2.10 mm away for each via. An independent census finds no prepared via center inside any pad bounding box. Exact r0 now contains 81 segments and 11 vias. The deleted AUDIO_P, AUDIO_N, and R13 audio vias are absent; the two source-escape vias remain present. The removed PRE_OUT seed changes no pad identity.

Native DRC on exact r0 reports no clearance, width, crossing, via-in-pad, courtyard, or mask finding. Its 52 reported pre-route warnings are exactly 44 local footprint-library warnings, six dangling-track warnings, and two dangling-via warnings; 33 unconnected items remain because r0 is a prepared, incompletely routed board. Schematic parity could not be fetched from this intermediate r0 and is not claimed here.

## Pin, connector, and topology census

The generated netlist passes 39/39 authored electrical invariants. Protection/topology ADR coverage is 3/3. The net-reference audit resolves 81/82 references with zero ghost names; its sole unreached value is the explicitly advisory power-tree label QUIET_5V.

The six critical native identities are intact:

- D1 is S1M-E3/61T: pin 1 VIN_PROTECTED and pin 2 12V_FUSED.
- D2 is SMBJ15A: pin 1 VIN_PROTECTED and pin 2 GND.
- J1 is Würth 615008160221: contacts 1 through 8 are 12V_POD, GND, 12V_POD, AUDIO_N, AUDIO_P, GND, 12V_POD, GND; shell tabs 9 and 10 are POD_SHIELD.
- U1 retains all 14 OPA1679 pins, including U1.8 on OUTP_DRV.
- U2 retains eight TPS7A4901 leads plus distinct grounded PowerPAD 9; pins 3 and 7 retain separate NC/DNC nets.
- U3 retains AUDIO_P on pin 3, GND on pin 4, AUDIO_N on pin 5, and isolated NC pins 1 and 2.

The independent spoke checker realizes exactly 1/1 required pod connector with the exact MPN, footprint, and ten-pad assignment.

R13.2 and TP6.1 remain on AUDIO_N at their unchanged positions. Raising their maximum route length from 5 to 9 mm changes a narrow route-acceptance heuristic, not their electrical identity. The source preserves F.Cu and the clamp-first prefix. The independent bounded review measures the native-clean route at 8.781118 mm with zero vias and accepts the 9 mm ceiling while retaining CMRR/EMC as first-article work. Its evidence is copied into this packet.

The new canonicalize_chains step is post-route copper policy. Its four edit groups are confined to AUDIO_P, AUDIO_N, OUTP_DRV, and MIC_BIAS on F.Cu at 0.26, 0.26, 0.26, and 0.50 mm respectively. These match the governed classes and do not rewrite source pads or the netlist. Final chain correctness and native DRC remain post-route gates.

## One-sided population

The exact placement board and r0 each contain 44 footprints. All 38 footprints containing SMD pads are on F.Cu and none is on B.Cu. Seven are bare TP1 through TP7 probe lands, leaving 31 populated top-side SMT references. J1 and MK1 remain manual through-hole work; H1 through H4 remain mechanical holes. This satisfies assembly.yaml sides: [top].

The existing generated fab BOM/CPL remains outside this pre-route verdict and must be regenerated before fab/release acceptance because its D1 line still names the superseded JKSEMI part rather than the exact-board Vishay S1M-E3/61T. J1 is intentionally omitted from machine assembly as manual THT.

FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force.
