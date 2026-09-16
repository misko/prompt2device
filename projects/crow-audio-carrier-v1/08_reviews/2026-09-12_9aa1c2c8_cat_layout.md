subject: crow-audio-carrier-v1 exact current-board pre-route layout review
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_cat_layout_review
context-given: release-archive-only
source_commit: 4793527e8645e2e58dd3061bb2eb64b591e69ccb
review_stage: pre-route
review_kind: layout
design_verdict: INCOMPLETE
order_verdict: DO-NOT-ORDER
board_sha256: 9aa1c2c821a31129176a8b519b9a211d78dfc011adb997a64470c03d0726891f
design_rules_sha256: 0637fdb2d3f5ab247c301147ad6ed875343674c225e5036a2bb1935bd025cec3
source_parts: 87 hash-bound part.yaml dossiers; combined manifest SHA-256 85777e1060b81ee2e49dffaf7a48c43fec1d0b06ccf4853b8058b11bec09a2d7
task_identity: task_id=cat-layout-review; run_id=cat-layout-review; input_handoff_id=cat-layout-review; stage_id=KICAD-PLACEMENT
envelope_sha256: c803bdb4b8e2e2d55f39533cc4a086ce78a239e86f995fc43eeec09cae69a686
reviewer_id: /root/carrier_cat_layout_review
reviewer_provenance: independent
context_mode: FRESH
raw_subject_sha256: 751660046216f17d21968bd1ceb4f306f48556844e3eafab92564cd6bcaf0cfe
semantic_subject_sha256: 82636f3aa7f2fcd0de80058570ecde0ad75bd49f17823499bc1ff102b7bcf29d
completed_at_utc: 2026-09-12T01:05:39.716127Z
original_layout_report_sha256: b3bed69157aa3aeb1e57996ff94485c40fb8e7f5751026dae972edd5f25da115
layout_binding_correction_sha256: 37df93c152a6e8f4104ef4f8bfff352e164a124769af35adbe9774c2aece73f4
consolidation_reviewer: Codex independent judgment agent /root/carrier_cat_review_consolidation
consolidation_scope: provenance serialization and physical-census wording only; no new layout inspection
physical_census_exact_source: 11
physical_census_conservative_source: 10
physical_census_unknown: 21
physical_census_total: 42
blocking_finding_ids: ["LAYOUT-001"]
layout_finding: LAYOUT-001
layout_finding_state: OPEN
layout_finding_class: missing_simultaneous_corridor_evidence
diagnostic_request: bounded_saved_board_route_probe_or_simultaneous_corridor_reservation
diagnostic_nets: ADC1P,ADC1N,ADC2P,ADC2N,ADC3P,ADC3N,ADC4P,ADC4N
diagnostic_pad_denominator: 32
diagnostic_path_denominator: 24
diagnostic_pn_groups: ANALOG_CH1_ADC,ANALOG_CH2_ADC,ANALOG_CH3_ADC,ANALOG_CH4_ADC
diagnostic_max_spread_mm: 1.0
diagnostic_layers: F.Cu,B.Cu
diagnostic_track_width_mm: 0.20
diagnostic_clearance_mm: 0.20
diagnostic_via_mm: 0.50/0.20
diagnostic_reference_plane_proof: REQUIRED
diagnostic_promotion: FORBIDDEN

# Independent exact-board pre-route layout review

The exact Cat board is locally disciplined and physically legal, but one placement-stage question remains unproved: the four north analog channel pairs reverse order before the ADC and no simultaneous two-layer corridor is reserved or realized. That is a missing-evidence finding, not a demonstrated impossible route or a proven electrical defect. The design verdict is therefore INCOMPLETE and the order verdict remains DO-NOT-ORDER.

## Methodology and provenance

I independently bound and opened the immutable `project/04_kicad/crow_audio_carrier_v1.kicad_pcb`, recomputed its SHA-256, and recomputed the semantic design-rule SHA-256 with the supplied canonical `pre_route_review_check.design_rules_digest(project)` function. I enumerated board geometry with pcbnew under bounded `pipeline_runtime.run_stage`. I inspected newly generated KiCad top and bottom 3D renders, a KiCad F.Cu/F.Silkscreen/F.Courtyard/Edge.Cuts plan, the supplied native locator, and a net-labelled ADC-pad detail derived from pcbnew geometry. The render resolved 333/333 assembled models. I treated the carried render proof, prior layout report and placement receipt as hypotheses and corroboration, not as geometry proof.

The board contains 340 footprints: 333 assembled components plus four mounting holes and three fiducials; 1,002 pads; 220 nonempty nets; and 81 zones. It has eleven vias, all existing local/thermal structures, and zero signal track segments. The capped 499-unconnected native report was not used as a route census. No route, route candidate, KRT invocation, corridor reservation, or manufacturing evidence was created or judged.

All 336 immutable packet inputs passed exact size and SHA-256 verification before judgment and again after evidence assembly. Raw runtime logs preserve command output, return code, timestamps and complete outer argv/cwd metadata in `evidence.json`.

## Full functional coverage

