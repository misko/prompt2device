# Terra audit — DLC/USB public-stock reconciliation (2026-09-23)

## Verdict: PASS, with correctly bounded meaning

`01_docs/sourcing/jlc-stock-dlc-usb-2026-09-23.md` is materially truthful for
the current composed circuit.  It accurately reports a dated *public catalog*
screen, and it does not claim authentication, private availability, allocation,
reservation, purchase, or PCBA fulfillment.  It must not be read as an
order-time availability result.

The currently generated circuit is SHA-256
`416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da`,
the same hash stated by the draft and the refresh evidence.

## Exact population reconciliation

The refresh request, direct catalog report, and jlcsearch screen have the same
set of 88 LCSC codes.  For every code, their designator tuple and five-board
quantity agree:

* request: `06_build/verification/dlc-usb-public-refresh-20260923/06_build/sourcing/request.json`,
  SHA-256 `9cc31cc38165bbbece09d5ccd31328360d1bb02041e0c524f64f0c848dde9d9c`;
* direct catalog report: `.../public-stock.json`, SHA-256
  `6084330d4795ca1f2a8a4691cf8d41981be60d8665ddadb73596cbd56ae79252`;
* derivative screen: `.../screen.json`, SHA-256
  `a5229c6065239e0d22e4cd51982e62fab11716e0707076b18828152ca45069d6`.

The direct report has 88 graded / 88 total lines, no uncoded lines, no failures,
and `PASS`.  Its stated rule is `5 × per-board aggregated quantity + 150`,
except the explicit D10 override for `C6362698` / `XU316-1024-TQ128-C24`:
five required, zero surplus, 41 observed.  No other direct line has a surplus
override.

The 24 manual references are exactly the existing D9 exclusions: sixteen
`C_A[1-8][NP]` film capacitors and `J1` through `J8`.  They are not graded in
the 88-line JLC catalog screen.  This does not say that every through-hole
reference is manual: `J_PWR` remains a coded JLC line (`C192562`).

`C192562` has catalog MPN `436500200` in the direct report while source selects
Molex `43650-0200`.  This is a documented exact catalog alias in
`02_parts/43650-0200/part.yaml` (`sourcing.catalog_mpn`) and the earlier D10
record; the direct result is 3,886 versus threshold 155.  The draft properly
identifies this narrowly, rather than generalizing MPN normalization.

## Direct versus derivative evidence

The derivative jlcsearch report correctly has 83 `CATALOG_OBSERVED` and five
`UNKNOWN` rows: `C105872`, `C106231`, `C1852023`, `C192562`, and `C6362698`.
The first, second, third, and fifth are marked absent from that search index;
`C192562` is marked MPN-mismatch/ambiguous by the literal screen.  These are
not direct-catalog shortages.

The six listed mirror counts are indeed below the direct-screen reserve rule
when recomputed from the stored rows: `C138002` 47 < 160; `C138033` 8 < 200;
`C2675550` 7 < 160; `C60490` 32 < 355; `C60491` 17 < 335; and `C93943` 10 <
155.  `screen.json` itself labels these as meeting only its required quantity;
thus “below the surplus threshold” in the draft is arithmetic comparison with
the direct `+150` rule, not an additional failing jlcsearch verdict.  The
draft’s stated unknown upstream timestamp and no-freshness/no-substitution
inference are appropriate.

## Readiness interpretation

`manufacturing_readiness-current.json` is `ACCEPTED`, 4/4 checks:
exact-code identity (568/568 source components), procurement exposure,
public-catalog prelayout, and source-value identity.  Its own output confines
this to a public stock design screen and says the final JLC uploader allocation
and economics remain mandatory.  The draft’s “source-design admission only”
is therefore accurate.

No corrective project edit is indicated.  Preserve the draft’s current scope
and use a new final uploader result for allocation, pricing, MOQ, and
fulfillment decisions.
