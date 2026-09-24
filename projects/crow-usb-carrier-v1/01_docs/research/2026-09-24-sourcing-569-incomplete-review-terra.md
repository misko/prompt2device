# Independent public-prelayout sourcing review

review_verdict: INCOMPLETE

public_prelayout_admission: INCOMPLETE

authenticated_allocation: NOT_REVIEWED

## Scope and integrity

This is a fresh, read-only judgment of public catalog evidence only.  It makes
no allocation, orderability, BOM-upload, substitution, native-vendor, or
release claim.

Verified handoff hashes:

| Item | SHA-256 | Result |
| --- | --- | --- |
| schema-2 review envelope | `7711cf6eb2a71b30caeff8c1c53bbf86f4b21be19c7ddb7d761a9cefad2efcdd` | match |
| manifest | `0d3ed41153f3010be0f487568de1755733574e77137fe2d29f2f7b65a9bd63bc` | match |
| candidate | `b967c1c33bdac9b3fb538496d07040400608fec4f6b9fe141d0e8fdf83084a12` | match and request-bound |
| request | `5ee047e243f504e00d913f76c0a1137b8c02f37cf462c548d03075956e419cef` | match |
| Circuit JSON | `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448` | match |

All 105 declared envelope inputs have the declared SHA-256 and byte size.
This includes all 88 supplied `cache/jlcsearch` raw-cache records.  For all
88 report rows, the cache filename, URL, fetch timestamp, decoded body byte
count, and body SHA-256 agree with the report evidence: **88/88 raw query
records are intact and row-linked**.  Of them, 83 are report-labelled
`CATALOG_OBSERVED` and five are report-labelled `UNKNOWN`.

The candidate additionally names an older direct source,
`06_build/sourcing/public-stock.json`, SHA-256
`6084330d4795ca1f2a8a4691cf8d41981be60d8665ddadb73596cbd56ae79252`.
That file and its raw records are not envelope inputs.  Therefore its stated
stock values and its stated observation time cannot be independently
revalidated from raw evidence here: **0/88 carried observations have supplied
raw-source proof in this handoff**.  This does not turn them into zero stock;
it prevents their admission as verified threshold proof.

## Independent population and threshold derivation

The Circuit JSON contains 569 `source_component` records.  Exactly 24 are the
declared manual THT set and have no JLC code: `J1`--`J8` and
`C_A1N`, `C_A1P`, through `C_A8N`, `C_A8P`.  The remaining 545 coded placed
references aggregate into exactly 88 LCSC lines; none has a missing code, no
extra line exists, and every source-ref list, per-board count, and five-board
quantity agrees with the saved request and candidate (**88/88**).

The independently derived build quantity is five.  The threshold is
`per_board_refs * 5 + 150` for each exact LCSC/MPN line, except exactly
`C6362698` / `XU316-1024-TQ128-C24` / `U_XU`, for which D10 makes the buffer
zero and the threshold is five.  The candidate implements this rule on
**88/88** rows.

`C1525` is correct in the new Circuit JSON: 80 exact
`CL05B104KO5NNNC` references, build demand 400, and threshold 550.  Its raw
catalog observation was fetched at `2026-09-24T00:09:51.328713+00:00`, has
body SHA-256 `a64ecfb1884c8884907da603c8c02ff36ebae95276ae784f1e107663a8780196`,
and reports 16,407,331 units, so this line passes.

## Fresh public observations and threshold grading

Use the individual raw-cache `fetched_at` as the query observation time.  Do
not use the later report generation (`00:11`) or candidate generation
(`00:16`) timestamp as a stock observation time.  The cache has no upstream
stock timestamp, so it proves an observed public response at its fetch time,
not an upstream inventory snapshot time.

Submitted report-status threshold denominator: **77 PASS / 6 FAIL / 5
UNKNOWN = 88**.  The six failed, stock-observed exact lines are:

| LCSC / exact MPN | refs per board | build | buffer | threshold | observed stock | raw fetch time |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| C138002 / RC0402FR-0733RL | 2 | 10 | 150 | 160 | 47 | 00:09:47.822923Z |
| C138033 / RC0402FR-071ML | 10 | 50 | 150 | 200 | 8 | 00:09:48.702363Z |
| C2675550 / SN74LVC1G125DCKT | 2 | 10 | 150 | 160 | 7 | 00:09:58.942792Z |
| C60490 / RC0402FR-0710KL | 41 | 205 | 150 | 355 | 32 | 00:10:06.664995Z |
| C60491 / RC0402FR-07100KL | 37 | 185 | 150 | 335 | 17 | 00:10:07.112107Z |
| C93943 / RC0402FR-0747KL | 1 | 5 | 150 | 155 | 10 | 00:10:20.144306Z |

The five submitted `UNKNOWN` lines are not stock zero:

