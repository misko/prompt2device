# Fresh authoritative public-catalog prelayout review

review_verdict: SOUND

public_prelayout_evidence: ELIGIBLE

authenticated_pcba_allocation: NOT_REVIEWED

mutation: NOT_PERFORMED

## Scope and packet integrity

This was a fresh, read-only review of the immutable packet.  It is a
request-bound, unauthenticated LCSC public-catalog prelayout screen only.  It
does not allocate, reserve, procure, order, upload a PCBA BOM, grant native
JLCPCB admission, or release anything.

I independently recomputed SHA-256 and byte size for every **120/120**
envelope inputs, including all 88 raw bodies: all match the envelope.  The
source-review manifest also hashes to
`5b66e3a0342ef8c8a5cf880fc59fe30c47c156a56ce7e2642514399a1e9911e5`.
The subject/output hash is
`aa9491bf6df447b646bb6985921cf489ed07c3d01893f2fd2829b13759acf142`
for `public-stock.json`; the semantic hash is identical.

The authoritative producer is `jlc_stock_check.py`, SHA-256
`3937fd797d3f3e239be931a3ec1815eec11c0a627f03efbc28ee734777f5e69d`,
with surplus policy `stock_surplus_policy.py`, SHA-256
`50b81feb9900825b43c6aacda1b3ba7d4b6331e60df030161368d17831bd7b59`.
The pre-execution record binds that producer, its harness
`a1d3f4fd912f96630bcee2eb20e58c886022af4bb21bc9e5dcc38c1d1793cac1`,
probe BOM `3d5a5d4cc7e8c43aa8c3be7be83ba1138213d1cbf9795c2a17de66a0e87e4571`,
assembly policy, exact request, and argv.  The final record binds the output,
CSV, capture log, stdout, stderr, verification result, circuit, verifier
stdout and verifier stderr.  `checker.stderr` and `verify-request.stderr` are
the expected empty files; retained `verify-request.stdout` says
`JLC-PCBA REQUEST PASS: phase=prelayout`.

I read the runpy recorder.  It calls the real `urllib.request.urlopen`, reads
each response once, records the returned bytes and metadata, and returns those
same bytes through `RecordedResponse` to the authoritative parser.  It does
not transform response bodies or relabel checker output.  The checker writes
the CSV/JSON/stdout/stderr itself.  This passes the transparent-capture test.

## Independent 88-row raw and calculation audit

The schema-v2 request SHA-256 is
`5ee047e243f504e00d913f76c0a1137b8c02f37cf462c548d03075956e419cef`; its
bound circuit JSON is SHA-256
`1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`.
The request contains 88 unique exact codes, 88 rows, build quantity 5, and
88/88 coverage.  Its 24 exclusions are the declared manual/THT references
`J1`–`J8` and `C_A1N/P`–`C_A8N/P`; they are outside the PCBA public-stock
denominator and are not silently graded as stock passes.

I parsed all **88/88** JSONL capture records and **88/88** raw JSON bodies.
All ordinal numbers and request codes are unique; all are POSTs to the
authoritative `selectSmtComponentList` endpoint; all request bodies are exact
`{currentPage:1,pageSize:5,keyword:<requested code>}` requests; all HTTP
statuses are 200; all start/end UTC timestamps are present; and all recorded
raw lengths and SHA-256 values match the corresponding immutable raw file.
For every row I independently found exactly one exact `componentCode` in the
raw response, and confirmed that its code, MPN, and `stockCount` equal the
checker output.  The raw-request, request, and output code sets are identical:
**88/88, 88/88, 88/88**.  There are no zero, UNKNOWN, absent, mismatched, or
unbound rows, and no failing or ambiguous raw rows.

I recomputed every output row from request quantity and parsed raw `stockCount`:
`required_qty = 5 * per_board_qty`,
`threshold = required_qty + applied_surplus`, and
`absolute_surplus = stock - required_qty`.  Results are **88/88** matching
quantities, thresholds, absolute surpluses, and `OK` comparisons; all 88 meet
their threshold.  This includes C1525 / `CL05B104KO5NNNC`: 80 per board, 400
for five boards, ordinary +150, threshold **550**, observed stock 25,612,946.
The sole D10 exception is C6362698 / `XU316-1024-TQ128-C24` / `U_XU`: one per
board, required 5, applied surplus 0, threshold **5**, observed stock 41.
The other 87 rows carry the exact +150 surplus.

The sole format alias is C192562: supplied `part.yaml` binds primary Molex
`43650-0200` to catalog MPN `436500200`, explicitly says that it normalizes
to that primary order code, and request evidence binds C192562.  That supplied
dossier evidence is sufficient for this exact alias; it is not a substitution
or allocation assertion.

