# Independent capacitor substitute qualification

Review: 2026-10-31 America/Los_Angeles (source retrieval 2026-11-01 03:44–03:50 UTC). Scope: two carriers and eight pods; no purchasing, allocation, CAD, release, BOM/CPL or quote changes performed. One proposed candidate screened per original, within the maximum-three bound.

## Disposition

All three **CAN be adopted for this existing prototype application (local engineering PASS)**, as same-footprint candidates with the limited downstream rechecks below. This is engineering qualification of the substitutions, not whole-board acceptance, a PCBA reservation or order approval. No capacitor needs an engineering HOLD on the evidence inspected. Do not interpret this as establishing guaranteed biased capacitance, lifetime, EMI compliance or measured rail performance.

| Original | Installed build need | Exact replacement | Sourcing | Application disposition |
|---|---:|---|---|---|
| Murata GRM21BR71A105KA01L | carrier C11/C21: 2 × 2 = 4; pod C3: 1 × 8 = 8; total 12 | Samsung CL21B105KBFNNNE, C28323 | Exact JLC InStock, count unknown | CAN adopt: 1 µF reference bypass / microphone coupling |
| TDK C2012X7R1V225K125AE | pod C1: 1 × 8 = 8 | Samsung CL21B225KBYVPNE, C5362585 | Exact JLC InStock, count unknown | CAN adopt: protected-input bypass; not LDO output capacitor |
| TDK C3216X7R1V106K160AC | carrier C1/C2: 2 × 2 = 4 | Samsung CL31B106KBHNNNE, C89632 | Exact JLC InStock, count unknown | CAN adopt: protected-input local/bulk bypass; not converter output capacitor |

