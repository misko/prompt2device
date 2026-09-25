# Project status

<!-- pause-state:9896617e997ea678514d368a445b7d54876bbb90b9377739d201886f992c4215 -->

- Phase: `prototype-layout-diagnostic`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`15288355fcc7`)
- Blocker: Static USB endpoint screen: canonical 0.410-mm centered launches leave 0.145-mm Type-C and 0.070-mm XU foreign clearance against 0.150 required. Historical D15 0.180/0.100 pair clearance is XU-area-only. Full path, return, P1/P2, connector FULL and prototype-only ESD qualification remain open; 499 opens are inherited from the frozen unrouted board.
- Next command: `Prepare one unadopted same-placement 3313A USB pair-domain source proposal: 0.180-mm width, intended DP/DN-only 0.100-mm clearance, foreign clearance 0.150 mm unchanged. Review complete connector/ESD/XU domain and transition model before any new native experiment; retain D18 P1/P2 prerequisites. Do not replay D15/D17, adopt a stack, route, fabricate or order from this static screen. Use the new read-only pair-footprint command before full placement and review any scoped-rule INCOMPLETE; it grants no route or stage admission.`

## Bound receipts

- `01_docs/BRIEF.md` — `d58ce4e0f783`
- `01_docs/decisions/0012-initial-public-stock-lock.md` — `acffa297e45c`
- `01_docs/decisions/0013-usb-esd-prototype-boundary.md` — `ed83de26a0c3`
- `01_docs/decisions/0018-evidence-scheduling-and-private-design-work.md` — `3844ed14d92b`
- `01_docs/findings.yaml` — `27cbf04b140a`
- `01_docs/journal/placement.md` — `fcb1fa2dc644`
- `01_docs/research/2026-09-24-public-stock-569/public-stock.json` — `aa9491bf6df4`
- `01_docs/research/2026-09-25-early-pair-preflight/expanded_locked.json` — `00dba81709ab`
- `01_docs/research/2026-09-25-early-pair-preflight/historical_d15.json` — `dd3264b35baa`
- `01_docs/research/2026-09-25-early-pair-preflight/replay.json` — `a78a74a4f228`
- `01_docs/research/2026-09-25-ti-prototype-p-prec-isolated-check-sol.md` — `980eebc12250`
- `01_docs/research/2026-09-25-ti-prototype-source-schematic-checks-terra.md` — `153cc44ff650`
- `01_docs/research/2026-09-25-ti-unrouted-diagnostic-board-sol.md` — `f84f08170719`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/README.md` — `c1d467cbba92`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/measure.py` — `967b9c3efb9e`
- `08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md` — `48f056d1aa96`
- `08_reviews/2026-09-25_usb-complete-path-feasibility_terra.md` — `54278b66a7e4`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
