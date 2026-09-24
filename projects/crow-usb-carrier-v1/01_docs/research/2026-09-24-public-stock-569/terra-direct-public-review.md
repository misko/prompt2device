# Independent direct-public prelayout sourcing re-review

review_verdict: DEFECTIVE

public_prelayout_source_admission: NOT_ELIGIBLE

authenticated_pcba_allocation: NOT_REVIEWED

## Scope and integrity

This is a fresh read-only review of the supplied direct-public catalog screen.
It does not make a JLCPCB allocation, uploader, orderability, substitution,
purchase, or release claim.

The declared review-envelope SHA-256 is
`bc1b4b62a714626f38b9015074454ee101451a36247806f3ca4a88e040007df3` and
the declared manifest SHA-256 is
`743fe665b146b536b8b30d9234d4110f52fd5d709a25c687a22c92425efcf8ee`; both
match. All 18 manifest input records match both their declared SHA-256 and
byte size. Relevant verified hashes are:

| Item | SHA-256 |
| --- | --- |
| direct artifact `fresh-direct-public-stock-r2.json` | `34fdd4c7758d08152bc5abd6e25101c7519f948b74c84dd9db610bd1c4f84485` |
| request | `5ee047e243f504e00d913f76c0a1137b8c02f37cf462c548d03075956e419cef` |
| Circuit JSON | `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448` |
| generated probe BOM | `3d5a5d4cc7e8c43aa8c3be7be83ba1138213d1cbf9795c2a17de66a0e87e4571` |
| retained stock tool | `46da3bfefbddd3f59a26d2c359176bf9b86c103a866b6956ea922a5bd3541cb1` |
| assembly policy | `a9be61f176b35eefc46b8677a9de68c9f6f0ebabf0a136711a8279205ef44985` |
| procurement policy | `2385b85a974ab1ccc3204e5c3a50dca0d7250c3252276d4d8ffc132ea06723a0` |
| D10 | `09abd75af76f8a4daf8705d90a140bae957fd61dd4b1c25b510350b36c971c27` |
| ADR-0010 | `3495bcba8b76058e722c24b9c5fa5b03627e987eeb7f7a6a2751d67f1cfbd24b` |
| preserved prior incomplete review | `73daf4dba2a1abb004aa86caa595d058f5f764de9d70099d3893fbcc2bf53406` |

## Independent population and line audit

The Circuit JSON contains 569 `source_component` records. The assembly policy
declares exactly 24 manual THT exclusions: J1--J8 and C_A1N/P through
C_A8N/P. Each excluded source component has no JLC code. The remaining 545
references aggregate into exactly 88 unique requested LCSC codes.

I independently compared the Circuit JSON grouping, request, generated probe
BOM, and every artifact line. Results: 88/88 code memberships; 88/88 exact
ordered reference lists; 88/88 per-board quantities; 88/88 five-board demand
calculations; 88/88 applied buffers; 88/88 thresholds; 88/88 absolute-surplus
calculations; and 88/88 claimed `OK` comparisons are arithmetically correct.
The probe BOM has 88 unique lines and matches the request's exact code and
designator lists. The artifact's `generated_at` is
`2026-09-24T00:28:02.930919+00:00`, its declared field is
`lcsc_catalog_stockCount`, and it declares 88 graded, 88 total, zero failures,
zero uncoded lines, and `PASS`.

All 87 ordinary source MPNs are literal matches between Circuit JSON and the
artifact. C192562 is the one format difference: the source names
`43650-0200`, while the artifact names `436500200`. The official Molex record
for `436500200` explicitly lists `43650-0200` and `0436500200` as keywords,
so this is a verified identity alias, not a replacement or substitution:
https://www.molex.com/en-us/products/part-detail/436500200

The required C1525 check is correct as arithmetic and source identity:
80 references of `CL05B104KO5NNNC`, five-board demand 400, 150 buffer,
threshold 550, and the artifact's claimed direct stock 25,620,513.

The only zero-buffer row is C6362698 / `XU316-1024-TQ128-C24` / U_XU:
five-board demand and threshold are both 5, with claimed stock 41. Every other
row applies +150, exactly as D10, ADR-0010, and `assembly.yaml` require.

