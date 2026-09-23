# Terra review — self-short / post-placement via guard

**Reviewed input:** `fc9a1dd1ad17348b8bd660ae5e6bc0ead1f42d2e` only, parent `60c0194a21e203d1cae177191d21d5afdfa3879a`.

**Verdict: DEFECTIVE.** The new same-footprint guard has a concrete copper-short false negative, and the new via recheck does not retain the stated owner-pad invariant after a move.

## Findings

### P1 — every unnetted copper pad is exempted as “mechanical”

At `generate_board_generic.py:1594`, the self-short path returns whenever either pad has `GetNetCode() <= 0`.  That does not identify a mechanical hole: the enclosing collection already selects pads with a copper stack, and an ordinary SMD pad may be unnetted.  Such a land physically overlaps and electrically joins its neighbour’s copper even though it has no net assignment.

The committed `netless_mechanical` clean test itself demonstrates the hole: it creates `M` as `PAD_ATTRIB_SMD`, rectangular F.Cu copper, directly coincident with a GND SMD pad, and expects `PASS`.  It is not an NPTH/mechanical construction.  Therefore an electrically meaningful same-footprint overlap can still reach a board unchanged, defeating the guard’s purpose.  Do not exempt by net code; copper-bearing pads on shared layers should be geometrically checked, with any truly non-copper mechanical holes already excluded by the existing `CuStack()` filter (or classify NPTH explicitly if needed).

### P2 — post-placement check only checks foreign-net collisions, not that a thermal via remains in its owner pad

`check_emitted_via_collisions()` records `(source, ref, padnum, via)` but at `1444–1464` never resolves `ref.padnum` or verifies `HitTest(via position)` after `legalize()` / `apply_post_anchors()`.  A moved owner can leave its named thermal via behind with no foreign pad at that coordinate; the method passes, although the thermal via is no longer attached to its authored exposed pad and may be an unrouted isolated via.

I modified only the temporary in-memory test probe to move U_LDO far enough that the original via was outside pad 11 and left no foreign pad under it.  `check_emitted_via_collisions()` returned `@@PASS`.  The guard should, for each recorded via, find the current owner footprint and same-net numbered pad(s), then require that the via centre remains inside at least one owner pad before checking other-net effective shapes.  This also makes the recorded ownership data serve its documented purpose.

## Verified working behavior

The proposed geometry choices are otherwise sound for the stated P1 cases: same-layer selection precedes collision; actual `GetEffectiveShape(layer)` is used for same-footprint copper; same-net fused/composite pads pass; opposite-side pads pass; and the moved-via different-net case uses shared copper layers and correctly fails.  Explicit field vias and promoted heatsink vias are both tracked for the post-placement pass.

Focused committed tests:

```
/usr/bin/python3 tests/t1_generate_board.py --only='P-COLLIDE rejects different-net pads in one native footprint|P-COLLIDE keeps fused, netless and opposite-side native pads legal|post-placement via check rejects owner signal-pad short|post-placement via check accepts its own ground exposed pad'
```

Result: **4 passed, 0 failed** (two known-bad rejection witnesses).  This does not clear the P1 finding because the clean witness misclassifies its deliberately created SMD copper land as mechanical.

No source, board, or root-worktree files were modified.
