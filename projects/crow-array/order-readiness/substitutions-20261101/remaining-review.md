# Crow remaining-parts independent review — 31 October 2026 (Los Angeles)

Recommendation: retain all three exact originals. Adequate public distributor stock was independently found for each identity; no replacement currently simplifies the build enough to justify reopening its engineering. This resolves public sourcing feasibility, not JLC allocation or manufacturing acceptance. No CAD, BOM, CPL, quote or account changes; no vendor contact, reservation or purchase.

Reviewed the find-substitute-part skill and vNext part-recheck procedure. Scope is two assembled carriers and eight assembled pods, not the release's historical five/ten procurement quantities. Installed need: fuse `8 × 2 + 1 × 8 = 24`; oscillator `1 × 2 = 2`; RECOM `1 × 2 = 2`. No spare/attrition allowance is inferred.

## Shortlist and route

All observations below were retrieved 2026-11-01 UTC, corresponding to the evening of 2026-10-31 PDT. Public inventory is unreserved and has no guaranteed update/warehouse-ready date.

| Exact original / installed need | Recommended source and present-stock evidence | Impact class | Remaining boundary |
| --- | --- | --- | --- |
| Littelfuse `1206L010/30WR`, 1206 / 24 | [DigiKey](https://www.digikey.com/en/products/detail/littelfuse-inc/1206L010-30WR/6346986), `18-1206L010/30WRCT-ND`, **45,522** publicly in stock; cut tape minimum tier 1. JLC [C2153988](https://jlcpcb.com/partdetail/C2153988) exact-code recovery: InStock, primary quantity unknown, overseas 7, presale 5, separate pools. | Exact retention; distributor cut-tape fulfillment is packaging-only, not a rating change. | JLC exact global-source/consignment eligibility, per-job allocation and feeder allowance. Supplier attribute conflict noted below. |
| CTS `CB3LV-3I-12M288000`, custom 7050 four-pad / 2 | [DigiKey](https://www.digikey.com/en/products/detail/cts-frequency-controls/CB3LV-3I-12M288000/4308709), `110-CB3LV-3I-12M288000CT-ND`, **1,449** publicly in stock, cut tape tier 1. Exact JLC [C17275161](https://jlcpcb.com/partdetail/C17275161) is OutOfStock, overseas/presale 0. | Exact retention; packaging-only sourcing route. | Global-source or consignment admission; reconcile JLC Wave Soldering/manual label against CTS reflow requirements. |
| RECOM Power `R-78E5.0-0.5`, SIP3 THT / 2 | [DigiKey](https://www.digikey.com/en/products/detail/recom-power/R-78E5-0-0-5/2834904), `945-1648-5-ND`, **32,674** publicly in stock, tube tier 1; separate factory pool 966 is not added. Exact JLC [C5199916](https://jlcpcb.com/partdetail/C5199916) OutOfStock and not orderable. | Exact retention; no design change. | Existing Global Sourcing DigiKey offer is the simplest factory lead; actual quantity/fees/date and controlled THT installation remain unconfirmed. |

Illustrative direct DigiKey installed-only component lines, excluding fees/shipping/tax: fuse 24 × $0.562 = $13.488; clock 2 × $1.66 = $3.32; RECOM 2 × $3.76 = $7.52. These are public price-tier arithmetic, not quotes or JLC landed prices. Cut tape may need different preparation for factory handling; manufacturer reel size is not the distributor MOQ.

The supplied browser report at `origin/codex/crow-jlc-source-review-20261030:projects/crow-array/order-readiness/JLC-R5-EXACT-MATCH-20261031.md` separately records the exact RECOM DigiKey Global Sourcing screen: MOQ 1, tube, two pieces $9.69 extended and estimated 8–14 business days. Prefer this informational lead over the Sager ten-piece/MOQ-10 offer. This independent pass did not re-open that account screen; its terms are attributed to that report, not claimed as newly verified allocation. Public direct pricing above is a different offer and does not replace Global Sourcing terms.

Fallback for all three: authorized exact-part distributor sourcing followed by JLC-approved consignment, or the already controlled post-factory installation route if the coordinator explicitly chooses it. No need to qualify a new electrical identity merely because JLC public stock is short.

## Engineering basis and bounded alternatives

### PTC: do not adopt the 60 V variant on voltage rating alone

The [Littelfuse primary datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5), revision 2024-02-26, gives both parts 0.10 A hold, 0.25 A trip, 1.5 Ω initial minimum, 10 Ω post-trip maximum and 1.5 s maximum trip at 0.5 A. `/30` has 40 A maximum fault current; `/60` has only 10 A. Both share planar dimensions; maximum thickness changes 1.10 to 1.25 mm. Hold-current temperature guidance is similar but not identical at cold temperatures. `WR` means 3,000-piece tape/reel; `/60` is an electrical rating, not packaging.

One alternative screened: `1206L010/60WR`, [JLC C2153714](https://jlcpcb.com/partdetail/C2153714), same-footprint candidate **not qualified/recommended**. Fresh direct response gives InStock quantity unknown, overseas 2,315 and presale 2,016 separately. It is not a demonstrated factory allocation.

Actual released carrier netlist shows jack J1 → 1 A `0451001.MRL` F1 → D3 → `/12V`, with C1/C2 on `/12V` and F101–F108 feeding external port power; pod F1 protects incoming port power before local buzzer/LDO loads. A 1 A fuse is not a 1 A instantaneous current limiter, and capacitors lie downstream of that fuse. No exact adapter/source fault limit was established. The tempting nominal bound 12 V / 1.5 Ω = 8 A is only a room-condition estimate, not proof across source tolerance, transients and cold/aged PTC resistance. Thus neither a made-up adapter limit nor F1's nameplate closes the 10 A qualification. Retaining `/30WR` avoids this new source/protection review.

DigiKey's exact `/30WR` attribute table contradicts the manufacturer sheet by listing 10 A and automotive qualification. Its linked datasheet is the same primary sheet above, which says 40 A for `/30`. Use the manufacturer's rating for this comparison; retain incoming exact-MPN/revision traceability and reconcile the catalog discrepancy before relying on the supplier's parametric data. This is not evidence that the two ratings are interchangeable.

### Clock: retain the qualified exact CTS

Released X1 has pin 1 OE tied high with pin 4 on 3.3 V; pin 2 ground; pin 3 → 68 Ω R3 → separate 56 Ω R4/R5 → U1/U2 SCKI pin 15. The released review identifies a conditional 27.323 pF load model against the CTS 30 pF screen; it explicitly does not turn the 8 ns/15 pF limit into an 8 ns/30 pF guarantee. A generic 12.288 MHz oscillator is therefore not automatically equivalent. No different clock was screened after exact stock cleared.

[CTS revision K](https://www.ctscorp.com/Files/DataSheets/Passives/FCP/Clock-Oscillators/clock-ocillators-CB3_CB3LV-datasheet.pdf) decodes LV/3/I as 3.3 V/±50 ppm/−40…85°C and lists this frequency and pinout. Its SMD reflow limit is 260°C for 20 s, MSL1. CTS explicitly allows distributor `-T`/`-1` packaging suffixes, but none is needed for the exact DigiKey lead. JLC's Wave Soldering label remains a process/cost question, not a redesign reason or permission to apply an unreviewed process.

### Regulator: preserve RECOM identity and startup basis

Released U10 pin 1 consumes protected `/12V`; pin 3 supplies `/5V`, then D2 feeds Pico VSYS. [RECOM R-78E datasheet, revision 9/2025](https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf) specifies 7–28 V input for 5 V/0.5 A, SIP3 11.6 × 8.5 × 10.4 mm, pin order input/ground/output and 220 µF maximum capacitive load.

One genuine alternate screened: `R-78K5.0-0.5`, same-footprint candidate, not qualified or stock-searched further because exact stock clears the need. Its [RECOM revision 5/2025 sheet](https://recom-power.com/pdf/Innoline/R-78K-0.5.pdf) changes input/UVLO behavior, ripple, switching frequency and input-slew/hot-plug requirements; it is not proven startup-equivalent into the Pico/diode load. Qualifying it would reopen power/startup/USB-isolation, package/assembly and associated prototype checks without solving a demonstrated exact-part shortage.

The JLC `C18212367` YLPTEC same-text MPN is **rejected as exact-match evidence**, not accepted as a substitute. No independent YLPTEC qualification was attempted. This is a second screened alternative, below the three-candidate bound.

Lifecycle distinction: CTS and RECOM primary websites currently retain their series pages and datasheets; DigiKey labels these originals Active. JLC C5199916 nevertheless says no longer manufactured, a supplier/manufacturer conflict not resolved by a current web page. No primary EOL notice was established. Keep that lifecycle issue separate from the adequate existing exact stock; do not claim manufacturer-confirmed active production or a new-design lifecycle qualification.

## Handoff and evidence

Public sourcing guard: adequate dated exact supplier evidence for all three current build totals. Coordinator may record the new two/eight quantity subjects as sourcing-checked, preserving these observations and lifecycle caveat; this report itself changes no acceptance state. Factory allocation: **open for all three**. Do not combine the fuse's seven-piece pool with Global Sourcing unless JLC confirms a permissible route, or count it twice across jobs. Actual attrition, packaging, warehouse date, handling, cost and factory eligibility remain open. No engineering substitution is recommended.

Board evidence reopened: released `fab/assembly/carrier-consigned-bom.csv`, `pod-consigned-bom.csv`, `population.csv`; `native/design/06_build/recovery/first-run-r3-native/{carrier,pod}/native.xml`; `verification/reviews/2026-10-22-first-run-schematic-costscope.md`; and carrier process `56-2026-10-22-first-run-r3-qualification.md`. Release root: `/home/mouse9911/gits/circuits-publish-vnext-crow-v3-20261025/projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1`.

Saved direct JLC structured evidence: `jlc-fuse-recovery.json`, `jlc-clock-structured.json`, `jlc-regulator-structured.json`, `jlc-fuse-alt.json`, each with HTTP retrieval time and hash. Initial `.json`-named files without `-structured`/`-recovery`/`-alt` are text-format helper outputs, retained as attempts, not parseable JSON. `external-*.json` similarly retain text-format failed HTTP403 attempts; these failures are not zero stock. Browser page review recovered adequate exact product offers independently; values and URLs are in `browser-observations.json`. Downloaded maker PDFs and extracted text for CTS/RECOM accompany this report; direct Littelfuse download received403, while the browsing tool successfully opened the primary linked PDF today. No anti-bot retry or bypass was performed.
