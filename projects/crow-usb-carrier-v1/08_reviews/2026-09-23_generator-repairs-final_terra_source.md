# Terra final review — generator repair commits

**Verdict: PASS** for the repair set reviewed here.

| Commit | Review result |
| --- | --- |
| `fc9a1dd1ad17348b8bd660ae5e6bc0ead1f42d2e` | Its original self-short/via guard was correctly identified as defective in the preserved earlier report. |
| `325b928621434ffc7a5a53e0d5489e8f0c285925` (atop `fc9a1dd1`) | PASS: fixes both reported holes without introducing a placement-order or reproducibility regression. |
| `817db28a05ddbf3f0c94c4ccd1329997fa7ff8bf` (parent `f45f634bce9bd13d1004c186024fda7f34c57607`) | PASS: supports an already-physical native pad token while keeping alias identity fail-closed. |

## Self-short / via repair (`325b928621434ffc7a5a53e0d5489e8f0c285925`)

The physical classification is now correct.  The prior false-pass fixture was `PAD_ATTRIB_SMD` with an F.Cu layer: an unassigned numbered SMD land is real copper and is now rejected when it overlaps a netted land.  The retained mechanical fixture is an NPTH pad with no copper layer; it never enters the existing `CuStack()` candidate set.  This is a justified narrow mechanical exception, rather than treating all net-code-zero pads as mechanical.

Thermal vias now emit after `run_asserts()`, `legalize()`, and `apply_post_anchors()`, so their footprint-relative positions use final pad geometry.  `check_emitted_via_collisions()` additionally requires every explicit field via to still hit a same-net, same-number owner pad; promoted heatsink pads are intentionally exempt because their source pad is replaced by the via.  The foreign-net collision check remains per shared copper layer and effective copper shape.  Same-net composite/fused pads and opposite-side pads remain legal.

Moving emission does not introduce a UUID-order change in the present build pipeline: between the old and new point, legalization and post-anchors only reposition footprints; they do not add board objects.  Targeted existing M-REPRO exercised two byte-identical runs and UUID uniqueness successfully.

Focused validation in the repaired worktree:

```
/usr/bin/python3 tests/t1_generate_board.py --only='P-COLLIDE rejects different-net pads in one native footprint|P-COLLIDE keeps fused, netless and opposite-side native pads legal|P-COLLIDE rejects unassigned SMD copper crossing a netted land|post-placement via check rejects owner signal-pad short|post-placement via check rejects orphaned owner field via|post-placement via check accepts its own ground exposed pad|post_anchors moves only reviewed refs'
```

Result: **7 passed, 0 failed**, including four known-bad rejection witnesses.  The focused M-REPRO/post-anchor run also passed (**2 passed, 0 failed**).

## Exact native alias compatibility (`817db28a`)

`resolve_pad_aliases()` now accepts an input pin that is either an evidenced schematic alias or an evidenced physical-pad token.  If a token has both meanings, it accepts it only when both resolve to the same physical pad; different targets hard-fail as ambiguous.  Unknown tokens still fail, and distinct nets resolving to one physical pad still hard-fail.  The physical USB1130 shell (`SH`) resolves to its only physical pad whether the input used schematic pin `5`, physical `SH`, or both with the same net.

Focused validation in the compatibility worktree:

```
/usr/bin/python3 tests/t1_generate_board.py --only='native USB4105 aliases preserve every logical contact and NC land|native converter physical shell pin uses the exact USB1130 dossier|board alias resolver rejects unevidenced, missing and conflicting maps|board aliases leave identity parts unchanged|board generator refuses a missing unconnected alias pad'
```

Result: **5 passed, 0 failed**, including two known-bad rejection witnesses.

This is code acceptance only; it makes no board-placement or fabrication admission.
