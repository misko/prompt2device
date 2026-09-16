# contract: 01_docs/renders/

Purpose: tracked native board render evidence, governed by ../contracts.md.
Mutable current views are regenerated from the saved 04_kicad board. They are
not source geometry, independent reviews, or release admission.

## Allowed

| File | Purpose | Rule |
|---|---|---|
| contracts.md | Membership and validation | This file |
| README.md | View guide and reproducible commands | State current evidence limits |
| manifest.json | Exact producer board, models, tools, commands and image hashes | Regenerate with images; never restamp old pixels |
| front-left.png | South connector mouths, left oblique | Native KiCad rendering |
| front-right.png | South connector mouths, right oblique | Native KiCad rendering |
| rear-left.png | North connector mouths, rear oblique | Native KiCad rendering |
| bare_top.png | Top copper/mask/silk without component bodies | Generated fabrication truth view |
| bare_bottom.png | Bottom copper/mask/silk without component bodies | Generated fabrication truth view |

## Validate

Reopen every image and verify SHA-256 against manifest.json. Verify the current
board bytes match board_sha256 and every resolved model matches its hash.
Replay the recorded commands with matching KiCad/tool/model versions. Inspect
the entire board frame, RJ45 mouths on both rows, and mounting side. Native
render success does not prove enclosure fit, cable service, routing or release.
Disposable camera experiments and logs remain under 06_build/renders/.
