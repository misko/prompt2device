# JLC r9 selection and quote follow-up — 2026-11-01

Quote-only browser session. Scope: five fabricated / two assembled carriers and ten fabricated / eight assembled pods. Factory BOM keeps all r9 factory parts; carrier clock X1 and the other r9 HOME parts remain for home installation. No new substitutions, purchases, reservations, vendor messages or manufacturing commitments.

## Result

The earlier duplicate-code selection warnings were bypassed by merging only rows with identical code, manufacturer, MPN, footprint, assembly route and supply route. The first merged uploads revealed a further issue: the carrier table and placement list did not display the eight C1711 references even while saying 23/23 confirmed; the first pod upload's table did not display R6 even while saying 20/20. The reason is unknown. After changing the affected row comment and order, the v2 carrier and pod uploads showed every expected group and reference in both the BOM and the placement list, respectively 23 and 20 groups. R5/R9/R10 are grouped under exact C844747; R6 is C844779. Both proceeded to preview without the earlier selection warning. See [candidate files and hashes](quote-draft/r9-merged-bom-candidates/README.md). Do not use the first candidates.

[Carrier draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=5e6ccfa5ec0b4bac8f06c7b79760b061) and [pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97) are account-specific, automatically saved quote drafts.

| Displayed charge, USD | Carrier | Pod |
| --- | ---: | ---: |
| PCB | 67.93 | 42.24 |
| Standard PCBA | 161.18 | 119.74 |
| Total | 229.11 | 161.98 |

Combined displayed total: **$391.09** before shipping, tax, HOME parts or further adjustments. These are draft estimates, not an order or complete delivered quote. Both displayed PCB 3 days plus assembly 5–6 days; no committed usable-stock arrival or delivery date was provided. Carrier PCB: engineering 25.00, finish 19.10, board 13.60, outline tolerance 9.18, production-file confirmation 1.05. Pod PCB: special offer 14.00, finish 18.30, outline tolerance 8.89, production-file confirmation 1.05. Via covering was 0.00 for both.

| PCBA item, USD | Carrier | Pod |
| --- | ---: | ---: |
| Setup | 25.75 | 25.75 |
| Stencil | 8.27 | 8.27 |
| Components | 72.75 | 32.77 |
| Feeder loading | 31.00 | 29.45 |
| SMT assembly | 1.61 | 1.40 |
| Placement confirmation | 0.45 | 0.45 |
| Hand solder labor | 3.61 | 3.61 |
| Manual assembly | 2.31 | 1.06 |
| Handling | 14.92 | 16.47 |
| Packaging | 0.51 | 0.51 |

Panel and large-size charges were zero. Rounded lines may not independently sum exactly to JLC totals.

## Remaining holds

- The preview lists are populated; full independent per-part position, rotation, polarity, package and first-article review has not been completed. The pod 3D preview was visually opened; that is not signoff. Confirm all factory THT/manual operations and the physical orientation of critical parts with JLC before any production approval.
- The carrier quote currently uses stackup **No Requirement**, not the intended 7628A requirement; the existing stack/tolerance hold is unresolved and the price is not a quote for a confirmed compliant stack. Preserve the existing rail, process and release holds. The pod used 7628.
- Stock is not reserved and may change. Confirm quantities/attrition and actual assembly acceptance, plus shipping/tax and the exact home-install parts and cost. The quote includes manual and hand-solder charges, but does not independently prove all required manual work will be accepted.
- JLC may reinterpret uploads; recheck the complete actual displayed references and preview, not only the 23/23 or 20/20 counter, before further action. The original r9 source files are unchanged. No placement or production approval was given.
