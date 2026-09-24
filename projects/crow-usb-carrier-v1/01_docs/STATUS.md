# Project status

<!-- pause-state:f17e02f640e587d7b75ed22a4f7c43ea480c1e98ac20c99f2b7cb79fd7d90919 -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: P1 remains unaccepted. All 13 QSPI handoffs validate on the isolated QSPI-gap board, but the full 59-net schema-2 packet FAILS. The four-net JTAG strip has raw space and four XU handoffs validate. Generic fixed-connector access is now fail-closed, yet the current single-rectangle contract cannot admit all four J_JTAG pads: TMS/TCK/TDO rectangles hit intervening header pads; TDI has a pad-clear side-contact candidate with only 0.02 mm raw gap and no clearance/return proof. U_XU.38 reset remains a nonlocal witness; its five endpoints span three owners with no saved copper. The crystal window includes only 3 of 7 pads, and XU crystal witnesses cross the QSPI owner. J_USB edge region/outline is unresolved pending connector FULL. Native DRC is nonzero with 499 unconnected items; USB has six unqualified sub-0.410-mm launch widths. Connector FULL has 19 physical unknowns and TMUX filled/capped process acceptance is external. No P1/P2/P3/route/release or order result is accepted.
- Next command: `Design a source-owned segmented/waypoint J_JTAG access contract or re-evaluate fixed connector placement; prove all four simultaneous native pad escapes, effective clearance and In1.Cu return without weakening the 59-net denominator. Model the separate five-endpoint XU_RESET_N branch and revise oscillator handoffs without crossing the QSPI owner. Resolve J_USB edge/outline after connector FULL, then rerun P1/P2. Connector FULL gates P3/routing; TMUX process acceptance gates release. Do not promote scratch USB copper.`

## Bound receipts

- `01_docs/research/2026-09-24-jtag-fixed-access-blocker-sol.md` — `8ccc15c9c587`
- `01_docs/research/2026-09-24-jtag-fixed-access-rectangle-obstruction-terra.md` — `a85ea3ef537b`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
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
