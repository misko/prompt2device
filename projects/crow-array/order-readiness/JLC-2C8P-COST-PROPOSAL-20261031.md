# Draft exact-parts cost proposal — two carriers and eight pods

**31 October 2026. Not a complete vendor quotation or an order.** The user
accepts two assembled carriers and requests a proposal only: no substitutions,
purchases, reservations or manufacturing commitments. Amounts are USD and
unreserved public/browser snapshots; supplier and JLC prices, allocations,
delivery and actual totals require confirmation. No messages or orders sent.

## Build scope

The current JLC drafts show five bare carriers with two assembled (Economic),
and ten bare pods with eight assembled (Standard). JLC supplies and installs
the 478 SMT placements (127 per carrier, 28 per pod). Through-hole parts,
Pico, microphones and buzzers are user-installed. The 1+8 home kit below
finishes one carrier and all eight pods; the second carrier remains an SMT-only
spare unless the user later wants it completed. Portal-proposed rails/tooling,
stack, paste exclusions, finished holes and production process are not accepted.

## Six exact SMT sourcing lines

Demand is installed count for 2+8, not purchase quantity. Browser observations
are from `JLC-HOME-QUOTE-OBSERVATIONS-20261031.md`; select no replacement.

| Manufacturer / exact MPN | Installed need | JLC observation / candidate | Known indicative amount |
|---|---:|---|---:|
| CTS CB3LV-3I-12M288000 | 2 | Zero public stock; regular pre-order min 4; confirm compatible SMT handling | 4 / $10.20 |
| Littelfuse 1206L010/30WR | 24 | 18 carrier and 10 pod gross displayed including portal allowances; each showed 7 available, possibly same pool. Confirm allocation once and replenishment terms. | Not priced for required combined quantity |
| Murata GRM21BR71A105KA01L | 12 | Zero public stock; pre-order min 407; 20 displayed required for each job | 407 / $8.71 |
| TDK C2012X7R1V225K125AE | 8 | Zero public stock; pre-order min 62; 10 displayed pod requirement | 62 / $8.80 |
| TDK C3216X7R1V106K160AC | 4 | Zero public stock; pre-order min 14; listing estimated 28 days | 14 / $8.83 |
| TI PCM1864DBT | 4 | Zero ordinary stock; evaluate exact JLC Global Sourcing, tube, not DBTR | Current 2+8 global price/MOQ unconfirmed |

The four minimum-line estimates sum to **$36.54** only. This is not the
six-part cost, an allocated stock purchase or the SMT BOM subtotal. If the
seven fuse units are one shared eligible pool and the two jobs' displayed gross
requirements 18+10 are valid simultaneously, the illustrative shortfall is
21. Verify this with JLC; do not assume the two separate seven-unit views are
fourteen units. Factory attrition, lot minima, pricing and eligible inventory
may differ by job. Earlier account observation of $104.88 for ten PCM1864DBT
through Global Sourcing was a query for ten, not a proven MOQ or current quote.

