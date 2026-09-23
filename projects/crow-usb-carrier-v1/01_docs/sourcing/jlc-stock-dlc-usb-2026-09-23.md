# Composed DLC/USB public stock observation — 2026-09-23

These numbers are dated observations and may already be stale. M-IMPORT CITED: JLC public catalog `stockCount` was read through the existing unauthenticated checker at 2026-09-23T20:13:07.818000+00:00; no login, allocation, reservation or order occurred. Candidate circuit SHA256 is `416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da`.

The direct public check grades **88/88 exact codes, zero shortages** against five boards plus150 per part, except exact XMOS C6362698 surplus0. The 24 manually assembled THT refs remain excluded by existing assembly policy. Exact-MPN comparison agrees except the already documented Molex43650-0200 ↔ catalog436500200 alias. `manufacturing_readiness.py` prelayout reports4/4 ACCEPTED against the exact new request and ADR0010; that is source-design admission only.

| Selected code | Stock observed | Required total |
|---|---:|---:|
| C1713 | 495970 | 180 |
| C2686428 | 11895 | 155 |
| C37616412 | 354 | 155 |
| C473385 | 2312 | 165 |
| C6362698 | 41 | 5 |

Direct public source: https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList (exact code POST query, no authentication). Full exact-code counts/MPNs and timestamp are retained under `06_build/verification/dlc-usb-public-refresh-20260923/public-stock.json`.

The independent derivative jlcsearch screen observed83/88 codes; C105872,C106231,C1852023,C6362698 were absent from its search index, and C192562 had the documented catalog MPN formatting difference. Six resistor/logic codes had derivative counts below the surplus threshold, in conflict with direct public records: C138002,C138033,C2675550,C60490,C60491,C93943. For example C138002 was47 in jlcsearch versus8234679 in the direct response. Upstream derivative observation time is unknown. These discrepancies remain visible; no substitution or freshness claim is inferred from the mirror. Raw jlcsearch responses preserve exact URLs, fetch times and SHA256 in its screen/cache.

The source checker does not persist full direct HTTP response bodies, so its report is the retained direct observation; the jlcsearch cache retains raw bytes. Neither source proves PCBA allocation.

Retained report hashes:
- `public-stock.json`: `6084330d4795ca1f2a8a4691cf8d41981be60d8665ddadb73596cbd56ae79252`
- `screen.json`: `a5229c6065239e0d22e4cd51982e62fab11716e0707076b18828152ca45069d6`