## Authority, freshness, and consumer compatibility

The assembly policy SHA-256 is
`a9be61f176b35eefc46b8677a9de68c9f6f0ebabf0a136711a8279205ef44985`: it
sets build quantity 5, `sourcing_authority: public-observations`, ordinary
surplus 150, and the exact D10 override.  Procurement policy SHA-256 is
`2385b85a974ab1ccc3204e5c3a50dca0d7250c3252276d4d8ffc132ea06723a0`.
ADR-0009 SHA-256 is
`09abd75af76f8a4daf8705d90a140bae957fd61dd4b1c25b510350b36c971c27` and
ADR-0010 SHA-256 is
`3495bcba8b76058e722c24b9c5fa5b03627e987eeb7f7a6a2751d67f1cfbd24b`.
These bind exactly the stated D10/D11 scope.  The retained request verifier
passes for the copied exact circuit, assembly, procurement policy, build 5,
and prelayout phase.

`public-stock.json` was generated at `2026-09-24T00:45:18.073286+00:00`.
At this review's freshness calculation (`2026-09-24T00:50:08.833761+00:00`)
its age was **290.760 seconds (0.0808 hours)**, within the consumer's inclusive
0..24-hour rule.  This artifact-generation time is distinct from the capture
observations: the first fetch began `2026-09-24T00:43:00.806526+00:00` and the
last completed `2026-09-24T00:45:16.872218+00:00`; each of the 88 records has
its own UTC start/end time.

I audited `manufacturing_readiness.py` SHA-256
`582fc41b418abea49fabb29b44b2f16e3abe767d51d0f8b7b3b341ab78f401ff` and
owning `rebuild_all.sh` SHA-256
`e85e4d5d3f8926e05e64966888f29cad0cbac1b3808860b55948ae5563d246e2`.
Their prelayout path consumes a verified schema-v2 request and the legacy
public-stock sidecar, requires tool `jlc_stock_check.py`, source
`lcsc_catalog_stockCount`, `predicts_jlc_assembly_allocation: false`, request
binding, complete coverage, exact D10 policy and the public-catalog decision.
The consumer is compatible with this packet.

The existing owning boundary is `rebuild_all.sh` lines 269–312: it first
verifies the canonical request, requires a present fresh sidecar, then invokes
`manufacturing_readiness.py grade --phase prelayout`; only that owning sequence
may mint `06_build/verification/manufacturing_readiness_prelayout.json` and its
stage bundle/result.  The exact owner commands are:

```sh
python3 skills/jlcpcb-fab/scripts/jlc_pcba_availability.py verify-request 06_build/sourcing/prelayout_request.json --bom 03_tscircuit/build/circuit.json --assembly 03_src/rules/assembly.yaml --procurement-policy 01_docs/sourcing/procurement-policy.yaml --build-quantity 5 --phase prelayout
python3 skills/jlcpcb-fab/scripts/manufacturing_readiness.py grade . --phase prelayout --catalog-request 06_build/sourcing/prelayout_request.json --catalog-evidence 06_build/sourcing/public-stock.json --catalog-decision 01_docs/decisions/0010-public-records-design-admission.md --json 06_build/verification/manufacturing_readiness_prelayout.json --stage-bundle 06_build/verification/pipeline/bundles/part_freeze --stage-result 06_build/verification/pipeline/S-PART-FREEZE.stage.json
```

If canonical bytes have changed, the owner must first prepare the request from
those bytes using the `jlc_pcba_availability.py prepare` invocation at
`rebuild_all.sh` lines 288–294, recapture a fresh catalog sidecar with the
authoritative checker/harness, then run the two commands above.  The PCBA
response importer/grade workflow is a different authenticated/order workflow
and was neither substituted nor run.

## Findings and retained history

* **P0:** none.
* **P1:** none for this immutable raw-evidence packet.
* **P2:** public catalog stock can change after its observed timestamps; the
  bounded 24-hour freshness rule addresses evidence recency only.  Authenticated
  JLCPCB PCBA allocation, reservation, attrition/minimums, procurement,
  ordering, native admission, and release remain missing by design and outside
  this review's scope.

The earlier `terra-direct-public-review.md` remains an immutable DEFECTIVE
historical review of its different packet with its genuine 0/88 raw-provenance
gap.  Its corrigendum correctly narrows the producer finding: the old retained
helper could not establish incapability of this authoritative D10-capable
producer.  Neither history item is erased or relabeled by this result.
