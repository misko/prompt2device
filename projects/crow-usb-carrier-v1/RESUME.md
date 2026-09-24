# Resume

<!-- pause-state:bb59a516a147e2373c0eef32ef5df23312d5fd4a27b79f825e48cc525ef267eb -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The distinct P1 root remains unaccepted. On the isolated QSPI-gap board, all 13 exact QSPI handoffs validate, but the whole 59-net schema-2 screen is FAIL: legacy U_XU.51 is an oversized nonlocal JTAG witness and its allocation aborts. A pinned one-part U_USB_ESD east-move trial places all seven USB support courtyards in a disjoint region and leaves an open JTAG strip, but fixed J_USB remains an unmodeled edge endpoint and XU_RESET_N has a third digital_power owner. Native DRC remains nonzero with 499 unconnected items; the USB launch has six sub-0.410-mm width violations without qualified impedance. Connector FULL has 19 physical unknowns and TMUX filled/capped process acceptance remains external. No P1/P2/P3/route/release or order result is accepted.
3. Resume with: `Source-model a disjoint JTAG corridor for the four two-party JTAG nets, an explicit fixed J_USB edge/support handoff, and a separate XU_RESET_N digital-power branch; measure exact native faces, pad access and return without weakening 59-net coverage. Independently admit a fresh P1 packet after the remaining internal allocations are resolved. Keep connector FULL before P3/routing and TMUX process acceptance before release; do not promote scratch USB copper.`

The authenticated checkpoint is `06_build/checkpoints/schematic.json` at
`917a45414c65cf43dbeef24704da01beda6b9711175cf9cec3af109ec027f4d6`.
