# Project status

<!-- pause-state:22f93e51e77f56ac1dfea5ed55bc45565a8419fe427c5d2749c5f5eb153c62f1 -->

- Phase: `prototype-layout-diagnostic`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`15288355fcc7`)
- Blocker: 3313A exact-pair clearance is tested but unadopted. Current source has incomplete P1 reset/USB ownership and timing bundle access/return; affected P2, connector FULL, prototype-only ESD, stack/order and release remain open. The 0.15-mm JTAG access geometry is a screened proposal, not a routed/native P1 pass.
- Next command: `On the frozen expanded placement, make one source-backed P1 candidate for the five-terminal reset tree and owned USB fixed-connector corridor, then test native pad access and the complete P1 denominator. Separately resolve timing-neighbour access and local GND return for affected P2. Keep 3313A source unadopted until full USB topology/return review; D18 allows no private route experiment before independent P1 and affected P2 admission. Preserve D15 failed history and physical/release holds.`

## Bound receipts

- `01_docs/BRIEF.md` — `d58ce4e0f783`
- `01_docs/decisions/0012-initial-public-stock-lock.md` — `acffa297e45c`
- `01_docs/decisions/0013-usb-esd-prototype-boundary.md` — `ed83de26a0c3`
- `01_docs/decisions/0018-evidence-scheduling-and-private-design-work.md` — `3844ed14d92b`
- `01_docs/findings.yaml` — `27cbf04b140a`
- `01_docs/journal/placement.md` — `cc7a04e10e5a`
- `01_docs/research/2026-09-24-public-stock-569/public-stock.json` — `aa9491bf6df4`
- `01_docs/research/2026-09-25-early-pair-preflight/expanded_locked.json` — `00dba81709ab`
- `01_docs/research/2026-09-25-early-pair-preflight/historical_d15.json` — `dd3264b35baa`
- `01_docs/research/2026-09-25-early-pair-preflight/replay.json` — `a78a74a4f228`
- `01_docs/research/2026-09-25-expanded-locked-p1p2-single-experiment-no-go-terra.md` — `1209860e291b`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/README.md` — `50422032d2fd`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/probe.py` — `9ad727e43a2a`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/result.json` — `3dc4584cc1ab`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/README.md` — `6e3284fc9f4c`
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
