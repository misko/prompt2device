# Corrigendum to independent direct-public prelayout sourcing re-review

This corrigendum preserves, and does not alter, the original report
`terra-direct-public-review.md`.

## Narrowed producer finding

The helper I actually read during the original review was the packet path
`subject/jlc_stock_check.py`, SHA-256
`46da3bfefbddd3f59a26d2c359176bf9b86c103a866b6956ea922a5bd3541cb1`.
That retained helper has a global `--min-surplus` implementation and does not
read `assembly.yaml`, implement `stock_surplus_policy` / `surplus_for`, or
emit the D10-specific `public_stock_surplus_overrides` and
`applied_surplus` fields found in the direct artifact.

I retract the original report's broader implication that the *actual*
artifact producer could not emit those fields. The root reviewer has
established that the authoritative producer is a different helper, SHA prefix
`3937fd797...`, which implements D10 through `stock_surplus_policy` /
`surplus_for` and `--assembly`. That producer was not the helper at the packet
path and hash I inspected, so the original evidence only established a packet
provenance mismatch, not an incapability of the authoritative producer.

## Unchanged old-packet disposition

The original packet still contains no per-row direct-public URL/request,
raw response or response hash, or per-row observation/fetch timestamp in the
88-line artifact. Thus the original review's 0/88 raw-provenance gap remains
valid for that old packet. Its `review_verdict: DEFECTIVE` and
`public_prelayout_source_admission: NOT_ELIGIBLE` remain unchanged. This
corrigendum conducts no review of any new capture.
