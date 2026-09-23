# Crow sourcing exception disposition — 2026-09-23

Dated observations only: stock may already be stale. M-IMPORT grade CITED public catalog/API/product-page evidence; no reservation, assembly acceptance or purchasing authority. The earlier report filename2026-09-22 used local date; its fetch times were2026-09-23UTC. This review uses UTC.

## Measured result

The direct JLC checker covered84/84codes for5boards plus the configured150unit buffer:70pass,14fail. Nine fail actual build demand; five fail only the buffer. No missing-code or network-error rows. Distributor observations identify an exact-part alternative above the numerical threshold for each14line, but do not establish JLC consignment acceptance or constitute a manufacturing-readiness receipt.

| Exact MPN | JLC stock | Build | Build+150 | Alternate stock/source | Observation |
|---|---:|---:|---:|---|---|
| ASFL1-24.576MHZ-EC-T | 86 | 5 | 155 | [digikey: 4530](https://www.digikey.com/en/products/detail/abracon-llc/ASFL1-24-576MHZ-EC-T/687864) | 2026-09-23 page read |
| 744373240047 | 0 | 15 | 165 | [digikey: 3227](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/744373240047/2791039) | 2026-09-23 page read |
| TPS389018DSER | 0 | 10 | 160 | [digikey: 3099](https://www.digikey.com/en/products/detail/texas-instruments/TPS389018DSER/6123508) | 2026-09-23 page read |
| TPS389030DSER | 58 | 15 | 165 | [digikey: 2262](https://www.digikey.com/en/products/detail/texas-instruments/TPS389030DSER/6123510) | 2026-09-23 page read |
| TPS6282518DMQR | 51 | 5 | 155 | [digikey: 6192](https://www.digikey.com/en/products/detail/texas-instruments/TPS6282518DMQR/9428258) | 2026-09-23 page read |
| CKG57KX7R1E476M335JH | 0 | 65 | 215 | [digikey: 5652](https://www.digikey.com/en/products/detail/tdk-corporation/CKG57KX7R1E476M335JH/6236783) | 2026-09-23 page read |
| FA-238 24.0000MD30X-W5 | 0 | 5 | 155 | [digikey: 39505](https://www.digikey.com/en/products/detail/epson/FA-238-24-0000MD30X-W5/5259755) | 2026-09-23 page read |
| OPA2320AID | 13 | 40 | 190 | [digikey: 448](https://www.digikey.com/en/products/detail/texas-instruments/OPA2320AID/2833369) | 2026-09-23 page read |
| TPS6282533DMQR | 44 | 5 | 155 | [digikey: 3120](https://www.digikey.com/en/products/detail/texas-instruments/TPS6282533DMQR/15212775) | 2026-09-23 page read |
| R82DC4100CK60J | 6 | 80 | 230 | [digikey: 969](https://www.digikey.com/en/products/detail/kemet/R82DC4100CK60J/21776592) | 2026-09-23 page read |
| TPSM63603V5RDHR | 0 | 5 | 155 | [mouser: 1816](https://www.mouser.com/ProductDetail/Texas-Instruments/TPSM63603V5RDHR) | 2026-09-23 API |
| TMUX2821DSGR | 16 | 40 | 190 | [digikey: 2449](https://www.digikey.com/en/products/detail/texas-instruments/TMUX2821DSGR/28738833) | 2026-09-23 page read |
| XU316-1024-TQ128-C24 | 46 | 5 | 155 | [digikey: 589](https://www.digikey.com/en/products/detail/xmos/XU316-1024-TQ128-C24/17764326) | 2026-09-23 page read |
| 615008160221 | 0 | 40 | 190 | [digikey: 991](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/615008160221/11627337) | 2026-09-22 retained page |

## Dispositions

Six resistor exceptions clear fresh direct-JLC stock; no replacement is indicated. Molex explicitly cross-identifies436500200/43650-0200/0436500200 on its [manufacturer page](https://www.molex.com/en-us/products/part-detail/436500200). DirectJLC C192562 has3881units: naming discrepancy resolved without changing MPN or matching rules.

SN74LVC1G125DCKT has186JLC units against165threshold, but refreshed DigiKey shows5 and Mouser API has null availability. It currently has only one observed qualifying pool. Historical85/85two-pool qualification is not current proof.

DigiKey page fetch times are not warehouse timestamps; some retrieval-service pages were cached days earlier. Raw HTML was unavailable for those reads. Mouser API raw responses retain timestamps/hashes. Distributor stock cannot prove JLC allocation, consignment acceptance or costs. Separate ADC assembler and LT3045process qualification remain open.

## Proposed design-only continuation — not adopted

Retain all selected parts. Use direct public catalog plus named exact-MPN distributor observations to continue pre-layout design, explicitly accepting source-pool, observation-freshness and provider-fulfillment risks. Keep the sourcing/assembly hold before manufacturing. DO-NOT-ORDER: no spending or procurement-limit changes.

This needs an explicit project decision before replacing the current provider checkpoint. Existing distributor-prelayout code supports DigiKey records; TPSM63603V5RDHR requires genuine Mouser-evidence support or a named unresolved-risk disposition. Never relabel Mouser as DigiKey, lower the buffer silently, or fill PCBA response fields with catalog numbers. Formal schematic review and process-dependent layout gates still apply.

## Evidence

Direct checker `06_build/sourcing/direct-check-20260923.json`: generated 2026-09-23T02:10:44.238329+00:00, SHA256 `94b033d3633dde690ec43741ded2a7b74f6260eb2eb4ad97394d0ec85ac800d3`. Exact84code set reopened against current request. Input refdes/MPNs came from canonical Circuit JSON, not the historical exact-parts.csv that predates the CKG selection.

SOL active/passive and Terra connector reports plus raw local evidence are retained in `06_build/verification/sourcing-exceptions-20260923/`. No component, schematic, footprint or gate was changed.
