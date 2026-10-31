# JLC browser availability — 2026-10-30 PDT

One complete read-only Mac Chrome pass for **five carriers and ten pods**.
Observed 17:30–17:36 PDT (2026-10-31 00:30–00:36 UTC). **26 exact identities
have sufficient displayed available-to-order quantity, seven have insufficient
or zero JLC stock, and two stocked candidates require identity reconciliation.**
All 35 requested identities were covered. No failed or missing catalog lookup
remains in this pass. This is supplier inventory evidence, not allocation,
engineering acceptance, an approved upload BOM, or permission to order.

The selected split remains 915 JLC SMT placements plus 60 requested JLC
connector/regulator installations. User installs 20 acoustic parts and five
original SC0915 Picos, outside JLC paste/placement scope with applicable holes
open. Protected acoustic handling and D1-only Pico instructions remain binding.
No substitutions, uploads, cart/library additions, supplier messages, reservations,
orders, or purchases were made. No Pico-fit research was reopened.

## Exceptions

“Stock” below is JLC's displayed In Stock field, while “orderable” is its separate
Available Order Qty field. They are not added. Minimum quantities are catalog
observations, not adopted purchasing quantities or invented attrition.

| Exact requested identity | JLC code | Need | Browser observation | Remaining exception |
|---|---|---:|---|---|
| CTS-Frequency Controls CB3LV-3I-12M288000 | [C17275161](https://jlcpcb.com/partdetail/18404298-CB3LV_3I12M288000/C17275161) | 5 | Stock 0; minimum 4 | New exact code. Pre-order shown. SMD7050-4P is labeled Wave Soldering by JLC; reconcile catalog/process before use. |
| Murata GRM21BR71A105KA01L | [C97917](https://jlcpcb.com/partdetail/MurataElectronics-GRM21BR71A105KA01L/C97917) | 20 | Stock 0; minimum 407 | Pre-order shown; minimum 407 exceeds 20 installed need. No purchasing quantity adopted. |
| Littelfuse 1206L010/30WR | [C2153988](https://jlcpcb.com/partdetail/Littelfuse-1206L01030WR/C2153988) | 50 | Stock 2; minimum 14 | Two in stock versus 50 installed need; pre-order shown. Do not treat the positive count as adequate. |
| Panasonic Industry ERJ-3EKF68R0V | [C403329](https://jlcpcb.com/partdetail/PANASONIC-ERJ3EKF68R0V/C403329) | 5 | Stock 3,713; orderable 3,665 | JLC returned ERJ3EKF68R0V (hyphen omitted). Stock belongs to that spelling; exact identity reconciliation remains open, not a substitution. |
| RECOM Power R-78E5.0-0.5 | [C5199916](https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_05/C5199916) | 5 | Stock 0; minimum 3 | Zero JLC stock. Wave Soldering catalog eligibility does not approve the released manual process. Replenishment/consignment route and lead time unverified. |
| Same Sky PJ-102AH | [C3096093](https://jlcpcb.com/partdetail/CUI-PJ102AH/C3096093) | 5 | Stock 1,052; orderable 959 | JLC manufacturer is CUI, released manufacturer is Same Sky. Brand identity remains unresolved; positive stock is conditional on reconciliation. Wave Soldering does not establish released manual-process compatibility. |
| TDK C2012X7R1V225K125AE | [C2167593](https://jlcpcb.com/partdetail/TDK-C2012X7R1V225K125AE/C2167593) | 10 | Stock 0; minimum 62 | New exact code. Pre-order shown; minimum 62 exceeds 10 installed need. No purchasing quantity adopted. |
| TDK C3216X7R1V106K160AC | [C2182140](https://jlcpcb.com/partdetail/TDK-C3216X7R1V106K160AC/C2182140) | 10 | Stock 0; minimum 14 | Pre-order shown; minimum 14 exceeds 10 installed need. No purchasing quantity adopted. |
| Texas Instruments PCM1864DBT | [C2863172](https://jlcpcb.com/partdetail/TexasInstruments-PCM1864DBT/C2863172) | 10 | Stock 0; minimum 2 | Exact code found. Page says unavailable for purchase, may be consigned for assembly. TFSOP-30-175mil is the literal catalog package label; reconcile with released TSSOP-30. Search also returned PCM1864DBTR with 70 stock; different suffix excluded. |

## What the pass resolved

- Exact new catalog leads: CTS C17275161, TDK C2167593, TI C2863172;
  Panasonic C403329 is a stocked spelling-reconciliation candidate.
- Exact Amphenol RJHSE-5080: 869 in stock, **569 available to order** against 50.
  Package Plugin; Wave Soldering; Economic and Standard PCBA.
- Exact Littelfuse SMBJ15A: 13,148 in stock, **12,416 available to order** against
  15. The earlier HTTP 429 was an access failure, not evidence of a shortage.
- The 14 former LCSC-positive/JLC-eligibility-pending SMT leads now have exact
  JLC catalog pages, sufficient available-to-order counts, and SMT eligibility.
- All product pages identify Source JLCPCB and Economic and Standard PCBA.
  That does not establish the released job's process compatibility. The oscillator
  is unexpectedly labeled Wave Soldering; the three JLC-requested through-hole
  identities also carry Wave Soldering rather than exact manual-process approval.
- No exact replenishment or delivery lead time was established. No independently
  orderable global-sourcing offer was verified. Pre-order is future supply,
  not ready stock. Current LCSC or Western inventory was not rechecked; inherited
  fallback URLs and their old observation dates remain separate in the JSON.

## Ranked next paths

1. **Preferred — continue the JLC-led route with these exact parts.** Prepare a
   new draft matching/sourcing packet outside the immutable release, reconcile
   CUI/Same Sky and Panasonic spelling, and list the seven supply exceptions plus
   the oscillator/package and manual-process questions. Review the draft before
   any separately authorized upload. Use JLC's normal matching and exact-part
   pre-order/global-sourcing/consignment options first; targeted support is only
   for unresolved concrete exceptions. This keeps assembly coordination with
   JLC, with uncertain lead times and potentially disproportionate minima.
2. **Fallback — prepare exact external-source consignment for the seven supply
   exceptions.** Use the retained Western leads as starting points, verify exact
   maker/MPN, stock, lead time and packaging, then seek JLC acceptance of those
   exact consigned lots and the selected installation split. This may bypass JLC
   shortages, at the cost of separate procurement, shipping and consignment fees.
   If JLC rejects any requested manual operation, return that decision to the
   user; do not silently transfer work or substitute a part.

Neither recommendation authorizes contact, upload, procurement or ordering.
No ordering hold has been closed. Stop this matching pass; do not repeat stock
polling. Complete process agreement, usable allocation, placement preview and
actual itemized quote approval remain separate prerequisites.

## Full observation record

[JLC-BROWSER-20261030.json](JLC-BROWSER-20261030.json) retains all 35 requested
maker/MPN/quantity/reference subjects, observed catalog maker/MPN/code/package,
separate stock and orderable counts, minima/reel quantities, stock-pool labels,
assembly/PCBA eligibility, unknown lead times, URLs and UTC timestamps. It is a
transcription of visible browser fields; no raw HTML or screenshot archive is
claimed. The RJ record uses the initial fully rendered browser observation.

| MPN | Need | In stock | Available to order | Package | Result |
|---|---:|---:|---:|---|---|
| [0451001.MRL](https://jlcpcb.com/partdetail/Littelfuse-0451001MRL/C3099) | 5 | 15,473 | 14,640 | 2410 | jlc_orderable_sufficient |
| [1206L010/30WR](https://jlcpcb.com/partdetail/Littelfuse-1206L01030WR/C2153988) | 50 | 2 | not shown | 1206 | jlc_insufficient_or_zero |
| [1N5819HW-7-F](https://jlcpcb.com/partdetail/DiodesIncorporated-1N5819HW_7F/C82544) | 5 | 301,868 | 300,279 | SOD-123 | jlc_orderable_sufficient |
| [BAT54S-7-F](https://jlcpcb.com/partdetail/DiodesIncorporated-BAT54S_7F/C83574) | 20 | 11,730 | 11,698 | SOT-23 | jlc_orderable_sufficient |
| [BZT52C3V9-7-F](https://jlcpcb.com/partdetail/DiodesIncorporated-BZT52C3V9_7F/C154917) | 80 | 11,482 | 11,407 | SOD-123 | jlc_orderable_sufficient |
| [C2012X7R1V225K125AE](https://jlcpcb.com/partdetail/TDK-C2012X7R1V225K125AE/C2167593) | 10 | 0 | not shown | 0805 | jlc_insufficient_or_zero |
| [C3216X7R1V106K160AC](https://jlcpcb.com/partdetail/TDK-C3216X7R1V106K160AC/C2182140) | 10 | 0 | not shown | 1206 | jlc_insufficient_or_zero |
| [CB3LV-3I-12M288000](https://jlcpcb.com/partdetail/18404298-CB3LV_3I12M288000/C17275161) | 5 | 0 | not shown | SMD7050-4P | jlc_insufficient_or_zero |
| [CL21B104KBCNNNC](https://jlcpcb.com/partdetail/CL21B104KBCNNNC/C1711) | 55 | 2,420,064 | 2,020,335 | 0805 | jlc_orderable_sufficient |
| [CL21C222JBFNNNE](https://jlcpcb.com/partdetail/29010-CL21C222JBFNNNE/C28260) | 80 | 204,318 | 152,378 | 0805 | jlc_orderable_sufficient |
| [CRCW0603100KFKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW0603100KFKEA/C844916) | 60 | 1,035,225 | 1,023,619 | 0603 | jlc_orderable_sufficient |
| [CRCW060310K0FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW060310K0FKEA/C844918) | 60 | 1,339,534 | 1,160,398 | 0603 | jlc_orderable_sufficient |
| [CRCW06031K00FKEAHP](https://jlcpcb.com/partdetail/VishayIntertech-CRCW06031K00FKEAHP/C844747) | 30 | 60,251 | 59,858 | 0603 | jlc_orderable_sufficient |
| [CRCW06032K20FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW06032K20FKEA/C844925) | 10 | 88,046 | 87,611 | 0603 | jlc_orderable_sufficient |
| [CRCW06032K70FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW06032K70FKEA/C844770) | 80 | 29,670 | 29,658 | 0603 | jlc_orderable_sufficient |
| [CRCW0603330RFKEAHP](https://jlcpcb.com/partdetail/VishayIntertech-CRCW0603330RFKEAHP/C844355) | 10 | 833 | 379 | 0603 | jlc_orderable_sufficient |
| [CRCW060339K0FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW060339K0FKEA/C844779) | 10 | 42,828 | 42,623 | 0603 | jlc_orderable_sufficient |
| [CRCW06034K70FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW06034K70FKEA/C844931) | 10 | 1,102,023 | 1,097,761 | 0603 | jlc_orderable_sufficient |
| [CRCW060356R0FKEA](https://jlcpcb.com/partdetail/VishayIntertech-CRCW060356R0FKEA/C844179) | 10 | 31,570 | 30,720 | 0603 | jlc_orderable_sufficient |
| [DMN3023L-7](https://jlcpcb.com/partdetail/DiodesIncorporated-DMN3023L7/C443825) | 50 | 9,389 | 9,201 | SOT-23 | jlc_orderable_sufficient |
| [ERJ-3EKF68R0V](https://jlcpcb.com/partdetail/PANASONIC-ERJ3EKF68R0V/C403329) | 5 | 3,713 | 3,665 | 0603 | identity_review_stock_sufficient |
| [GRM21BR71A105KA01L](https://jlcpcb.com/partdetail/MurataElectronics-GRM21BR71A105KA01L/C97917) | 20 | 0 | not shown | 0805 | jlc_insufficient_or_zero |
| [GRM21BR71A106MA73L](https://jlcpcb.com/partdetail/749264-GRM21BR71A106MA73L/C710992) | 40 | 6,743 | 5,570 | 0805 | jlc_orderable_sufficient |
| [GRM31MR71E225KA93L](https://jlcpcb.com/partdetail/MurataElectronics-GRM31MR71E225KA93L/C97962) | 80 | 1,532 | 1,525 | 1206 | jlc_orderable_sufficient |
| [GRM32ER71A476KE15L](https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71A476KE15L/C84494) | 10 | 4,891 | 3,694 | 1210 | jlc_orderable_sufficient |
| [MMBT3906LT1G](https://jlcpcb.com/partdetail/onsemi-MMBT3906LT1G/C53444) | 10 | 906,968 | 905,144 | SOT-23 | jlc_orderable_sufficient |
| [PCM1864DBT](https://jlcpcb.com/partdetail/TexasInstruments-PCM1864DBT/C2863172) | 10 | 0 | not shown | TFSOP-30-175mil | jlc_insufficient_or_zero |
| [PJ-102AH](https://jlcpcb.com/partdetail/CUI-PJ102AH/C3096093) | 5 | 1,052 | 959 | Plugin | identity_review_stock_sufficient |
| [R-78E5.0-0.5](https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_05/C5199916) | 5 | 0 | not shown | SIP-3 | jlc_insufficient_or_zero |
| [RJHSE-5080](https://jlcpcb.com/partdetail/AmphenolICC-RJHSE5080/C599441) | 50 | 869 | 569 | Plugin | jlc_orderable_sufficient |
| [SMBJ15A](https://jlcpcb.com/partdetail/Littelfuse-SMBJ15A/C83846) | 15 | 13,148 | 12,416 | DO-214AA | jlc_orderable_sufficient |
| [SP0504BAHTG](https://jlcpcb.com/partdetail/Littelfuse-SP0504BAHTG/C10675) | 50 | 2,740 | 2,426 | SOT-23-5 | jlc_orderable_sufficient |
| [SS34-E3/57T](https://jlcpcb.com/partdetail/VishayIntertech-SS34_E357T/C13354) | 5 | 6,416 | 6,314 | SMC(DO-214AB) | jlc_orderable_sufficient |
| [TLV9062IDR](https://jlcpcb.com/partdetail/TexasInstruments-TLV9062IDR/C398355) | 10 | 188,817 | 187,903 | SOIC-8 | jlc_orderable_sufficient |
| [TPS70933DBVR](https://jlcpcb.com/partdetail/TPS70933DBVR/C89347) | 10 | 7,274 | 5,591 | SOT-23-5 | jlc_orderable_sufficient |

## Validation and execution limits

- Demand join PASS: exactly the 35 JLC-requested worksheet identities; 975 installed
  parts = 915 SMT + 60 manual, with the other 25 user parts excluded.
- Count/quantity checks PASS: 26 sufficient, seven insufficient/zero, two identity
  exceptions. The initial conversational 27/6 count was corrected before saving.
- Publication preservation PASS for all 256 payload files; order remains
  **DO-NOT-ORDER**, engineering acceptance NOT_REASSESSED.
- All 15 publication and 14 sourcing/mapping tests PASS with the environment
  accommodations below. No code or historical receipts were changed.
- Initial publication tests failed because the default macOS temporary path has
  `/var` as a symlink, rejected by the preservation checker. Reran unchanged tests
  with `TMPDIR=/private/tmp`; all passed.
- Initial sourcing tests could not import absent `vnext/tools/stock_lookup.py`.
  Loaded that exact file from local HEAD into an isolated temporary directory,
  supplied it through PYTHONPATH, ran the unchanged tests successfully, and removed
  the temporary directory. No network lookup was performed by this workaround.
- vNext is absent from the working tree; seven applicable instruction files
  (5,044 words, estimated load rather than tokens) were read from local Git
  HEAD `26e5b4f7c123d59d2ad2094c0ee4e6de357d7651`. The pre-existing index reports
  widespread deletions alongside untracked checkout files. No index/worktree repair,
  commit, reset or restoration was attempted.
- Coordinator observation checks only; no independent engineering/sourcing
  acceptance or fabricated order-admission receipt. Prior OR1–OR5 history and
  budgets remain retained. OR6 is the newly authorized browser route.
