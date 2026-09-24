# Project status

<!-- pause-state:a34372a264ecfe5b21c9a64bea524ae39c54056bb587f68b632a34340f4fcf50 -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: The distinct P1 root remains unaccepted. The isolated XU/clock rectangle and QSPI integration-gap regenerations preserve 569 refs, 1,872 pad identities and all 27 fixed poses, but the gap has no schema-2 owned handoff, measured pad access, return, or 59-net corridor proof. The regenerated board retains 225 native clearance violations and 499 unconnected items; the scratch USB pair requires six sub-0.410-mm neck segments that violate the canonical USB_HS width rule and have no qualified impedance model. Connector FULL has 19 physical unknowns, TMUX filled/capped process acceptance is external, and no P2/P3/route/release or order result is accepted.
- Next command: `Finish and independently review the fail-closed integration-corridor handoff checker, then bind the QSPI gap to exact source ownership and P2 pad/return obligations in an isolated packet. Reassess the remaining P1 allocations before any fresh one-attempt native admission; do not promote scratch USB copper or bypass connector FULL.`

## Bound receipts

- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic-summary.json` — `394b0d89ade9`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic.md` — `42949404b4a3`
- `01_docs/research/2026-09-24-usb-launch-em-input-inventory-terra.md` — `0bdd918292b9`
- `01_docs/research/2026-09-24-xu-service-reservation-contract-recommendation-terra.md` — `5de4aa58c71b`
- `01_docs/research/xu_service_variant/QSPI_GAP.md` — `6945f823ba36`
- `01_docs/research/xu_service_variant/REGENERATION.md` — `1e05986d34c7`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
