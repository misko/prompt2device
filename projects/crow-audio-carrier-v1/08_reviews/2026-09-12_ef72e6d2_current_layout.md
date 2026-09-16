subject: crow-audio-carrier-v1 exact current-board pre-route layout review
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_owned_layout_review
context-given: FRESH; immutable 1,111-input exact-current placement packet; accepted current pin/render reports; prior layout and exhausted LAYOUT-001 history; READ_ONLY subject
source_commit: b9d77ca73ac2b7eff4111e07bd8a8a0d6376d22e
review_stage: pre-route
review_kind: layout
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
design_rules_sha256: 53529b7c990d7a8313be7515483aaff9d5b92f2bf8f4b8b34c4153b39aac9b23
actual_board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
owning_design_rules_sha256: 53529b7c990d7a8313be7515483aaff9d5b92f2bf8f4b8b34c4153b39aac9b23
task_identity: task_id=owned-layout-review; run_id=owned-layout-review; input_handoff_id=owned-layout-review; stage_id=KICAD-PLACEMENT
envelope_sha256: eb72acf72165ee945b60fdabad9367683f9bc58ae2857cb3baea23809991a021
reviewer_id: /root/carrier_owned_layout_review
reviewer_provenance: independent judgment; FRESH context; no child agents; read-only exact-current placement review; current native geometry independently extracted under bounded runtime
context_mode: FRESH
raw_subject_sha256: fef0025a5d604c0e6d17601c660ac01289029b729c741aceeb7e5ab22d86b6d0
semantic_subject_sha256: c3f38165feffeb412de647e5ada1d8b75cd629c15cdf51ede9360486e2c6a66f
completed_at: 2026-09-12T06:32:59Z
actualcompleted_at: 2026-09-12T06:32:59Z
assembled_coverage: 333/333
functional_group_denominator: 24
functional_net_denominator: 48
functional_endpoint_denominator: 192
functional_path_denominator: 144
north_group_denominator: 4
north_net_denominator: 8
north_pad_denominator: 32
north_path_denominator: 24
blocking_finding_ids: []
layout_finding: LAYOUT-001
layout_finding_state: RESOLVED
layout_finding_class: corrected_upstream_channel_association_restores_ordered_ordinary_route_placement
layout_diagnostic_budget: 3/3 spent
layout_diagnostic_pending: 0
layout_diagnostic_campaign_state: REASSESS
diagnostic_geometry_saved: 0
diagnostic_credit_restored: false

# Independent exact-current pre-route layout review

The exact current carrier placement is **SOUND for ordinary routing**. The accepted ADR0027 association removes the specific north-channel order reversal that created LAYOUT-001, while preserving P/N polarity. Current native pad geometry leaves simultaneous launch and transition room for all eight north nets and access to the two continuous inner reference-plane roles. LAYOUT-001 is therefore resolved at the placement boundary. This judgment does not claim routed copper, filled-plane continuity, realized matching, DRC cleanliness, analog performance, fabrication readiness, or permission to order; the order verdict remains **DO-NOT-ORDER**.

## Method and complete coverage

I independently hash-bound and loaded a verified scratch copy of `project/04_kicad/crow_audio_carrier_v1.kicad_pcb` under bounded `pipeline_runtime.run_stage`. Native enumeration found 340 footprints: 333/333 assembled components plus H1–H4 and FID1–FID3; 1,002 pad objects; 81 zones; eleven existing via/track objects and no routed signal segments. I inspected the exact-current native full-top render, populated twin plan, locator plan view, and a newly derived exact native pad/bounding-box plan. The accepted pin report independently covers 333/333 assembled references and all 1,002 physical pad objects; the accepted render report covers 333/333 bodies and 25/25 locator pages. Receipts and earlier reports were used as corroboration, not as a substitute for the current native geometry.

Coverage includes the complete source contract of 24 P/N groups, 48 nets, 192 endpoints and 144 declared paths, including all 4 north groups, 8 north nets, 32 north pads and 24 north paths. The retained per-section spread ceiling is 1.0 mm, the router length-match tolerance is 0.5 mm, and every stated 5 mm keep-short obligation remains downstream-verifiable on saved copper.

## Functional placement judgment

