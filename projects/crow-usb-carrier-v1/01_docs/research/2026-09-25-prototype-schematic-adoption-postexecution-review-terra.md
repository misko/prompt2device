# Independent post-execution review: TI prototype schematic adoption

**Receipt reviewed:**
`06_build/prototype_only/adoptions/20260925T103620Z-1653530.json`, SHA-256
`2a20067d8c6106ce835255ad3758bb4b5c041fe40b1ceec3d2c767d86447cd82`.

**Disposition: PASS for the recorded `PROTOTYPE_ONLY`, `SCHEMATIC_ONLY`
transaction.**  This review neither promotes the ordinary checkpoint nor makes
a PCB, routing, release, order, electrical-qualification, or P1 claim.

## Receipt and artifact binding

The receipt identifies the private TI producer receipt by SHA-256
`5cccaaa7b577a9ad07b647e77a7759ce203e81d8e6efd35a3fa55e7a9ab5cd42` and
records these exact output bytes, all rehashed after adoption:

| Permitted output | Receipt / current SHA-256 |
| --- | --- |
| `03_tscircuit/build/circuit.json` | `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d` |
| `04_kicad/crow_carrier.kicad_sch` | `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d` |
| `06_build/netlists/crow_carrier.net` | `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd` |
| `03_tscircuit/build/schematic.pdf` | `d2e54c1195a217b231fbc2ab058e051b01dc8e45b534c65d38006978af386eed` |

The native netlist parses as 569 components, 1,787 pad/net tuples, and 428
nets.  `U_USB_ESD` is exactly
`Package_TO_SOT_SMD:Texas_DRT-3` / `TPD2EUSB30ADRTR`, with pads
1=`USB_DP`, 2=`USB_DN`, and 3=`GND`.

The private backup at
`06_build/prototype_only/adoptions/20260925T1030Z-ti-adoption-backup/`
contains all four receipt `before` bytes.  In particular, the preserved stale
Nexperia circuit, schematic, netlist, and PDF hashes are respectively
`ff30fe8a46bc44befa7533038bbf17d2ed0aed2e2b263b87dbd36f8fb5f3d41a`,
`3794e0f05bf8acd3532d392b38026d6cb59b23af0d43119c2e02f5e7bbf6f28e`,
`457763489019b299491c38d303b618561b45be2dc43e6298fe89b25effd8e0cd`, and
`41989418b96805c04e7b833b2e17d8c53dfbc18d8be1eaa866ec09de9c6947a2`.

## State and gates

- The pause state remains byte-identical to the receipt binding:
  `70e66e83c408c14c5140ed76d1bb69298be64e95e821f51ca1f60af2b4dea4d0`.
  The selection binding is likewise unchanged:
  `15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
- `06_build/checkpoints/schematic.json` is unchanged in Git.  The receipt
  explicitly records `ordinary_checkpoint: NOT_REFRESHED` and
  `pinned_reuse_schematic: NOT_PROMOTED`.
- Fresh canonical checks passed: E-FAULT `1/1` conditional source/fuse family,
  P-PREC 69 selected / 69 applications / 69 research covered with semantic
  `APPROVED` and engineering `INCOMPLETE`, and KiCad ERC with zero errors.
  These do not discharge the source/fuse supplier and first-article debt or
  any layout engineering debt.
- Ordinary
  `critical_part_selection_admission.py` still reports `PROTOTYPE_ONLY` and
  exits 1; `--require-prototype` exits 0.  Thus the ordinary conductor remains
  closed.

There is no canonical `04_kicad/*.kicad_pcb` tracked artifact to have been
altered by this adoption.  The only changed canonical KiCad path is the
permitted `crow_carrier.kicad_sch`.

## Commands run

```sh
python3 skills/kicad-pcb/scripts/early_design_check.py \
  projects/crow-usb-carrier-v1 --fault-envelope
python3 skills/kicad-pcb/scripts/ic_reference_check.py \
  projects/crow-usb-carrier-v1 --require-semantic-review
kicad-cli sch erc --severity-error --exit-code-violations \
  -o /tmp/crow-ti-audit-erc.*/erc.txt \
  projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_sch
python3 skills/pcb-design/scripts/critical_part_selection_admission.py \
  projects/crow-usb-carrier-v1
```

All three schematic-stage gates returned zero; ordinary selection returned 1
as required for this prototype-only selection.
