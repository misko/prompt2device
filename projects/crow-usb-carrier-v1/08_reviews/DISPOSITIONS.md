# Review dispositions

| Review | Finding | Disposition | Evidence boundary |
|---|---|---|---|
| [USB source contract, SOL](2026-09-22_usb-contract_sol_decision.md) | Initial ADR reference did not adopt skew/layer/via policy. | Closed by accepted ADR0008 and exact reviewed full route/nets snapshots. | Source decision only; no native routing, impedance, return-path or physical acceptance. |
| [Source schema normalization, SOL](2026-09-22_schema-normalization_sol_source.md) | 43 orphan key shapes and five stale reader claims. | Closed by evidence-preserving normalization; executable limits retained and five unread locator claims marked OWED. | Source-schema governance only; does not qualify physical implementation. |
| [USB/ADC capacitors, SOL](2026-09-22_gcm-capacitor_sol_source.md) | Initial GCM VMID estimate below shown2.2uF. | VMID uses existing qualified KEMET10uF; five separate per-pin banks pass. | Source estimate and selection; native geometry and first-article performance remain owed. |
| [ADC F2 authority, SOL](2026-09-22_adc-f2_sol_source.md) | New hardware-mode clock phase requirement and dual-function pin labels. | F2 current authority, historical F1 retained; labels updated with unchanged pin states; phase proof assigned to clock configuration, buffer/route timing and measurement. | Source acceptance only; actual clock-phase verification remains owed. |
| [493-reference previews, SOL](2026-09-22_source-pages-40_sol_source.md) | Changed capacitor banks and F2 labels need visual review. | ACCEPT40pages/493unique; no clipping/collision/partition findings. | Source previews only, not native schematic acceptance. |
| [Integrated CKG bank, SOL](2026-09-22_ckg-bank_sol_source.md) | Native footprint, source census and arithmetic require final review. | ACCEPTexact051246af source;13caps, corrected margins, explicit conditional stability/ESL obligations. | Does not approve board realization or manufacturing. |