- West input/protection: J9, F_IN, Q_IN, D_QIN_GS, D_IN, D_BUCK_IN, hold-up parts and their corrected control/resistor network retain a clear west-to-east flow. J9's intended body overhang leaves its copper in-board. The exact placement compositor reports zero envelope overlaps, zero foreign-pad intrusions, and no screw-head/edge placement conflict.
- Buck, hold and LT3041 LDO: U_BUCK.5 to L_BUCK.1 is 2.677500 mm and U_BUCK.6 to C_BUCK_BST.1 is 2.134551 mm. U_LDO input pins 1/2/3 to C_LDO_IN.1 are 3.249712/3.729695/4.214336 mm; output pins 12/13/14 to C_LDO_OUT.1 are 2.075000/2.134391/2.303394 mm. Hot-loop, bootstrap, feedback, Kelvin and quiet-return satellites are placed within their source budgets with separation from the switch node. Routed loop area, Kelvin copper, DCR and thermal behavior remain owed.
- ADC, EP, reference and bypass: every U_ADC pad, the exposed-pad field, supply/configuration launches, VMID/reference parts, common-mode shunts and local ground structures were covered. The 0.4 mm ADC north row supports eight 0.20 mm traces at the ordinary 0.20 mm clearance exactly between adjacent pads. Each launch has at least 1.0607 mm measured edge clearance to the nearest foreign pad, allowing the one-millimetre F.Cu spread already declared in source before any 0.50/0.20 mm via transition. F.Cu and B.Cu are eligible signal layers; In1.Cu and In2.Cu are declared continuous reference-plane roles. Final copper and filled zones must prove actual return continuity.
- Eight analog/protection paths: J1–J8, U_ESD1–U_ESD8, F1–F8, coupling parts, U_AFE1–U_AFE8, U_ISO1–U_ISO8, output/filter/common-mode/bias branches and all ADC endpoints preserve the repeated connector-to-ADC progression. The source checker contract covers all 24 matched groups / 48 nets / 192 endpoints / 144 paths. All eight ESD devices retain the accepted shunt topology and local return access.
- Clock, reset, TDM, bypass and service geometry: J10/J11, U_CLK, reset/supervisor/transistor cells, U_TDM_SCH, U_TDM, U_OE and their satellites have open launch areas and retained keep-short placements. J1–J11 remain accessible in their approved edge orientations; the tightest reported pad-to-outline margin is 1.32 mm at J10.11 against a 0.15 mm minimum. Installed mating, cable bend/strain relief and service handling remain first-article matters.

## LAYOUT-001 — RESOLVED at placement; diagnostic budget remains exhausted

The earlier board presented north source bundles in one lateral order and their ADC destinations in the reverse order, producing 24 cross-channel inversions. ADR0027 changed the logical-to-physical association to pods 1–8 = ADC physical channels 4,3,2,1,5,6,7,8. On this exact native board, north bias endpoints now appear left-to-right as ADC1P/N, ADC2P/N, ADC3P/N and ADC4P/N at source x ranges 38.26–42.74, 70.26–74.74, 102.26–106.74 and 134.26–138.74 mm. Their ADC row appears in that same bundle and polarity order at x=93.8, 94.2, 94.6, 95.0, 96.2, 96.6, 97.0 and 97.4 mm on pins 48,47,46,45,42,41,40,39. The projected cross-channel and within-pair inversion counts are both zero.

The order-preserving association is sufficient for planar monotone fan-in on F.Cu: no north pair must cross another before its ADC pad, all eight pad exits fit simultaneously at 0.20/0.20 mm, and the measured foreign-pad clearance permits spreading before a legal via. The placement compositor's worst global cut has demand 15 nets versus capacity 258 tracks over the two eligible signal layers. These facts establish placement suitability for ordinary routing without relying on a synthetic or saved route candidate. They do not establish the route itself.

All three historical LAYOUT-001 diagnostics remain spent: two invalid custom A-star models and the owning configuration-root setup stop produced zero saved geometry. There are 3/3 attempts spent, zero pending reservations, and campaign state REASSESS. No fourth diagnostic, alternate ledger, route probe, or candidate generation was performed or requested. The accepted upstream association and this fresh native placement judgment resolve the original placement concern; ordinary routing may proceed only through the existing owning route generation and saved-board gates.

## Remaining gates and limits

Every later route must be judged from its exact saved-board hash. It must close all 24 groups / 48 nets / 192 endpoints / 144 paths, including the north 4 / 8 / 32 / 24 subset; prove the 1.0 mm per-section spread and 0.5 mm router matching tolerance; recheck every 5 mm keep-short constraint; show legal 0.50/0.20 mm vias and allowed layers; pass fresh native DRC/parity; and prove filled quiet-reference continuity, Kelvin realization, DCR/current/thermal budgets, and absence of stubs or detours.

The capped native value of 499 unrouted items is not a complete connection census and was not used as one. ADR0007 still defers 21 physical unknowns out of 42 entries; those are physical qualification items, not electrical placement defects. The three diode/model uploader and polarity-order holds (`D_BUCK_IN`, `D_HOLD`, `D_QIN_GS`), installed connector/cable/enclosure checks, analog capture/performance and first-article fault/thermal tests remain outside this layout verdict and keep the order verdict at DO-NOT-ORDER.