- West input/protection: J9, F_IN, Q_IN, D_QIN_GS, D_IN, D_BUCK_IN, the corrected input resistor/control network, and hold-up parts were inspected on the current board. The flow is west-to-east, copper remains in-board despite the intentional J9 body overhang, and no body/courtyard/screw-head conflict is visible.
- Buck converter: U_BUCK, C_BUCK_IN/2/3, C_BUCK_BST, L_BUCK and C_BUCK_O1/O2/O3 were inspected against the source layout obligations. U_BUCK.5 to L_BUCK.1 measures 2.677500 mm center-to-center; U_BUCK.6 to C_BUCK_BST.1 measures 2.134551 mm. The hot-loop satellites remain locally grouped and the feedback area is separated from the switch node. Routed loop area and thermal performance remain later obligations.
- LT3041 LDO: U_LDO, C_LDO_IN, C_LDO_OUT, C_OPA_BULK, C_LDO_NR4/5 and R_LDO_SET were inspected. Input pins 1/2/3 to C_LDO_IN.1 measure 3.249712/3.729695/4.214336 mm; OUTS12/OUT13/OUT14 to C_LDO_OUT.1 measure 2.075000/2.134391/2.303394 mm. Placement supports the required Kelvin split and quiet return, but only routed filled copper can prove those structures.
- ADC and fine-pitch escape: all U_ADC pad identities, its EP field, nearby supply/reference/filter/config components, sixteen analog inputs and the existing local GND vias were inspected. The 0.4 mm-pitch exits have open immediate launch space; no foreign pad or courtyard blocks their first escape. This does not discharge the simultaneous north-channel corridor finding.
- Eight analog channels: J1..J8, U_ESD1..8, F1..F8, coupling capacitors, U_AFE1..8 cells, U_ISO1..8, common-mode capacitors, pulldowns and all ADC endpoints were inspected. All eight shunt ESD topologies are source/net bound in the exact receipt, and the repeated cells preserve their intended connector-to-ADC progression. Channels 5..8 approach the south ADC side without the order reversal found on channels 1..4.
- Digital clock/reset/TDM: J10, J11, U_CLK, U_RST1/U_RST2/Q_RST1, U_TDM_SCH, U_TDM and U_OE plus their satellites were inspected. Their F.Cu launch areas are open, and no placement crossing or blocked pad escape was found.
- Connectors and mechanics: J1..J11, H1..H4 and FID1..FID3 were inspected in plan and 3D. The exact machine receipt reports 333 assembled envelopes, zero close/overlapping envelope pair, zero foreign-pad intrusion, and a tightest pad-to-outline margin of 1.32 mm at J10.11 against 0.15 mm. Connector assembly SOURCE remains PASS. The 42-entry physical-evidence census is 11 exact-source, 10 conservative-source, and 21 unknown; these source-known categories are not physical qualifications. FULL remains INCOMPLETE with 21 physical unknowns under ADR0007, which is a first-article physical-mating boundary and does not waive layout evidence.

## Measured findings

### LAYOUT-001 — BLOCKER — OPEN — missing simultaneous corridor evidence

For the north channels, source-side R_ADC_PD1P/N, R_ADC_PD2P/N, R_ADC_PD3P/N and R_ADC_PD4P/N appear left-to-right as channel bundles 1,2,3,4, spanning x=38.26 to 138.74 mm. Their U_ADC destinations appear left-to-right at x=93.8 to 97.4 mm as pads 48,47,46,45,42,41,40,39, corresponding to channel bundles 4,3,2,1. Independent endpoint projection yields 24 cross-channel inversions (28 if the four within-pair polarity inversions are also counted).

ANALOG_AUDIO is eligible on F.Cu and B.Cu. The exact placement receipt declares zero corridors, and the current board contains zero signal segments. Immediate pad escape and broad global cut capacity do not prove that all eight nets, four P/N groups and their local branches can coexist with 0.20 mm width/0.20 mm clearance, legal 0.50/0.20 mm vias, <=1.0 mm within-group spread, and continuous quiet reference planes. Earlier custom attempts produced no saved native geometry, and the synthetic/snapped-endpoint method was not qualified as board evidence.

Disposition: retain LAYOUT-001 as the sole blocking layout finding. Before routing admission, supply either an explicit simultaneous corridor/layer-transition reservation or the one bounded saved-board route probe defined in the owning metadata above. Recheck all 32 pads, 24 required paths, four P/N groups, via legality, path spread and filled reference-plane continuity. The diagnostic cannot be promoted as production routing, and canonical PR-REVIEW remains FAIL until its prerequisites and this evidence are accepted.

### LAYOUT-002 — INFO — CLOSED — local placement and escape geometry

The exact current board passed the physical placement compositor with 0 failures and 0 warnings. The measured buck/LDO distances above meet their source pin-center budgets; the repeated channel cells, ADC immediate escapes, digital launches, board-edge margins, and 0.10 mm courtyard floor show no additional placement defect. The source changes for the Cat off-board shield/cable/join dossiers do not change the 340-footprint/1,002-pad native interface, while the current fuse/FET/resistor corrections are present and were inspected in the west power region.

### LAYOUT-003 — INFO — ADR0007 FIRST ARTICLE

The 42-entry physical-evidence census is 11 exact-source, 10 conservative-source, and 21 unknown. These are source-evidence categories, not physical qualifications; the 21 unknown physical items remain governed by ADR0007. This review neither promotes those unknowns nor turns them into an electrical-layout defect.

## Limits

This pre-route review does not claim a complete route, filled quiet-reference continuity, Kelvin realization, routed DCR or matched length, thermal performance, physical mating, installed capacitor behavior, fabrication fit, manufacturing readiness or first-article behavior. Any later saved-board route must be reviewed from its own exact hash and measured independently.
