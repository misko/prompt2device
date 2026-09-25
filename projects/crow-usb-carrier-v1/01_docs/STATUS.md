# Project status

<!-- pause-state:c0459bd22505a7aa59af86c16af37d54bbfab272aab129d01c80af5141d94de0 -->

- Phase: `prototype-layout-diagnostic`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`15288355fcc7`)
- Blocker: The exact-pair 3313A rule is tested but unadopted. Frozen-board P1 remains INCOMPLETE: JTAG accesses narrow below Default width, reset geometry is unfinished, and timing pad access/allocation is unproved. Affected P2, USB complete route/return, connector FULL, prototype-only ESD, stack/order and release remain open.
- Next command: `On the frozen expanded placement, resolve source-backed JTAG/reset and timing pad access; rerun independent P1 and affected P2 checks. Then review the unadopted 3313A USB four-leaf merge/ESD/XU transition and In1.Cu return before one bounded native route experiment. Preserve D15 failed history and D18 physical/release holds; do not regenerate D15 or order.`

## Bound receipts

- `01_docs/BRIEF.md` — `d58ce4e0f783`
- `01_docs/decisions/0012-initial-public-stock-lock.md` — `acffa297e45c`
- `01_docs/decisions/0013-usb-esd-prototype-boundary.md` — `ed83de26a0c3`
- `01_docs/decisions/0018-evidence-scheduling-and-private-design-work.md` — `3844ed14d92b`
- `01_docs/findings.yaml` — `27cbf04b140a`
- `01_docs/journal/placement.md` — `7e522f50f925`
- `01_docs/research/2026-09-24-public-stock-569/public-stock.json` — `aa9491bf6df4`
- `01_docs/research/2026-09-25-early-pair-preflight/expanded_locked.json` — `00dba81709ab`
- `01_docs/research/2026-09-25-early-pair-preflight/historical_d15.json` — `dd3264b35baa`
- `01_docs/research/2026-09-25-early-pair-preflight/replay.json` — `a78a74a4f228`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/README.md` — `ad12ca96b0ae`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measure.py` — `7812eb60ee26`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measurement.json` — `93bb33a0e1ef`
- `01_docs/research/2026-09-25-ti-prototype-p-prec-isolated-check-sol.md` — `980eebc12250`
- `01_docs/research/2026-09-25-ti-prototype-source-schematic-checks-terra.md` — `153cc44ff650`
- `01_docs/research/2026-09-25-ti-unrouted-diagnostic-board-sol.md` — `f84f08170719`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/README.md` — `5dad1c08fbb1`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-20260925.json` — `ec9cfedff7b1`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-independent-terra.json` — `2ef86d1c3b69`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/replay.py` — `3b01efdf4f44`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/source_diff.patch` — `707d8b940751`
- `01_docs/research/2026-09-25-unadopted-3313a-usb-pair-domain-sol.md` — `1d24b5c4790a`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/README.md` — `c1d467cbba92`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/measure.py` — `967b9c3efb9e`
- `08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md` — `48f056d1aa96`
- `08_reviews/2026-09-25_usb-complete-path-feasibility_terra.md` — `54278b66a7e4`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
