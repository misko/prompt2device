# Selected BOM sourcing observation — 2026-09-22

The owning shopping-list gate grades the current 85 exact MPNs / 489 references for five boards. Its result is **FAIL: 41/85 have two qualifying distributor pools, 34/85 have one, and 10/85 have none; zero inputs are unparseable**. See [machine report](shopping-list-2026-09-22.json) and [generated list](shopping-list-2026-09-22.md).

The source identity matches commit f788f245 (electrical source unchanged since d048c010). The isolated fixture contains only the 85 selected dossiers, excluding unused historical dossiers. Root reran the owning tool using the current main script and reproduced its coverage. The committed report is an observation, not stock allocation or permission to purchase.

The mutable manual quote input now retains 78 deduplicated records: 75 DigiKey and three Mouser. Newer negative observations supersede older positives. Ten DigiKey parts have observed zero stock; ten other rows lack direct observations. Missing evidence has not been converted to zero stock. The two accepted Mouser records transcribe explicit immediate-shipment notes already present in the original ADC and film-capacitor observations; no new page read is claimed for those entries.

Known-code JLC evidence qualifies 50/85 rows, DigiKey 65/85, and Mouser 2/85. This snapshot excludes subsequent nine-row DigiKey evidence and proposed additional LCSC codes, which require a separate integration and grade. The obsolete BKH1005LM601-T PLL bead remains a source backtrack. Its candidate replacement has not yet passed the retained-primary and sourcing checks. Commission admission remains incomplete.

Reproduction artifacts are under `06_build/verification/sourcing-consolidated/`; the frozen selected-dossier fixture is `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/quotes_consolidated_d048c010/project`. All availability figures are dated observations and must be reread before ordering.
