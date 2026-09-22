# Project status

<!-- pause-state:0c0667abf5a416f1f621c974dedce195c12b81b8832aec60d9703b66d7f8911c -->

- Phase: `schematic`
- State: **PAUSED**
- Checkpoint: `03_tscircuit/build/circuit.json` (`ead8cb33c07a`)
- Blocker: J-PCBA-PRELAYOUT requires actual provider availability/economic response for 84 exact codes; response template generated, no placement started
- Next command: `python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py grade projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_request.json projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_response.csv --out projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_receipt.json`

## Bound receipts

- `06_build/verification/pipeline/electrical_closure.json` — `adf49bc658e3`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
