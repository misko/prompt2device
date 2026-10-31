# Exact-part sourcing draft — coordinator review, not upload approval

Follow-on OR8: `SOURCING-COMPARISON-20261030.md` now supplies prices and a revised
route recommendation. It also clarifies from JLC's FAQ that the Wave Soldering
label means manual assembly, not necessarily literal wave exposure. Read the
historical OR7 process concern below with that correction; compatible SMD
installation still needs verification, not a redesign or compulsory relabeling.

Input: browser commit `be16560f0fe14c102ea048fbad64d362366efc51`, unchanged
`JLC-BROWSER-20261030.json`, v3 worksheet and sealed 5-carrier/10-pod population.
Reviewed 2026-10-30 PDT. No repeated JLC inventory pass or live external-stock
refresh was performed. Browser observations remain transcriptions, not screenshots
or allocated stock. No substitution or production-data change is adopted.

## Matching dispositions

| Released identity / catalog code | Review and next disposition |
|---|---|
| Panasonic ERJ-3EKF68R0V / C403329 | Supported exact spelling reconciliation for this draft: Panasonic publishes ERJ3EKF68R0V, 68 ohm, 1%, 0.1 W, 0603, paper tape. DigiKey uses the hyphenated form with matching specifications and a Panasonic datasheet link. Preserve both strings; do not introduce generic punctuation stripping. Browser orderable count is 3,665 for five needed. |
| Same Sky PJ-102AH / C3096093 | Supported manufacturer-history reconciliation for this draft: Same Sky's rebrand notice retains model numbers/BOMs; a historical CUI manufacturer drawing names PJ-102AH, and the exact distributor listing now identifies Same Sky (formerly CUI Devices). Do not accept arbitrary CUI parts as Same Sky or replace the current mechanical requirements with the old drawing. Browser orderable count is 959 for five needed. Final JLC match must retain the exact part/datasheet. |
| CTS CB3LV-3I-12M288000 / C17275161 | Manufacturer identifies ceramic 7 x 5 mm surface mount; datasheet gives reflow conditions, maximum 260 C for 20 seconds. Retain SMT population. JLC's Wave Soldering label conflicts with that process route; require corrected matching/process before using this catalog item. This is not evidence the circuit or footprint needs redesign. |
| TI PCM1864DBT / C2863172 | TI confirms TSSOP (DBT), 30 pins, tube packaging. Do not change the native footprint to JLC's literal TFSOP label. Check the accepted vendor match against TI's package drawing. TI explicitly lists DBTR as the same product in a different carrier (tape/reel); that is a focused packaging-variant qualification option, not an adopted replacement. |

These two naming explanations support 28 draft matching candidates with positive
OR6 quantities; the original 26/7/2 browser classifications stay unchanged.
This is a coordinator judgment, not independent sourcing admission or an approved
factory BOM. No blanket manufacturer alias or suffix-normalization code was added.

## Seven supply exceptions — one combined sourcing decision

| Exact MPN | Installed need | OR6 JLC stock / displayed minimum | Preferred exact-part path to evaluate |
|---|---:|---|---|
| CB3LV-3I-12M288000 | 5 | 0 / 4 | Compare exact DigiKey consignment with JLC replenishment; resolve SMT classification first. |
| 1206L010/30WR | 50 | 2 / 14 | Compare complete exact external lot with replenishment. Two present units do not cover the build. |
| GRM21BR71A105KA01L | 20 | 0 / 407 | Compare exact external lot against cost/lead time of the disproportionate JLC minimum. |
| R-78E5.0-0.5 | 5 | 0 / 3 | Exact RECOM external lot or replenishment; no same-named other-maker modules. |
| C2012X7R1V225K125AE | 10 | 0 / 62 | Compare exact external lot against JLC minimum and lead time. |
| C3216X7R1V106K160AC | 10 | 0 / 14 | Recheck the retained Buerklin exact offer; compare delivered consignment cost against replenishment. |
| PCM1864DBT | 10 | 0 / 2 | Exact DBT external lot/consignment is the unchanged-design path. Separately, DBTR packaging qualification could avoid consignment if authorized and supported. |

Exact fallback URLs are already recorded per row in the browser JSON. Their
old availability is not refreshed by this document. Displayed minima are not
approved purchase quantities; replenishment lead times, lot packaging, fees,
spares/attrition and JLC consignment acceptance remain unknown. No savings or
delivery promise can be calculated yet.

1. **Preferred:** keep the 28 supported catalog matches and prepare one combined
   seven-line exact external-source/consignment comparison, with refreshed stock,
   quantities, packaging and delivered costs. This avoids seven separate user
   decisions and disproportionate passive minima, while keeping JLC assembly.
2. **Alternative:** keep all exact MPNs through JLC replenishment where offered,
   plus exact DBT consignment. Simpler procurement coordination but unknown wait
   and potentially larger minimum purchases. DBTR is an additional proposed
   qualification, not silently substituted into either plan.

No contact, upload or purchase is needed to prepare that comparison. Actual
vendor acceptance/quote and user approval remain subsequent requirements. Stop
this review here; do not repeat the completed 35-part browser pass.

## Sources checked during review

- [Panasonic exact model](https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ3EKF68R0V)
  and [DigiKey hyphenated listing](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-3EKF68R0V/1746446).
  This is identity evidence, not a refreshed stock or lifecycle assessment.
- [Same Sky manufacturer rebranding release, hosted by Arrow](https://static4.arrow.com/-/media/arrow/images/application-pages/ipe-global-page/2024/cui-devices-is-now-same-sky-pr.pdf),
  [historical CUI drawing, hosted by Adafruit](https://cdn-shop.adafruit.com/datasheets/21mmdcjackDatasheet.pdf)
  and [exact current distributor identity](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-102AH/408448).
  Direct current maker PDF/press pages returned 403/404; no unseen PDF geometry
  was accepted. The old drawing establishes identity history only.
- [CTS series](https://www.ctscorp.com/Product-Series/CB3LV.htm) and
  [manufacturer datasheet, page 4](https://www.ctscorp.com/Files/DataSheets/Passives/FCP/Clock-Oscillators/clock-ocillators-CB3_CB3LV-datasheet.pdf).
- [TI exact DBT package and carrier options](https://www.ti.com/product/PCM1864/part-details/PCM1864DBT).

## Portable handoff correction

The Mac report documents a damaged/incomplete local checkout (missing vNext,
staged deletions), not missing repository content. Do not commit those deletions
or reset user work. Use a clean separate clone/checkout for continuation if the
existing checkout cannot be repaired safely. On macOS, use `TMPDIR=/private/tmp`
for publication tests when `/var` symlink resolution triggers the checker.
Server baseline verification passes unchanged: 256 preserved payloads, 29 tests.
New browser-binding tests verify the 35 subjects, 975 installed units, exact
worksheet hash and quantity classifications; they do not prove inventory truth.
