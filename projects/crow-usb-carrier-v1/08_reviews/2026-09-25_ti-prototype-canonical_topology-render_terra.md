subject: Crow USB Carrier v1 canonical TI schematic artifacts, prototype-only topology and render review
date: 2026-09-25
reviewer: independent Terra, native-netlist topology and PDF readability lens
context-given: exact canonical schematic-only adoption subject
source_commit: 084f5abbf765eb61120379084eab27b4db1b422d
board_sha256: not-applicable (this review does not use or authorize a PCB)
design_verdict: SOUND
order_verdict: DO-NOT-ORDER

# TI canonical prototype schematic topology and render review

**Decision: SOUND only for the hash-bound schematic topology and PDF
readability subject below.**  The selected USB ESD part remains
`PROTOTYPE_ONLY`.  This is not an ordinary checkpoint, pre-route permission,
P1/P2 result, ESD-transient qualification, physical-placement/routing review,
release, or order decision.

## Exact subject and current policy binding

| Artifact | SHA-256 |
| --- | --- |
| `03_tscircuit/build/circuit.json` | `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d` |
| `04_kicad/crow_carrier.kicad_sch` | `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d` |
| `06_build/netlists/crow_carrier.net` | `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd` |
| `03_tscircuit/build/schematic.pdf` | `d2e54c1195a217b231fbc2ab058e051b01dc8e45b534c65d38006978af386eed` |
| normalized native-netlist topology | `b3d04cf63d786f66d8052541e9a830d6fd4096b1e74b34e326de892c46827805` |
| current `02_parts/*/part.yaml` aggregate (114 dossiers) | `ffc4929303fd056303a0798573660c70c18c363efeed6e0c5df01badce227266` |
| current semantic design-rules projection | `36aa880be39c4c2d2a1927a3c266c1ffd9ea98a78538701406c730d0464d2858` |
| `02_parts/TPD2EUSB30ADRTR/part.yaml` | `091b698cfc5bd7f72766c80388ab1efe3331c025254bedea1d628de6b465a387` |
| `03_src/rules/critical_part_selection.yaml` | `15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba` |

The last rule still declares the exact `U_USB_ESD = TPD2EUSB30ADRTR / C94934`
selection as `prototype_only`; ordinary critical-selection admission exits 1.

## Native topology review

The circuit contains 569 `source_component` and 569 `schematic_component`
records.  The native netlist contains the same 569-reference set, 1,787
assigned pad/net tuples, and 428 named nets.  A fresh scratch
`kicad-cli sch export netlist` from the exact canonical schematic parsed to
the same component, pad/net, and net dictionaries as the bound native
netlist: 569/569, 1,787/1,787, and 428/428 respectively.

`U_USB_ESD` is exactly native footprint
`Package_TO_SOT_SMD:Texas_DRT-3`, value `TPD2EUSB30ADRTR`, with pad 1 on
`USB_DP`, pad 2 on `USB_DN`, and pad 3 on `GND`.  The data paths remain
separate:

| Net | Exact native endpoints |
| --- | --- |
| `USB_DP` | `J_USB.A6`, `J_USB.B6`, `U_USB_ESD.1`, `U_XU.60` |
| `USB_DN` | `J_USB.A7`, `J_USB.B7`, `U_USB_ESD.2`, `U_XU.59` |

This establishes graph identity and exact TI pin/net assignment for this
subject.  It does not establish signal integrity, ESD clamping performance,
connector mating, or a physical return path.

## Render/readability review

`pdfinfo` reports a readable, unencrypted PDF 1.7 with 45 pages at
900 × 607.5 pt.  I rasterized pages 1, 39, 44, and 45 at 220–300 dpi and
checked the extracted text across all 45 pages.  Page 39 clearly identifies
the USB connector, TI `U_USB_ESD`, `USB_DP`, `USB_DN`, and GND.  XMOS appendix
pages 44 and 45 have distinct rows and columns through pins 79–129, including
I²C pins 93–94, QSPI pins 127–128, and EP/GND pin 129; no clipping or
overprint was observed.  The first page's power-input symbols and labels are
also legible at normal rendered-page scale.

The older canonical `pre-route_topology.md` and
`pre-route_schematic_render.md` remain stale for their own ordinary
pre-route contract.  This dated prototype-only review does not update or
substitute for them.

## Commands and limits

```sh
kicad-cli sch export netlist --output /tmp/crow-ti-topology/export.net \
  projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_sch
pdfinfo projects/crow-usb-carrier-v1/03_tscircuit/build/schematic.pdf
pdftoppm -f 39 -l 45 -r 300 -png \
  projects/crow-usb-carrier-v1/03_tscircuit/build/schematic.pdf \
  /tmp/crow-ti-canonical-pdf-review/page
```

No PCB was generated, inspected, or accepted.  The open prototype-only
selection hold and all ordinary schematic, physical, manufacturing, and
qualification gates remain in force.