Preferred path: exact JLC replenishment for the five non-ADC identities and
exact Global Sourcing for the ADC, subject to a written itemized quote and
usable inventory dates. Fallback: exact [DigiKey PCM1864DBT tube listing](https://www.digikey.com/en/products/detail/texas-instruments/PCM1864DBT/5213896)
as consignment input; page observed 673 available and $10.45 each for 1–9,
but four at $41.80 is only a distributor benchmark, before JLC-required
allowance, shipping, consignment fees and intake, not a JLC quote. See JLC's
[Global Sourcing](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service),
[pre-order](https://jlcpcb.com/help/article/what-is-jlcpcb-parts-pre-order-service)
and [overseas consignment](https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb)
procedures. Do not initiate any transaction or assume published fee schedules
are additive or applicable without the account-specific itemization.

## Home-install kit: finish one carrier and eight pods

Illustrative US DigiKey pricing from public page snapshots; no cart, shipping,
tax or tariff quote. Assumes none of these parts is already owned. Buying ten
microphones and ten buzzers costs less at the displayed quantity breaks than
buying eight, and yields two spare of each. The 16-jack calculation uses the
10-unit tier. MPN/source identity must be confirmed, including distributor
spelling `RJHSE5080` versus released `RJHSE-5080`, before any purchase.

| Exact part | Installed | Illustrative purchase | Estimated line | Source |
|---|---:|---:|---:|---|
| Amphenol RJHSE-5080 | 16 | 16 | $18.93 | [DigiKey RJHSE5080 listing](https://www.digikey.com/en/products/detail/amphenol-icc-commercial-products/RJHSE5080/1242687) |
| Same Sky PJ-102AH | 1 | 1 | $0.83 | [DigiKey power jack](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-102AH/408448) |
| RECOM R-78E5.0-0.5 | 1 | 1 | $3.76 | [DigiKey RECOM](https://www.digikey.com/en/products/detail/recom-power/R-78E5-0-0-5/2834904) |
| Raspberry Pi SC0915 | 1 | 1 | $4.59 | [DigiKey Pico](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13684020) |
| Same Sky CMA-4544PF-W | 8 | 10 | $11.24 | [DigiKey microphone](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMA-4544PF-W/1869981) |
| Same Sky CPE-203 | 8 | 10 | $28.72 | [DigiKey buzzer](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CPE-203/1738900) |
| **Home kit subtotal** | **35** | **39** | **$68.07** | Before shipping, tax, tariffs and other charges |

The RJ45 price is $1.183 each at the 10-unit tier (16 × $1.183 = $18.928,
rounded to $18.93). Eight microphones at the one-unit tier cost $11.92,
versus ten for $11.24. Eight buzzers at the one-unit tier cost $30.16,
versus ten for $28.72. Listings are unreserved and some search/index snapshots
may be days or weeks old; recheck pricing, stock, exact identity, packaging and
shipping before purchasing. Quotes omit existing stock, spares other than the
two microphone and buzzer tier extras, and any tools or consumables.

If the user decides to finish the second carrier at home, add eight RJ45, one
PJ-102AH, one RECOM and one Pico. At the listed tiers, 25 RJ45 cost $27.72,
less than 24 at the 10-unit tier, and supply one spare; two jacks cost $1.66,
two RECOM $7.52 and two Picos $9.18. The ten microphones and ten buzzers
remain $11.24 and $28.72: **$86.04** total for 46 installed parts plus one
RJ45 and four acoustic spares, before shipping/tax. This is an alternative,
not a decision to populate the extra carrier at home.

## Complete-cost worksheet — not yet quotable

| Cost bucket | Current evidence |
|---|---|
| JLC carrier fabrication / engineering | $37.40 portal display for five bare/two assembled, preliminary and process unaccepted |
| JLC pod fabrication | Earlier ten-bare-board display $14.00; settings/rails not accepted; refresh needed |
| JLC SMT components, other than shortages | Not fully quoted |
| All six shortage parts / procurement surplus | Not fully quoted; $36.54 covers four minimum lines only |
| SMT labor, stencils, setup, feeder and sourcing fees | Not fully quoted |
| JLC shipping / tax / duty | Combined shipment not quoted; $26.94 was carrier-only shipping estimate |
| Home-install parts | $68.07 illustrative; $86.04 if finishing the spare carrier too |
| Home shipment / tax / tariff | Not quoted |
| **Grand total and arrival** | **Unknown; cannot calculate an honest complete PCBA quote** |

Before any order: establish all exact parts and job-specific allowances with
uniquely allocated stock; acquire a current, non-binding itemized JLC quote or
document the prepayment boundary; reconcile the portal BOM/placement previews,
CTS assembly method, pin-1/cathode rotations, 7628A/7628 stacks, stencil/paste,
rails, finished-hole and acoustic/mechanical requirements; assess shipment and
home part identity; then present the actual complete amount and build scope for
explicit approval. The JLC portal currently warns that proceeding without the
short components would leave them unplaced; do not press that option or omit
required SMT to obtain a misleading total.
