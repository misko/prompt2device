# JLC r6 quote session — 31 October 2026 Pacific

User explicitly requested following the r6 MacBook instructions, authorizing the
four listed replacement identities for this quote-only session. Scope remains
five fabricated/two assembled carriers and ten fabricated/eight assembled pods.
No payment, purchase, reservation, noncancelable pre-order, vendor message,
production approval or manufacturing commitment was made.

## Upload and matching

Verified remote commit `54a7e820` and ran the public integrity verifier on the
94-file package: `QUOTE_PAYLOAD_INTEGRITY_PASS`. The output correctly records
that two research artifacts are not bundled, full engineering replay was not
performed and production readiness is false. Existing r5 Gerbers remained in
the saved drafts; uploaded and processed both r6 BOM/CPL pairs.

JLC showed the requested replacement MPN/C-code rows selected:

| Job | MPN / code | JLC displayed gross quantity | Displayed line |
|---|---|---:|---:|
| Carrier | Samsung CL31B106KBHNNNE / C89632 | 6 | $1.5210 |
| Carrier | Samsung CL21B105KBFNNNE / C28323 | 20 | $0.8440 |
| Carrier | TI PCM1864DBTR / C544855 | 4 | $18.3000 |
| Pod | Samsung CL21B225KBYVPNE / C5362585 | 12 | $2.2428 |
| Pod | Samsung CL21B105KBFNNNE / C28323 | 20 | $0.8440 |

These are matching-page observations, not reserved inventory or a complete
quote; gross numbers are job-specific and must not be replaced with installed
need. Reprocessing reset eight grouped carrier capacitor rows and two grouped
pod resistor rows to unchecked; restored them after matching their existing
exact r6 BOM codes. JLC also auto-selected U10 YLPTEC C18212367 again; it was
deselected. The required exact RECOM remains unresolved, not DNP. The carrier
showed two shortage rows (fuse and oscillator) and the pod one (fuse); the
carrier's 35 confirmed / 30 rows and pod's 22 confirmed / 21 rows reveal that
summary counters do not prove coverage. A row-by-row UI check found no other
unchecked matched carrier rows and no unchecked matched pod rows; shortage rows
remain unselected and require sourcing.

## Exact Global Sourcing candidates, unreserved

At approximately 21:15 Pacific the JLC search interface displayed the following
DigiKey offers. Quantity fields were edited to calculate illustrative lines;
no Add or cart action was taken. Stock shown is distributor stock, not available
JLC warehouse inventory. Shipping, inspection, sourcing charges, machine
handling, taxes and usable-stock dates are not established by these lines.

| Exact part / DigiKey item | Displayed offer | Illustrative quantity / extended price |
|---|---|---|
| Littelfuse 1206L010/30WR / 18-1206L010/30WRCT-ND | Cut tape, MOQ 1, stock 45,522, estimated attrition 2, minimum assembly 2, 8–14 business days | 30 / $21.72 |
| CTS CB3LV-3I-12M288000 / 110-CB3LV-3I-12M288000CT-ND | Cut tape, MOQ 1, stock 1,449, attrition 0, minimum assembly 0, 8–14 business days | 2 / $4.28 |
| RECOM R-78E5.0-0.5 / 945-1648-5-ND | Tube, MOQ 1, stock 32,691, attrition 0, minimum assembly 0, 8–14 business days | 2 / $9.69 |

Illustrative component lines total $35.69; this is not an orderable quantity or
complete sourcing quote. Fuse job gross requirements were 18 carrier and 10 pod
in the matching pages; confirm allowances and allocation per job, and do not
sum the seven public units with the global pool. Fuse inspection/3C and other
fees remain open. CTS manual-versus-reflow handling and RECOM THT assembly
acceptance remain open. Lead-time ranges are not warehouse-ready dates.

## Preview and quote status

Pod NEXT displayed “Project has unselected parts”, offering “Do not place” or
“Select parts”. Chose “Select parts”; no required component was designated DNP.
Both complete placement previews and a complete itemized PCBA quote remain
unavailable. The carrier stackup warning is still unanswered; preserve the
production-file/placement reviews and no-auto-confirm preferences, verify
actual selected construction, stack/rails/stencil and all process controls.
Prior board-only screen figures are incomplete and predate current final matching.
Review the exact factory previews and process acceptance before any production
decision; this session does not approve the r6 design for manufacture.
