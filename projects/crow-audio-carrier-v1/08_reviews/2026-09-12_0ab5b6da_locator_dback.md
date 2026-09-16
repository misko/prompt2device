subject: crow-audio-carrier-v1 locator omission after ADR-0027 logical reference remap
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_locator_omission_dback
context-given: FRESH; immutable 494-input packet; READ_ONLY source; scratch-only measurements
source_commit: 5a8b8ca236e0969410da07fd470ecb2892900f77
board_sha256: 0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090
design_rules_sha256: 5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712
review_stage: pre-route
review_kind: noncanonical D-BACK source silk/locator causal diagnosis and capability proposal
design_verdict: REASSESS-SOURCE-SILK-CAPABILITY
order_verdict: DO-NOT-ORDER
engineering_verdict: CURRENT-BOARD-LOCATOR-BLOCKED
process_verdict: COMPLETE
scope: exact old/current native reference visibility, placement algorithm and existing-control expressiveness; no canonical placement acceptance
baseline_hidden_refs: 25
current_hidden_refs: 27
accepted_hidden_ceiling: 25
candidate_generations: 0
locator_status: BLOCKED
completed_at_utc: 2026-09-12T04:07:00Z

# D-BACK judgment — locator omission after logical reference remap

## Verdict

The current board remains **BLOCKED for A-LOCATOR**: native hidden reference fields increased from 25 to 27 while the authored exception set remains 25. The exact delta is three newly hidden references, `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT`, offset by one newly visible reference, `R_FILT2P`. Updating the locator source to 27 or hiding `R_FILT2P` would only encode the regression and is not an acceptable repair.

The cause is the generic generator's greedy, sequential refdes placement after the ADR-0027 logical reference exchange. The eight `C_ADC_CM1..4P/N` logical references moved among unchanged physical capacitor sites. `_ownership()` keys every footprint centroid by logical refdes; `_place_owned()` accepts the first collision-free, owned slot and permanently adds it to `silk_obst`. The moved C identities therefore choose different early slots, and those changed obstacles cascade into later C and R placement. On otherwise fixed footprints, 23 reference-field records changed position, size, rotation, or visibility. This is downstream silk ordering behavior, not a thermal, electrical, pad, copper, plane, route, or physical-footprint defect.

The supplied full native pin projection already establishes 340 footprints and 1,002 pads, with exact equality after only ADR-0027's eight-cap reference exchange and ADC/cap net exchange across exactly nine refs. My native read independently found 1,002 pads on each board and 81 zones on each board; zone-mode records are exact-equal. Raw pad rows differ before applying the declared logical remap, as expected. The packet reports current native DRC/parity PASS and repaired thermal behavior; those accepted findings were not reopened or rerun here.

## Existing controls cannot express the isolated repair

`floorplan.yaml` currently sets `silk.refdes.priority_prefixes: "JUQF"`. The implementation sorts with only `(prefix_is_priority, full_refdes)`. Thus all non-priority C references already sort before all non-priority R references. Adding `C` has no ordering effect. Adding `R` moves every resistor ahead of every capacitor, a board-wide reorder whose likely displaced identities cannot be inferred from the four-name delta. Adding both `C` and `R` restores the present C-before-R order. The remaining refdes controls (`size`, `min_size`, `clearance`, and `fab_copy`) are global; changing them would alter the preserved legibility or clearance contract. `silk.labels` and `silk.captions` create separate board text and do not make a footprint's native Reference field visible, so they cannot close the locator mismatch.

For that reason I ran zero source-generation candidates. The task permits at most two, but it forbids broad speculative sweeps and requires isolated use of existing controls. Neither distinct existing-prefix candidate is an isolated hypothesis: one is a no-op and the other reverses the entire C/R class order. A count-only result from the latter would also be insufficient because it could exchange unrelated hidden identities.

## Minimal source capability and next action

Add one narrowly scoped optional control to the shared generator and source contract:

`silk.refdes.priority_refs: [<exact unique refdes>, ...]`

Validate it as an ordered, duplicate-free list of known non-hole footprint references. In `prio(fp)`, exact entries receive their explicit list rank; existing `priority_prefixes` and lexical sorting remain the fallback. Absence of the key must preserve byte-for-byte ordering behavior. This is a label-order control only: it must not change footprint/pad/copper/zone/net geometry, text size, stroke, clearance, ownership scoring, search offsets, thermal modes, or route state.

The first bounded source hypothesis should prioritize exactly `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT`, regenerate once in isolation, and accept it only if native omissions are at most 25 and every hidden identity is intentionally reviewed. If ordering alone merely displaces three other labels or remains above 25, stop rather than expanding the list. The next minimal capability would then be a per-ref `preferred_offsets` list that is prepended to the existing `OFF` search while retaining the same frame, collision, clearance, and ownership checks; it must never force-place text. Either capability needs positive/hostile shared tests and the governing contract update before project use.

Any successful candidate still owes the complete native footprint/pad geometry/net comparison after ADR-0027 remap, exact zone-mode equality, fresh native DRC/parity, exact hidden identity census, locator source update for the final set without raising the 25 ceiling, and visual review. It is a source candidate, not acceptance of this current board.

## Visual evidence and limits

I inspected the freshly rendered 1800×1200 top view produced from a hash-verified scratch copy of the current board and sidecars. It confirms the dense central ADC/filter/reference region and that visible identifiers are interleaved tightly around fitted bodies. The whole-board render is contextual evidence only; native field visibility and exact identities come from the independent pcbnew census.

No source candidate, locator atlas, BOM/CPL/zip export, assembly checker, fresh DRC, schematic test, route, fabrication, or release action was run. Thermal/native-pin/DRC findings are retained supplied evidence. The failed exporter removed BOM/CPL/zip/index artifacts and no later twin/overlay/locator render was claimed. Routing and the exhausted LAYOUT-0013/3 history remain outside this diagnosis.
