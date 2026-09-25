# Resume

<!-- pause-state:9b64b7187cbb52ededba3690929ac49f09aa9d6aa60328b756643a28e9b95342 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: Critical USB ESD selection is unaccepted: public XU316 records do not define powered or rail-off USB DP/DM transient limits; 5UX component data and public stock cannot establish exact-board pin survival.
3. Resume with: `Search the bounded public XMOS XU316 reference set for exact USB protection evidence, then decide whether a separate engineering prototype and measured ESD/USB test is required before release; rerun critical_part_selection_admission.py only on new evidence.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`c5dd2302a6faa6020458335aaf51da24a8bf93e74c3c3804393b540fb869616f`.
