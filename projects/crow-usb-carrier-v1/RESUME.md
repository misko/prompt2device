# Resume

<!-- pause-state:5447218e447058e84d5926739113c933c6490d943bdc28c4f837f7bcab9f1ce2 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: P1 remains unaccepted. On the isolated QSPI-gap board, all 13 QSPI handoffs validate, but the full 59-net schema-2 packet still FAILS. A four-net JTAG integration strip is native-open and validates four XU handoffs. Generic fixed-connector access is now represented fail-closed, but no exact J_JTAG access paths have been declared/proven; U_XU.38 reset remains a nonlocal witness. The reset net has five endpoints across three owners and no saved native copper. The crystal window contains only 3 of 7 pads; both XU crystal witnesses cross the QSPI owner. A pinned USB ESD move fits seven support courtyards, but J_USB edge region/outline remains unresolved pending connector FULL. Native DRC is nonzero with 499 unconnected items, and the USB launch has six unqualified sub-0.410-mm widths. Connector FULL has 19 physical unknowns; TMUX filled/capped process acceptance is external. No P1/P2/P3/route/release or order result is accepted.
3. Resume with: `On an isolated variant, declare and native-check four disjoint fixed J_JTAG access reservations into the source-owned JTAG strip, keeping the 59-net denominator and separate five-endpoint XU_RESET_N branch. Revise oscillator region/handoffs without crossing the QSPI owner. Resolve the separate J_USB edge region/outline after connector FULL evidence, then rerun P1 and P2. Connector FULL gates P3/routing; TMUX process acceptance gates release. Do not promote scratch USB copper.`

The authenticated checkpoint is `06_build/checkpoints/schematic.json` at
`917a45414c65cf43dbeef24704da01beda6b9711175cf9cec3af109ec027f4d6`.
