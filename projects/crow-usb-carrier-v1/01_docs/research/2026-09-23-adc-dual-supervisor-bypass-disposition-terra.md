# ADC dual-supervisor bypass disposition

**Bounded source research; no source/BOM/board edit or acceptance.** Packet examined: `/tmp/crow-p2-adc-reference-complete64-20260923`. The selected supervisor dossier is `TPS389018DSER`, TI TPS3890 datasheet `02_parts/TPS389018DSER/TPS3890-SBVS228A.pdf` (the PDF’s own document banner is **SLVSD65A, revised May 2016**; the `part.yaml` `SBVS228A` document identifier should be reconciled separately).

## Finding

Both `U_ADC_1V8_OK` and `U_ADC_3V3X_OK` are TPS389018DSER devices. Their VDD pin is **pin 4** and GND is **pin 2**. The source connects both VDD pins to the common `N3V3_ADC` rail; their names identify the rails being supervised through SENSE/divider networks, not distinct VDD supplies. `C_ADC_DIGITAL_OK` is a 100 nF, 0402 `CL05B104KO5NNNC` / JLC `C1525` from N3V3_ADC to GND.

TI TPS3890 **§11.1, page 17** states: “Make sure that the connection to the VDD pin is low impedance. Good analog design practice is to place a 0.1µF ceramic capacitor near the VDD pin.” Figure 27 labels that input capacitor `CIN` at the VDD/GND side. This is manufacturer layout guidance/recommendation, not a stated electrical must/shall requirement or a quantitative distance limit.

The complete64 handoff measures the sole C to supervisor supply/GND pins at **2.066/4.101 mm** for `U_ADC_1V8_OK` and **2.813/2.453 mm** for `U_ADC_3V3X_OK`. That confirms a common supply rail and a physically compact shared component, but it does **not** make one capacitor “near the VDD pin” of *each* package by device-local wording. TI’s singular per-device layout example supports a local capacitor per supervisor; it provides no authority that one capacitor may substitute for two local bypass capacitors, even when the devices share VDD.

## Disposition

A single capacitor is electrically connected and may be functional on the shared low-current rail, but the authored single-capacitor choice is **not defensible as complete compliance with the selected part’s per-device local-bypass recommendation**. This is a recommendation-level layout debt, not evidence of a violated hard datasheet operating requirement. It should not be recorded as a P2 acceptance pass based on connectivity/proximity alone.

## Minimal source/BOM repair proposal

Add exactly one device-local bypass capacitor:

| New ref | Value / footprint / stocked MPN | Connectivity | Placement intent |
|---|---|---|---|
| `C_ADC_3V3X_OK_VDD` | 100 nF, `C_0402_1005Metric`, existing `CL05B104KO5NNNC`, existing JLC `C1525` | pad 1 → `N3V3_ADC`, pad 2 → GND; do not connect to SENSE, CT, MR, or RESET | place next to `U_ADC_3V3X_OK.4` (VDD) with short local return to `.2` (GND) |

Retain `C_ADC_DIGITAL_OK` as the local bypass for `U_ADC_1V8_OK` and retain all divider/CT/reset circuitry. The existing shopping list already assigns this same MPN to `C_ADC_DIGITAL_OK` and other 100-nF bypass capacitors, so the change introduces no alternate part or new sourcing record. Source owner must add the symbol/netlist/BOM/floorplan ownership and re-run the normal source and placement verification; P3/FULL must verify low-impedance VDD/GND copper returns.

No manufacturer mm was inferred. If the source owner chooses to keep one capacitor, it must be explicitly marked as a deliberate deviation from TI’s device-local layout recommendation and accepted as such; connectivity alone is not manufacturer authority for equivalence.

## Follow-up: authoritative dossier identity and source-repair inventory

### Exact TI document identity

The local bytes have SHA-256 `ee79599730e7606ba9718d9820b411020e3dcd9ff7d44572f8ee63fead15b9d0`, exactly matching `02_parts/TPS389018DSER/part.yaml`. However, page headers and the copyright/footer in those bytes identify the document as **TI TPS3890, SLVSD65A, March 2016, revised May 2016**. Thus the authoritative identity for the existing hash-bound PDF is `TPS3890 / SLVSD65A / revised May 2016`, reached through TI’s stable product symlink `https://www.ti.com/lit/ds/symlink/tps3890.pdf`.

`part.yaml` currently calls the same bytes `doc_id: SBVS228A`, `revision: A`, and its local filename says `TPS3890-SBVS228A.pdf`. That is metadata/filename drift, not evidence of a different document: the hash is consistent, the displayed document identifier is not. The source owner should correct only the document identity fields (and optionally the local filename while updating its references) to `SLVSD65A` / `May 2016`; retain the existing hash and URL unless a newly fetched TI primary PDF is deliberately admitted.

### Exact authored and derived change inventory

