# Exact THT source refresh — 2026-09-23

Read-only sourcing refresh against the current project policy: five boards plus
an absolute 150-unit public-stock surplus, assessed per aggregated line. The
user requirement is that JLC populate non-through-hole parts. This report does
not select a THT assembly disposition, order parts, change an MPN, change a
mate contract, or alter the 1 µF film-capacitor value.

## Result

| Exact MPN | Need / policy threshold | Current direct LCSC result | Exact public distributor result | Conclusion |
|---|---:|---:|---|---|
| Würth Elektronik `615008160221` RJ45, 8/board | 40 / **190** | C6461980: **0**, `LOW_STOCK(0)` | DigiKey: **991** | Exact public supply clears 190; JLC population does not. |
| KEMET `R82DC4100CK60J` film capacitor, 16/board | 80 / **230** | C3778009: **6**, `LOW_STOCK(6)` | DigiKey: **969** | Exact public supply clears 230; JLC population does not. |

The direct LCSC check was generated
`2026-09-23T02:10:44.238329+00:00`; its raw artifact is
`06_build/sourcing/direct-check-20260923.json`, SHA-256
`94b033d3633dde690ec43741ded2a7b74f6260eb2eb4ad97394d0ec85ac800d3`.
It records catalog stock only and expressly does not predict JLC assembly
allocation. The prior retained JLC response for C6461980 is likewise zero; the
newer full check is controlling for the stock statement here.

## Exact page evidence, refreshed

| Part | Exact product page | Read time | Identity and stock readout |
|---|---|---|---|
| Würth `615008160221` | <https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/615008160221/11627337> | page crawled 2026-09-23 | Page identifies manufacturer Würth Elektronik and manufacturer product number `615008160221`, through-hole 8p8c right-angle shielded jack, Active, **In-Stock: 991**. It clears 190 by 801. |
| KEMET `R82DC4100CK60J` | <https://www.digikey.com/en/products/detail/kemet/R82DC4100CK60J/21776592> | page crawled 2026-09-23 | Page identifies manufacturer KEMET and manufacturer product number `R82DC4100CK60J`, 1 µF ±5% 63 VDC radial through-hole film capacitor, Active, **In-Stock: 969**. It clears 230 by 739. |

The pages are direct distributor product pages, but their live HTML rejected an
unauthenticated byte fetch (HTTP 403), so this report does **not** invent a raw
page-body hash. The retained source records provide reproducible raw hashes:

* `01_docs/sourcing/manual_quotes.yaml` SHA-256
  `b6df0eb77726f44ef8818ede6a2f39a1da4ea0b7b92bde51cfd292a7547a41da`.
  Its exact-page records were captured 2026-09-22: Würth/DigiKey 991;
  KEMET/DigiKey 969. It also records KEMET/Mouser 5,775 at
  `2026-09-22T04:05:51-07:00` from
  <https://www.mouser.com/ProductDetail/KEMET/R82DC4100CK60J>.
* The current direct LCSC artifact and its SHA-256 are stated above. It is the
  raw, machine-readable evidence for the 0 and 6 observations.

## Disposition boundary

The evidence supports only this narrow conclusion: **exact parts are publicly
sourceable in enough quantity for a possible manual THT assembly path.** It
does not convert either part to a JLC-populated line, satisfy JLC stock policy,
or approve manual assembly. Any manual-THT proposal would still need an explicit
assembly disposition and the associated process, first-article, and order-time
allocation evidence. Until then the listed selected parts, connector mate
contracts, and film-capacitor value remain unchanged.

## Subsequent user disposition — D9

The user subsequently chose “Plan manual assembly for these through-hole parts.” This authorizes the source assembly plan for J1–J8 and the sixteen C_A coupling capacitors, without purchasing. The manufacturer identities, values, reserve quantity and connector interfaces remain unchanged. assembly.yaml owns the24 manual references; the JLC-specific BOM/CPL will omit them, while the full design retains them. The earlier undecided-disposition statements above are historical.
