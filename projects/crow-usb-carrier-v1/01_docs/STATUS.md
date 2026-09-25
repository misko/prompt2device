# Project status

<!-- pause-state:b3e6d4386d4d672943059f054b6408756e57503b3d92cdfc076304eac60f5011 -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: P1 remains unaccepted. The pinned QSPI-gap board has a reviewed four-net segmented JTAG declaration with all eight handoffs and the full 59-net source denominator. A separate unresolved XU_RESET_N declaration now binds all five exact native pads across three owners without geometry or capacity credit; its physical blocker inventory records two digital_power pads inside audio_clock_tdm. The whole schema-2 packet advances past reset and FAILS at nonlocal U_XU.34 on XTAL. A native 0.15/0.15 XTAL dogleg candidate preserves C_XU_VDDIO_35 and shifts the QSPI owner/face east, but source-region split, P2 copper/return and oscillator electrical proof are not admitted. Native DRC remains nonzero with 499 unconnected items and six unqualified sub-0.410-mm USB launch widths. J_USB edge region/outline awaits connector FULL (19 physical unknowns); TMUX filled/capped process acceptance remains external. No P1/P2/P3/route/release or order result is accepted.
- Next command: `Build and independently validate an isolated seven-endpoint XTAL handoff packet with the retained C_XU_VDDIO_35 pose, disjoint west/east XMOS cells, a source-owned oscillator transition, and QSPI face shifted to x=219.2; keep the full 59-net denominator. Repair the two reset source-region overlaps before P1 admission. Then regenerate native board, prove P2 pad access, effective clearance and filled In1.Cu return, and rerun all P1 allocations. Connector FULL gates P3/routing; TMUX process acceptance gates release. Do not promote scratch copper.`

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
- `01_docs/research/reset_branch_packet/README.md` — `e066b2e53b08`
- `01_docs/research/reset_branch_packet/result.json` — `d44bc4e77662`
- `01_docs/research/xu_service_variant/C_XU_VDDIO35_POSE_SEARCH.md` — `cdd8da6631e8`
- `01_docs/research/xu_service_variant/QSPI_GAP.md` — `6945f823ba36`
- `01_docs/research/xu_service_variant/REGENERATION.md` — `1e05986d34c7`
- `01_docs/research/xu_service_variant/XTAL_REGION_HANDOFF_SEARCH.md` — `25fadedf39be`
- `01_docs/research/xu_service_variant/XTAL_SOUTH_CAP_HANDOFF.md` — `2caf261007ee`
- `01_docs/research/xu_service_variant/XTAL_WINDOW_NATIVE_AUDIT.md` — `7ebc5a430185`
- `01_docs/research/xu_service_variant/jtag_gap_trial/FIXED_CONNECTOR_ACCESS.md` — `7317ee60c6fb`
- `01_docs/research/xu_service_variant/jtag_gap_trial/trial_receipt.json` — `ec31176866f4`
- `01_docs/research/xu_service_variant/p1_integration_corridor_schema.md` — `9992b673c7d2`
- `01_docs/research/xu_service_variant/p1_qspi_packet/README.md` — `aac745bb6a38`
- `01_docs/research/xu_service_variant/p1_qspi_packet/evaluation.json` — `3ba0a91f8e3a`
- `01_docs/research/xu_service_variant/xtal_south_cap_handoff.json` — `3dc3510d8a9f`
- `01_docs/research/xu_service_variant/xtal_window_native_audit.json` — `00f8087d59a7`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