The electrical source of this control cell is `03_tscircuit/src/crow_retained_analog.tsx`, lines 263–270: it instantiates both supervisors and the present `C_ADC_DIGITAL_OK`. Add the new `<C>` there with the existing `100nF`, `CL05B104KO5NNNC`, `C1525`, and `3V3_ADC`/`GND` arguments. The current component source uses `TPS389001DSER` while the selected dossier directory is `TPS389018DSER`; resolve that exact selected-MPN/dossier discrepancy in the same source-admission change before claiming exact-part authority.

Authoritative placement/control ownership then needs an added reference in `03_src/modular_plan.json`, `03_src/rules/integration.yaml`, and `03_src/floorplan.yaml` (new post-anchor/ownership and a local pose beside `U_ADC_3V3X_OK`). `03_tscircuit/src/z_analog_schematic_presentation.tsx` needs a presentation placement so the regenerated schematic remains legible. The expected derived outputs are `03_tscircuit/build/circuit.json`, `03_tscircuit/build/schematic.pdf`, `04_kicad/crow_carrier.kicad_sch`, board/BOM outputs, and sourcing manifests including `01_docs/sourcing/shopping-list-2026-09-22-1437.{json,md}`, `01_docs/sourcing/exact-parts.csv`, and the current `06_build/sourcing/*` receipts. Do not hand-edit those derived artifacts: rebuild through `03_src/rebuild_all.sh`, whose declared TSX root is `03_tscircuit/src/crow_carrier.tsx`, after the normal source admission.

### Existing public-stock evidence and five-board delta

The existing cited JLC record in `01_docs/sourcing/shopping-list-2026-09-22-1437.json` records `C1525` / `CL05B104KO5NNNC`, read **2026-09-22** (one day old), at 26,390,124 pieces; current required quantity is 340 = 68 per board × five boards. One added capacitor per board makes the five-board requirement **345** and leaves an arithmetic snapshot margin of **26,389,779** pieces. This is a one-day-old public-record calculation, not a live availability assertion and not a new sourcing admission.

## Critical variant correction and procurement threshold (2026-09-23)

The prior wording “both supervisors are TPS389018DSER” is **incorrect** for the authored circuit. `03_tscircuit/src/crow_retained_analog.tsx:261` and `:266` explicitly instantiate both `U_ADC_1V8_OK` and `U_ADC_3V3X_OK` as **TPS389001DSER**, JLC `C1509297`. `01_docs/sourcing/exact-parts.csv` likewise assigns TPS389001DSER to both. The only checked-in TPS3890 part dossier is instead `02_parts/TPS389018DSER/part.yaml`, a different MPN. Do not normalize this discrepancy by changing a name.

The primary TI TPS3890 datasheet, **SLVSD65A revision A, page 3 Device Comparison Table**, makes the distinction electrically critical: TPS389001 has an **adjustable** 1.15-V negative threshold, whereas TPS389018 is a **fixed 1.8-V** part (1.73-V negative threshold). The authored supervisors use SENSE dividers: 1V8 uses 52.3 kΩ/100 kΩ, yielding about 1.182 V at a 1.8-V rail; 3V3X uses 169 kΩ/100 kΩ, yielding about 1.228 V at a 3.3-V rail. Those values are compatible with a TPS389001-style adjustable threshold and incompatible with a TPS389018 fixed 1.8-V threshold. The selected exact electrical MPN in the actual circuit is therefore TPS389001DSER; the absence of a matching part dossier is a source-admission blocker independent of the bypass repair.

The VDD bypass-layout recommendation is family-level and still applies to TPS389001 (same page 3 VDD pin function and page 17 layout guidance), so the one-additional-100-nF recommendation remains valid. Its downstream source repair must use/introduce a **TPS389001DSER** exact dossier and correct sourcing/footprint authority rather than reusing the TPS389018 dossier as evidence.

The prior stock arithmetic omitted the required user procurement buffer. Existing build demand is 340 (68 per board × 5). The added capacitor raises build demand to **345**. Adding the user-required **150 per MPN** produces a procurement threshold of **495**. Against the 2026-09-22 JLC snapshot of 26,390,124 C1525 pieces, the snapshot arithmetic surplus is **26,389,629**. This is a one-day-old public-record calculation, not a fresh stock claim.

### Corrigendum to the critical-variant finding

The immediately preceding sentence saying no TPS389001DSER dossier exists is corrected here while preserving the audit trail. `02_parts/TPS389001DSER/part.yaml` **does exist**, has the same SHA-bound primary `TPS3890_SLVSD65A.pdf`, names TPS389001DSER as an adjustable supervisor, and records the 1.15-V threshold. It is the correct exact-part dossier for both authored ADC supervisors. The required repair is therefore to bind the two references to this existing TPS389001 dossier/footprint authority and remove the erroneous use of TPS389018DSER as their evidence; no new TPS389001 dossier is needed. The fixed-versus-adjustable finding and the resulting source-admission issue remain unchanged.
