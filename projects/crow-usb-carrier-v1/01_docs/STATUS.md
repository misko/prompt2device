# Project status

<!-- pause-state:7ffb40a64ef3aa675dc0bce0b93aef0a8abe37533c186e66628c8d3b3c18016a -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: P1/P2/P3 and release remain unaccepted. Rebased source now declares disjoint QSPI and XTAL handoffs, fixed JTAG access, and a five-terminal unresolved reset branch. The full P1 checker is INCOMPLETE with no global errors; USB J_USB.4 still crosses its source region, and connector edge geometry extends 0.55 mm beyond the board outline. The oscillator r2 scratch poses intersect the required empty handoff, so no candidate copper or placement was promoted. Four oscillator GND terminals, filled return, crystal performance, six USB launch widths, connector FULL physical facts, and TMUX external process acceptance remain open.
- Next command: `Resolve the USB fixed-connector edge owner and support-cell geometry from exact public physical evidence; keep FULL-dependent claims pending. Regenerate a source-owned P1 candidate and review all 59 crossings. Then perform a bounded source-generated P2 oscillator placement entirely inside clock_flash_debug, prove the three oscillator signal nets, four local GND egress paths, continuous filled In1 return, clearance and silk before any P3 or release claim.`

## Bound receipts

- `01_docs/findings.yaml` — `bd12196e2892`
- `01_docs/research/2026-09-24-jtag-fixed-access-blocker-sol.md` — `8ccc15c9c587`
- `01_docs/research/2026-09-24-jtag-fixed-access-rectangle-obstruction-terra.md` — `a85ea3ef537b`
- `01_docs/research/2026-09-24-jtag-native-dogleg-physical-feasibility-terra.md` — `6a931bc0c1c7`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
- `01_docs/research/2026-09-24-segmented-fixed-access-checker-sol.md` — `18c9cbdb0fce`
- `01_docs/research/2026-09-24-usb-edge-endpoint-handoff-terra/README.md` — `b5b81e83b3f9`
- `01_docs/research/2026-09-24-usb-edge-endpoint-source-model-terra.md` — `583ed72ceb5b`
- `01_docs/research/2026-09-24-usb-edge-source-current-diagnosis-sol.md` — `b7b079ac74cc`
- `01_docs/research/2026-09-24-usb-esd-east-region-trial-sol.md` — `4de0ec64fbff`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic-summary.json` — `394b0d89ade9`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic.md` — `42949404b4a3`
- `01_docs/research/2026-09-24-usb-launch-em-input-inventory-terra.md` — `0bdd918292b9`
- `01_docs/research/2026-09-24-xmos-service-remaining-net-blocker-terra.md` — `edb09dcaab6a`
- `01_docs/research/2026-09-24-xu-reset-five-terminal-branch-terra.md` — `3af94c20e590`
- `01_docs/research/2026-09-24-xu-reset-region-repair-terra/native_region_audit.json` — `797a732f23ab`
- `01_docs/research/2026-09-24-xu-service-reservation-contract-recommendation-terra.md` — `5de4aa58c71b`
- `01_docs/research/candidate_loop_xtal/r1_result.json` — `45ad819f30b4`
- `01_docs/research/candidate_loop_xtal/r2_result.json` — `68a9121c2916`
- `01_docs/research/candidate_loop_xtal/xtal_r2_return_terra.json` — `c5f17a4310f2`
- `01_docs/research/candidate_loop_xtal/xtal_r2_signal_audit.json` — `b80ffd3d3265`
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
- `01_docs/research/xu_service_variant/p1_xtal_jtag_packet/validation.json` — `30d6a45b8432`
- `01_docs/research/xu_service_variant/p1_xtal_packet/validation.json` — `df3aa871ff10`
- `01_docs/research/xu_service_variant/xtal_south_cap_handoff.json` — `3dc3510d8a9f`
- `01_docs/research/xu_service_variant/xtal_window_native_audit.json` — `00f8087d59a7`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `03_src/floorplan.yaml` — `aa20999d5100`
- `03_src/modular_plan.json` — `75c3a517cea5`
- `03_src/rules/p1_corridor_requirements.yaml` — `f65ba88b0bb9`
- `08_reviews/2026-09-24_xtal-source-corridor_terra_review.md` — `56b26c0afa2e`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
