# Project status

<!-- pause-state:9b64b7187cbb52ededba3690929ac49f09aa9d6aa60328b756643a28e9b95342 -->

- Phase: `sourcing`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`c5dd2302a6fa`)
- Blocker: Critical USB ESD selection is unaccepted: public XU316 records do not define powered or rail-off USB DP/DM transient limits; 5UX component data and public stock cannot establish exact-board pin survival.
- Next command: `Search the bounded public XMOS XU316 reference set for exact USB protection evidence, then decide whether a separate engineering prototype and measured ESD/USB test is required before release; rerun critical_part_selection_admission.py only on new evidence.`

## Bound receipts

- `01_docs/findings.yaml` — `c6873217e959`
- `01_docs/research/2026-09-24-pesd2usb5ux-xu316-transient-hold-terra.md` — `22ea9288ce35`
- `01_docs/research/2026-09-24-usb-esd-selection-recovery-strategy.md` — `5580719edde3`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
