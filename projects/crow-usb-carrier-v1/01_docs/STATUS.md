# Project status

<!-- pause-state:bc21b3e8c3cc4a67cdb7fd6b8d0acbd8aad2698ede3ac384542fb850b4940e63 -->

- Phase: `sourcing`
- State: **PAUSED**
- Checkpoint: `03_src/rules/critical_part_selection.yaml` (`eb3f74a6a2b8`)
- Blocker: Crow selected TI USB ESD stock is locked to the initial 307-versus-155 public screen. Electrical selection still holds on the open XU316 powered/rail-off transient finding; no later stock recheck may force a source change.
- Next command: `Complete independent TI/XU316 USB transient suitability review from public primary records; if still unbounded, define a prototype-only exact-board ESD test before accepting selection. Then rerun critical_part_selection_admission.py and the full conductor on a coherent TI source.`

## Bound receipts

- `01_docs/BRIEF.md` — `45906e341218`
- `01_docs/decisions/0012-initial-public-stock-lock.md` — `acffa297e45c`
- `01_docs/findings.yaml` — `08a4b74f6170`
- `01_docs/research/2026-09-24-public-stock-569/public-stock.json` — `aa9491bf6df4`
- `01_docs/research/2026-09-24-ti-usb-esd-stock-lock-reinstatement.md` — `2a9c1feacebf`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
