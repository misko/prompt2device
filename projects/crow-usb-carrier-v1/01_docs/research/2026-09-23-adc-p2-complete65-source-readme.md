# ADC supervisor bypass source proposal

Base: `682b862b84873c30f0de5f2721bfecc330bcd2db` in `projects/crow-usb-carrier-v1`.

`source.patch` is retained as incomplete composition history and is superseded.
It placed the capacitors against supervisor locations that only exist in the
separate complete64 placement proposal. Do not apply it alone.

The complete proposal is `complete65_source.patch`. It composes the complete64
ADC-reference placement with the following source repair and overrides the old
shared-cap coordinate exactly once. It adds `C_ADC_3V3X_OK_VDD` as 100 nF 0402,
`CL05B104KO5NNNC`, JLC `C1525`, pin 1 to `N3V3_ADC` (authored as `3V3_ADC`)
and pin 2 to GND. `C_ADC_DIGITAL_OK` remains the device-local bypass for
`U_ADC_1V8_OK`; the new capacitor is the device-local bypass for
`U_ADC_3V3X_OK`. The existing ADC supervisors remain the functionally selected
adjustable `TPS389001DSER` / `C1509297`; no `TPS389018DSER` substitution is
proposed.

The composed floorplan moves `C_ADC_DIGITAL_OK` to `[113.1, 107.0, 270]` and
places `C_ADC_3V3X_OK_VDD` at `[118.1, 107.0, 270]`.

Independent joint-65 verification passed against the composed proposal. It
found zero courtyard findings (minimum 0.250001 mm, at the new capacitor and
`U_ADC_3V3X_OK`), zero findings across 326,123 foreign-net pad pairs, 117,248
body-to-pad checks, and 117,576 pad-to-body checks. All four VREF corridors were
clear across 1,396 tested foreign non-GND effective F.Cu pads each. Numeric
constraints were 17/17 exact and the inherited prediction remained 16/16.
For each capacitor, pad 2 to its supervisor GND pin 2 is 1.300154 mm; pad 1 to
the actual VDD pin 4 is 2.905237 mm. The same rail also reaches MR pin 3 at
1.969873 mm. The report is `complete65_joint_verification.json`, SHA-256
`70677edc20c6363d68f6bfeef44c407d6adf1765ba1bd83ebd4a7d65f83a6519`.
These are source-proposal measurements only; regenerated placement and P3/FULL
must verify the final VDD/GND copper paths.

Apply `complete65_source.patch` from the authoritative repository root. Then run the full
source conductor because TSX changed:

```bash
cd projects/crow-usb-carrier-v1
bash 03_src/rebuild_all.sh
```

Stop when the conductor reaches its required schematic-review checkpoint. This
packet does not authorize continuing beyond that checkpoint. The isolated P2
placement proposal requires separate admission before any later FULL19 work;
do not invoke `--resume-after-schematic-review` from this packet.

## Expected accounting changes

- ADC-reference proposal scope: 64 -> 65 components.
- Whole-board source census: 568 -> 569 components.
- Part/MPN set: unchanged; the added ref reuses `CL05B104KO5NNNC` / `C1525`.
- Five-board demand for this MPN: 340 -> 345 pieces.
- With the user-required 150-piece stock buffer, admission threshold: 495.
- Existing public JLC snapshot: 26,390,124 pieces; arithmetic surplus over the
  buffered threshold: 26,389,629. This is historical public-record arithmetic,
  not live stock or allocation evidence.

## Invalidated downstream evidence

The source change invalidates every artifact or receipt derived from the prior
568-component TSX/netlist or 64-component ADC-reference scope, including:

- `03_tscircuit/build/circuit.json`, `03_tscircuit/build/schematic.pdf`,
  `03_tscircuit/kicad/crow_carrier.kicad_sch`, and all `03_tscircuit/verification/*`.
- Current generated `04_kicad/crow_carrier.kicad_sch` and
  `04_kicad/crow_carrier.kicad_pcb`, placement/proximity results, route imports,
  fill/stitch, ERC/DRC/parity, and layout-seal evidence.
- Generated BOM/CPL/Gerber/drill/fabrication payloads, digital-twin and assembly
  receipts, and release-review/publication evidence derived from them.
- Sourcing manifests and receipts whose quantities or component census bind the
  old state, including `01_docs/sourcing/shopping-list-2026-09-22-1437.{json,md}`,
  `01_docs/sourcing/exact-parts.csv`, and current `06_build/sourcing/*` outputs.
- The complete64 proposal is superseded as source-only research. It remains
  historical evidence and supplies no native-generation, placement, routing,
  sourcing-admission, or release acceptance for this 65-component proposal.

No generated Circuit JSON, schematic, KiCad board, BOM, sourcing manifest, or
receipt is included here. No native generation, save, route, authenticated
sourcing, release mutation, or firmware work was performed.