## Preserved provider contradictions

The prior incomplete review remains immutable history. Its jlcsearch results
are a different provider representation and are neither deleted nor relabeled
as current direct-catalog values. The direct artifact claims these formerly
short rows now clear their respective thresholds:

| Code | prior jlcsearch stock / threshold | direct claimed stock / threshold |
| --- | ---: | ---: |
| C138002 | 47 / 160 | 8,233,459 / 160 |
| C138033 | 8 / 200 | 1,762,273 / 200 |
| C2675550 | 7 / 160 | 181 / 160 |
| C60490 | 32 / 355 | 7,926,190 / 355 |
| C60491 | 17 / 335 | 8,769,196 / 335 |
| C93943 | 10 / 155 | 5,435,108 / 155 |

The four prior jlcsearch no-observation rows also have claimed direct values
that exceed their thresholds: C105872 2,127,743/160; C106231 569,417/155;
C1852023 188/160; and C6362698 41/5. C192562 is additionally claimed as
3,886/155 and its alias identity is verified above. These are contradictory
provider observations, not evidence that the earlier observations were false.

## Admission finding

ADR-0010 permits public exact-code observations for the design-only prelayout
screen and expressly defers allocation, assembly attrition, minimums, price,
fees, and order readiness. It also says that missing, stale, mismatched, or
insufficient public evidence must fail that screen. Thus this screen need not
be an authenticated PCBA receipt, but it still needs auditable public-source
provenance.

That provenance is absent here for all 88/88 lines. The JSON line schema has
only code, designators, quantity, threshold arithmetic, status, stock, type,
MPN, and manufacturer. It contains no public URL, request URL/body, raw
response or body hash, per-row observation/fetch time, or evidence identifier.
The single artifact generation time is not a per-row catalog observation time.

There is a second, independent provenance defect. The retained
`jlc_stock_check.py` computes one global `min_absolute_surplus`; it does not
read the assembly policy or D10, does not implement an override, and does not
emit `public_stock_surplus_overrides` or per-line `applied_surplus`. The
artifact represents itself as output of that tool while containing all three
of those features. No retained wrapper or producer source explains the
difference. Its `bom` path also points outside this handoff, and its JSON has
no request or probe-BOM hash. The artifact's content can be reconciled to the
packet after the fact, but its claimed direct observations and producer cannot
be independently reproduced or authenticated from the retained evidence.

This is a P1 defect, not a stock shortage finding: the 88 numerical claims
pass their stated arithmetic, but their direct-public evidence provenance is
insufficient under ADR-0010. The existing schema-2 request verifier also
fails in this handoff because the request embeds original absolute paths for
the Circuit JSON, assembly policy, and procurement policy; the bytes/hash
match but strict reconstruction reports those three records stale after packet
relocation. That is a separate P2 request-portability defect.

The screen is therefore `NOT_ELIGIBLE` as a public-prelayout source-admission
record. It is also not, and must not be renamed or rehashed into, an accepted
PCBA receipt.

## Exact next action

Retain a reproducible public-catalog evidence bundle for all 88 exact request
codes: the producer script or wrapper SHA, exact POST URL/request body, raw
response/body SHA, fetch time for each row, parsed exact code/MPN/stock, the
request SHA and probe-BOM SHA, and D10 override application. Then implement
or invoke the owning **public-prelayout importer/grader** that validates those
records against `prelayout_request.json` and emits a distinct request-bound
public-screen receipt. No such public importer exists in the supplied
`jlc_pcba_availability.py`; that program's `grade` input is an
`authority_required: jlcpcb_pcba_interface` response and would create a PCBA
receipt, which D11 deliberately does not require for this design-only screen.

The existing request-binding check to use after making its paths portable is:

```text
python3 jlc_pcba_availability.py verify-request \
  06_build/sourcing/prelayout_request.json \
  --bom 03_tscircuit/build/circuit.json \
  --assembly 03_src/rules/assembly.yaml \
  --procurement-policy 01_docs/procurement-policy.yaml \
  --build-quantity 5 --phase prelayout
```

Only a new, request-bound public-prelayout receipt produced from retained raw
public observations can cure this evidence defect. Authenticated PCBA
allocation remains deferred and unreviewed.
