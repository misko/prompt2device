# Project status

<!-- pause-state:bb59a516a147e2373c0eef32ef5df23312d5fd4a27b79f825e48cc525ef267eb -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: The distinct P1 root remains unaccepted. On the isolated QSPI-gap board, all 13 exact QSPI handoffs validate, but the whole 59-net schema-2 screen is FAIL: legacy U_XU.51 is an oversized nonlocal JTAG witness and its allocation aborts. A pinned one-part U_USB_ESD east-move trial places all seven USB support courtyards in a disjoint region and leaves an open JTAG strip, but fixed J_USB remains an unmodeled edge endpoint and XU_RESET_N has a third digital_power owner. Native DRC remains nonzero with 499 unconnected items; the USB launch has six sub-0.410-mm width violations without qualified impedance. Connector FULL has 19 physical unknowns and TMUX filled/capped process acceptance remains external. No P1/P2/P3/route/release or order result is accepted.
- Next command: `Source-model a disjoint JTAG corridor for the four two-party JTAG nets, an explicit fixed J_USB edge/support handoff, and a separate XU_RESET_N digital-power branch; measure exact native faces, pad access and return without weakening 59-net coverage. Independently admit a fresh P1 packet after the remaining internal allocations are resolved. Keep connector FULL before P3/routing and TMUX process acceptance before release; do not promote scratch USB copper.`

## Bound receipts

- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
- `01_docs/research/2026-09-24-usb-edge-endpoint-source-model-terra.md` — `583ed72ceb5b`
- `01_docs/research/2026-09-24-usb-esd-east-region-trial-sol.md` — `4de0ec64fbff`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic-summary.json` — `394b0d89ade9`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic.md` — `42949404b4a3`
- `01_docs/research/2026-09-24-usb-launch-em-input-inventory-terra.md` — `0bdd918292b9`
- `01_docs/research/2026-09-24-xmos-service-remaining-net-blocker-terra.md` — `edb09dcaab6a`
- `01_docs/research/2026-09-24-xu-service-reservation-contract-recommendation-terra.md` — `5de4aa58c71b`
- `01_docs/research/xu_service_variant/QSPI_GAP.md` — `6945f823ba36`
- `01_docs/research/xu_service_variant/REGENERATION.md` — `1e05986d34c7`
- `01_docs/research/xu_service_variant/p1_integration_corridor_schema.md` — `9992b673c7d2`
- `01_docs/research/xu_service_variant/p1_qspi_packet/README.md` — `aac745bb6a38`
- `01_docs/research/xu_service_variant/p1_qspi_packet/evaluation.json` — `3ba0a91f8e3a`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