No attrition or spares assumed. Public supplier pages: [C28323](https://jlcpcb.com/partdetail/C28323), [C5362585](https://jlcpcb.com/partdetail/C5362585), [C89632](https://jlcpcb.com/partdetail/C89632). The read-only helper's exact-identity JSON observations are retained beside this review. All show supplier structured `InStock`, matching maker, full MPN and package, no conflicting availability, and an unpublished public stock count. Per part-recheck policy that suffices for design availability; numeric allocation remains unknown. Overseas/presale are separate: respectively 2,355,002/1,410,348; 10,584/10,051; 80,958/23,802. These are NOT added, called public PCBA stock, or promised available to this order. No need for a distributor fallback to clear this design-availability check. Exact original through consignment remains a fallback, not an instructed purchase.

## Circuit basis and capacitance judgment

I inspected the release's native exported netlists (`native/design/06_build/recovery/first-run-r3-native/{carrier,pod}/native.xml`), source schematics (`native/design/03_src/recovery/first-run-r3-source/crow-{carrier,pod}.kicad_sch`), and the actual final PCB instances (`native/source/{carrier,pod}/{carrier,pod}.kicad_pcb`). `analysis-results.json` contains a fresh parser extraction of all six affected board positions and manufacturer-curve interpolations. Baseline path:

`/home/mouse9911/gits/circuits-publish-vnext-crow-v3-20261025/projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1`

### 1 µF: reference bypass and microphone coupling

Carrier C11/C21 are `/REF1` and `/REF2` to ground, each directly at PCM1864 pin 6, not input-rail decoupling. TI's PCM1864 pin-function table specifies a **nominal 1 µF** VREF-to-AGND capacitor and states VREF is normally half AVDD (the retained local-rail envelope is 3.0–3.6 V, hence approximately 1.5–1.8 V bias). The separate application drawing uses 2.2 µF; it does not turn the pin-table's 1 µF into an effective-capacitance minimum. [TI PCM1864](https://www.ti.com/lit/ds/symlink/pcm1864.pdf), downloaded here, p.11/p.72.

Pod C3 is `/MIC_NODE` to `/MIC_AC`; R1 is 2.2 kΩ microphone bias from 3V3, R2 is 100 kΩ to VMID, and U2A is TLV9062's noninverting input. C3 blocks DC; it never carries protected 12 V. Using the whole 3.6 V rail as an intentionally generous bias screen covers the normal microphone-to-midrail offset. The candidate is about 1.009 µF at 1.65 V, 0.995 µF at 3.6 V on Samsung's typical curve. Multiplying by 0.9 tolerance and 0.85 X7R temperature allowance gives illustrative 0.772/0.761 µF screens, not guaranteed combined minima. With R2's 99 kΩ lower tolerance, 0.761 µF has a roughly 2.1 Hz high-pass scale even omitting additional source/VMID impedance. This is a circuit implication, not a newly imposed audio-band requirement. It preserves the existing ordinary 1 µF coupling function and 1 µF nominal VREF bypass. There is no basis to demand the exact old Murata bias curve.

Samsung's exact E-packaging listing is current Mass Production; nominal 1 µF, ±10%, X7R, 50 V, 2.00×1.25×1.25 mm with ±0.10 mm dimensions. Original is 1 µF/10 V/X7R/±10% in the same nominal body; no loss of voltage, tolerance or temperature capability. [Samsung current product and curves](https://product.samsungsem.com/mlcc/CL21B105KBFNNN.do); exact reference specification downloaded via the manufacturer's `/part/download.do` with `masterKey=CL21B105KBFNNN&type=specsheet` (May 9, 2024).

### 2.2 µF: pod protected 12 V input

Native pod C1 connects `/12V` to GND after F1, alongside D1 and TPS70933 input, also supplying the buzzer branch. It is NOT pod C2, the TPS709 output/stability capacitor. TI explicitly says an input capacitor is not required for stability and recommends 0.1–2.2 µF for input reactive-source/transient/noise improvement; the 1.5 µF effective minimum and ESR constraint apply to the OUTPUT. [TI TPS709](https://www.ti.com/lit/ds/symlink/tps709.pdf), downloaded here, §8.1.1.

Candidate typical effective C is 1.995 µF at the retained modeled 7.75 V lower pod bus and 1.738 µF at 12 V. The same tolerance/temperature sensitivity is 1.526/1.330 µF; 13.2 V (a sensitivity, not a newly asserted supply requirement) gives 1.267 µF. This is ample ordinary local input bypass in the maker's recommended scale, without inventing an exact 2.2 µF-effective requirement. Buzzer-edge rail behavior remains subject to the existing prototype loaded-rail falsifier, not assumed solved by a capacitor's rating.

Samsung listing is Mass Production automotive/AEC-Q200, 2.2 µF ±10%, X7R, 50 V, 2.00×1.25×1.25 mm ±0.20 mm; metal-epoxy termination is explicitly documented. The original TDK is a soft-termination 35 V ±10% part (despite schematic value text saying 20%); candidate does not silently downgrade that to rigid termination. The Samsung reference sheet's board-flex test is 3 mm/60 s under its stated test, not a system bending guarantee. [Samsung product and curves](https://product.samsungsem.com/mlcc/CL21B225KBYVPN.do); downloaded exact reference sheet April 4, 2024; [TDK original](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1V225K125AE).

### 10 µF: carrier protected-input bypass

Both native carrier C1/C2 are `/12V` to ground, on the protected rail feeding fused pods and U10 R-78E5.0-0.5 VIN. Neither is U10's output capacitor. The exact RECOM datasheet labels external input and output 10 µF MLCCs optional in its standard application. Its EMC filter suggestions do not apply to this unfiltered rail topology and are not claimed here. There is no hold-up time, ripple-energy budget or 10 µF-effective minimum in the inspected source that depends on C1/C2. [RECOM R-78E Rev9/2025](https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf), downloaded here, p.I-3/I-4.

Important: candidate bias loss is substantial. At 12 V Samsung's curve gives only **4.646 µF each**, 9.293 µF total at DC; at 13.2 V, 4.206 µF each. The tolerance/temperature screens are 3.554 and 3.218 µF each. Spatially separated capacitors cannot simply be treated as one HF lump. Nonetheless each remains µF-scale local low-ESR input bypass and the combined rail bulk remains several µF after the stated screen, while the converter has no mandatory external-input-capacitance stability floor. Thus this specific prototype application supports adoption; 50 V is NOT claimed to mean improved effective C. Requiring an arbitrary exact match to the old TDK curve would invent a requirement. If a later input-transient/hold-up requirement is established, requalify against that requirement instead.

Samsung exact E code is Mass Production, 10 µF ±10%, X7R/50 V, 3.20×1.60×1.60 mm ±0.20 mm; source TDK is ±10%/35 V/X7R with the same dimensional tolerance (schematic value text allows 20%). [Samsung product/curves](https://product.samsungsem.com/mlcc/CL31B106KBHNNN.do); exact Samsung reference specification downloaded, September 17, 2025; [TDK original](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X7R1V106K160AC).

### Limits of curve evidence

Samsung curves are typical design references at 25 °C, 1 kHz, 1 Vrms. All three are Class II ceramics: DC/AC bias, temperature and logarithmic aging can reduce capacitance; no combined production minimum or aging lifetime is proved by these curves. Multiplication by tolerance and X7R temperature limits is a sensitivity screen, not a warranted joint bound. This is appropriate evidence for these existing nominal bypass/coupling functions, not sufficient evidence for a critical hold-up or stability minimum. No new aging/lifetime allowance is invented. Nominal/temperature/tolerance labels alone were not used for acceptance.

## Native lands, occupied envelope and assembly

All replacements are two-terminal, nonpolar SMT MLCCs. Actual 0805 pads are 1.00×1.45 mm at x=±0.95 (0.90 mm inner gap; 2.90 mm total span); actual 1206 pads are 1.15×1.80 at x=±1.475 (1.80 mm gap; 4.10 mm span). I checked the final board instances, not only library names. The documented Samsung termination lengths (1 µF and 2.2 µF: 0.2–0.7 mm; 10 µF: 0.2–0.8 mm) overlap those lands across the body dimensional range. Even the shortest 1206 body/end termination has its 0.2 mm terminal segment at x=1.3–1.5 entirely over x=0.9–2.05 copper, before placement tolerance. These are compatible same-footprint lands; no pin, rotation, routing or firmware change is indicated.

Samsung's generic recommended-land table is **not an exact match** to existing IPC nominal lands: its 2012 ±0.10 row has a smaller gap/pad width, while its 3216 ±0.20 row recommends 1.64–1.76 mm gap and 1.19–1.31 mm pad length versus existing 1.80/1.15. Its manual explicitly calls for evaluation in the actual board/process. The termination-overlap screen and existing IPC geometry support retaining these lands for this prototype; factory paste/placement and solder-joint inspection must be locally rechecked, not described as maker-identical. Samsung spec PDFs include the product manual §5.4 and recommend J-STD-020F reflow. This is not a new mandatory footprint redesign.

Max replacement body sizes are 2.10×1.35×1.35, 2.20×1.45×1.45, and 3.40×1.80×1.80 mm. They fit within retained conservative occupied envelopes of 2.50×1.50×1.65 mm for 0805 and 3.60×1.90×2.05 mm for 1206 (`historical/documentation/carrier/process/55-2026-10-22-first-run-mating-complete.md`, P007/P008/P022 rationale). No envelope expansion or new mating interference is indicated. Real solder/seat acceptance remains required; these are component-body dimensions, not guaranteed assembled heights.

JLC pages identify SMT Economic/Standard service; C28323 is Basic, the other two Extended. Catalog listing is assembly eligibility evidence, not confirmation of the final order's selection, cost, loading or lead time. All exact Samsung E suffixes are 7-inch embossed reel packaging, not new electrical variants. Current manufacturer pages explicitly list those suffixes and Mass Production; lifecycle suitability clears, separately from supplier stock. Reflow, handling/board-flex control, no-polarity inspection and ordinary thermal-stress precautions remain.

## Local adoption/recheck scope for coordinator

Adopt only after updating the owning exact-part source and current mixed-board demand. Reopen the affected schematic/BOM identity and part-recheck evidence for carrier C1/C2/C11/C21 and pod C1/C3, the local electrical review above, their footprint/occupied-model identity mapping, and affected assembly/sourcing outputs. Keep existing nets, placements, pads, routing and CPL rotations; verify parity and regenerate/review the affected BOM/assembly evidence rather than transferring old hashes. Re-evaluate assembly preview/paste/part mapping with the factory and inspect first-article joints at these lands. Preserve original sealed history.

Existing first-article checks should cover loaded protected-12V/3V3 startup and buzzer transients, converter operation, reference settling/noise and microphone low-frequency response. These are retained empirical falsifiers, not claims that physical hardware has already been tested. No whole-board architecture restart, firmware change, certified EMI claim, stock reservation, vendor contact or purchase is authorized by this review.

## Retained evidence / reproducibility

- `stock-C28323.json`, `stock-C5362585.json`, `stock-C89632.json`: fresh exact JLC observations, retrieval times and response hashes.
- `CL21B105KBFNNN.html`, `CL21B225KBYVPN.html`, `CL31B106KBHNNN.html`: current manufacturer pages including full numeric typical curves and E-code/lifecycle listing.
- `CL21B105KBFNNN-spec.pdf`, `CL21B225KBYVPN-spec.pdf`, `CL31B106KBHNNN-spec.pdf`: exact maker reference sheets plus product manuals downloaded using the manufacturer's own form endpoint, POST `masterKey=<family>&type=specsheet`; corresponding `.txt` extracts.
- `pcm1864.pdf`, `tps709.pdf`, `R-78E-0.5.pdf`: primary circuit-device data sheets; corresponding `.txt` extracts.
- `analyze.cjs`, `analysis-results.json`: curve interpolation and actual PCB-instance pad/net extraction. Run `node /tmp/crow-cap-review-OSRijwkC/analyze.cjs` to reproduce (read-only stdout).
- `SHA256SUMS`: hashes of retained manufacturer HTML (including numeric DC-bias observations), manufacturer PDFs, stock JSON, and analysis code/result.
- Retrieval limitations: Murata product page and direct TDK PDF/page downloads returned 403/timeouts; original baseline dimensions/ratings are corroborated by the native exact identities and accessible primary TDK product descriptions. Samsung full source and exact sheets were fetched successfully. No failed lookup was treated as zero inventory or as an electrical failure.
