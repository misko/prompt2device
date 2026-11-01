# Crow r6 — reviewed substitutions, quote-only

**Not production/order approval. No purchases authorized.** This derivative
replaces four part identities in the working schematic/PCB metadata and BOM,
while preserving all footprints, pin mappings, placements, tracks, vias, zones,
outline, Gerbers and CPL bytes. The old release and r5 remain unchanged.
Existing release receipts do not automatically accept this new BOM revision.

Scope: **5 fabricated / 2 assembled carriers; 10 fabricated / 8 assembled pods**.
BOMs and CPLs describe ONE board each; set assembly counts in the portal, not in
the uploaded rows. Total: 478 SMT + 28 factory THT + 18 home-installed parts.
Factory THT remains 24 RJ jacks + 2 power jacks + 2 exact RECOM modules.
Home installation remains 2 SC0915 Picos + 8 CMA-4544PF-W microphones + 8 CPE-203
buzzers. No home/factory scope was changed to make a shortage disappear.

## Adopted changes

Independent SOL 6.1 high reviews support these local changes. Availability was
checked 2026-11-01 UTC (2026-10-31 PDT). Public stock is NOT allocation.

| Original | Replacement / JLC locator | Installed need | Reason / availability |
|---|---|---:|---|
| TI PCM1864DBT | TI PCM1864DBTR / C544855 | 4 | Same device and DBT30 package; reel instead of tube. Exact public InStock; count unknown. Aggregate/overseas 70 and presale 63 are separate observations, not additive stock. |
| Murata GRM21BR71A105KA01L | Samsung CL21B105KBFNNNE / C28323 | 12 | 1 µF, 50 V, ±10%, X7R, 0805; reference/coupling roles reviewed. Exact public InStock, count unknown. |
| TDK C2012X7R1V225K125AE | Samsung CL21B225KBYVPNE / C5362585 | 8 | 2.2 µF, 50 V, ±10%, X7R, 0805; protected-input bypass reviewed. Exact public InStock, count unknown. |
| TDK C3216X7R1V106K160AC | Samsung CL31B106KBHNNNE / C89632 | 4 | 10 µF, 50 V, ±10%, X7R, 1206; optional protected-input bypass reviewed. Exact public InStock, count unknown. |

The 10 µF replacement is approximately 4.65 µF at 12 V on the maker's typical
curve, NOT 10 µF effective. This was reviewed against its actual optional-input
bypass role; no hold-up or regulator-output stability minimum is being waived.
Samsung recommended lands differ slightly from retained IPC lands; reviewed
terminal overlap/body envelopes support retention. Factory paste/placement and
first-article joint checks remain. No claim of measured prototype performance.

## Retain these exact parts; change the sourcing route

| Exact identity | Installed need | Dated DigiKey public count | Preferred next route |
|---|---:|---:|---|
| Littelfuse 1206L010/30WR | 24 | 45,522 | Exact Global Sourcing offer; approved consignment fallback |
| CTS CB3LV-3I-12M288000 | 2 | 1,449 | Exact Global Sourcing; retain CTS-compatible reflow handling |
| RECOM R-78E5.0-0.5 | 2 | 32,674 | Recheck existing exact DigiKey Global Sourcing lead; consignment fallback |

Exact URLs are in `procurement-plan.csv`. External stock is not JLC warehouse
stock or an assembly agreement. Public clock/fuse codes remain locators in that
plan, but their BOM C-code cells are blank for separate exact Global/consignment
matching; never fabricate a private inventory ID. Blank code does NOT mean DNP.
The original RECOM two-for-$9.69 / 8–14-business-day account observation is a
historical lead, not a refreshed quote. Final prices, fees, attrition and dates
remain unknown. Do not add the fuse's public seven-piece pool to another source
or count that pool independently for each job.

The alternative 60 V fuse has only a 10 A fault rating versus the original
maker's 40 A rating. An upstream 1 A fuse is not an instantaneous current limiter;
without a bounded source fault current, that replacement is not adopted. Do not
use a 5 V clock or YLPTEC's same-text regulator MPN. The distributor's fuse-rating
attribute and JLC's RECOM lifecycle claim conflict with other evidence; retain
exact maker traceability and do not use those attributes as electrical authority.

## MacBook checklist — information only

1. Use only this revision's `carrier-bom.csv` + `carrier-cpl.csv` together and
   `pod-bom.csv` + `pod-cpl.csv` together. Gerber ZIPs are byte-identical to r5.
   If working in saved drafts, record the revision and verify every changed row.
2. Match the FOUR new identities above by exact maker/MPN/C-code. Check usable
   stock for both jobs and gross demand including JLC's actual allowances.
   An InStock public page does not guarantee selection in the account draft.
3. Check exact Global Sourcing offers for all THREE retained identities. Capture
   installed versus purchase quantity, MOQ/multiples, feeder/attrition, source
   pool, fees, currency, usable warehouse date and assembly eligibility. If the
   portal requires purchase or non-cancelable pre-order to proceed, STOP and
   report the missing quote information. Do not acquire or reserve inventory.
4. Keep all required parts populated. Do not use "Do not place" to bypass
   shortages. Reject wrong-maker matches. Obtain complete placement previews;
   recheck ADC pin1/orientation and capacitor exact-library mapping. CPL angles
   are intentionally unchanged; do not normalize them to native PCB angles.
5. Preserve ENIG, carrier JLC04161H-7628A and pod JLC04161H-7628 intent, precision
   outline, special mask/paste controls and manual THT process requirements.
   Carrier 1.5542 mm ±10% portal acknowledgement is still unresolved. Pod two
   5 mm rails/no-depanel configuration needs review; no mechanical waiver here.
   Keep production-file/placement reviews and "Do not confirm automatically".
6. Record itemized boards, components, SMT/THT labor, setup/stencil, sourcing,
   shipping/taxes and remaining unknowns. Do not approve previews/production,
   send vendor messages, pay or order under this handoff.

## Source and validation

The accompanying `native/` contains revised schematic/library and PCB metadata;
these are working sources, not a newly sealed release. Review records, retained
manufacturer evidence, fresh stock snapshots, adopted change map and regenerated
schematic PDFs/ERC/DRC live in `order-readiness/substitutions-20261101/` in the
repository. `manifest.json` binds the exact inputs and generated package files.
Use `substitute_quote.py verify` with the adopted change map to replay the package.
The generator proves a byte-exact inverse of only specified property strings;
KiCad/netlist checks separately test the resulting sources. Neither is a vendor
placement approval, physical qualification or purchasing authorization.
