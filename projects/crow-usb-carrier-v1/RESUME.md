# Resume

<!-- pause-state:bc21b3e8c3cc4a67cdb7fd6b8d0acbd8aad2698ede3ac384542fb850b4940e63 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: Crow selected TI USB ESD stock is locked to the initial 307-versus-155 public screen. Electrical selection still holds on the open XU316 powered/rail-off transient finding; no later stock recheck may force a source change.
3. Resume with: `Complete independent TI/XU316 USB transient suitability review from public primary records; if still unbounded, define a prototype-only exact-board ESD test before accepting selection. Then rerun critical_part_selection_admission.py and the full conductor on a coherent TI source.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`eb3f74a6a2b821128b194ca0a283716e64a3f4c00ea4a352917f69b5f8463a57`.
