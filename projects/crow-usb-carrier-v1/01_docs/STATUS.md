# Project status

<!-- pause-state:b4b8ffe748a1645af70701b28dbb17a3e60cc5ea360cfb5352025f3edde60854 -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`917a45414c65`)
- Blocker: The distinct P1 root remains unaccepted. The isolated XU/clock and QSPI gap regenerations preserve 569 refs, 1,872 pad identities and all 27 fixed poses; the generic schema-2 checker now recognizes an integration corridor but Crow has no exact source handoff, P2 pad access/return, or 59-net corridor proof. The regenerated board retains 225 native clearance violations and 499 unconnected items. The scratch USB pair has six sub-0.410-mm neck segments that violate the canonical USB_HS width rule and lack a qualified impedance model. Connector FULL has 19 physical unknowns, TMUX filled/capped process acceptance is external, and no P2/P3/route/release or order result is accepted.
- Next command: `Bind the isolated QSPI gap to exact Crow source ownership, handoffs and P2 pad/return obligations using the reviewed integration-corridor schema; independently review that packet and reassess all remaining P1 allocations before any fresh one-attempt native admission. Do not promote scratch USB copper or bypass connector FULL.`

## Bound receipts

- `01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/SHA256SUMS` — `fc465fc54773`
- `01_docs/research/2026-09-24-p1-native-evidence-failure-owner-reassessment.md` — `15ccef4423ee`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic-summary.json` — `394b0d89ade9`
- `01_docs/research/2026-09-24-usb-fcu-launch-diagnostic.md` — `42949404b4a3`
- `01_docs/research/2026-09-24-usb-launch-em-input-inventory-terra.md` — `0bdd918292b9`
- `01_docs/research/2026-09-24-xu-service-reservation-contract-recommendation-terra.md` — `5de4aa58c71b`
- `01_docs/research/xu_service_variant/QSPI_GAP.md` — `6945f823ba36`
- `01_docs/research/xu_service_variant/REGENERATION.md` — `1e05986d34c7`
- `01_docs/research/xu_service_variant/p1_integration_corridor_schema.md` — `9992b673c7d2`
- `03_src/diagnostics/usb_fcu_launch_probe.py` — `7a05b24297f6`
- `08_reviews/pre-route_schematic_render.md` — `05ff9b639b7f`
- `08_reviews/pre-route_topology.md` — `76dbfea927e5`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
