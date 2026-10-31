# Seven-shortage sourcing comparison — 5 carriers / 10 pods

OR8, 2026-10-30 PDT. Decision support only: no purchase, reservation, vendor
submission, substitution, allocation, or order acceptance. The sealed release
and original browser evidence are unchanged. This supersedes OR7's unpriced
route ranking, not its identity evidence. Only these seven shortages are priced;
this is not the total board-batch cost.

## Recommendation

Prefer **JLC-managed procurement**: evaluate regular replenishment for six exact
parts and **JLC Global Sourcing for PCM1864DBT**, which the ordinary catalog does
not offer for purchase. Use Global Sourcing for any of the other six if its
account-specific arrival date is better. This keeps logistics inside JLC; it is
not a claim that all seven are currently offered through the global portal.

The supposedly excessive capacitor minima total only $27.32 at catalog prices.
Paying a modest component premium can be simpler than coordinating two outside
suppliers, international shipment approval and consignment charges. This is a
logistics judgment, conditional on the actual JLC price/date, not a guarantee of
the cheapest or fastest route. Do not wait indefinitely for unquoted restocking.

Fallback: purchase the unchanged exact parts from DigiKey (six lines) and Bürklin
(one line), then consign using JLC's approved shipment workflow. Do not buy or
send parts before quantities, packaging, fees and receipt route are established.
No DBTR packaging substitution is included.

## Component comparison

All quantities below exclude factory attrition/minimum assembly allowances.
JLC quantities are max(installed need, OR6 displayed minimum), not approved
purchase quantities. No credit is taken for the two unallocated existing fuses.
External columns are stock/price observations, not reservations or delivered
quotes. DigiKey web snapshots were crawled within the preceding week, not a
signed-in live checkout. Bürklin and JLC price pages were fetched directly today.

