# Resume

<!-- pause-state:d1789bb6807c72a76f974f97991b308358a5980cd9e50bd847fcfd8d76290240 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: D5/D7 source admission remains held: XMOS last observed 46/155; ADC and analog-switch replacements remain under review. The adjustable main buck and core feedback are integrated source candidates. D9 manual assembly covers exactly 24 THT refs with qualifying dated distributor stock. Diagnostic source has 509 components; canonical 493-reference schematic is historical. Carrier ambient and private-XMOS inventory questions remain unanswered.
3. Resume with: `Complete ADC and analog-switch source reviews and XMOS sourcing, then regenerate and admit the schematic before P1-P5 block placement; preserve all 150-extra stock requirements`

The authenticated checkpoint is `03_tscircuit/build/circuit.json` at
`ead8cb33c07afcb9dd371a5c61188c8f2fde59c55c9e703400d5b21765daa336`.