| LCSC / MPN | build + buffer = threshold | supplied current raw outcome | submitted grade |
| --- | ---: | --- | --- |
| C105872 / RC0402FR-075K1L | 10 + 150 = 160 | HTTP 200 body with empty component list at 00:09:42.818705Z | UNKNOWN / no stock observation |
| C106231 / RC0402FR-070RL | 5 + 150 = 155 | HTTP 200 body with empty component list at 00:09:43.387433Z | UNKNOWN / no stock observation |
| C1852023 / TLV320ADC6140IRTWT | 10 + 150 = 160 | HTTP 200 body with empty component list at 00:09:53.578763Z | UNKNOWN / no stock observation |
| C192562 / 43650-0200 | 5 + 150 = 155 | code query returned 436500200, stock 3,064, at 00:09:54.449058Z | submitted UNKNOWN |
| C6362698 / XU316-1024-TQ128-C24 | 5 + 0 = 5 | HTTP 200 body with empty component list at 00:10:07.548580Z | UNKNOWN / no stock observation |

The supplied raw outcomes do not substantiate later prose that the C1852023
probe timed out or that the C6362698 probe returned HTTP 500: the row-linked
raw code queries are both HTTP 200 empty lists.  The supplemental discovery
files for those claims contain no evidence object/raw cache payload, so they
are not admitted for this review.

## Identity and age

87/88 candidate source MPNs are literal matches.  C192562 is the remaining
formatting case.  Independent primary-manufacturer review of Molex product
record `436500200` confirms that its part number is `436500200` and lists both
`43650-0200` and `0436500200` as keywords.  Thus its supplied raw C192562
result is the same manufacturer part for identity purposes; this is an alias
proof, not punctuation normalization or a substitute.  It permits the raw
3,064 value to clear the 155 threshold if the report disposition is
re-generated.  It does not create allocation, orderability, or any other
vendor commitment.  The submitted candidate nevertheless labels the line
`UNKNOWN`; I preserve that submitted status rather than hand-editing evidence.
Evidence: https://www.molex.com/en-us/products/part-detail/436500200

After that identity correction, the raw evidence itself is 78 threshold passes,
six threshold fails, and four no-stock-observation rows; the submitted
candidate's 83-observed/5-unknown status remains 77/6/5 as stated above.

Neither supplied `assembly.yaml` nor `procurement-policy.yaml` supplies an
explicit maximum public-observation age.  The candidate declares its carried
direct observation occurred at `2026-09-23T20:13:07.818000+00:00`, roughly
four hours before candidate construction, but the absent carried raw artifact
means that age is an unverified assertion here.  It must not be replaced by
the candidate's file-generation time.  The owning receipt grader separately
has a default 24-hour `Checked At` limit for actual operator evidence; that is
not a supplied public-stock policy and cannot make this candidate a receipt.

## Findings and disposition

P0: none.

P1: The six exact, raw, fresh stock observations above fail the required
five-board-plus-buffer thresholds.  This independently blocks admission.

P1: Four lines lack a current stock observation (C105872, C106231, C1852023,
and C6362698).  They are `UNKNOWN`/`NOT_OBSERVED`, not zero.  The only stated
older values that clear them are in an omitted raw source, so they cannot cure
the gap in this packet.

P1: The purported carried direct evidence is not supplied as raw evidence, so
the candidate's claimed 88/88 historical threshold passes cannot be audited.

P2: C192562's primary alias proof cures its string identity, but the candidate
disposition remains stale (`UNKNOWN` despite a raw 3,064 observation).

P2: The later timeout/HTTP-500 descriptions conflict with the row-linked raw
HTTP-200 empty-list records and lack their own retained raw proof.

The candidate is therefore **not eligible now**.  `INCOMPLETE` is used rather
than a fabricated pass because the four no-stock rows and all carried-source
claims lack admission-grade current/raw proof; the independently observed six
threshold failures are also material defects.  No unknown is converted to
zero.

## Exact next action and owning gate

Obtain current, saved JLCPCB PCBA-interface evidence for all 88 exact requested
codes, resolving the four unobserved lines and the six threshold shortages
under the approved policy.  Preserve each actual operator/export row with
exact resolved code, `AVAILABLE` status, available quantity, fulfillment and
economic fields, RFC3339 `Checked At`, and nonblank evidence.  Then the owning
gate must create a new receipt from those bytes, never rename or rehash this
candidate:

```text
python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py verify-request \
  06_build/sourcing/prelayout_request.json --bom 03_tscircuit/build/circuit.json \
  --assembly 03_src/rules/assembly.yaml \
  --procurement-policy 01_docs/sourcing/procurement-policy.yaml \
  --build-quantity 5 --phase prelayout
python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py grade \
  06_build/sourcing/prelayout_request.json ACTUAL_JLCPCB_RESPONSE.csv \
  --out 06_build/sourcing/prelayout_receipt.json
python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py verify \
  06_build/sourcing/prelayout_receipt.json \
  --bom 03_tscircuit/build/circuit.json --phase prelayout
```

Only an `ACCEPTED`, reproducible new `prelayout_receipt.json` from that gate
can be consumed by downstream prelayout readiness.  This public candidate is
not such a receipt.
