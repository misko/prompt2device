# Resume

<!-- pause-state:da8bc23e8f08ee671e01c5824f2f49d51afb5a8a782bd1a5a23de9ff088461ce -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: D5/D7 require JLC population and build-plus-150 stock; selected XMOS has 46 versus 155 required; ADC and remaining SMD substitutions unqualified. Checkpoint is historical before OPA/crystal source changes.
3. Resume with: `Qualify stocked USB/ADC and remaining source alternatives, regenerate and review source admission, then resume the schematic and P1-P5 block graph`

The authenticated checkpoint is `03_tscircuit/build/circuit.json` at
`ead8cb33c07afcb9dd371a5c61188c8f2fde59c55c9e703400d5b21765daa336`.
