# Resume

<!-- pause-state:0c0667abf5a416f1f621c974dedce195c12b81b8832aec60d9703b66d7f8911c -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: J-PCBA-PRELAYOUT requires actual provider availability/economic response for 84 exact codes; response template generated, no placement started
3. Resume with: `python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py grade projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_request.json projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_response.csv --out projects/crow-usb-carrier-v1/06_build/sourcing/prelayout_receipt.json`

The authenticated checkpoint is `03_tscircuit/build/circuit.json` at
`ead8cb33c07afcb9dd371a5c61188c8f2fde59c55c9e703400d5b21765daa336`.
