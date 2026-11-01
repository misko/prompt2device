# Independent narrow ADC review — PCM1864DBT → PCM1864DBTR

Date: 2026-11-01 UTC / 2026-10-31 PDT. Verdict: **PASS for local metadata-only working-source/BOM adoption**, affecting carrier U1 and U2, `2 × 2 carriers = 4` installed. No spare/attrition allowance is inferred. Compatibility class: **packaging-only**. This is not acceptance of a new release, factory placement, allocation, procurement or production. No design, BOM, quote or account edits were performed by this reviewer.

## Independently inspected evidence

I read the supplied TI PDF directly, extracted its packaging rows and pin-function tables, rendered its actual DBT0030A package/land-pattern pages, reopened the released schematic and BOM, and loaded the released carrier PCB read-only through pcbnew to inspect U1/U2 pads and nets. I independently inspected the supplied fresh structured JLC response, not another review's verdict. pcbnew emitted its three existing property-enum warnings but returned both footprints; no board was saved and no new DRC result is claimed.

Source release root: `/home/mouse9911/gits/circuits-publish-vnext-crow-v3-20261025/projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1`.

### Identity, lifecycle and packing: PASS

[TI primary PCM186x datasheet](https://www.ti.com/lit/ds/symlink/pcm1864.pdf), supplied PDF SHA256 `c42b9dfac5d8a4f684edc45edc8a3b2b82d3e26ea352f1e019044ed8aad4ab50`, package-option addendum dated 2025-11-10: both exact orderables are Active/Production, TSSOP DBT, 30 pins, RoHS, NiPdAu, −40…125°C, marking PCM1864. Both carry Level-2 / 260°C / one-year moisture classification. `PCM1864DBT` is a 60-piece tube; `PCM1864DBTR` is 2,000-piece large tape/reel. The shared DBT package, device identity and electrical tables provide direct primary evidence that R changes packing, not ADC functionality, package pinout or electrical limits. A 2,000-piece manufacturer reel is not proof of a 2,000-piece factory purchase minimum.

### Existing schematic and actual copper: PASS for unchanged integration

`fab/assembly/carrier-consigned-bom.csv` identifies Texas Instruments PCM1864DBT at U1/U2, quantity two per carrier, footprint `Package_SO:TSSOP-30_4.4x7.8mm_P0.5mm`. Both actual instances and embedded U1/U2 symbols in `native/design/03_src/recovery/first-run-r3-source/crow-carrier.kicad_sch` preserve the 30-pin mapping in TI pp10–11. Inspected functions include analog inputs 1–4/27–30, VREF6, AGND7, AVDD8, XO9/XI10, LDO11, DGND12, DVDD13, IOVDD14, 3.3 V SCKI15, LRCK16, BCK17, DOUT18, I2C SDA23/SCL24, address25 and control26. There is no variant-specific pin reassignment.

Read-only `native/source/carrier/carrier.kicad_pcb` inspection found 30 pads on each footprint, two columns of 15 with 0.5 mm pitch, local centers x=±2.8625 mm, y=−3.5…+3.5 mm, and 1.475 × 0.300 mm pads. Local pad1 is upper-left, 15 lower-left, 16 lower-right, 30 upper-right, consistent with TI's top-view numbering. Both ADCs have their corresponding analog/clock nets; supplies13/14 are3V3, SCKI15 receives the separately damped MCLK, 23/24 share I2C, 26 is grounded and25 differs for the existing addresses. This substitution requires no topology, pin, rail, clock, firmware or routing change.

TI DBT0030A (PDF page142) gives 0.5 mm pitch, 4.3–4.5 mm body width, 7.75–7.85 mm body length and 1.2 mm maximum height. Its page143 land example uses 1.500 × 0.300 mm pads and 5.800 mm column spacing; current pads are0.025 mm shorter and columns0.075 mm closer. These are pre-existing differences for the identical DBT package, not new DBTR changes. TI labels this a layout example. This narrow pass neither changes the pattern nor independently reaccepts its complete paste/mask/tolerance process.

Actual native rotations remain U1+90°/U2−90°; released consigned CPL lists U1 0°/U2 180°. Preserve both existing conventions; supplier-library pin1 orientation still requires actual factory preview. Do not normalize or rotate parts merely because tape orientation differs from tube packing.

### Dated availability: PASS as a sourcing guard, not allocation

[JLC C544855](https://jlcpcb.com/partdetail/C544855) evidence `adc-stock.json` was retrieved 2026-11-01T03:45:33.918668Z. It explicitly identifies **Texas Instruments / PCM1864DBTR / TSSOP-30**, InStock; the primary count is unknown, overseas count70, presale63. The discovery count70 may overlap the overseas pool and is not added. Published overseas70 alone exceeds four installed; presale is not counted as present stock. The response is adequate dated exact-identity design-availability evidence under part-recheck policy, not a confirmed public-PCBA allocation. Factory source eligibility, receiving date, packaging/attrition, MSL handling, acceptable actual reflow profile and pin1 preview remain open.

JLC response SHA256 recorded by helper: `dd43deffa7363a9a0e242080ff3ca1f877758333680a722e3a8aecb2d902f158`. Saved JSON file SHA256: `068e0f088aee2be0e4da8ba91358572ecd12351282b8349c3df983c291000fb1`. I did not perform another broad search because the supplied fresh exact supplier evidence and primary packing table clear this bounded question.

## Adoption boundary and affected checks

Coordinator may adopt **Texas Instruments PCM1864DBTR / C544855** only in the explicitly authorized working source and derived BOM metadata for U1/U2. Keep footprint, all pin/net functions, placement, copper, stencil and firmware unchanged. Start the new exact-MPN/four-piece quantity subject's sourcing record with this dated evidence; update only affected identity/dossier/population/schematic/BOM consistency and journal references. Verify a semantic before/after diff shows only intended maker/MPN/value/supplier metadata changes. Preserve prior receipts as history rather than transferring whole-board acceptance to a new subject.

No whole-board restart is justified by this manufacturer-documented packing-only difference. Nevertheless downstream release, manufacturing artifacts, factory matching/preview, quote and order remain **HOLD / not admitted by this report** until their existing coordinator-owned checks are completed. The frozen release itself remains unchanged.

Evidence read: `/home/mouse9911/gits/circuits-crow-stock-substitutions-20261101/projects/crow-array/order-readiness/substitutions-20261101/evidence/{pcm1864.pdf,adc-stock.json}`. Local independently generated inspection aids: `adc-ti.txt`, `adc-drawing-142.png`, `adc-land-143.png` alongside this review.
