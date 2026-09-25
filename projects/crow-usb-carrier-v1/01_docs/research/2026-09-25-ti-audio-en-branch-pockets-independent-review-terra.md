# Independent review: AUDIO_EN branch-owner pockets

Reviewed immutable checker and packet commit `8db2a8e5`. This extension is a
strictly no-credit source-location record, not a physical-cell partition or a
route acceptance mechanism.

The packet reproduces as `INCOMPLETE`, zero global errors, with
`p1_accepted: false` and `routing_realized: false`. Its regenerated
`result.json` is byte-identical to the committed artifact (SHA-256
`06a954a0a75a22553e6156e8c83d3b2a7f246c44e2eabf63360fc78611e37dab`).
It retains all 11 exact AUDIO_EN terminals, ten required tree edges, all 11
P2 pad-to-tree obligations, and the continuous In1.Cu GND reference obligation.
The existing `R_AUDIO_PU.2` / `input_buck` source-region blocker remains
reported. The representative reservation is `INCOMPLETE` with null capacity;
there is no route, clearance, DRC, or P1/P2/P3 claim.

The three permitted pockets are tightly constrained to native full envelopes
and pads: `R_AUDIO_PD` and `U_AUDIO` for `quiet_power`, and `U_ISO1` for
`analog_ch1`. The checker requires exact source keys and board/floorplan/alias
hashes, owner membership, non-duplicate refs, board containment, no foreign
native footprint or pad, no foreign source region, no conflicting pattern, and
no pocket overlap. It also requires every declared `(branch, ref)` pair to be
used by an exact unresolved-branch endpoint. Endpoint and P2 obligation pocket
tags must agree, and a pocket cannot be combined with a physical-cell tag.
Thus it neither changes modular functional ownership nor turns a sparse pocket
into physical-cell authority.

The packet’s adversarial suite covers clipped/foreign body, foreign region and
pattern, stale board/alias/floorplan hashes, wrong owner/ref/endpoint tag,
duplicate or omitted terminals, omitted blocker/P2/tree/return duty, capacity
or PASS claims, physical-cell substitution, and reservation PASS. All fail
closed. The focused checker suite also passes: `168` tests.

I found no fail-open path in the new pocket flow. Its narrow scope remains
appropriate only for unresolved multi-terminal branches with their complete
native denominator and duties intact. A later physical-cell partition, native
route, filled return, DRC, and connected-tree evidence are still independently
required before P2 or P1 consideration.
