# r9 merged BOM quote candidates — 2026-11-01

Quote-only candidates; the hash-bound r9 package is unchanged. The v2 files group rows only when code, manufacturer, MPN, footprint, assembly route and supply route are identical. The per-reference identity and route comparison against r9 passed for 136 carrier and 29 pod references. The r9 CPLs and Gerbers were retained; carrier X1 remains HOME.

JLC reported 23/23 confirmed for the first carrier candidate, but its table and placement list did not show the eight C1711 references. The first pod candidate similarly showed 20/20 but its table did not display R6. Neither first candidate is safe to use; the cause is unknown. The v2 candidates change the affected row comment and order and JLC then displayed all expected groups and references in the BOM and placement list: carrier 23, pod 20. Those lists are not an engineering inspection of placement geometry or polarity. A count alone is not sufficient evidence.

- Carrier v2 SHA-256: `39ec9078f5e01fb6177d1114878e99c06e552118da2c0f8c4f1932241145e2bf`
- Pod v2 SHA-256: `d297047101ca69a0d3466518a5c2e85e9ab6f7d900e3f265640d1d1066b78131`

See [session report](../../JLC-R9-SELECTION-QUOTE-FOLLOWUP-20261101.md). This is quote evidence only; no production approval, stackup acceptance or placement signoff is implied.