| Exact part | Installed need | External stock observed | External unit / line cost | JLC illustrative qty / line cost |
|---|---:|---:|---:|---:|
| [CB3LV-3I-12M288000](https://www.digikey.com/en/products/detail/cts-frequency-controls/CB3LV-3I-12M288000/4308709) | 5 | 1,449 DigiKey | $1.66 / $8.30 | [5 / $13.22](https://jlcpcb.com/partdetail/18404298-CB3LV_3I12M288000/C17275161) |
| [1206L010/30WR](https://www.digikey.com/en/products/detail/littelfuse-inc/1206L010-30WR/6346986) | 50 | 45,562 DigiKey | $0.4662 / $23.31 | [50 / $33.60](https://jlcpcb.com/partdetail/Littelfuse-1206L01030WR/C2153988) |
| [GRM21BR71A105KA01L](https://www.digikey.com/en/products/detail/murata-electronics/GRM21BR71A105KA01L/587408) | 20 | 1,191,768 DigiKey | $0.106 / $2.12 | [407 / $9.04](https://jlcpcb.com/partdetail/MurataElectronics-GRM21BR71A105KA01L/C97917) |
| [R-78E5.0-0.5](https://www.digikey.com/en/products/detail/recom-power/R-78E5-0-0-5/2834904) | 5 | 32,828 DigiKey | $3.624 / $18.12 | [5 / $19.41](https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_05/C5199916) |
| [C2012X7R1V225K125AE](https://www.digikey.com/en/products/detail/tdk/C2012X7R1V225K125AE/3283652) | 10 | 273,176 DigiKey | $0.571 / $5.71 | [62 / $9.13](https://jlcpcb.com/partdetail/TDK-C2012X7R1V225K125AE/C2167593) |
| [C3216X7R1V106K160AC](https://www.buerklin.com/en/p/tdk/ceramic-capacitors/c3216x7r1v106k160ac/75D7535/) | 10 | 1,185 Bürklin | €0.4879 / €4.88 | [14 / $9.15](https://jlcpcb.com/partdetail/TDK-C3216X7R1V106K160AC/C2182140) |
| [PCM1864DBT](https://www.digikey.com/en/products/detail/texas-instruments/PCM1864DBT/5213896) | 10 | 673 DigiKey | $8.14 / $81.40 | [Not offered for ordinary purchase](https://jlcpcb.com/partdetail/TexasInstruments-PCM1864DBT/C2863172); Global Sourcing quote needed |

External component subtotal: **$138.96 + €4.88**. Six JLC catalog lines:
**$93.54**, calculated before rounding individual lines. Adding the ADC's
external price as a proxy gives **$174.94**, but that is explicitly **not** a
JLC Global Sourcing quote. No exchange rate has been assumed. Shipping, tax,
customs, assembly, handling, attrition and packing extras are excluded. Bürklin's
applicable export/tax treatment must be established at checkout.

External packing: cut tape for the oscillator, fuse and DigiKey capacitors;
tube for ADC and RECOM. Bürklin packing was not established. Do not assume cut
tape requires a full reel, or that supplier tubes require loose-part processing;
use JLC's actual intake requirements. Digi-Reel's optional $7/reel is not included.

## Cost and lead-time comparison

| Route | Price basis / extra costs | Published timing and remaining unknowns |
|---|---|---|
| Regular JLC replenishment | $93.54 catalog illustration for six; price may change on procurement confirmation. Does not solve ADC by itself. | No verified arrival date for any of these six. JLC says final price confirmation is within 48 hours after initial payment; that is not delivery time. |
| JLC Global Sourcing | Account offer required; use distributor prices as benchmarks only. Usually no separate shipping charge; certain modules can incur duty, and fuses can incur inspection/certification charges. | Review 1–3 business days; purchasing normally 9–20 business days. These are published stages, not a promised total. Exact part/date is shown in account. |
| Buy externally + consign | $138.96 + €4.88 before extras. Add supplier shipping, any consolidation/forwarding, JLC intake/handling, packing and applicable deposits. | All seven external listings show enough parts for installed need. No destination-specific shipping date was obtained. JLC price review within two business days; transit, clearance and warehouse intake not quoted. Cannot responsibly promise this is faster. |

Sources: [JLC pre-order guide](https://jlcpcb.com/help/article/what-is-jlcpcb-parts-pre-order-service),
[Global Sourcing guide](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service),
[overseas consignment guide](https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb).
Board fabrication, assembly and finished-board shipping come after these sourcing
steps; none is included in the times above. Pre-order terms' 18-day threshold is
an approval rule, not an 18-day delivery guarantee.

### Consignment fees: do not invent an all-in quote

JLC's [consignment terms](https://jlcpcb.com/help/article/consignment-part-terms-conditions)
list $70 per 50 identities plus $15 handling: $85 for seven identities. They also
list possible loose-part fees and $8/48-hour baking. If $85 applies once, the
component-plus-service illustration is **$223.96 + €4.88**, still excluding
shipping and other extras.

The [overseas guide](https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb)
instead describes a 2% handling fee, minimum $10 per shipment, and refundable
import duty/VAT deposits. It requires approved shipments to the Hong Kong address
shown in the account, supporting purchase records and a sale/rebuy agreement.
These publications do not establish whether the $85 and newer handling fees
replace or supplement one another for our account. **Do not add them together,
or assume the cheapest one applies.** Obtain the itemized screen. Deposits are
cash-flow requirements, not automatically permanent cost; unused minimum-order
surplus may remain in JLC inventory. Do not use an old published warehouse address.

## One bounded account pass to turn this into an order proposal

1. Open Parts Manager → Order Parts. Inspect the six regular exact offers and
   the Global Sourcing offer for **PCM1864DBT** (not DBTR). If an ordinary offer
   has no practical arrival date, compare its global exact offer in the same pass.
2. Record full installed demand split by carrier and pod, factory attrition for
   each board job, minimum/pack quantity, exact maker/MPN, packing, itemized total,
   arrival date and assembly eligibility. Account stock must cover both jobs;
   do not assume pooled attrition or split one line across incompatible stock pools.
3. Rank complete JLC-managed coverage first, external consignment second. Only
   fall back for a failed/expensive/slow exact line. For consignment obtain the
   actual fee screen and both suppliers' destination shipping prices before
   comparing landed totals; two direct shipments versus consolidation must be
   priced, not assumed cheaper either way.
4. Present one purchase proposal for user approval. Do not pay simply to discover
   a final quote: JLC's pre-order flow can require payment before final pricing,
   and Global Sourcing payment is generally non-cancelable. Stop at that boundary.
   Verify receipt in usable JLC inventory before relying on it for PCBA.

This is an account-workflow task, not a new engineering research cycle or a
request to recheck all 35 identities. The exact portal offers and landed shipping
costs cannot be recovered reliably from public catalog pages.

## Process clarification carried forward

JLC's [assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) says its
“Wave Soldering” catalog label denotes manual assembly. Therefore the CTS label
alone does **not** prove the oscillator will undergo wave soldering. This narrows
OR7's concern to a compatible SMD installation/matching check; no redesign or
full-reel purchase is justified by that label. RECOM remains JLC-installed under
the user's 60/20 split; no work is reassigned to the user.

## Evidence and limits

`sourcing-comparison-20261030.csv` retains exact prices, quantities, sources and
freshness. JLC tiers were extracted from identity-bound public catalog payloads
at 01:27:34–01:27:37 UTC on Oct 31 (Oct 30 PDT). Product AggregateOffer low/high
labels are inverted on some pages; they were not used to choose a quantity price.
The generic InStock flag for the fuse does not override OR6's insufficient count
of two. No historical browser result was rewritten.

Bürklin's web-reader request returned 403; a normal direct public fetch succeeded
at 01:24:04 UTC, with exact product/brand, stock 1,185 and 10–49 price €0.4879.
Its payload hash is retained in the CSV. Broad web searches returned no results;
official pages and exact distributor leads were opened directly. Local helper
import and arithmetic syntax errors were corrected before any result was used.
No failed request was interpreted as missing stock. Tests check preservation and
arithmetic, not supplier allocation or engineering acceptance.

Validation: 256 release payloads preserved; 15 publication and 18 order-readiness
tests pass. Separate comparison checks confirm seven exact OR6 subjects, matching
installed/minimum quantities and source URLs, independent currency totals, no
ordinary ADC purchase price, and byte-identical browser evidence versus be16560f.
All work remains local on `codex/crow-jlc-source-review-20261030`.
