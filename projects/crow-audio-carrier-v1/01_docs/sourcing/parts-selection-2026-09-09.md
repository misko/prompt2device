# Targeted OPA2320/reference-resistor selection — 2026-09-09

These are dated public observations and are stale before ordering. They prove
neither reserved stock, JLCPCB PCBA allocation nor full-board sourcing closure.
No login, upload, supplier contact or purchase occurred.

The two exact new MPNs were screened BEFORE source adoption on2026-09-09.
Both independently composed Q-2SOURCE results are PASS1/1 for five boards,
using JLCPCB/LCSC as one pool and DigiKey as the second. Mouser is OWED and
Amazon has no quote; neither was counted. All quantities below are CITED
observations from the dated public catalogue/product pages, not present stock.

| Manufacturer / exact MPN | Per board / five boards | JLC/LCSC code and observed stock | DigiKey cut-tape line and observed stock |
|---|---|---|---|
| Texas Instruments OPA2320AIDR | 9 /45 | C2863402 /3101 | 296-29885-1-ND /1086 |
| YAGEO RC0402FR-071KL | 2 /10 | C106235 /4461819 | 311-1.00KLRCT-ND /6348432 |

DigiKey sources were opened exact product pages, not search snippets:
[OPA2320AIDR](https://www.digikey.com/en/products/detail/texas-instruments/OPA2320AIDR/2782284)
and [RC0402FR-071KL](https://www.digikey.com/en/products/detail/yageo/RC0402FR-071KL/729460).
Both displayed Active, cut-tape minimum/multiple1, exact manufacturer and
MPN. The1k resistor's search snippet had a different stock count; only the
opened-page count above was used. Exact dated inputs are in manual_quotes.yaml.
JLC catalogue queries used the exact codes; raw observations and machine
reports remain disposable, and the committed record is not a build input.

Machine evidence retained unchanged under
`../../06_build/sourcing/opa2320-adoption-20260909/`:

- `opa2320-catalog.json`: public catalogue PASS1/1, attempt
  opa2320-public-catalog-20260909,20:35:39.604879..20:35:41.357260Z.
- `opa2320-two-source.json`: composed-pools PASS1/1, attempt
  opa2320-two-pool-public-20260909,20:37:09.231390..20:37:09.286972Z.
- `reference-1k-catalog.json`: public catalogue PASS1/1, attempt
  reference-1k-public-catalog-20260909,20:41:15.786714..20:41:17.571420Z.
- `reference-1k-two-source.json`: composed-pools PASS1/1, attempt
  reference-1k-two-pool-public-20260909,20:42:15.159608..20:42:15.214984Z.

The source-correction outcome binds these files by SHA256. Both composition
runs used shopping_list.py with--scope all,--boards5,--required-pools2 and
--offline against one-line temporary candidate projects and supplied dated
JLC evidence. Scope is two selected parts, NOT the whole carrier BOM. No
Mouser request or configured credential was used. The two10k input limiters
reuse the existing RC0402FR-0710KL identity; full-board quantity refresh,
all other part coverage and order-day allocation remain separate obligations.

## Precision reference-divider quantity refresh —21:33 UTC

Before ADR0024 adoption, rechecked the existing RT0603BRD0710KL/C95204 at
its increased total of six per carrier (two supervisor bottoms and four
reference dividers),30 for five carriers. This adds no new MPN to the board.
The targeted public-catalog run `reference-divider-public-stock-20260909`
passed1/1, observing1,960,049 catalog units; raw sidecar SHA256
`af1bc92ba1c13f4f86646e0e76637a2a9206de1975bf400b7f2eb888f3558782`.

The separately opened
[LCSC product page](https://www.lcsc.com/product-detail/C95204.html) displayed
449,920 units and minimum/multiple20; do not reconcile different public stock
observations by choosing a preferred figure. The opened
[DigiKey exact page](https://www.digikey.com/en/products/detail/yageo/RT0603BRD0710KL/4340589)
displayed Active, YAG1236CT-ND cut tape,402,522 units, and a quantity-one
price row. Both pages matched10k,0.1percent,25ppm/C,0603 and YAGEO identity.
This is public two-distributor observation, not a newly executed Q-2SOURCE
composition, full-board coverage, PCBA allocation or a purchase authorization.
The earlier search snippet had a different DigiKey count; it was not adopted.

## Isolation/interlock candidate observations — 2026-09-09, 22 UTC hour

These are CITED public product-page observations for the fresh isolation
comparison, not selected BOM additions or a Q-2SOURCE composition. No exact
new candidate MPN was adopted, no inventory was reserved and no allocation,
login, upload, supplier contact or order occurred. Quantities are stale before
ordering; a zero in one observed pool is not proof of worldwide unavailability.

| Exact candidate MPN | Proposed quantity per board / five | Opened public page observation |
|---|---|---|
| TMUX7412FRRPR | 5 /25, eighteen of twenty contacts used | LCSC C2982617, 1,735 units, minimum/multiple1, WQFN16 |
| AQY221R2SZ | 18 /90 | LCSC C2653917, out of stock, minimum/multiple1, full reel1,000; DigiKey 255-2585-1-ND, 853 units, Active, cut tape/TR/Digi-Reel |
| TPS92612DBVR | 9 /45 | DigiKey 296-TPS92612DBVRCT-ND, Active, **0 in stock**, quantity-one cut-tape row; 3,000 expected2026-12-07 is not current stock |
| TPS92612QDBVRQ1 | alternate comparison only, not adopted | Independently opened DigiKey exact page: 296-50440-1-ND, Active, 2,145 units, quantity-one cut-tape row |

The AQY221R2SZ suffix is Panasonic's exact tape/reel orientation/orderable;
AQY221R2S tube and AQY221R2SX are not interchangeable procurement strings.
The non-Q1 LED driver's search snippet was not adopted as stock evidence.
The Q1 driver is a distinct exact identity: its SLDS237B primary has different
table conditions, including PWM LOW for the quiescent-current row, compared
with PWM HIGH in the non-Q1 SLVSFG3 table. No automatic substitution or shared
electrical/sourcing pass is inferred. These observations leave pool composition,
the exact18-ohm sense resistor, any increased existing-part quantities and
full-board sourcing for a later actual adoption.

Opened sources:

- [TMUX7412FRRPR LCSC](https://www.lcsc.com/product-detail/analog-switches-multiplexers_texas-instruments-tmux7412frrpr_C2982617.html)
- [AQY221R2SZ LCSC](https://www.lcsc.com/product-detail/C2653917.html)
- [AQY221R2SZ DigiKey](https://www.digikey.com/en/products/detail/panasonic-electric-works/AQY221R2SZ/646322)
- [TPS92612DBVR DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/TPS92612DBVR/12352289)
- [TPS92612QDBVRQ1 DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/TPS92612QDBVRQ1/9685579)
- [TPS92612-Q1 primary](https://www.ti.com/lit/ds/symlink/tps92612-q1.pdf)

The [isolation/interlock report](../reports/2026-09-09-isolation-interlock-decision.md)
contains the architecture decision and explicitly separates proposal from source
adoption and native review.
