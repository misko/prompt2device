# Combined hardware source check — 2026-09-22

The current analog, USB front end, digital and input-power modules expand to 422 unique component references. All footprint shorthand strings accepted the pinned footprinter parser. All 85 distinct MPNs resolve to a current local part dossier and a literal KiCad library:name footprint. A coordinator check loaded every one of those 85 native footprints from the current worktree or installed KiCad libraries. This checks loadability, not pin-to-net correctness or manufacturing acceptance.

Evidence: `06_build/tmp/analog-adoption/expanded-components.json` and `06_build/tmp/power-adoption/combined-native-load.json`. The historical analog-adoption directory name does not limit the combined inventory's scope.

The input-power component fixture expanded 17 source components and 65 pads. Its default positions produced two footprint-overlap errors and two corresponding pad-clearance errors between D_IN and J_PWR, plus an autorouting-skipped error. These are unplaced fixture collisions; no accepted placement or routing is claimed. The complete render is retained as `06_build/tmp/power-adoption/component-render.json`. Placement must resolve and recheck these relationships on the actual board.

Project contracts audit: 390 files, zero violations. Commissioning hold remains in force. Next work is source pin/net mapping verification, schematic composition and readable presentation, and replacement of scaffold rules before native schematic admission.

A separate connected-pin census examined 1,276 source connections. 1,261 have matching literal native pad numbers; the remaining 15 are J_USB contacts, all resolved through the existing dossier’s explicit schematic-to-manufacturer aliases. Zero connected source pins remain unmatched. This is identity coverage, not confirmation of electrical function, NC correctness, or full native schematic/PCB parity. Evidence: `06_build/tmp/power-adoption/combined-connected-pin-check.json`.
