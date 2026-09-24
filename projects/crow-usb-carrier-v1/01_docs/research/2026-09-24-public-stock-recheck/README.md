# Crow public-stock reconciliation — 2026-09-24

This is a read-only prelayout catalog recheck, not JLCPCB PCBA allocation,
reservation, order, or release evidence. The selected request remains the
five-board, 88-line
[prelayout request](../../../06_build/sourcing/prelayout_request.json), with
ordinary **five-board quantity + 150 units per exact LCSC line** and the
accepted exact XMOS C6362698/U_XU zero-surplus exception.

At 16:18 UTC, [jlcsearch-report.json](jlcsearch-report.json) queried all 88
selected codes through the public derivative jlcsearch endpoint with a fresh
cache. It observed 83 exact MPN/code rows. Applying Crow's surplus policy
independently gave **77 above threshold, 6 below, and 5 unconfirmed**; the
screen's own `stock_vs_required` field compares only the five-board quantity,
not the extra 150. All 88 recorded response bodies are retained in
[jlcsearch-cache](jlcsearch-cache/) and their hashes/byte counts match the
report (report SHA-256
`97e93430e1f5e9d10581e2cce7c171b8c402662b9ecea8092def90bd317954f8`).
JLCsearch publishes no upstream inventory timestamp, and an absent search row
does not establish zero stock.

I rechecked those eleven apparent problem codes, plus two jlcsearch rows
with the smallest positive margins, against JLC's unauthenticated public
`selectSmtComponentList` catalog endpoint. The [direct manifest](direct/manifest.json)
binds exact POST bodies, UTC timestamps, raw SHA-256, exact codes, MPNs,
five-board quantities, and thresholds; all 13 HTTP responses and raw JSON
bodies are retained alongside it. An independent raw parse verified 13/13
hashes, one exact code/MPN result each (the already documented C192562 Molex
`43650-0200`/`436500200` catalog alias), and **13/13 stock values above
their Crow thresholds**. The direct manifest SHA-256 is
`a868404875808e03e146bbdc40be6b065c000490c5e44efddfa4ae72e7ca5272`.

| Exact code / selected MPN | Direct public stock | Crow threshold | Margin |
|---|---:|---:|---:|
| C2675550 / SN74LVC1G125DCKT | 181 | 160 | 21 |
| C1852023 / TLV320ADC6140IRTWT | 188 | 160 | 28 |
| C6362698 / XU316-1024-TQ128-C24 | 39 | 5 | 34 |
| C22428234 / TMUX4827YBHR | 5,437 | 190 | 5,247 |
| C861313 / RT0603BRD0730K9L | 3,554 | 155 | 3,399 |

The other eight directly rechecked rows also clear their thresholds; see the
manifest for exact counts. The earlier immutable [88-line direct public
packet](../2026-09-24-public-stock-569/terra-authoritative-public-review.md)
passed every line at 00:45 UTC. This newer 13-line direct sample reconciles
the derivative-index discrepancies but does **not** refresh the remaining
75 lines. Before any release/order decision, recapture a request-bound full
88-line direct public packet and separately satisfy whatever JLC PCBA
availability/allocation authority the release stage requires. No authenticated
interface, private uploader, purchase, or order was used here.
