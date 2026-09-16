review_stage: pre-route
review_kind: layout
reviewer: Codex /root/rj45_pod_layout_s1m1
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
design_rules_sha256: 474e5d0a81baf576aefac32e9c60bce37704bb138961c16bf92573843b6409c4
prepared_board_sha256: fad0f345909d3169bd2e371896b6b0491c4c981f98725303b5aa3fad9c292a81
completed_at: 2026-09-14T03:43:22.631738+00:00

# Fresh independent pod pre-route layout review

## Verdict

SOUND for pre-route placement. The exact 60 x 40 mm native board has 44 footprints and 113 pads. Its population census is 31 fitted SMD, all on F.Cu; one manually fitted THT RJ45 (J1); one off-board microphone represented by the MK1 wire landing; seven bare test pads; and four bare mounting holes. No footprint is on B.Cu. The placement is physically legal and provides a credible route field. This verdict does not accept the prepared board as a global route.

The exact packet DRC contains 0 violations, 58 expected unconnected-item findings, and 0 schematic-parity findings. The retained raw JSON preserves every exact finding and both endpoint nodes. Independent placement grading found a tightest pad-to-outline margin of 2.26 mm at J1.9, a minimum reported courtyard gap of at least 0.100 mm at R1/R9, no courtyard/body or foreign-pad collision, and a worst cut demand of 6 nets against capacity for 121 tracks. No pad/edge, hole, drill, courtyard, keepout, or body-placement defect is present in the exact DRC and placement evidence.

## Placement and source-owned copper

The connector/clamp cell is correctly ordered for later routing. J1.5 to U3.3 measures 8.4347 mm pad-centre and the prepared F.Cu path is 8.749831 mm, within its 8.6 mm placement and 9.0 mm prepared-path budgets. J1.4 to U3.5 measures 5.5382 mm pad-centre and the F.Cu path is 6.967676 mm, within 5.7 mm and 7.5 mm budgets. Both connector-to-clamp prefixes are via-free. U3.4 has a 0.85 mm F.Cu launch to the dedicated GND via at (47.2875, 33.4) mm. The subsequent AUDIO_P/AUDIO_N vias occur after U3, so they do not defeat connector-first clamping.

All eleven preparation-applicable short paths pass independently. D1.1 to D2.1 is 9.5 mm on F.Cu against 12.0 mm. U2 input, output, NR, and feed-forward partners all pass their 3.0 mm limits: U2.8-C1.1 2.532719 mm, U2.8-C2.1 2.225031 mm, U2.1-C5.1 2.180166 mm, U2.1-C6.1 1.552265 mm, U2.6-C4.1 1.870167 mm, U2.2-C3.2 1.553713 mm, and U2.1-C3.1 1.353338 mm. U1.4-C10.1 is 1.945 mm against 3.0 mm. The prepared board uses 92 track segments and 12 vias: widths are 30 x 0.26 mm, 4 x 0.40 mm, 46 x 0.50 mm, and 12 x 0.60 mm; all meet or exceed the declared 0.25/0.40/0.50 mm class floors (0.26 mm realizes the 0.25 mm signal floor). Vias are 0.60/0.30 mm.

The full post-route critical-path launch intentionally does not pass on r0: its first raw failure is `endpoint R12.2 does not touch this net's copper` at R12.2 (57.9125, 36.0) mm. R12/TP5 and R13/TP6 downstream branches remain part of the expected 58-open pre-route state. This is a routing-stage obligation, not a placement defect and not a waiver. The route owner must close it, rerun the unfiltered checker, and obtain native DRC closure before promotion.

## Physical and manufacturing limits

The inspected exact top render is consistent with the census and with the board coordinates. The inspected bottom render shows no bottom SMD population. The exact J1 orientation receipt binds this board hash, reports a north-edge mating axis with 0.5 mm mating-plane edge offset and no failures, and the model-registration aggregate passes for J1 and U2. Connector orientation approval is treated only as P-ORIENT evidence.

The PCB remains FIRST-ARTICLE-ONLY / DO-NOT-ORDER. Enclosure fit, plug access, cable strain and bend radius, manual J1 soldering, MK1 wire strain relief/polarity, rail noise, gain, clipping, cable/EMC behavior, and roof-environment behavior require first-article checks. These unresolved physical qualifications do not change the pre-route placement verdict.

## Findings

| ID | severity | exact locus | finding | next owner |
|---|---|---|---|---|
| PREP-OPEN-001 | INFO / expected pre-route | 58 exact node pairs in `exact-pre-route-drc.json`; first is TP3.1 (24.0,47.0) to C6.1 (32.48,47.0) on 5V_QUIET | Global copper is incomplete by design at this gate. | Route owner: complete routing and close every native open without bypass. |
| PREP-PATH-001 | INFO / routing obligation | R12.2 (57.9125,36.0), AUDIO_P; related R13.2 (62.9125,36.0), AUDIO_N | The unfiltered post-route path audit cannot yet reach downstream probe/output branches from the connector/clamp prefixes. | Route owner: connect branches after U3, rerun exact unfiltered critical-path audit. |
| FA-PHYSICAL-001 | INFO / first article | J1 north edge, MK1 landing at (73.0,42.5), assembled pod | Cord/enclosure/service geometry and environmental/electrical behavior have no physical first article in this evidence. | First-article owner: execute the governed qualification plan before ordering production. |

No ERROR or WARN placement finding was identified.

## Methods and evidence

I verified the frozen packet before analysis; loaded working copies of the exact native and prepared boards with `/usr/bin/python3 -B` and pcbnew; independently enumerated footprints, pads, sides, coordinates, track/via widths, and declared path distances; ran the placement/routability compositor and placement policy audit against the frozen project; ran the critical-path checker on the actual r0 with a review-only preparation-applicable projection; deliberately ran the unfiltered current path contract to expose its first unresolved downstream endpoint; inspected exact top and bottom images; and reviewed the orientation/model-registration receipts. All direct subprocesses were finite and retained runtime/log evidence. The evidence archive contains the raw measurements, exact DRC node pairs, inspected image copies, configurations, and runtimes.

Limitations: I did not route, regenerate checkpoints, modify board bytes, qualify the enclosure or cable physically, or claim production readiness. The isolated native DRC rerun additionally reported seven `lib_footprint_issues` warnings because the scratch KiCad configuration does not enable the packet-local footprint nickname; these environment-only warnings are preserved and are not substituted for the packet's exact 0-violation DRC.
