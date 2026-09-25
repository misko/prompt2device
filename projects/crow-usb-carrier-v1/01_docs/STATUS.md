# Project status

<!-- pause-state:9fca6b57b9e65fe03e121c8b5c0b80c0a29b08462a3e57b333b4ecfc60d70378 -->

- Phase: `prototype-layout-diagnostic`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`15288355fcc7`)
- Blocker: The frozen expanded board has no admitted P1/P2 integrated candidate. Its shared reset/JTAG screen is INCOMPLETE despite zero checker errors; USB 7628G full-width launches miss 0.150-mm foreign clearance at Type-C and XMOS, while the narrower 3313A source remains unadopted. The isolated C105 timing move improves local geometry but all 14 timing nets/54 pad duties remain INCOMPLETE. D18 private routing needs independent P1 and affected P2 first. Connector FULL, prototype-only TI ESD, production stack, release and order holds remain open.
- Next command: `Decide the 3313A research source/stack hypothesis from the pinned public sensitivity and exact rule packet; preserve D15 FAILED_RESEARCH. Then create one separately authorized, source-generated unrouted candidate on the frozen placement reference that integrates the reviewed shared-reset and C105 proposals, reopens source/native parity, and independently grades all P1 plus affected P2. Do not launch D18 private routing until those admissions and connector-neighbour assumptions are met.`

## Bound receipts

- `01_docs/BRIEF.md` — `d58ce4e0f783`
- `01_docs/decisions/0012-initial-public-stock-lock.md` — `acffa297e45c`
- `01_docs/decisions/0013-usb-esd-prototype-boundary.md` — `ed83de26a0c3`
- `01_docs/decisions/0018-evidence-scheduling-and-private-design-work.md` — `3844ed14d92b`
- `01_docs/findings.yaml` — `27cbf04b140a`
- `01_docs/journal/placement.md` — `72e483c6fed2`
- `01_docs/research/2026-09-24-public-stock-569/public-stock.json` — `aa9491bf6df4`
- `01_docs/research/2026-09-25-early-pair-preflight/expanded_locked.json` — `00dba81709ab`
- `01_docs/research/2026-09-25-early-pair-preflight/historical_d15.json` — `dd3264b35baa`
- `01_docs/research/2026-09-25-early-pair-preflight/replay.json` — `a78a74a4f228`
- `01_docs/research/2026-09-25-expanded-locked-p1p2-single-experiment-no-go-terra.md` — `1209860e291b`
- `01_docs/research/2026-09-25-expanded-locked-usb-edge-ownership-proposal-terra.md` — `5b04898fa6fe`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/README.md` — `50422032d2fd`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/probe.py` — `9ad727e43a2a`
- `01_docs/research/2026-09-25-expanded-service-reset-access-sol/result.json` — `3dc4584cc1ab`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/README.md` — `6e3284fc9f4c`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measure.py` — `7812eb60ee26`
- `01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measurement.json` — `93bb33a0e1ef`
- `01_docs/research/2026-09-25-expanded-tdm-c105-placement-sol/README.md` — `11fe8bb7f044`
- `01_docs/research/2026-09-25-expanded-tdm-c105-placement-sol/receipt.json` — `beac75216c5d`
- `01_docs/research/2026-09-25-expanded-tdm-c105-placement-sol/replay.py` — `f9f2eb559274`
- `01_docs/research/2026-09-25-jlc-3313-uniform-usb-solve-sol/mask_sensitivity_capture.json` — `9e08ce38014b`
- `01_docs/research/2026-09-25-jlc-3313-uniform-usb-solve-sol/mask_sensitivity_receipt.md` — `854ab55b0602`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/README-linked.md` — `2d8ed4470f93`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/README.md` — `5c4dd4568f12`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/build.py` — `9c23a3c6099f`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/build_linked.py` — `69f064a7185a`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/linked-summary.json` — `5fd498e74fd1`
- `01_docs/research/2026-09-25-reset-two-corridor-schema-probe-sol/summary.json` — `c517898f4659`
- `01_docs/research/2026-09-25-ti-prototype-p-prec-isolated-check-sol.md` — `980eebc12250`
- `01_docs/research/2026-09-25-ti-prototype-source-schematic-checks-terra.md` — `153cc44ff650`
- `01_docs/research/2026-09-25-ti-unrouted-diagnostic-board-sol.md` — `f84f08170719`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/README.md` — `7caae0d954d6`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-20260925.json` — `ec9cfedff7b1`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-independent-terra.json` — `2ef86d1c3b69`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/replay.py` — `e1473de36945`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/source_adoption_gate.md` — `f2c8cc83a871`
- `01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/source_diff.patch` — `707d8b940751`
- `01_docs/research/2026-09-25-unadopted-3313a-usb-pair-domain-sol.md` — `1d24b5c4790a`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/README.md` — `c1d467cbba92`
- `01_docs/research/2026-09-25-usb-path-feasibility-sol/measure.py` — `967b9c3efb9e`
- `08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md` — `48f056d1aa96`
- `08_reviews/2026-09-25_usb-complete-path-feasibility_terra.md` — `54278b66a7e4`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
