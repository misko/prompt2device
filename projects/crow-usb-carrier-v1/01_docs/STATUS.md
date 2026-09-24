# Project status

<!-- pause-state:09155bf4c4193c9be4156affb69af00a6854bd7ed37d78ac42a8ee248d63e3c2 -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: P1 remains unaccepted. On the pinned QSPI-gap board, all 13 QSPI endpoints are declared, and an independently reviewed four-net JTAG packet now validates the unchanged fixed header pose, four segmented native access chains, four XU handoffs, eight P2 obligations and the full 59-net denominator. Its standalone declaration is INCOMPLETE; the whole schema-2 packet still FAILS at the nonlocal U_XU.38 reset witness. Reset has five endpoints across three owners and no saved native copper. The crystal window includes only 3 of 7 pads and both XU crystal witnesses cross the QSPI owner. Filled In1.Cu return, effective routing, DRC and P2 remain open. J_USB edge region/outline is unresolved pending connector FULL. Native DRC is nonzero with 499 unconnected items and USB has six unqualified sub-0.410-mm launch widths. Connector FULL has 19 physical unknowns; TMUX filled/capped process acceptance is external. No P1/P2/P3/route/release or order is accepted.
- Next command: `Source-model the five-endpoint, three-owner XU_RESET_N branch without treating it as a point-to-point JTAG lane; remove the legacy nonlocal witness while retaining the exact 59-net denominator. Repair oscillator region/handoffs so all seven XTAL pads and QSPI owner boundaries are respected. Re-run the whole native P1 packet, then prove P2 pad access, effective clearance, and filled In1.Cu return. Resolve J_USB edge/outline after connector FULL; connector FULL gates P3/routing and TMUX process acceptance gates release. Do not promote scratch copper.`

## Bound receipts

- `01_docs/research/2026-09-24-jtag-fixed-access-blocker-sol.md` — `8ccc15c9c587`
- `01_docs/research/2026-09-24-jtag-fixed-access-rectangle-obstruction-terra.md` — `a85ea3ef537b`
- `01_docs/research/2026-09-24-jtag-native-dogleg-physical-feasibility-terra.md` — `6a931bc0c1c7`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
- `01_docs/research/2026-09-24-segmented-fixed-access-checker-sol.md` — `18c9cbdb0fce`
- `01_docs/research/2026-09-24-usb-edge-endpoint-handoff-terra/README.md` — `b5b81e83b3f9`
- `01_docs/research/2026-09-24-usb-edge-endpoint-source-model-terra.md` — `583ed72ceb5b`
- `01_docs/research/2026-09-24-usb-esd-east-region-trial-sol.md` — `4de0ec64fbff`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic-summary.json` — `394b0d89ade9`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic.md` — `42949404b4a3`
- `01_docs/research/2026-09-24-usb-launch-em-input-inventory-terra.md` — `0bdd918292b9`
- `01_docs/research/2026-09-24-xmos-service-remaining-net-blocker-terra.md` — `edb09dcaab6a`
- `01_docs/research/2026-09-24-xu-reset-five-terminal-branch-terra.md` — `3af94c20e590`
- `01_docs/research/2026-09-24-xu-service-reservation-contract-recommendation-terra.md` — `5de4aa58c71b`
- `01_docs/research/jtag_fixed_access_probe_sol.json` — `5f73551e562d`
- `01_docs/research/jtag_native_dogleg_probe_terra.json` — `8a526c09a13f`
- `01_docs/research/jtag_segmented_packet/README.md` — `69f5922ec931`
- `01_docs/research/jtag_segmented_packet/result.json` — `ecbbdbaba018`
- `01_docs/research/xu_service_variant/QSPI_GAP.md` — `6945f823ba36`
- `01_docs/research/xu_service_variant/REGENERATION.md` — `1e05986d34c7`
- `01_docs/research/xu_service_variant/XTAL_WINDOW_NATIVE_AUDIT.md` — `7ebc5a430185`
- `01_docs/research/xu_service_variant/jtag_gap_trial/FIXED_CONNECTOR_ACCESS.md` — `7317ee60c6fb`
- `01_docs/research/xu_service_variant/jtag_gap_trial/trial_receipt.json` — `ec31176866f4`
- `01_docs/research/xu_service_variant/p1_integration_corridor_schema.md` — `9992b673c7d2`
- `01_docs/research/xu_service_variant/p1_qspi_packet/README.md` — `aac745bb6a38`
- `01_docs/research/xu_service_variant/p1_qspi_packet/evaluation.json` — `3ba0a91f8e3a`
- `01_docs/research/xu_service_variant/xtal_window_native_audit.json` — `00f8087d59a7`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
