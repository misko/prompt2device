# Resume

<!-- pause-state:cc6e6ea13cdc2033f3d002e814c23185cb236815c6fe548bcd6660d95e10b5ef -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: Clean layout restart paused at first input issue: U_USB_ESD critical selection is PROTOTYPE_ONLY (ordinary admission exit 1). XU316 transient protection evidence is deferred; locked stock is not the issue. No fresh layout generated.
3. Resume with: `Discuss and resolve USB ESD electrical evidence and prototype-versus-release scope before choosing the clean restart path. Do not continue placement, generate a board, or repair the gate automatically.`

The authenticated checkpoint is `01_docs/BRIEF.md` at
`72d51682c4f5cceb2aabccf4b4b13a73c5961ffa06058ba6b7ea93042c585acb`.
